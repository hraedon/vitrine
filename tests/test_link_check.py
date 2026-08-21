"""WI-023: the link checker's content verification, unit-tested without network.

The f08a/f08ar incident: a source URL returned 200 OK while serving the wrong
table variant. `expect` markers on a source make the weekly link check look
inside the served document. These tests exercise the extraction and matching
helpers with in-memory fixtures.
"""

import io
import zipfile
import zlib

from link_check import _pdf_text, missing_markers, searchable_text

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


def _make_pdf(*content_streams: bytes) -> bytes:
    """A minimal in-memory PDF whose FlateDecode streams hold the given
    content-stream text (text operators and all)."""
    parts = [b"%PDF-1.4\n"]
    for content in content_streams:
        compressed = zlib.compress(content)
        parts.append(
            b"<< /Length %d /Filter /FlateDecode >>\nstream\n" % len(compressed)
            + compressed
            + b"\nendstream\n"
        )
    parts.append(b"%%EOF")
    return b"".join(parts)


def test_pdf_markers_found_in_compressed_content_stream() -> None:
    body = _make_pdf(b"BT /F1 12 Tf (Table F-8. Median Income of Families) Tj ET\n")
    text = searchable_text("https://example.org/doc.pdf", body, "application/pdf")
    assert text is not None
    assert missing_markers(text, ["Table F-8", "Median Income of Families"]) == []


def test_pdf_word_split_across_tj_array_is_found() -> None:
    """Kerning splits words into separate strings: [(Medi)(an Inc)-3(ome)] TJ."""
    body = _make_pdf(b"BT [(Medi)(an Inc)-3(ome of Fami)(lies)] TJ ET\n")
    text = searchable_text("https://example.org/doc.pdf", body, "application/pdf")
    assert text is not None
    assert missing_markers(text, ["Median Income of Families"]) == []


def test_pdf_wrong_document_is_caught() -> None:
    body = _make_pdf(b"BT (Table F-8. Size of Family--Asian Alone) Tj ET\n")
    text = searchable_text("https://example.org/doc.pdf", body, "application/pdf")
    assert text is not None
    assert missing_markers(text, ["All Families by Median Income"]) != []


def test_pdf_hex_string_and_escapes_are_decoded() -> None:
    body = _make_pdf(
        b"(All \\(Families\\)) Tj\n<416C6C2046616D696C696573> Tj\n"
        b"(Med\\151an) Tj\n"
    )
    text = _pdf_text(body)
    assert text is not None
    assert missing_markers(text, ["All (Families)", "All Families", "Median"]) == []


def test_pdf_image_only_scan_stays_resolve_only() -> None:
    """Streams open but contain no text operators: this extractor cannot
    verify the document, so it must say so rather than fail on a guess."""
    body = _make_pdf(b"q 1 0 0 1 0 0 cm /Im0 Do Q\n")
    text = searchable_text("https://example.org/scan.pdf", body, "application/pdf")
    assert text is None


def test_pdf_font_binary_stream_does_not_poison_extraction() -> None:
    """Embedded font programs are FlateDecode streams too; their inflated
    binary must not turn a readable document into reported mojibake."""
    font_binary = bytes(range(256)) * 8
    body = _make_pdf(
        b"BT (Readable Table Title) Tj ET\n",
        b"<< /Length1 2048 /FontFile2 >>\nstream\n"
        + zlib.compress(font_binary)
        + b"\nendstream\n",
    )
    text = searchable_text("https://example.org/doc.pdf", body, "application/pdf")
    assert text is not None
    assert missing_markers(text, ["Readable Table Title"]) == []


def test_pdf_nested_paren_strings_are_found() -> None:
    """PDF literal strings may contain balanced nested parens."""
    body = _make_pdf(b"BT (Table \\(F-8\\) Median Income of Families) Tj ET\n")
    text = searchable_text("https://example.org/doc.pdf", body, "application/pdf")
    assert text is not None
    assert missing_markers(text, ["Table (F-8)", "Median Income of Families"]) == []


def test_pdf_binary_soup_does_not_hang_extraction() -> None:
    """Regression: a backtracking regex over font/image binaries (long runs
    of brackets, quotes and nulls — as in a real 1950 Census PDF's embedded
    fonts) had catastrophic runtime. The linear scanner must finish fast,
    and the readable stream must still verify."""
    soup = b"[[[[\x00\x00\"'\x00" * 20000 + b"(stray) 12 Tf "
    body = _make_pdf(
        b"BT (Readable Table Title) Tj ET\n",
        zlib.compress(soup),
    )
    text = searchable_text("https://example.org/doc.pdf", body, "application/pdf")
    assert text is not None
    assert missing_markers(text, ["Readable Table Title"]) == []


def test_pdf_unterminated_string_and_hex_do_not_break_scanning() -> None:
    body = b"%PDF-1.4\n<< /Length 60 >>\nstream\n" + (
        b"BT (never closes... <AB CD [unclosed (Readable After Garbage?) Tj ET"
    ) + b"\nendstream\n%%EOF"
    # The scanner must terminate; whether it finds anything is unimportant.
    from link_check import _pdf_text

    _pdf_text(body)


def test_pdf_encrypted_or_garbage_stays_resolve_only() -> None:
    assert (
        searchable_text(
            "https://example.org/doc.pdf", b"not a pdf", "application/pdf"
        )
        is None
    )
    assert (
        searchable_text(
            "https://example.org/doc.pdf", b"%PDF-1.4\n%%%%EOF", "application/pdf"
        )
        is None
    )


def test_uncompressed_pdf_stream_is_searched_too() -> None:
    body = (
        b"%PDF-1.4\n<< /Length 44 >>\nstream\n"
        b"BT (Uncompressed Table Title Here) Tj ET\nendstream\n%%EOF"
    )
    text = searchable_text("https://example.org/doc.pdf", body, "application/pdf")
    assert text is not None
    assert missing_markers(text, ["Uncompressed Table Title Here"]) == []


def test_content_type_spreadsheet_routes_to_xlsx() -> None:
    body = _make_xlsx(["marker cell"])
    text = searchable_text(
        "https://example.org/download?file=data",
        body,
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    assert text is not None
    assert missing_markers(text, ["marker cell"]) == []
