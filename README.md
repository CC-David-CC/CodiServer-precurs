# Codi Codes Server — Linux offline recovery

A local C++ HTTP API and inference engine derived from UnbiasedStrata and Strata
0.1.42, with the engine ports recorded in [docs/UPGRADE.md](docs/UPGRADE.md).
The server binds to `127.0.0.1` by default. It has no web application, updater,
automatic model downloader, saved-prefix files, filesystem tools, or persona store.

The pinned llama.cpp dependency is included as actual source files. Build and
startup do not fetch it. Linux recovery packages and SDK archives use Git LFS;
fetching those objects is part of the initial acquisition.

## Scope

Profiles target `middle-child`, `a5500`, `llm-79`, `llm-60`, `llm-49`, `r730`, and
`g3070`. Ubuntu 24.04 and 26.04 packages are separate. Pascal uses CUDA 12.6 and
NVIDIA 580; newer NVIDIA GPUs use CUDA 13. AMD profiles preserve their respective
HIP toolchains. See [recovery instructions](docs/RECOVERY.md).

Model weights, prepared expert packs, draft heads, operating-system installation
media, Windows software, personal configuration, and credentials are excluded.
Start from a matching installed Ubuntu x86-64 system. This is not a bare-metal OS
installer or a substitute for backing up models and personal files.

## Initial acquisition

Local validation uses the private box-git repository. Public publication is
paused. Use an authorized Git client with Git LFS installed:

```sh
git clone --branch validation/recovery-proof dflanag3@box-git:/srv/data/git/codi-offline-recovery.git
cd codi-offline-recovery
git lfs pull
python3 recovery/recover.py verify
```

The checkout is ready for disconnected recovery only when verification succeeds.
A ZIP download or clone with LFS smudging disabled contains pointers instead of
the required payloads. Keep the hydrated checkout on recovery storage.

## Offline restore and build

Choose the matching machine profile. Review its manifest before restoring system
packages; this explicit step installs compilers, runtimes, kernel and GPU drivers.
Driver/kernel changes may require a reboot. Verification and compilation do not
change installed drivers.

```sh
python3 recovery/recover.py verify --profile middle-child
sudo python3 recovery/recover.py install-packages --profile middle-child
python3 recovery/recover.py build --profile middle-child --jobs 6
python3 recovery/recover.py run --profile middle-child -- --help
```

APT downloads are disabled. The build uses restored system compilers and bundled
source. Tests and limitations are recorded in [validation](docs/RECOVERY_VALIDATION.md).

## Run

Supply your existing model shards, expert pack and prepared draft head:

```sh
python3 recovery/recover.py run --profile middle-child -- \
  --model /path/to/model-00001-of-00002.gguf \
  --pack /path/to/pack --mtp /path/to/mtp
```

Endpoints: `GET /health`, `GET /v1/models`, and `POST /v1/chat/completions`, with
streaming and non-streaming replies. The native engine CLI is available as
`run --profile MACHINE -- --engine ...`. The run helper selects the matching SDK
runtime libraries locally; it does not reinstall packages or verify the entire
multi-gigabyte payload on every server start. The HTTP frontend retains Robert's single-model
workflow; native multi-GPU support does not imply HTTP multi-GPU support.

## Provenance

[UPSTREAM.md](UPSTREAM.md) records source origins. Unmodified packages retain
embedded licenses and notices. Matching Ubuntu source archives accompany binary
packages; proprietary NVIDIA SDK portions retain vendor licenses. Identities,
sizes and SHA-256 hashes are recorded in `recovery/manifest.json`. Hash verification
detects incomplete or changed payloads; it does not certify absence of vulnerabilities.
