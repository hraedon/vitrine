"""Cross-decade comparator — the affordability axis projection (Plan 003 WI-4).

For a given concept (e.g. "a new car"), calls ``afford()`` across every decade
that has the priced fact and its room's anchors, producing an ordered
hours-to-afford series. Decades without the fact or without anchors are simply
absent from the points tuple — the renderer shows the gap ("no record"),
consistent with the charter's "render the gap" rule.
"""

from __future__ import annotations

from dataclasses import dataclass

from vitrine.affordability import Affordability, afford
from vitrine.model import Corpus, Fact, Measure, Room, measure_label

# Within one decade room a price and its anchor should be near-contemporaneous;
# a wider gap (e.g. a 1947 price against a 1939 wage in the bifurcated 1940s)
# folds a real-wage change into a point the axis presents as inflation-free.
_MAX_ANCHOR_YEAR_GAP = 3


@dataclass(frozen=True, slots=True)
class ComparisonPoint:
    decade: str
    afford: Affordability
    price_display: str


@dataclass(frozen=True, slots=True)
class Comparison:
    label: str
    points: tuple[ComparisonPoint, ...]
    caveats: tuple[str, ...] = ()  # why the series may not be directly comparable


def _find_room_and_fact(corpus: Corpus, fact_id: str) -> tuple[Room, Fact] | None:
    for room in corpus.rooms:
        for fact in room.facts:
            if fact.id == fact_id:
                return room, fact
    return None


def _find_fact_in_room(room: Room, fact_id: str) -> Fact | None:
    for fact in room.facts:
        if fact.id == fact_id:
            return fact
    return None


def compare_item(corpus: Corpus, label: str, fact_ids: dict[str, str]) -> Comparison:
    """Build a cross-decade comparison for a set of priced facts.

    *fact_ids* maps decade -> fact_id of the priced fact for that decade.
    Looks up each fact, finds its room's wage/income anchors, calls ``afford()``.
    Decades where the fact or anchors are missing are skipped (render the gap).
    """
    points: list[ComparisonPoint] = []
    for decade, fid in fact_ids.items():
        found = _find_room_and_fact(corpus, fid)
        if found is None:
            continue
        room, price_fact = found
        if price_fact.amount_minor is None:
            continue

        wage_fact: Fact | None = None
        income_fact: Fact | None = None
        wage_population = ""
        income_population = ""
        wage_measure: Measure | None = None
        income_measure: Measure | None = None

        if room.wage_anchor:
            wage_fact = _find_fact_in_room(room, room.wage_anchor)
            if wage_fact is not None:
                src = corpus.sources.get(wage_fact.source)
                if src is not None:
                    wage_population = src.population
                    wage_measure = src.measure

        if room.income_anchor:
            income_fact = _find_fact_in_room(room, room.income_anchor)
            if income_fact is not None:
                src = corpus.sources.get(income_fact.source)
                if src is not None:
                    income_population = src.population
                    income_measure = src.measure

        if wage_fact is None and income_fact is None:
            continue

        afford_result = afford(
            price_fact,
            wage=wage_fact,
            income=income_fact,
            wage_population=wage_population,
            income_population=income_population,
            wage_measure=wage_measure,
            income_measure=income_measure,
        )

        points.append(
            ComparisonPoint(
                decade=decade,
                afford=afford_result,
                price_display=price_fact.value,
            )
        )

    ordered = sorted(points, key=lambda p: p.decade)
    return Comparison(
        label=label,
        points=tuple(ordered),
        caveats=_caveats(ordered),
    )


def _caveats(points: list[ComparisonPoint]) -> tuple[str, ...]:
    """Surface why a series may not be directly comparable — never hide it.

    Two anchors of the same basis are still incomparable if they measure
    different things (money income vs wages-only vs a survey reconstruction),
    and a within-"decade" division across a wide year gap folds a real-wage
    change into an axis presented as inflation-free. We flag; we do not drop.
    """
    caveats: list[str] = []

    hours_measures = {
        p.afford.hours_measure
        for p in points
        if p.afford.hours_to_afford is not None and p.afford.hours_measure is not None
    }
    if len(hours_measures) > 1:
        named = ", ".join(sorted(measure_label(m) for m in hours_measures))
        caveats.append(
            f"Hours-to-afford mixes wage concepts across decades ({named}); "
            f"a step between points may reflect the concept change, not affordability."
        )

    pct_measures = {
        p.afford.pct_measure
        for p in points
        if p.afford.pct_of_income is not None and p.afford.pct_measure is not None
    }
    if len(pct_measures) > 1:
        named = ", ".join(sorted(measure_label(m) for m in pct_measures))
        caveats.append(
            f"Share-of-income mixes income concepts across decades ({named}); "
            f"a step between points may reflect the concept change, not affordability."
        )

    wide = sorted(
        {
            p.decade
            for p in points
            if p.afford.year_gap is not None and p.afford.year_gap > _MAX_ANCHOR_YEAR_GAP
        }
    )
    if wide:
        caveats.append(
            f"Price and anchor years differ by more than {_MAX_ANCHOR_YEAR_GAP} "
            f"years in: {', '.join(wide)} — the hours axis is not strictly "
            f"inflation-free there."
        )

    return tuple(caveats)
