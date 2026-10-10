Local validation update: essential shell/base utilities and their exact preferred
sources have been added after an isolated dependency-root test exposed the
base-OS shell assumption. The earlier checks below apply to baseline `46cabe8`;
the extended payload is undergoing fresh local validation. No public push is authorized
by these partial results. OS media, live driver installation and reboot testing remain
separate from extraction/build checks.

# Recovery validation

The complete local manifest verifies 1,857 assets: 13,834,712,524 bytes across
paths, approximately 11.92 GiB of unique LFS payload after hash deduplication.
Initial acquisition must hydrate all LFS objects before disconnected recovery.

Completed checks:

- Five helper tests pass on Windows: hash/tamper/LFS-pointer rejection, path
  escape rejection, absolute package-link handling, and tar traversal rejection.
  unknown manifest-reference rejection. Windows is a development host, not a recovery target.
- C++ `codi-server` builds and `--help` succeeds on middle-child (CUDA 12.6 / sm_61)
  and a5500 (HIP / gfx1012).
- All seven Linux hosts were inventoried. Package acquisition uses download-only
  mode with an empty dependency status to collect dependency closures. No live
  system packages or drivers were installed.
- Fresh server source builds, help and native version checks passed with networking
  disabled (`sudo unshare -n`, then `runuser`) on llm-60, llm-49, g3070, r730 and
  llm-79. Installed compilers/SDKs were used for these checks; they are not fresh
  package installations. The R730 check used its installed CUDA 12.0 / GCC 12;
  its recovery profile restores CUDA 12.6 / GCC 13.
- Selected native CTest results in the same disconnected environments: llm-60,
  llm-49 and g3070 each passed nine tests; r730 passed eight with one expected
  dense-Q8 tensor-core skip on Pascal; llm-79 passed six. Tests cover CPU IQ parity,
  GPU selection, commit bounds, and on CUDA, refill lifetime and dense Q8.
- All seven package closures passed APT simulation with networking disabled,
  empty package status, disabled download/repository access, and local packages
  only. This checks dependency resolution without installing packages.
- All 3,608 regular files from the pinned llama.cpp archive match the vendored
  working tree byte for byte.
- The actual recovery helper completed fresh disconnected builds on llm-60 and
  llm-79. The latter used the extracted SDK archive with recorded alternatives
  aliases restored inside the recovery tree, without changing `/opt/rocm` or
  `/etc/alternatives` on the host.

- Full local size/SHA-256 verification passed for all 1,857 manifest assets.
- The run helper selects the extracted SDK's runtime library path. On llm-79,
  loader inspection with that path resolved HIP, BLAS and compiler-runtime
  dependencies inside the extracted recovery SDK; the native version command
  passed with networking disabled.

Publication verification is performed after pushing. Live driver installations,
bare-metal restores and full-model HTTP/speed runs were not performed for this kit.
Earlier native fixture coverage and two Pascal gaps are documented separately in
`UPGRADE_VALIDATION.md`. No new full-model HTTP or speed result is claimed.
