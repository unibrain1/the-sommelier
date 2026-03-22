# Wine Plan

A personal wine cellar management system that maintains a multi-year drinking plan synchronized with a live [CellarTracker](https://www.cellartracker.com) inventory and a Google Calendar menu plan.

## What It Does

- Fetches your CellarTracker inventory nightly
- Pulls your meal plan from Google Calendar
- Generates wine-food pairing suggestions ("The Sommelier") based on what's in your cellar
- Prioritizes bottles that need drinking soon (past peak, expiring)
- Publishes a self-contained HTML wine plan you can open in any browser

## Quick Start

### Prerequisites

- Python 3.12+
- [1Password CLI](https://developer.1password.com/docs/cli/) (`op`) for credential management
- A CellarTracker account with credentials stored in 1Password
- A Google Calendar with meal plans (see [Menu Guide](docs/menu-guide.md))

### Setup

1. Clone the repo
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create `.env` with your credentials:
   ```
   OP_SERVICE_ACCOUNT_TOKEN=<your-token>
   USERNAME="op://<vault>/<item>/username"
   PASSWORD="op://<vault>/<item>/password"
   GOOGLE_CALENDAR_ICS_URL=https://calendar.google.com/calendar/ical/.../basic.ics
   ```

### Run

```bash
bash fetch.sh
open site/index.html
```

### Docker (Homelab)

```bash
docker compose up --build
```

Runs the pipeline at startup and nightly at 2 AM. Serves the plan at `http://localhost:8080`.

## The Sommelier

The pairing engine matches your meal plan keywords (proteins, cuisines, cooking methods) against your cellar inventory and suggests wines to drink. Suggestions prioritize:

1. Past-peak bottles that need opening now
2. Bottles expiring this year or next
3. Bottles in their peak drinking window

Each card on the plan shows:
- The planned wine for the week
- Menu items with pairing indicators
- Specific bottle suggestions from your cellar when a better match exists

See the [Menu Guide](docs/menu-guide.md) for tips on writing calendar entries that produce the best pairing suggestions.

## Project Structure

```
site/index.html        — Self-contained wine plan (HTML/CSS/JS)
scripts/               — Pipeline scripts (Python)
docs/                  — Workflow instructions and menu guide
pipeline.sh            — Shared pipeline logic
fetch.sh               — Local entry point
fetch_docker.sh        — Docker entry point
Dockerfile             — Container definition
docker-compose.yml     — Container orchestration
```

## Documentation

- [CLAUDE.md](CLAUDE.md) — Project conventions for AI-assisted development
- [docs/fetch.md](docs/fetch.md) — Full pipeline workflow and plan criteria
- [docs/menu-guide.md](docs/menu-guide.md) — How to write menu entries for best pairings
