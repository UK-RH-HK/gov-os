"""Fixtures for the W2-198 acceptance tests: a fixture HOME per test, under its ``tmp_path``."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_198_support as support  # noqa: E402


@pytest.fixture
def home(tmp_path):
    return support.make_home(tmp_path)


@pytest.fixture
def env(home):
    return support.make_env(home)
