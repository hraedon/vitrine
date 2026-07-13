"""Jinja2 environment construction — PackageLoader, globals, render helper."""

from __future__ import annotations

from jinja2 import Environment, PackageLoader, select_autoescape

from vitrine.model import basis_label, panel_title, tier_label
from vitrine.site import tokens


def build_environment(disclaimer: str, disclaimer_title: str) -> Environment:
    """Construct the production Jinja environment with all globals wired.

    Templates resolve off ``PackageLoader("vitrine.site", "templates")`` so
    page templates live as files under ``site/templates/`` and reference one
    another by filename (``{% extends "base.html" %}``,
    ``{% from "macros/placards.html" import ... %}``). Autoescape defaults on, matching
    the prior ``DictLoader`` configuration; the rendered output is unchanged.

    ``disclaimer`` / ``disclaimer_title`` are the composite-family assumption's
    resolved text — the charter requires the disclaimer on every room, so the
    caller (which owns corpus access) raises ``ValueError`` before calling if
    the assumption is absent.
    """
    env = Environment(
        loader=PackageLoader("vitrine.site", "templates"),
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
    env.globals["disclaimer"] = disclaimer
    env.globals["disclaimer_title"] = disclaimer_title
    return env
