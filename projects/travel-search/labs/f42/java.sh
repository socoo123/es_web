#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
test -s backend/target/f42-classpath.txt
test -s labs/f42/target/projection-classpath.txt
F42_CP="backend/target/classes:$(cat backend/target/f42-classpath.txt):$(cat labs/f42/target/projection-classpath.txt)"
mkdir -p labs/f42/target/classes
javac --release 25 -cp "$F42_CP" -d labs/f42/target/classes labs/f42/java/F42Worker.java
exec java -Xms32m -Xmx128m -cp "labs/f42/target/classes:$F42_CP" F42Worker "$@"
