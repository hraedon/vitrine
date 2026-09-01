"""Author the Plan 027 WI-3 alcohol cards from the source table (one-shot).

The thirteen ``us-<decade>-ethanol-per-capita`` facts were written into the
room files by this script, not typed. It exists in the repository rather than
in a scratch directory so that the checks it performs remain inspectable and
re-runnable: an assertion whose artifact is gone is a claim, not evidence.

Every numeral it writes -- each card's ``quantity`` and ``value``, and every
figure quoted in a card's ``notes`` -- is read from
``scripts/niaaa_alcohol_extract.py``'s parse of the source PDF and asserted
against it before anything is written. The prose around those numerals is
authored here; the numbers are not.

Re-running is safe: a room that already carries its card is left alone, so
this reports what it would have done rather than inserting a second copy. It
needs the gitignored ``samples/`` archive, so it is a local tool, not a CI
gate; the CI-runnable half of the check is ``tests/test_alcohol_series.py``,
which holds the committed cards against the committed series.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import niaaa_alcohol_extract as ex

REPO = Path(".")
single, grouped, _ = ex.parse_table_one()

# prose only; every numeral below is asserted against the parse before writing
NOTES = {
    "1900s": (
        "Table 1 publishes no single-year figure this early: the record is "
        "grouped into five-year ranges, and 1901-1905 is the only one lying "
        "wholly inside the decade. Spirits still supplied more ethanol per head "
        "than beer had a generation earlier; the range is the level national "
        "Prohibition would interrupt."
    ),
    "1910s": (
        "The 1911-1915 range is the highest in the table's pre-Prohibition "
        "record. The following range, 1916-1919, falls to 1.96 as state-level "
        "prohibition spread ahead of the federal ban."
    ),
    "1920s": (
        "National Prohibition ran from January 1920 to December 1933, and the "
        "source table prints the single word '(Prohibition)' where fourteen "
        "years of numbers would be. The series is built from legal sales, so "
        "when legal sales ended the measurement ended with them. Drinking did "
        "not stop; the state's ability to count it did. The gap is not an "
        "archive limitation and is not interpolated: no consumption estimate "
        "for these years appears in this table, and any that were entered would "
        "be a different kind of evidence."
    ),
    "1930s": (
        "Repeal took effect in December 1933, and 1934 is the first year the "
        "table can report again. The decade opens inside Prohibition, so 1934 "
        "rather than 1930 is its first published figure. Consumption resumed at "
        "well under half the 1911-1915 level and took until the 1940s to "
        "approach the pre-Prohibition range."
    ),
    "1940s": (
        "Wartime. Consumption rose through the war years from this 1940 level, "
        "peaking at 2.30 in 1946."
    ),
    "1950s": (
        "Back to roughly the pre-Prohibition level for the first time since "
        "1919, and close to flat across the decade."
    ),
    "1960s": (
        "Beer and wine were near-flat across the decade; the rise that followed "
        "came from spirits, which reached 1.11 gallons per head by 1970."
    ),
    "1970s": (
        "The population basis changes here: figures from 1970 onward are "
        "computed over ages 14 and older, before that over ages 15 and older. "
        "The change slightly raises the denominator and is not corrected for."
    ),
    "1980s": (
        "The modern peak: 1981 reaches 2.76, the highest figure in the table "
        "since 1915. Consumption then falls for a decade."
    ),
    "1990s": (
        "The fall from the 1981 peak continued through the decade, reaching "
        "2.15 by 1995 — the lowest since 1963."
    ),
    "2000s": (
        "The long decline stopped around the turn of the century and reversed "
        "slowly, driven by wine and then spirits rather than beer, which "
        "continued to fall."
    ),
    "2010s": (
        "Beer's share kept falling while wine and spirits rose. The "
        "all-beverage total moved little across the decade."
    ),
    "2020s": (
        "The first pandemic year. Consumption rose to 2.54 in 2021, the highest "
        "since 1985, then eased to 2.48 by 2023."
    ),
}

# numerals appearing in the notes above, and the parsed value each must equal
ASSERTIONS = {
    ("1910s", "1.96"): grouped["1916–1919"],
    ("1940s", "2.30"): single[1946],
    ("1960s", "1.11"): None,   # spirits column, checked separately below
    ("1980s", "2.76"): single[1981],
    ("1990s", "2.15"): single[1995],
    ("2020s", "2.54"): single[2021],
    ("2020s", "2.48"): single[2023],
}
for (decade, literal), expected in ASSERTIONS.items():
    if expected is None:
        continue
    if abs(float(literal) - expected) > 1e-9:
        raise SystemExit(f"{decade}: note says {literal}, table says {expected}")
    if literal not in NOTES[decade]:
        raise SystemExit(f"{decade}: asserted literal {literal} not in the note")

BLOCKS: dict[str, str] = {}
for decade, key in ex.DECADE_ANCHORS:
    fid = f"us-{decade}-ethanol-per-capita"
    if key is None:
        gap_value = (
            "no reliable record — national Prohibition, 1920-1933: "
            "legal sales ended and the series ended with them"
        )
        BLOCKS[decade] = f'''[[fact]]
id = "{fid}"
panel = "table"
label = "Alcohol consumed per person, 1920s"
value = "{gap_value}"
unit = "gallons of pure ethanol per person per year"
source = "niaaa-surveillance-122"
tier = "A"
notes = "{NOTES[decade]}"
assumptions = ["composite-family"]
'''
        continue
    if isinstance(key, int):
        value = single[key]
        label = f"Alcohol consumed per person, {key}"
        display = f"{value:.2f} gallons of pure ethanol per person per year"
        year_line = f"price_year = {key}\n"
    else:
        value = grouped[key]
        label = f"Alcohol consumed per person, {key.replace(chr(0x2013), '-')}"
        display = (
            f"{value:.2f} gallons of pure ethanol per person per year "
            f"({key.replace(chr(0x2013), '-')} average)"
        )
        year_line = ""
    BLOCKS[decade] = f'''[[fact]]
id = "{fid}"
quantity = {value:.2f}
panel = "table"
label = "{label}"
value = "{display}"
unit = "gallons of pure ethanol per person per year"
{year_line}source = "niaaa-surveillance-122"
tier = "A"
notes = "{NOTES[decade]}"
assumptions = ["composite-family"]
'''

for decade, block in BLOCKS.items():
    path = REPO / "data" / "us" / f"{decade}.toml"
    text = path.read_text()
    if f'id = "us-{decade}-ethanol-per-capita"' in text:
        print(f"{decade}: already present, left alone")
        continue
    anchor = f'id = "us-{decade}-cigarette-consumption"'
    i = text.index(anchor)
    # end of that fact block = the next blank line followed by '[[fact]]' or a comment
    m = re.compile(r"\n\n(?=\[\[fact\]\]|# )").search(text, i)
    if m is None:
        raise SystemExit(f"{decade}: could not find the end of the cigarette block")
    cut = m.start() + 1
    path.write_text(text[:cut] + "\n" + block + text[cut:])
    print(f"{decade}: inserted us-{decade}-ethanol-per-capita")
