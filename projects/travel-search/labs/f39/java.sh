#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
if [[ $# -ne 1 ]]; then echo 'Usage: bash labs/f39/java.sh inspect|drain|follow' >&2; exit 2; fi
test -s backend/target/f39-classpath.txt
test -s labs/f39/target/projection-classpath.txt
F39_CP="backend/target/classes:$(cat backend/target/f39-classpath.txt):$(cat labs/f39/target/projection-classpath.txt)"
mkdir -p labs/f39/target/classes
javac --release 25 -cp "$F39_CP" -d labs/f39/target/classes labs/f39/java/F39Consumer.java
exec java -Xms32m -Xmx128m -cp "labs/f39/target/classes:$F39_CP" F39Consumer "$1"
