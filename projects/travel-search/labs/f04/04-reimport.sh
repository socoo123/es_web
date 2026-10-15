#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"

# 重导入五份完整文档，固定 ID 防止重复，不代表版本或写入成本不变。
curl --fail-with-body -sS -X POST "$ES_URL/tut-f04-attractions/_bulk?pretty" \
  -H 'Content-Type: application/x-ndjson' --data-binary @data/f04/attractions.ndjson
curl --fail-with-body -sS -X POST "$ES_URL/tut-f04-attractions/_refresh?pretty"
curl --fail-with-body -sS "$ES_URL/tut-f04-attractions/_count?pretty"
curl --fail-with-body -sS "$ES_URL/tut-f04-attractions/_doc/a-hz-xihu?pretty"
