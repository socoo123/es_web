#!/usr/bin/env bash
set -euo pipefail
endpoint="${ES_URL:-http://127.0.0.1:19220}"
for attempt in $(seq 1 90); do
  # GET / may return 200 before cluster state recovery. Wait for actual health.
  if curl --max-time 4 --fail --silent "$endpoint/_cluster/health?wait_for_status=yellow&wait_for_nodes=1&timeout=2s" | python3 -c 'import json,sys; r=json.load(sys.stdin); sys.exit(0 if not r["timed_out"] and r["status"] in {"green","yellow"} and r["number_of_nodes"] == 1 else 1)' 2>/dev/null; then
    echo "F20 ES recovered: $endpoint"
    exit 0
  fi
  sleep 1
done
echo "F20 ES did not recover: $endpoint" >&2
exit 1
