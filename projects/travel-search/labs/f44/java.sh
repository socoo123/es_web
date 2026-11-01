#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
F44_CP="backend/target/classes:$(cat backend/target/f44-classpath.txt)"
if [[ "${1:-}" == compile ]]; then
  mkdir -p labs/f44/target/classes
  javac --release 25 -cp "$F44_CP" -d labs/f44/target/classes labs/f44/java/F44Search.java
  exit
fi
exec java -Xms64m -Xmx192m -cp "labs/f44/target/classes:$F44_CP" F44Search "$@"
