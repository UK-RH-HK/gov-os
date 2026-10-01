"""Fixtures for the W1-01 acceptance tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w1_01_support as support  # noqa: E402


@pytest.fixture(scope="session")
def repo_root():
    return support.REPO_ROOT


@pytest.fixture(scope="session")
def deny_rules(repo_root):
    """``permissions.deny`` of the repository's ``.claude/settings.json``."""
    path = repo_root / support.SETTINGS_REL
    assert path.is_file(), f"{support.SETTINGS_REL} does not exist"
    try:
        return support.deny_rules_from_text(path.read_text(encoding="utf-8"))
    except ValueError as exc:
        pytest.fail(f"{support.SETTINGS_REL} is not valid JSON: {exc}")


@pytest.fixture(scope="session")
def bootstrap_text(repo_root):
    """Text of ``governance/project/bootstrap.md``, the record W1-01 writes."""
    path = repo_root / support.BOOTSTRAP_REL
    assert path.is_file(), f"{support.BOOTSTRAP_REL} does not exist"
    text = path.read_text(encoding="utf-8")
    assert text.strip(), f"{support.BOOTSTRAP_REL} is empty"
    return text


@pytest.fixture(scope="session")
def w1_05_landed(repo_root):
    return support.w1_05_has_landed(repo_root)


@pytest.fixture()
def interim(w1_05_landed):
    """Skip a check that only holds until W1-05 lands (DEC-084)."""
    if w1_05_landed:
        pytest.skip("W1-05 is closed: the interim guardrail is retired (DEC-084)")
