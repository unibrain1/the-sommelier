#!/usr/bin/env bash
set -euo pipefail

echo "==> Starting wine plan service..."

# Run the pipeline once at startup
echo "==> Running initial sync..."
bash /app/fetch_docker.sh || echo "WARNING: Initial sync failed, serving stale plan"

# Set up periodic sync (default: 2:00 AM daily, configurable via SYNC_SCHEDULE env var)
SCHEDULE="${SYNC_SCHEDULE:-0 2 * * *}"
echo "${SCHEDULE} cd /app && bash fetch_docker.sh >> /proc/1/fd/1 2>&1" | crontab -
echo "    Scheduled sync: ${SCHEDULE}"

# Start cron daemon in background
service cron start

# Start nginx in foreground (serves directly from /app/site via volume mount)
echo "==> Starting web server on port 80..."
nginx -g 'daemon off;'
