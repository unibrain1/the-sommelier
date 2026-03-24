---
name: pairing-audit
description: Audit wine_keywords.py against menu data for coverage gaps and rule consistency
disable-model-invocation: true
---

# Pairing Audit

Audit the wine-food pairing engine for keyword coverage gaps, rule consistency, and match quality.

## Workflow

1. **Load pairing rules and keywords**:

   Read `scripts/wine_keywords.py` and extract:
   - All food keywords and their categories
   - All pairing rules (varietal → food category mappings)
   - Scoring weights and thresholds

2. **Load current menu data** (if available):

   ```bash
   python3 -c "
   import json
   try:
       with open('data/menu.json') as f:
           menu = json.load(f)
       for meal in menu[:20]:
           print(f'{meal.get(\"date\", \"?\")} | {meal.get(\"summary\", \"?\")}')
       print(f'... {len(menu)} meals total')
   except FileNotFoundError:
       print('No menu.json — run fetch.sh first or audit keywords only')
   "
   ```

3. **Analyze keyword coverage**:

   ```bash
   python3 -c "
   import json, sys
   sys.path.insert(0, 'scripts')
   from wine_keywords import FOOD_KEYWORDS, extract_keywords

   try:
       with open('data/menu.json') as f:
           menu = json.load(f)
   except FileNotFoundError:
       print('No menu.json available — skipping coverage analysis')
       sys.exit(0)

   unmatched = []
   matched = []
   for meal in menu:
       summary = meal.get('summary', '')
       keywords = extract_keywords(summary)
       if keywords:
           matched.append((summary, keywords))
       else:
           unmatched.append(summary)

   print(f'Matched: {len(matched)}/{len(menu)} meals ({100*len(matched)//max(len(menu),1)}%)')
   print(f'Unmatched: {len(unmatched)} meals')
   if unmatched:
       print()
       print('UNMATCHED MENU ENTRIES:')
       for s in unmatched:
           print(f'  - {s}')
   "
   ```

4. **Analyze rule consistency**:

   Read `scripts/wine_keywords.py` and `scripts/pairing.py` and check:
   - Are there food categories referenced in pairing rules that have no keywords defined?
   - Are there keywords defined that no pairing rule references?
   - Are there varietals in the inventory that have no pairing rules?
   - Do any rules contradict each other (same food category paired as both "good" and "poor" for the same wine type)?

5. **Load current pairing suggestions** (if available) and spot-check quality:

   ```bash
   python3 -c "
   import json
   try:
       with open('site/pairing_suggestions.json') as f:
           suggestions = json.load(f)
       good = sum(1 for s in suggestions if s.get('score') == 'good')
       partial = sum(1 for s in suggestions if s.get('score') == 'partial')
       poor = sum(1 for s in suggestions if s.get('score') == 'poor')
       neutral = sum(1 for s in suggestions if s.get('score') == 'neutral')
       print(f'Suggestions: {len(suggestions)} total')
       print(f'  good: {good}, partial: {partial}, poor: {poor}, neutral: {neutral}')
   except FileNotFoundError:
       print('No pairing_suggestions.json — run fetch.sh first')
   "
   ```

6. **Report findings**:

   - **Coverage**: % of menu entries that match at least one keyword
   - **Gaps**: Menu entries with no keyword matches (candidates for new keywords)
   - **Orphaned keywords**: Keywords defined but never matched by any menu entry
   - **Orphaned rules**: Pairing rules for varietals not in inventory
   - **Consistency issues**: Any contradictions or missing mappings
   - **Recommendations**: Specific keywords or rules to add, ranked by impact (frequency of unmatched menu entries)
