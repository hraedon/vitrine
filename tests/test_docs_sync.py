"""Docs-drift guard: the README status block must equal the computed corpus stats.

The README quotes corpus counts in its Status section; this test fails CI the
moment curation makes them stale. Regenerate the block with
``python scripts/sync_readme_status.py``.
"""

from pathlib import Path

from vitrine.loader import load_corpus
from vitrine.stats import (
    README_BEGIN,
    README_END,
    corpus_stats,
    extract_status_block,
    render_status_line,
)

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_readme_status_block_matches_corpus() -> None:
    corpus = load_corpus(REPO_ROOT / "data")
    readme = (REPO_ROOT / "README.md").read_text()
    block = extract_status_block(readme)
    assert block is not None, (
        f"README.md is missing the status markers {README_BEGIN!r} / {README_END!r}"
    )
    expected = " ".join(render_status_line(corpus_stats(corpus)).split())
    assert block == expected, (
        "README status block drifted from the corpus — regenerate with "
        "`python scripts/sync_readme_status.py`"
    )
