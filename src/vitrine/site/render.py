"""Minimal V0 renderer: lobby, room pages, methodology. Schematic on purpose.

Every rendered fact id is also written to _site/facts-manifest.txt — the seed
for the render-coverage invariant (Plan 001 WI-4).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from jinja2 import DictLoader, Environment, select_autoescape

from vitrine.affordability import afford
from vitrine.compare import Comparison, compare_item
from vitrine.model import Basis, Corpus, Panel, Room, basis_label, panel_title, tier_label

_BASE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{% block title %}vitrine{% endblock %}</title>
<style>
  body { font-family: Georgia, serif; max-width: 60rem; margin: 2rem auto; padding: 0 1rem;
         background: #faf8f4; color: #222; }
  a { color: #5a4632; }
  h1, h2 { font-weight: normal; }
  .tier { font-family: monospace; font-size: 0.8em; border: 1px solid #999;
          border-radius: 3px; padding: 0 0.3em; margin-left: 0.4em; }
  .disclaimer { border: 1px solid #c9b8a0; background: #f3ecdf; padding: 0.8rem 1rem;
                font-style: italic; margin: 1.5rem 0; }
  .panel { margin: 2rem 0; }
  .fact { margin: 0.8rem 0; }
  .fact .value { font-size: 1.15em; }
  .afford { color: #5a4632; }
  .comparison { margin: 2rem 0; }
  .comparison ul { list-style: none; padding-left: 0; }
  details { margin-top: 0.2rem; }
  details summary { cursor: pointer; color: #5a4632; font-size: 0.85em; }
  .card { font-size: 0.85em; background: #fff; border: 1px solid #ddd;
          padding: 0.6rem 0.8rem; margin-top: 0.3rem; }
</style>
</head>
<body>
<p><a href="{{ root }}index.html">vitrine</a> · <a href="{{ root }}methodology.html">methodology</a></p>
{% block body %}{% endblock %}
</body>
</html>
"""

_INDEX = """{% extends "base" %}
{% block title %}vitrine — the museum lobby{% endblock %}
{% block body %}
<h1>vitrine</h1>
<p>A decade-by-decade museum of the median-income family's lifestyle.
Every fact is behind glass: open its drawer to see who measured it, when, and how sure we are.</p>
{% for country, rooms in by_country %}
<h2>{{ country }}</h2>
<ul>
{% for room in rooms %}
<li><a href="rooms/{{ room.slug }}.html">{{ room.decade }}</a> ({{ room.facts | length }} facts)</li>
{% endfor %}
</ul>
{% endfor %}
{% if comparisons %}
<hr>
<h2>Cross-decade comparisons</h2>
{% for comp in comparisons %}
<div class="comparison">
<h3>{{ comp.label }}</h3>
<ul>
{% for row in comp.rows %}
<li>
{% if row.has_data %}
<strong>{{ row.decade }}</strong>: {{ row.price_display }}
{% if row.hours_display %} — {{ row.hours_display }}{% endif %}
{% if row.pct_display %} · {{ row.pct_display }}{% endif %}
<span class="tier">{{ row.tier }}</span>
{% else %}
<strong>{{ row.decade }}</strong>: <em>no record</em>
{% endif %}
</li>
{% endfor %}
</ul>
{% for row in comp.rows %}
{% if row.has_data and row.anchor_note %}
<p><small>{{ row.decade }} anchors: {{ row.anchor_note }}</small></p>
{% endif %}
{% endfor %}
</div>
{% endfor %}
{% endif %}
{% endblock %}
"""

_ROOM = """{% extends "base" %}
{% block title %}{{ room.country }} · {{ room.decade }} — vitrine{% endblock %}
{% block body %}
<h1>{{ room.country | upper }} — the {{ room.decade }}</h1>
<div class="disclaimer">{{ disclaimer }}</div>
{% for panel, facts in panels %}
<div class="panel">
<h2>{{ panel_title(panel) }}</h2>
{% if not facts %}<p><em>Not yet curated.</em></p>{% endif %}
{% for fact in facts %}
<div class="fact">
  <span class="value"><strong>{{ fact.value }}</strong> — {{ fact.label }}</span>
  <span class="tier" title="{{ tier_label(fact.tier) }}">{{ fact.tier.value }}</span>
  <br><small>{{ fact.unit }}</small>
  {% if fact.id in affordability %}
  {% set aff = affordability[fact.id] %}
  {% if aff.hours %}
  <br><small class="afford">{{ aff.hours }} <span class="tier" title="affordability confidence">{{ aff.tier }}</span></small>
  {% endif %}
  {% if aff.pct %}
  <br><small class="afford">{{ aff.pct }}</small>
  {% endif %}
  {% endif %}
  <details>
    <summary>provenance</summary>
    <div class="card">
      {% set src = sources[fact.source] %}
      <strong>{{ src.title }}</strong><br>
      {{ src.publisher }}, {{ src.year }} · <a href="{{ src.url }}">source</a><br>
      <em>Population measured:</em> {{ src.population }}<br>
      <em>Confidence:</em> {{ fact.tier.value }} — {{ tier_label(fact.tier) }}
      {% if fact.basis is not none %}
      <br><em>Basis:</em> {{ basis_label(fact.basis) }}
      {% endif %}
      {% if fact.id in affordability and affordability[fact.id].anchor_note %}
      <br><em>Affordability anchors:</em> {{ affordability[fact.id].anchor_note }}
      {% endif %}
      {% if fact.notes %}<br><em>Curator note:</em> {{ fact.notes }}{% endif %}
      {% if src.notes %}<br><em>Source note:</em> {{ src.notes }}{% endif %}
      {% for aid in fact.assumptions %}
      <br><em>Assumption:</em> <a href="{{ root }}methodology.html#{{ aid }}">{{ assumptions[aid].title }}</a>
      {% endfor %}
    </div>
  </details>
</div>
{% endfor %}
</div>
{% endfor %}
{% endblock %}
"""

_METHODOLOGY = """{% extends "base" %}
{% block title %}methodology — vitrine{% endblock %}
{% block body %}
<h1>Methodology &amp; assumptions</h1>
<p>Every methodological choice that would mislead if left implicit is written
here once and linked from every fact it touches.</p>
{% for a in assumptions %}
<h2 id="{{ a.id }}">{{ a.title }}</h2>
<p>{{ a.statement }}</p>
{% endfor %}
{% endblock %}
"""


def _panels_for(room: Room) -> list[tuple[Panel, list[object]]]:
    return [(panel, [f for f in room.facts if f.panel is panel]) for panel in Panel]


@dataclass(frozen=True, slots=True)
class _ComparisonRow:
    decade: str
    price_display: str
    hours_display: str
    pct_display: str
    tier: str
    anchor_note: str
    has_data: bool


@dataclass(frozen=True, slots=True)
class _ComparisonView:
    label: str
    rows: tuple[_ComparisonRow, ...]


def _format_hours(hours: float) -> str:
    if hours < 100:
        return f"≈ {hours:.1f} hours of work"
    return f"≈ {hours:,.0f} hours of work"


def _format_pct(pct: float) -> str:
    return f"≈ {pct:.1f}% of annual income"


def _affordability_for_room(corpus: Corpus, room: Room) -> dict[str, dict[str, str]]:
    """Compute affordability display for each TOTAL-basis fact in a room."""
    display: dict[str, dict[str, str]] = {}
    if not room.wage_anchor and not room.income_anchor:
        return display

    by_id = {f.id: f for f in room.facts}
    wage_fact = by_id.get(room.wage_anchor) if room.wage_anchor else None
    income_fact = by_id.get(room.income_anchor) if room.income_anchor else None

    wage_pop = ""
    income_pop = ""
    if wage_fact is not None:
        src = corpus.sources.get(wage_fact.source)
        if src is not None:
            wage_pop = src.population
    if income_fact is not None:
        src = corpus.sources.get(income_fact.source)
        if src is not None:
            income_pop = src.population

    for fact in room.facts:
        if fact.basis is not Basis.TOTAL or fact.amount_minor is None:
            continue
        aff = afford(
            fact,
            wage=wage_fact,
            income=income_fact,
            wage_population=wage_pop,
            income_population=income_pop,
        )

        hours_str = ""
        if aff.hours_to_afford is not None:
            hours_str = _format_hours(aff.hours_to_afford)
        pct_str = ""
        if aff.pct_of_income is not None:
            pct_str = _format_pct(aff.pct_of_income)

        display[fact.id] = {
            "hours": hours_str,
            "pct": pct_str,
            "tier": aff.tier.value,
            "anchor_note": aff.anchor_note,
        }

    return display


def _build_comparison_view(comparison: Comparison, decades: list[str]) -> _ComparisonView:
    point_map = {p.decade: p for p in comparison.points}
    rows: list[_ComparisonRow] = []
    for decade in decades:
        point = point_map.get(decade)
        if point is None:
            rows.append(
                _ComparisonRow(
                    decade=decade,
                    price_display="",
                    hours_display="",
                    pct_display="",
                    tier="",
                    anchor_note="",
                    has_data=False,
                )
            )
        else:
            hours_str = ""
            if point.afford.hours_to_afford is not None:
                hours_str = _format_hours(point.afford.hours_to_afford)
            pct_str = ""
            if point.afford.pct_of_income is not None:
                pct_str = _format_pct(point.afford.pct_of_income)
            rows.append(
                _ComparisonRow(
                    decade=decade,
                    price_display=point.price_display,
                    hours_display=hours_str,
                    pct_display=pct_str,
                    tier=point.afford.tier.value,
                    anchor_note=point.afford.anchor_note,
                    has_data=True,
                )
            )
    return _ComparisonView(label=comparison.label, rows=tuple(rows))


def render_site(corpus: Corpus, out_dir: Path) -> None:
    env = Environment(
        loader=DictLoader(
            {"base": _BASE, "index": _INDEX, "room": _ROOM, "methodology": _METHODOLOGY}
        ),
        autoescape=select_autoescape(default=True),
    )
    env.globals["panel_title"] = panel_title
    env.globals["tier_label"] = tier_label
    env.globals["basis_label"] = basis_label

    disclaimer_entry = corpus.assumptions.get("composite-family")
    if disclaimer_entry is None:
        raise ValueError(
            "assumption ledger must contain 'composite-family' — "
            "the disclaimer renders on every room (charter rule)"
        )

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "rooms").mkdir(exist_ok=True)

    by_country: dict[str, list[Room]] = {}
    for room in corpus.rooms:
        by_country.setdefault(room.country, []).append(room)

    decades = sorted({room.decade for room in corpus.rooms})
    comparisons = [
        compare_item(
            corpus,
            "A median home, in hours of work",
            {
                "1950s": "us-1950s-median-home-value",
                "2020s": "us-2020s-median-home-value",
            },
        ),
    ]
    comparison_views = [_build_comparison_view(c, decades) for c in comparisons]

    (out_dir / "index.html").write_text(
        env.get_template("index").render(
            root="",
            by_country=sorted(by_country.items()),
            comparisons=comparison_views,
        )
    )
    (out_dir / "methodology.html").write_text(
        env.get_template("methodology").render(
            root="", assumptions=list(corpus.assumptions.values())
        )
    )

    rendered_ids: list[str] = []
    for room in corpus.rooms:
        (out_dir / "rooms" / f"{room.slug}.html").write_text(
            env.get_template("room").render(
                root="../",
                room=room,
                panels=_panels_for(room),
                sources=corpus.sources,
                assumptions=corpus.assumptions,
                disclaimer=disclaimer_entry.statement,
                affordability=_affordability_for_room(corpus, room),
            )
        )
        rendered_ids.extend(fact.id for fact in room.facts)

    (out_dir / "facts-manifest.txt").write_text("\n".join(rendered_ids) + "\n")
