#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

set -a
source .env
set +a

source pipeline.sh

echo "==> Done."
echo ""
jq '.summary' data/report.json
echo ""
echo "Pairing summary:"
jq '{total_meals, matched_weeks, sommelier_picks}' data/pairing_suggestions.json
