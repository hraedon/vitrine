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
from vitrine.model import Corpus, Fact, Room


@dataclass(frozen=True, slots=True)
class ComparisonPoint:
    decade: str
    afford: Affordability
    price_display: str


@dataclass(frozen=True, slots=True)
class Comparison:
    label: str
    points: tuple[ComparisonPoint, ...]


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

        if room.wage_anchor:
            wage_fact = _find_fact_in_room(room, room.wage_anchor)
            if wage_fact is not None:
                src = corpus.sources.get(wage_fact.source)
                if src is not None:
                    wage_population = src.population

        if room.income_anchor:
            income_fact = _find_fact_in_room(room, room.income_anchor)
            if income_fact is not None:
                src = corpus.sources.get(income_fact.source)
                if src is not None:
                    income_population = src.population

        if wage_fact is None and income_fact is None:
            continue

        afford_result = afford(
            price_fact,
            wage=wage_fact,
            income=income_fact,
            wage_population=wage_population,
            income_population=income_population,
        )

        points.append(
            ComparisonPoint(
                decade=decade,
                afford=afford_result,
                price_display=price_fact.value,
            )
        )

    ordered = sorted(points, key=lambda p: p.decade)
    return Comparison(label=label, points=tuple(ordered))
