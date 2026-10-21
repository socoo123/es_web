#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"
python3 labs/f12/lab.py java "$@"
