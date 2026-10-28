#!/usr/bin/env bash
# Read and execute section by section from projects/travel-search. Compare outputs before proceeding.
# start the F34 cluster and Java service as described in README.md first.
set -u
export F34_ES=http://127.0.0.1:19834
export APP_URL=http://127.0.0.1:18082

# c01. Run lab.py cleanup first (new receipt directory) to remove only F34 resources.
# Expected 500: path is outside path.repo. Then register and verify the correct shared volume.
curl -sS -X PUT "$F34_ES/_snapshot/tut-f34-outside" -H 'Content-Type: application/json' --data-binary @search/f34/repository-bad.json
curl -sS -X PUT "$F34_ES/_snapshot/tut-f34-fs" -H 'Content-Type: application/json' --data-binary @search/f34/repository.json
curl -sS -X POST "$F34_ES/_snapshot/tut-f34-fs/_verify"
curl -sS -X PUT "$F34_ES/tut-f34-attractions-v001" -H 'Content-Type: application/json' --data-binary @search/f34/create-main.json
curl -sS -X POST "$F34_ES/tut-f34-attractions-v001/_bulk?wait_for_active_shards=all" -H 'Content-Type: application/x-ndjson' --data-binary @data/f34/v001.ndjson
curl -sS -X POST "$F34_ES/_aliases" -H 'Content-Type: application/json' --data-binary @search/f34/aliases-initial.json
curl -sS -X PUT "$F34_ES/tut-f34-attractions-v001/_block/write"
curl -sS -X POST "$F34_ES/tut-f34-attractions-v001/_refresh"
curl -sS -X POST "$F34_ES/tut-f34-attractions-v001/_search?allow_partial_search_results=false" -H 'Content-Type: application/json' --data-binary @search/f34/fields.json
# Observe Java: p01=6000, p02=0. The formal script uses async accepted + polling; this manual path waits synchronously.
curl -sS -X POST "$APP_URL/api/attractions/search" -H 'Content-Type: application/json' --data-binary @search/f34/input.json
curl -sS -X PUT "$F34_ES/_snapshot/tut-f34-fs/before-delete?wait_for_completion=true" -H 'Content-Type: application/json' --data-binary @search/f34/snapshot-good.json
curl -sS "$F34_ES/_snapshot/tut-f34-fs/before-delete"
curl -sS "$F34_ES/_snapshot/tut-f34-fs/before-delete/_status"

# c02. Resume writes only after the complete snapshot has finished. Both writes must succeed on two copies.
curl -sS -X PUT "$F34_ES/tut-f34-attractions-v001/_settings" -H 'Content-Type: application/json' --data-binary '{"index.blocks.write":false}'
curl -sS -X PUT "$F34_ES/tut-f34-attractions-v001/_doc/p01?wait_for_active_shards=all" -H 'Content-Type: application/json' --data-binary @data/f34/p01-updated.json
curl -sS -X DELETE "$F34_ES/tut-f34-attractions-v001/_doc/p02?wait_for_active_shards=all"
curl -sS -X POST "$F34_ES/tut-f34-attractions-v001/_refresh"
curl -sS -X POST "$F34_ES/tut-f34-attractions-v001/_search?allow_partial_search_results=false&preference=_only_nodes:travel-f34-n1" -H 'Content-Type: application/json' --data-binary @search/f34/fields.json
curl -sS -X POST "$F34_ES/tut-f34-attractions-v001/_search?allow_partial_search_results=false&preference=_only_nodes:travel-f34-n2" -H 'Content-Type: application/json' --data-binary @search/f34/fields.json
# Observe Java: only p01=6500. Never try to recover p02 by reading a replica.
curl -sS -X POST "$APP_URL/api/attractions/search" -H 'Content-Type: application/json' --data-binary @search/f34/input.json
curl -sS -X PUT "$F34_ES/tut-f34-risk" -H 'Content-Type: application/json' --data-binary @search/f34/create-risk.json
curl -sS -X PUT "$F34_ES/tut-f34-risk/_doc/risk-01" -H 'Content-Type: application/json' --data-binary @data/f34/risk.json
curl -sS -X POST "$F34_ES/tut-f34-risk/_refresh"
curl -sS "$F34_ES/_cat/shards/tut-f34-risk?format=json&h=index,shard,prirep,state,docs,node"
docker compose -f infra/f34/compose.yaml stop n2
# Wait for exactly one node and MAIN yellow (not global green); inspect timed_out=false before proceeding.
curl -sS "$F34_ES/_cluster/health/tut-f34-attractions-v001?wait_for_nodes=1&wait_for_status=yellow&wait_for_no_initializing_shards=true&timeout=120s"
curl -sS "$F34_ES/_cat/shards/tut-f34-risk?format=json&h=index,shard,prirep,state,node"
curl -sS -X PUT "$F34_ES/_snapshot/tut-f34-fs/missing-primary?wait_for_completion=true" -H 'Content-Type: application/json' --data-binary @search/f34/snapshot-partial.json
curl -sS "$F34_ES/_snapshot/tut-f34-fs/missing-primary"
curl -sS "$F34_ES/_snapshot/tut-f34-fs/missing-primary/_status"
# Restore original n2 before attempting restore; even if earlier output differs, bring it back first.
docker compose -f infra/f34/compose.yaml up -d n2
curl -sS "$F34_ES/_cluster/health?wait_for_nodes=2&wait_for_status=green&wait_for_no_relocating_shards=true&wait_for_no_initializing_shards=true&timeout=120s"
curl -sS "$F34_ES/tut-f34-risk/_count"
# Expected 500: incomplete risk index. Explicit partial=true demonstrates data loss, not complete recovery.
curl -sS -X POST "$F34_ES/_snapshot/tut-f34-fs/missing-primary/_restore?wait_for_completion=true" -H 'Content-Type: application/json' --data-binary @search/f34/restore-partial-refused.json
curl -sS -X POST "$F34_ES/_snapshot/tut-f34-fs/missing-primary/_restore?wait_for_completion=true" -H 'Content-Type: application/json' --data-binary @search/f34/restore-partial-accepted.json
curl -sS "$F34_ES/_cluster/health/tut-f34-partial-attractions-v001,tut-f34-partial-risk?wait_for_status=green&wait_for_no_initializing_shards=true&timeout=120s"
curl -sS "$F34_ES/tut-f34-partial-risk/_count"
curl -sS "$F34_ES/tut-f34-risk/_count"
curl -sS "$F34_ES/_alias/tut-f34-attractions-read"

# c03. Expected 500: open original index already has the same name. Keep it; use an isolated restore name.
curl -sS -X POST "$F34_ES/_snapshot/tut-f34-fs/before-delete/_restore?wait_for_completion=true" -H 'Content-Type: application/json' --data-binary @search/f34/restore-conflict.json
curl -sS -X POST "$F34_ES/_snapshot/tut-f34-fs/before-delete/_restore?wait_for_completion=true" -H 'Content-Type: application/json' --data-binary @search/f34/restore-good.json
curl -sS "$F34_ES/_cluster/health/tut-f34-restore-attractions-v001?wait_for_status=green&wait_for_no_relocating_shards=true&wait_for_no_initializing_shards=true&timeout=120s"
curl -sS -X POST "$F34_ES/tut-f34-restore-attractions-v001/_refresh"
curl -sS "$F34_ES/tut-f34-restore-attractions-v001/_count"
curl -sS "$F34_ES/tut-f34-restore-attractions-v001/_mapping"
curl -sS "$F34_ES/tut-f34-restore-attractions-v001/_settings?flat_settings=true"
curl -sS "$F34_ES/tut-f34-restore-attractions-v001/_recovery?detailed=true"
curl -sS -X POST "$F34_ES/tut-f34-restore-attractions-v001/_search?allow_partial_search_results=false" -H 'Content-Type: application/json' --data-binary @search/f34/fields.json
curl -sS -X POST "$F34_ES/tut-f34-restore-attractions-v001/_search?allow_partial_search_results=false" -H 'Content-Type: application/json' --data-binary @search/f34/search.json
curl -sS "$F34_ES/tut-f34-restore-attractions-v001/_alias"
# Observe live Java still p01=6500; isolated restore did not change the read alias.
curl -sS -X POST "$APP_URL/api/attractions/search" -H 'Content-Type: application/json' --data-binary @search/f34/input.json
# Only after fields, settings, queries and aliases match: read the validated historical copy.
curl -sS -X POST "$F34_ES/_aliases" -H 'Content-Type: application/json' --data-binary @search/f34/aliases-restored.json
curl -sS "$F34_ES/_alias/tut-f34-attractions-read"
curl -sS -X POST "$APP_URL/api/attractions/search" -H 'Content-Type: application/json' --data-binary @search/f34/input.json
curl -sS "$F34_ES/tut-f34-attractions-v001/_count"
# Cleanup and down via lab.py after recording results. Never delete or alter files inside the repository.
