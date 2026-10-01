"""Fixtures for the W1-05 acceptance tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w1_05_support as support  # noqa: E402

NOT_SWITCHED_OVER = (
    "the switch-over has not happened: .claude/settings.json does not register a PreToolUse hook for "
    "Edit, Write, NotebookEdit and Bash and a PostToolUse hook for Bash"
)


@pytest.fixture(scope="session")
def settings():
    """``.claude/settings.json`` of this repository."""
    return support.load_settings()


@pytest.fixture(scope="session")
def switched_over(settings):
    """The settings file, once it wires the guard and the containment check."""
    if not support.is_switched_over(settings):
        pytest.fail(NOT_SWITCHED_OVER, pytrace=False)
    return settings


@pytest.fixture(scope="session")
def sandbox(tmp_path_factory):
    return support.make_sandbox(tmp_path_factory.mktemp("w1-05-sandbox"))


@pytest.fixture(scope="session")
def live(switched_over, tmp_path_factory):
    """A committed copy of the working tree. Tests that only ask for decisions share it."""
    return support.copy_working_tree(tmp_path_factory.mktemp("w1-05-live") / "repo")


@pytest.fixture()
def scratch_copy(switched_over, tmp_path):
    """A committed copy of the working tree for one test that changes files."""
    return support.copy_working_tree(tmp_path / "repo")


@pytest.fixture()
def decide(switched_over, sandbox):
    """``decide(project, tool_name, tool_input, role, ticket, subagent=None, permission_mode="default")``."""

    def _decide(project, tool_name, tool_input, role=None, ticket=None, subagent=None, permission_mode="default"):
        return support.pre_tool_use(project, switched_over, sandbox, tool_name, tool_input, role=role,
                                    ticket=ticket, subagent=subagent, permission_mode=permission_mode)

    return _decide
