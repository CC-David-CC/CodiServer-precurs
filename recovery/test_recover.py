import io
import json
from pathlib import Path
import tarfile
import tempfile
import unittest

import recover


class LocalRecoveryTests(unittest.TestCase):
    def test_unknown_manifest_asset_is_rejected(self):
        manifest = {'profiles': {'test': {'assets': ['missing']}}, 'assets': []}
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, 'unknown assets'):
                recover.verify(Path(directory), manifest, 'test')

    def test_payload_hash_tamper_and_lfs_pointer(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'asset').write_bytes(b'original')
            manifest = {'profiles': {'test': {'assets': ['asset']}}, 'assets': [
                {'path': 'asset', 'kind': 'deb', 'bytes': 8,
                 'sha256': recover.digest(root / 'asset')}]}
            self.assertEqual(recover.verify(root, manifest, 'test'), 1)
            (root / 'asset').write_bytes(b'modified')
            with self.assertRaises(ValueError):
                recover.verify(root, manifest, 'test')
            (root / 'asset').write_text('version https://git-lfs.github.com/spec/v1\n')
            with self.assertRaises(ValueError):
                recover.verify(root, manifest, 'test')

    def test_manifest_cannot_escape_checkout(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'repo'
            root.mkdir()
            (root.parent / 'outside').write_text('private')
            with self.assertRaises(ValueError):
                recover.local_asset(root, '../outside')

    def test_absolute_package_links_are_rebased(self):
        with tempfile.TemporaryDirectory() as directory:
            member = tarfile.TarInfo('usr/bin/tool')
            member.type = tarfile.SYMTYPE
            member.linkname = '/usr/lib/tool'
            safe = recover.safe_tar_member(member, directory)
            self.assertEqual(Path(safe.linkname).as_posix(), '../lib/tool')

    def test_archive_escape_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            member = tarfile.TarInfo('../../outside')
            with self.assertRaises(tarfile.TarError):
                recover.safe_tar_member(member, directory)


if __name__ == '__main__':
    unittest.main()
