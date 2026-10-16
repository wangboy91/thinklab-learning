#!/bin/sh
set -eu
cd -- "$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
if ! command -v python3 >/dev/null 2>&1; then
  echo 'Python 3.11+ is required; no runtime is installed automatically.' >&2
  exit 1
fi
exec python3 scripts/start_local.py "$@"
