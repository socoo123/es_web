#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"
curl --fail-with-body -sS -X POST "$ES_URL/tut-f09-attractions/_search?pretty" -H 'Content-Type: application/json' --data-binary @search/f09/selected.json
curl --fail-with-body -sS -X POST "$ES_URL/tut-f09-attractions/_search?pretty" -H 'Content-Type: application/json' --data-binary @search/f09/multi-city.json
curl --fail-with-body -sS -X POST "$ES_URL/tut-f09-attractions/_search?pretty" -H 'Content-Type: application/json' --data-binary @search/f09/overlap.json
curl --fail-with-body -sS -X POST "$ES_URL/tut-f09-attractions/_search?pretty" -H 'Content-Type: application/json' --data-binary @search/f09/empty.json
curl --fail-with-body -sS -X POST "$ES_URL/tut-f09-attractions/_search?pretty" -H 'Content-Type: application/json' --data-binary @search/f09/unselected.json
