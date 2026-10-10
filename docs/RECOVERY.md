# Linux recovery procedure

Start with compatible installed Ubuntu x86-64. Obtain OS installation media and
model backups separately. Keep a hydrated, verified Git LFS checkout before
disconnecting.

| Profile | Ubuntu | GPU target | Compiler/SDK |
| --- | --- | --- | --- |
| middle-child | 24.04 | GTX 1050 Ti, sm_61 | GCC 13, CUDA 12.6, AVX CPU floor |
| r730 | 24.04 | Tesla P4, sm_61 | GCC 13, CUDA 12.6 |
| g3070 | 24.04 | RTX 3070, sm_86 | GCC 13, CUDA 13.2 |
| llm-60 | 24.04 | RTX PRO 6000 Blackwell, sm_120 | GCC 13, CUDA 13.2 |
| llm-49 | 26.04 | RTX 4090, sm_89 | GCC 15, CUDA 13.3 |
| a5500 | 24.04 | RX 5500 XT, gfx1012 | GCC 13, distro HIP 5.7 / Clang 17 |
| llm-79 | 26.04 | RX 7900 XTX, gfx1100 | GCC 15, recorded ROCm 10.0.0rc4 |

These are collected profiles, not a claim that every GPU completed full-model
validation. Consult `RECOVERY_VALIDATION.md` for actual results.

1. Run `python3 recovery/recover.py verify --profile MACHINE`. Add
   `--include-sources` to check matching source archives. A full `verify` checks
   all profiles, binaries, and source archives.
2. Review `recovery/manifest.json`. Run the explicit `sudo python3
   recovery/recover.py install-packages --profile MACHINE` when restoring system
   packages is intended. It cannot download dependencies and refuses a different
   Ubuntu version. APT may reject conflicts rather than fetch replacements.
3. Reboot if kernel/driver restoration requires it. Secure Boot may require normal
   local module-signing/enrollment for DKMS drivers.
4. Run `python3 recovery/recover.py build --profile MACHINE --jobs 6`.
5. Check `python3 recovery/recover.py run --profile MACHINE -- --help`, then run with existing model,
   expert pack and draft head. The default address is loopback.

Use the run helper to select SDK libraries for the selected profile. A raw binary
on an installed ROCm machine can pick up that machine's libraries instead of the
extracted recovery SDK; the helper puts the recovery SDK first in the runtime
library path. It performs no dependency download or system installation.

Python 3 and APT are standard Ubuntu prerequisites. Python's offline packages are
included, but the helper cannot bootstrap itself without Python. Restore it using
offline APT from the matching package directory first. `prepare` extracts packages
for inspection; it does not replace explicit system-package restoration.

Live host drivers are not replaced to test this kit. Offline dependency-solver
checks and disconnected build results are reported separately; a simulated APT
restore is not a tested bare-metal recovery.
