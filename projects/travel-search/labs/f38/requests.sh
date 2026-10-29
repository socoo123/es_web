#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
F38_ES=http://127.0.0.1:20238
case "${1:-}" in
  changes|delete|offline)
    docker compose --profile mysql -f infra/f38/compose.yaml exec -T mysql mysql --defaults-extra-file=/run/secrets/admin-cnf --batch --raw --skip-column-names --default-character-set=utf8mb4 < "data/f38/$1.sql"
    ;;
  inspect)
    docker compose --profile mysql -f infra/f38/compose.yaml exec -T mysql mysql --defaults-extra-file=/run/secrets/admin-cnf --batch --raw --skip-column-names --default-character-set=utf8mb4 < data/f38/positions.sql
    curl --fail-with-body -sS http://127.0.0.1:18238/connectors/f38-mysql/status
    curl --fail-with-body -sS http://127.0.0.1:18238/connectors/f38-mysql/offsets
    curl --fail-with-body -sS -X POST "$F38_ES/tut-f38-attractions-read/_search?allow_partial_search_results=false" -H 'Content-Type: application/json' --data-binary @search/f38/all.json
    ;;
  refresh)
    curl --fail-with-body -sS -X POST "$F38_ES/tut-f38-attractions-v001/_refresh"
    ;;
  stop-connect|start-connect)
    if [[ "$1" == stop-connect ]]; then
      docker compose --profile mysql -f infra/f38/compose.yaml stop connect
    else
      docker compose --profile mysql -f infra/f38/compose.yaml start connect
    fi
    ;;
  *) echo 'Usage: requests.sh changes|delete|offline|inspect|refresh|stop-connect|start-connect' >&2; exit 2 ;;
esac
