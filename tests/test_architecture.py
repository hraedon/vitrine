"""Import-boundary test: the core never imports the [site] extra or jinja2."""

import subprocess
import sys


def test_core_does_not_import_site_or_jinja2() -> None:
    # Explicit module list (not just what cli happens to pull in): a new
    # core module not reachable from cli must not silently lose protection.
    core_modules = (
        "vitrine.cli, vitrine.check, vitrine.loader, vitrine.model, "
        "vitrine.affordability, vitrine.compare, vitrine.series, "
        "vitrine.derive, vitrine.export, vitrine.publish, vitrine.money, vitrine.audit"
    )
    code = (
        "import sys\n"
        f"import {core_modules}\n"
        "bad = [m for m in sys.modules if m in ('jinja2', 'openpyxl') "
        "or m.startswith('vitrine.site')]\n"
        "sys.exit(1 if bad else 0)\n"
    )
    result = subprocess.run([sys.executable, "-c", code], capture_output=True)
    assert result.returncode == 0, "core imports pulled in jinja2 or vitrine.site"
