"""Fixtures for the W1-02 acceptance tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w1_02_support as support  # noqa: E402


@pytest.fixture(scope="session")
def hook():
    """The guard's PreToolUse hook script in the kernel template."""
    try:
        return support.hook_entry()
    except support.HookMissing as exc:
        reason = str(exc)
    pytest.fail(reason, pytrace=False)


@pytest.fixture()
def sandbox(tmp_path):
    """Empty ``HOME`` and bytecode-cache directories for the hook process."""
    home = tmp_path / "home"
    pycache = tmp_path / "pycache"
    home.mkdir()
    pycache.mkdir()
    return home, pycache


@pytest.fixture()
def project(hook, tmp_path):
    """A committed project with one engineer ticket in progress."""
    return support.make_project(
        tmp_path / "project",
        {f"{support.TICKET_ID}.md": support.ticket_text()},
    )


@pytest.fixture()
def call(sandbox):
    """``call(project, tool_name, tool_input)`` runs the hook once, with no role declared."""
    home, pycache = sandbox

    def _call(project, tool_name, tool_input):
        return support.run_hook(project, tool_name, tool_input, home, pycache)

    return _call
