#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"
curl --fail-with-body -sS "$ES_URL/?pretty"
curl --fail-with-body -sS -X PUT "$ES_URL/tut-f11-attractions?pretty" -H 'Content-Type: application/json' --data-binary @search/f11/index.json
curl --fail-with-body -sS "$ES_URL/_cluster/health/tut-f11-attractions?wait_for_status=green&timeout=30s&pretty"
curl --fail-with-body -sS -X POST "$ES_URL/tut-f11-attractions/_bulk?pretty" -H 'Content-Type: application/x-ndjson' --data-binary @data/f11/attractions.ndjson
curl --fail-with-body -sS -X POST "$ES_URL/tut-f11-attractions/_refresh?pretty"
curl --fail-with-body -sS "$ES_URL/tut-f11-attractions/_count?pretty"
