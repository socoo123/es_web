#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
docker compose -f infra/f15/compose.yaml restart es
bash infra/f15/wait.sh
python3 labs/f15/lab.py loaded-new
