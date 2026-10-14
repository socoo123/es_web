#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"

curl --fail-with-body -sS -X PUT \
  "$ES_URL/tut-f01-attractions/_doc/a-hz-xihu?pretty" \
  -H 'Content-Type: application/json' \
  --data-binary @data/f01/xihu.json
