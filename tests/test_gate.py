"""The provenance gate: green on the committed corpus, red on broken data."""

from pathlib import Path

import pytest

from vitrine.check import check_corpus, check_render_coverage
from vitrine.loader import LoadError, load_corpus

DATA = Path(__file__).parent.parent / "data"


def test_committed_corpus_is_green() -> None:
    corpus = load_corpus(DATA)
    assert check_corpus(corpus) == []
    assert corpus.rooms, "corpus must contain at least one room"


def _write_minimal(tmp_path: Path, fact_source: str = "src-1") -> Path:
    (tmp_path / "sources.toml").write_text(
        '[[source]]\nid = "src-1"\ntitle = "T"\npublisher = "P"\nyear = 1950\n'
        'url = "https://example.org"\npopulation = "all families"\n'
    )
    (tmp_path / "assumptions.toml").write_text(
        '[[assumption]]\nid = "composite-family"\ntitle = "A"\nstatement = "S"\n'
    )
    room_dir = tmp_path / "us"
    room_dir.mkdir()
    (room_dir / "1950s.toml").write_text(
        '[room]\ncountry = "us"\ndecade = "1950s"\n\n'
        '[[fact]]\nid = "us-1950s-x"\npanel = "budget"\nlabel = "L"\nvalue = "V"\n'
        f'unit = "U"\nsource = "{fact_source}"\ntier = "A"\n'
    )
    return tmp_path


def test_dangling_source_fails_gate(tmp_path: Path) -> None:
    data = _write_minimal(tmp_path, fact_source="no-such-source")
    problems = check_corpus(load_corpus(data))
    assert any("unknown source" in p for p in problems)


def test_valid_minimal_corpus_passes(tmp_path: Path) -> None:
    data = _write_minimal(tmp_path)
    assert check_corpus(load_corpus(data)) == []


def test_bad_tier_rejected_at_parse(tmp_path: Path) -> None:
    data = _write_minimal(tmp_path)
    room = data / "us" / "1950s.toml"
    room.write_text(room.read_text().replace('tier = "A"', 'tier = "Z"'))
    with pytest.raises(LoadError, match="tier 'Z'"):
        load_corpus(data)


def test_bool_year_rejected_at_parse(tmp_path: Path) -> None:
    """``bool`` is a subclass of ``int`` in Python, so a TOML ``year = true``
    would silently become ``year = 1`` without an explicit guard. The loader
    rejects bools on integer fields (year, price_year, amount_minor, precision)."""
    data = _write_minimal(tmp_path)
    sources = data / "sources.toml"
    sources.write_text(sources.read_text().replace("year = 1950", "year = true"))
    with pytest.raises(LoadError, match="not an integer"):
        load_corpus(data)


def test_wrong_id_prefix_fails_gate(tmp_path: Path) -> None:
    data = _write_minimal(tmp_path)
    room = data / "us" / "1950s.toml"
    room.write_text(room.read_text().replace('id = "us-1950s-x"', 'id = "uk-1950s-x"'))
    problems = check_corpus(load_corpus(data))
    assert any("must start with" in p for p in problems)


# ── Render-coverage gate (Plan 001 WI-4) ────────────────────────────────────


def test_render_coverage_passes_when_manifest_matches(tmp_path: Path) -> None:
    data = _write_minimal(tmp_path)
    corpus = load_corpus(data)
    build_dir = tmp_path / "_site"
    build_dir.mkdir()
    (build_dir / "facts-manifest.txt").write_text("us-1950s-x\n")
    assert check_render_coverage(corpus, build_dir) == []


def test_render_coverage_fails_when_fact_missing_from_manifest(tmp_path: Path) -> None:
    data = _write_minimal(tmp_path)
    corpus = load_corpus(data)
    build_dir = tmp_path / "_site"
    build_dir.mkdir()
    (build_dir / "facts-manifest.txt").write_text("")
    problems = check_render_coverage(corpus, build_dir)
    assert any("curated but not rendered" in p for p in problems)


def test_render_coverage_fails_when_manifest_has_extra_fact(tmp_path: Path) -> None:
    data = _write_minimal(tmp_path)
    corpus = load_corpus(data)
    build_dir = tmp_path / "_site"
    build_dir.mkdir()
    (build_dir / "facts-manifest.txt").write_text("us-1950s-x\nus-1950s-ghost\n")
    problems = check_render_coverage(corpus, build_dir)
    assert any("rendered but not curated" in p for p in problems)


def test_render_coverage_fails_when_manifest_missing(tmp_path: Path) -> None:
    data = _write_minimal(tmp_path)
    corpus = load_corpus(data)
    build_dir = tmp_path / "_site"
    build_dir.mkdir()
    problems = check_render_coverage(corpus, build_dir)
    assert any("not found" in p for p in problems)


def test_render_coverage_on_committed_corpus(tmp_path: Path) -> None:
    """Build the real corpus and verify coverage end-to-end."""
    from vitrine.series import load_series
    from vitrine.site.render import render_site

    corpus = load_corpus(DATA)
    render_site(corpus, tmp_path, load_series(DATA), DATA)
    assert check_render_coverage(corpus, tmp_path) == []


# ── Structured amount + anchor invariants (Plan 003 WI-2) ────────────────────


def _write_structured_room(
    tmp_path: Path,
    room_toml: str,
) -> Path:
    (tmp_path / "sources.toml").write_text(
        '[[source]]\nid = "src-1"\ntitle = "T"\npublisher = "P"\nyear = 1950\n'
        'url = "https://example.org"\npopulation = "all families"\n'
        '[[source]]\nid = "src-wage"\ntitle = "W"\npublisher = "P"\nyear = 1950\n'
        'url = "https://example.org"\npopulation = "workers"\nmeasure = "hourly_earnings"\n'
        '[[source]]\nid = "src-income"\ntitle = "I"\npublisher = "P"\nyear = 1950\n'
        'url = "https://example.org"\npopulation = "families"\nmeasure = "money_income"\n'
    )
    (tmp_path / "assumptions.toml").write_text(
        '[[assumption]]\nid = "composite-family"\ntitle = "A"\nstatement = "S"\n'
    )
    room_dir = tmp_path / "us"
    room_dir.mkdir()
    (room_dir / "1950s.toml").write_text(room_toml)
    return tmp_path


_TOTAL_FACT_NO_ANCHOR = """\
[room]
country = "us"
decade = "1950s"

[[fact]]
id = "us-1950s-car"
panel = "table"
label = "Car price"
value = "$1,511"
unit = "USD"
source = "src-1"
tier = "D"
amount_minor = 151100
currency = "USD"
price_year = 1950
basis = "total"
"""


def test_priced_fact_without_anchor_fails_gate(tmp_path: Path) -> None:
    data = _write_structured_room(tmp_path, _TOTAL_FACT_NO_ANCHOR)
    problems = check_corpus(load_corpus(data))
    assert any("no wage_anchor or income_anchor" in p for p in problems)


_MIS_TYPED_ANCHOR = """\
[room]
country = "us"
decade = "1950s"
wage_anchor = "us-1950s-car"

[[fact]]
id = "us-1950s-car"
panel = "table"
label = "Car price"
value = "$1,511"
unit = "USD"
source = "src-1"
tier = "D"
amount_minor = 151100
currency = "USD"
price_year = 1950
basis = "total"
"""


def test_mis_typed_anchor_fails_gate(tmp_path: Path) -> None:
    data = _write_structured_room(tmp_path, _MIS_TYPED_ANCHOR)
    problems = check_corpus(load_corpus(data))
    assert any("wage_anchor" in p and "expected 'hourly'" in p for p in problems)


_ANCHOR_NONEXISTENT = """\
[room]
country = "us"
decade = "1950s"
wage_anchor = "us-1950s-no-such-fact"

[[fact]]
id = "us-1950s-car"
panel = "table"
label = "Car price"
value = "$1,511"
unit = "USD"
source = "src-1"
tier = "D"
amount_minor = 151100
currency = "USD"
price_year = 1950
basis = "total"
"""


def test_nonexistent_anchor_fails_gate(tmp_path: Path) -> None:
    data = _write_structured_room(tmp_path, _ANCHOR_NONEXISTENT)
    problems = check_corpus(load_corpus(data))
    assert any("does not resolve" in p for p in problems)


_VALID_PRICED_ROOM = """\
[room]
country = "us"
decade = "1950s"
wage_anchor = "us-1950s-wage"
income_anchor = "us-1950s-income"

[[fact]]
id = "us-1950s-car"
panel = "table"
label = "Car price"
value = "$1,511"
unit = "USD"
source = "src-1"
tier = "D"
amount_minor = 151100
currency = "USD"
price_year = 1950
basis = "total"

[[fact]]
id = "us-1950s-wage"
panel = "day"
label = "Hourly wage"
value = "$1.32"
unit = "USD/hr"
source = "src-wage"
tier = "A"
amount_minor = 132
currency = "USD"
price_year = 1950
basis = "hourly"

[[fact]]
id = "us-1950s-income"
panel = "budget"
label = "Median income"
value = "$3,319"
unit = "USD/yr"
source = "src-income"
tier = "A"
amount_minor = 331900
currency = "USD"
price_year = 1950
basis = "annual"
"""


def test_valid_priced_room_passes_gate(tmp_path: Path) -> None:
    data = _write_structured_room(tmp_path, _VALID_PRICED_ROOM)
    assert check_corpus(load_corpus(data)) == []


def test_anchor_source_without_measure_fails_gate(tmp_path: Path) -> None:
    """An anchor whose source declares no measure is rejected: you cannot
    divide by a denominator without saying what it measures."""
    room = _VALID_PRICED_ROOM.replace(
        'id = "us-1950s-income"\npanel = "budget"\nlabel = "Median income"\n'
        'value = "$3,319"\nunit = "USD/yr"\nsource = "src-income"',
        'id = "us-1950s-income"\npanel = "budget"\nlabel = "Median income"\n'
        'value = "$3,319"\nunit = "USD/yr"\nsource = "src-1"',
    )
    data = _write_structured_room(tmp_path, room)
    problems = check_corpus(load_corpus(data))
    assert any("declares no measure" in p and "income_anchor" in p for p in problems)


def test_anchor_measure_wrong_axis_fails_gate(tmp_path: Path) -> None:
    """A wage anchor whose source measures an income concept is rejected —
    same-basis is necessary but the measure must sit on the right axis."""
    room = _VALID_PRICED_ROOM.replace(
        'id = "us-1950s-wage"\npanel = "day"\nlabel = "Hourly wage"\n'
        'value = "$1.32"\nunit = "USD/hr"\nsource = "src-wage"',
        'id = "us-1950s-wage"\npanel = "day"\nlabel = "Hourly wage"\n'
        'value = "$1.32"\nunit = "USD/hr"\nsource = "src-income"',
    )
    data = _write_structured_room(tmp_path, room)
    problems = check_corpus(load_corpus(data))
    assert any("belongs to the" in p and "axis" in p for p in problems)


_INCONSISTENT_CURRENCY = """\
[room]
country = "us"
decade = "1950s"
wage_anchor = "us-1950s-wage"

[[fact]]
id = "us-1950s-car"
panel = "table"
label = "Car price"
value = "£1,200"
unit = "GBP"
source = "src-1"
tier = "D"
amount_minor = 120000
currency = "GBP"
price_year = 1950
basis = "total"

[[fact]]
id = "us-1950s-wage"
panel = "day"
label = "Hourly wage"
value = "$1.32"
unit = "USD/hr"
source = "src-1"
tier = "A"
amount_minor = 132
currency = "USD"
price_year = 1950
basis = "hourly"
"""


def test_inconsistent_currency_fails_gate(tmp_path: Path) -> None:
    data = _write_structured_room(tmp_path, _INCONSISTENT_CURRENCY)
    problems = check_corpus(load_corpus(data))
    assert any("inconsistent currencies" in p for p in problems)


_MISSING_REQUIRED_FIELDS = """\
[room]
country = "us"
decade = "1950s"

[[fact]]
id = "us-1950s-car"
panel = "table"
label = "Car price"
value = "$1,511"
unit = "USD"
source = "src-1"
tier = "D"
amount_minor = 151100
"""


def test_amount_minor_without_currency_year_basis_fails(tmp_path: Path) -> None:
    data = _write_structured_room(tmp_path, _MISSING_REQUIRED_FIELDS)
    problems = check_corpus(load_corpus(data))
    assert any("currency is empty" in p for p in problems)
    assert any("price_year is missing" in p for p in problems)
    assert any("basis is missing" in p for p in problems)


# ── Structured quantity (Plan 007) ───────────────────────────────────────────


def _write_quantity_room(tmp_path: Path, fact_lines: str) -> Path:
    data = _write_minimal(tmp_path)
    room = data / "us" / "1950s.toml"
    room.write_text(
        '[room]\ncountry = "us"\ndecade = "1950s"\n\n' + fact_lines
    )
    return data


def test_quantity_matching_display_value_passes(tmp_path: Path) -> None:
    data = _write_quantity_room(
        tmp_path,
        '[[fact]]\nid = "us-1950s-tv"\npanel = "diffusion"\nlabel = "TV"\n'
        'value = "12.3%"\nunit = "% of households"\nsource = "src-1"\ntier = "A"\n'
        "quantity = 12.3\n",
    )
    assert check_corpus(load_corpus(data)) == []


def test_quantity_with_thousands_separator_passes(tmp_path: Path) -> None:
    data = _write_quantity_room(
        tmp_path,
        '[[fact]]\nid = "us-1950s-sqft"\npanel = "home"\nlabel = "Floor area"\n'
        'value = "Median 1,500 sq ft"\nunit = "sq ft"\nsource = "src-1"\ntier = "A"\n'
        "quantity = 1500\n",
    )
    assert check_corpus(load_corpus(data)) == []


def test_quantity_absent_from_display_value_fails(tmp_path: Path) -> None:
    """The structured quantity transcribes the displayed datum — drift is a gate failure."""
    data = _write_quantity_room(
        tmp_path,
        '[[fact]]\nid = "us-1950s-tv"\npanel = "diffusion"\nlabel = "TV"\n'
        'value = "12.3%"\nunit = "% of households"\nsource = "src-1"\ntier = "A"\n'
        "quantity = 12.4\n",
    )
    problems = check_corpus(load_corpus(data))
    assert any("does not appear in the display value" in p for p in problems)


def test_quantity_must_be_numeric(tmp_path: Path) -> None:
    data = _write_quantity_room(
        tmp_path,
        '[[fact]]\nid = "us-1950s-tv"\npanel = "diffusion"\nlabel = "TV"\n'
        'value = "12.3%"\nunit = "% of households"\nsource = "src-1"\ntier = "A"\n'
        'quantity = "12.3"\n',
    )
    with pytest.raises(LoadError, match="must be a number"):
        load_corpus(data)


def test_uk_rooms_declare_resolvable_anchors() -> None:
    """Every UK room that declares an anchor resolves it to a usable fact.

    ``check_corpus`` already fails a dangling or wrong-basis anchor. What this
    adds is the population count: the rooms that are *supposed* to carry an
    anchor still do. A silent regression that dropped ``income_anchor`` from a
    room would leave the gate green — the room would simply stop computing
    affordability, which reads exactly like a room that never had it.
    """
    corpus = load_corpus(DATA)
    uk = {r.decade: r for r in corpus.rooms if r.country == "uk"}
    assert set(uk) == {"1950s", "1960s", "1970s", "1980s", "1990s", "2000s", "2010s"}

    with_income = {d for d, r in uk.items() if r.income_anchor}
    with_wage = {d for d, r in uk.items() if r.wage_anchor}
    assert with_income == {"1970s", "1980s", "1990s", "2000s", "2010s"}
    assert with_wage == {"1990s", "2000s", "2010s"}


def test_uk_affordability_axis_computes_where_anchored() -> None:
    """The three fully anchored UK rooms produce both axes, at tier A.

    This is the deliverable of the UK affordability work: a priced fact, a wage
    anchor and an income anchor in the same room and the same year, so that the
    house price divides into hours of work and into a share of income.
    """
    from vitrine.site.projections.affordability import affordability_for_room

    corpus = load_corpus(DATA)
    for decade in ("1990s", "2000s", "2010s"):
        room = next(
            r for r in corpus.rooms if r.country == "uk" and r.decade == decade
        )
        display = affordability_for_room(corpus, room)
        priced = f"uk-{decade}-house-price"
        assert priced in display, f"{decade}: house price computes no affordability"
        assert "hours of work" in display[priced]["hours"]
        assert "% of annual income" in display[priced]["pct"]
        assert display[priced]["tier"] == "A"


def test_uk_hours_to_afford_a_house_rose_across_the_anchored_decades() -> None:
    """1997 → 2010: the same dwelling costs strictly more hours each decade.

    A guard on the arithmetic rather than the prose. If an anchor were swapped
    for the wrong population — the full-time median instead of the all-jobs one,
    say — the ratios would still render, and only their direction and spacing
    would betray it.
    """
    from vitrine.affordability import afford

    corpus = load_corpus(DATA)
    hours = {}
    for decade in ("1990s", "2000s", "2010s"):
        room = next(
            r for r in corpus.rooms if r.country == "uk" and r.decade == decade
        )
        by_id = {f.id: f for f in room.facts}
        result = afford(
            by_id[f"uk-{decade}-house-price"],
            wage=by_id[room.wage_anchor],
            income=by_id[room.income_anchor],
        )
        assert result.hours_to_afford is not None
        hours[decade] = result.hours_to_afford

    assert hours["1990s"] < hours["2000s"] < hours["2010s"]
    assert hours["2010s"] > 2 * hours["1990s"]
