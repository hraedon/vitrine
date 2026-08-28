"""Projection for the downloadable corpus landing page."""

from __future__ import annotations

from vitrine.export import quantified_fact_count
from vitrine.model import Corpus
from vitrine.site.context import DataPage


def project_data(corpus: Corpus) -> DataPage:
    """Project corpus counts used by ``data.html``."""
    return DataPage(
        rooms=len(corpus.rooms),
        facts=sum(len(room.facts) for room in corpus.rooms),
        derived=sum(len(room.derived) for room in corpus.rooms),
        sources=len(corpus.sources),
        assumptions=len(corpus.assumptions),
        quantified_facts=quantified_fact_count(corpus),
    )


__all__ = ["project_data"]
