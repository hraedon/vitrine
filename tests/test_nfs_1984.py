"""The selected food observations retain the original annual column and units."""

import json
from pathlib import Path

import pytest
from nfs_1984_extract import FILE, decimal_token, extract

from vitrine.loader import load_corpus


def test_selected_food_records_preserve_acquisition_scope() -> None:
    corpus = load_corpus(Path(__file__).parent.parent / "data")
    room = next(room for room in corpus.rooms if room.slug == "uk-1980s")
    facts = {fact.id: fact for fact in room.facts}
    milk = facts["uk-1980s-full-price-whole-milk"]
    eggs = facts["uk-1980s-eggs-at-home"]
    assert milk.quantity == 3.53 and "pints" in milk.unit
    assert eggs.quantity == 3.21 and "eggs" in eggs.unit
    assert "not amounts actually eaten" in milk.notes
    assert "Private households in mainland Great Britain" in corpus.sources[milk.source].population
    assert facts["uk-1980s-food-basket-gap"].value.startswith("no reliable record")


def test_original_nfs_pdf_reproduces_selected_cells() -> None:
    samples = Path(__file__).parent.parent / "samples"
    source = samples / FILE
    artifact = samples / "59-workbook-review/nfs-1984-observations.json"
    if not source.is_file() or not artifact.is_file():
        pytest.skip("gitignored original NFS PDF and extraction artifact required")
    pytest.importorskip("pypdf", reason="curator-only PDF reader required")
    assert extract(source.read_bytes()) == json.loads(artifact.read_text(encoding="utf-8"))


def test_nfs_source_pin_rejects_replacement_before_extraction() -> None:
    with pytest.raises(ValueError, match="original NFS report bytes"):
        extract(b"different source")


@pytest.mark.parametrize("value", ["3-<7", "3 25", "3.53", "missing"])
def test_damaged_source_cell_is_not_silently_repaired(value: str) -> None:
    with pytest.raises(ValueError, match="unambiguous"):
        decimal_token(value)
