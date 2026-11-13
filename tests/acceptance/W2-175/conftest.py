"""The W2-175 acceptance tests import their helpers from this folder and W2-128's statement reader (README)."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
for folder in (HERE, HERE.parent / "W2-128"):
    if str(folder) not in sys.path:
        sys.path.insert(0, str(folder))
