#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"
# 只删除本课12份教学资料；不删其他索引、容器或持久卷。
curl --fail-with-body -sS -X DELETE "$ES_URL/tut-f07-attractions?pretty"
