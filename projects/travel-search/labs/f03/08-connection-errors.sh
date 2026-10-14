#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"

expect_unreachable() {
  local result=0
  curl -sS --connect-timeout 2 --max-time 5 "$1" || result=$?
  printf 'curl exit=%s（本案例期望 7）\n' "$result"
  test "$result" -eq 7
}

# 19299 必须是未监听端口。若已有服务，换一个空闲端口再实验。
expect_unreachable http://127.0.0.1:19299/

# 异常退出也尝试恢复本工程的 es 服务；不停止源码篇容器。
restore_es() {
  docker compose -f infra/single-node/compose.yaml start es
}
trap restore_es EXIT
docker compose -f infra/single-node/compose.yaml stop es
expect_unreachable "$ES_URL/"
restore_es
bash infra/single-node/wait.sh
trap - EXIT
# HTTP 已打开不代表持久索引已恢复：只等待本课索引，临时 404 也重试。
curl --fail-with-body -sS --retry 30 --retry-all-errors --retry-delay 1 \
  --max-time 35 \
  "$ES_URL/_cluster/health/tut-f03-attractions?wait_for_status=green&timeout=30s&pretty"
bash labs/f03/04-search.sh
