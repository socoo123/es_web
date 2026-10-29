#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
if [[ $# -lt 1 || $# -gt 2 ]]; then echo 'Usage: requests.sh inspect|refresh|shared|transfer|naive|delete-tag|close|delete-root|reopen [new-output-directory]' >&2; exit 2; fi
case "$1" in inspect|refresh|shared|transfer|naive|delete-tag|close|delete-root|reopen) ;; *) exit 2 ;; esac
exec python3 labs/f39/lab.py "$1" --out "${2:-/tmp/f39-$1-$(date +%Y%m%d-%H%M%S)-$RANDOM}"
