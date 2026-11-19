"""Curator extraction keeps original workbook cells and rejects formula caches."""

import hashlib
import json
import struct
from pathlib import Path

import pytest
from workbook_review_extract import PINS, LiteralBook, extract, formula_cells


def test_biff_formula_coordinates_are_not_accepted_as_literal_cells() -> None:
    stream = struct.pack("<HHHH", 0x0006, 4, 51, 12)
    book = LiteralBook.__new__(LiteralBook)
    book.formulas = formula_cells(stream)
    # Refusal happens before any cached numeric value could be read.
    with pytest.raises(ValueError, match="formula coordinate"):
        book.cell("Sheet", 52, 13)


@pytest.mark.parametrize("stream", [b"\x01", struct.pack("<HH", 6, 20)])
def test_truncated_formula_stream_is_an_error(stream: bytes) -> None:
    with pytest.raises(ValueError, match="truncated"):
        formula_cells(stream)


def test_original_workbooks_reproduce_extraction_artifact() -> None:
    samples = Path(__file__).parent.parent / "samples"
    artifact = samples / "59-workbook-review" / "observations.json"
    if not artifact.is_file() or not all((samples / name).is_file() for name in PINS):
        pytest.skip("gitignored original workbooks and extraction artifact required")
    pytest.importorskip("xlrd", reason="curator-only XLS reader required")
    pytest.importorskip("openpyxl", reason="existing ASHE helper requires openpyxl")
    assert extract(samples) == json.loads(artifact.read_text(encoding="utf-8"))


def test_changed_workbook_cannot_reuse_inspected_vintage(tmp_path: Path) -> None:
    pytest.importorskip("xlrd", reason="curator-only XLS reader required")
    pytest.importorskip("openpyxl", reason="existing ASHE helper requires openpyxl")
    first = next(iter(PINS))
    path = tmp_path / first
    path.parent.mkdir(parents=True)
    path.write_bytes(b"different source bytes")
    with pytest.raises(ValueError, match="original source bytes changed"):
        extract(tmp_path)


def test_real_fies_cached_formula_is_refused() -> None:
    samples = Path(__file__).parent.parent / "samples"
    name = "36-jp-income/fies-a18-2.xls"
    path = samples / name
    if not path.is_file():
        pytest.skip("gitignored original FIES workbook required")
    pytest.importorskip("xlrd", reason="curator-only XLS reader required")
    blob = path.read_bytes()
    assert hashlib.sha256(blob).hexdigest() == PINS[name]
    book = LiteralBook(blob)
    # An actual cached formula in the original workbook, not a synthetic value.
    with pytest.raises(ValueError, match="formula coordinate"):
        book.cell(book.book.sheet_names()[0], 52, 13)
