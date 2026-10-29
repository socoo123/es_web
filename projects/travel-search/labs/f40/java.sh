#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
test -s backend/target/f40-classpath.txt
test -s labs/f40/target/projection-classpath.txt
F40_CP="backend/target/classes:$(cat backend/target/f40-classpath.txt):$(cat labs/f40/target/projection-classpath.txt)"
mkdir -p labs/f40/target/classes
javac --release 25 -cp "$F40_CP" -d labs/f40/target/classes labs/f40/java/F40Consumer.java
exec java -Xms32m -Xmx128m -cp "labs/f40/target/classes:$F40_CP" F40Consumer "$@"
