"""Pairwise corridor projection — ``project_pair`` builds a ``PairPage``.

Gathers every fact family the measure guard certifies comparable between two
decades, plus the affordability comparisons and budget-composition bars. Every
value cell links to its placard; non-comparable axes render their documented
gap reason.
"""

from __future__ import annotations

from markupsafe import Markup

from vitrine.compare import compare_item
from vitrine.model import Corpus
from vitrine.site import curation, svg
from vitrine.site.context import (
    CompositionRow,
    PairAffordSection,
    PairCell,
    PairFamily,
    PairPage,
)
from vitrine.site.projections.affordability import afford_fact_ids
from vitrine.site.projections.arcs import fold_shares
from vitrine.site.projections.facts import FactRef, overlay_facts, placard_href


def pair_families(
    index: dict[str, FactRef], a: str, b: str, root: str
) -> tuple[PairFamily, ...]:
    families: list[PairFamily] = []
    for arc in curation.ARCS:
        if a not in arc.fact_ids or b not in arc.fact_ids:
            continue
        cells: list[PairCell] = []
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
            PairFamily(
                label=arc.label, unit=arc.unit, caveats=arc.caveats, cells=tuple(cells)
            )
        )
    return tuple(families)


def pair_afford(
    corpus: Corpus, index: dict[str, FactRef], a: str, b: str, root: str
) -> tuple[PairAffordSection, ...]:
    sections: list[PairAffordSection] = []
    for _slug, label, pattern in curation.AFFORD_ITEMS:
        ids = afford_fact_ids(corpus, pattern)
        if a not in ids or b not in ids:
            continue
        comparison = compare_item(corpus, label, {a: ids[a], b: ids[b]})
        computable = [p for p in comparison.points if p.afford.hours_to_afford is not None]
        hours_measures = {p.afford.hours_measure for p in computable}
        # the measure guard: a mixed-concept axis renders as the gap it is
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
        rows: list[PairCell] = []
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
    return tuple(sections)


def project_pair(
    corpus: Corpus,
    index: dict[str, FactRef],
    a: str,
    b: str,
    affordability: dict[str, dict[str, str]],
) -> PairPage:
    """Project one pairwise decade comparison into a ``PairPage``."""
    root = "../"
    comp_rows: list[CompositionRow] = []
    overlay_ids: list[str] = []
    if a in curation.COMPOSITIONS and b in curation.COMPOSITIONS:
        for decade in (a, b):
            overlay_ids.append(curation.COMPOSITIONS[decade])
            fact = index[curation.COMPOSITIONS[decade]].fact
            segments = fold_shares(fact, index, root)
            if segments:
                comp_rows.append(
                    CompositionRow(
                        bar=Markup(svg.composition_bar(decade, segments)),
                        decade=decade,
                        fact_id=curation.COMPOSITIONS[decade],
                        segments=segments,
                    )
                )
    families = pair_families(index, a, b, root)
    for fam in families:
        overlay_ids.extend(cell.fact_id for cell in fam.cells)
    afford_sections = pair_afford(corpus, index, a, b, root)
    for section in afford_sections:
        overlay_ids.extend(row.fact_id for row in section.rows)
    return PairPage(
        a=a,
        b=b,
        families=families,
        afford_sections=afford_sections,
        comp_rows=tuple(comp_rows),
        sources=corpus.sources,
        assumptions=corpus.assumptions,
        affordability=affordability,
        overlay_facts=overlay_facts(index, tuple(overlay_ids)),
    )
