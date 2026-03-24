#!/usr/bin/env python3
"""Parse a Google Calendar .ics feed into menu.json.

Extracts events from the calendar and outputs a JSON array of menu entries
sorted by date. Each entry has: date, meal, description, keywords.

Keywords are extracted from the meal title and description for wine pairing.
"""

import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from icalendar import Calendar

from wine_keywords import ALL_KEYWORDS

# How far ahead to look (days)
HORIZON_DAYS = 730  # ~2 years, matching the plan horizon

# Local timezone for converting UTC calendar events
LOCAL_TZ = ZoneInfo("America/Los_Angeles")


def extract_keywords(text: str) -> list[str]:
    """Pull pairing-relevant keywords from text."""
    lower = text.lower()
    found = []
    for kw in ALL_KEYWORDS:
        if kw in lower:
            found.append(kw)
    return sorted(set(found))


def parse_ics(ics_text: str) -> list[dict]:
    """Parse .ics text into a list of menu entries."""
    cal = Calendar.from_ical(ics_text)
    today = date.today()
    # Include meals from the start of the current week (Monday)
    week_start = today - timedelta(days=today.weekday())
    cutoff = date.fromordinal(today.toordinal() + HORIZON_DAYS)

    entries = []
    for component in cal.walk():
        if component.name != "VEVENT":
            continue

        dt_start = component.get("dtstart")
        if dt_start is None:
            continue

        event_date = dt_start.dt
        if isinstance(event_date, datetime):
            # Convert UTC to local timezone before extracting date
            if event_date.tzinfo is not None:
                event_date = event_date.astimezone(LOCAL_TZ)
            event_date = event_date.date()

        # Include events from current week start through horizon
        if event_date < week_start or event_date > cutoff:
            continue

        summary = str(component.get("summary", ""))
        description = str(component.get("description", ""))

        combined_text = f"{summary} {description}"
        keywords = extract_keywords(combined_text)

        entries.append(
            {
                "date": event_date.isoformat(),
                "meal": summary.strip(),
                "description": description.strip() if description else "",
                "keywords": keywords,
            }
        )

    entries.sort(key=lambda e: e["date"])
    return entries


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: parse_menu.py <calendar.ics>", file=sys.stderr)
        sys.exit(1)

    ics_path = Path(sys.argv[1])
    ics_text = ics_path.read_text(encoding="utf-8")
    entries = parse_ics(ics_text)
    print(json.dumps(entries, indent=2))


if __name__ == "__main__":
    main()
