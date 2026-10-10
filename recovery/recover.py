"""Verify and use the local Linux recovery payload. This tool never downloads."""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import tarfile


REPO = Path(__file__).resolve().parents[1]


def digest(path):
    value = hashlib.sha256()
    with path.open('rb') as source:
        for block in iter(lambda: source.read(1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()


def local_asset(root, name):
    path = (root / name).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError('Missing or unsafe recovery asset: ' + name)
    return path


def verify(root, manifest, profile=None, include_sources=False):
    selected = set(manifest['profiles'][profile]['assets']) if profile else None
    known = {item['path'] for item in manifest['assets']}
    if selected is not None and selected - known:
        raise ValueError('Profile references unknown assets: ' + ', '.join(sorted(selected - known)))
    count = 0
    for item in manifest['assets']:
        if selected is not None and item['path'] not in selected:
            continue
        if item['kind'] == 'source' and not include_sources and profile:
            continue
        path = local_asset(root, item['path'])
        if path.stat().st_size != item['bytes'] or digest(path) != item['sha256']:
            raise ValueError('Incomplete, changed, or unhydrated LFS asset: ' + item['path'])
        count += 1
    if not count:
        raise ValueError('No recovery assets selected')
    return count


def safe_tar_member(member, destination):
    """Rebase package absolute links into the extraction root, then validate."""
    member = copy.copy(member)
    if member.issym() and member.linkname.startswith('/'):
        target = Path(destination) / member.linkname.lstrip('/')
        parent = Path(destination) / Path(member.name).parent
        member.linkname = Path(os.path.relpath(target, parent)).as_posix()
    elif member.islnk() and member.linkname.startswith('/'):
        member.linkname = member.linkname.lstrip('/')
    return tarfile.data_filter(member, destination)


def unpack_deb(path, destination):
    with subprocess.Popen(['dpkg-deb', '--fsys-tarfile', str(path)],
                          stdout=subprocess.PIPE) as process:
        with tarfile.open(fileobj=process.stdout, mode='r|') as archive:
            archive.extractall(destination, filter=safe_tar_member)
        if process.wait() != 0:
            raise RuntimeError('Could not unpack ' + path.name)


def check_platform(config):
    if platform.system() != 'Linux' or platform.machine() not in ('x86_64', 'amd64'):
        raise ValueError('This recovery branch supports Linux x86-64 only')
    fields = {}
    for line in Path('/etc/os-release').read_text().splitlines():
        if '=' in line:
            key, value = line.split('=', 1)
            fields[key] = value.strip('"')
    if fields.get('ID') != 'ubuntu' or fields.get('VERSION_ID') != config['ubuntu']:
        raise ValueError('This profile requires Ubuntu ' + config['ubuntu'])


def prepare(root, manifest, profile):
    check_platform(manifest['profiles'][profile])
    verify(root, manifest, profile)
    work = root / '.recovery' / profile
    sysroot = work / 'sysroot'
    sysroot.mkdir(parents=True, exist_ok=True)
    selected = set(manifest['profiles'][profile]['assets'])
    for item in manifest['assets']:
        if item['path'] in selected and item['kind'] == 'deb':
            unpack_deb(local_asset(root, item['path']), sysroot)
    # Debian's CMake import files sometimes encode /usr rather than their prefix.
    # Only extracted text metadata is relocated; original package bytes stay intact.
    for path in (sysroot / 'usr').rglob('*.cmake'):
        text = path.read_text(encoding='utf-8')
        changed = text.replace('"/usr', '"' + str(sysroot / 'usr'))
        if changed != text:
            path.write_text(changed, encoding='utf-8')
    config = manifest['profiles'][profile]
    if config.get('sdk_archive'):
        toolkit = work / config['backend']
        toolkit.mkdir(exist_ok=True)
        for item in manifest['assets']:
            if item['path'] not in selected or item['kind'] not in ('cuda-sdk', 'hip-sdk'):
                continue
            with tarfile.open(local_asset(root, item['path'])) as archive:
                prefix = item['archive_prefix'] + '/'
                members = []
                for member in archive.getmembers():
                    if member.name == item['archive_prefix']:
                        continue
                    if not member.name.startswith(prefix):
                        raise ValueError('Unexpected toolkit archive member: ' + member.name)
                    member = copy.copy(member)
                    member.name = member.name[len(prefix):]
                    members.append(member)
                archive.extractall(toolkit, members=members, filter=safe_tar_member)
        lib64 = toolkit / 'lib64'
        if config['backend'] == 'cuda' and not lib64.exists():
            lib64.symlink_to('lib', target_is_directory=True)
    return work


def build(root, manifest, profile, jobs):
    config = manifest['profiles'][profile]
    check_platform(config)
    verify(root, manifest, profile)
    work = root / '.recovery' / profile
    work.mkdir(parents=True, exist_ok=True)
    environment = dict(os.environ)
    # Compilers and system runtimes are restored with install-packages first.
    # Debian compilers are not advertised as relocatable executable bundles.
    cmake = Path('/usr/bin/cmake')
    compiler = Path('/usr/bin/g++-' + str(config['gcc']))
    args = [str(cmake), '-S', str(root), '-B', str(work / 'build'), '-G', 'Ninja',
            '-DCMAKE_BUILD_TYPE=Release', '-DSTRATA_NATIVE_EXPERTS=ON',
            '-DSTRATA_BUILD_TESTS=OFF', '-DCMAKE_CXX_COMPILER=' + str(compiler),
            '-DCMAKE_C_COMPILER=/usr/bin/gcc-' + str(config['gcc']),
            '-DCMAKE_MAKE_PROGRAM=/usr/bin/ninja',
            '-DSTRATA_ISA_FLOOR=' + config.get('isa', 'avx2')]
    if config['backend'] == 'cuda':
        if config.get('sdk_archive'):
            toolkit = prepare(root, manifest, profile) / 'cuda'
        else:
            toolkit = Path(config['toolkit'])
        args += ['-DSTRATA_ENABLE_CUDA=ON',
                 '-DSTRATA_EXPERIMENTAL_SM60=' + ('ON' if int(config['arch']) < 70 else 'OFF'),
                 '-DCMAKE_CUDA_ARCHITECTURES=' + config['arch'],
                 '-DCMAKE_CUDA_COMPILER=' + str(toolkit / 'bin/nvcc'),
                 '-DCMAKE_CUDA_HOST_COMPILER=' + str(compiler),
                 '-DCUDAToolkit_ROOT=' + str(toolkit)]
        environment['LD_LIBRARY_PATH'] = str(toolkit / 'lib64') + os.pathsep + str(toolkit / 'lib') + os.pathsep + environment.get('LD_LIBRARY_PATH', '')
    else:
        if config.get('sdk_archive'):
            toolkit = prepare(root, manifest, profile) / 'hip'
            hip_compiler = str(toolkit / config['compiler_relative'])
        else:
            toolkit = Path(config['toolkit'])
            hip_compiler = config['hip_compiler']
        args += ['-DSTRATA_ENABLE_HIP=ON', '-DCMAKE_HIP_ARCHITECTURES=' + config['arch'],
                 '-DCMAKE_HIP_COMPILER=' + hip_compiler,
                 '-DCMAKE_HIP_COMPILER_ROCM_ROOT=' + str(toolkit),
                 '-DCMAKE_PREFIX_PATH=' + str(toolkit)]
        environment['LD_LIBRARY_PATH'] = str(toolkit / 'lib') + os.pathsep + environment.get('LD_LIBRARY_PATH', '')
        args += config.get('cmake_options', [])
    for tool in (cmake, compiler):
        if not tool.is_file():
            raise ValueError('Restore bundled packages with install-packages first; missing ' + str(tool))
    subprocess.run(args, env=environment, check=True)
    subprocess.run([str(cmake), '--build', str(work / 'build'), '-j', str(jobs),
                    '--target', 'codi-server'], env=environment, check=True)
    print('Built local server: ' + str(work / 'build/codi-server'))


def install_packages(root, manifest, profile):
    check_platform(manifest['profiles'][profile])
    verify(root, manifest, profile)
    if os.geteuid() != 0:
        raise ValueError('Driver/system recovery requires root; run this explicit command with sudo')
    selected = set(manifest['profiles'][profile]['assets'])
    packages = [str(local_asset(root, item['path'])) for item in manifest['assets']
                if item['path'] in selected and item['kind'] == 'deb']
    subprocess.run(['apt-get', '--no-download', '-o', 'Dir::Etc::sourcelist=/dev/null',
                    '-o', 'Dir::Etc::sourceparts=-', 'install', *packages], check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('verify', 'prepare', 'build', 'install-packages'))
    parser.add_argument('--profile', help='Machine profile from recovery/manifest.json')
    parser.add_argument('--include-sources', action='store_true')
    parser.add_argument('--jobs', type=int, default=6)
    args = parser.parse_args()
    manifest = json.loads((REPO / 'recovery/manifest.json').read_text(encoding='utf-8'))
    if args.profile and args.profile not in manifest['profiles']:
        parser.error('Unknown profile; choose ' + ', '.join(manifest['profiles']))
    if args.command != 'verify' and not args.profile:
        parser.error('--profile is required for this command')
    if not 1 <= args.jobs <= 32:
        parser.error('--jobs must be between 1 and 32')
    try:
        if args.command == 'verify':
            count = verify(REPO, manifest, args.profile, args.include_sources)
            print('Verified ' + str(count) + ' local recovery assets')
        elif args.command == 'prepare':
            print('Prepared local tools: ' + str(prepare(REPO, manifest, args.profile)))
        elif args.command == 'build':
            build(REPO, manifest, args.profile, args.jobs)
        else:
            install_packages(REPO, manifest, args.profile)
    except (OSError, ValueError, subprocess.CalledProcessError, tarfile.TarError) as error:
        parser.exit(1, str(error) + '\nNo dependency download was attempted.\n')


if __name__ == '__main__':
    main()
