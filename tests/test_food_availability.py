"""Plan 027 WI-6a — the availability arc group, which is not a smooth rise.

Four commodities on one shared pounds-per-person axis. The exhibit's honesty
depends on three things this file holds: that the cards and their series agree,
that the group keeps saying availability is not intake, and that the selected
lines retain their documented curation windows.
"""

from __future__ import annotations

import tomllib
from pathlib import Path

import pytest

from vitrine.loader import load_corpus
from vitrine.series import load_series
from vitrine.site import curation

DATA = Path(__file__).parent.parent / "data"
GROUP = "exotic-turned-ordinary"
COMMODITIES = ("broccoli", "bell-peppers", "avocados", "grapes")

# First year selected for each curated line; earlier publisher years may exist.
CURATION_START = {"broccoli": 1960, "bell-peppers": 1960, "avocados": 1970, "grapes": 1970}


def _facts() -> dict[str, dict[str, object]]:
    corpus = load_corpus(DATA)
    out: dict[str, dict[str, object]] = {c: {} for c in COMMODITIES}
    for room in corpus.rooms:
        if room.country != "us":
            continue
        for fact in room.facts:
            for c in COMMODITIES:
                if fact.id == f"us-{room.decade}-availability-{c}":
                    out[c][room.decade] = fact
    return out


def test_the_group_is_placed_and_names_four_commodities() -> None:
    group = curation.ARC_GROUP_BY_SLUG[GROUP]
    assert len(group.members) == len(COMMODITIES)
    slugs = {slug for slug, _label, _colour in group.members}
    assert slugs == {f"availability-{c}" for c in COMMODITIES}
    wing = {w.slug: w for w in curation.CORRIDOR_WINGS}["different-country"]
    assert GROUP in wing.arc_slugs


def test_every_member_colour_role_resolves() -> None:
    """A fourth commodity needed a fourth role; unknown roles crash the render."""
    from vitrine.site import tokens

    known = {"copper", "copper-deep", "brass", "brass-deep"}
    roles = [colour for _s, _l, colour in curation.ARC_GROUP_BY_SLUG[GROUP].members]
    assert set(roles) <= known
    assert len(set(roles)) == len(roles), "two commodities share a colour"
    assert tokens.COPPER_DEEP and tokens.BRASS_DEEP


@pytest.mark.parametrize("commodity", COMMODITIES)
def test_cards_match_their_series(commodity: str) -> None:
    series = load_series(DATA)[f"us-availability-{commodity}"]
    cards = _facts()[commodity]
    assert cards, f"{commodity} has no cards"
    for decade, fact in cards.items():
        year = fact.price_year  # type: ignore[attr-defined]
        assert year is not None, f"{decade}: no year on the card"
        assert year in series.values, f"{decade}: {year} is not in the series"
        assert fact.quantity == pytest.approx(series.values[year])  # type: ignore[attr-defined]


@pytest.mark.parametrize("commodity", COMMODITIES)
def test_cards_fit_the_curated_series_window(commodity: str) -> None:
    """Cards use the selected series window, not a claim about the original sheet."""
    series = load_series(DATA)[f"us-availability-{commodity}"]
    assert min(series.values) == CURATION_START[commodity]
    years = [f.price_year for f in _facts()[commodity].values()]  # type: ignore[attr-defined]
    assert min(years) >= CURATION_START[commodity]


def test_the_group_says_availability_is_not_intake() -> None:
    """The single most important caveat on this exhibit."""
    joined = " ".join(curation.ARC_GROUP_BY_SLUG[GROUP].caveats).lower()
    assert "availability, not intake" in joined
    assert "not what anyone ate" in joined
    assert "farm weight" in joined


def test_the_group_admits_the_shape_is_not_a_smooth_rise() -> None:
    """Checked against the data, not merely asserted in prose."""
    joined = " ".join(curation.ARC_GROUP_BY_SLUG[GROUP].caveats).lower()
    assert "not a smooth rise" in joined
    avocados = load_series(DATA)["us-availability-avocados"].values
    broccoli = load_series(DATA)["us-availability-broccoli"].values
    assert avocados[1986] == 2.4 and avocados[1989] == 1.1, (
        "the caveat's 1980s avocado swing no longer matches the series"
    )
    assert broccoli[max(broccoli)] < broccoli[2000], (
        "broccoli is no longer below its 2000 level — the caveat's example is stale"
    )


def test_the_source_declares_a_content_marker() -> None:
    raw = tomllib.loads((DATA / "sources.toml").read_text(encoding="utf-8"))
    source = next(s for s in raw["source"] if s["id"] == "usda-ers-fads")
    assert "Food Availability (Per Capita) Data System" in source["expect"]


def test_formula_replay_only_ignores_missing_values_inside_sum() -> None:
    """A missing source component cannot silently become zero in arithmetic."""
    from ers_fads_extract import _formula_value
    from openpyxl import Workbook

    workbook = Workbook()
    sheet = workbook.active
    assert sheet is not None
    sheet["C7"] = 4
    sheet["D7"] = "NA"
    sheet["E7"] = "=SUM(C7,D7)"
    assert str(_formula_value(sheet, "E7", 7)) == "4"
    sheet["E7"] = "=C7+D7"
    with pytest.raises(ValueError, match="outside SUM"):
        _formula_value(sheet, "E7", 7)
    sheet["E7"] = "=C8"
    with pytest.raises(ValueError, match="cross-row"):
        _formula_value(sheet, "E7", 7)
    sheet["E7"] = "=SUM(C157:D157)"
    with pytest.raises(ValueError, match="cross-row"):
        _formula_value(sheet, "E7", 7)
    workbook.close()


def test_all_selected_series_reproduce_from_pinned_sources(tmp_path: Path, monkeypatch) -> None:
    """Regenerate every existing curated year without changing the checkout."""
    import shutil

    import ers_fads_extract as extractor

    if not extractor.VEG.exists() or not extractor.FRUIT.exists():
        pytest.skip("Pinned USDA workbooks are required for source replay")
    for slug in extractor.COMMODITIES:
        name = f"us-availability-{slug}.toml"
        shutil.copyfile(DATA / "series" / name, tmp_path / name)
    monkeypatch.setattr(extractor, "OUT_DIR", tmp_path)
    extractor.main()
    for slug in extractor.COMMODITIES:
        name = f"us-availability-{slug}.toml"
        assert (tmp_path / name).read_bytes() == (DATA / "series" / name).read_bytes()
