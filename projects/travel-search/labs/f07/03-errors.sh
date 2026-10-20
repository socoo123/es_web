#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"
# 故障对照会短暂停止框架篇专用 ES；不触及源码篇 9200/9201。
# 若中途退出，仍尝试恢复专用容器；Java 服务由读者在另一终端运行。
trap 'docker compose -f infra/single-node/compose.yaml up -d es >/dev/null' EXIT
curl --fail-with-body -sS "$APP_URL/api/health"
curl -sS -w '\nHTTP %{http_code}\n' -X POST "$APP_URL/api/attractions/search" \
  -H 'Content-Type: application/json' --data-binary @search/f07/input-invalid.json
docker compose -f infra/single-node/compose.yaml stop es
curl --fail-with-body -sS "$APP_URL/api/health"
curl -sS -w '\nHTTP %{http_code}\n' -X POST "$APP_URL/api/attractions/search" \
  -H 'Content-Type: application/json' --data-binary @search/f07/input-near.json
docker compose -f infra/single-node/compose.yaml up -d es
bash infra/single-node/wait.sh
curl --fail-with-body -sS -X POST "$APP_URL/api/attractions/search" \
  -H 'Content-Type: application/json' --data-binary @search/f07/input-near.json
