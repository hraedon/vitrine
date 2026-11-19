from pathlib import Path

import pytest
from ornl_car_price_review import YEARS, extract, parse_page

SOURCE = Path("samples/remaining-audit-20261028/recent_us-originals/TEDB_Ed_39.pdf")


def source_page() -> str:
    if not SOURCE.is_file():
        pytest.skip("ORNL source PDF unavailable")
    pypdf = pytest.importorskip("pypdf")
    return pypdf.PdfReader(SOURCE).pages[287].extract_text()


def test_six_total_current_dollar_values() -> None:
    source_page()
    result = extract(SOURCE)
    assert {int(y): v["total_current_dollars"] for y, v in result["years"].items()} == YEARS


def test_heading_and_fifth_column_must_match() -> None:
    page = source_page()
    with pytest.raises(ValueError, match="headings"):
        parse_page(page.replace(" Domestica  Import  Total", " Import  Domestica  Total"))
    with pytest.raises(ValueError, match="1970"):
        parse_page(page.replace("3,543  23,344", "3,544  23,344"))


def test_changed_pdf_bytes_rejected(tmp_path: Path) -> None:
    if not SOURCE.is_file():
        pytest.skip("ORNL source PDF unavailable")
    path = tmp_path / "changed.pdf"
    path.write_bytes(SOURCE.read_bytes() + b" ")
    with pytest.raises(ValueError, match="bytes changed"):
        extract(path)
