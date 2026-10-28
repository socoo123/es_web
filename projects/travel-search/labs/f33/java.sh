#!/usr/bin/env bash
set -euo pipefail
LAB_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd -- "$LAB_DIR/../.." && pwd)"
cd "$PROJECT_DIR"
F33_CP="backend/target/classes:$(cat backend/target/f33-classpath.txt)"
exec java --class-path "$F33_CP" labs/f33/java/AliasWriter.java "$@"
