"""W2-137's acceptance tests: the tree under test and the support module on the path.

The tests use the tree ``PYTHONPATH`` names; without one, this worktree's own ``src``. No fixture starts a process,
a socket, a model or a GPU.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
if importlib.util.find_spec("gov") is None:
    sys.path.insert(0, str(HERE.parents[2] / "src"))
