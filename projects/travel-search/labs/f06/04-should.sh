#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"

curl --fail-with-body -sS -X POST "$ES_URL/tut-f06-attractions/_search?pretty" \
  -H 'Content-Type: application/json' --data-binary @search/f06/should-optional.json
curl --fail-with-body -sS -X POST "$ES_URL/tut-f06-attractions/_search?pretty" \
  -H 'Content-Type: application/json' --data-binary @search/f06/should-required.json
curl --fail-with-body -sS -X POST "$ES_URL/tut-f06-attractions/_search?pretty" \
  -H 'Content-Type: application/json' --data-binary @search/f06/should-only.json
curl --fail-with-body -sS -X POST "$ES_URL/tut-f06-attractions/_search?pretty" \
  -H 'Content-Type: application/json' --data-binary @search/f06/should-filter-default.json
curl --fail-with-body -sS -X POST "$ES_URL/tut-f06-attractions/_search?pretty" \
  -H 'Content-Type: application/json' --data-binary @search/f06/should-filter-required.json
curl --fail-with-body -sS -X POST "$ES_URL/tut-f06-attractions/_search?pretty" \
  -H 'Content-Type: application/json' --data-binary @search/f06/filter-only.json
