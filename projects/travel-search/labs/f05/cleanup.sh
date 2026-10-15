#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"

# 只删除 F05 景点索引；不会触碰 F03/F04 或读者业务索引。
curl --fail-with-body -sS -X DELETE "$ES_URL/tut-f05-attractions?ignore_unavailable=true&pretty"
