#!/usr/bin/env bash
set -euo pipefail
# 从任何工作目录执行；仅探测本工程固定端口。
for attempt in {1..90}; do
  if curl --fail --silent --show-error --max-time 2 \
    http://127.0.0.1:19200/ >/dev/null 2>&1; then
    printf 'ES HTTP 已就绪：http://127.0.0.1:19200/\n'
    exit 0
  fi
  sleep 2
done
printf '180 秒内未就绪。检查 compose 日志、端口和 Docker 内存。\n' >&2
exit 1
