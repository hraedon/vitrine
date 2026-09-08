"""Resolve the Japan exhibit without converting archive decades into dates."""

from __future__ import annotations

import re

from markupsafe import Markup

from vitrine.model import Corpus, Fact
from vitrine.site import symbols
from vitrine.site.context import (
    CollectionLensView,
    CollectionObservationView,
    CollectionThemeView,
    JapanCollectionPage,
)
from vitrine.site.curation.collections import JAPAN_EDITORIAL, JAPAN_THEMES, CollectionTheme
from vitrine.site.projections.facts import GAP_PREFIX, index_facts


def observation_year(fact: Fact) -> int:
    """Require an unambiguous year in the authored label, agreeing with price_year.

    Never fall back to the room decade or publication year. A new compound or
    undated selection needs editorial attention instead of an inferred date.
    """
    years = {int(y) for y in re.findall(r"\b(?:18|19|20)\d{2}\b", fact.label)}
    if len(years) != 1:
        raise ValueError(f"collection fact {fact.id} needs one observation year in its label")
    year = years.pop()
    if fact.price_year is not None and year != fact.price_year:
        raise ValueError(f"collection fact {fact.id}: label and price year disagree")
    return year


def project_japan_collection(
    corpus: Corpus, themes: tuple[CollectionTheme, ...] = JAPAN_THEMES,
) -> JapanCollectionPage:
    index = index_facts(corpus)
    seen: set[str] = set()
    slugs: set[str] = set()
    views: list[CollectionThemeView] = []
    for theme in themes:
        if theme.slug in slugs or not re.fullmatch(r"[a-z][a-z0-9-]*", theme.slug):
            raise ValueError(f"collection theme slug must be unique and portable: {theme.slug}")
        slugs.add(theme.slug)
        if not theme.lenses:
            raise ValueError(f"collection theme needs a source lens: {theme.slug}")
        lenses: list[CollectionLensView] = []
        for lens in theme.lenses:
            if lens.slug in slugs or not re.fullmatch(r"[a-z][a-z0-9-]*", lens.slug):
                raise ValueError(f"collection lens slug must be unique and portable: {lens.slug}")
            slugs.add(lens.slug)
            if not lens.fact_ids:
                raise ValueError(f"collection lens needs observations: {lens.slug}")
            observations: list[CollectionObservationView] = []
            for fact_id in lens.fact_ids:
                if fact_id not in index:
                    raise ValueError(f"collection names unknown fact: {fact_id}")
                ref = index[fact_id]
                if fact_id in seen or ref.room.country != "jp" or ref.fact.source != lens.source:
                    raise ValueError(
                        f"collection fact duplicated or outside source/population lens: {fact_id}"
                    )
                if ref.fact.value.strip().lower().startswith(GAP_PREFIX):
                    raise ValueError(f"collection observation is a documented gap: {fact_id}")
                seen.add(fact_id)
                year = observation_year(ref.fact)
                artifact = lens.artifact
                if lens.slug == "appliances":
                    artifact = "refrigerator" if "refrigerator" in fact_id else "washing-machine"
                elif lens.slug == "communications":
                    artifact = ("computer" if "pc-" in fact_id else
                                "telephone" if "smartphone" in fact_id else "")
                symbol = symbols.symbol(
                    artifact, f"{year // 10 * 10}s", ref.fact.value, ref.fact.label,
                )
                observations.append(CollectionObservationView(
                    ref, year, Markup(symbol.svg if symbol else ""),
                ))
            lenses.append(CollectionLensView(
                lens.slug, lens.title, corpus.sources[lens.source], lens.note,
                tuple(sorted(observations, key=lambda item: item.year)),
            ))
        views.append(CollectionThemeView(theme.slug, theme.title, theme.question, tuple(lenses)))
    return JapanCollectionPage(
        themes=tuple(views),
        rooms=tuple(sorted((r for r in corpus.rooms if r.country == "jp"), key=lambda r: r.decade)),
        editorial=JAPAN_EDITORIAL,
        sources=corpus.sources,
        assumptions=corpus.assumptions,
        overlay_facts=tuple(index[fid] for fid in sorted(seen)),
    )
