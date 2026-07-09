"""The series layer (plan 010): loader parsing, gate invariants, and the
series/fact drift detector. Mirrors the gate-test discipline: green on valid
data, red on each enumerated break."""

from pathlib import Path

import pytest

from vitrine.check import check_series
from vitrine.loader import load_corpus
from vitrine.series import SeriesError, load_series

DATA = Path(__file__).parent.parent / "data"


def _write_corpus(tmp_path: Path, *, fact_amount: str = "") -> Path:
    """A minimal corpus with one source and one fact (optionally structured)."""
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
        '[[fact]]\nid = "us-1950s-x"\npanel = "budget"\nlabel = "L"\nvalue = "100"\n'
        'unit = "U"\nsource = "src-1"\ntier = "A"\n'
        + fact_amount
    )
    return tmp_path


# A valid values-series (floats) and a valid values_minor-series (integer cents).
_GOOD_VALUES = (
    '[[series]]\n'
    'id = "cpi-test"\nlabel = "Test CPI"\nsource = "src-1"\ntier = "A"\n'
    'unit = "index"\npopulation = "all"\n\n'
    "[series.values]\n1950 = 24.1\n1951 = 26.0\n"
)
_GOOD_MINOR = (
    '[[series]]\n'
    'id = "income-test"\nlabel = "Test income"\nsource = "src-1"\ntier = "A"\n'
    'unit = "USD"\npopulation = "all"\n\n'
    "[series.values_minor]\n1950 = 331900\n1951 = 340000\n"
)


def _series_body(tail: str, *, sid: str = "s", source: str = "src-1") -> str:
    """A series block with the given sub-table tail, e.g. '[series.values]\\n1950 = 1.0'."""
    return (
        "[[series]]\n"
        f'id = "{sid}"\nlabel = "L"\nsource = "{source}"\ntier = "A"\n'
        'unit = "u"\npopulation = "p"\n\n'
        + tail
    )


def _write_series(tmp_path: Path, body: str) -> Path:
    sdir = tmp_path / "series"
    sdir.mkdir(exist_ok=True)
    (sdir / "test.toml").write_text(body)
    return tmp_path


# ── committed corpus ─────────────────────────────────────────────────────────


def test_committed_series_load_and_pass_gate() -> None:
    corpus = load_corpus(DATA)
    series = load_series(DATA)
    assert series, "committed corpus must declare at least one series"
    assert check_series(series, corpus) == []


# ── loader parsing ───────────────────────────────────────────────────────────


def test_loader_parses_year_keys_to_int(tmp_path: Path) -> None:
    data = _write_corpus(tmp_path)
    _write_series(data, _GOOD_VALUES)
    series = load_series(data)
    assert set(series["cpi-test"].values) == {1950, 1951}
    assert series["cpi-test"].values[1950] == 24.1


def test_loader_rejects_non_integer_year_key(tmp_path: Path) -> None:
    data = _write_corpus(tmp_path)
    _write_series(data, _series_body('[series.values]\n"not-a-year" = 1.0\n'))
    with pytest.raises(SeriesError, match="not an integer year"):
        load_series(data)


def test_loader_rejects_float_in_minor_table(tmp_path: Path) -> None:
    data = _write_corpus(tmp_path)
    _write_series(data, _series_body("[series.values_minor]\n1950 = 3319.5\n"))
    with pytest.raises(SeriesError, match="must be an integer"):
        load_series(data)


def test_loader_rejects_bad_tier(tmp_path: Path) -> None:
    data = _write_corpus(tmp_path)
    body = _series_body("[series.values]\n1950 = 1.0\n").replace('tier = "A"', 'tier = "Z"')
    with pytest.raises(SeriesError, match="tier 'Z'"):
        load_series(_write_series(data, body))


def test_loader_rejects_single_table_not_array(tmp_path: Path) -> None:
    """A curator writing [series] instead of [[series]] gets a clear error."""
    data = _write_corpus(tmp_path)
    _write_series(
        data,
        '[series]\nid = "s"\nlabel = "L"\nsource = "src-1"\ntier = "A"\n'
        'unit = "u"\npopulation = "p"\n\n[series.values]\n1950 = 1.0\n',
    )
    with pytest.raises(SeriesError, match="array of tables"):
        load_series(data)


def test_load_series_handles_missing_dir(tmp_path: Path) -> None:
    """The layer is optional until a chart references one."""
    data = _write_corpus(tmp_path)
    assert load_series(data) == {}


# ── gate invariants ──────────────────────────────────────────────────────────


def test_gate_rejects_unresolved_source(tmp_path: Path) -> None:
    data = _write_corpus(tmp_path)
    _write_series(data, _series_body("[series.values]\n1950 = 1.0\n", source="no-such"))
    problems = check_series(load_series(data), load_corpus(data))
    assert any("unknown source" in p for p in problems)


def test_gate_rejects_empty_values(tmp_path: Path) -> None:
    data = _write_corpus(tmp_path)
    _write_series(data, _series_body(""))
    problems = check_series(load_series(data), load_corpus(data))
    assert any("neither" in p for p in problems)


def test_gate_rejects_both_values_and_values_minor(tmp_path: Path) -> None:
    data = _write_corpus(tmp_path)
    _write_series(
        data, _series_body("[series.values]\n1950 = 1.0\n[series.values_minor]\n1950 = 100\n")
    )
    problems = check_series(load_series(data), load_corpus(data))
    assert any("both" in p for p in problems)


def test_gate_rejects_id_collision_with_fact(tmp_path: Path) -> None:
    data = _write_corpus(tmp_path)
    _write_series(data, _GOOD_VALUES.replace('id = "cpi-test"', 'id = "us-1950s-x"'))
    problems = check_series(load_series(data), load_corpus(data))
    assert any("collides with a fact id" in p for p in problems)


# ── drift detector (invariant 9) ─────────────────────────────────────────────


_FACT_WITH_AMOUNT = (
    'amount_minor = 331900\ncurrency = "USD"\nprice_year = 1950\nbasis = "annual"\n'
)


def test_drift_detector_catches_disagreement_with_fact(tmp_path: Path) -> None:
    """A unique-source series whose year overlaps a structured fact's price_year
    must agree — the same number must not drift in two places."""
    data = _write_corpus(tmp_path, fact_amount=_FACT_WITH_AMOUNT)
    _write_series(data, _series_body("[series.values_minor]\n1950 = 999999\n"))
    problems = check_series(load_series(data), load_corpus(data))
    assert any("drifted in two places" in p for p in problems)


def test_drift_detector_silent_when_agreement(tmp_path: Path) -> None:
    data = _write_corpus(tmp_path, fact_amount=_FACT_WITH_AMOUNT)
    _write_series(data, _GOOD_MINOR)
    assert check_series(load_series(data), load_corpus(data)) == []


def test_drift_detector_skips_when_two_series_share_source(tmp_path: Path) -> None:
    """When two series share a source the 1:1 correspondence is ambiguous;
    the detector skips rather than false-positive (documented limit)."""
    data = _write_corpus(tmp_path, fact_amount=_FACT_WITH_AMOUNT)
    _write_series(
        data,
        _series_body("[series.values_minor]\n1950 = 1\n", sid="a")
        + _series_body("[series.values_minor]\n1950 = 2\n", sid="b"),
    )
    assert check_series(load_series(data), load_corpus(data)) == []


# ── cross-unit wage drift (series values-dollars vs fact amount_minor cents) ──


def _write_hourly_fact(tmp_path: Path, *, amount_minor: int, basis: str = "hourly") -> Path:
    data = _write_corpus(tmp_path)
    (data / "us" / "1950s.toml").write_text(
        '[room]\ncountry = "us"\ndecade = "1950s"\n\n'
        '[[fact]]\nid = "us-1950s-x"\npanel = "day"\nlabel = "L"\nvalue = "$1.32"\n'
        'unit = "USD/hr"\nsource = "src-1"\ntier = "A"\n'
        f"amount_minor = {amount_minor}\ncurrency = \"USD\"\nprice_year = 1950\n"
        f'basis = "{basis}"\n'
    )
    return data


def test_cross_unit_drift_catches_mismatched_wage(tmp_path: Path) -> None:
    """An hourly series (float dollars) must agree with an hourly fact (cents)
    converted to dollars within cent-rounding tolerance."""
    data = _write_hourly_fact(tmp_path, amount_minor=132)  # $1.32/hr
    _write_series(data, _series_body("[series.values]\n1950 = 2.50\n"))  # drifts
    problems = check_series(load_series(data), load_corpus(data))
    assert any("drifted in two places" in p for p in problems)


def test_cross_unit_drift_passes_within_rounding(tmp_path: Path) -> None:
    """$1.3158 (annual mean) vs $1.32 (fact, rounded to the cent) agrees."""
    data = _write_hourly_fact(tmp_path, amount_minor=132)
    _write_series(data, _series_body("[series.values]\n1950 = 1.3158\n"))
    assert check_series(load_series(data), load_corpus(data)) == []


def test_cross_unit_drift_skips_weekly_facts(tmp_path: Path) -> None:
    """A weekly-earnings fact shares an hourly series's source but is a
    different basis — the detector must not compare them (no false positive)."""
    data = _write_hourly_fact(tmp_path, amount_minor=5329, basis="weekly")  # $53.29/wk
    _write_series(data, _series_body("[series.values]\n1950 = 1.3158\n"))  # $/hr
    assert check_series(load_series(data), load_corpus(data)) == []


# ── float (CPI-style) drift via fact.quantity ────────────────────────────────


def test_float_drift_catches_mismatched_quantity(tmp_path: Path) -> None:
    """A float series must agree (within display rounding) with a quantity fact."""
    data = _write_corpus(tmp_path)
    (data / "us" / "1950s.toml").write_text(
        '[room]\ncountry = "us"\ndecade = "1950s"\n\n'
        '[[fact]]\nid = "us-1950s-x"\npanel = "work-buys"\nlabel = "L"\nvalue = "24.1"\n'
        'unit = "index"\nsource = "src-1"\ntier = "A"\nquantity = 24.1\nprice_year = 1950\n'
    )
    _write_series(data, _series_body("[series.values]\n1950 = 50.0\n"))  # drifts
    problems = check_series(load_series(data), load_corpus(data))
    assert any("drifted in two places" in p for p in problems)
