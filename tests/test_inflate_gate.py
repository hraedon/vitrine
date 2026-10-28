"""The provenance gate must reject an index ratio the evaluator cannot divide."""

import pytest

from vitrine.check import check_corpus, check_series
from vitrine.derive import DeriveError, evaluate
from vitrine.model import Basis, Corpus, DerivedFact, DerivedOp, Fact, Panel, Room, Source, Tier
from vitrine.series import Series


def specimen(base: float, target: float) -> tuple[Corpus, dict[str, Series]]:
    fact = Fact(
        "us-1950s-base", Panel.BUDGET, "Base", "$1", "USD", "source", Tier.A,
        amount_minor=100, currency="USD", price_year=1950, basis=Basis.ANNUAL,
    )
    derived = DerivedFact(
        "us-1950s-inflated", Panel.BUDGET, "Inflated", "USD", DerivedOp.INFLATE,
        numerator=fact.id, inflate_series="index", inflate_from_year=1950,
        inflate_to_year=1960,
    )
    corpus = Corpus(
        {"source": Source("source", "Source", "Publisher", 1960,
                          "https://example.org", "population")},
        {}, (Room("us", "1950s", (fact,), (derived,)),),
    )
    series = {"index": Series(
        "index", "Index", "source", Tier.A, "index", "population",
        values={1950: base, 1960: target},
    )}
    return corpus, series


def test_zero_inflation_base_fails_gate_before_evaluation() -> None:
    corpus, series = specimen(0, 1)
    assert check_series(series, corpus) == []  # Zero is a finite, literal observation.
    assert any("inflate_from_year value is zero" in p for p in check_corpus(corpus, series))
    room = corpus.rooms[0]
    with pytest.raises(DeriveError, match="inflate_from_year value is zero"):
        evaluate(room, room.derived[0], series)


def test_zero_inflation_target_remains_a_defined_ratio() -> None:
    corpus, series = specimen(1, 0)
    assert check_corpus(corpus, series) == []
    room = corpus.rooms[0]
    assert evaluate(room, room.derived[0], series).numeric_value == 0
