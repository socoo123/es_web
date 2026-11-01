#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
F45_CP="backend/target/classes:$(cat backend/target/f45-classpath.txt):$(cat labs/f45/target/projection-classpath.txt)"
if [[ "${1:-}" == compile ]]; then
  mkdir -p labs/f45/target/classes
  javac --release 25 -cp "$F45_CP" -d labs/f45/target/classes labs/f45/java/F45Lab.java
  exit
fi
exec java -Xms32m -Xmx160m -cp "labs/f45/target/classes:$F45_CP" F45Lab "$@"
