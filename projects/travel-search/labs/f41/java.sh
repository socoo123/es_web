#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
test -s backend/target/f41-classpath.txt
test -s labs/f41/target/projection-classpath.txt
F41_CP="backend/target/classes:$(cat backend/target/f41-classpath.txt):$(cat labs/f41/target/projection-classpath.txt)"
mkdir -p labs/f41/target/classes
javac --release 25 -cp "$F41_CP" -d labs/f41/target/classes labs/f41/java/F41Worker.java
exec java -Xms32m -Xmx128m -cp "labs/f41/target/classes:$F41_CP" F41Worker "$@"
