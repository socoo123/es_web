#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
if [[ $# -ne 1 ]]; then echo 'Usage: bash labs/f36/java.sh projection.ndjson' >&2; exit 2; fi
test -s backend/target/f36-classpath.txt
F36_CP="backend/target/classes:$(cat backend/target/f36-classpath.txt)"
mkdir -p backend/target/f36-classes
javac --release 25 -cp "$F36_CP" -d backend/target/f36-classes labs/f36/java/ProjectionImport.java
java -cp "backend/target/f36-classes:$F36_CP" ProjectionImport "$1"
