"""Fixtures for the W1-04 acceptance tests."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w1_04_support as support  # noqa: E402

CANARY = "pip install requests"


@pytest.fixture(scope="session")
def hook():
    """The guard's PreToolUse hook script in the kernel template."""
    try:
        return support.hook_entry()
    except support.HookMissing as exc:
        reason = str(exc)
    pytest.fail(reason, pytrace=False)


@pytest.fixture(scope="session")
def install_rule(hook, tmp_path_factory):
    """The install rule is in the guard: the plainest install by the orchestrator gets ``ask``.

    Every test of the rule depends on this fixture. Until the rule exists they
    all stop here, with one reason, whatever each of them would assert.
    """
    base = tmp_path_factory.mktemp("install-rule")
    project = support.make_project(base / "project")
    sandbox = support.make_sandbox(base / "sandbox")
    result = support.run_hook(project, "Bash", support.bash_input(CANARY), sandbox,
                              role=support.ORCHESTRATOR, ticket=support.ORCHESTRATOR_TICKET_ID)
    if result.decision != "ask":
        pytest.fail(
            f"the PreToolUse guard answered `{CANARY}` by the orchestrator with {result.decision}, not ask: "
            f"the install rule is not in the guard ({result.describe()})",
            pytrace=False,
        )
    return hook


@pytest.fixture()
def sandbox(tmp_path):
    """``HOME`` (with ``.local/bin``) and the system temporary directory, both outside the project."""
    return support.make_sandbox(tmp_path / "sandbox")


@pytest.fixture()
def project(install_rule, tmp_path):
    """A committed project with the fixture tickets, all in progress."""
    return support.make_project(tmp_path / "project")


@pytest.fixture()
def bash(sandbox):
    """``bash(project, command, role, ticket, subagent=None, mode="default")`` asks the guard about one Bash call.

    ``{root}`` in the command is the project path and ``{home}`` the session's
    HOME. The command is not run.
    """

    def _bash(project, command, role=None, ticket=None, subagent=None, mode="default"):
        command = command.format(root=project, home=sandbox.home)
        return support.run_hook(project, "Bash", support.bash_input(command), sandbox, role=role, ticket=ticket,
                                subagent=subagent, permission_mode=mode)

    return _bash


@pytest.fixture()
def write(sandbox):
    """``write(project, relpath, role, ticket)`` asks the guard about one Write call."""

    def _write(project, relpath, role=None, ticket=None):
        tool_input = {"file_path": str(Path(project) / relpath), "content": "written by the acceptance test\n"}
        return support.run_hook(project, "Write", tool_input, sandbox, role=role, ticket=ticket)

    return _write


@pytest.fixture(scope="session")
def schema():
    """The tool-registry schema of the kernel template, parsed."""
    directory = support.REPO_ROOT / support.SCHEMA_DIR_REL
    path = directory / support.SCHEMA_NAME
    if not path.is_file():
        found = sorted(p.name for p in directory.glob(support.SCHEMA_GLOB)) if directory.is_dir() else []
        pytest.fail(
            f"{support.SCHEMA_DIR_REL}/{support.SCHEMA_NAME} does not exist: the tool-registry schema is missing"
            + (f" (found instead: {', '.join(found)})" if found else ""),
            pytrace=False,
        )
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as exc:
        pytest.fail(f"{support.SCHEMA_DIR_REL}/{support.SCHEMA_NAME} is not JSON: {exc}", pytrace=False)
    return data
