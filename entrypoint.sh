#!/usr/bin/env bash
set -euo pipefail

echo "==> Starting wine plan service..."

# Run the pipeline once at startup
echo "==> Running initial sync..."
bash /app/fetch_docker.sh || echo "WARNING: Initial sync failed, serving stale plan"

# Set up nightly cron (2:00 AM)
echo "0 2 * * * cd /app && bash fetch_docker.sh >> /var/log/wine-sync.log 2>&1" | crontab -

# Start cron daemon in background
service cron start

# Start nginx in foreground
echo "==> Starting web server on port 80..."
nginx -g 'daemon off;'
