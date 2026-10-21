#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"
# 只删除 F10 独立索引；404 表示已经清理。
code=$(curl -sS -o /dev/null -w '%{http_code}' -X DELETE "$ES_URL/tut-f10-attractions")
case "$code" in 200|404) printf 'tut-f10-attractions: HTTP %s\n' "$code";; *) printf '清理失败 HTTP %s\n' "$code" >&2; exit 1;; esac
