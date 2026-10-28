#!/usr/bin/env bash
# Manual alternative to lab.py run. Run from projects/travel-search, on F33 only.
# This resets only the TWO named F33 indices, including their aliases and blocks.
set -euo pipefail
export F33_ES=http://127.0.0.1:19733

# c01: explicit old/new schema, fixed initial copy.
curl -sS -X DELETE "$F33_ES/tut-f33-attractions-v001"
curl -sS -X DELETE "$F33_ES/tut-f33-attractions-v002"
curl -sS -X PUT "$F33_ES/tut-f33-attractions-v001" -H 'Content-Type: application/json' --data-binary @search/f33/create-old.json
curl -sS -X POST "$F33_ES/tut-f33-attractions-v001/_bulk?wait_for_active_shards=all" -H 'Content-Type: application/x-ndjson' --data-binary @data/f33/v001.ndjson
curl -sS -X POST "$F33_ES/tut-f33-attractions-v001/_refresh"
curl -sS -X POST "$F33_ES/_aliases" -H 'Content-Type: application/json' --data-binary @search/f33/aliases-initial.json
curl -sS -X PUT "$F33_ES/tut-f33-attractions-v001/_mapping" -H 'Content-Type: application/json' --data-binary @search/f33/incompatible-mapping.json
curl -sS -X PUT "$F33_ES/tut-f33-attractions-v002" -H 'Content-Type: application/json' --data-binary @search/f33/create-new.json
curl -sS -X POST "$F33_ES/tut-f33-attractions-v001/_analyze" -H 'Content-Type: application/json' --data-binary @search/f33/analyze.json
curl -sS -X POST "$F33_ES/tut-f33-attractions-v002/_analyze" -H 'Content-Type: application/json' --data-binary @search/f33/analyze.json
curl -sS -X POST "$F33_ES/_reindex?wait_for_completion=true&wait_for_active_shards=all&refresh=true&slices=1" -H 'Content-Type: application/json' --data-binary @search/f33/reindex.json
curl -sS -X POST "$F33_ES/tut-f33-attractions-v002/_search?allow_partial_search_results=false" -H 'Content-Type: application/json' --data-binary @search/f33/search.json

# Observe 01: Java/read still uses v001. Searching 西湖 returns zero.
curl -sS -X POST "$APP_URL/api/attractions/search" -H 'Content-Type: application/json' --data-binary @search/f33/input.json

# c02: complete the initial reindex BEFORE changing the old source.
curl -sS -X PUT "$F33_ES/tut-f33-attractions-write/_doc/p01?require_alias=true&wait_for_active_shards=all" -H 'Content-Type: application/json' --data-binary @data/f33/p01-updated.json
bash labs/f33/java.sh tut-f33-attractions-write p01 data/f33/p01-updated.json
curl -sS -X DELETE "$F33_ES/tut-f33-attractions-write/_doc/p02?wait_for_active_shards=all"
bash labs/f33/java.sh tut-f33-attractions-write p07 data/f33/p07.json
curl -sS -X POST "$F33_ES/tut-f33-attractions-v001/_refresh"
curl -sS "$F33_ES/tut-f33-attractions-v001/_count"
curl -sS "$F33_ES/tut-f33-attractions-v002/_count"
curl -sS -X POST "$F33_ES/_reindex?wait_for_completion=true&wait_for_active_shards=all&refresh=true&slices=1" -H 'Content-Type: application/json' --data-binary @search/f33/reindex.json
curl -sS -X POST "$F33_ES/tut-f33-attractions-v002/_search?allow_partial_search_results=false" -H 'Content-Type: application/json' --data-binary @search/f33/search.json

# Pause ALL writers here; this file is the only writer in the manual exercise.
curl -sS -X PUT "$F33_ES/tut-f33-attractions-v001/_block/write"
curl -sS -X PUT "$F33_ES/tut-f33-attractions-write/_doc/p09?require_alias=true" -H 'Content-Type: application/json' --data-binary @data/f33/p09.json
bash labs/f33/java.sh tut-f33-attractions-write p09 data/f33/p09.json
curl -sS -X POST "$F33_ES/tut-f33-attractions-v001/_refresh"
curl -sS "$F33_ES/_alias/tut-f33-attractions-read,tut-f33-attractions-write"
curl -sS -X DELETE "$F33_ES/tut-f33-attractions-v002"
curl -sS -X PUT "$F33_ES/tut-f33-attractions-v002" -H 'Content-Type: application/json' --data-binary @search/f33/create-new.json
curl -sS -X POST "$F33_ES/_reindex?wait_for_completion=true&wait_for_active_shards=all&refresh=true&slices=1" -H 'Content-Type: application/json' --data-binary @search/f33/reindex.json
for F33_INDEX in tut-f33-attractions-v001 tut-f33-attractions-v002; do
  curl -sS "$F33_ES/$F33_INDEX/_count"
  curl -sS -X POST "$F33_ES/$F33_INDEX/_search?allow_partial_search_results=false" -H 'Content-Type: application/json' -d '{"size":20,"track_total_hits":true,"query":{"match_all":{}},"sort":[{"attraction_id":"asc"}]}'
  curl -sS "$F33_ES/$F33_INDEX/_doc/p02"
done
curl -sS -X POST "$F33_ES/tut-f33-attractions-v002/_search?allow_partial_search_results=false" -H 'Content-Type: application/json' --data-binary @search/f33/search.json

# Observe 02: old search still works while writes are blocked. Stop if checks differ.
curl -sS -X POST "$APP_URL/api/attractions/search" -H 'Content-Type: application/json' --data-binary @search/f33/input.json

# c03: a wrong must_exist precondition rejects the entire action list.
curl -sS -X POST "$F33_ES/_aliases" -H 'Content-Type: application/json' --data-binary @search/f33/aliases-bad-precondition.json
curl -sS "$F33_ES/_alias/tut-f33-attractions-read,tut-f33-attractions-write"
curl -sS -X POST "$F33_ES/_aliases" -H 'Content-Type: application/json' --data-binary @search/f33/aliases-switch.json
curl -sS "$F33_ES/_alias/tut-f33-attractions-read,tut-f33-attractions-write"
# Observe 03: p01=6500, p07=1500. Do NOT allow any business writes yet.
curl -sS -X POST "$APP_URL/api/attractions/search" -H 'Content-Type: application/json' --data-binary @search/f33/input.json
curl -sS -X POST "$F33_ES/_aliases" -H 'Content-Type: application/json' --data-binary @search/f33/aliases-rollback.json
curl -sS "$F33_ES/_alias/tut-f33-attractions-read,tut-f33-attractions-write"
# Observe 04: old recall returns; v001 is still write-blocked.
curl -sS -X POST "$APP_URL/api/attractions/search" -H 'Content-Type: application/json' --data-binary @search/f33/input.json
curl -sS -X PUT "$F33_ES/tut-f33-attractions-write/_doc/p09?require_alias=true" -H 'Content-Type: application/json' --data-binary @data/f33/p09.json
curl -sS -X POST "$F33_ES/_aliases" -H 'Content-Type: application/json' --data-binary @search/f33/aliases-switch.json

# Resume the controlled writer ONLY NOW; p08 goes to v002.
bash labs/f33/java.sh tut-f33-attractions-write p08 data/f33/p08.json
curl -sS -X POST "$F33_ES/tut-f33-attractions-v002/_refresh"
curl -sS "$F33_ES/tut-f33-attractions-v001/_doc/p08"
curl -sS "$F33_ES/tut-f33-attractions-v002/_doc/p08"
# Observe 05: p01=6500, p07=1500, p08=2000; old target lacks p08.
curl -sS -X POST "$APP_URL/api/attractions/search" -H 'Content-Type: application/json' --data-binary @search/f33/input.json
