"""Minimal V0 renderer: lobby, room pages, methodology. Schematic on purpose.

Every rendered fact id is also written to _site/facts-manifest.txt — the seed
for the render-coverage invariant (Plan 001 WI-4).
"""

from __future__ import annotations

from pathlib import Path

from jinja2 import DictLoader, Environment, select_autoescape

from vitrine.model import Corpus, Panel, Room, panel_title, tier_label

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
  <details>
    <summary>provenance</summary>
    <div class="card">
      {% set src = sources[fact.source] %}
      <strong>{{ src.title }}</strong><br>
      {{ src.publisher }}, {{ src.year }} · <a href="{{ src.url }}">source</a><br>
      <em>Population measured:</em> {{ src.population }}<br>
      <em>Confidence:</em> {{ fact.tier.value }} — {{ tier_label(fact.tier) }}
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


def render_site(corpus: Corpus, out_dir: Path) -> None:
    env = Environment(
        loader=DictLoader(
            {"base": _BASE, "index": _INDEX, "room": _ROOM, "methodology": _METHODOLOGY}
        ),
        autoescape=select_autoescape(default=True),
    )
    env.globals["panel_title"] = panel_title
    env.globals["tier_label"] = tier_label

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

    (out_dir / "index.html").write_text(
        env.get_template("index").render(root="", by_country=sorted(by_country.items()))
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
            )
        )
        rendered_ids.extend(fact.id for fact in room.facts)

    (out_dir / "facts-manifest.txt").write_text("\n".join(rendered_ids) + "\n")
