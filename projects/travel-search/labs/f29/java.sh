#!/usr/bin/env bash
set -euo pipefail
LAB_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd -- "$LAB_DIR/../.." && pwd)"
cd "$PROJECT_DIR"
# First build backend and run dependency:build-classpath (README). All artifacts remain in target/.
F29_CP="backend/target/classes:$(cat backend/target/f29-classpath.txt)"
exec java --class-path "$F29_CP" labs/f29/java/RoutingLab.java
