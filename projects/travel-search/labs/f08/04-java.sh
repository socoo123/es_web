#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"
for query in multi alias empty; do
  curl --fail-with-body -sS -X POST "$APP_URL/api/attractions/multi-search" \
    -H 'Content-Type: application/json' --data-binary "@search/f08/input-$query.json"
done
