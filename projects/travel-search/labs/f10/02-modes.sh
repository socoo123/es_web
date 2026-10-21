#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"
curl --fail-with-body -sS -X POST "$ES_URL/tut-f10-attractions/_search?pretty" -H 'Content-Type: application/json' --data-binary @search/f10/default.json
printf '\n'
curl --fail-with-body -sS -X POST "$ES_URL/tut-f10-attractions/_search?pretty" -H 'Content-Type: application/json' --data-binary @search/f10/relevance.json
printf '\n'
curl --fail-with-body -sS -X POST "$ES_URL/tut-f10-attractions/_search?pretty" -H 'Content-Type: application/json' --data-binary @search/f10/price.json
printf '\n'
curl --fail-with-body -sS -X POST "$ES_URL/tut-f10-attractions/_search?pretty" -H 'Content-Type: application/json' --data-binary @search/f10/distance.json
printf '\n'
