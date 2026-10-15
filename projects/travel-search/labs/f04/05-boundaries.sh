#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"

curl --fail-with-body -sS -X PUT "$ES_URL/tut-f04-boundaries?pretty" \
  -H 'Content-Type: application/json' --data-binary @search/f04/index.json
curl --fail-with-body -sS -X POST "$ES_URL/tut-f04-boundaries/_bulk?pretty" \
  -H 'Content-Type: application/x-ndjson' --data-binary @data/f04/boundaries.ndjson
curl --fail-with-body -sS -X POST "$ES_URL/tut-f04-boundaries/_refresh?pretty"
curl --fail-with-body -sS "$ES_URL/tut-f04-boundaries/_count?pretty"
curl --fail-with-body -sS -X POST "$ES_URL/tut-f04-boundaries/_search?pretty" \
  -H 'Content-Type: application/json' --data-binary @search/f04/all.json
