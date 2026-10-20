#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"
curl --fail-with-body -sS -X POST "$APP_URL/api/attractions/facet-search" -H 'Content-Type: application/json' --data-binary @search/f09/input-selected.json
curl --fail-with-body -sS -X POST "$APP_URL/api/attractions/facet-search" -H 'Content-Type: application/json' --data-binary @search/f09/input-multi-city.json
curl --fail-with-body -sS -X POST "$APP_URL/api/attractions/facet-search" -H 'Content-Type: application/json' --data-binary @search/f09/input-overlap.json
curl --fail-with-body -sS -X POST "$APP_URL/api/attractions/facet-search" -H 'Content-Type: application/json' --data-binary @search/f09/input-empty.json
curl --fail-with-body -sS -X POST "$APP_URL/api/attractions/facet-search" -H 'Content-Type: application/json' --data-binary @search/f09/input-unselected.json
