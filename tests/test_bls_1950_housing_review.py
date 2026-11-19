import hashlib
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts import bls_1950_housing_review as review


def test_review_guards_source_and_page(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    pdf = tmp_path / "original.pdf"
    pdf.write_bytes(b"known source")
    monkeypatch.setattr(review, "SOURCE_SHA256", hashlib.sha256(pdf.read_bytes()).hexdigest())
    page = SimpleNamespace(extract_text=lambda: " ".join(review.SENTINELS))
    monkeypatch.setitem(
        sys.modules,
        "pypdf",
        SimpleNamespace(PdfReader=lambda _: SimpleNamespace(pages=[None] * 59 + [page])),
    )
    result = review.review(pdf)
    assert result["housing_percent"] == 10.6
    assert result["housing_dollars"] == 415
    assert result["consumption_dollars"] == 3925
    assert result["sample_families"] == 7007
    monkeypatch.setitem(
        sys.modules,
        "pypdf",
        SimpleNamespace(
            PdfReader=lambda _: SimpleNamespace(
                pages=[None] * 59 + [SimpleNamespace(extract_text=lambda: "changed page")]
            )
        ),
    )
    with pytest.raises(ValueError, match="page OCR"):
        review.review(pdf)
    pdf.write_bytes(b"changed source")
    with pytest.raises(ValueError, match="hash changed"):
        review.review(pdf)
