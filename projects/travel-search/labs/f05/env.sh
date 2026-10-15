#!/usr/bin/env bash
F05_PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$F05_PROJECT_ROOT"
export ES_URL=http://127.0.0.1:19200
