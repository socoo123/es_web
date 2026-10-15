#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"
docker compose -f infra/single-node/compose.yaml up -d
bash infra/single-node/wait.sh
# 不自动清理旧资源；第一次运行或按 cleanup.sh 点名清理后运行。
for step in 01-create 02-mixed 03-retry 04-reimport 05-boundaries 06-dynamic; do
  printf '\n运行 %s\n' "$step"
  bash "labs/f04/$step.sh"
done
