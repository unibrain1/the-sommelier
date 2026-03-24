#!/usr/bin/env python3
"""Composite scoring functions for wine scheduling.

Symbols exported:
  window_position_score — drinking-window position score (0–100, higher = schedule sooner)
"""

from wine_utils import CURRENT_YEAR

# ---------------------------------------------------------------------------
# Window position scoring
# ---------------------------------------------------------------------------


def window_position_score(wine: dict) -> float:
    """Score a wine's drinking-window position on a 0–100 scale.

    Higher scores indicate the wine is more desirable to schedule now.
    The wine dict is never mutated; begin/end inference uses local variables.

    Args:
        wine: Wine dict with optional integer keys BeginConsume and EndConsume.

    Returns:
        Float in [0.0, 100.0].
    """
    begin = wine.get("BeginConsume")
    end = wine.get("EndConsume")

    # --- Missing data handling ---
    if begin is None and end is None:
        return 35.0
    if begin is None and end is not None:
        begin = end - 5
    if end is None and begin is not None:
        end = begin + 10

    assert begin is not None and end is not None  # guaranteed by inference above

    # --- Past peak ---
    if end < CURRENT_YEAR:
        years_past = CURRENT_YEAR - end
        return min(100.0, 70.0 + years_past * 5.0)

    # --- Before window ---
    if begin > CURRENT_YEAR:
        years_before = begin - CURRENT_YEAR
        return max(0.0, 15.0 - years_before * 5.0)

    # --- In window ---
    window_length = end - begin
    if window_length <= 0:
        window_length = 1
    position = (CURRENT_YEAR - begin) / window_length
    peak_quality = 1.0 - abs(position - 0.5) * 2
    end_urgency = position
    blended = 0.5 * peak_quality + 0.5 * end_urgency
    return 30.0 + blended * 35.0
