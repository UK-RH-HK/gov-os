"""Fixtures for the W2-62 acceptance tests (the session-start hook's resume in full)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_62_support as support  # noqa: E402


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "local_only: starts a real Claude Code session on this machine; not for CI (DEC-232)")


@pytest.fixture(scope="session")
def code_under_test():
    """The hook that runs is this checkout's (DEC-732)."""
    assert support.SESSIONSTART.is_file(), f"no session-start hook at {support.SESSIONSTART}"
    assert (support.SRC / "gov" / "__init__.py").is_file(), f"no gov package under {support.SRC}"
    return support.SESSIONSTART


@pytest.fixture()
def sandbox(tmp_path, code_under_test):
    return support.make_sandbox(tmp_path / "sandbox")


@pytest.fixture()
def project(tmp_path, code_under_test):
    """A main tree whose roster names the stand-in prompt ``governance/project/prompts/w2-orchestrator.md``."""
    return support.make_project(tmp_path / "repo", support.roster(support.DEFAULT_PROMPT))


@pytest.fixture()
def worktree(project, tmp_path):
    """A linked worktree of ``project``, as a ticket lead works in."""
    return support.add_worktree(project, tmp_path / "worktrees" / "lead-fixture")
