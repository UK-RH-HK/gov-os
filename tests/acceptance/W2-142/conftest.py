"""The W2-142 acceptance tests import their helpers from this folder (README); no fixtures, no stand-ins."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
