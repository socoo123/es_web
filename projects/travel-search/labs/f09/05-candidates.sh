#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"
curl --fail-with-body -sS -X PUT "$ES_URL/tut-f09-candidates?pretty" -H 'Content-Type: application/json' --data-binary @search/f09/candidates-index.json
curl --fail-with-body -sS "$ES_URL/_cluster/health/tut-f09-candidates?wait_for_status=green&timeout=30s&pretty"
# 对照两份响应的 shards[0][0].shard，a 与 b 必须落到不同主分片。
curl --fail-with-body -sS "$ES_URL/tut-f09-candidates/_search_shards?routing=a&pretty"
curl --fail-with-body -sS "$ES_URL/tut-f09-candidates/_search_shards?routing=b&pretty"
curl --fail-with-body -sS -X POST "$ES_URL/tut-f09-candidates/_bulk?pretty" -H 'Content-Type: application/x-ndjson' --data-binary @data/f09/candidates.ndjson
curl --fail-with-body -sS -X POST "$ES_URL/tut-f09-candidates/_refresh?pretty"
curl --fail-with-body -sS "$ES_URL/tut-f09-candidates/_count?pretty"
curl --fail-with-body -sS -X POST "$ES_URL/tut-f09-candidates/_search?pretty" -H 'Content-Type: application/json' --data-binary @search/f09/candidate-small.json
curl --fail-with-body -sS -X POST "$ES_URL/tut-f09-candidates/_search?pretty" -H 'Content-Type: application/json' --data-binary @search/f09/candidate-wide.json
curl --fail-with-body -sS -X POST "$ES_URL/tut-f09-candidates/_search?pretty" -H 'Content-Type: application/json' --data-binary @search/f09/candidate-all.json
