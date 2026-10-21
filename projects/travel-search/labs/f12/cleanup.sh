#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"
# Only these two F12 resources. 404 means already absent; other errors stop cleanup.
python3 - <<'PY'
from labs.f12.lab import call
for index in ['tut-f12-attractions','tut-f12-graduation']:
    import urllib.request,urllib.error
    try:
        urllib.request.urlopen('http://127.0.0.1:19200/'+index).close()
    except urllib.error.HTTPError as e:
        if e.code != 404: raise
    else: call('DELETE','/'+index)
    call('GET','/'+index,expected=404)
PY
