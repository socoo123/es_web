#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"
# Close Java cursors in the observation page before deleting this lesson's index.
code=$(curl -sS -o /dev/null -w '%{http_code}' -X DELETE "$ES_URL/tut-f11-attractions")
case "$code" in 200|404) printf 'tut-f11-attractions: HTTP %s\n' "$code";; *) exit 1;; esac
