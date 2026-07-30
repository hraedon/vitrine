"""The docent numeral gate and essay rendering (Plan 016).

Essays are data whose prose interpolates facts by id. The gate closes the
numeral channel: after stripping ``{fact:…}`` bindings, only years and
decade words may remain — everything else fails the build naming the token.
"""

from __future__ import annotations

import re
from html import unescape
from pathlib import Path

import pytest

from vitrine.check import check_essays
from vitrine.loader import load_corpus
from vitrine.model import BlockKind, Corpus, Essay, EssayBlock
from vitrine.series import load_series
from vitrine.site.projections.essays import validate_essay_registries
from vitrine.site.render import render_site

DATA = Path(__file__).parent.parent / "data"


def essay(
    slug: str = "tour",
    blocks: tuple[EssayBlock, ...] = (EssayBlock(kind=BlockKind.PROSE, text="ok"),),
    standfirst: str = "A standfirst.",
) -> Essay:
    return Essay(slug=slug, title="A tour", standfirst=standfirst, blocks=blocks)


@pytest.fixture(scope="module")
def corpus() -> Corpus:
    return load_corpus(DATA)


# ── loading ──────────────────────────────────────────────────────────────────


def test_essays_load(corpus: Corpus) -> None:
    assert len(corpus.essays) == 2
    one = next(e for e in corpus.essays if e.slug == "one-paycheck")
    assert one.title == "One paycheck"
    assert any(b.kind is BlockKind.CHART and b.metric for b in one.blocks)
    two = next(e for e in corpus.essays if e.slug == "the-work-that-moved")
    assert any(b.kind is BlockKind.CHART and b.group for b in two.blocks)


def test_committed_essays_pass_the_gate(corpus: Corpus) -> None:
    assert check_essays(corpus) == []


# ── the numeral gate ─────────────────────────────────────────────────────────


def _gate_problem(corpus: Corpus, bad: Essay) -> list[str]:
    victim = Corpus(
        sources=corpus.sources,
        assumptions=corpus.assumptions,
        rooms=corpus.rooms,
        essays=(bad,),
    )
    return check_essays(victim)


def test_bare_dollar_amount_fails_naming_block_and_token(corpus: Corpus) -> None:
    bad = essay(
        blocks=(
            EssayBlock(
                kind=BlockKind.PROSE,
                text="The median family reported $3,675 a year.",
            ),
        )
    )
    problems = _gate_problem(corpus, bad)
    assert any("$3,675" in p and "block 1" in p for p in problems)


def test_allowed_year_forms_pass(corpus: Corpus) -> None:
    good = essay(
        blocks=(
            EssayBlock(
                kind=BlockKind.PROSE,
                text=(
                    "In 1950, after 1947–1955 and before the 1960s ended, the "
                    "century (1900) turned quietly toward 2035 and the 2020s."
                ),
            ),
            EssayBlock(kind=BlockKind.CHART, arc="radio"),
        )
    )
    problems = _gate_problem(corpus, good)
    assert not any("numeral" in p for p in problems), problems


def test_verbal_neighbors_of_numbers_fail(corpus: Corpus) -> None:
    for token in ("40%", "nearly 40", "52", "$53.46", "3.5", "twenty 2"):
        bad = essay(
            blocks=(
                EssayBlock(kind=BlockKind.PROSE, text=f"Share fell to {token} flat."),
                EssayBlock(kind=BlockKind.CHART, metric="food-share"),
            )
        )
        assert any("numeral" in p for p in _gate_problem(corpus, bad)), token


def test_unknown_fact_in_prose_fails(corpus: Corpus) -> None:
    bad = essay(
        blocks=(
            EssayBlock(
                kind=BlockKind.PROSE,
                text="It cost {fact:us-1999s-nope}.",
            ),
        )
    )
    problems = _gate_problem(corpus, bad)
    assert any("us-1999s-nope" in p for p in problems)


def test_unknown_standfirst_fact_fails(corpus: Corpus) -> None:
    bad = essay(standfirst="Costs {fact:us-0000s-ghost}.")
    problems = _gate_problem(corpus, bad)
    assert any("standfirst" in p for p in problems)


def test_chart_block_naming_two_slugs_fails(corpus: Corpus) -> None:
    bad = essay(
        blocks=(EssayBlock(kind=BlockKind.CHART, arc="radio", metric="food-share"),)
    )
    problems = _gate_problem(corpus, bad)
    assert any("exactly one" in p for p in problems)


def test_chart_block_with_prose_fails(corpus: Corpus) -> None:
    bad = essay(
        blocks=(EssayBlock(kind=BlockKind.CHART, arc="radio", text="caption creep"),)
    )
    problems = _gate_problem(corpus, bad)
    assert any("no prose text" in p for p in problems)


def test_essay_without_binding_fails(corpus: Corpus) -> None:
    bad = essay(blocks=(EssayBlock(kind=BlockKind.PROSE, text="Pure vibes."),))
    problems = _gate_problem(corpus, bad)
    assert any("must engage the record" in p for p in problems)


def test_duplicate_slug_fails(corpus: Corpus) -> None:
    victim = Corpus(
        sources=corpus.sources,
        assumptions=corpus.assumptions,
        rooms=corpus.rooms,
        essays=(essay(), essay()),
    )
    problems = check_essays(victim)
    assert any("duplicate essay slug" in p for p in problems)


def test_malformed_slug_fails(corpus: Corpus) -> None:
    problems = _gate_problem(corpus, essay(slug="Not A Slug"))
    assert any("slug must be lowercase" in p for p in problems)


def test_zero_essays_passes() -> None:
    corpus = Corpus(sources={}, assumptions={}, rooms=(), essays=())
    assert check_essays(corpus) == []


def test_unknown_chart_slugs_fail_build_validation(corpus: Corpus) -> None:
    bad = essay(blocks=(EssayBlock(kind=BlockKind.CHART, arc="no-such-arc"),))
    victim = Corpus(
        sources=corpus.sources,
        assumptions=corpus.assumptions,
        rooms=corpus.rooms,
        essays=(bad,),
    )
    with pytest.raises(ValueError, match="no-such-arc"):
        validate_essay_registries(victim)
    validate_essay_registries(corpus)  # the committed essays resolve


# ── rendering ────────────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def site(corpus: Corpus, tmp_path_factory: pytest.TempPathFactory) -> Path:
    out = tmp_path_factory.mktemp("essay-site")
    render_site(corpus, out, load_series(DATA), DATA)
    return out


def test_essay_pages_render_interpolated_chips(site: Path) -> None:
    html = (site / "essays" / "one-paycheck.html").read_text()
    # every figure in the prose is a deep-linked chip carrying its fact id
    assert html.count('class="factchip"') == 7
    assert html.count('class="factchip computed"') == 2
    for fid in (
        "us-1950s-median-income-four-person",
        "us-1950s-weekly-earnings",
        "us-2020s-married-women-lfpr",
    ):
        assert f'data-fact-id="{fid}"' in html
    # the metric chart renders inside the essay
    assert 'id="metric-single-earner-wage-coverage"' in html


def test_essay_deck_covers_every_prose_fact(site: Path) -> None:
    from vitrine.check import check_mark_coverage

    corpus = load_corpus(DATA)
    assert check_mark_coverage(corpus, site) == []
    html = (site / "essays" / "one-paycheck.html").read_text()
    # the 7 interpolated plain facts each get an overlay on the page
    assert html.count('class="placard-overlay"') == 7


def test_rooms_backlink_to_tours(site: Path) -> None:
    html_1950s = (site / "rooms" / "us-1950s.html").read_text()
    assert 'href="../essays/one-paycheck.html"' in html_1950s
    html_1900s = (site / "rooms" / "us-1900s.html").read_text()
    assert 'href="../essays/one-paycheck.html"' not in html_1900s
    assert 'href="../essays/the-work-that-moved.html"' in html_1900s


def test_tours_index_and_lobby_list_tours(site: Path) -> None:
    index = (site / "essays" / "index.html").read_text()
    assert "One paycheck" in index and "The work that moved" in index
    lobby = (site / "index.html").read_text()
    assert 'href="essays/one-paycheck.html"' in lobby
    assert 'href="essays/the-work-that-moved.html"' in lobby


def test_standfirst_carries_no_bare_numerals(site: Path) -> None:
    """Belt and braces: rendered docent cards contain no digit outside a chip
    or the gate's allowed year/decade forms — the promise, checked at the DOM."""
    year_form = re.compile(
        r"(?:18[5-9]\d|19\d\d|20(?:[01]\d|2\d|3[0-5]))s?(?:[-–—](?:18[5-9]\d|19\d\d|20(?:[01]\d|2\d|3[0-5]))s?)?"
    )
    html = (site / "essays" / "the-work-that-moved.html").read_text()
    for card in re.findall(r'<div class="docent-card">(.*?)</div>', html, re.S):
        text_only = re.sub(r'<a class="factchip[^"]*"[^>]*>.*?</a>', "", card)
        bare = unescape(re.sub(r"<[^>]+>", "", text_only))
        bare = year_form.sub("", bare)
        assert not re.search(r"\d", bare), bare
