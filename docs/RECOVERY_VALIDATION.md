# Recovery validation — in progress

The payload is being assembled. This working tree is not a completed recovery
checkout until its manifest verifies and its Git LFS payload is published.

Completed checks:

- Four helper tests pass on Windows: hash/tamper/LFS-pointer rejection, path
  escape rejection, absolute package-link handling, and tar traversal rejection.
  Windows is a development host, not a recovery target.
- C++ `codi-server` builds and `--help` succeeds on middle-child (CUDA 12.6 / sm_61)
  and a5500 (HIP / gfx1012).
- All seven Linux hosts were inventoried. Package acquisition uses download-only
  mode with an empty dependency status to collect dependency closures. No live
  system packages or drivers were installed.

Pending: complete payload/source provenance, full manifest verification, offline
dependency-solver checks, fresh disconnected builds, publication verification.
Earlier native fixture coverage and two Pascal gaps are documented separately in
`UPGRADE_VALIDATION.md`. No new full-model HTTP or speed result is claimed.
