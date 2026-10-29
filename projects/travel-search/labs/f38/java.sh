#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
if [[ $# -ne 1 ]]; then echo 'Usage: bash labs/f38/java.sh inspect|drain|follow' >&2; exit 2; fi
test -s backend/target/f38-classpath.txt
test -s labs/f38/target/kafka-classpath.txt
F38_CP="backend/target/classes:$(cat backend/target/f38-classpath.txt):$(cat labs/f38/target/kafka-classpath.txt)"
mkdir -p labs/f38/target/classes
javac --release 25 -cp "$F38_CP" -d labs/f38/target/classes labs/f38/java/F38Consumer.java
exec java -Xms32m -Xmx128m -cp "labs/f38/target/classes:$F38_CP" F38Consumer "$1"
