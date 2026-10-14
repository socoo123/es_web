#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"

curl --fail-with-body -sS -X POST \
  "$ES_URL/tut-f03-attractions/_refresh?pretty"

curl --fail-with-body -sS -X POST \
  "$ES_URL/tut-f03-attractions/_search?pretty" \
  -H 'Content-Type: application/json' \
  --data-binary @search/f03/search-xihu.json
