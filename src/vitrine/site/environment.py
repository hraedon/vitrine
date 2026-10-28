"""Jinja2 environment construction — PackageLoader, globals, render helper."""

from __future__ import annotations

from typing import assert_never

from jinja2 import Environment, PackageLoader, select_autoescape

from vitrine.model import (
    AuditOperation,
    AuditRounding,
    AuditTarget,
    Panel,
    basis_label,
    panel_title,
    tier_label,
)
from vitrine.site import tokens


def audit_target_label(target: AuditTarget) -> str:
    match target:
        case AuditTarget.QUANTITY:
            return "Calculation of the headline numeric value"
        case AuditTarget.AMOUNT_MINOR:
            return "Calculation of the monetary amount"
        case _ as unreachable:
            assert_never(unreachable)


def audit_operation_label(operation: AuditOperation) -> str:
    match operation:
        case AuditOperation.MEAN:
            return "Arithmetic mean"
        case AuditOperation.PCT_OF:
            return "Percentage of the denominator"
        case _ as unreachable:
            assert_never(unreachable)


def audit_rounding_label(rounding: AuditRounding) -> str:
    match rounding:
        case AuditRounding.HALF_EVEN:
            return "to the nearest even digit"
        case AuditRounding.HALF_UP:
            return "away from zero"
        case _ as unreachable:
            assert_never(unreachable)


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
    env.globals["panels"] = tuple(Panel)
    env.globals["panel_title"] = panel_title
    env.globals["tier_label"] = tier_label
    env.globals["basis_label"] = basis_label
    env.globals["audit_target_label"] = audit_target_label
    env.globals["audit_operation_label"] = audit_operation_label
    env.globals["audit_rounding_label"] = audit_rounding_label
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
