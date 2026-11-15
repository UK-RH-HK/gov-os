"""Fixtures for the W2-111 reopen's acceptance cases (DEC-1184 (3))."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_111_support as support  # noqa: E402


@pytest.fixture(scope="session")
def hook():
    """The product guard's PreToolUse hook in the kernel template."""
    try:
        return support.guard.hook_entry()
    except support.guard.HookMissing as exc:
        reason = str(exc)
    pytest.fail(reason, pytrace=False)


@pytest.fixture(scope="session")
def bash_world(hook, tmp_path_factory):
    """W1-02's fixture project, the engineer on its ticket; one for the run (the cases only ask for decisions)."""
    return support.bash_world(tmp_path_factory.mktemp("w2-111-bash"))


@pytest.fixture(scope="session")
def trees_world(hook, tmp_path_factory):
    """The planted repository with 150 worktrees registered; built once for the run."""
    return support.trees_world(tmp_path_factory.mktemp("w2-111-trees"))
