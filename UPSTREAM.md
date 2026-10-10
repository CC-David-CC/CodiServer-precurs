# Source provenance

The server starts from the tested UnbiasedStrata upgrade at
`cb9ce3c81d4d2ed6b96aa3c418ef12192dace3df` in
<https://github.com/CC-David-CC/UnbiasedStrata>. That upgrade retains Robert Karl's
C++ frontend and imports Strata main `61b3fb5dd3f1e8ec09cf7e4e05208bc6d3c46406`
(0.1.42), plus the engine ports listed in [docs/UPGRADE.md](docs/UPGRADE.md).

The original UnbiasedStrata baseline is
`d0a44ea7e757c59fa35a78b4b98d0c4bb44ce2cf`. Sources:
<https://github.com/robertkarl/UnbiasedStrata> and <https://github.com/Niko1221/Strata>.

llama.cpp is vendored at upstream Strata's exact pin:
`3cf03257f219afbe7334045ff7c6a06ac68c627d`, from
<https://github.com/ggml-org/llama.cpp>. It is not a Git submodule here.
The complete pinned source includes upstream examples; their web assets are not
built into or served by Codi Codes Server.

Changes rename the executable to `codi-server`, make `--help` successful, enable
the C++ frontend target on HIP as well as CUDA, and add Linux offline recovery.
Native engine names and APIs remain upstream-compatible. No persona, saved-prefix
persistence, Python server, updater, web chat, or LaTeX rendering is imported.

Historical results in `docs/UPGRADE_VALIDATION.md` describe the preceding upgrade.
New recovery validation is recorded in `docs/RECOVERY_VALIDATION.md`; earlier
results are not proof of a fresh offline restore on every machine.
