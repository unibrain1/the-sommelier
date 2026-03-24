#!/usr/bin/env python3
"""Parse CellarTracker inventory TSV into structured JSON.

Input:  inventory.tsv (tab-delimited, one row per physical bottle)
Output: inventory.json to stdout — array of unique wines with quantities.
"""

import csv
import json
import sys
from pathlib import Path

KEEP_FIELDS = [
    "iWine",
    "Vintage",
    "Wine",
    "Varietal",
    "MasterVarietal",
    "Type",
    "Color",
    "Category",
    "Country",
    "Region",
    "SubRegion",
    "Appellation",
    "Producer",
    "Designation",
    "Vineyard",
    "Location",
    "Bin",
    "Size",
    "BeginConsume",
    "EndConsume",
    "CT",
    "MY",
]


def int_or_none(val: str | None) -> int | None:
    try:
        return int(val)  # type: ignore[arg-type]
    except (ValueError, TypeError):
        return None


def float_or_none(val: str | None) -> float | None:
    try:
        return float(val)  # type: ignore[arg-type]
    except (ValueError, TypeError):
        return None


def parse_inventory(tsv_path: str | Path) -> list[dict]:
    with open(tsv_path, encoding="latin-1") as f:
        reader = csv.DictReader(f, delimiter="\t")
        rows = list(reader)

    # Group by (iWine, Vintage) to count bottles
    def key_fn(r):
        return (r.get("iWine", ""), r.get("Vintage", ""))

    groups = {}
    for row in rows:
        k = key_fn(row)
        groups.setdefault(k, []).append(row)

    wines = []
    for (iwine, vintage), bottles in groups.items():
        rep = bottles[0]  # representative row
        wine = {field: rep.get(field, "").strip() for field in KEEP_FIELDS}
        wine["Quantity"] = len(bottles)
        wine["Vintage"] = int_or_none(wine["Vintage"])
        wine["BeginConsume"] = int_or_none(wine["BeginConsume"])
        wine["EndConsume"] = int_or_none(wine["EndConsume"])
        wine["CT"] = float_or_none(wine["CT"])
        wine["MY"] = float_or_none(wine["MY"])
        wines.append(wine)

    # Sort by EndConsume ascending (nulls last)
    wines.sort(key=lambda w: (w["EndConsume"] is None, w["EndConsume"] or 9999))
    return wines


if __name__ == "__main__":
    tsv = (
        sys.argv[1]
        if len(sys.argv) > 1
        else str(Path(__file__).parent / "inventory.tsv")
    )
    wines = parse_inventory(tsv)
    json.dump(wines, sys.stdout, indent=2, ensure_ascii=False)
    print()  # trailing newline
