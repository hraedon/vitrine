"""Reproduce the literal 1972-73 four-person food categories, without a budget splice."""

from __future__ import annotations

import hashlib
import io
import re
import tomllib
from decimal import Decimal
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
FILE = "02-cex/cex-1972-73-integrated.pdf"
SHA256 = "448844ea53f0c7700c8fd43ce278c91ccd3fafedafcb36aca6f9129f0e062cc3"
LABELS = {
    "foodtotal": "Food", "foodathometotal": "food at home",
    "foodawayfromhome": "food away from home", "mealsaspay": "meals as pay",
    "beef": "beef", "bakeryproducts": "bakery", "freshmilkandcream": "fresh milk and cream",
    "pork": "pork", "poultry": "poultry", "othermeats": "other meats",
    "fishandseafood": "fish and seafood", "eggs": "eggs", "cerealsandcerealproducts": "cereals",
}


def selected_amount(line: str, start: int) -> str:
    # Only the all-family through four-person columns are needed. A damaged
    # five-person OCR token must neither shift this selection nor be repaired.
    prefix = line[start:].split()[:5]
    if len(prefix) != 5 or any(
        re.fullmatch(r"\$?\d[\d,]*\.\d{2}", token) is None for token in prefix
    ):
        raise ValueError("source selected column or preceding columns are incomplete")
    return prefix[4].replace("$", "").replace(",", "")


def selected_row(line: str) -> tuple[str, str] | None:
    first = re.search(r"[$\d]", line)
    if first is None:
        return None
    label = re.sub(r"[^a-z]", "", line[:first.start()].lower())
    if label not in LABELS:
        return None
    return label, selected_amount(line, first.start())


def extract(blob: bytes) -> dict[str, str]:
    if hashlib.sha256(blob).hexdigest() != SHA256:
        raise ValueError("original 1972-73 CEX source changed")
    from pypdf import PdfReader

    text = PdfReader(io.BytesIO(blob)).pages[43].extract_text() or ""
    if "Table 2." not in text or "4 Persons" not in text:
        raise ValueError("source table or four-person header changed")
    values: dict[str, str] = {}
    for line in text.splitlines():
        observation = selected_row(line)
        if observation is None:
            continue
        label, value = observation
        if label in values:
            raise ValueError("source row is incomplete or ambiguous")
        values[label] = value
    if set(values) != set(LABELS):
        raise ValueError("not every selected food category was found")
    return values


def render(values: dict[str, str]) -> str:
    def amount(key: str) -> str:
        return f"${Decimal(values[key]):,.2f}"

    return (
        f"Food {amount('foodtotal')}/yr; food at home {amount('foodathometotal')}; "
        f"food away from home {amount('foodawayfromhome')}; meals as pay {amount('mealsaspay')}. "
        "Selected food-at-home categories: " + ", ".join(
            f"{LABELS[key]} {amount(key)}" for key in list(LABELS)[4:]
        ) + "."
    )


def qualify(samples: Path, data: Path) -> None:
    values = extract((samples / FILE).read_bytes())
    facts = tomllib.loads((data / "us/1970s.toml").read_text(encoding="utf-8"))["fact"]
    by_id = {fact["id"]: fact for fact in facts}
    if by_id["us-1970s-food-basket"]["value"] != render(values):
        raise ValueError("1972-73 food placard disagrees with original cents-precision means")
    for key in ("us-1970s-expenditure-shares", "us-1970s-cex-apparel-share"):
        if "quantity" in by_id[key] or not by_id[key]["value"].startswith("no reliable record"):
            raise ValueError("unverified denominator silently restored as a budget comparison")


if __name__ == "__main__":
    qualify(REPO / "samples", REPO / "data")
    print("Qualified 1972-73 literal food categories; no harmonized budget denominator asserted")
