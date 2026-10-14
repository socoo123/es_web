#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"

# 相同索引、相同 _id、相同完整文档；不会多出第二条景点。
bash labs/f03/03-write.sh
curl --fail-with-body -sS -X POST "$ES_URL/tut-f03-attractions/_refresh?pretty"
curl --fail-with-body -sS "$ES_URL/tut-f03-attractions/_count?pretty"
curl --fail-with-body -sS "$ES_URL/tut-f03-attractions/_doc/a-hz-xihu?pretty"
