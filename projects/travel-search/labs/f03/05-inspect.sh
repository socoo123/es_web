#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"

curl --fail-with-body -sS "$ES_URL/tut-f03-attractions/_mapping?pretty"
curl --fail-with-body -sS "$ES_URL/tut-f03-attractions/_count?pretty"
curl --fail-with-body -sS "$ES_URL/tut-f03-attractions/_doc/a-hz-xihu?pretty"
