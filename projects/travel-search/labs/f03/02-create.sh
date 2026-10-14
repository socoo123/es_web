#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"

curl --fail-with-body -sS -X PUT \
  "$ES_URL/tut-f03-attractions?pretty" \
  -H 'Content-Type: application/json' \
  --data-binary @search/f03/index.json

curl --fail-with-body -sS \
  "$ES_URL/_cluster/health/tut-f03-attractions?wait_for_status=green&timeout=30s&pretty"

# 索引已就绪但尚无景点：同一名称查询应 total=0。
curl --fail-with-body -sS -X POST "$ES_URL/tut-f03-attractions/_search?pretty" \
  -H 'Content-Type: application/json' \
  --data-binary @search/f03/search-xihu.json
