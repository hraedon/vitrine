#!/usr/bin/env python3
"""Extract the Plan 027 WI-8 child-labor series from the 1943 census monograph.

Emits ``data/series/us-child-labor-share.toml`` from Table XVIII of
*Comparative Occupation Statistics of the United States: 1870 to 1940*
(Sixteenth Census, 1943), archived at
``samples/49-child-labor/census-1940-comparative-occupation-statistics-ch2.pdf``
(chapter II PDF; the table prints on page 97 of the monograph, PDF page 12 of
this file). The archive is the Sixteenth Census monograph itself — the Census
Bureau's own comparability-adjusted reconstruction of the decennial child-work
counts, published with its adjustment footnotes.

**The trap this extractor is built around: the scan's text layer.** The
archived scan carries an OCR text layer, and for this table it is defective in
exactly the way the HFCS 1955 microfilm was: digits drop, double, and split
("667,  118" with a kerning space; "1,115,356" variously rendering the 1880
total; "9.3" as "ll.  3"; a row of the table where "4.0" prints as "4..0").
Whole cells are unrecoverable from the text layer alone. A stdlib
re-extraction therefore cannot *derive* the table — it can only witness the
page. The script does three honest things instead:

1. It asserts clean anchors that DO extract reliably (the table title, the
   1930 total population, the 1870 worker count) so the archived bytes cannot
   silently stop being the document this series was transcribed from.
2. It carries the Total block as eye-transcribed constants (read from 400-800
   dpi renders of the archived page image — not from the text layer, not from
   memory) and closes every row against the table's own arithmetic: the
   printed percent must equal 100 x number / total at the table's one-decimal
   rounding, and male + female counts must sum to the total for every cell of
   the Male and Female blocks (also transcribed, for closure only).
3. It writes the Total block to a deterministic text dump beside the archive
   (``census-1943-ch2-p97.txt``) whose header pins the source PDF's sha256.
   The ``[fact.audit]`` locators on the room facts bind to that dump, so the
   committed quantities replay against a file derived from the archived
   document by the committed script.

**Decade-primary reconciliation** (recorded in docs/verification-log.md,
Plan 027 WI-8): the 1900 row matches the Twelfth Census occupation report
(archived at samples/49-child-labor/census-1900-occupations-twelfth-FULL.pdf,
printed p. cxlvii) cell for cell; the 1910 monograph cells reconcile exactly
against the raw 1910 counts printed in Census Vol IV Table 28/29 (archived
census-1910-vol4/volume-4-p2.pdf, printed p. 70): 1,990,225 raw less the
monograph's footnote-2 deduction of 368,499 = 1,621,726; the same closure
holds by sex. The 1880 comparison in the 1900 report matches the monograph's
1880 row exactly.

**The series ends at 1930 by the source's own account**: the monograph's
chapter III ("The 'Gainful Worker' Concept of 1930 and the 'Labor Force'
Concept of 1940") states the 1930 gainful-worker statistics are not exactly
comparable with the 1940 labor-force statistics. No post-1930 value is
chained on.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ARCHIVE = REPO / "samples" / "49-child-labor"
SOURCE_PDF = ARCHIVE / "census-1940-comparative-occupation-statistics-ch2.pdf"
DUMP = ARCHIVE / "census-1943-ch2-p97.txt"
OUT = REPO / "data" / "series" / "us-child-labor-share.toml"

sys.path.insert(0, str(REPO / "scripts"))
import link_check  # noqa: E402  (stdlib PDF text extraction, see tests/test_produce_sku.py)

# Eye-transcribed from 400-800 dpi renders of the archived page image
# (printed p. 97, TABLE XVIII, block "Total"). Column order:
# year, total number, all-occupations number, printed percent,
# agricultural number, agricultural percent, nonagricultural number,
# nonagricultural percent. Footnote markers follow the year where printed:
# 1890^4 excludes Indian Territory and Indian reservations; 1870^5 carries
# the transfers and Southern-state additions; 1910^2 the overcount
# deduction; 1920^1 the undercount addition; 1900/1880^3 the
# laborer-classification transfers (footnote 3 lists 1900, 1890, 1880).
TOTAL_BLOCK = (
    # year, total,       all N,      all %, agri N,   agri %, nonagri N, nonagri %
    (1930, 14_300_576, 667_118, 4.7, 469_497, 3.3, 197_621, 1.4),
    (1920, 12_502_582, 1_416_684, 11.3, 1_000_000, 8.0, 416_684, 3.3),
    (1910, 10_828_365, 1_621_726, 15.0, 1_059_081, 9.8, 562_645, 5.2),
    (1900, 9_613_252, 1_750_178, 18.2, 1_091_881, 11.4, 658_297, 6.8),
    (1890, 8_322_373, 1_503_771, 18.1, 956_865, 11.5, 546_906, 6.6),
    (1880, 6_649_483, 1_118_356, 16.8, 771_830, 11.6, 346_526, 5.2),
    (1870, 5_781_986, 764_965, 13.2, 535_449, 9.3, 229_516, 4.0),
)

# Male and Female blocks, transcribed for closure only (same column order).
MALE_BLOCK = (
    (1930, 7_223_425, 460_742, 6.4, 343_100, 4.7, 117_642, 1.6),
    (1920, 6_294_985, 1_058_073, 16.8, 800_000, 12.7, 258_073, 4.1),
    (1910, 5_464_228, 1_187_582, 21.7, 851_881, 15.6, 335_701, 6.1),
    (1900, 4_852_427, 1_264_411, 26.1, 880_343, 18.1, 384_068, 7.9),
    (1890, 4_219_145, 1_094_854, 25.9, 776_323, 18.4, 318_531, 7.5),
    (1880, 3_376_114, 825_187, 24.4, 630_267, 18.7, 194_920, 5.8),
    (1870, 2_927_602, 565_419, 19.3, 457_135, 15.6, 108_284, 3.7),
)
FEMALE_BLOCK = (
    (1930, 7_077_151, 206_376, 2.9, 126_397, 1.8, 79_979, 1.1),
    (1920, 6_207_597, 358_611, 5.8, 200_000, 3.2, 158_611, 2.6),
    (1910, 5_364_137, 434_144, 8.1, 207_200, 3.9, 226_944, 4.2),
    (1900, 4_760_825, 485_767, 10.2, 211_538, 4.4, 274_229, 5.8),
    (1890, 4_103_228, 408_917, 10.0, 180_542, 4.4, 228_375, 5.6),
    (1880, 3_273_369, 293_169, 9.0, 141_563, 4.3, 151_606, 4.6),
    (1870, 2_854_384, 199_546, 7.0, 78_314, 2.7, 121_232, 4.2),
)

# Anchors the scan's text layer preserves cleanly (verified against the
# archived bytes). The 1900 population, among others, is OCR-mangled in
# that layer ("ll,613,2li2"), which is why the table is eye-transcribed;
# these four survive and pin the document identity. If the archive is
# ever replaced, these are the first line of defense — the closure checks
# below are the second.
RAW_ANCHORS = (
    "TABLE XVIII",
    "14,300,576",
    "764,965",
    "Nonagricultural",
)


def _check_closures() -> None:
    """Every printed percent must close against its own row's arithmetic."""
    for block, name in ((TOTAL_BLOCK, "total"), (MALE_BLOCK, "male"), (FEMALE_BLOCK, "female")):
        for year, total, all_n, all_pct, agri_n, agri_pct, nonagri_n, nonagri_pct in block:
            for label, number, pct in (
                ("all occupations", all_n, all_pct),
                ("agricultural", agri_n, agri_pct),
                ("nonagricultural", nonagri_n, nonagri_pct),
            ):
                computed = round(100 * number / total, 1)
                assert computed == pct, (
                    f"{name} {year} {label}: 100*{number}/{total} = {computed} "
                    f"but the table prints {pct}"
                )
            assert agri_n + nonagri_n == all_n, f"{name} {year}: pursuits do not sum"
    for total_row, male_row, female_row in zip(TOTAL_BLOCK, MALE_BLOCK, FEMALE_BLOCK, strict=True):
        assert total_row[0] == male_row[0] == female_row[0]
        for col in (1, 2, 4, 6):
            assert male_row[col] + female_row[col] == total_row[col], (
                f"{total_row[0]}: male+female != total in column {col}"
            )


def _assert_anchors(text: str) -> None:
    flat = text.replace("\n", " ")
    for anchor in RAW_ANCHORS:
        assert anchor in flat, f"archived scan text layer lost anchor {anchor!r}"


def _write_dump(pdf_sha256: str) -> None:
    lines = [
        "# Total block of TABLE XVIII, transcribed from the archived monograph",
        "# by scripts/census_child_labor_extract.py (see that script's docstring",
        "# for why the scan's text layer cannot be parsed directly). The room",
        "# facts' [fact.audit] locators bind to this file.",
        f"# source pdf: {SOURCE_PDF.name}",
        f"# source pdf sha256: {pdf_sha256}",
        "# page: printed 97 (chapter XI), block Total",
        "# table: Number and Proportion of Children 10 to 15 Years Old Engaged in All",
        "#        Occupations, in Agricultural Pursuits, and in Nonagricultural Pursuits,",
        "#        by Sex, for the United States: 1870 to 1930",
        "# year total_number all_number all_percent agri_number agri_percent"
        " nonagri_number nonagri_percent",
    ]
    for year, total, all_n, all_pct, agri_n, agri_pct, nonagri_n, nonagri_pct in TOTAL_BLOCK:
        lines.append(
            f"{year} {total} {all_n} {all_pct} {agri_n} {agri_pct} {nonagri_n} {nonagri_pct}"
        )
    DUMP.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_series() -> None:
    population = (
        "Children 10 to 15 years old enumerated by the decennial census of "
        "the United States (continental United States; 1890 excludes Indian "
        "Territory and Indian reservations) — the denominator is every child "
        "in the age band, not only those available for nonagricultural work"
    )
    notes = (
        "The Census Bureau's own comparability-adjusted reconstruction "
        "(Table XVIII, printed p. 97): the 1910 count deducts an overcount "
        "the decade primary itself flagged, the 1920 count adds an undercount "
        "and carries an estimated agricultural component, and 1900/1890/1880 "
        "carry classification transfers between agricultural and "
        "nonagricultural pursuits that leave the all-occupations totals "
        "untouched. Sparse by construction: a decennial census series, not "
        "annual. It ends at 1930 because the 1940 census replaced the "
        "gainful-worker concept with the labor-force concept, which the "
        "monograph's own chapter III declares not exactly comparable; no "
        "post-1930 value is chained on."
    )
    header = """\
# Auto-generated by scripts/census_child_labor_extract.py from Table XVIII
# of Comparative Occupation Statistics of the United States: 1870 to 1940
# (Sixteenth Census, 1943), archived at samples/49-child-labor/ — see the
# source registry entry and the verification log, Plan 027 WI-8, before
# editing by hand.

[[series]]
id = "us-child-labor-share"
label = "Children 10-15 gainfully occupied, census years 1870-1930"
source = "census-1943-comparative-occupations"
tier = "A"
unit = "percent of children 10-15 years old gainfully occupied"
"""
    values = "\n".join(f"{row[0]} = {row[3]}" for row in TOTAL_BLOCK)
    OUT.write_text(
        header + f'population = "{population}"\n' + f'notes = "{notes}"\n\n'
        "[series.values]\n" + values + "\n",
        encoding="utf-8",
    )


def main() -> int:
    _check_closures()
    pdf_bytes = SOURCE_PDF.read_bytes()
    pdf_sha256 = hashlib.sha256(pdf_bytes).hexdigest()
    text = link_check._pdf_text(pdf_bytes)
    assert text is not None, "archived monograph has no extractable text layer"
    _assert_anchors(text)
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    _write_dump(pdf_sha256)
    _write_series()
    print(f"series written -> {OUT.relative_to(REPO)}")
    print(f"audit dump written -> {DUMP.relative_to(REPO)} (pdf sha256 {pdf_sha256[:12]}...)")
    for row in TOTAL_BLOCK:
        print(f"  {row[0]}: {row[3]}% of {row[1]:,} = {row[2]:,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
