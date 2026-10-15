#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"

curl --fail-with-body -sS -X POST "$ES_URL/tut-f05-attractions/_search?pretty" \
  -H 'Content-Type: application/json' --data-binary @search/f05/all.json
curl --fail-with-body -sS -X POST "$ES_URL/tut-f05-attractions/_analyze?pretty" \
  -H 'Content-Type: application/json' --data-binary @search/f05/analyze-query.json
curl --fail-with-body -sS -X POST "$ES_URL/tut-f05-attractions/_analyze?pretty" \
  -H 'Content-Type: application/json' --data-binary @search/f05/analyze-name.json
curl --fail-with-body -sS -X POST "$ES_URL/tut-f05-attractions/_analyze?pretty" \
  -H 'Content-Type: application/json' --data-binary @search/f05/analyze-tea.json
curl --fail-with-body -sS -X POST "$ES_URL/tut-f05-attractions/_search?pretty" \
  -H 'Content-Type: application/json' --data-binary @search/f05/term-name.json
curl --fail-with-body -sS -X POST "$ES_URL/tut-f05-attractions/_search?pretty" \
  -H 'Content-Type: application/json' --data-binary @search/f05/match-or.json
curl --fail-with-body -sS -X POST "$ES_URL/tut-f05-attractions/_search?pretty" \
  -H 'Content-Type: application/json' --data-binary @search/f05/match-and.json
