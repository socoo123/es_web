#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"

# 首次执行；重做前先 bash labs/f01/cleanup.sh。
docker compose -f infra/single-node/compose.yaml up -d
bash infra/single-node/wait.sh
for step in 01-observe 02-create 03-write 04-search 05-inspect; do
  printf '\n运行 %s\n' "$step"
  bash "labs/f01/$step.sh"
done
