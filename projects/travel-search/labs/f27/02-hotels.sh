#!/usr/bin/env bash
set -euo pipefail
base="$(cd "$(dirname "$0")" && pwd)"
python3 "$base/lab.py" hotels --out "${F27_OUT:-/tmp/f27-reader-round1}" "$@"
