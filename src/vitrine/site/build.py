"""Build orchestration — renders the static site from the corpus.

This module is thin orchestration: it calls projections to build typed contexts,
then renders package-resource templates. No template logic, no SVG generation,
no affordability computation lives here.
"""

from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, PackageLoader, select_autoescape
from markupsafe import Markup

from vitrine.compare import compare_item
from vitrine.derive import ComputedFact, evaluate_room
from vitrine.model import (
    Corpus,
    Panel,
    Room,
    basis_label,
    panel_title,
    tier_label,
)
from vitrine.series import Series
from vitrine.site import curation, svg, tokens
from vitrine.site.context import (
    AffordabilityDashboardSection,
    ArcSection,
    CompositionRow,
    CorridorAffordSection,
    PanelSection,
    WalkthroughHouse,
    WalkthroughMetric,
    WalkthroughMetricCell,
    WalkthroughPerson,
    WalkthroughPersonRow,
    WalkthroughStop,
)
from vitrine.site.projections import (
    FactRef,
    afford_arc_chart,
    afford_fact_ids,
    affordability_for_room,
    arc_chart_for,
    arc_group_chart_for,
    build_stage,
    fold_shares,
    index_facts,
    load_recessions,
    metric_markers,
    pair_afford,
    pair_families,
    placard_href,
    resolve_metric,
)

_FIGS = {
    "father": '<path class="fig" d="M-12 -26 L12 -26 L8 44 L-8 44 Z"/><circle class="fig head" cx="0" cy="-37" r="9"/>',
    "mother": '<path class="fig" d="M-9 -25 L9 -25 L5 12 L15 44 L-15 44 L-5 12 Z"/><circle class="fig head" cx="0" cy="-36" r="8.5"/>',
    "children": '<g transform="translate(-11,4)"><path class="fig" d="M-7 -14 L7 -14 L5 28 L-5 28 Z"/><circle class="fig head" cx="0" cy="-23" r="6.5"/></g><g transform="translate(13,10) scale(0.82)"><path class="fig" d="M-7 -14 L7 -14 L5 28 L-5 28 Z"/><circle class="fig head" cx="0" cy="-23" r="6.5"/></g>',
}


def _make_env() -> Environment:
    env = Environment(
        loader=PackageLoader("vitrine.site", "templates"),
        autoescape=select_autoescape(default=True),
    )
    env.globals["panel_title"] = panel_title
    env.globals["tier_label"] = tier_label
    env.globals["basis_label"] = basis_label
    env.globals["T"] = tokens
    env.globals["tier_names"] = {
        "A": "official statistical series",
        "B": "official microdata, computed by this project",
        "C": "reconstructed from period surveys",
        "D": "scholarly estimate",
    }
    return env


def _overlay_facts(
    index: dict[str, FactRef], fact_ids: tuple[str, ...]
) -> tuple[FactRef, ...]:
    """Unique fact refs for the popup placard layer on corridor pages."""
    seen: set[str] = set()
    refs: list[FactRef] = []
    for fid in fact_ids:
        if fid in seen or fid not in index:
            continue
        seen.add(fid)
        refs.append(index[fid])
    return tuple(refs)


def _panels_for(
    room: Room, computed: tuple[ComputedFact, ...]
) -> list[PanelSection]:
    return [
        PanelSection(
            panel=panel,
            facts=[f for f in room.facts if f.panel is panel],
            computed=[c for c in computed if c.panel is panel],
        )
        for panel in Panel
    ]


def build_site(
    corpus: Corpus,
    out_dir: Path,
    series: dict[str, Series] | None = None,
    data_dir: Path | None = None,
) -> None:
    if series is None:
        series = {}
    env = _make_env()

    disclaimer_entry = corpus.assumptions.get("composite-family")
    if disclaimer_entry is None:
        raise ValueError(
            "assumption ledger must contain 'composite-family' — "
            "the disclaimer renders on every room (charter rule)"
        )
    env.globals["disclaimer"] = disclaimer_entry.statement
    env.globals["disclaimer_title"] = disclaimer_entry.title

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "rooms").mkdir(exist_ok=True)
    (out_dir / "corridors").mkdir(exist_ok=True)
    (out_dir / "assets").mkdir(exist_ok=True)

    # copy the stylesheet and enhancement script
    css_path = Path(__file__).parent / "assets" / "vitrine.css"
    (out_dir / "assets" / "vitrine.css").write_text(css_path.read_text())
    js_path = Path(__file__).parent / "assets" / "placard.js"
    (out_dir / "assets" / "placard.js").write_text(js_path.read_text())

    index = index_facts(corpus)
    rooms = sorted(corpus.rooms, key=lambda r: r.decade)
    decades = [room.decade for room in rooms]

    # lobby
    (out_dir / "index.html").write_text(
        env.get_template("index.html").render(root="", rooms=rooms)
    )

    # methodology
    (out_dir / "methodology.html").write_text(
        env.get_template("methodology.html").render(
            root="", assumptions=list(corpus.assumptions.values())
        )
    )

    # bibliography
    (out_dir / "bibliography.html").write_text(
        env.get_template("bibliography.html").render(
            root="", sources=list(corpus.sources.values())
        )
    )

    # rooms
    rendered_ids: list[str] = []
    all_affordability: dict[str, dict[str, str]] = {}
    for room in rooms:
        computed = evaluate_room(room, series)
        room_afford = affordability_for_room(corpus, room)
        all_affordability.update(room_afford)
        (out_dir / "rooms" / f"{room.slug}.html").write_text(
            env.get_template("room.html").render(
                root="../",
                room=room,
                rooms=rooms,
                stage_svg=Markup(svg.stage_svg(build_stage(room, index, "../"), overlay_links=True)),
                panels=_panels_for(room, computed),
                sources=corpus.sources,
                assumptions=corpus.assumptions,
                affordability=room_afford,
                gap_banner=curation.ROOM_GAP_BANNERS.get(room.decade, ""),
            )
        )
        rendered_ids.extend(fact.id for fact in room.facts)
        rendered_ids.extend(cf.id for cf in computed)

    # corridors index
    corridor_root = "../"
    arc_sections: list[ArcSection] = []
    rendered_groups: set[str] = set()
    for arc in curation.ARCS:
        group = curation.ARC_GROUP_BY_MEMBER.get(arc.slug)
        if group is not None:
            if group.slug in rendered_groups:
                continue
            rendered_groups.add(group.slug)
            arc_sections.append(
                ArcSection(
                    slug=group.slug,
                    label=group.label,
                    unit=group.unit,
                    caveats=group.caveats,
                    chart=Markup(arc_group_chart_for(group, index, corridor_root)),
                )
            )
            continue
        arc_sections.append(
            ArcSection(
                slug=arc.slug,
                label=arc.label,
                unit=arc.unit,
                caveats=arc.caveats,
                chart=Markup(arc_chart_for(arc, index, series, corridor_root)),
            )
        )

    afford_sections: list[CorridorAffordSection] = []
    for _slug, label, pattern in curation.AFFORD_ITEMS:
        ids = afford_fact_ids(corpus, pattern)
        if len(ids) < 2:
            continue
        comparison = compare_item(corpus, label, ids)
        caveats = curation.AFFORD_ITEM_CAVEATS.get(_slug, ()) + comparison.caveats
        afford_sections.append(
            CorridorAffordSection(
                label=label,
                caveats=caveats,
                chart=Markup(afford_arc_chart(comparison, ids, index, corridor_root)),
            )
        )

    comp_rows: list[CompositionRow] = []
    for decade in sorted(curation.COMPOSITIONS):
        fact_id = curation.COMPOSITIONS[decade]
        fact = index[fact_id].fact
        segments = fold_shares(fact, index, corridor_root)
        if segments:
            comp_rows.append(
                CompositionRow(
                    bar=Markup(svg.composition_bar(decade, segments)),
                    decade=decade,
                    fact_id=fact_id,
                    segments=segments,
                )
            )
    comp_caveats = (
        "Survey populations differ across the century — 1901 wage-earner families "
        "vs modern consumer units; each bar links to its placard, which names who "
        "was measured.",
    )
    epochs = [("1900s", "1950s"), ("1950s", "2020s"), ("1900s", "2020s")]
    corridor_overlay_ids: list[str] = []
    for arc in curation.ARCS:
        corridor_overlay_ids.extend(arc.fact_ids.values())
    for _slug, _label, pattern in curation.AFFORD_ITEMS:
        corridor_overlay_ids.extend(afford_fact_ids(corpus, pattern).values())
    corridor_overlay_ids.extend(curation.COMPOSITIONS.values())
    (out_dir / "corridors" / "index.html").write_text(
        env.get_template("corridors.html").render(
            root=corridor_root,
            decades=decades,
            epochs=epochs,
            arc_sections=arc_sections,
            afford_sections=afford_sections,
            comp_rows=comp_rows,
            comp_caveats=comp_caveats,
            sources=corpus.sources,
            assumptions=corpus.assumptions,
            affordability=all_affordability,
            overlay_facts=_overlay_facts(index, tuple(corridor_overlay_ids)),
        )
    )

    # pairwise set
    for i, a in enumerate(decades):
        for b in decades[i + 1 :]:
            pair_comp_rows: list[CompositionRow] = []
            pair_overlay_ids: list[str] = []
            if a in curation.COMPOSITIONS and b in curation.COMPOSITIONS:
                for decade in (a, b):
                    pair_overlay_ids.append(curation.COMPOSITIONS[decade])
                    fact = index[curation.COMPOSITIONS[decade]].fact
                    segments = fold_shares(fact, index, corridor_root)
                    if segments:
                        pair_comp_rows.append(
                            CompositionRow(
                                bar=Markup(svg.composition_bar(decade, segments)),
                                decade=decade,
                                fact_id=curation.COMPOSITIONS[decade],
                                segments=segments,
                            )
                        )
            pair_fams = pair_families(index, a, b, corridor_root)
            for fam in pair_fams:
                pair_overlay_ids.extend(cell.fact_id for cell in fam.cells)
            pair_afford_secs = pair_afford(corpus, index, a, b, corridor_root)
            for section in pair_afford_secs:
                pair_overlay_ids.extend(row.fact_id for row in section.rows)
            (out_dir / "corridors" / f"{a}--{b}.html").write_text(
                env.get_template("pair.html").render(
                    root=corridor_root,
                    a=a,
                    b=b,
                    families=pair_fams,
                    afford_sections=pair_afford_secs,
                    comp_rows=pair_comp_rows,
                    sources=corpus.sources,
                    assumptions=corpus.assumptions,
                    affordability=all_affordability,
                    overlay_facts=_overlay_facts(index, tuple(pair_overlay_ids)),
                )
            )

    # walkthrough
    stop_sections: list[WalkthroughStop] = []
    walkthrough_overlay_ids: list[str] = []
    for decade in curation.WALKTHROUGH_STOPS:
        room = next(r for r in rooms if r.decade == decade)
        stage = build_stage(room, index, "")
        walkthrough_overlay_ids.extend(a.fact_id for a in stage.artifacts)
        walkthrough_overlay_ids.extend(n.fact_id for n in stage.zone_notes)
        people: list[WalkthroughPerson] = []
        for figure, name in (
            ("father", "The paid-work record"),
            ("mother", "The unpaid-work record"),
            ("children", "The childhood record"),
        ):
            rows: list[WalkthroughPersonRow] = []
            for fid in curation.WALKTHROUGH_PEOPLE[figure].get(decade, ()):
                fact = index[fid].fact
                walkthrough_overlay_ids.append(fid)
                rows.append(
                    WalkthroughPersonRow(
                        fact_id=fid,
                        href=f"#{fid}--modal",
                        label=fact.label,
                        value=fact.value if len(fact.value) <= 90 else fact.value[:87] + "…",
                        tier=fact.tier.value,
                    )
                )
            people.append(
                WalkthroughPerson(name=name, fig=Markup(_FIGS[figure]), rows=rows)
            )
        stop_sections.append(
            WalkthroughStop(
                decade=decade,
                stage=Markup(svg.stage_svg(stage, overlay_links=True)),
                people=people,
            )
        )

    metrics: list[WalkthroughMetric] = []
    for slug in curation.WALKTHROUGH_METRICS:
        arc = curation.ARC_BY_SLUG[slug]
        stop_facts = [
            (d, arc.fact_ids.get(d)) for d in curation.WALKTHROUGH_STOPS
        ]
        quantities = [
            q
            for _, mfid in stop_facts
            if mfid is not None and (q := index[mfid].fact.quantity) is not None
        ]
        q_max = max(quantities) if quantities else 1.0
        cells: list[WalkthroughMetricCell] = []
        for decade, mfid in stop_facts:
            if mfid is None:
                cells.append(
                    WalkthroughMetricCell(
                        decade=decade, fact_id="", href="", tier="", gap=True,
                        text="not yet curated", bar=0
                    )
                )
                continue
            fact = index[mfid].fact
            walkthrough_overlay_ids.append(mfid)
            cells.append(
                WalkthroughMetricCell(
                    decade=decade,
                    fact_id=mfid,
                    href=f"#{mfid}--modal",
                    tier=fact.tier.value,
                    gap=fact.quantity is None,
                    text="see the placard" if fact.quantity is None else f"{fact.quantity:g}",
                    bar=0 if fact.quantity is None or q_max == 0 else round(100 * fact.quantity / q_max),
                )
            )
        metrics.append(
            WalkthroughMetric(label=arc.label, unit=arc.unit, falling=arc.falling, cells=cells)
        )

    women_arc = curation.ARC_BY_SLUG["home-production-women"]
    meter_bars = []
    for decade in sorted(women_arc.fact_ids):
        fid = women_arc.fact_ids[decade]
        fact = index[fid].fact
        walkthrough_overlay_ids.append(fid)
        meter_bars.append(
            svg.MeterBar(
                decade=decade,
                fact_id=fid,
                href=placard_href(index, fid, ""),
                tier=fact.tier.value,
                label=fact.label,
                value=fact.value,
                quantity=(
                    None if decade in women_arc.plot_gaps else fact.quantity
                ),
                note=(
                    "different unit and concept — see the placard"
                    if decade in women_arc.plot_gaps
                    else ""
                ),
            )
        )
    meter = Markup(svg.hours_meter(tuple(meter_bars), women_arc.unit, overlay_links=True))

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
            scale = 0.75
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
                fact_id=area_fid if area_fid is not None and area_fact is not None else "",
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
            walkthrough_overlay_ids.append(area_fid)

    (out_dir / "walkthrough.html").write_text(
        env.get_template("walkthrough.html").render(
            root="",
            stops=list(curation.WALKTHROUGH_STOPS),
            stop_sections=stop_sections,
            metrics=metrics,
            meter=meter,
            meter_caveats=women_arc.caveats,
            houses=houses,
            sources=corpus.sources,
            assumptions=corpus.assumptions,
            affordability=all_affordability,
            overlay_facts=_overlay_facts(index, tuple(walkthrough_overlay_ids)),
        )
    )

    # affordability dashboard
    recessions, recession_url = load_recessions((data_dir or Path("data")) / "recessions.toml")
    _build_affordability(corpus, series, recessions, recession_url, index, env, out_dir)

    (out_dir / "facts-manifest.txt").write_text("\n".join(rendered_ids) + "\n")


def _build_affordability(
    corpus: Corpus,
    series: dict[str, Series],
    recessions: tuple[svg.Recession, ...],
    recession_url: str,
    index: dict[str, FactRef],
    env: Environment,
    out_dir: Path,
) -> None:
    """Build the /affordability/ dashboard — five stacked metric charts."""
    sections: list[AffordabilityDashboardSection] = []
    for metric in curation.AFFORDABILITY_METRICS:
        values, note = resolve_metric(metric, series)
        markers = metric_markers(metric, index, "../")
        if not values and not markers:
            sections.append(
                AffordabilityDashboardSection(
                    metric=metric, chart="", note=note or "no data yet"
                )
            )
            continue
        chart = svg.affordability_chart(
            values,
            recessions,
            metric.unit,
            metric_slug=metric.slug,
            falling=metric.falling,
            markers=markers,
            zero_baseline=metric.zero_baseline,
        )
        sections.append(
            AffordabilityDashboardSection(metric=metric, chart=Markup(chart), note=note)
        )
    (out_dir / "affordability").mkdir(exist_ok=True)
    (out_dir / "affordability" / "index.html").write_text(
        env.get_template("affordability.html").render(
            root="../",
            sections=sections,
            disclaimer=env.globals["disclaimer"],
            recession_url=recession_url,
        )
    )
