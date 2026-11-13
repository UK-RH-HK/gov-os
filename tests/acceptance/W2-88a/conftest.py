"""Fixtures for the W2-88a acceptance tests (the adopt skill's kernel text)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "local_only: starts a real model or service on this machine; not for CI (DEC-232)")
