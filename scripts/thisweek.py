#!/usr/bin/env python3
"""Find the current week's entry from plan.json.

Input:  plan.json path (positional argument)
Output: the matching allWeeks entry as JSON to stdout.
        Falls back to the first entry if no match is found.
"""

import argparse
import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path


def find_current_week(all_weeks: list[dict]) -> dict:
    """Return the week entry that contains today, or the first entry as fallback."""
    today = date.today()

    for week in all_weeks:
        raw = week.get("date", "")
        try:
            week_monday = datetime.strptime(raw, "%b %d, %Y").date()
        except ValueError:
            continue
        # The week spans Monday through Sunday (7 days)
        if week_monday <= today < week_monday + timedelta(days=7):
            return week

    # Fallback: return the first entry
    return all_weeks[0]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Output the current week's entry from plan.json."
    )
    parser.add_argument("plan_json", help="Path to plan.json")
    args = parser.parse_args()

    plan_data = json.loads(Path(args.plan_json).read_text())
    all_weeks: list[dict] = (
        plan_data.get("allWeeks", plan_data)
        if isinstance(plan_data, dict)
        else plan_data
    )

    if not all_weeks:
        print("Error: allWeeks is empty", file=sys.stderr)
        sys.exit(1)

    entry = find_current_week(all_weeks)
    json.dump(entry, sys.stdout, indent=2, ensure_ascii=False)
    print()  # trailing newline


if __name__ == "__main__":
    main()
