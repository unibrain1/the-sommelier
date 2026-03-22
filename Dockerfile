# hadolint global ignore=DL3008
FROM python:3.12-slim AS base

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Install nginx, curl, jq, cron, and 1Password CLI
RUN apt-get update && apt-get install -y --no-install-recommends \
    nginx curl jq gnupg cron \
    && curl -sS https://downloads.1password.com/linux/keys/1password.asc | \
       gpg --dearmor --output /usr/share/keyrings/1password-archive-keyring.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/1password-archive-keyring.gpg] https://downloads.1password.com/linux/debian/amd64 stable main" \
       > /etc/apt/sources.list.d/1password.list \
    && apt-get update && apt-get install -y --no-install-recommends 1password-cli \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy application code
COPY scripts/ /app/scripts/
COPY site/ /app/site/
COPY pipeline.sh fetch_docker.sh entrypoint.sh /app/
COPY nginx.conf /etc/nginx/sites-available/default

WORKDIR /app

RUN mkdir -p /app/data && chmod +x /app/entrypoint.sh /app/fetch_docker.sh /app/pipeline.sh

EXPOSE 80

ENTRYPOINT ["/app/entrypoint.sh"]
