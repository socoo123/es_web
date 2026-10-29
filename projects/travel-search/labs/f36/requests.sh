#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
F36_ES=http://127.0.0.1:20036
f36sql() { docker compose -f infra/f36/compose.yaml exec -T postgres psql -X -qAt -v ON_ERROR_STOP=1 -U travel -d travel_f36 "$@"; }
request() { curl --fail-with-body -sS -w '\nHTTP %{http_code}\n' "$@"; }
case "${1:-}" in
prepare)
  test $# -eq 2
  mkdir "$2"
  # Fresh F36 resources only; duplicates fail. Use point-named cleanup before repeating.
  f36sql < data/f36/schema.sql
  f36sql < data/f36/seed.sql
  f36sql < data/f36/projection-view.sql
  f36sql < data/f36/export.sql > "$2/initial.ndjson"
  request -X PUT "$F36_ES/tut-f36-attractions-v001" -H 'Content-Type: application/json' --data-binary @search/f36/create.json
  request -X POST "$F36_ES/_aliases" -H 'Content-Type: application/json' --data-binary @search/f36/aliases.json
  python3 labs/f36/to-bulk.py "$2/initial.ndjson" > "$2/initial.bulk.ndjson"
  request -X POST "$F36_ES/tut-f36-attractions-write/_bulk?require_alias=true" -H 'Content-Type: application/x-ndjson' --data-binary "@$2/initial.bulk.ndjson"
  request -X POST "$F36_ES/tut-f36-attractions-v001/_refresh"
  ;;
related)
  test $# -eq 2
  f36sql < data/f36/related-change.sql
  f36sql < data/f36/export.sql > "$2/related.ndjson"
  ;;
change)
  f36sql < data/f36/during-snapshot.sql
  ;;
delta)
  test $# -eq 2
  f36sql < data/f36/known-delta.sql > "$2/delta.ndjson"
  ;;
inspect)
  request -X POST "$F36_ES/tut-f36-attractions-read/_search?allow_partial_search_results=false" -H 'Content-Type: application/json' --data-binary @search/f36/all.json
  ;;
refresh)
  request -X POST "$F36_ES/tut-f36-attractions-v001/_refresh"
  ;;
*) echo 'Usage: requests.sh prepare|related|change|delta|inspect|refresh [new-work-directory]' >&2; exit 2 ;;
esac
