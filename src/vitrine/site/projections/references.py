"""Reference-page projections — methodology and bibliography.

Trivial wrappers that freeze the corpus's assumption/source registers into
ordered tuples for the methodology and bibliography templates.
"""

from __future__ import annotations

from vitrine.model import Corpus
from vitrine.site.context import BibliographyPage, MethodologyPage


def project_methodology(corpus: Corpus) -> MethodologyPage:
    """Project the assumption-ledger page."""
    return MethodologyPage(assumptions=tuple(corpus.assumptions.values()))


def project_bibliography(corpus: Corpus) -> BibliographyPage:
    """Project the full source-register page."""
    return BibliographyPage(sources=tuple(corpus.sources.values()))
