#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"
curl --fail-with-body -sS -X POST "$APP_URL/api/attractions/sort-search" -H 'Content-Type: application/json' --data-binary @search/f10/input-relevance.json
printf '\n'
curl --fail-with-body -sS -X POST "$APP_URL/api/attractions/sort-search" -H 'Content-Type: application/json' --data-binary @search/f10/input-price.json
printf '\n'
curl --fail-with-body -sS -X POST "$APP_URL/api/attractions/sort-search" -H 'Content-Type: application/json' --data-binary @search/f10/input-distance.json
printf '\n'
curl --fail-with-body -sS -X POST "$APP_URL/api/attractions/sort-search" -H 'Content-Type: application/json' --data-binary @search/f10/input-price-scores.json
printf '\n'
curl --fail-with-body -sS -X POST "$APP_URL/api/attractions/sort-search" -H 'Content-Type: application/json' --data-binary @search/f10/input-hz-distance.json
printf '\n'
curl --fail-with-body -sS -X POST "$APP_URL/api/attractions/sort-search" -H 'Content-Type: application/json' --data-binary @search/f10/input-budget-price.json
printf '\n'
curl --fail-with-body -sS -X POST "$APP_URL/api/attractions/sort-search" -H 'Content-Type: application/json' --data-binary @search/f10/input-empty.json
printf '\n'
