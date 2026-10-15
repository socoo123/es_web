#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"

curl --fail-with-body -sS -X POST "$ES_URL/tut-f05-attractions/_search?pretty" \
  -H 'Content-Type: application/json' --data-binary @search/f05/match-and-reversed.json
curl --fail-with-body -sS -X POST "$ES_URL/tut-f05-attractions/_search?pretty" \
  -H 'Content-Type: application/json' --data-binary @search/f05/phrase.json
curl --fail-with-body -sS -X POST "$ES_URL/tut-f05-attractions/_search?pretty" \
  -H 'Content-Type: application/json' --data-binary @search/f05/phrase-reversed.json
curl --fail-with-body -sS -X POST "$ES_URL/tut-f05-attractions/_search?pretty" \
  -H 'Content-Type: application/json' --data-binary @search/f05/phrase-full.json
