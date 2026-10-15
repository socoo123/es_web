#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"

curl --fail-with-body -sS "$ES_URL/?pretty"
curl --fail-with-body -sS -X PUT "$ES_URL/tut-f05-attractions?pretty" \
  -H 'Content-Type: application/json' --data-binary @search/f05/index.json
curl --fail-with-body -sS "$ES_URL/_cluster/health/tut-f05-attractions?wait_for_status=green&timeout=30s&pretty"
curl --fail-with-body -sS "$ES_URL/tut-f05-attractions/_mapping?pretty"
curl --fail-with-body -sS -X POST "$ES_URL/tut-f05-attractions/_bulk?pretty" \
  -H 'Content-Type: application/x-ndjson' --data-binary @data/f05/attractions.ndjson
curl --fail-with-body -sS -X POST "$ES_URL/tut-f05-attractions/_refresh?pretty"
