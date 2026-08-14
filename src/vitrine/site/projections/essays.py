"""Docent projections — essays assembled into typed pages.

The docent may interpret; the docent may not quote from memory. Prose is
interpolated here with fact chips (value + tier, deep-linked), resolved
*after* the core gate has already stripped and scanned the raw copy. Chart
blocks reuse the corridor builders verbatim — an arc in an essay is the same
projection as the same arc in its wing. Unknown chart slugs are a red build
(``validate_essay_registries``), mirroring the room-story and wing gates.
"""

from __future__ import annotations

import re

from markupsafe import Markup, escape

from vitrine.derive import ComputedFact
from vitrine.model import INTERPOLATION_RE, BlockKind, Corpus, Essay, tier_label
from vitrine.series import Series
from vitrine.site import curation, svg, tokens
from vitrine.site.context import (
    EssayBlockView,
    EssayEntryView,
    EssayLink,
    EssayPage,
    EssaysIndexPage,
)
from vitrine.site.projections.arcs import arc_chart_for, arc_group_chart_for
from vitrine.site.projections.facts import FactRef, overlay_facts
from vitrine.site.projections.metrics import metric_markers, resolve_metric

_PARAGRAPH_RE = re.compile(r"\n\s*\n")


def _chip(fact_id: str, label_only: bool, ref: FactRef) -> Markup:
    fact = ref.fact
    href = f"#{fact_id}--modal"
    tier = fact.tier.value
    chip = (
        f'<span class="tchip" title="{escape(tier_label(fact.tier))}" '
        f'style="background:{tokens.TIER_COLORS[tier]}">{tier}</span>'
    )
    body = (
        escape(fact.label)
        if label_only
        else Markup(f'<b class="factchip-val">{escape(fact.value)}</b>{chip}')
    )
    return Markup(
        f'<a class="factchip" href="{href}" data-fact-id="{fact_id}">{body}</a>'
    )


def _derived_chip(
    fact_id: str, label_only: bool, cf: ComputedFact, root: str
) -> Markup:
    room_slug = "-".join(cf.id.split("-")[:2])
    href = f"{root}rooms/{room_slug}.html#{cf.id}"
    tier = cf.tier.value
    chip = (
        f'<span class="tchip" title="Computed; weakest input governs" '
        f'style="background:{tokens.TIER_COLORS[tier]}">{tier}</span>'
    )
    body = (
        escape(cf.label)
        if label_only
        else Markup(f'<b class="factchip-val">{escape(cf.value)}</b>{chip}')
    )
    return Markup(
        f'<a class="factchip computed" href="{href}" data-fact-id="{fact_id}">'
        f'{body}<span class="record-kind">computed</span></a>'
    )


def interpolate(
    text: str,
    index: dict[str, FactRef],
    derived_by_id: dict[str, ComputedFact],
    root: str,
) -> Markup:
    """Resolve ``{fact:…}`` bindings into deep-linked provenance chips."""
    out: list[str] = []
    cursor = 0
    for match in INTERPOLATION_RE.finditer(text):
        out.append(str(escape(text[cursor : match.start()])))
        fact_id, label_only = match.group(1), bool(match.group(2))
        ref = index.get(fact_id)
        if ref is not None:
            out.append(str(_chip(fact_id, label_only, ref)))
        else:
            cf = derived_by_id[fact_id]  # the gate proved it resolves
            out.append(str(_derived_chip(fact_id, label_only, cf, root)))
        cursor = match.end()
    out.append(str(escape(text[cursor:])))
    return Markup("".join(out))


def interpolate_paragraphs(
    text: str,
    index: dict[str, FactRef],
    derived_by_id: dict[str, ComputedFact],
    root: str,
) -> Markup:
    """Interpolate prose and wrap each blank-line-separated paragraph."""
    paragraphs = [
        f"<p>{interpolate(chunk.strip(), index, derived_by_id, root)}</p>"
        for chunk in _PARAGRAPH_RE.split(text)
        if chunk.strip()
    ]
    return Markup("".join(paragraphs))


def _chart_block(
    block_slug: tuple[str, str, str],
    index: dict[str, FactRef],
    series: dict[str, Series],
    recessions: tuple[svg.Recession, ...],
    root: str,
) -> EssayBlockView:
    """Render one CHART block by reusing the corridor builders."""
    arc_slug, group_slug, metric_slug = block_slug
    if arc_slug:
        arc = curation.ARC_BY_SLUG[arc_slug]
        return EssayBlockView(
            kind=BlockKind.CHART,
            prose=Markup(""),
            chart_slug=arc_slug,
            chart=Markup(arc_chart_for(arc, index, series, root)),
            chart_label=arc.label,
            chart_unit=arc.unit,
            caveats=arc.caveats,
        )
    if group_slug:
        group = curation.ARC_GROUP_BY_SLUG[group_slug]
        return EssayBlockView(
            kind=BlockKind.CHART,
            prose=Markup(""),
            chart_slug=group_slug,
            chart=Markup(arc_group_chart_for(group, index, root)),
            chart_label=group.label,
            chart_unit=group.unit,
            caveats=group.caveats,
        )
    metric = curation.METRIC_BY_SLUG[metric_slug]
    values, note = resolve_metric(metric, series)
    markers = metric_markers(metric, index, root)
    chart = Markup("")
    if values or markers:
        chart = Markup(
            svg.affordability_chart(
                values,
                recessions,
                metric.unit,
                metric_slug=metric.slug,
                falling=metric.falling,
                markers=markers,
                zero_baseline=metric.zero_baseline,
            )
        )
    return EssayBlockView(
        kind=BlockKind.CHART,
        prose=Markup(""),
        chart_slug=metric_slug,
        chart=chart,
        chart_label=metric.label,
        chart_unit=metric.unit,
        caveats=metric.caveats,
        note=note or metric.caption,
    )


def validate_essay_registries(corpus: Corpus) -> None:
    """Build-time gate: every essay chart slug must resolve to a registry."""
    problems: list[str] = []
    for essay in corpus.essays:
        for i, block in enumerate(essay.blocks, start=1):
            if block.kind is not BlockKind.CHART:
                continue
            if block.arc and block.arc not in curation.ARC_BY_SLUG:
                problems.append(f"{essay.slug} block {i}: unknown arc {block.arc!r}")
            if block.group and block.group not in curation.ARC_GROUP_BY_SLUG:
                problems.append(
                    f"{essay.slug} block {i}: unknown group {block.group!r}"
                )
            if block.metric and block.metric not in curation.METRIC_BY_SLUG:
                problems.append(
                    f"{essay.slug} block {i}: unknown metric {block.metric!r}"
                )
    if problems:
        raise ValueError("essay registry validation failed: " + "; ".join(problems))


def _essay_fact_ids(essay: Essay, index: dict[str, FactRef]) -> set[str]:
    """Corpus fact ids an essay engages — resolved prose ids plus chart ids."""
    ids: set[str] = set()
    texts = [essay.standfirst] + [
        b.text for b in essay.blocks if b.kind is BlockKind.PROSE
    ]
    for text in texts:
        ids.update(
            match.group(1)
            for match in INTERPOLATION_RE.finditer(text)
            if match.group(1) in index
        )
    for block in essay.blocks:
        if block.kind is not BlockKind.CHART:
            continue
        if block.arc:
            ids.update(curation.ARC_BY_SLUG[block.arc].fact_ids.values())
        elif block.group:
            for arc_slug, *_ in curation.ARC_GROUP_BY_SLUG[block.group].members:
                ids.update(curation.ARC_BY_SLUG[arc_slug].fact_ids.values())
        elif block.metric:
            metric = curation.METRIC_BY_SLUG[block.metric]
            if metric.source_arc:
                ids.update(curation.ARC_BY_SLUG[metric.source_arc].fact_ids.values())
    return ids


def _essay_derived_room_slugs(essay: Essay, index: dict[str, FactRef]) -> set[str]:
    """Room slugs an essay engages via *derived* interpolations (not in the index).

    A derived fact's id follows ``<country>-<decade>-<slug>``; the room slug is
    the first two parts. Keying by slug (not decade alone) keeps a second
    country's room of the same decade from inheriting another country's tour
    backlinks — the WI-024 collision.
    """
    slugs: set[str] = set()
    for text in (essay.standfirst, *(b.text for b in essay.blocks)):
        for match in INTERPOLATION_RE.finditer(text):
            if match.group(1) not in index:
                parts = match.group(1).split("-")
                if len(parts) >= 2:
                    slugs.add("-".join(parts[:2]))
    return slugs


def _rooms_cited(fact_ids: set[str], index: dict[str, FactRef]) -> tuple[str, ...]:
    return tuple(sorted({index[fid].room.slug for fid in fact_ids}))


def essays_by_room(
    corpus: Corpus, index: dict[str, FactRef]
) -> dict[str, tuple[EssayLink, ...]]:
    """Room backlink index: which tours cite each room's exhibits.

    Keyed by room slug (``<country>-<decade>``), not decade alone, so a second
    country's room of the same decade never inherits another country's tours.
    """
    by_room: dict[str, list[EssayLink]] = {}
    for essay in corpus.essays:
        slugs = set(_rooms_cited(_essay_fact_ids(essay, index), index))
        slugs |= _essay_derived_room_slugs(essay, index)
        for slug in sorted(slugs):
            by_room.setdefault(slug, []).append(
                EssayLink(slug=essay.slug, title=essay.title)
            )
    return {slug: tuple(links) for slug, links in by_room.items()}


def project_essay(
    corpus: Corpus,
    essay: Essay,
    index: dict[str, FactRef],
    series: dict[str, Series],
    computed_by_room: dict[str, tuple[ComputedFact, ...]],
    affordability: dict[str, dict[str, str]],
    recessions: tuple[svg.Recession, ...],
    root: str,
) -> EssayPage:
    """Project one docent tour into a fully-prepared ``EssayPage``."""
    derived_by_id = {cf.id: cf for c in computed_by_room.values() for cf in c}
    blocks: list[EssayBlockView] = []
    for block in essay.blocks:
        if block.kind is BlockKind.PROSE:
            blocks.append(
                EssayBlockView(
                    kind=BlockKind.PROSE,
                    prose=interpolate_paragraphs(block.text, index, derived_by_id, root),
                    chart_slug="",
                    chart=Markup(""),
                    chart_label="",
                    chart_unit="",
                    caveats=(),
                )
            )
        else:
            slugs = (block.arc, block.group, block.metric)
            blocks.append(_chart_block(slugs, index, series, recessions, root))
    prose_ids = _essay_fact_ids(essay, index)
    return EssayPage(
        slug=essay.slug,
        title=essay.title,
        standfirst=interpolate(essay.standfirst, index, derived_by_id, root),
        blocks=tuple(blocks),
        rooms_cited=tuple(
            sorted(set(_rooms_cited(prose_ids, index)) | _essay_derived_room_slugs(essay, index))
        ),
        sources=corpus.sources,
        assumptions=corpus.assumptions,
        affordability=affordability,
        overlay_facts=overlay_facts(index, tuple(sorted(prose_ids))),
    )


def essay_entry_views(
    corpus: Corpus,
    index: dict[str, FactRef],
    computed_by_room: dict[str, tuple[ComputedFact, ...]],
    root: str,
) -> tuple[EssayEntryView, ...]:
    """Directory rows for the docent tours — shared by the lobby and the index."""
    derived_by_id = {cf.id: cf for c in computed_by_room.values() for cf in c}
    entries: list[EssayEntryView] = []
    for essay in corpus.essays:
        ids = _essay_fact_ids(essay, index)
        entries.append(
            EssayEntryView(
                slug=essay.slug,
                title=essay.title,
                standfirst=interpolate(essay.standfirst, index, derived_by_id, root),
                blocks=len(essay.blocks),
                rooms_cited=tuple(
                    sorted(
                        set(_rooms_cited(ids, index))
                        | _essay_derived_room_slugs(essay, index)
                    )
                ),
            )
        )
    return tuple(entries)


def project_essays_index(
    corpus: Corpus,
    index: dict[str, FactRef],
    computed_by_room: dict[str, tuple[ComputedFact, ...]],
    affordability: dict[str, dict[str, str]],
    root: str,
) -> EssaysIndexPage:
    """Project the docent-tour directory."""
    overlay_ids: list[str] = []
    for essay in corpus.essays:
        overlay_ids.extend(sorted(_essay_fact_ids(essay, index)))
    return EssaysIndexPage(
        entries=essay_entry_views(corpus, index, computed_by_room, root),
        overlay_facts=overlay_facts(index, tuple(overlay_ids)),
        sources=corpus.sources,
        assumptions=corpus.assumptions,
        affordability=affordability,
    )


__all__ = [
    "essay_entry_views",
    "essays_by_room",
    "interpolate",
    "interpolate_paragraphs",
    "project_essay",
    "project_essays_index",
    "validate_essay_registries",
]
