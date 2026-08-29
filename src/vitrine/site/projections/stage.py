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
    curated = curation.STAGE_BY_COUNTRY.get(room.country)
    # A country without stage curation would silently borrow the US room of
    # the same decade through the shared, decade-keyed registries. It gets a
    # bare stage instead; its facts still render in the ledgers below.
    if curated is None:
        return svg.Stage(decade=room.decade, artifacts=(), zone_notes=())

    room_ids = {fact.id for fact in room.facts}

    def resolve(fid: str, what: str) -> FactRef:
        if fid not in room_ids:
            raise ValueError(
                f"room {room.slug}: stage {what} names fact {fid!r} outside "
                "the room — a stage may only draw its own room's exhibits"
            )
        return index[fid]

    # The locale's layout: shared artifact positions, overridden where the
    # country's curation says otherwise.
    layout: dict[str, tuple[int, int]] = dict(svg.STAGE_POS)
    layout.update(curated.positions)

    artifacts: list[svg.StageArtifact] = []
    for artifact, (x, y) in layout.items():
        fid = curated.diffusion.get(artifact, {}).get(room.decade)
        kind = "diffusion"
        if fid is None:
            fid = curated.stats.get(artifact, {}).get(room.decade)
            kind = "stat"
        if fid is None:
            continue  # absent technology isn't drawn
        ref = resolve(fid, f"artifact {artifact!r}")
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
    comp_id = curated.compositions.get(room.decade)
    if comp_id is not None:
        segments = fold_shares(resolve(comp_id, "composition").fact, index, root)
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
        fs_fid = curated.food_share.get(room.decade)
        if fs_fid is not None:
            fact = resolve(fs_fid, "food-share note").fact
            if fact.quantity is not None:
                x, y = curation.ZONE_NOTE_POS["food"]
                zone_notes.append(
                    svg.ZoneNote(
                        text=f"food {fact.quantity:g}% of spending",
                        x=x,
                        y=y,
                        fact_id=fs_fid,
                        href=placard_href(index, fs_fid, root),
                    )
                )

    # home-scale: proportionally scale the house outline to the sourced
    # floor-area datum, so the visitor sees the home grow across decades.
    home_scale = 1.0
    size_fid = curated.home_size.get(room.decade)
    if size_fid is not None:
        size_fact = resolve(size_fid, "home-scale").fact
        if size_fact.quantity is not None:
            if curated.home_size_baseline is None or curated.home_size_baseline <= 0:
                raise ValueError(
                    f"room {room.slug}: home-scale datum needs a positive "
                    "home_size_baseline in the country's stage curation"
                )
            # Scale by sqrt so the linear dimension changes proportionally,
            # clamped so a locale cannot balloon or vanish the outline.
            home_scale = max(
                0.6,
                min(1.35, (size_fact.quantity / curated.home_size_baseline) ** 0.5),
            )

    return svg.Stage(
        decade=room.decade,
        artifacts=tuple(artifacts),
        zone_notes=tuple(zone_notes),
        home_scale=home_scale,
    )
