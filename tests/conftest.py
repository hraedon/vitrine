"""Test-path setup: make scripts/ importable for direct script tests.

``scripts/`` is not a Python package, but its modules are unit-tested
directly (``test_link_check.py``, ``test_docs_sync.py`` imports the vitrine
package instead). Adding the directory to ``sys.path`` makes plain
``import link_check`` resolve; the identifier-gate tests keep their own
importlib loading because they register the module explicitly.
"""

import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "scripts"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))
