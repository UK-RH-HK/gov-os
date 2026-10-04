"""Fixtures for the W1-37 acceptance tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w1_37_support as support  # noqa: E402


def _load(loader):
    try:
        return loader()
    except support.Missing as exc:
        reason = str(exc)
    pytest.fail(reason, pytrace=False)


@pytest.fixture(scope="session")
def vendor():
    """The files under ``template/governance/kernel/vendor/superpowers/`` (DEC-194), relative to that folder."""
    return _load(support.load_vendor)


@pytest.fixture(scope="session")
def copy():
    """The files under ``template/governance/kernel/skills/superpowers/`` (DEC-244), relative to that folder."""
    return _load(support.load_copy)


@pytest.fixture(scope="session")
def record(copy):
    """The record file of DEC-246, parsed."""
    return _load(support.load_record)
