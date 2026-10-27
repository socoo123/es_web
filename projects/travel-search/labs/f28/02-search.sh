#!/usr/bin/env bash
set -euo pipefail
LAB_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
: "${F28_OUT:?Set F28_OUT to a NEW receipt directory for this round}"
python3 "$LAB_DIR/lab.py" prepare --out "$F28_OUT/prepare"
