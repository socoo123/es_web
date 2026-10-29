#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
if [[ $# -ne 1 ]]; then echo 'Usage: bash labs/f37/java.sh inspect|drain|follow' >&2; exit 2; fi
test -s backend/target/f37-classpath.txt
test -s labs/f37/target/kafka-classpath.txt
F37_CP="backend/target/classes:$(cat backend/target/f37-classpath.txt):$(cat labs/f37/target/kafka-classpath.txt)"
mkdir -p labs/f37/target/classes
javac --release 25 -cp "$F37_CP" -d labs/f37/target/classes labs/f37/java/F37Consumer.java
exec java -Xms32m -Xmx128m -cp "labs/f37/target/classes:$F37_CP" F37Consumer "$1"
