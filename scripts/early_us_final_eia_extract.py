"""Extract pinned EIA household air-conditioning rows for review."""

from __future__ import annotations

import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path

SOURCE_SHA = "5c61b3b9dc35738fc92b0add2bea1797af37abe61f25af4bc7f6ab9585d09e11"
YEARS = [
    "1978",
    "1979",
    "1980",
    "1981",
    "1982",
    "1984",
    "1987",
    "1990",
    "1993",
    "1997",
    "2001",
    "2005",
    "2009",
    "1980 to 2009",
]


class TableParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.rows: list[list[str]] = []
        self.row: list[str] | None = None
        self.cell: list[str] | None = None
        self.text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "tr":
            self.row = []
        if tag in ("td", "th") and self.row is not None:
            self.cell = []

    def handle_data(self, data: str) -> None:
        self.text.append(data)
        if self.cell is not None:
            self.cell.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag in ("td", "th") and self.cell is not None and self.row is not None:
            self.row.append(" ".join("".join(self.cell).split()))
            self.cell = None
        if tag == "tr" and self.row is not None:
            self.rows.append(self.row)
            self.row = None


def extract(source: bytes) -> dict[str, object]:
    if hashlib.sha256(source).hexdigest() != SOURCE_SHA:
        raise ValueError("EIA source hash changed")
    parser = TableParser()
    parser.feed(source.decode("utf-8", errors="replace"))
    text = " ".join(" ".join(parser.text).split())
    for phrase in (
        "Table 2.6 Household End Uses",
        "Percent of Households",
        'counted only under "Central System."',
        "Totals may not equal sum of components due to independent rounding.",
    ):
        if phrase not in text:
            raise ValueError("EIA context changed")
    if YEARS not in parser.rows:
        raise ValueError("EIA year header changed")
    result: dict[str, object] = {
        "source_sha256": SOURCE_SHA,
        "population": "U.S. households",
        "both_systems": "central",
        "unit": "percent",
    }
    for label, key in (
        ("Air Conditioning - Equipment Central System 5", "central"),
        ("Window/Wall Unit 5", "window_wall"),
        ("None", "none"),
    ):
        rows = [row for row in parser.rows if row and row[0] == label]
        if len(rows) != 1:
            raise ValueError("EIA row missing or ambiguous")
        row = rows[0]
        result[key] = {year: int(row[YEARS.index(year) + 1]) for year in ("1978", "1980", "1993")}
    return result


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    folder = root / "samples" / "remaining-audit-20261028"
    output = extract((folder / "final-eia-stb0206.xls").read_bytes())
    (folder / "early_us-final-eia-extract.json").write_text(
        json.dumps(output, indent=2) + "\n", encoding="utf-8", newline="\n"
    )


if __name__ == "__main__":
    main()
