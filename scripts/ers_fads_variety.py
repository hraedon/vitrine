#!/usr/bin/env python3
"""Author the Plan 027 WI-6 derived produce-variety facts (one-shot).

Writes one ``[[derived]]`` entry (op = count_above) into each US room from
the 1960s on: how many fresh fruit and vegetable commodities the food
supply provided at least a pound per person that year, of the commodities
ERS tracked that year. The count itself is never written — the structure
(series ids, threshold, year) is authored here and the value is computed by
the build, like every derived fact (plan 006).

Discipline, same as the other generators:

- The candidate series list is every commodity in
  ``scripts/ers_fads_extract.py`` — enumerated explicitly, no prefix
  convention — and the workbooks are parsed through the same extractor, so
  the committed ``data/series/`` files and this list cannot drift apart
  silently: the script recomputes the count from BOTH the workbook parse
  and the committed series files and refuses to write if they disagree.
- The count year is the decade's first year (1960, 1970, …), the same
  convention the availability cards use; no decade before the record begins
  (the per-commodity sheets start at the earliest 1960) gets a fact — that
  boundary is recorded in the gap log, not papered over.

Re-running is safe: a room that already carries the derived fact is left
alone.
"""

from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import ers_fads_extract as ex

REPO = Path(__file__).resolve().parent.parent
THRESHOLD = 1.0  # a full pound per person per year, farm weight
FIRST_DECADE = 1960  # the per-commodity record begins; earlier decades render nothing

NOTES = (
    "Every fresh fruit and vegetable commodity sheet in the two ERS fresh "
    "workbooks, counted when the food supply provided at least a full pound per "
    "person that year, farm weight. The total is the commodities ERS tracked "
    "that year: series that had not yet begun or had already ended are outside "
    "the count, so a widening record cannot masquerade as rising variety. "
    "Availability is a disappearance estimate — what the supply made available, "
    "not what anyone ate; the rule and its rationale are in the assumption "
    "ledger (produce-variety-rule)."
)
UNIT = "of the fresh-produce commodities ERS tracked that year"


def committed_values() -> dict[str, dict[int, float]]:
    """year -> value per committed series file — the derive engine's inputs."""
    out: dict[str, dict[int, float]] = {}
    for path in sorted((REPO / "data" / "series").glob("us-availability-*.toml")):
        with path.open("rb") as fh:
            data = tomllib.load(fh)
        for entry in data["series"]:
            out[entry["id"]] = {int(y): float(v) for y, v in entry["values"].items()}
    return out


def main() -> None:
    series_ids = sorted(f"us-availability-{slug}" for slug in ex.COMMODITIES)
    parsed = {f"us-availability-{slug}": ex.parse(wb, sheet)[0]
              for slug, (wb, sheet, _l) in ex.COMMODITIES.items()}
    committed = committed_values()

    missing = [sid for sid in series_ids if sid not in committed]
    if missing:
        raise SystemExit(
            f"committed series missing {missing[0]!r} — run "
            f"scripts/ers_fads_extract.py first"
        )

    written = 0
    for decade_start in range(FIRST_DECADE, 2030, 10):
        decade = f"{decade_start}s"
        year = decade_start
        # the count recomputed from both sources; disagreement means a
        # committed series file no longer matches the archived workbook
        from_wb = sum(
            1 for sid in series_ids
            if year in parsed[sid] and parsed[sid][year] >= THRESHOLD
        )
        tracked_wb = sum(1 for sid in series_ids if year in parsed[sid])
        from_committed = sum(
            1 for sid in series_ids
            if year in committed[sid] and committed[sid][year] >= THRESHOLD
        )
        tracked_committed = sum(1 for sid in series_ids if year in committed[sid])
        if (from_wb, tracked_wb) != (from_committed, tracked_committed):
            raise SystemExit(
                f"{decade}: workbook parse ({from_wb} of {tracked_wb}) disagrees "
                f"with committed series ({from_committed} of {tracked_committed}) "
                f"— regenerate data/series/ before authoring"
            )

        fid = f"us-{decade}-produce-variety-count"
        path = REPO / "data" / "us" / f"{decade}.toml"
        text = path.read_text()
        if f'id = "{fid}"' in text:
            continue

        listing = ",\n".join(f'  "{sid}"' for sid in series_ids)
        block = f'''[[derived]]
id = "{fid}"
panel = "table"
label = "Fresh-produce commodities at a pound or more per person, {year}"
op = "count_above"
unit = "{UNIT}"
count_series = [
{listing},
]
threshold = {THRESHOLD}
at_year = {year}
notes = "{NOTES}"
assumptions = ["produce-variety-rule", "composite-family"]
'''
        # place the derived fact with its sibling availability cards: after
        # the last availability card block in the room
        anchors = [m.start() for m in re.finditer(r'id = "us-' + decade + r'-availability-', text)]
        if not anchors:
            raise SystemExit(f"{decade}: no availability card to anchor against")
        m = re.compile(r"\n\n(?=\[\[|\[room\]|# )").search(text, anchors[-1])
        if m is None:
            raise SystemExit(f"{decade}: no insertion point")
        cut = m.start() + 1
        path.write_text(text[:cut] + "\n" + block + text[cut:])
        written += 1
        print(f"  {decade}  {from_wb} of {tracked_wb} tracked  ({year})")
    print(f"\n{written} derived fact(s) written")
    print("counts recomputed from the workbooks AND the committed series; "
          "values are computed at build, never authored")


if __name__ == "__main__":
    main()
