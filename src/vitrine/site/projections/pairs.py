"""Pairwise corridor projections — fact families for decade-pair pages."""

from __future__ import annotations

from dataclasses import dataclass

from vitrine.compare import compare_item
from vitrine.model import Corpus
from vitrine.site import curation
from vitrine.site.projections.affordability import afford_fact_ids
from vitrine.site.projections.facts import FactRef, placard_href


@dataclass(frozen=True, slots=True)
class PairCell:
    decade: str
    fact_id: str
    href: str
    overlay_href: str
    tier: str
    text: str
    gap: bool


@dataclass(frozen=True, slots=True)
class PairFamily:
    label: str
    unit: str
    caveats: tuple[str, ...]
    cells: tuple[PairCell, ...]


@dataclass(frozen=True, slots=True)
class PairAffordSection:
    label: str
    caveats: tuple[str, ...]
    rows: tuple[PairCell, ...]
    gap_reason: str = ""


def pair_families(
    index: dict[str, FactRef], a: str, b: str, root: str
) -> list[PairFamily]:
    families = []
    for arc in curation.ARCS:
        if a not in arc.fact_ids or b not in arc.fact_ids:
            continue
        cells = []
        for decade in (a, b):
            fid = arc.fact_ids[decade]
            fact = index[fid].fact
            gap = fact.quantity is None
            cells.append(
                PairCell(
                    decade=decade,
                    fact_id=fid,
                    href=placard_href(index, fid, root),
                    overlay_href=f"#{fid}--modal",
                    tier=fact.tier.value,
                    text=fact.value if not gap else f"{fact.value} — see the placard",
                    gap=gap,
                )
            )
        families.append(
            PairFamily(label=arc.label, unit=arc.unit, caveats=arc.caveats, cells=tuple(cells))
        )
    return families


def pair_afford(
    corpus: Corpus, index: dict[str, FactRef], a: str, b: str, root: str
) -> list[PairAffordSection]:
    sections = []
    for _slug, label, pattern in curation.AFFORD_ITEMS:
        ids = afford_fact_ids(corpus, pattern)
        if a not in ids or b not in ids:
            continue
        comparison = compare_item(corpus, label, {a: ids[a], b: ids[b]})
        computable = [p for p in comparison.points if p.afford.hours_to_afford is not None]
        hours_measures = {p.afford.hours_measure for p in computable}
        if len(computable) < 2:
            reason = (
                "the hours axis needs a structured price and a verified wage "
                "anchor in both rooms — not yet curated for this pair"
            )
            sections.append(
                PairAffordSection(
                    label=label, caveats=comparison.caveats, rows=(), gap_reason=reason
                )
            )
            continue
        if len(hours_measures) != 1 or None in hours_measures:
            reason = next(
                (c for c in comparison.caveats if "mixes" in c),
                "the wage anchors do not share a measure",
            )
            sections.append(
                PairAffordSection(
                    label=label, caveats=comparison.caveats, rows=(), gap_reason=reason
                )
            )
            continue
        rows = []
        for p in computable:
            hours = p.afford.hours_to_afford
            assert hours is not None
            fid = ids[p.decade]
            rows.append(
                PairCell(
                    decade=p.decade,
                    fact_id=fid,
                    href=placard_href(index, fid, root),
                    overlay_href=f"#{fid}--modal",
                    tier=p.afford.tier.value,
                    text=f"{p.price_display} ≈ {hours:,.0f} hours of work",
                    gap=False,
                )
            )
        sections.append(
            PairAffordSection(label=label, caveats=comparison.caveats, rows=tuple(rows))
        )
    return sections
