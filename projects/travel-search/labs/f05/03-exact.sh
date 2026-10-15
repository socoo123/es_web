#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"

curl --fail-with-body -sS -X POST "$ES_URL/tut-f05-attractions/_search?pretty" \
  -H 'Content-Type: application/json' --data-binary @search/f05/term-city.json
curl --fail-with-body -sS -X POST "$ES_URL/tut-f05-attractions/_search?pretty" \
  -H 'Content-Type: application/json' --data-binary @search/f05/term-city-lower.json
curl --fail-with-body -sS -X POST "$ES_URL/tut-f05-attractions/_search?pretty" \
  -H 'Content-Type: application/json' --data-binary @search/f05/term-name-raw.json
curl --fail-with-body -sS -X POST "$ES_URL/tut-f05-attractions/_search?pretty" \
  -H 'Content-Type: application/json' --data-binary @search/f05/term-name-full.json
curl --fail-with-body -sS -X POST "$ES_URL/tut-f05-attractions/_search?pretty" \
  -H 'Content-Type: application/json' --data-binary @search/f05/term-name-token.json
