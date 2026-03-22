#!/usr/bin/env python3
"""Parse the allWeeks JavaScript array from wine-plan-complete.html into JSON.

Output: plan.json to stdout — array of bottle objects as defined in the HTML.
"""

import json
import re
import sys
from pathlib import Path

def extract_allweeks_js(html_path):
    """Extract the raw JS array literal from the HTML file."""
    text = Path(html_path).read_text(encoding="utf-8")

    # Find `const allWeeks = [` and grab everything until the matching `];`
    m = re.search(r"const\s+allWeeks\s*=\s*\[", text)
    if not m:
        raise ValueError("Could not find allWeeks array in HTML")

    start = m.start() + len("const allWeeks = ")
    # Walk forward to find balanced bracket close
    depth = 0
    i = start
    while i < len(text):
        ch = text[i]
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                break
        i += 1

    raw = text[start : i + 1]
    return raw

def js_array_to_json(raw_js):
    """Convert JS object literal syntax to valid JSON."""
    s = raw_js

    # Remove single-line JS comments
    s = re.sub(r"//[^\n]*", "", s)

    # Remove multi-line JS comments
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.DOTALL)

    # Quote unquoted keys: word characters before a colon
    s = re.sub(r"(?<=[{,\n])\s*(\w+)\s*:", r' "\1":', s)

    # Replace single quotes with double quotes (for string values)
    # Handle JS strings in single quotes, being careful not to break apostrophes in double-quoted strings
    s = re.sub(r":\s*'([^']*)'", lambda m: ': "' + m.group(1).replace('"', '\\"') + '"', s)

    # Convert JS booleans/null
    s = s.replace(": true", ": true").replace(": false", ": false").replace(": null", ": null")

    # Remove trailing commas before } or ]
    s = re.sub(r",\s*([}\]])", r"\1", s)

    # Resolve JS Unicode escapes (e.g. \u00b7 → ·) to literal characters
    s = re.sub(r"\\u([0-9a-fA-F]{4})", lambda m: chr(int(m.group(1), 16)), s)

    return json.loads(s)

def parse_plan(html_path):
    raw = extract_allweeks_js(html_path)
    bottles = js_array_to_json(raw)
    return bottles

if __name__ == "__main__":
    html = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).parent / "site" / "index.html")
    bottles = parse_plan(html)
    json.dump(bottles, sys.stdout, indent=2, ensure_ascii=False)
    print()
