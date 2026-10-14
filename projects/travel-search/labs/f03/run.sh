#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"

# C01 主流程 12 条 HTTP 请求，探活另计。首次执行；重做前先 bash labs/f03/cleanup.sh。
docker compose -f infra/single-node/compose.yaml up -d
bash infra/single-node/wait.sh
for step in 01-observe 02-create 03-write 04-search 05-inspect; do
  printf '\n运行 %s\n' "$step"
  bash "labs/f03/$step.sh"
done
