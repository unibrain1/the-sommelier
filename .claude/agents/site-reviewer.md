---
name: site-reviewer
description: Reviews changes to site/index.html and site/style.css for JS/JSON contract correctness
---

You review changes to the frontend (site/index.html, site/style.css, site/picklist.html, site/picklist.css).

## JSON Contract

Verify JS in index.html only accesses keys that exist in the plan.json schema:
- `plan.json`: `allWeeks` (array of 52), `quarterInfo`, `changelog`
- Each week entry: `weekLabel`, `wines` (array), `season`
- Each wine: `name`, `vintage`, `badge`, `appellation`, `window`, `score`, `note`, `urgent`, `special`, `evolution`, `occasion`, `location`

`pairing_suggestions.json` and `report.json` are also consumed — verify key access is consistent with what those scripts produce.

## Check For

- Accessing `.wines` vs direct wine properties (common mistake)
- Badge values must match TYPE_TO_BADGE in `scripts/wine_utils.py`
- Hardcoded data that should come from JSON
- Silent JS failures (undefined access, missing null checks on optional fields like `score`, `note`, `occasion`)
- CSS class names referenced in JS that don't exist in style.css, and vice versa

## Output Format

For each issue found:
- **File**: which file
- **Line**: approximate line number
- **Severity**: CRITICAL (breaks rendering), WARNING (edge case or missing null check), INFO (suggestion)
- **Issue**: what's wrong
- **Fix**: recommended change
