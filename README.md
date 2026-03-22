# Wine Plan

A personal wine cellar management system that maintains a multi-year drinking plan synchronized with a live [CellarTracker](https://www.cellartracker.com) inventory and a Google Calendar menu plan.

## What It Does

- Fetches your CellarTracker inventory nightly
- Pulls your meal plan from Google Calendar
- Generates wine-food pairing suggestions ("The Sommelier") based on what's in your cellar
- Prioritizes bottles that need drinking soon (past peak, expiring)
- Validates all wine metadata against CellarTracker (system of record)
- Publishes a web app you can view in any browser

## Architecture

Data, presentation, and style are cleanly separated:

```
site/
  plan.json                  ← Plan data (allWeeks + changelog)
  pairing_suggestions.json   ← Generated pairings
  index.html                 ← App shell (JS rendering)
  style.css                  ← Styles (Sandstone theme)
```

The pipeline generates JSON data files. The HTML app shell fetches them on load — no data is embedded in the HTML.

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
# Then serve site/ with any web server, e.g.:
python3 -m http.server -d site 8080
```

### Docker (Homelab)

```bash
# Persistent service (nightly sync at 2 AM + nginx)
docker compose up --build

# One-shot test run
docker compose run --rm run-now
```

Container name: `wine-planner`. Serves the plan at `http://localhost:8080`.

## The Sommelier

The pairing engine matches your meal plan keywords (proteins, cuisines, cooking methods) against your cellar inventory and suggests wines to drink. Suggestions prioritize:

1. Past-peak bottles that need opening now
2. Bottles expiring this year or next
3. Bottles in their peak drinking window

Each card on the plan shows:
- The planned wine for the week
- Menu items with pairing indicators and suggested bottles (with window and score)

See the [Menu Guide](docs/menu-guide.md) for tips on writing calendar entries that produce the best pairing suggestions.

## Documentation

- [CLAUDE.md](CLAUDE.md) — Project conventions for AI-assisted development
- [docs/fetch.md](docs/fetch.md) — Full pipeline workflow and plan criteria
- [docs/menu-guide.md](docs/menu-guide.md) — How to write menu entries for best pairings
