# Recovery payload licensing and origins

Distribution packages are stored without modification. Their copyright files,
licenses, notices, kernel sources and maintainers' control scripts remain inside
the original `.deb` archives. Installation extracts those files normally.

Ubuntu dependency sources are obtained from Ubuntu source indexes. Each file's
expected SHA-256 and size are recorded in the manifest. Older pinned kernel
versions use official Launchpad source descriptors where the current source index
no longer lists that version. Their descriptor identities and member hashes are
checked; this is not a claim that every descriptor signature was independently
verified by this project's helper.

NVIDIA CUDA Linux redistributable archives retain their original license files.
Their original acquisition uses NVIDIA's redistributable manifest for CUDA 12.6.3.
CUDA 13 SDK packages come from NVIDIA's public Ubuntu package repository. These
proprietary SDK portions do not become open source by inclusion here. Consult the
[CUDA EULA](https://docs.nvidia.com/cuda/eula/) and the licenses embedded in each
package. NVIDIA's Linux driver packages retain their distribution agreements;
the Linux driver agreement permits unaltered distribution for open-source kernels
subject to its conditions and provision of that agreement.

The NVIDIA-distributed DKMS package contains its preferred shell-script source.
An additional archive preserves the exact scripts and package control needed to
repack it, with upstream v3.4.3 source, Makefile and manual source alongside it.
Repacking is not claimed to reproduce timestamps/compression byte for byte.
The MIT-licensed EGL Wayland package retains its notices and includes upstream
release source as supporting provenance.

The recorded ROCm/TheRock 10.0.0rc4 SDK preserves the installed versioned toolkit,
its component notices, and `share/therock/therock_manifest.json`, including component
source pins. Recovery rewires recorded `/etc/alternatives` aliases inside the
extracted SDK; it does not change the archived compiler/runtime binaries or the
live system's alternatives. See [TheRock](https://github.com/ROCm/TheRock).

The server and bundled dependencies retain their original repository licenses.
Personal files, private configuration, model weights, Windows installers, and OS
installation media are not included. This provenance is not a vulnerability or
malware clearance for vendor compilers, drivers, or this server.
