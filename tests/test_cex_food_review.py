"""Compound CEX records never turn missing cells into published observations."""

import json
from pathlib import Path

import pytest
from cex_food_review import PINS, extract, pdf_row, render, render_budget

from vitrine.loader import load_corpus


def test_absent_four_person_cell_stays_absent() -> None:
    value, _ = pdf_row("Food away from home 1,441 1,006", "Food away from home", 4)
    assert value is None


def test_ambiguous_same_named_row_is_not_silently_selected() -> None:
    with pytest.raises(ValueError, match="ambiguous"):
        pdf_row("Food 1 2 3 4 5 6 7\nFood 7 6 5 4 3 2 1", "Food", 4)


def test_new_compound_food_records_retain_scope_and_blank() -> None:
    corpus = load_corpus(Path(__file__).parent.parent / "data")
    facts = {fact.id: fact for room in corpus.rooms for fact in room.facts}
    fact = facts["us-1980s-food-basket"]
    assert "no value printed" in fact.value and "$1,806" not in fact.value
    assert "consumer unit" in fact.unit and "per family" not in fact.unit
    assert "cex-ratios-of-means" in fact.assumptions


def test_original_cex_tables_reproduce_every_displayed_food_and_budget_field() -> None:
    root = Path(__file__).parent.parent
    samples = root / "samples"
    artifact = samples / "59-workbook-review/cex-food-observations.json"
    if not artifact.is_file() or not (samples / "02-cex/cusize-1985.pdf").is_file():
        pytest.skip("gitignored original CEX tables and extraction artifact required")
    pytest.importorskip("pypdf", reason="curator-only PDF reader required")
    pytest.importorskip("openpyxl", reason="optional XLSX reader required")
    results = extract(samples)
    assert results == json.loads(artifact.read_text(encoding="utf-8"))
    assert len(results) == len(PINS)
    for year in PINS:
        decade = f"{year // 10 * 10}s"
        data = json.loads(json.dumps(results[str(year)]))
        corpus = load_corpus(root / "data")
        room = next(room for room in corpus.rooms if room.slug == f"us-{decade}")
        facts = {fact.id: fact for fact in room.facts}
        assert facts[f"us-{decade}-food-basket"].value == render(data, year)
        assert facts[f"us-{decade}-expenditure-shares"].value == render_budget(data, year)
