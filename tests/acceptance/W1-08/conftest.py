"""Fixtures for the W1-08 acceptance tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w1_08_support as support  # noqa: E402


def pytest_configure(config):
    config.addinivalue_line("markers", "local_only: needs check-jsonschema installed on this machine; not for CI")


@pytest.fixture
def check(tmp_path):
    """Validates a document against a schema file with check-jsonschema; skipped when the tool is absent."""
    if support.validator_path() is None:
        pytest.skip(f"{support.VALIDATOR} is not installed on this machine")
    return support.Checker(tmp_path)
