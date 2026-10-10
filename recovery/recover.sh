#!/bin/sh
set -eu
recovery_script_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
if ! command -v python3 >/dev/null 2>&1; then
    echo 'Ubuntu Python 3 is required. Restore it from the matching Ubuntu offline package directory first.' >&2
    exit 1
fi
exec python3 "$recovery_script_root/recovery/recover.py" "$@"
