#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
python3 infra/f15/select-dictionary.py travel
python3 labs/f15/lab.py file-only
