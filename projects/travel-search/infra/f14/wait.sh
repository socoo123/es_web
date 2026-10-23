#!/usr/bin/env bash
set -euo pipefail
endpoint="${ES_URL:-http://127.0.0.1:19214}"
for attempt in $(seq 1 90); do
  if curl --fail --silent --show-error "$endpoint/" > /dev/null 2>&1; then
    echo "F14 ES ready: $endpoint"
    exit 0
  fi
  sleep 1
done
echo "F14 ES did not become ready: $endpoint" >&2
exit 1
