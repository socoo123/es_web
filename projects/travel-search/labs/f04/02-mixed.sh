#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"

# HTTP 200 不等于所有条目成功：逐个阅读 items。
curl --fail-with-body -sS -X POST "$ES_URL/tut-f04-attractions/_bulk?pretty" \
  -H 'Content-Type: application/x-ndjson' --data-binary @data/f04/mixed.ndjson
curl --fail-with-body -sS -X POST "$ES_URL/tut-f04-attractions/_refresh?pretty"
curl --fail-with-body -sS "$ES_URL/tut-f04-attractions/_count?pretty"
