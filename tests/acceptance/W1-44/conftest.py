"""Fixtures for the W1-44 acceptance tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
sys.path.insert(0, str(_HERE.parent / "W1-21"))

import w1_21_support as support  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[3]
LESSONS_DIR = REPO_ROOT / "docs" / "lessons"


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "needs(*names): what the case needs on this machine (gitleaks, sqlite_vec); "
        "it skips, with the reason, when one is absent",
    )


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    names = [name for marker in item.iter_markers("needs") for name in marker.args]
    reasons = support.lacking(*names)
    if reasons:
        pytest.skip("; ".join(reasons))


@pytest.fixture(scope="session")
def lessons():
    """All lesson files in docs/lessons/ as (path, frontmatter, body) triples.

    Fails when no lesson records exist — expected before implementation."""
    files = sorted(LESSONS_DIR.glob("*.md"))
    assert files, "no lesson records exist in docs/lessons/"
    result = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---\n") or "\n---\n" not in text[4:]:
            pytest.fail(f"{path.name} has no YAML frontmatter")
        raw = text[4:text.index("\n---\n", 4)]
        front = yaml.safe_load(raw)
        body = text[text.index("\n---\n", 4) + 5:]
        result.append((path, front, body))
    return result
