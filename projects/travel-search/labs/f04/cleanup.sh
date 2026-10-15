#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"

# 仅删除本课四个索引；不存在时显式允许忽略，不影响其他课和数据卷。
curl --fail-with-body -sS -X DELETE \
  "$ES_URL/tut-f04-attractions,tut-f04-boundaries,tut-f04-dynamic,tut-f04-rebuilt?ignore_unavailable=true&pretty"
