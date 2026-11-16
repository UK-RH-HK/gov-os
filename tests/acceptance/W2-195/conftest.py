"""The W2-195 acceptance tests import their helpers from this folder (README); each case builds its own fixture."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
