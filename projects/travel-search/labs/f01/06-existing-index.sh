#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"

# 这里故意不加 --fail-with-body：保留预期 400 的正文供观察。
curl -sS -X PUT "$ES_URL/tut-f01-attractions?pretty" \
  -H 'Content-Type: application/json' \
  --data-binary @search/f01/index.json
