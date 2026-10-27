#!/usr/bin/env bash
set -euo pipefail
base="$(cd "$(dirname "$0")" && pwd)"
python3 "$base/lab.py" collapse --out "${F26_OUT:-/tmp/f26-reader-round1}"
