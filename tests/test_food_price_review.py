"""Compound food prices bind year, item, unit and explicit decimal rounding."""

import copy
from pathlib import Path

import pytest
from food_price_review import SERIES, qualify, render

from vitrine.loader import load_corpus


def specimen() -> tuple[dict[str, object], dict[str, str]]:
    document = {"status": "REQUEST_SUCCEEDED", "Results": {"series": [
        {"seriesID": identifier, "data": [
            {"year": "2024", "period": "M12", "periodName": "December", "value": "1.005"},
        ]} for identifier, _, _, _ in SERIES
    ]}}
    metadata = {
        identifier: f"Average Price: {description} "
        f"({'Cost per Dozen' if unit == 'doz' else 'Cost per Pound/453.6 Grams'}) "
        f"in U.S. City Average ({identifier})"
        for identifier, _, unit, description in SERIES
    }
    return document, metadata


def test_rounding_is_explicit_half_up_and_item_identity_is_specific() -> None:
    document, metadata = specimen()
    value = render(document, 2024, metadata)
    assert "ground chuck $1.01/lb" in value
    assert "eggs $1.01/doz" in value


@pytest.mark.parametrize("field,value", [("year", "2023"), ("periodName", "November")])
def test_wrong_december_context_is_rejected(field: str, value: str) -> None:
    document, metadata = specimen()
    document["Results"]["series"][0]["data"][0][field] = value
    with pytest.raises(ValueError, match="year or period"):
        render(document, 2024, metadata)


def test_duplicate_source_series_is_rejected() -> None:
    document, metadata = specimen()
    document["Results"]["series"].append(copy.deepcopy(document["Results"]["series"][0]))
    with pytest.raises(ValueError, match="duplicate"):
        render(document, 2024, metadata)


def test_different_beef_product_cannot_reuse_the_series_identity() -> None:
    document, metadata = specimen()
    metadata["APU0000703111"] = metadata["APU0000703111"].replace("Ground Chuck", "Round Steak")
    with pytest.raises(ValueError, match="identity or unit"):
        render(document, 2024, metadata)


def test_archived_api_and_metadata_reproduce_all_compound_placards() -> None:
    root = Path(__file__).parent.parent
    archive = root / "samples/59-workbook-review"
    if not (archive / "bls-average-prices-1980-response.json").is_file():
        pytest.skip("gitignored original public BLS responses and metadata required")
    qualify(archive, root / "data")


def test_historical_food_prices_keep_original_package_units() -> None:
    corpus = load_corpus(Path(__file__).parent.parent / "data")
    facts = {fact.id: fact for room in corpus.rooms for fact in room.facts}
    old = facts["us-1950s-food-prices"]
    later = facts["us-1970s-food-prices"]
    assert "sugar 48.7¢/5lb" in old.value and "potatoes 69.2¢/15lb" in old.value
    assert "fifteen-pound" in old.unit and "five-pound" in old.unit
    assert "milk 65.5¢/half-gallon" in later.value
    assert "half-gallon" in later.unit and "quart" not in later.unit
