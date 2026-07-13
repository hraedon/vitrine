"""Walkthrough projection — ``project_walkthrough`` builds a ``WalkthroughPage``.

The guided three-stop transect: a stage per stop with paid/unpaid/childhood
figure lenses, the same-measures-across-stops grid, the women's labour-hours
meter, and the true-scale house row. Every record links to its placard.
"""

from __future__ import annotations

from markupsafe import Markup

from vitrine.model import Corpus, Room
from vitrine.site import curation, svg
from vitrine.site.context import (
    WalkthroughHouse,
    WalkthroughMetric,
    WalkthroughMetricCell,
    WalkthroughPage,
    WalkthroughPerson,
    WalkthroughPersonRow,
    WalkthroughStop,
)
from vitrine.site.projections.facts import FactRef, overlay_facts, placard_href
from vitrine.site.projections.stage import build_stage

# demo figure primitives (decoration; the stats beside them carry the facts)
_FIGS = {
    "father": '<path class="fig" d="M-12 -26 L12 -26 L8 44 L-8 44 Z"/><circle class="fig head" cx="0" cy="-37" r="9"/>',
    "mother": '<path class="fig" d="M-9 -25 L9 -25 L5 12 L15 44 L-15 44 L-5 12 Z"/><circle class="fig head" cx="0" cy="-36" r="8.5"/>',
    "children": '<g transform="translate(-11,4)"><path class="fig" d="M-7 -14 L7 -14 L5 28 L-5 28 Z"/><circle class="fig head" cx="0" cy="-23" r="6.5"/></g><g transform="translate(13,10) scale(0.82)"><path class="fig" d="M-7 -14 L7 -14 L5 28 L-5 28 Z"/><circle class="fig head" cx="0" cy="-23" r="6.5"/></g>',
}


def _build_stop_sections(
    rooms_by_decade: dict[str, Room],
    index: dict[str, FactRef],
    overlay_ids: list[str],
) -> tuple[WalkthroughStop, ...]:
    stops: list[WalkthroughStop] = []
    for decade in curation.WALKTHROUGH_STOPS:
        room = rooms_by_decade[decade]
        stage = build_stage(room, index, "")
        overlay_ids.extend(a.fact_id for a in stage.artifacts)
        overlay_ids.extend(n.fact_id for n in stage.zone_notes)
        people: list[WalkthroughPerson] = []
        # The source series are sex- and activity-specific, not observations
        # of one literal father and mother. Lens labels keep the composite
        # honest and avoid assigning a family structure the data never states.
        for figure, name in (
            ("father", "The paid-work record"),
            ("mother", "The unpaid-work record"),
            ("children", "The childhood record"),
        ):
            rows: list[WalkthroughPersonRow] = []
            for fid in curation.WALKTHROUGH_PEOPLE[figure].get(decade, ()):
                fact = index[fid].fact
                overlay_ids.append(fid)
                rows.append(
                    WalkthroughPersonRow(
                        fact_id=fid,
                        href=f"#{fid}--modal",
                        label=fact.label,
                        value=fact.value if len(fact.value) <= 90 else fact.value[:87] + "…",
                        tier=fact.tier.value,
                    )
                )
            people.append(WalkthroughPerson(name=name, fig=Markup(_FIGS[figure]), rows=tuple(rows)))
        stops.append(
            WalkthroughStop(
                decade=decade,
                stage=Markup(svg.stage_svg(stage, overlay_links=True)),
                people=tuple(people),
            )
        )
    return tuple(stops)


def _build_metrics(index: dict[str, FactRef], overlay_ids: list[str]) -> tuple[WalkthroughMetric, ...]:
    metrics: list[WalkthroughMetric] = []
    for slug in curation.WALKTHROUGH_METRICS:
        arc = curation.ARC_BY_SLUG[slug]
        stop_facts = [(d, arc.fact_ids.get(d)) for d in curation.WALKTHROUGH_STOPS]
        quantities = [
            q
            for _, mfid in stop_facts
            if mfid is not None and (q := index[mfid].fact.quantity) is not None
        ]
        q_max = max(quantities) if quantities else 1.0
        cells: list[WalkthroughMetricCell] = []
        for decade, mfid in stop_facts:
            if mfid is None:
                # no fact at all for this stop — an uncurated slot, not a mark
                cells.append(
                    WalkthroughMetricCell(
                        decade=decade,
                        fact_id="",
                        href="",
                        tier="",
                        gap=True,
                        text="not yet curated",
                        bar=0,
                    )
                )
                continue
            fact = index[mfid].fact
            overlay_ids.append(mfid)
            cells.append(
                WalkthroughMetricCell(
                    decade=decade,
                    fact_id=mfid,
                    href=f"#{mfid}--modal",
                    tier=fact.tier.value,
                    gap=fact.quantity is None,
                    text="see the placard" if fact.quantity is None else f"{fact.quantity:g}",
                    bar=0
                    if fact.quantity is None or q_max == 0
                    else round(100 * fact.quantity / q_max),
                )
            )
        metrics.append(
            WalkthroughMetric(
                label=arc.label, unit=arc.unit, falling=arc.falling, cells=tuple(cells)
            )
        )
    return tuple(metrics)


def _build_meter(index: dict[str, FactRef], overlay_ids: list[str]) -> Markup:
    women_arc = curation.ARC_BY_SLUG["home-production-women"]
    meter_bars = []
    for decade in sorted(women_arc.fact_ids):
        fid = women_arc.fact_ids[decade]
        fact = index[fid].fact
        overlay_ids.append(fid)
        meter_bars.append(
            svg.MeterBar(
                decade=decade,
                fact_id=fid,
                href=placard_href(index, fid, ""),
                tier=fact.tier.value,
                label=fact.label,
                value=fact.value,
                quantity=(None if decade in women_arc.plot_gaps else fact.quantity),
                note=(
                    "different unit and concept — see the placard"
                    if decade in women_arc.plot_gaps
                    else ""
                ),
            )
        )
    return Markup(svg.hours_meter(tuple(meter_bars), women_arc.unit, overlay_links=True))


def _build_houses(index: dict[str, FactRef], overlay_ids: list[str]) -> tuple[WalkthroughHouse, ...]:
    houses: list[WalkthroughHouse] = []
    sourced_area: float | None = None
    for decade in curation.WALKTHROUGH_STOPS:
        area_fid = curation.WALKTHROUGH_FLOOR_AREA.get(decade)
        if area_fid is not None and index[area_fid].fact.quantity is not None:
            sourced_area = index[area_fid].fact.quantity
    for decade in curation.WALKTHROUGH_STOPS:
        area_fid = curation.WALKTHROUGH_FLOOR_AREA.get(decade)
        area_fact = index[area_fid].fact if area_fid is not None else None
        if area_fact is not None and area_fact.quantity is not None and sourced_area:
            scale = (area_fact.quantity / sourced_area) ** 0.5
            gap = False
            caption = f"{area_fact.quantity:,.0f} sq ft (sourced)"
        else:
            scale = 0.75  # reference outline only — carries no datum
            gap = True
            caption = (
                "rooms counted, floor area not measured"
                if area_fact is not None
                else "floor area not yet curated"
            )
        w = round(150 * scale)
        hgt = round(120 * scale)
        houses.append(
            WalkthroughHouse(
                decade=decade,
                fact_id=area_fid or "",
                href=(
                    f"#{area_fid}--modal"
                    if area_fid is not None and area_fact is not None
                    else ""
                ),
                gap=gap,
                w=w,
                hgt=hgt,
                path=(
                    f"M{w * 0.08:.0f} {hgt * 0.45:.0f} L{w * 0.5:.0f} {hgt * 0.08:.0f} "
                    f"L{w * 0.92:.0f} {hgt * 0.45:.0f} M{w * 0.15:.0f} {hgt * 0.45:.0f} "
                    f"V{hgt * 0.92:.0f} H{w * 0.85:.0f} V{hgt * 0.45:.0f}"
                ),
                caption=caption,
            )
        )
        if area_fid is not None and area_fact is not None:
            overlay_ids.append(area_fid)
    return tuple(houses)


def project_walkthrough(
    corpus: Corpus,
    index: dict[str, FactRef],
    rooms: list[Room] | tuple[Room, ...],
    affordability: dict[str, dict[str, str]],
) -> WalkthroughPage:
    """Project the guided transect into a ``WalkthroughPage``."""
    rooms_by_decade = {room.decade: room for room in rooms}
    overlay_ids: list[str] = []

    stop_sections = _build_stop_sections(rooms_by_decade, index, overlay_ids)
    metrics = _build_metrics(index, overlay_ids)
    meter = _build_meter(index, overlay_ids)
    houses = _build_houses(index, overlay_ids)

    women_arc = curation.ARC_BY_SLUG["home-production-women"]

    return WalkthroughPage(
        stops=tuple(curation.WALKTHROUGH_STOPS),
        stop_sections=stop_sections,
        metrics=metrics,
        meter=meter,
        meter_caveats=women_arc.caveats,
        houses=houses,
        sources=corpus.sources,
        assumptions=corpus.assumptions,
        affordability=affordability,
        overlay_facts=overlay_facts(index, tuple(overlay_ids)),
    )
