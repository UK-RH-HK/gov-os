"""Fixtures for the W1-49 acceptance tests."""

from __future__ import annotations

import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w1_49_support as support  # noqa: E402


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "local_only: needs the Claude Code CLI on this machine, or starts a real session; not for CI")


@pytest.fixture(scope="session")
def registration():
    """``(hooks, env)`` of this repository's ``.claude/settings.json``; no other key is read."""
    return support.load_hooks_and_env()


@pytest.fixture(scope="session")
def hooks(registration):
    return registration[0]


@pytest.fixture(scope="session")
def settings_env(registration):
    return registration[1]


def _registered(hooks, event, values, rel):
    """One command for every matcher value, or the red reason."""
    if not (support.REPO_ROOT / rel).is_file():
        pytest.fail(f"the hook {rel} does not exist yet", pytrace=False)
    commands = {value: support.command_for(hooks, event, value, rel) for value in values}
    missing = [value for value, command in commands.items() if command is None]
    if missing:
        pytest.fail(f"{support.SETTINGS_REL} registers no {event} hook that runs {rel} for {missing}", pytrace=False)
    return commands


@pytest.fixture(scope="session")
def precompact_commands(hooks):
    """The registered PreCompact command by trigger (``manual``, ``auto``)."""
    return _registered(hooks, "PreCompact", ("manual", "auto"), support.PRECOMPACT_REL)


@pytest.fixture(scope="session")
def sessionstart_commands(hooks):
    """The registered SessionStart command by source (``compact``, ``clear``, ``resume``)."""
    return _registered(hooks, "SessionStart", ("compact", "clear", "resume"), support.SESSIONSTART_REL)


@pytest.fixture(scope="session")
def base(tmp_path_factory):
    """The temporary project, built once. Every test works on its own copy."""
    return support.make_project(tmp_path_factory.mktemp("w1-49-base") / "repo")


@pytest.fixture()
def project(base, tmp_path):
    """This test's own main tree."""
    target = tmp_path / "repo"
    shutil.copytree(base, target, symlinks=True)
    return target


@pytest.fixture()
def worktree(project, tmp_path):
    """A linked worktree of this test's project, as a ticket lead works in."""
    return support.add_worktree(project, tmp_path / "worktrees" / "lead-fixture")


@pytest.fixture()
def sandbox(tmp_path):
    return support.make_sandbox(tmp_path / "sandbox")


@dataclass(frozen=True)
class Hooks:
    precompact_commands: dict
    sessionstart_commands: dict
    sandbox: object

    def precompact(self, tree, trigger, role=support.ORCHESTRATOR, transcript_age_s=600.0, stdin=None):
        data = stdin if stdin is not None else support.precompact_input(tree, self.sandbox, trigger, transcript_age_s)
        return support.run_hook(self.precompact_commands[trigger], tree, self.sandbox, data, role=role)

    def sessionstart(self, tree, source, role=support.ORCHESTRATOR, stdin=None):
        data = stdin if stdin is not None else support.sessionstart_input(tree, self.sandbox, source)
        command = self.sessionstart_commands.get(source) or self.sessionstart_commands["resume"]
        return support.run_hook(command, tree, self.sandbox, data, role=role)


@pytest.fixture()
def run(precompact_commands, sessionstart_commands, sandbox):
    """``run.precompact(tree, trigger)`` and ``run.sessionstart(tree, source)``: the registered commands, run once."""
    return Hooks(precompact_commands, sessionstart_commands, sandbox)
