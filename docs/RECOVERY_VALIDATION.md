# Local recovery validation

Validation uses the private `box-git` repository and branch
`validation/recovery-proof`. The tested payload revision is
`8ecdfe739d5ec96ca7d3966c4e3998e9af65eed6`. The owner authorized public publication after these isolated checks.

The manifest contains 2,254 asset paths totaling 15,130,389,292 bytes.
Its 2,200 unique SHA-256 objects total 14,077,178,791 bytes (13.11 GiB).
Git LFS acquisition and full hydration are prerequisites for disconnected use.
Model weights, prepared packs, draft heads and OS installation media are excluded.

A separate fresh full Git/LFS clone on the box-git data disk acquired and
verified all manifest assets inside a network-disabled namespace. This used the
local repository transport and did not access GitHub or the Internet.

## Completed fleet checks

Every host fetched its selected assets from `box-git` and verified their size and
SHA-256 with networking disabled. `llm-60` verified the entire manifest.
Every host built the C++ server and ran the native version command inside an
isolated dependency root. Only bundled packages/SDKs and vendored source were
visible to the build; host compilers and SDKs were hidden.

Every host also unpacked and configured its actual package set through the
recovery helper's `install-packages` operation, with APT downloads disabled and
the network namespace disconnected. Service starts were suppressed. Real host
devices, EFI variables and live boot files were not mounted into these roots.

| Host | Package configuration | Native checks exercised | Expected skips | Not exercised |
| --- | --- | --- | --- | --- |
| middle-child | 337 packages, pass | 4 pass | 1 | 4 AVX2 parity cases |
| a5500 | 293 packages, pass | 6 pass | 0 | 0 |
| llm-60 | 349 packages, pass | 9 pass | 0 | 0 |
| llm-49 | 368 packages, pass | 8 pass | 1 | 0 |
| llm-79 | 240 packages, pass | 6 pass | 0 | 0 |
| r730 | 334 packages, pass | 8 pass | 1 | 0 |
| g3070 | 349 packages, pass | 8 pass | 1 | 0 |

The 57 selected CTest cases comprise 49 exercised passes, four explicit skips,
and four AVX2 parity cases that return success without exercising parity on the
AVX-only middle-child CPU. Dense-Q8 T8 coverage requires SM120 and is explicitly
skipped on the other CUDA GPUs. Tests cover commit bounds, CPU IQ parity where
supported, GPU selection, CUDA refill lifetime and supported dense-Q8 kernels.
Runtime GPU checks use the existing host kernel driver and bundled userspace;
they do not prove that a newly restored kernel driver loads after reboot.

Actual offline NVIDIA DKMS builds succeeded on middle-child, r730 and llm-49.
For llm-60 and g3070, matching Ubuntu prebuilt open modules and their versioned
dependency-provider package are bundled with the working 595.91.07 userspace.
The llm-49 DKMS installation generated a certificate and signed its module using
bundled tools; an independent offline sign-file test also succeeded. Neither
certificate was enrolled and neither newly built module was loaded into a host.

Real HTTP API generation passed on llm-60 (CUDA) and a5500 (HIP), with bundled
userspace, existing model files mounted read-only and loopback networking only.
Checks cover health/models endpoints, a two-token non-streaming completion,
matching streaming output with termination, and rejection of an invalid request.
These short functional probes are not performance benchmarks. Other hosts have
build/native coverage but do not yet have full-model HTTP coverage for this kit.

All 3,608 regular vendored llama.cpp files match the pinned archive. Recovery
helper checks cover hash tampering, unhydrated LFS pointers, invalid references
and extraction path escapes. No engine source changes were made during the
package-closure fixes recorded here.

## Fixes exposed by recovery tests

The isolated tests exposed missing essential shell/base utilities, APT itself,
microcode dependencies, initramfs tooling and signing tools. These packages and
their matching preferred sources are now bundled. The installed NVIDIA driver
version was captured rather than mixing newer userspace with the host's kernel
module. The final APT retest caught the missing prebuilt-module dependency
provider; it and its matching source were added before the successful retest.

The test fixture also required `/dev/fd` links for DKMS shell process substitution
and writable `/proc/self` thread metadata for CUDA. `/proc/sys` remains read-only.
Neither correction modifies the live host configuration.

## Remaining recovery proof

This kit starts from compatible installed Ubuntu, not a bare-metal OS restore.
Cold-boot recovery on disposable installations/spare disks remains untested on
all seven hosts. llm-49 has Secure Boot enabled and needs controlled certificate
enrollment and boot acceptance testing. EFI-variable operations were deliberately
unavailable in the isolated package test. Multi-GPU full-model operation and
full-model HTTP tests on the remaining five machines are also untested.

The published kit does not claim complete cold-boot recovery. Local evidence is preserved;
test keys, model files and personal configuration do not belong in Git.
