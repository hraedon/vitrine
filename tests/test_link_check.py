"""WI-023: the link checker's content verification, unit-tested without network.

The f08a/f08ar incident: a source URL returned 200 OK while serving the wrong
table variant. `expect` markers on a source make the weekly link check look
inside the served document. These tests exercise the extraction and matching
helpers with in-memory fixtures.
"""

import io
import zipfile

from link_check import missing_markers, searchable_text

F08AR_URL = "https://www2.census.gov/programs-surveys/cps/tables/time-series/historical-income-families/f08ar.xlsx"


def _make_xlsx(shared_strings: list[str], sheet_names: list[str] | None = None) -> bytes:
    """A minimal in-memory .xlsx carrying the given shared strings."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        strings = "".join(
            f'<si><t xml:space="preserve">{s}</t></si>' for s in shared_strings
        )
        zf.writestr(
            "xl/sharedStrings.xml",
            f'<sst xmlns="http://x">{strings}</sst>',
        )
        if sheet_names is not None:
            sheets = "".join(f'<sheet name="{n}"/>' for n in sheet_names)
            zf.writestr("xl/workbook.xml", f"<workbook>{sheets}</workbook>")
    return buf.getvalue()


def test_xlsx_markers_found_in_shared_strings() -> None:
    body = _make_xlsx(["Table F-8. Size of Family--All Families by Median and Mean Income"])
    text = searchable_text(F08AR_URL, body, "application/octet-stream")
    assert text is not None
    assert missing_markers(text, ["Table F-8", "Size of Family--All Families"]) == []


def test_xlsx_wrong_variant_is_caught() -> None:
    """The incident itself: the Asian-families table lacks the All-Families title."""
    body = _make_xlsx(["Table F-8. Size of Family--Asian Alone by Median and Mean Income"])
    text = searchable_text(F08AR_URL, body, "application/octet-stream")
    assert text is not None
    assert missing_markers(text, ["Size of Family--All Families"]) == [
        "Size of Family--All Families"
    ]


def test_xlsx_falls_back_to_workbook_when_no_shared_strings() -> None:
    body = _make_xlsx([], sheet_names=["All Races"])
    text = searchable_text(F08AR_URL, body, "application/octet-stream")
    assert text is not None
    assert missing_markers(text, ["All Races"]) == []


def test_xlsx_garbage_body_is_unsupported_not_crash() -> None:
    assert searchable_text(F08AR_URL, b"not a zip", "application/octet-stream") is None


def test_html_body_searched_case_and_whitespace_insensitively() -> None:
    body = b"<html><title>Historical  Income\nTables: Families</title></html>"
    text = searchable_text("https://www2.census.gov/x/", body, "text/html")
    assert text is not None
    assert missing_markers(text, ["historical income tables: families"]) == []


def test_pdf_is_resolve_only() -> None:
    text = searchable_text("https://example.org/doc.pdf", b"%PDF-1.4 ...", "application/pdf")
    assert text is None


def test_content_type_spreadsheet_routes_to_xlsx() -> None:
    body = _make_xlsx(["marker cell"])
    text = searchable_text(
        "https://example.org/download?file=data",
        body,
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    assert text is not None
    assert missing_markers(text, ["marker cell"]) == []
