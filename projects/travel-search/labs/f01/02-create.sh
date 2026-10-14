#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"

curl --fail-with-body -sS -X PUT \
  "$ES_URL/tut-f01-attractions?pretty" \
  -H 'Content-Type: application/json' \
  --data-binary @search/f01/index.json

curl --fail-with-body -sS \
  "$ES_URL/_cluster/health/tut-f01-attractions?wait_for_status=green&timeout=30s&pretty"
