"""Stage projection — the house cutaway for one room or walkthrough stop.

Builds the ``svg.Stage`` (artifacts placed by curation, zone notes folded from
the composition fact, home-scale from the floor-area datum). The orchestrator
wraps the returned stage with ``svg.stage_svg`` + ``Markup``.
"""

from __future__ import annotations

from vitrine.model import Room
from vitrine.site import curation, svg, symbols
from vitrine.site.projections.arcs import fold_shares
from vitrine.site.projections.facts import FactRef, placard_href


def build_stage(room: Room, index: dict[str, FactRef], root: str) -> svg.Stage:
    artifacts: list[svg.StageArtifact] = []
    for artifact, (x, y) in svg.STAGE_POS.items():
        fid = curation.STAGE_DIFFUSION.get(artifact, {}).get(room.decade)
        kind = "diffusion"
        if fid is None:
            fid = curation.STAGE_STATS.get(artifact, {}).get(room.decade)
            kind = "stat"
        if fid is None:
            continue  # absent technology isn't drawn
        ref = index[fid]
        sym = symbols.symbol(artifact, room.decade, ref.fact.value)
        if sym is None:
            continue
        artifacts.append(
            svg.StageArtifact(
                artifact=artifact,
                glyph_svg=sym.svg,
                x=x,
                y=y,
                fact_id=fid,
                href=placard_href(index, fid, root),
                label=ref.fact.label,
                value=ref.fact.value,
                quantity=ref.fact.quantity if kind == "diffusion" else None,
                kind=kind,
            )
        )

    zone_notes: list[svg.ZoneNote] = []
    comp_id = curation.COMPOSITIONS.get(room.decade)
    if comp_id is not None:
        segments = fold_shares(index[comp_id].fact, index, root)
        for seg in segments:
            pos = curation.ZONE_NOTE_POS.get(seg.slot)
            if pos is None:
                continue
            zone_notes.append(
                svg.ZoneNote(
                    text=f"{seg.slot} {seg.pct:g}% of spending",
                    x=pos[0],
                    y=pos[1],
                    fact_id=seg.fact_id,
                    href=seg.href,
                )
            )
    else:
        food_arc = curation.ARC_BY_SLUG["food-share"]
        fid = food_arc.fact_ids.get(room.decade)
        if fid is not None and index[fid].fact.quantity is not None:
            fact = index[fid].fact
            x, y = curation.ZONE_NOTE_POS["food"]
            zone_notes.append(
                svg.ZoneNote(
                    text=f"food {fact.quantity:g}% of spending",
                    x=x,
                    y=y,
                    fact_id=fid,
                    href=placard_href(index, fid, root),
                )
            )

    # home-scale: proportionally scale the house outline to the sourced
    # floor-area datum, so the visitor sees the home grow across decades.
    home_scale = 1.0
    size_fid = curation.HOME_SIZE_FACTS.get(room.decade)
    if size_fid is not None and size_fid in index:
        size_fact = index[size_fid].fact
        if size_fact.quantity is not None:
            # baseline: 1,525 sq ft (1970s, the earliest datum). Scale by
            # sqrt so the linear dimension changes proportionally.
            home_scale = max(0.6, min(1.35, (size_fact.quantity / 1525.0) ** 0.5))

    return svg.Stage(
        decade=room.decade,
        artifacts=tuple(artifacts),
        zone_notes=tuple(zone_notes),
        home_scale=home_scale,
    )
