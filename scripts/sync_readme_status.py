#!/usr/bin/env python3
"""Regenerate the README corpus-status block from the data.

The block between <!-- corpus-status:begin --> and <!-- corpus-status:end -->
is machine-checked by tests/test_docs_sync.py; run this after curating so the
README's Status section keeps quoting the corpus, not a memory of it.

Usage: python3 scripts/sync_readme_status.py
"""

from pathlib import Path

from vitrine.loader import load_corpus
from vitrine.stats import README_BEGIN, README_END, corpus_stats, render_status_line

REPO_ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    readme_path = REPO_ROOT / "README.md"
    text = readme_path.read_text()
    begin = text.find(README_BEGIN)
    end = text.find(README_END)
    if begin == -1 or end == -1 or end < begin:
        raise SystemExit(
            f"README.md is missing the status markers {README_BEGIN!r} / {README_END!r}"
        )
    line = render_status_line(corpus_stats(load_corpus(REPO_ROOT / "data")))
    updated = text[: begin + len(README_BEGIN)] + line + text[end:]
    if updated == text:
        print("README status block already current")
        return 0
    readme_path.write_text(updated)
    print(f"README status block updated: {line}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
