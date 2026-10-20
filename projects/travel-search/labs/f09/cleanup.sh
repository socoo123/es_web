#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"
# 只删除本课两个索引；404 表示已经清理，不使用通配符。
for index in tut-f09-attractions tut-f09-candidates; do
  code=$(curl -sS -o /dev/null -w '%{http_code}' -X DELETE "$ES_URL/$index")
  case "$code" in 200|404) printf '%s: HTTP %s\n' "$index" "$code";; *) printf '清理失败: %s HTTP %s\n' "$index" "$code" >&2; exit 1;; esac
done
