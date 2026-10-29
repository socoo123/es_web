#!/usr/bin/env bash
# Run one named stage from projects/travel-search. Credentials stay in curl config files.
set -euo pipefail
export F35_ES=https://127.0.0.1:19935
F35_LOCAL="$(cd infra/f35/.local && pwd)"
request() {
  local principal="$1" method="$2" path="$3"; shift 3
  curl -sS --config "$F35_LOCAL/$principal.curl" -X "$method" "$F35_ES$path" "$@" -w '\nHTTP %{http_code}\n'
}
case "${1:-}" in
prepare)
  python3 labs/f35/lab.py cleanup --out "${2:?new receipt directory}"
  request admin PUT /tut-f35-attractions-v001 -H 'Content-Type: application/json' --data-binary @search/f35/create-main.json
  request admin GET '/_cluster/health/tut-f35-attractions-v001?wait_for_status=green&timeout=30s'
  request admin POST '/tut-f35-attractions-v001/_bulk?refresh=true&wait_for_active_shards=all' -H 'Content-Type: application/x-ndjson' --data-binary @data/f35/v001.ndjson
  request admin POST /_aliases -H 'Content-Type: application/json' --data-binary @search/f35/aliases.json
  python3 labs/f35/lab.py credentials --out "${3:?new credential receipt directory}"
  ;;
permissions)
  # 200 read alias; 403 direct physical name and write; 403 cluster health.
  request reader GET /_security/_authenticate
  request reader POST /tut-f35-attractions-read/_search -H 'Content-Type: application/json' --data-binary '{"query":{"match_all":{}}}'
  request reader POST /tut-f35-attractions-v001/_search -H 'Content-Type: application/json' --data-binary '{"query":{"match_all":{}}}'
  request reader PUT '/tut-f35-attractions-write/_doc/p01?require_alias=true' -H 'Content-Type: application/json' --data-binary @data/f35/p01-updated.json
  request reader GET /_cluster/health
  # Writer updates/deletes documents; cannot search, refresh, or change settings.
  request writer PUT '/tut-f35-attractions-write/_doc/p01?require_alias=true&wait_for_active_shards=all' -H 'Content-Type: application/json' --data-binary @data/f35/p01-updated.json
  request writer DELETE '/tut-f35-attractions-write/_doc/p02?wait_for_active_shards=all'
  request writer POST /tut-f35-attractions-read/_search -H 'Content-Type: application/json' --data-binary '{"query":{"match_all":{}}}'
  request writer POST /tut-f35-attractions-write/_refresh
  request writer PUT /tut-f35-attractions-v001/_settings -H 'Content-Type: application/json' --data-binary '{"index.refresh_interval":"1s"}'
  request admin POST /tut-f35-attractions-v001/_refresh
  ;;
repair)
  # Fixed IDs: restore the two changed documents, then admin explicitly refreshes.
  request writer PUT '/tut-f35-attractions-write/_doc/p01?require_alias=true&wait_for_active_shards=all' -H 'Content-Type: application/json' --data-binary @data/f35/p01-original.json
  request writer PUT '/tut-f35-attractions-write/_doc/p02?require_alias=true&wait_for_active_shards=all' -H 'Content-Type: application/json' --data-binary @data/f35/p02-original.json
  request admin POST /tut-f35-attractions-v001/_refresh
  ;;
*) printf '%s\n' 'Usage: bash labs/f35/requests.sh prepare NEW_CLEANUP_DIR NEW_CREDENTIAL_DIR | permissions | repair' >&2; exit 2;;
esac
