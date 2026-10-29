#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
F37_ES=http://127.0.0.1:20137
case "${1:-}" in
  changes|delete|offline)
    docker compose -f infra/f37/compose.yaml exec -T postgres psql -X -qAt -v ON_ERROR_STOP=1 -U travel -d travel_f37 < "data/f37/$1.sql"
    ;;
  inspect)
    docker compose -f infra/f37/compose.yaml exec -T postgres psql -X -qAt -v ON_ERROR_STOP=1 -U travel -d travel_f37 < data/f37/positions.sql
    curl --fail-with-body -sS http://127.0.0.1:18137/connectors/f37-pg/status
    curl --fail-with-body -sS http://127.0.0.1:18137/connectors/f37-pg/offsets
    curl --fail-with-body -sS -X POST "$F37_ES/tut-f37-attractions-read/_search?allow_partial_search_results=false" -H 'Content-Type: application/json' --data-binary @search/f37/all.json
    ;;
  refresh)
    curl --fail-with-body -sS -X POST "$F37_ES/tut-f37-attractions-v001/_refresh"
    ;;
  stop-connect|start-connect)
    if [[ "$1" == stop-connect ]]; then
      docker compose -f infra/f37/compose.yaml stop connect
    else
      docker compose -f infra/f37/compose.yaml start connect
    fi
    ;;
  *) echo 'Usage: requests.sh changes|delete|offline|inspect|refresh|stop-connect|start-connect' >&2; exit 2 ;;
esac
