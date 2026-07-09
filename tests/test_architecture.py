"""Import-boundary test: the core never imports the [site] extra or jinja2."""

import subprocess
import sys


def test_core_does_not_import_site_or_jinja2() -> None:
    code = (
        "import sys\n"
        "import vitrine.cli, vitrine.check, vitrine.loader, vitrine.model, "
        "vitrine.affordability, vitrine.compare, vitrine.series\n"
        "bad = [m for m in sys.modules if m == 'jinja2' or m.startswith('vitrine.site')]\n"
        "sys.exit(1 if bad else 0)\n"
    )
    result = subprocess.run([sys.executable, "-c", code], capture_output=True)
    assert result.returncode == 0, "core imports pulled in jinja2 or vitrine.site"
