#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"

# 只修正失败的 B/E；index 动作后必须带完整文档，文件末尾保留换行。
curl --fail-with-body -sS -X POST "$ES_URL/tut-f04-attractions/_bulk?pretty" \
  -H 'Content-Type: application/x-ndjson' --data-binary @data/f04/retry.ndjson
curl --fail-with-body -sS -X POST "$ES_URL/tut-f04-attractions/_refresh?pretty"
curl --fail-with-body -sS -X POST "$ES_URL/tut-f04-attractions/_search?pretty" \
  -H 'Content-Type: application/json' --data-binary @search/f04/all.json
