#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

set -a
source .env
set +a

source pipeline.sh

echo "==> Copying site to web root..."
cp -r site/* /usr/share/nginx/html/

echo "==> Done."
jq '.summary' data/report.json
echo ""
echo "Pairing summary:"
jq '{total_meals, matched_weeks, sommelier_picks}' data/pairing_suggestions.json
