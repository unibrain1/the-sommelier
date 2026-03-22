---
name: fetch
description: Fetch CellarTracker inventory, compare against the wine drinking plan, and present the diff report
---

## Instructions

1. Run the pipeline:

```bash
bash fetch.sh
```

2. Read `report.json` and present all four sections to the user:
   - **Consumed** — bottles in the plan but no longer in inventory
   - **Urgent new** — in inventory, not in plan, EndConsume ≤ current year + 1
   - **Quantity mismatches** — plan count differs from inventory count
   - **Unplanned** — in inventory but not scheduled anywhere

3. Ask the user to confirm before proceeding to plan regeneration.

4. If confirmed, read `fetch.md` for the full plan criteria (seasonal preferences, prioritization order, evolution tracking, hold list, past-peak handling) and regenerate `site/index.html` accordingly. Update the `changelog` object with changes made.
