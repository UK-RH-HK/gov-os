"""Fixtures for the W2-188 acceptance tests (the adopt skill's step 6 and the practice record)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "local_only: starts a real model or service on this machine; not for CI (DEC-232)")
