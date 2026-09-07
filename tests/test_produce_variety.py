"""Plan 027 WI-6 (FWI-007 item 1) — the derived produce-variety count.

The WI-12 acceptance says the derived variety-count must agree with its
inputs. This file holds that: every ``us-*-produce-variety-count`` derived
fact is recomputed here straight from the committed availability series and
must match, value for value. It also holds the two honesty boundaries: the
candidate set is exactly the committed availability series (a new commodity
cannot silently widen or narrow the count), and no decade before the
per-commodity record begins (the sheets start at the earliest 1960) carries
the fact at all.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

from vitrine.derive import evaluate
from vitrine.loader import load_corpus
from vitrine.series import load_series

DATA = Path(__file__).parent.parent / "data"

# the counts as generated from the archived workbooks
# (scripts/ers_fads_variety.py) — count of tracked, by decade's first year
EXPECTED = {
    "1960s": "11 of 18",
    "1970s": "25 of 43",
    "1980s": "31 of 45",
    "1990s": "34 of 49",
    "2000s": "38 of 54",
    "2010s": "42 of 54",
    "2020s": "41 of 52",
}


def _committed_values() -> dict[str, dict[int, float]]:
    out: dict[str, dict[int, float]] = {}
    for path in sorted((DATA / "series").glob("us-availability-*.toml")):
        with path.open("rb") as fh:
            entry = tomllib.load(fh)["series"][0]
        out[entry["id"]] = {int(y): float(v) for y, v in entry["values"].items()}
    return out


def _variety_derived(corpus):
    for room in corpus.rooms:
        if room.country != "us":
            continue
        for derived in room.derived:
            if derived.id.endswith("-produce-variety-count"):
                yield room, derived


def test_variety_count_agrees_with_committed_series() -> None:
    """The WI-12 acceptance: recompute from data/series/, compare values."""
    corpus = load_corpus(DATA)
    series = load_series(DATA)
    committed = _committed_values()

    seen: set[str] = set()
    for room, derived in _variety_derived(corpus):
        tracked = [sid for sid in derived.count_series if derived.at_year in committed[sid]]
        n = sum(
            1
            for sid in tracked
            if committed[sid][derived.at_year] >= derived.threshold
        )
        computed = evaluate(room, derived, series=series)
        assert computed.value == f"{n} of {len(tracked)}"
        assert computed.value == EXPECTED[room.decade]
        assert computed.tier.value == "A"
        seen.add(room.decade)

    assert seen == set(EXPECTED), "a decade's variety fact went missing"


def test_candidate_set_is_exactly_the_committed_availability_series() -> None:
    """Explicit enumeration, never a convention: the count's candidate set
    must be exactly the committed us-availability-* series. A new commodity
    series redds this test until the derived entries are regenerated — the
    widening is a visible diff, not a silent recount."""
    corpus = load_corpus(DATA)
    listed: set[str] = set()
    for _room, derived in _variety_derived(corpus):
        listed.update(derived.count_series)
    committed = set(_committed_values())
    assert listed == committed


def test_no_variety_fact_before_the_record_begins() -> None:
    """The per-commodity sheets start at the earliest 1960; decades before
    that render no count — the boundary is a documented gap, not zeros."""
    corpus = load_corpus(DATA)
    early = {"1900s", "1910s", "1920s", "1930s", "1940s", "1950s"}
    for room in corpus.rooms:
        if room.country == "us" and room.decade in early:
            assert not any(
                d.id.endswith("-produce-variety-count") for d in room.derived
            ), f"{room.decade}: the record does not reach this decade"


def test_every_variety_fact_names_the_rule_assumption() -> None:
    corpus = load_corpus(DATA)
    for _room, derived in _variety_derived(corpus):
        assert "produce-variety-rule" in derived.assumptions
        assert "composite-family" in derived.assumptions


def test_count_year_is_the_decades_first_year() -> None:
    """Same convention as the availability cards; no cherry-picked year."""
    corpus = load_corpus(DATA)
    for room, derived in _variety_derived(corpus):
        assert derived.at_year == int(room.decade[:4])


def test_input_unit_is_farm_weight_pounds() -> None:
    """The drawer states the rule in the inputs' shared unit; it must be the
    availability unit, not the count's own display unit."""
    corpus = load_corpus(DATA)
    series = load_series(DATA)
    for room, derived in _variety_derived(corpus):
        computed = evaluate(room, derived, series=series)
        assert computed.input_unit == "pounds per person per year (farm weight)"
