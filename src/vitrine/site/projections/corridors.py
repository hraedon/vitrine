"""Corridor atlas projection — ``project_corridor`` builds a ``CorridorPage``.

Assembles the four-wing atlas: arc/group charts, the economy wing's
affordability exhibits and budget-composition bars, the pairwise epoch grid,
and the overlay placard deck. Validates that every rendered arc is placed in
exactly one wing (registry-consistency gate).
"""

from __future__ import annotations

from markupsafe import Markup

from vitrine.compare import compare_item
from vitrine.model import Corpus, Room
from vitrine.series import Series
from vitrine.site import curation, svg
from vitrine.site.context import (
    ArcSection,
    CompositionRow,
    CorridorPage,
    CorridorWingView,
)
from vitrine.site.projections.affordability import afford_arc_chart, afford_fact_ids
from vitrine.site.projections.arcs import (
    arc_chart_for,
    arc_coverage,
    arc_group_chart_for,
    arc_group_coverage,
    fold_shares,
)
from vitrine.site.projections.facts import FactRef, overlay_facts

_AFFORD = curation.AFFORD_ITEMS
_COMP_CAVEATS = (
    "Survey populations differ across the century — 1901 wage-earner families "
    "vs modern consumer units; each bar links to its placard, which names who "
    "was measured.",
)
_EPOCHS = (("1900s", "1950s"), ("1950s", "2020s"), ("1900s", "2020s"))


def _build_arc_sections(
    index: dict[str, FactRef],
    series: dict[str, Series],
    room_count: int,
    root: str,
) -> tuple[ArcSection, ...]:
    """One ArcSection per rendered arc (group members collapse to their group)."""
    sections: list[ArcSection] = []
    rendered_groups: set[str] = set()
    for arc in curation.ARCS:
        group = curation.ARC_GROUP_BY_MEMBER.get(arc.slug)
        if group is not None:
            if group.slug in rendered_groups:
                continue
            rendered_groups.add(group.slug)
            sections.append(
                ArcSection(
                    slug=group.slug,
                    label=group.label,
                    unit=group.unit,
                    caveats=group.caveats,
                    coverage=arc_group_coverage(group, index, room_count),
                    chart=Markup(arc_group_chart_for(group, index, root)),
                )
            )
            continue
        sections.append(
            ArcSection(
                slug=arc.slug,
                label=arc.label,
                unit=arc.unit,
                caveats=arc.caveats,
                coverage=arc_coverage(arc, index, series, room_count),
                chart=Markup(arc_chart_for(arc, index, series, root)),
            )
        )
    return tuple(sections)


def _build_afford_sections(
    corpus: Corpus,
    index: dict[str, FactRef],
    room_count: int,
    root: str,
) -> tuple[ArcSection, ...]:
    """The economy wing's hours-axis affordability exhibits."""
    sections: list[ArcSection] = []
    for _slug, label, pattern in _AFFORD:
        ids = afford_fact_ids(corpus, pattern)
        if len(ids) < 2:
            continue
        comparison = compare_item(corpus, label, ids)
        caveats = curation.AFFORD_ITEM_CAVEATS.get(_slug, ()) + comparison.caveats
        sections.append(
            ArcSection(
                slug=_slug,
                label=label,
                caveats=caveats,
                coverage=f"{len(comparison.points)} of {room_count} rooms charted",
                unit="hours of work to afford",
                chart=Markup(afford_arc_chart(comparison, ids, index, root)),
            )
        )
    return tuple(sections)


def _build_comp_rows(
    index: dict[str, FactRef], root: str
) -> tuple[CompositionRow, ...]:
    rows: list[CompositionRow] = []
    for decade in sorted(curation.COMPOSITIONS):
        fact_id = curation.COMPOSITIONS[decade]
        fact = index[fact_id].fact
        segments = fold_shares(fact, index, root)
        if segments:
            rows.append(
                CompositionRow(
                    bar=Markup(svg.composition_bar(decade, segments)),
                    decade=decade,
                    fact_id=fact_id,
                    segments=segments,
                )
            )
    return tuple(rows)


def _build_wings(
    arc_sections: tuple[ArcSection, ...], afford_count: int
) -> tuple[CorridorWingView, ...]:
    """Gather arc sections into the four editorial wings; validate placement."""
    by_slug = {section.slug: section for section in arc_sections}
    wing_arc_slug_list = [
        slug for wing in curation.CORRIDOR_WINGS for slug in wing.arc_slugs
    ]
    wing_arc_slugs = set(wing_arc_slug_list)
    rendered_arc_slugs = set(by_slug)
    if (
        len(wing_arc_slug_list) != len(wing_arc_slugs)
        or wing_arc_slugs != rendered_arc_slugs
    ):
        missing = sorted(rendered_arc_slugs - wing_arc_slugs)
        unknown = sorted(wing_arc_slugs - rendered_arc_slugs)
        raise ValueError(
            "corridor wing registry must place every rendered arc exactly once; "
            f"missing={missing}, unknown={unknown}"
        )
    wings: list[CorridorWingView] = []
    for wing in curation.CORRIDOR_WINGS:
        wing_arcs = tuple(by_slug[slug] for slug in wing.arc_slugs)
        economy_exhibits = afford_count + 1 if wing.slug == "economy" else 0
        wings.append(
            CorridorWingView(
                slug=wing.slug,
                number=wing.number,
                title=wing.title,
                question=wing.question,
                introduction=wing.introduction,
                arcs=wing_arcs,
                exhibit_count=len(wing_arcs) + economy_exhibits,
            )
        )
    return tuple(wings)


def project_corridor(
    corpus: Corpus,
    index: dict[str, FactRef],
    series: dict[str, Series],
    rooms: list[Room] | tuple[Room, ...],
    affordability: dict[str, dict[str, str]],
) -> CorridorPage:
    """Project the corridor atlas index into a ``CorridorPage``."""
    root = "../"
    room_count = len(rooms)
    decades = tuple(room.decade for room in rooms)

    arc_sections = _build_arc_sections(index, series, room_count, root)
    afford_sections = _build_afford_sections(corpus, index, room_count, root)
    comp_rows = _build_comp_rows(index, root)
    wings = _build_wings(arc_sections, len(afford_sections))

    overlay_ids: list[str] = []
    for arc in curation.ARCS:
        overlay_ids.extend(arc.fact_ids.values())
    for _slug, _label, pattern in _AFFORD:
        overlay_ids.extend(afford_fact_ids(corpus, pattern).values())
    overlay_ids.extend(curation.COMPOSITIONS.values())

    return CorridorPage(
        decades=decades,
        epochs=_EPOCHS,
        pair_count=len(decades) * (len(decades) - 1) // 2,
        wings=wings,
        afford_sections=afford_sections,
        comp_rows=comp_rows,
        comp_caveats=_COMP_CAVEATS,
        sources=corpus.sources,
        assumptions=corpus.assumptions,
        affordability=affordability,
        overlay_facts=overlay_facts(index, tuple(overlay_ids)),
    )
