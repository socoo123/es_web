#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"

curl --fail-with-body -sS "$ES_URL/?pretty"
curl --fail-with-body -sS -X PUT "$ES_URL/tut-f04-attractions?pretty" \
  -H 'Content-Type: application/json' --data-binary @search/f04/index.json
curl --fail-with-body -sS "$ES_URL/_cluster/health/tut-f04-attractions?wait_for_status=green&timeout=30s&pretty"
curl --fail-with-body -sS "$ES_URL/tut-f04-attractions/_mapping?pretty"
