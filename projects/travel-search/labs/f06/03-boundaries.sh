#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"

curl --fail-with-body -sS -X POST "$ES_URL/tut-f06-attractions/_search?pretty" \
  -H 'Content-Type: application/json' --data-binary @search/f06/strict-upper.json
curl --fail-with-body -sS -X POST "$ES_URL/tut-f06-attractions/_search?pretty" \
  -H 'Content-Type: application/json' --data-binary @search/f06/free.json
curl --fail-with-body -sS -X POST "$ES_URL/tut-f06-attractions/_search?pretty" \
  -H 'Content-Type: application/json' --data-binary @search/f06/missing-price.json
curl --fail-with-body -sS -X POST "$ES_URL/tut-f06-attractions/_search?pretty" \
  -H 'Content-Type: application/json' --data-binary @search/f06/not-offline.json
