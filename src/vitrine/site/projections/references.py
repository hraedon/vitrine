"""Reference-page projections — methodology and bibliography.

Trivial wrappers that freeze the corpus's assumption/source registers into
ordered tuples for the methodology and bibliography templates.
"""

from __future__ import annotations

from vitrine.audit import fingerprint
from vitrine.model import Corpus, Source
from vitrine.site.context import (
    BibliographyPage,
    MethodologyPage,
    SourceCollectionPage,
    SourceFactView,
    SourceRoomView,
)


def project_methodology(corpus: Corpus) -> MethodologyPage:
    """Project the assumption-ledger page."""
    return MethodologyPage(assumptions=tuple(corpus.assumptions.values()))


def project_bibliography(corpus: Corpus) -> BibliographyPage:
    """Project the full source-register page."""
    return BibliographyPage(sources=tuple(corpus.sources.values()))


def project_source(corpus: Corpus, source: Source) -> SourceCollectionPage:
    ledger = {entry.fact_id: entry for entry in corpus.audit_ledger}
    groups = []
    for room in corpus.rooms:
        facts = []
        for fact in room.facts:
            if fact.source != source.id:
                continue
            entry = ledger.get(fact.id)
            current = entry is not None and entry.fingerprint == fingerprint(corpus, fact)
            facts.append(
                SourceFactView(fact=fact, audited=entry.audited if entry and current else "")
            )
        if facts:
            groups.append(SourceRoomView(room, tuple(facts)))
    return SourceCollectionPage(
        source=source,
        rooms=tuple(groups),
        count=sum(len(g.facts) for g in groups),
        audited_count=sum(bool(f.audited) for g in groups for f in g.facts),
    )
