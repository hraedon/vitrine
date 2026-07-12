"""The production renderer — three surfaces on the demo's design language.

Plan 007: rooms (the gallery proper), corridors (cross-decade arcs and the
pairwise comparison set), and the walkthrough (Plan 005's transect). All
pre-rendered, no ``<script>`` anywhere; the demo's click-to-inspect is anchor +
CSS ``:target``, so every placard is a citable URL. Every chart mark carries
``data-fact-id`` and the gate scans the built HTML (check_mark_coverage).

Every rendered fact id is written to _site/facts-manifest.txt — the
render-coverage invariant unchanged from Plan 001.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path

from jinja2 import DictLoader, Environment, select_autoescape
from markupsafe import Markup

from vitrine.affordability import afford
from vitrine.compare import Comparison, compare_item
from vitrine.derive import ComputedFact, evaluate_room
from vitrine.model import (
    Basis,
    Corpus,
    Fact,
    Measure,
    Panel,
    Room,
    basis_label,
    measure_label,
    panel_title,
    tier_label,
)
from vitrine.series import Series
from vitrine.site import curation, svg, symbols, tokens

# ── page shell ────────────────────────────────────────────────────────────────

_BASE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{% block title %}vitrine{% endblock %}</title>
<style>
  :root{color-scheme:dark}
  *{box-sizing:border-box}
  body{margin:0;background:{{ T.GROUND }};color:{{ T.IVORY }};font-family:{{ T.SANS }};line-height:1.55;-webkit-font-smoothing:antialiased}
  .wrap{max-width:1120px;margin:0 auto;padding:clamp(20px,4vw,44px)}
  a{color:{{ T.BRASS }}}
  .eyebrow{font-family:{{ T.MONO }};font-size:12px;letter-spacing:.22em;text-transform:uppercase;color:{{ T.BRASS }};margin:0 0 10px}
  h1{font-family:{{ T.SERIF }};font-weight:600;text-wrap:balance;font-size:clamp(28px,4.4vw,44px);line-height:1.08;margin:0 0 6px;color:#f3ead7}
  h1 em{font-style:italic;color:{{ T.BRASS }}}
  .sub{color:{{ T.INK_SOFT }};max-width:64ch;font-size:15px;margin:0}
  .topnav{font-family:{{ T.MONO }};font-size:11.5px;letter-spacing:.14em;text-transform:uppercase;margin:0 0 22px}
  .topnav a{color:{{ T.INK_SOFT }};text-decoration:none;margin-right:14px}
  .topnav a:hover,.topnav a.here{color:{{ T.BRASS }}}
  .plaque{margin:24px 0 20px;padding:16px 20px;border:1px solid {{ T.EDGE }};border-left:3px solid {{ T.BRASS }};background:linear-gradient(180deg,{{ T.CASE_2 }},{{ T.CASE }});border-radius:3px;max-width:76ch}
  .plaque b{color:#f3ead7;font-family:{{ T.SERIF }};font-style:italic;font-weight:600}
  .plaque span{color:{{ T.INK_SOFT }};font-size:14.5px}
   .decades{display:flex;gap:6px;align-items:center;flex-wrap:wrap;justify-content:center;margin:0 0 16px}
   .decades .lab{font-family:{{ T.MONO }};font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:{{ T.INK_SOFT }};margin-right:4px}
   .dbtn{font-family:{{ T.SERIF }};font-size:16px;color:{{ T.IVORY }};background:{{ T.CASE_2 }};border:1px solid {{ T.EDGE }};padding:5px 11px;border-radius:2px;text-decoration:none;white-space:nowrap}
  .dbtn:hover{border-color:{{ T.BRASS_DIM }};color:#f3ead7}
  .dbtn.on{background:{{ T.BRASS }};color:#241d10;border-color:{{ T.BRASS }};box-shadow:0 0 22px -6px {{ T.BRASS_DEEP }}}
   h2.case-title,summary.case-title{font-family:{{ T.MONO }};font-size:12px;letter-spacing:.18em;text-transform:uppercase;color:{{ T.BRASS }};margin:34px 0 4px;font-weight:600;list-style:none;cursor:pointer}
   summary.case-title::-webkit-details-marker{display:none}
   details.panel-group{margin-bottom:10px}
   details.panel-group[open]>summary.case-title{margin-bottom:14px}
   .case-sub{font-size:13px;color:{{ T.INK_SOFT }};margin:0 0 14px}
  .caveat{border-left:3px solid {{ T.BRASS_DEEP }};background:{{ T.CASE }};padding:8px 12px;margin:8px 0;font-size:13px;color:#c9bfa4;max-width:76ch}
  .gap-banner{border:1px solid #665037;border-left:4px solid {{ T.COPPER }};background:linear-gradient(90deg,#2b211a,{{ T.CASE }});padding:12px 15px;margin:14px 0 16px;color:#d8c9ad;font-size:14px;max-width:80ch}
  .gap-banner b{color:{{ T.COPPER }};font-family:{{ T.MONO }};font-size:10.5px;letter-spacing:.14em;text-transform:uppercase;margin-right:7px}
  .stage{position:relative;border:1px solid {{ T.EDGE }};border-radius:5px;background:{{ T.GROUND }};padding:8px;overflow:hidden}
  .stage::after{content:"";position:absolute;inset:0;pointer-events:none;box-shadow:inset 0 0 90px -30px #000;border-radius:5px}
  .stagehint{font-family:{{ T.MONO }};font-size:10.5px;letter-spacing:.12em;text-transform:uppercase;color:#5c5240;text-align:center;padding:6px 0 3px}
  svg.house{display:block;width:100%;height:auto}
  .house .structure *{stroke:{{ T.BRASS_DIM }};fill:none;stroke-width:1.6;opacity:.62}
  .house .groundline{stroke:{{ T.BRASS_DIM }};stroke-width:1.4;opacity:.4}
  .house .zlabel{font-family:{{ T.MONO }};font-size:8.5px;letter-spacing:.1em;fill:#6b5f47;text-transform:uppercase}
  .house .znote{font-family:{{ T.MONO }};font-size:9px;letter-spacing:.06em;fill:{{ T.BRASS }};text-transform:uppercase}
  .house a{text-decoration:none}
  .hs .ring{fill:none;stroke:{{ T.BRASS_DIM }};stroke-width:1.4;opacity:.5}
  .hs .gapring{stroke:{{ T.GAP }};stroke-dasharray:3 3;opacity:.9}
  .hs .glyph{stroke:{{ T.BRASS }};fill:none;stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round}
  .hs .glyph.fill{fill:{{ T.BRASS }};stroke:none}
  .hs .pct{font-family:{{ T.MONO }};font-size:9px;fill:{{ T.BRASS }};text-anchor:middle;opacity:.85}
  .hs .pct.gap{fill:{{ T.GAP }}}
  .hs:hover .ring{stroke:{{ T.BRASS }};opacity:1}
  .chart-panel{border:1px solid {{ T.EDGE }};border-radius:5px;background:{{ T.GROUND }};padding:14px 10px 6px;margin:10px 0 22px}
  svg.arc,svg.comp,svg.meter{display:block;width:100%;height:auto}
  svg.arc text,svg.comp text,svg.meter text{font-family:{{ T.MONO }}}
  .grid{stroke:#34291f;stroke-width:1}
  .ylab{font-size:9.5px;fill:{{ T.INK_SOFT }};text-anchor:end}
  .xlab{font-size:9.5px;fill:{{ T.INK_SOFT }};text-anchor:middle}
  .unit{font-size:10px;fill:{{ T.INK_SOFT }};letter-spacing:.08em;text-transform:uppercase}
  .vlab{font-size:10px;fill:{{ T.IVORY }};text-anchor:middle}
  .tlet{font-size:9px;text-anchor:middle;font-weight:700}
  .join{stroke-width:1.8;fill:none;opacity:.75}
  .dot:hover{r:6}
  .gapdot{fill:none;stroke:{{ T.GAP }};stroke-dasharray:3 3}
  .gaplab{font-size:9px;fill:{{ T.GAP }};text-anchor:middle;font-style:italic}
  .gaptrack{fill:none;stroke:#5a5344;stroke-dasharray:4 4}
  .seglab{font-size:10px;fill:{{ T.GROUND }};text-anchor:middle;font-weight:700}
  .caplab{font-size:10.5px;fill:{{ T.INK_SOFT }}}
  .composition-key{border:1px solid {{ T.EDGE }};border-radius:4px;background:{{ T.CASE }};padding:10px 13px;margin:-10px 0 24px;max-width:100%}
  .composition-key summary{cursor:pointer;font-family:{{ T.MONO }};font-size:10.5px;letter-spacing:.1em;text-transform:uppercase;color:{{ T.BRASS }};width:max-content;max-width:100%}
  .composition-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:8px 14px;margin-top:10px}
  .composition-decade{border-top:1px solid #34291f;padding-top:8px;font-size:12px;color:{{ T.INK_SOFT }}}
  .composition-decade>a{font-family:{{ T.MONO }};font-weight:700;text-decoration:none;margin-right:6px}
  .composition-decade b{color:#c9bfa4;font-weight:600}
  .cases{display:grid;grid-template-columns:repeat(auto-fill,minmax(310px,1fr));gap:14px}
  .placard{background:linear-gradient(178deg,{{ T.IVORY }},{{ T.IVORY_2 }});color:{{ T.INK }};border-radius:4px;padding:18px 18px 16px;border:1px solid #cbbfa1;box-shadow:0 18px 40px -22px #000;scroll-margin-top:20px}
   .placard:target{outline:3px solid {{ T.BRASS_LIT }};outline-offset:2px;box-shadow:0 0 34px -8px {{ T.BRASS_DEEP }}}
   .placard-overlay{display:none;position:fixed;inset:0;z-index:100;padding:5vh 10vw;overflow:auto;align-items:flex-start;justify-content:center}
    .placard-overlay:target{display:flex}
    .overlay-backdrop{position:fixed;inset:0;z-index:101;background:rgba(0,0,0,.62)}
    .placard-overlay .placard-card{position:relative;z-index:102;max-height:88vh;overflow:auto;max-width:760px;width:auto;margin-top:0;padding-right:54px}
    .overlay-close{position:absolute;top:8px;right:9px;z-index:103;font-size:25px;line-height:1;text-decoration:none;color:{{ T.BRASS_DEEP }};background:{{ T.IVORY_2 }};border:1px solid #cbbfa1;border-radius:3px;padding:2px 8px}
    .overlay-close:hover{color:{{ T.BRASS_LIT }}}
    .overlay-close:focus-visible{outline:3px solid {{ T.BRASS_LIT }};outline-offset:2px}
   .placard .ceyebrow{font-family:{{ T.MONO }};font-size:10px;letter-spacing:.16em;text-transform:uppercase;color:{{ T.BRASS_DEEP }}}
  .placard .cval{font-family:{{ T.SERIF }};font-size:19px;line-height:1.2;margin:7px 0 2px;color:{{ T.INK }};text-wrap:balance}
  .placard .clab{font-size:13.5px;color:#5f5540;margin:0 0 10px}
   .placard .cunit{font-family:{{ T.MONO }};font-size:10.5px;color:#8a7d61;margin:0 0 10px;overflow-wrap:anywhere;word-break:break-all}
  .tchip{font-family:{{ T.MONO }};font-size:10px;font-weight:700;color:#fff;border-radius:2px;padding:1px 5px;margin-left:7px;vertical-align:1px}
  .afford-box{margin:11px 0 4px;padding:9px 11px;background:#eadfc6;border-left:3px solid {{ T.BRASS_DEEP }};border-radius:3px}
  .afford-box .mk{font-family:{{ T.MONO }};font-size:9px;letter-spacing:.14em;text-transform:uppercase;color:{{ T.BRASS_DEEP }};display:block;margin-bottom:3px}
  .afford{font-family:{{ T.SERIF }};font-size:15px;color:#493b27;margin:2px 0;font-variant-numeric:tabular-nums}
  .afford-warning{font-size:11.5px;color:#6a5636;margin:6px 0 0;padding-top:6px;border-top:1px solid #d2c29e;line-height:1.4}
  .measured{margin:10px 0 0;padding:9px 11px;background:#e7dbc0;border-radius:3px;border-left:3px solid {{ T.BRASS_DEEP }}}
  .measured .mk{font-family:{{ T.MONO }};font-size:9.5px;letter-spacing:.16em;text-transform:uppercase;color:{{ T.BRASS_DEEP }};display:block;margin-bottom:2px}
  .measured .mv{font-size:12.5px;color:#453d2b;line-height:1.45}
  .placard details{margin-top:10px}
  .placard summary{cursor:pointer;font-family:{{ T.MONO }};font-size:10.5px;letter-spacing:.1em;text-transform:uppercase;color:{{ T.BRASS_DEEP }}}
  .drawer{font-size:12.5px;color:#554b38;margin-top:6px;line-height:1.5}
  .drawer a{color:{{ T.BRASS_DEEP }}}
  .gap-placard .cval{font-style:italic;color:#8a7f66}
  .statrow{display:grid;grid-template-columns:1fr auto;gap:2px 12px;align-items:baseline;padding:8px 0;border-top:1px solid #d5c9aa;text-decoration:none}
  .statrow .sk{font-size:12.5px;color:#4a4231;font-weight:600}
  .statrow .sv{font-family:{{ T.SERIF }};font-size:14px;color:{{ T.INK }};text-align:right;font-variant-numeric:tabular-nums}
  .legends{display:grid;grid-template-columns:1fr;gap:14px;margin-top:26px}
  @media(min-width:680px){.legends{grid-template-columns:1fr 1fr}}
  .leg{border:1px solid {{ T.EDGE }};border-radius:4px;padding:15px 17px;background:{{ T.CASE }}}
  .leg h4{font-family:{{ T.MONO }};font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:{{ T.BRASS }};margin:0 0 11px;font-weight:600}
  .tierrow{display:flex;align-items:center;gap:10px;margin:7px 0;font-size:13px}
  .tierrow .swatch{width:13px;height:13px;border-radius:2px;flex:none}
  .leg p{font-size:13px;color:{{ T.INK_SOFT }};margin:6px 0 0}
  .leg p b{color:{{ T.IVORY }}}
  .metric{margin:11px 0;padding-top:11px;border-top:1px solid #34291f}
  .metric:first-of-type{border-top:none;padding-top:0}
  .metric .mlab{font-size:12.5px;color:#c9bfa4;margin-bottom:6px;display:flex;justify-content:space-between;align-items:baseline}
  .metric .mlab em{font-style:normal;font-family:{{ T.MONO }};font-size:10px;color:{{ T.INK_SOFT }};letter-spacing:.05em}
  .traj{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
  .tnode{border:1px solid #34291f;border-radius:3px;padding:7px 9px 8px;background:#211d17;display:block;text-decoration:none;color:inherit}
  .tnode:hover{border-color:{{ T.BRASS_DIM }}}
  .tnode .td{font-family:{{ T.MONO }};font-size:9.5px;letter-spacing:.08em;color:{{ T.INK_SOFT }};text-transform:uppercase}
  .tnode .tv{font-family:{{ T.SERIF }};font-size:16px;color:{{ T.IVORY }};line-height:1.15;margin-top:2px;font-variant-numeric:tabular-nums}
  .tnode .tv.gapv{font-family:{{ T.SANS }};font-size:12px;font-style:italic;color:#9a8b6b}
  .tbar{height:5px;border-radius:3px;background:#3a3024;margin-top:7px;overflow:hidden}
  .tbar i{display:block;height:100%;background:linear-gradient(90deg,{{ T.BRASS_DEEP }},{{ T.BRASS }});border-radius:3px}
  .tbar.fall i{background:linear-gradient(90deg,#9a7b53,{{ T.COPPER }})}
  .flag{font-family:{{ T.MONO }};font-size:8.5px;letter-spacing:.04em;padding:0 4px;border-radius:2px}
  .flag.gapf{background:rgba(148,138,120,.18);color:#b3a891;border:1px solid #5a5344}
  .flag.tier{color:#20281f}
  .thesis{margin-top:14px;border:1px solid {{ T.EDGE }};border-radius:5px;background:{{ T.CASE }};padding:15px 17px}
  .thesis h4{font-family:{{ T.MONO }};font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:{{ T.BRASS }};margin:0 0 3px;font-weight:600}
  .thesis .tcap{font-size:12.5px;color:{{ T.INK_SOFT }};margin:0 0 13px}
  .pairgrid{display:grid;grid-template-columns:1fr 1fr;gap:14px;max-width:900px}
  .valcard{border:1px solid {{ T.EDGE }};border-radius:4px;background:{{ T.CASE }};padding:13px 15px;text-decoration:none;display:block}
  .valcard:hover{border-color:{{ T.BRASS_DIM }}}
  .valcard .td{font-family:{{ T.MONO }};font-size:10px;letter-spacing:.1em;color:{{ T.INK_SOFT }};text-transform:uppercase}
  .valcard .tv{font-family:{{ T.SERIF }};font-size:17px;color:{{ T.IVORY }};margin-top:3px;line-height:1.25}
  .valcard .tv.gapv{font-size:13px;font-style:italic;color:#9a8b6b}
  .pairtable{font-size:13px;border-collapse:collapse;margin-top:10px}
  .pairtable td,.pairtable th{border:1px solid #34291f;padding:4px 8px;text-align:center}
  .pairtable a{text-decoration:none;font-family:{{ T.MONO }};font-size:11px}
  .people{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px;margin:14px 0}
  .person-card{border:1px solid {{ T.EDGE }};border-radius:4px;background:{{ T.CASE }};padding:13px 15px}
  .person-card h5{font-family:{{ T.SERIF }};font-size:16px;margin:6px 0 8px;color:#f3ead7;font-weight:600}
  .person-card svg{display:block;margin:0 auto}
  .fig{fill:rgba(207,159,76,.10);stroke:{{ T.BRASS }};stroke-width:1.7;stroke-linejoin:round}
  .fig.head{fill:rgba(207,159,76,.14)}
  .prow{display:block;text-decoration:none;padding:6px 0;border-top:1px solid #34291f}
  .prow .sk{font-size:12px;color:#c9bfa4;display:block}
  .prow .sv{font-family:{{ T.SERIF }};font-size:13.5px;color:{{ T.IVORY }}}
  .houses{display:flex;gap:26px;align-items:flex-end;flex-wrap:wrap;margin:14px 0}
  .houses figure{margin:0;text-align:center}
  .houses figcaption{font-family:{{ T.MONO }};font-size:10px;letter-spacing:.08em;color:{{ T.INK_SOFT }};text-transform:uppercase;margin-top:6px}
  .houses a{text-decoration:none}
  .hline{stroke:{{ T.BRASS }};fill:none;stroke-width:1.7;stroke-linejoin:round}
  .hline.gaph{stroke:{{ T.GAP }};stroke-dasharray:4 4}
  footer{margin-top:34px;padding-top:16px;border-top:1px solid {{ T.EDGE }};font-size:12.5px;color:#6b6049;max-width:80ch}
  footer b{color:{{ T.INK_SOFT }}}
  @media(prefers-reduced-motion:reduce){*{transition:none !important}}
</style>
</head>
<body>
<div class="wrap">
<nav class="topnav">
  <a href="{{ root }}index.html">vitrine</a>
  <a href="{{ root }}corridors/index.html">corridors</a>
  <a href="{{ root }}affordability/index.html">affordability</a>
  <a href="{{ root }}walkthrough.html">walkthrough</a>
  <a href="{{ root }}methodology.html">methodology</a>
  <a href="{{ root }}bibliography.html">bibliography</a>
</nav>
{% block body %}{% endblock %}
</div>
</body>
</html>
"""

_TIER_LEGEND = """
<div class="legends">
  <div class="leg">
    <h4>Confidence &amp; flags</h4>
    {% for t, color in T.TIER_COLORS.items() %}
    <div class="tierrow"><span class="swatch" style="background:{{ color }}"></span> {{ t }} — {{ tier_names[t] }}</div>
    {% endfor %}
    <div class="tierrow"><span class="swatch" style="background:{{ T.GAP }};opacity:.5;border:1px dashed {{ T.GAP }}"></span> Gap — no reliable record; shown as the gap it is</div>
  </div>
  <div class="leg">
    <h4>Reading the museum</h4>
    <p><b>Every fact is behind glass</b>: its placard names the source, the year, who was measured, and how sure we are. Chart points and stage glyphs deep-link to their placards.</p>
    <p style="margin-top:8px"><b>Falling</b> metrics render in <b style="color:{{ T.COPPER }}">copper</b>, <b>rising</b> in <b style="color:{{ T.BRASS }}">brass</b>. Absent technology isn't drawn — a bare house says more than ghosts.</p>
  </div>
</div>
"""

_INDEX = (
    """{% extends "base" %}
{% block title %}vitrine — the museum lobby{% endblock %}
{% block body %}
<p class="eyebrow">vitrine · a museum of the median family</p>
<h1>The <em>median family's</em> century, behind glass</h1>
<p class="sub">A decade-by-decade museum of the median-income four-person family's lifestyle. Every fact carries its source card and confidence tier; where the record is silent, the museum shows the gap.</p>
<div class="plaque"><b>{{ disclaimer_title }}.</b> <span>{{ disclaimer }}</span></div>
<h2 class="case-title">The rooms</h2>
<p class="case-sub">One room per decade — the house cutaway, the six display cases, the specimen labels.</p>
<div class="decades"><span class="lab">Decade</span>
{% for room in rooms %}<a class="dbtn" href="rooms/{{ room.slug }}.html">{{ room.decade }}</a>
{% endfor %}</div>
<h2 class="case-title">The corridors</h2>
<p class="case-sub"><a href="corridors/index.html">Cross-decade arcs</a> — diffusion, affordability in hours of work, budget composition, life expectancy — and the pairwise comparison set.</p>
<h2 class="case-title">The walkthrough</h2>
<p class="case-sub"><a href="walkthrough.html">The transect</a> — the composite household at three stops across the century.</p>
"""
    + _TIER_LEGEND
    + "{% endblock %}\n"
)

_PLACARD = """
{% macro composition_details(rows) %}
{% if rows %}
<details class="composition-key">
  <summary>Inspect the folded categories</summary>
  <div class="composition-grid">
  {% for row in rows %}
    <div class="composition-decade">
      <a href="#{{ row.fact_id }}--modal">{{ row.decade }}</a>
      {% for segment in row.segments %}
      <div><b>{{ segment.slot }}</b>:
        {% for name, pct in segment.breakdown %}{{ name }} {{ pct|round(2) }}%{% if not loop.last %} + {% endif %}{% endfor %}
      </div>
      {% endfor %}
    </div>
  {% endfor %}
  </div>
</details>
{% endif %}
{% endmacro %}
{% macro _placard_body(fact, room, sources, assumptions, affordability, root, modal) %}
  <div class="ceyebrow">{{ panel_title(fact.panel) }} · {{ room.decade }}</div>
  <div class="cval">{{ fact.value }}<span class="tchip" style="background:{{ T.TIER_COLORS[fact.tier.value] }}" title="{{ tier_label(fact.tier) }}">{{ fact.tier.value }}</span></div>
  <p class="clab">{{ fact.label }}</p>
  <p class="cunit">{{ fact.unit }}</p>
  {% if fact.id in affordability %}{% set aff = affordability[fact.id] %}
  {% if aff.hours or aff.pct %}<div class="afford-box"><span class="mk">Computed affordability</span>
  {% if aff.hours %}<p class="afford">{{ aff.hours }}</p>{% endif %}
  {% if aff.pct %}<p class="afford">{{ aff.pct }}</p>{% endif %}
  {% if aff.hours_large %}<p class="afford-warning">Large ratio: inspect the wage population and anchor years in provenance before reading this as one household's timeline.</p>{% endif %}
  </div>{% endif %}
  {% endif %}
  {% set src = sources[fact.source] %}
  <div class="measured"><span class="mk">Measured</span><span class="mv">{{ src.population }}</span></div>
  <details>
    <summary>provenance</summary>
    <div class="drawer">
      <b>{{ src.title }}</b><br>
      {{ src.publisher }}, {{ src.year }} · <a href="{{ src.url }}">source</a><br>
      <em>Confidence:</em> {{ fact.tier.value }} — {{ tier_label(fact.tier) }}
      {% if fact.basis is not none %}<br><em>Basis:</em> {{ basis_label(fact.basis) }}{% endif %}
      {% if fact.id in affordability and affordability[fact.id].anchor_note %}<br><em>Affordability anchors:</em> {{ affordability[fact.id].anchor_note }}{% endif %}
      {% if fact.id in affordability and affordability[fact.id].measures %}<br><em>Denominators measure:</em> {{ affordability[fact.id].measures }}{% endif %}
      {% if fact.notes %}<br><em>Curator note:</em> {{ fact.notes }}{% endif %}
      {% if src.notes %}<br><em>Source note:</em> {{ src.notes }}{% endif %}
      {% for aid in fact.assumptions %}<br><em>Assumption:</em> <a href="{{ root }}methodology.html#{{ aid }}">{{ assumptions[aid].title }}</a>{% endfor %}
    </div>
  </details>
{% endmacro %}
{% macro placard(fact, room, sources, assumptions, affordability, root, inline=true) %}
{% if inline %}
<div class="placard{% if fact.value.strip().lower().startswith('no reliable record') %} gap-placard{% endif %}" id="{{ fact.id }}">
  {{ _placard_body(fact, room, sources, assumptions, affordability, root, modal=false) }}
</div>
{% endif %}
<div class="placard-overlay" id="{{ fact.id }}--modal" role="dialog" aria-modal="true" aria-label="{{ fact.label }}">
  <a href="#dismissed" class="overlay-backdrop" aria-label="Close placard"></a>
  <div class="placard placard-card{% if fact.value.strip().lower().startswith('no reliable record') %} gap-placard{% endif %}">
    <a href="#dismissed" class="overlay-close" aria-label="Close placard">&times;</a>
    {{ _placard_body(fact, room, sources, assumptions, affordability, root, modal=true) }}
  </div>
</div>
{% endmacro %}
{% macro derived_placard(cf, room, assumptions, root) %}
<div class="placard" id="{{ cf.id }}">
  <div class="ceyebrow">{{ panel_title(cf.panel) }} · {{ room.decade }} · computed</div>
  <div class="cval">{{ cf.value }}<span class="tchip" style="background:{{ T.TIER_COLORS[cf.tier.value] }}" title="{{ tier_label(cf.tier) }} (weakest input)">{{ cf.tier.value }}</span></div>
  <p class="clab">{{ cf.label }}</p>
  <p class="cunit">{{ cf.unit }}</p>
  <details>
    <summary>derivation</summary>
    <div class="drawer">
      <em>Computed by vitrine</em> ({{ cf.op.value }}) — never authored by hand:<br>
      <em>Numerator:</em> {{ cf.numerator.value }} — {{ cf.numerator.label }} <span class="tchip" style="background:{{ T.TIER_COLORS[cf.numerator.tier.value] }}">{{ cf.numerator.tier.value }}</span><br>
      {% if cf.op.value == "inflate" %}
      <em>Inflation series:</em> {{ cf.inflate_series }} ({{ cf.inflate_from_year }} → {{ cf.inflate_to_year }})<br>
      {% else %}
      <em>Denominator:</em> {{ cf.denominator.value }} — {{ cf.denominator.label }} <span class="tchip" style="background:{{ T.TIER_COLORS[cf.denominator.tier.value] }}">{{ cf.denominator.tier.value }}</span><br>
      {% endif %}
      <em>Confidence:</em> {{ cf.tier.value }} — {{ tier_label(cf.tier) }}, the weakest input tier
      {% if cf.notes %}<br><em>Curator note:</em> {{ cf.notes }}{% endif %}
      {% for aid in cf.assumptions %}<br><em>Assumption:</em> <a href="{{ root }}methodology.html#{{ aid }}">{{ assumptions[aid].title }}</a>{% endfor %}
    </div>
  </details>
</div>
{% endmacro %}
"""

_ROOM = (
    """{% extends "base" %}
{% from "macros" import placard, derived_placard %}
{% block title %}{{ room.country | upper }} · {{ room.decade }} — vitrine{% endblock %}
{% block body %}
<p class="eyebrow">vitrine · {{ room.country | upper }} · the {{ room.decade }}</p>
<h1>The <em>{{ room.decade }}</em> room</h1>
{% if room.data_as_of %}<p class="case-sub">Data as of {{ room.data_as_of }} (decade ongoing — each fact states its own data year).</p>{% endif %}
<div class="plaque"><b>{{ disclaimer_title }}.</b> <span>{{ disclaimer }}</span></div>
<div class="decades"><span class="lab">Decade</span>
{% for r in rooms %}<a class="dbtn{% if r.slug == room.slug %} on{% endif %}" href="{{ r.slug }}.html">{{ r.decade }}</a>
{% endfor %}</div>
{% if gap_banner %}<div class="gap-banner"><b>Structural gap</b>{{ gap_banner }}</div>{% endif %}
<div class="stage">{{ stage_svg }}</div>
<div class="stagehint">era-graded light · absent technology isn't drawn · every glyph opens its specimen label</div>
{% for panel, facts, computed in panels %}
<details open class="panel-group">
<summary class="case-title">{{ panel_title(panel) }}</summary>
{% if not facts and not computed %}<p class="case-sub"><em>Not yet curated.</em></p>{% else %}
<div class="cases">
{% for fact in facts %}{{ placard(fact, room, sources, assumptions, affordability, root) }}{% endfor %}
{% for cf in computed %}{{ derived_placard(cf, room, assumptions, root) }}{% endfor %}
</div>
{% endif %}
{% if panel.value == "work-buys" and facts %}<p class="case-sub"><a href="{{ root }}affordability/index.html">See this metric across all decades →</a></p>{% endif %}
</details>
{% endfor %}
"""
    + _TIER_LEGEND
    + "{% endblock %}\n"
)

_METHODOLOGY = """{% extends "base" %}
{% block title %}methodology — vitrine{% endblock %}
{% block body %}
<p class="eyebrow">vitrine · methodology</p>
<h1>Methodology &amp; assumptions</h1>
<p class="sub">Every methodological choice that would mislead if left implicit is written here once and linked from every placard it touches.</p>
<div class="cases" style="margin-top:22px">
{% for a in assumptions %}
<div class="placard" id="{{ a.id }}">
  <div class="ceyebrow">assumption</div>
  <div class="cval">{{ a.title }}</div>
  <p class="clab">{{ a.statement }}</p>
</div>
{% endfor %}
</div>
{% endblock %}
"""

_BIBLIOGRAPHY = """{% extends "base" %}
{% block title %}bibliography — vitrine{% endblock %}
{% block body %}
<p class="eyebrow">vitrine · bibliography</p>
<h1>Bibliography &mdash; <em>all sources</em></h1>
<p class="sub">Every fact in the museum traces to one of these {{ sources|length }} sources. Each entry names the publisher, publication year, the population actually measured, and a link to verify.</p>
<div class="cases" style="margin-top:22px">
{% for src in sources %}
<div class="placard" id="{{ src.id }}">
  <div class="ceyebrow">source</div>
  <div class="cval">{{ src.title }}</div>
  <p class="clab">{{ src.publisher }}{% if src.year %}, {{ src.year }}{% endif %}{% if src.short_cite %} &middot; <em>{{ src.short_cite }}</em>{% endif %}</p>
  <div class="measured"><span class="mk">Measured</span><span class="mv">{{ src.population }}</span></div>
  {% if src.url %}<p class="cunit"><a href="{{ src.url }}">{{ src.url }}</a></p>{% endif %}
  {% if src.notes %}<details><summary>source notes</summary><div class="drawer">{{ src.notes }}</div></details>{% endif %}
</div>
{% endfor %}
</div>
{% endblock %}
"""

_AFFORDABILITY = """{% extends "base" %}
{% block title %}affordability — vitrine{% endblock %}
{% block body %}
<p class="eyebrow">vitrine · the affordability view</p>
<h1>Affordability over <em>time</em></h1>
<p class="sub">Five ratios, each computed at build from the underlying series — never authored. A metric's line runs only across the years both its numerator and denominator cover; the gaps are the honest shape of the record. Copper bands mark NBER recessions.</p>
<div class="caveat">⚠ {{ disclaimer }}</div>
{% for item in sections %}
<h2 class="case-title" id="metric-{{ item.metric.slug }}">{{ item.metric.label }}</h2>
<p class="case-sub">{{ item.metric.unit }}</p>
{% for caveat in item.metric.caveats %}<div class="caveat">⚠ {{ caveat }}</div>{% endfor %}
{% if item.chart %}
<div class="chart-panel">{{ item.chart }}</div>
<p class="case-sub">{{ item.metric.caption }}</p>
{% else %}
<div class="chart-panel"><p class="case-sub gapv">{{ item.note }}</p></div>
{% endif %}
{% endfor %}
<footer class="case-sub" style="margin-top:28px;border-top:1px solid #34291f;padding-top:12px;max-width:80ch;overflow-wrap:break-word;word-break:break-all">
Recession bands: NBER Business Cycle Dating Committee chronology, transcribed from
<a href="{{ recession_url }}">{{ recession_url }}</a>. They are annotation, not facts.
Methodology: each ratio divides two structured series; values display in nominal
period units. See <a href="{{ root }}methodology.html">methodology</a> for the
assumption ledger entries behind the composites.
</footer>
{% endblock %}
"""

_CORRIDORS = (
    """{% extends "base" %}
{% from "macros" import placard, composition_details %}
{% block title %}corridors — vitrine{% endblock %}
{% block body %}
<p class="eyebrow">vitrine · the corridors</p>
<h1>The <em>corridors</em> — cross-decade arcs</h1>
<p class="sub">Where the charts live. Every point is a sourced fact and opens its specimen card here; a decade whose record is silent renders as the gap it is.</p>
<p class="case-sub"><a href="affordability/index.html">Affordability over time →</a> — five computed ratios (home, car, wages, food, real pay) across the full annual record.</p>
<h2 class="case-title">Detailed epoch comparisons</h2>
<p class="case-sub">Side-by-side fact families for each pair — the charts above cover the full century.</p>
<div class="decades">
{% for a, b in epochs %}<a class="dbtn" href="{{ a }}--{{ b }}.html">{{ a }} ↔ {{ b }}</a>
{% endfor %}</div>
{% for item in afford_sections %}
<h2 class="case-title">{{ item.label }} — in hours of work</h2>
<p class="case-sub">Price ÷ the room's wage anchor, computed at build. Tier letters carry the weakest input.</p>
{% for caveat in item.caveats %}<div class="caveat">⚠ {{ caveat }}</div>{% endfor %}
<div class="chart-panel">{{ item.chart }}</div>
{% endfor %}
<h2 class="case-title">Budget composition</h2>
<p class="case-sub">Share of household expenditure, fixed category palette, direct labels. Decades without a parseable breakdown are not drawn.</p>
{% for caveat in comp_caveats %}<div class="caveat">⚠ {{ caveat }}</div>{% endfor %}
<div class="chart-panel">
{% for row in comp_rows %}{{ row.bar }}{% endfor %}
</div>
{{ composition_details(comp_rows) }}
{% for arc in arc_sections %}
<h2 class="case-title" id="{{ arc.slug }}">{{ arc.label }}</h2>
<p class="case-sub">{{ arc.unit }}</p>
{% for caveat in arc.caveats %}<div class="caveat">⚠ {{ caveat }}</div>{% endfor %}<div class="chart-panel">{{ arc.chart }}</div>
{% endfor %}
<h2 class="case-title">The pairwise set</h2>
<p class="case-sub">Every decade against every other — each page shows only the fact families the measure guard certifies comparable for that pair.</p>
<table class="pairtable"><tr><th></th>{% for d in decades %}<th>{{ d[2:4] }}s</th>{% endfor %}</tr>
{% for a in decades %}<tr><th>{{ a[2:4] }}s</th>
{% for b in decades %}<td>{% if a < b %}<a href="{{ a }}--{{ b }}.html">↔</a>{% else %}·{% endif %}</td>{% endfor %}</tr>
{% endfor %}</table>
<div class="overlay-deck">
{% for ref in overlay_facts %}{{ placard(ref.fact, ref.room, sources, assumptions, affordability, root, inline=false) }}{% endfor %}
</div>
"""
    + _TIER_LEGEND
    + "{% endblock %}\n"
)

_PAIR = (
    """{% extends "base" %}
{% from "macros" import placard, composition_details %}
{% block title %}{{ a }} ↔ {{ b }} — vitrine corridors{% endblock %}
{% block body %}
<p class="eyebrow">vitrine · corridor · pairwise</p>
<h1>{{ a }} <em>↔</em> {{ b }}</h1>
<p class="sub">Fact families the measure guard certifies comparable for this pair. Everything else renders as the gap it is. Every value links to its placard.</p>
<div class="decades" style="margin-top:16px"><span class="lab">Rooms</span>
<a class="dbtn" href="../rooms/us-{{ a }}.html">{{ a }}</a>
<a class="dbtn" href="../rooms/us-{{ b }}.html">{{ b }}</a>
<a class="dbtn" href="index.html">all corridors</a></div>
{% for item in afford_sections %}
<h2 class="case-title">{{ item.label }} — affordability</h2>
{% for caveat in item.caveats %}<div class="caveat">⚠ {{ caveat }}</div>{% endfor %}
{% if item.rows %}
    <div class="pairgrid">
    {% for row in item.rows %}
    <a class="valcard" href="{{ row.overlay_href }}" data-fact-id="{{ row.fact_id }}">
      <div class="td">{{ row.decade }} · Tier {{ row.tier }}</div>
      <div class="tv">{{ row.text }}</div>
    </a>
    {% endfor %}
    </div>
{% else %}
<div class="pairgrid"><span class="valcard"><div class="td">{{ a }} ↔ {{ b }}</div><div class="tv gapv">not comparable for this pair — {{ item.gap_reason }}</div></span></div>
{% endif %}
{% endfor %}
{% if comp_rows %}
<h2 class="case-title">Budget composition</h2>
<div class="chart-panel">{% for row in comp_rows %}{{ row.bar }}{% endfor %}</div>
{{ composition_details(comp_rows) }}
{% endif %}
{% for fam in families %}
<h2 class="case-title">{{ fam.label }}</h2>
<p class="case-sub">{{ fam.unit }}</p>
{% for caveat in fam.caveats %}<div class="caveat">⚠ {{ caveat }}</div>{% endfor %}
<div class="pairgrid">
{% for cell in fam.cells %}
<a class="valcard" href="{{ cell.overlay_href }}" data-fact-id="{{ cell.fact_id }}">
  <div class="td">{{ cell.decade }} · Tier {{ cell.tier }}</div>
  <div class="tv{% if cell.gap %} gapv{% endif %}">{{ cell.text }}</div>
</a>
{% endfor %}
</div>
{% endfor %}
<div class="overlay-deck">
{% for ref in overlay_facts %}{{ placard(ref.fact, ref.room, sources, assumptions, affordability, root, inline=false) }}{% endfor %}
</div>
"""
    + "{% endblock %}\n"
)

_WALKTHROUGH = (
    """{% extends "base" %}
{% from "macros" import placard %}
{% block title %}the walkthrough — vitrine{% endblock %}
{% block body %}
<p class="eyebrow">vitrine · the walkthrough · {{ stops | join(" → ") }}</p>
<h1>Walk the <em>composite household</em></h1>
<p class="sub">The home and its paid-work, unpaid-work, and childhood records at three stops across the century. No invented family biography — only sourced facts, their tiers, and the gaps.</p>
<div class="plaque"><b>{{ disclaimer_title }}.</b> <span>{{ disclaimer }}</span></div>
{% for stop in stop_sections %}
<h2 class="case-title">The {{ stop.decade }} — <a href="rooms/us-{{ stop.decade }}.html">enter the room</a></h2>
<div class="stage">{{ stop.stage }}</div>
<div class="people">
{% for person in stop.people %}
<div class="person-card">
  <svg viewBox="-40 -60 80 130" width="64" height="104" role="img" aria-label="{{ person.name }}">{{ person.fig }}</svg>
  <h5>{{ person.name }}</h5>
  {% for row in person.rows %}
  <a class="prow" href="{{ row.href }}" data-fact-id="{{ row.fact_id }}">
    <span class="sk">{{ row.label }}</span>
    <span class="sv">{{ row.value }}<span class="tchip" style="background:{{ T.TIER_COLORS[row.tier] }}">{{ row.tier }}</span></span>
  </a>
  {% endfor %}
</div>
{% endfor %}
</div>
{% endfor %}
<div class="thesis">
<h4>The same measures, three stops</h4>
<p class="tcap">Each row is one measure across the transect. A silent record renders as a gap, never a guess.</p>
{% for m in metrics %}
<div class="metric">
  <div class="mlab"><span>{{ m.label }}</span><em>{{ m.unit }}</em></div>
  <div class="traj">
  {% for cell in m.cells %}
  {% if not cell.fact_id %}
  <span class="tnode">
    <div class="td">{{ cell.decade }}</div>
    <div class="tv gapv">not yet curated</div>
    <div style="margin-top:5px"><span class="flag gapf">gap</span></div>
  </span>
  {% else %}
  <a class="tnode" href="{{ cell.href }}" data-fact-id="{{ cell.fact_id }}">
    <div class="td">{{ cell.decade }}</div>
    {% if cell.gap %}<div class="tv gapv">{{ cell.text }}</div><div style="margin-top:5px"><span class="flag gapf">gap</span></div>
    {% else %}<div class="tv">{{ cell.text }}</div>
    <div class="tbar{% if m.falling %} fall{% endif %}"><i style="width:{{ cell.bar }}%"></i></div>
    <div style="margin-top:5px"><span class="flag tier" style="background:{{ T.TIER_COLORS[cell.tier] }}">Tier {{ cell.tier }}</span></div>
    {% endif %}
  </a>
  {% endif %}
  {% endfor %}
  </div>
</div>
{% endfor %}
</div>
<h2 class="case-title">The labour-hours meter</h2>
<p class="case-sub">Women's weekly unpaid home production, drawn to the data's shape — including its gaps.</p>
{% for caveat in meter_caveats %}<div class="caveat">⚠ {{ caveat }}</div>{% endfor %}
<div class="chart-panel">{{ meter }}</div>
<h2 class="case-title">The true-scale house</h2>
<p class="case-sub">The house is drawn to the sourced floor-area datum; a stop without one keeps the dashed reference outline.</p>
<div class="houses">
{% for h in houses %}
<figure>
{% if h.fact_id %}<a href="{{ h.href }}">{% endif %}
<svg viewBox="0 0 {{ h.w }} {{ h.hgt }}" width="{{ h.w }}" height="{{ h.hgt }}" role="img" aria-label="House scale, {{ h.decade }}">
  <path class="hline{% if h.gap %} gaph{% endif %}" {% if h.fact_id %}data-fact-id="{{ h.fact_id }}"{% endif %} d="{{ h.path }}"/>
</svg>
{% if h.fact_id %}</a>{% endif %}
<figcaption>{{ h.decade }} — {{ h.caption }}</figcaption>
</figure>
{% endfor %}
</div>
<p class="case-sub" style="margin-top:20px"><a href="affordability/index.html">How did we get here? →</a> — the affordability view traces five ratios across the full annual record.</p>
<div class="overlay-deck">
{% for ref in overlay_facts %}{{ placard(ref.fact, ref.room, sources, assumptions, affordability, root, inline=false) }}{% endfor %}
</div>
"""
    + "{% endblock %}\n"
)

# demo figure primitives (decoration; the stats beside them carry the facts)
_FIGS = {
    "father": '<path class="fig" d="M-12 -26 L12 -26 L8 44 L-8 44 Z"/><circle class="fig head" cx="0" cy="-37" r="9"/>',
    "mother": '<path class="fig" d="M-9 -25 L9 -25 L5 12 L15 44 L-15 44 L-5 12 Z"/><circle class="fig head" cx="0" cy="-36" r="8.5"/>',
    "children": '<g transform="translate(-11,4)"><path class="fig" d="M-7 -14 L7 -14 L5 28 L-5 28 Z"/><circle class="fig head" cx="0" cy="-23" r="6.5"/></g><g transform="translate(13,10) scale(0.82)"><path class="fig" d="M-7 -14 L7 -14 L5 28 L-5 28 Z"/><circle class="fig head" cx="0" cy="-23" r="6.5"/></g>',
}

_GAP_PREFIX = "no reliable record"


# ── projection helpers ────────────────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class _FactRef:
    room: Room
    fact: Fact


def _index_facts(corpus: Corpus) -> dict[str, _FactRef]:
    return {f.id: _FactRef(room, f) for room in corpus.rooms for f in room.facts}


def _placard_href(index: dict[str, _FactRef], fact_id: str, root: str) -> str:
    ref = index[fact_id]
    return f"{root}rooms/{ref.room.slug}.html#{fact_id}"


def _arc_points(
    index: dict[str, _FactRef], arc: curation.Arc, root: str
) -> tuple[svg.ArcPoint, ...]:
    points = []
    for decade in sorted(arc.fact_ids):
        fid = arc.fact_ids[decade]
        ref = index[fid]
        # Marker year: the fact's own price_year when it states one, else the
        # mid-decade year (1950s → 1955). A fact that pins a year sits at that
        # year on the annual axis; a decade-level fact sits at mid-decade while
        # the annual series line carries the year-by-year detail.
        year = ref.fact.price_year if ref.fact.price_year else int(decade[:4]) + 5
        points.append(
            svg.ArcPoint(
                decade=decade,
                fact_id=fid,
                href=_placard_href(index, fid, root),
                tier=ref.fact.tier.value,
                label=ref.fact.label,
                value=ref.fact.value,
                quantity=(
                    None if decade in arc.plot_gaps else ref.fact.quantity
                ),
                year=year,
            )
        )
    return tuple(points)


def _arc_chart_for(
    arc: curation.Arc,
    index: dict[str, _FactRef],
    series: dict[str, Series],
    root: str,
) -> str:
    """The arc chart for ``arc`` — annual series where one backs it, else decades."""
    points = _arc_points(index, arc, root)
    if arc.series_id and arc.series_id in series:
        s = series[arc.series_id]
        return svg.arc_chart_series(
            s.values, points, arc.unit, series_id=arc.series_id, falling=arc.falling
        )
    return svg.arc_chart(points, arc.unit, falling=arc.falling)


def _arc_group_chart_for(
    group: curation.ArcGroup,
    index: dict[str, _FactRef],
    root: str,
) -> str:
    """Render a curated group of related arcs on one honest shared scale."""
    colors = {"copper": tokens.COPPER, "brass": tokens.BRASS, "brass-deep": tokens.BRASS_DEEP}
    chart_series = tuple(
        svg.ArcSeries(
            label=label,
            color=colors[color_role],
            points=_arc_points(index, curation.ARC_BY_SLUG[arc_slug], root),
        )
        for arc_slug, label, color_role in group.members
    )
    return svg.multi_arc_chart(chart_series, group.unit)


def _fold_shares(
    fact: Fact, index: dict[str, _FactRef], root: str
) -> tuple[svg.ShareSegment, ...]:
    """Parse a composition fact and fold categories into the fixed palette slots."""
    parsed = svg.parse_shares(fact.value)
    href = _placard_href(index, fact.id, root)
    by_slot: dict[str, list[tuple[str, float]]] = {}
    for category, pct in parsed:
        slot = tokens.CATEGORY_SLOT.get(category, "other")
        by_slot.setdefault(slot, []).append((category, pct))
    segments = []
    for slot in tokens.COMPOSITION_ORDER:
        if slot not in by_slot:
            continue
        breakdown = by_slot[slot]
        names = [name for name, _pct in breakdown]
        total = sum(pct for _name, pct in breakdown)
        label = "other" if slot == "other" else " + ".join(names)
        segments.append(
            svg.ShareSegment(
                slot=slot,
                category=label,
                pct=round(total, 2),
                fact_id=fact.id,
                href=href,
                breakdown=tuple(breakdown),
            )
        )
    return tuple(segments)


def _build_stage(room: Room, index: dict[str, _FactRef], root: str) -> svg.Stage:
    artifacts: list[svg.StageArtifact] = []
    for artifact, (x, y) in svg.STAGE_POS.items():
        fid = curation.STAGE_DIFFUSION.get(artifact, {}).get(room.decade)
        kind = "diffusion"
        if fid is None:
            fid = curation.STAGE_STATS.get(artifact, {}).get(room.decade)
            kind = "stat"
        if fid is None:
            continue  # absent technology isn't drawn
        ref = index[fid]
        sym = symbols.symbol(artifact, room.decade, ref.fact.value)
        if sym is None:
            continue
        artifacts.append(
            svg.StageArtifact(
                artifact=artifact,
                glyph_svg=sym.svg,
                x=x,
                y=y,
                fact_id=fid,
                href=_placard_href(index, fid, root),
                label=ref.fact.label,
                value=ref.fact.value,
                quantity=ref.fact.quantity if kind == "diffusion" else None,
                kind=kind,
            )
        )

    zone_notes: list[svg.ZoneNote] = []
    comp_id = curation.COMPOSITIONS.get(room.decade)
    if comp_id is not None:
        segments = _fold_shares(index[comp_id].fact, index, root)
        for seg in segments:
            pos = curation.ZONE_NOTE_POS.get(seg.slot)
            if pos is None:
                continue
            zone_notes.append(
                svg.ZoneNote(
                    text=f"{seg.slot} {seg.pct:g}% of spending",
                    x=pos[0],
                    y=pos[1],
                    fact_id=seg.fact_id,
                    href=seg.href,
                )
            )
    else:
        food_arc = curation.ARC_BY_SLUG["food-share"]
        fid = food_arc.fact_ids.get(room.decade)
        if fid is not None and index[fid].fact.quantity is not None:
            fact = index[fid].fact
            x, y = curation.ZONE_NOTE_POS["food"]
            zone_notes.append(
                svg.ZoneNote(
                    text=f"food {fact.quantity:g}% of spending",
                    x=x,
                    y=y,
                    fact_id=fid,
                    href=_placard_href(index, fid, root),
                )
            )

    # home-scale: proportionally scale the house outline to the sourced
    # floor-area datum, so the visitor sees the home grow across decades.
    home_scale = 1.0
    size_fid = curation.HOME_SIZE_FACTS.get(room.decade)
    if size_fid is not None and size_fid in index:
        size_fact = index[size_fid].fact
        if size_fact.quantity is not None:
            # baseline: 1,525 sq ft (1970s, the earliest datum). Scale by
            # sqrt so the linear dimension changes proportionally.
            home_scale = max(0.6, min(1.35, (size_fact.quantity / 1525.0) ** 0.5))

    return svg.Stage(
        decade=room.decade,
        artifacts=tuple(artifacts),
        zone_notes=tuple(zone_notes),
        home_scale=home_scale,
    )


def _afford_fact_ids(corpus: Corpus, pattern: str) -> dict[str, str]:
    """Every decade whose room holds the priced fact — structured or not.

    Unstructured facts can't compute an hours axis; they render as gap slots,
    which is the record's actual shape (Plan 003 structured only the rooms
    with verified anchors).
    """
    ids = {}
    for room in corpus.rooms:
        fid = pattern.format(decade=room.decade)
        if any(f.id == fid for f in room.facts):
            ids[room.decade] = fid
    return ids


def _afford_arc_chart(
    comparison: Comparison,
    ids: dict[str, str],
    index: dict[str, _FactRef],
    root: str,
) -> str:
    """Project an affordability comparison onto the arc chart (hours axis).

    Decades whose fact exists but can't compute hours (no structured amount,
    or no wage anchor in the room) render as gap slots.
    """
    computed = {
        p.decade: p for p in comparison.points if p.afford.hours_to_afford is not None
    }
    points = []
    for decade in sorted(ids):
        fid = ids[decade]
        ref = index[fid]
        p = computed.get(decade)
        if p is None:
            points.append(
                svg.ArcPoint(
                    decade=decade,
                    fact_id=fid,
                    href=_placard_href(index, fid, root),
                    tier=ref.fact.tier.value,
                    label=ref.fact.label,
                    value=f"{ref.fact.value} — hours axis not computable (see the placard)",
                    quantity=None,
                )
            )
            continue
        hours = p.afford.hours_to_afford
        assert hours is not None
        points.append(
            svg.ArcPoint(
                decade=decade,
                fact_id=fid,
                href=_placard_href(index, fid, root),
                tier=p.afford.tier.value,
                label=ref.fact.label,
                value=f"{p.price_display} ≈ {hours:,.0f} hours of work",
                quantity=round(hours, 1),
            )
        )
    return svg.arc_chart(tuple(points), "hours of work to afford", falling=False)


# ── affordability display (unchanged mechanics from the V0 renderer) ─────────


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
    wage_measure: Measure | None = None
    income_measure: Measure | None = None
    if wage_fact is not None:
        src = corpus.sources.get(wage_fact.source)
        if src is not None:
            wage_pop = src.population
            wage_measure = src.measure
    if income_fact is not None:
        src = corpus.sources.get(income_fact.source)
        if src is not None:
            income_pop = src.population
            income_measure = src.measure

    for fact in room.facts:
        if fact.basis is not Basis.TOTAL or fact.amount_minor is None:
            continue
        aff = afford(
            fact,
            wage=wage_fact,
            income=income_fact,
            wage_population=wage_pop,
            income_population=income_pop,
            wage_measure=wage_measure,
            income_measure=income_measure,
        )

        hours_str = ""
        if aff.hours_to_afford is not None:
            hours_str = _format_hours(aff.hours_to_afford)
        pct_str = ""
        if aff.pct_of_income is not None:
            pct_str = _format_pct(aff.pct_of_income)

        measure_parts: list[str] = []
        if aff.hours_to_afford is not None and aff.hours_measure is not None:
            measure_parts.append(f"hours axis: {measure_label(aff.hours_measure)}")
        if aff.pct_of_income is not None and aff.pct_measure is not None:
            measure_parts.append(f"income axis: {measure_label(aff.pct_measure)}")

        display[fact.id] = {
            "hours": hours_str,
            "hours_large": "true"
            if aff.hours_to_afford is not None and aff.hours_to_afford > 2000
            else "",
            "pct": pct_str,
            "tier": aff.tier.value,
            "anchor_note": aff.anchor_note,
            "measures": "; ".join(measure_parts),
        }

    return display


def _panels_for(
    room: Room, computed: tuple[ComputedFact, ...]
) -> list[tuple[Panel, list[Fact], list[ComputedFact]]]:
    return [
        (
            panel,
            [f for f in room.facts if f.panel is panel],
            [c for c in computed if c.panel is panel],
        )
        for panel in Panel
    ]


# ── pairwise corridor projection ──────────────────────────────────────────────


@dataclass(frozen=True, slots=True)
class _Cell:
    decade: str
    fact_id: str
    href: str
    overlay_href: str
    tier: str
    text: str
    gap: bool


@dataclass(frozen=True, slots=True)
class _Family:
    label: str
    unit: str
    caveats: tuple[str, ...]
    cells: tuple[_Cell, ...]


@dataclass(frozen=True, slots=True)
class _AffordSection:
    label: str
    caveats: tuple[str, ...]
    rows: tuple[_Cell, ...]
    gap_reason: str = ""


def _pair_families(
    index: dict[str, _FactRef], a: str, b: str, root: str
) -> list[_Family]:
    families = []
    for arc in curation.ARCS:
        if a not in arc.fact_ids or b not in arc.fact_ids:
            continue
        cells = []
        for decade in (a, b):
            fid = arc.fact_ids[decade]
            fact = index[fid].fact
            gap = fact.quantity is None
            cells.append(
                _Cell(
                    decade=decade,
                    fact_id=fid,
                    href=_placard_href(index, fid, root),
                    overlay_href=f"#{fid}--modal",
                    tier=fact.tier.value,
                    text=fact.value if not gap else f"{fact.value} — see the placard",
                    gap=gap,
                )
            )
        families.append(
            _Family(label=arc.label, unit=arc.unit, caveats=arc.caveats, cells=tuple(cells))
        )
    return families


def _pair_afford(
    corpus: Corpus, index: dict[str, _FactRef], a: str, b: str, root: str
) -> list[_AffordSection]:
    sections = []
    for _slug, label, pattern in curation.AFFORD_ITEMS:
        ids = _afford_fact_ids(corpus, pattern)
        if a not in ids or b not in ids:
            continue
        comparison = compare_item(corpus, label, {a: ids[a], b: ids[b]})
        computable = [p for p in comparison.points if p.afford.hours_to_afford is not None]
        hours_measures = {p.afford.hours_measure for p in computable}
        # the measure guard: a mixed-concept axis renders as the gap it is
        if len(computable) < 2:
            reason = (
                "the hours axis needs a structured price and a verified wage "
                "anchor in both rooms — not yet curated for this pair"
            )
            sections.append(
                _AffordSection(label=label, caveats=comparison.caveats, rows=(), gap_reason=reason)
            )
            continue
        if len(hours_measures) != 1 or None in hours_measures:
            reason = next(
                (c for c in comparison.caveats if "mixes" in c),
                "the wage anchors do not share a measure",
            )
            sections.append(
                _AffordSection(label=label, caveats=comparison.caveats, rows=(), gap_reason=reason)
            )
            continue
        rows = []
        for p in computable:
            hours = p.afford.hours_to_afford
            assert hours is not None
            fid = ids[p.decade]
            rows.append(
                _Cell(
                    decade=p.decade,
                    fact_id=fid,
                    href=_placard_href(index, fid, root),
                    overlay_href=f"#{fid}--modal",
                    tier=p.afford.tier.value,
                    text=f"{p.price_display} ≈ {hours:,.0f} hours of work",
                    gap=False,
                )
            )
        sections.append(
            _AffordSection(label=label, caveats=comparison.caveats, rows=tuple(rows))
        )
    return sections


# ── the site ─────────────────────────────────────────────────────────────────


# ── affordability dashboard (Plan 011) ───────────────────────────────────────


def _series_numeric(s: Series) -> dict[int, float]:
    """A series's values in canonical units: dollars for monetary series
    (values_minor cents → dollars), raw floats otherwise (CPI index, hours)."""
    if s.values_minor:
        return {y: v / 100.0 for y, v in s.values_minor.items()}
    return dict(s.values)


def _resolve_metric(
    metric: curation.Metric,
    series: dict[str, Series],
) -> tuple[dict[int, float], str]:
    """Compute a metric's year→value map, or report why it can't render.

    Ratio mode: merge each numerator/denominator series, take the intersection
    of years, divide (numerator x scale). base_year re-scales to an index;
    percent multiplies by 100. Direct mode returns an empty map (the caller
    draws the arc's decade markers instead). Returns (values, note).
    """
    if metric.source_arc:
        return {}, ""  # direct mode — markers carry the data
    if not metric.numerator or not metric.denominator:
        return {}, "metric declares no numerator/denominator"
    if metric.base_year is not None and metric.percent:
        return {}, "metric sets both base_year and percent (mutually exclusive)"

    num: dict[int, float] = {}
    for sid in metric.numerator:
        if sid not in series:
            return {}, f"numerator series {sid!r} not found"
        new_vals = _series_numeric(series[sid])
        overlap = set(num) & set(new_vals)
        if overlap:
            return {}, (
                f"numerator series {sid!r} overlaps {sorted(overlap)} with an "
                f"earlier numerator series — merge is ambiguous"
            )
        num.update(new_vals)
    den: dict[int, float] = {}
    for sid in metric.denominator:
        if sid not in series:
            return {}, f"denominator series {sid!r} not found"
        den.update(_series_numeric(series[sid]))

    years = sorted(set(num) & set(den))
    if not years:
        return {}, "numerator and denominator share no years"
    ratios: dict[int, float] = {}
    for y in years:
        d = den[y]
        if d == 0:
            continue  # render the gap — never divide by zero
        ratios[y] = (num[y] * metric.numerator_scale) / d
    if not ratios:
        return {}, "denominator is zero for every coverage year"
    if metric.base_year is not None:
        if metric.base_year not in ratios:
            return {}, f"base_year {metric.base_year} not in coverage"
        base = ratios[metric.base_year]
        if base == 0:
            return {}, f"base_year {metric.base_year} ratio is zero — cannot index"
        ratios = {y: v / base * 100.0 for y, v in ratios.items()}
    elif metric.percent:
        ratios = {y: v * 100.0 for y, v in ratios.items()}
    return ratios, ""


def _metric_markers(
    metric: curation.Metric,
    index: dict[str, _FactRef],
    root: str,
) -> tuple[svg.MetricMarker, ...]:
    """Decade-fact markers for a direct-mode metric (e.g. food share)."""
    if not metric.source_arc:
        return ()
    arc = curation.ARC_BY_SLUG.get(metric.source_arc)
    if arc is None:
        return ()
    markers: list[svg.MetricMarker] = []
    for decade, fid in arc.fact_ids.items():
        if fid not in index:
            continue
        fact = index[fid].fact
        year = fact.price_year if fact.price_year else int(decade[:4]) + 5
        markers.append(
            svg.MetricMarker(
                year=year,
                fact_id=fid,
                href=_placard_href(index, fid, root),
                tier=fact.tier.value,
                label=fact.label,
                value=fact.value,
                quantity=fact.quantity,
            )
        )
    return tuple(markers)


def _load_recessions(path: Path) -> tuple[tuple[svg.Recession, ...], str]:
    """Load NBER recession bands + the source url from data/recessions.toml."""
    if not path.is_file():
        return (), ""
    with path.open("rb") as fh:
        data = tomllib.load(fh)
    bands: list[svg.Recession] = []
    for entry in data.get("recession", []):
        bands.append(svg.Recession(peak=_ym_to_year(entry["peak"]), trough=_ym_to_year(entry["trough"])))
    return tuple(bands), str(data.get("url", ""))


def _ym_to_year(ym: str) -> float:
    """'1973-11' → 1973 + (11-1)/12 ≈ 1973.83 (fractional year for band edges)."""
    year_s, month_s = ym.split("-")
    return int(year_s) + (int(month_s) - 1) / 12.0


def _render_affordability(
    corpus: Corpus,
    series: dict[str, Series],
    recessions: tuple[svg.Recession, ...],
    recession_url: str,
    index: dict[str, _FactRef],
    env: Environment,
    out_dir: Path,
) -> None:
    """Build the /affordability/ dashboard — five stacked metric charts."""
    sections: list[dict[str, object]] = []
    for metric in curation.AFFORDABILITY_METRICS:
        values, note = _resolve_metric(metric, series)
        markers = _metric_markers(metric, index, "../")
        # a section renders if it has annual values OR direct-mode markers
        if not values and not markers:
            sections.append(
                {"metric": metric, "chart": "", "note": note or "no data yet"}
            )
            continue
        chart = svg.affordability_chart(
            values,
            recessions,
            metric.unit,
            metric_slug=metric.slug,
            falling=metric.falling,
            markers=markers,
            zero_baseline=metric.zero_baseline,
        )
        sections.append({"metric": metric, "chart": Markup(chart), "note": note})
    (out_dir / "affordability").mkdir(exist_ok=True)
    (out_dir / "affordability" / "index.html").write_text(
        env.get_template("affordability").render(
            root="../",
            sections=sections,
            disclaimer=env.globals["disclaimer"],
            recession_url=recession_url,
        )
    )


def render_site(
    corpus: Corpus,
    out_dir: Path,
    series: dict[str, Series] | None = None,
    data_dir: Path | None = None,
) -> None:
    if series is None:
        series = {}
    env = Environment(
        loader=DictLoader(
            {
                "base": _BASE,
                "index": _INDEX,
                "room": _ROOM,
                "methodology": _METHODOLOGY,
                "bibliography": _BIBLIOGRAPHY,
                "affordability": _AFFORDABILITY,
                "corridors": _CORRIDORS,
                "pair": _PAIR,
                "walkthrough": _WALKTHROUGH,
                "macros": _PLACARD,
            }
        ),
        autoescape=select_autoescape(default=True),
    )
    env.globals["panel_title"] = panel_title
    env.globals["tier_label"] = tier_label
    env.globals["basis_label"] = basis_label
    env.globals["T"] = tokens
    env.globals["tier_names"] = {
        "A": "official statistical series",
        "B": "official microdata, computed by this project",
        "C": "reconstructed from period surveys",
        "D": "scholarly estimate",
    }

    disclaimer_entry = corpus.assumptions.get("composite-family")
    if disclaimer_entry is None:
        raise ValueError(
            "assumption ledger must contain 'composite-family' — "
            "the disclaimer renders on every room (charter rule)"
        )
    env.globals["disclaimer"] = disclaimer_entry.statement
    env.globals["disclaimer_title"] = disclaimer_entry.title

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "rooms").mkdir(exist_ok=True)
    (out_dir / "corridors").mkdir(exist_ok=True)

    index = _index_facts(corpus)
    rooms = sorted(corpus.rooms, key=lambda r: r.decade)
    decades = [room.decade for room in rooms]

    # lobby + methodology
    (out_dir / "index.html").write_text(
        env.get_template("index").render(root="", rooms=rooms)
    )
    (out_dir / "methodology.html").write_text(
        env.get_template("methodology").render(
            root="", assumptions=list(corpus.assumptions.values())
        )
    )
    (out_dir / "bibliography.html").write_text(
        env.get_template("bibliography").render(
            root="", sources=list(corpus.sources.values())
        )
    )

    # rooms
    rendered_ids: list[str] = []
    all_affordability: dict[str, dict[str, str]] = {}
    for room in rooms:
        computed = evaluate_room(room, series)
        room_afford = _affordability_for_room(corpus, room)
        all_affordability.update(room_afford)
        (out_dir / "rooms" / f"{room.slug}.html").write_text(
            env.get_template("room").render(
                root="../",
                room=room,
                rooms=rooms,
                stage_svg=Markup(svg.stage_svg(_build_stage(room, index, "../"), overlay_links=True)),
                panels=_panels_for(room, computed),
                sources=corpus.sources,
                assumptions=corpus.assumptions,
                affordability=room_afford,
                gap_banner=curation.ROOM_GAP_BANNERS.get(room.decade, ""),
            )
        )
        rendered_ids.extend(fact.id for fact in room.facts)
        rendered_ids.extend(cf.id for cf in computed)

    def _overlay_facts(fact_ids: tuple[str, ...]) -> tuple[_FactRef, ...]:
        """Unique fact refs for the popup placard layer on corridor pages."""
        seen: set[str] = set()
        refs: list[_FactRef] = []
        for fid in fact_ids:
            if fid in seen or fid not in index:
                continue
            seen.add(fid)
            refs.append(index[fid])
        return tuple(refs)

    # corridors index: the arc charts
    corridor_root = "../"
    arc_sections: list[dict[str, object]] = []
    rendered_groups: set[str] = set()
    for arc in curation.ARCS:
        group = curation.ARC_GROUP_BY_MEMBER.get(arc.slug)
        if group is not None:
            if group.slug in rendered_groups:
                continue
            rendered_groups.add(group.slug)
            arc_sections.append(
                {
                    "slug": group.slug,
                    "label": group.label,
                    "unit": group.unit,
                    "caveats": group.caveats,
                    "chart": Markup(_arc_group_chart_for(group, index, corridor_root)),
                }
            )
            continue
        arc_sections.append(
            {
                "slug": arc.slug,
                "label": arc.label,
                "unit": arc.unit,
                "caveats": arc.caveats,
                "chart": Markup(_arc_chart_for(arc, index, series, corridor_root)),
            }
        )
    afford_sections = []
    for _slug, label, pattern in curation.AFFORD_ITEMS:
        ids = _afford_fact_ids(corpus, pattern)
        if len(ids) < 2:
            continue
        comparison = compare_item(corpus, label, ids)
        caveats = curation.AFFORD_ITEM_CAVEATS.get(_slug, ()) + comparison.caveats
        afford_sections.append(
            {
                "label": label,
                "caveats": caveats,
                "chart": Markup(_afford_arc_chart(comparison, ids, index, corridor_root)),
            }
        )
    comp_rows: list[dict[str, object]] = []
    for decade in sorted(curation.COMPOSITIONS):
        fact_id = curation.COMPOSITIONS[decade]
        fact = index[fact_id].fact
        segments = _fold_shares(fact, index, corridor_root)
        if segments:
            comp_rows.append(
                {
                    "bar": Markup(svg.composition_bar(decade, segments)),
                    "decade": decade,
                    "fact_id": fact_id,
                    "segments": segments,
                }
            )
    comp_caveats = (
        "Survey populations differ across the century — 1901 wage-earner families "
        "vs modern consumer units; each bar links to its placard, which names who "
        "was measured.",
    )
    epochs = [("1900s", "1950s"), ("1950s", "2020s"), ("1900s", "2020s")]
    corridor_overlay_ids: list[str] = []
    for arc in curation.ARCS:
        corridor_overlay_ids.extend(arc.fact_ids.values())
    for _slug, _label, pattern in curation.AFFORD_ITEMS:
        corridor_overlay_ids.extend(_afford_fact_ids(corpus, pattern).values())
    corridor_overlay_ids.extend(curation.COMPOSITIONS.values())
    (out_dir / "corridors" / "index.html").write_text(
        env.get_template("corridors").render(
            root=corridor_root,
            decades=decades,
            epochs=epochs,
            arc_sections=arc_sections,
            afford_sections=afford_sections,
            comp_rows=comp_rows,
            comp_caveats=comp_caveats,
            sources=corpus.sources,
            assumptions=corpus.assumptions,
            affordability=all_affordability,
            overlay_facts=_overlay_facts(tuple(corridor_overlay_ids)),
        )
    )

    # the pairwise set (the three epoch pages are the featured pairs)
    for i, a in enumerate(decades):
        for b in decades[i + 1 :]:
            pair_comp_rows: list[dict[str, object]] = []
            pair_overlay_ids: list[str] = []
            if a in curation.COMPOSITIONS and b in curation.COMPOSITIONS:
                for decade in (a, b):
                    pair_overlay_ids.append(curation.COMPOSITIONS[decade])
                    fact = index[curation.COMPOSITIONS[decade]].fact
                    segments = _fold_shares(fact, index, corridor_root)
                    if segments:
                        pair_comp_rows.append(
                            {
                                "bar": Markup(svg.composition_bar(decade, segments)),
                                "decade": decade,
                                "fact_id": curation.COMPOSITIONS[decade],
                                "segments": segments,
                            }
                        )
            pair_families = _pair_families(index, a, b, corridor_root)
            for fam in pair_families:
                pair_overlay_ids.extend(cell.fact_id for cell in fam.cells)
            pair_afford_sections = _pair_afford(corpus, index, a, b, corridor_root)
            for section in pair_afford_sections:
                pair_overlay_ids.extend(row.fact_id for row in section.rows)
            (out_dir / "corridors" / f"{a}--{b}.html").write_text(
                env.get_template("pair").render(
                    root=corridor_root,
                    a=a,
                    b=b,
                    families=pair_families,
                    afford_sections=pair_afford_sections,
                    comp_rows=pair_comp_rows,
                    sources=corpus.sources,
                    assumptions=corpus.assumptions,
                    affordability=all_affordability,
                    overlay_facts=_overlay_facts(tuple(pair_overlay_ids)),
                )
            )

    # the walkthrough
    stop_sections = []
    walkthrough_overlay_ids: list[str] = []
    for decade in curation.WALKTHROUGH_STOPS:
        room = next(r for r in rooms if r.decade == decade)
        stage = _build_stage(room, index, "")
        walkthrough_overlay_ids.extend(a.fact_id for a in stage.artifacts)
        walkthrough_overlay_ids.extend(n.fact_id for n in stage.zone_notes)
        people = []
        # The source series are sex- and activity-specific, not observations
        # of one literal father and mother. Lens labels keep the composite
        # honest and avoid assigning a family structure the data never states.
        for figure, name in (
            ("father", "The paid-work record"),
            ("mother", "The unpaid-work record"),
            ("children", "The childhood record"),
        ):
            rows = []
            for fid in curation.WALKTHROUGH_PEOPLE[figure].get(decade, ()):
                fact = index[fid].fact
                walkthrough_overlay_ids.append(fid)
                rows.append(
                    {
                        "fact_id": fid,
                        "href": f"#{fid}--modal",
                        "label": fact.label,
                        "value": fact.value if len(fact.value) <= 90 else fact.value[:87] + "…",
                        "tier": fact.tier.value,
                    }
                )
            people.append({"name": name, "fig": Markup(_FIGS[figure]), "rows": rows})
        stop_sections.append(
            {
                "decade": decade,
                "stage": Markup(svg.stage_svg(stage, overlay_links=True)),
                "people": people,
            }
        )

    metrics = []
    for slug in curation.WALKTHROUGH_METRICS:
        arc = curation.ARC_BY_SLUG[slug]
        stop_facts = [
            (d, arc.fact_ids.get(d)) for d in curation.WALKTHROUGH_STOPS
        ]
        quantities = [
            q
            for _, mfid in stop_facts
            if mfid is not None and (q := index[mfid].fact.quantity) is not None
        ]
        q_max = max(quantities) if quantities else 1.0
        cells = []
        for decade, mfid in stop_facts:
            if mfid is None:
                # no fact at all for this stop — an uncurated slot, not a mark
                cells.append(
                    {"decade": decade, "fact_id": "", "href": "", "tier": "", "gap": True,
                     "text": "not yet curated", "bar": 0}
                )
                continue
            fact = index[mfid].fact
            walkthrough_overlay_ids.append(mfid)
            cells.append(
                {
                    "decade": decade,
                    "fact_id": mfid,
                    "href": f"#{mfid}--modal",
                    "tier": fact.tier.value,
                    "gap": fact.quantity is None,
                    "text": "see the placard" if fact.quantity is None else f"{fact.quantity:g}",
                    "bar": 0
                    if fact.quantity is None or q_max == 0
                    else round(100 * fact.quantity / q_max),
                }
            )
        metrics.append(
            {"label": arc.label, "unit": arc.unit, "falling": arc.falling, "cells": cells}
        )

    women_arc = curation.ARC_BY_SLUG["home-production-women"]
    meter_bars = []
    for decade in sorted(women_arc.fact_ids):
        fid = women_arc.fact_ids[decade]
        fact = index[fid].fact
        walkthrough_overlay_ids.append(fid)
        meter_bars.append(
            svg.MeterBar(
                decade=decade,
                fact_id=fid,
                href=_placard_href(index, fid, ""),
                tier=fact.tier.value,
                label=fact.label,
                value=fact.value,
                quantity=(
                    None if decade in women_arc.plot_gaps else fact.quantity
                ),
                note=(
                    "different unit and concept — see the placard"
                    if decade in women_arc.plot_gaps
                    else ""
                ),
            )
        )
    meter = Markup(svg.hours_meter(tuple(meter_bars), women_arc.unit, overlay_links=True))

    houses = []
    sourced_area: float | None = None
    for decade in curation.WALKTHROUGH_STOPS:
        area_fid = curation.WALKTHROUGH_FLOOR_AREA.get(decade)
        if area_fid is not None and index[area_fid].fact.quantity is not None:
            sourced_area = index[area_fid].fact.quantity
    for decade in curation.WALKTHROUGH_STOPS:
        area_fid = curation.WALKTHROUGH_FLOOR_AREA.get(decade)
        area_fact = index[area_fid].fact if area_fid is not None else None
        if area_fact is not None and area_fact.quantity is not None and sourced_area:
            scale = (area_fact.quantity / sourced_area) ** 0.5
            gap = False
            caption = f"{area_fact.quantity:,.0f} sq ft (sourced)"
        else:
            scale = 0.75  # reference outline only — carries no datum
            gap = True
            caption = (
                "rooms counted, floor area not measured"
                if area_fact is not None
                else "floor area not yet curated"
            )
        w = round(150 * scale)
        hgt = round(120 * scale)
        houses.append(
            {
                "decade": decade,
                "fact_id": area_fid if area_fact is not None else "",
                "href": (
                    f"#{area_fid}--modal"
                    if area_fid is not None and area_fact is not None
                    else ""
                ),
                "gap": gap,
                "w": w,
                "hgt": hgt,
                "path": (
                    f"M{w * 0.08:.0f} {hgt * 0.45:.0f} L{w * 0.5:.0f} {hgt * 0.08:.0f} "
                    f"L{w * 0.92:.0f} {hgt * 0.45:.0f} M{w * 0.15:.0f} {hgt * 0.45:.0f} "
                    f"V{hgt * 0.92:.0f} H{w * 0.85:.0f} V{hgt * 0.45:.0f}"
                ),
                "caption": caption,
            }
        )
        if area_fid is not None and area_fact is not None:
            walkthrough_overlay_ids.append(area_fid)

    (out_dir / "walkthrough.html").write_text(
        env.get_template("walkthrough").render(
            root="",
            stops=list(curation.WALKTHROUGH_STOPS),
            stop_sections=stop_sections,
            metrics=metrics,
            meter=meter,
            meter_caveats=women_arc.caveats,
            houses=houses,
            sources=corpus.sources,
            assumptions=corpus.assumptions,
            affordability=all_affordability,
            overlay_facts=_overlay_facts(tuple(walkthrough_overlay_ids)),
        )
    )

    # the affordability dashboard (Plan 011)
    recessions, recession_url = _load_recessions((data_dir or Path("data")) / "recessions.toml")
    _render_affordability(corpus, series, recessions, recession_url, index, env, out_dir)

    (out_dir / "facts-manifest.txt").write_text("\n".join(rendered_ids) + "\n")
