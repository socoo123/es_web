#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"

# 刻意不给 properties，观察默认动态映射。
curl --fail-with-body -sS -X PUT "$ES_URL/tut-f04-dynamic?pretty" \
  -H 'Content-Type: application/json' --data-binary '{"settings":{"number_of_shards":1,"number_of_replicas":0}}'
curl --fail-with-body -sS -X PUT "$ES_URL/tut-f04-dynamic/_doc/a-hz-tea?pretty" \
  -H 'Content-Type: application/json' --data-binary @data/f04/dynamic.json
curl --fail-with-body -sS "$ES_URL/tut-f04-dynamic/_mapping?pretty"
# 预期 HTTP 400；省略 fail 选项以阅读 error.type，不能只看 curl 退出码。
curl -sS -X PUT "$ES_URL/tut-f04-dynamic/_mapping?pretty" \
  -H 'Content-Type: application/json' --data-binary @search/f04/change-type.json
# 用新索引的正确规则重新导入正确资料；原错误索引仍在，未自动迁移。
curl --fail-with-body -sS -X PUT "$ES_URL/tut-f04-rebuilt?pretty" \
  -H 'Content-Type: application/json' --data-binary @search/f04/index.json
curl --fail-with-body -sS -X PUT "$ES_URL/tut-f04-rebuilt/_doc/a-hz-tea?pretty" \
  -H 'Content-Type: application/json' --data-binary @data/f04/one.json
curl --fail-with-body -sS -X POST "$ES_URL/tut-f04-rebuilt/_refresh?pretty"
curl --fail-with-body -sS "$ES_URL/tut-f04-rebuilt/_count?pretty"
curl --fail-with-body -sS "$ES_URL/tut-f04-rebuilt/_mapping?pretty"
