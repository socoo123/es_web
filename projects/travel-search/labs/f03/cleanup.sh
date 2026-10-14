#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"

# 只删除本课索引和里面的景点。不使用通配符，不删除数据卷。
curl --fail-with-body -sS -X DELETE "$ES_URL/tut-f03-attractions?pretty"
