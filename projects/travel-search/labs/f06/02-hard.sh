#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"

curl --fail-with-body -sS -X POST "$ES_URL/tut-f06-attractions/_search?pretty" \
  -H 'Content-Type: application/json' --data-binary @search/f06/all.json
curl --fail-with-body -sS -X POST "$ES_URL/tut-f06-attractions/_search?pretty" \
  -H 'Content-Type: application/json' --data-binary @search/f06/keyword.json
curl --fail-with-body -sS -X POST "$ES_URL/tut-f06-attractions/_search?pretty" \
  -H 'Content-Type: application/json' --data-binary @search/f06/city.json
curl --fail-with-body -sS -X POST "$ES_URL/tut-f06-attractions/_search?pretty" \
  -H 'Content-Type: application/json' --data-binary @search/f06/budget.json
curl --fail-with-body -sS -X POST "$ES_URL/tut-f06-attractions/_search?pretty" \
  -H 'Content-Type: application/json' --data-binary @search/f06/open.json
curl --fail-with-body -sS -X POST "$ES_URL/tut-f06-attractions/_search?pretty" \
  -H 'Content-Type: application/json' --data-binary @search/f06/near.json
