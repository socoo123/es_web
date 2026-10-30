#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
F43_CP="backend/target/classes:$(cat backend/target/f43-classpath.txt)"
if [[ "${1:-}" == compile ]]; then
  mkdir -p labs/f43/target/classes
  javac --release 25 -cp "$F43_CP" -d labs/f43/target/classes labs/f43/java/F43Bulk.java
  exit
fi
exec java -Xms64m -Xmx192m -cp "labs/f43/target/classes:$F43_CP" F43Bulk "$@"
