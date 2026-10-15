#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"

docker compose -f infra/single-node/compose.yaml up -d
bash infra/single-node/wait.sh
# 不自动清理旧资源；首次运行或确认可删、点名 cleanup 后运行。
for step in 01-prepare 02-keywords 03-exact 04-phrase; do
  printf '\n运行 %s\n' "$step"
  bash "labs/f05/$step.sh"
done
