#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"
for query in near budget-80 empty; do
  curl --fail-with-body -sS -X POST "$ES_URL/tut-f07-attractions/_search?pretty" \
    -H 'Content-Type: application/json' --data-binary "@search/f07/$query.json"
  curl --fail-with-body -sS -X POST "$APP_URL/api/attractions/search" \
    -H 'Content-Type: application/json' --data-binary "@search/f07/input-$query.json"
done
