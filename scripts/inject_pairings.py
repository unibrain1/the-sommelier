#!/usr/bin/env python3
"""Inject pairing suggestions into site/index.html.

Replaces the PAIRING_PLACEHOLDER line with the actual pairing data
so the HTML works standalone without a web server.

Idempotent: works on both fresh and previously-injected files.
"""

import json
import re
import sys
from pathlib import Path

# Matches: const pairingSuggestions = <anything>; // PAIRING_PLACEHOLDER
PATTERN = re.compile(r"const pairingSuggestions = .*?; // PAIRING_PLACEHOLDER")


def main():
    if len(sys.argv) < 3:
        print("Usage: inject_pairings.py <pairing_suggestions.json> <site/index.html>", file=sys.stderr)
        sys.exit(1)

    pairing_path = Path(sys.argv[1])
    html_path = Path(sys.argv[2])

    data = json.loads(pairing_path.read_text())
    suggestions = data.get("suggestions", [])

    html = html_path.read_text(encoding="utf-8")

    replacement = f"const pairingSuggestions = {json.dumps(suggestions)}; // PAIRING_PLACEHOLDER"

    new_html, count = PATTERN.subn(lambda _: replacement, html)
    if count == 0:
        print("ERROR: PAIRING_PLACEHOLDER not found in HTML", file=sys.stderr)
        sys.exit(1)

    html_path.write_text(new_html, encoding="utf-8")
    print(f"Injected {len(suggestions)} pairing suggestions into {html_path}")


if __name__ == "__main__":
    main()
