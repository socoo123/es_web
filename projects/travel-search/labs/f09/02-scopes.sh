#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"
curl --fail-with-body -sS -X POST "$ES_URL/tut-f09-attractions/_search?pretty" -H 'Content-Type: application/json' --data-binary @search/f09/all-query.json
curl --fail-with-body -sS -X POST "$ES_URL/tut-f09-attractions/_search?pretty" -H 'Content-Type: application/json' --data-binary @search/f09/post-only.json
