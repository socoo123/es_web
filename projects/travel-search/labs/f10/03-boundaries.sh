#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"
curl --fail-with-body -sS -X POST "$ES_URL/tut-f10-attractions/_search?pretty" -H 'Content-Type: application/json' --data-binary @search/f10/price-scores.json
printf '\n'
curl --fail-with-body -sS -X POST "$ES_URL/tut-f10-attractions/_search?pretty" -H 'Content-Type: application/json' --data-binary @search/f10/hz-distance.json
printf '\n'
curl --fail-with-body -sS -X POST "$ES_URL/tut-f10-attractions/_search?pretty" -H 'Content-Type: application/json' --data-binary @search/f10/budget-price.json
printf '\n'
curl --fail-with-body -sS -X POST "$ES_URL/tut-f10-attractions/_search?pretty" -H 'Content-Type: application/json' --data-binary @search/f10/empty.json
printf '\n'
curl --fail-with-body -sS -X POST "$ES_URL/tut-f10-attractions/_search?pretty" -H 'Content-Type: application/json' --data-binary @search/f10/missing-last.json
printf '\n'
curl --fail-with-body -sS -X POST "$ES_URL/tut-f10-attractions/_search?pretty" -H 'Content-Type: application/json' --data-binary @search/f10/missing-zero.json
printf '\n'
