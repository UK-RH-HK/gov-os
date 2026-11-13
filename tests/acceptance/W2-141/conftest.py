"""Fixtures for the W2-141 acceptance tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_141_support as support  # noqa: E402


@pytest.fixture(scope="module")
def guard(tmp_path_factory):
    """decide() over the planted project, with a temporary HOME, GOV_ROLE and GOV_TICKET cleared (read-only cases)."""
    project = support.make_project(tmp_path_factory.mktemp("w2-141"))
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("HOME", str(project.home))
        for name in ("GOV_ROLE", "GOV_TICKET", "CLAUDE_PROJECT_DIR"):
            mp.delenv(name, raising=False)
        yield support.Guard(project, support.load_decide())
