#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"
for query in copy no-highlight empty; do
  curl --fail-with-body -sS -X POST "$ES_URL/tut-f08-attractions/_search?pretty" \
    -H 'Content-Type: application/json' --data-binary "@search/f08/$query.json"
done
