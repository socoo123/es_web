#!/usr/bin/env bash
set -euo pipefail
LAB_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd -- "$LAB_DIR/../.." && pwd)"
cd "$PROJECT_DIR"
F32_CP="backend/target/classes:$(cat backend/target/f32-classpath.txt)"
exec java --class-path "$F32_CP" labs/f32/java/AliasWriter.java "$@"
