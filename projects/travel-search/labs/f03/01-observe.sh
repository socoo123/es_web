#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"

curl --fail-with-body -sS "$ES_URL/?pretty"
curl --fail-with-body -sS \
  "$ES_URL/_cat/nodes?format=json&h=name,ip,node.role,master"
curl --fail-with-body -sS "$ES_URL/_cluster/health?pretty"
