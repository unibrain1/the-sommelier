#!/usr/bin/env python3
"""Find today's menu and wine pairing from pairing_suggestions.json.

Input:  pairing_suggestions.json path (positional argument)
Output: today's entry as JSON to stdout, or null if no meal today.
"""

import argparse
import json
import sys
from datetime import date
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Output today's menu and pairing suggestion."
    )
    parser.add_argument("pairing_json", help="Path to pairing_suggestions.json")
    args = parser.parse_args()

    data = json.loads(Path(args.pairing_json).read_text())
    suggestions = data.get("suggestions", [])
    today_str = date.today().isoformat()

    for entry in suggestions:
        if entry.get("date") == today_str:
            json.dump(entry, sys.stdout, indent=2, ensure_ascii=False)
            print()
            return

    # No meal planned today
    json.dump({"date": today_str, "meal": None}, sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()
