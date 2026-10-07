"""Fixtures for the W1-29 acceptance tests (session hooks).

The combined PreCompact and SessionStart hooks are the same files the W1-49
suite exercises: ``template/governance/kernel/hooks/precompact.py`` and
``sessionstart.py``.  For these two events, W1-29 tests run the registered
shell commands (read from ``.claude/settings.json``) in a temporary project
built by ``w1_49_support.make_project()``, extended with W1-29 fixture data.
Every case of ``tests/acceptance/W1-49/`` passes unchanged: W1-29 adds to
W1-49's hooks, it does not replace them.

Stop and SubagentStop are W1-29-only hooks in ``src/gov/hooks/``.  They are
run as Python scripts directly because they may not yet be registered.

The watchdog tests (failure line 3, CAP-37.c) call
``gov.checkpoint.record.watch`` directly because ``gov close`` (W1-30) is
not built.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]

_W1_49_DIR = str(REPO_ROOT / "tests" / "acceptance" / "W1-49")
if _W1_49_DIR not in sys.path:
    sys.path.insert(0, _W1_49_DIR)
import w1_49_support  # noqa: E402

_SRC_DIR = str(REPO_ROOT / "src")
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

HOOKS_DIR = REPO_ROOT / "src" / "gov" / "hooks"
SCRATCH_CHECKPOINTS_REL = ".gov-runtime/scratch/checkpoints"

ORCH = w1_49_support.ORCHESTRATOR_CHECKPOINT_REL
LEAD = w1_49_support.LEAD_CHECKPOINT_REL
TOKEN_CHARS = 4
BRIEF_TOKEN_LIMIT = 2500
SIZE_CAP_CHARS = w1_49_support.SIZE_CAP_CHARS

TWELVE_FIELDS = (
    "task", "status", "work_completed", "files_changed",
    "evidence", "tests", "discoveries", "risks",
    "lessons", "proposed_decisions", "unresolved",
    "recommended_next_action",
)

TICKET_TEXT = (
    "---\n"
    "id: TEST-abcd\n"
    "status: in_progress\n"
    "title: Test ticket\n"
    "sources: []\n"
    "depends_on: []\n"
    "---\n"
    "# TEST-abcd Test ticket\n"
)

CHECKPOINT_RECORD_TEXT = (
    "---\n"
    "id: CP-TEST-abcd-0001\n"
    "type: checkpoint\n"
    "status: ACTIVE\n"
    "state_class: NARRATIVE\n"
    "title: TEST-abcd at compaction\n"
    "task: TEST-abcd\n"
    "task_status: in_progress\n"
    "trigger: compaction\n"
    "next_action: Continue implementation\n"
    "created: 2026-10-05T00:00:00Z\n"
    "inputs:\n"
    "  - id: TEST-abcd\n"
    "    version: abc1234\n"
    "    hash: 'sha256:0000000000000000000000000000000000000000000000000000000000000000'\n"
    "---\n\n"
    "# CP-TEST-abcd-0001 — TEST-abcd at compaction\n\n"
    "## Next action\n\n"
    "Continue implementation\n"
)


def _tokens(text: str) -> int:
    """ceil(len(text) / 4), the counter W1-24 uses."""
    return -(-len(text) // TOKEN_CHARS)


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "local_only: needs dev tiers (GOV_DEV_TIERS) or a real session; not for CI",
    )


# ---------------------------------------------------------------------------
# Registration: read from the real repository's .claude/settings.json
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def registration():
    """``(hooks, env)`` of ``.claude/settings.json``; no other key is read."""
    return w1_49_support.load_hooks_and_env()


@pytest.fixture(scope="session")
def hooks(registration):
    return registration[0]


def _registered(hooks, event, values, rel):
    if not (REPO_ROOT / rel).is_file():
        pytest.fail(f"the hook {rel} does not exist yet", pytrace=False)
    commands = {v: w1_49_support.command_for(hooks, event, v, rel) for v in values}
    missing = [v for v, c in commands.items() if c is None]
    if missing:
        pytest.fail(
            f"no {event} hook registered that runs {rel} for {missing}",
            pytrace=False,
        )
    return commands


@pytest.fixture(scope="session")
def precompact_commands(hooks):
    """The registered PreCompact command by trigger."""
    return _registered(
        hooks, "PreCompact", ("manual", "auto"), w1_49_support.PRECOMPACT_REL,
    )


@pytest.fixture(scope="session")
def sessionstart_commands(hooks):
    """The registered SessionStart command by source."""
    return _registered(
        hooks, "SessionStart", ("compact", "clear", "resume"),
        w1_49_support.SESSIONSTART_REL,
    )


# ---------------------------------------------------------------------------
# Combined temporary project (W1-49 layout + W1-29 fixture data)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def combined_base(tmp_path_factory):
    """A git repository with the kernel hooks, ``src/gov``, a stand-in
    prompt, a ticket and a checkpoint record, committed."""
    project = w1_49_support.make_project(
        tmp_path_factory.mktemp("w29-base") / "repo",
    )
    w1_49_support.write(project, ".tickets/TEST-abcd.md", TICKET_TEXT)
    (project / "docs" / "checkpoints" / "TEST-abcd").mkdir(
        parents=True, exist_ok=True,
    )
    w1_49_support.write(
        project,
        "docs/checkpoints/TEST-abcd/CP-TEST-abcd-0001.md",
        CHECKPOINT_RECORD_TEXT,
    )
    w1_49_support.git(project, "add", "-A")
    w1_49_support.git(project, "commit", "-q", "-m", "add W1-29 fixture data")
    return project


@pytest.fixture()
def w49_project(combined_base, tmp_path):
    """This test's own copy of the combined project (main tree)."""
    target = tmp_path / "repo"
    shutil.copytree(combined_base, target, symlinks=True)
    return target


@pytest.fixture()
def worktree(w49_project, tmp_path):
    """A linked worktree of the combined project."""
    return w1_49_support.add_worktree(
        w49_project, tmp_path / "worktrees" / "lead-fixture",
    )


@pytest.fixture()
def sandbox(tmp_path):
    return w1_49_support.make_sandbox(tmp_path / "sandbox")


@dataclass(frozen=True)
class CombinedHooks:
    """Run the registered PreCompact and SessionStart commands."""
    precompact_commands: dict
    sessionstart_commands: dict
    sandbox: object

    def precompact(self, tree, trigger, role=w1_49_support.ORCHESTRATOR,
                   transcript_age_s=600.0, ticket=None, path=None):
        data = w1_49_support.precompact_input(
            tree, self.sandbox, trigger, transcript_age_s,
        )
        return w1_49_support.run_hook(
            self.precompact_commands[trigger], tree, self.sandbox,
            data, role=role, ticket=ticket, path=path,
        )

    def sessionstart(self, tree, source, role=w1_49_support.ORCHESTRATOR,
                     ticket=None, stdin=None):
        data = (
            stdin if stdin is not None
            else w1_49_support.sessionstart_input(tree, self.sandbox, source)
        )
        command = (
            self.sessionstart_commands.get(source)
            or self.sessionstart_commands["resume"]
        )
        return w1_49_support.run_hook(
            command, tree, self.sandbox, data, role=role, ticket=ticket,
        )


@pytest.fixture()
def run(precompact_commands, sessionstart_commands, sandbox):
    """``run.precompact(tree, trigger)`` and ``run.sessionstart(tree, source)``."""
    return CombinedHooks(precompact_commands, sessionstart_commands, sandbox)


# ---------------------------------------------------------------------------
# W1-29-only hook runner (Stop, SubagentStop from src/gov/hooks/)
# ---------------------------------------------------------------------------

def run_w29_hook(name, input_data, project_root, env_extra=None):
    """Run a W1-29-only hook script from ``src/gov/hooks/``.

    Returns ``(exit_code, parsed_stdout_or_None, stderr)``.
    """
    script = HOOKS_DIR / f"{name}.py"
    assert script.is_file(), (
        f"W1-29 hook '{name}' not built: {script} does not exist "
        f"(src/gov/hooks/ is empty)"
    )
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "PYTHONPATH": str(REPO_ROOT / "src"),
        "PYTHONDONTWRITEBYTECODE": "1",
        "CLAUDE_PROJECT_DIR": str(project_root),
    }
    if env_extra:
        env.update(env_extra)
    result = subprocess.run(
        [sys.executable, str(script)],
        input=json.dumps(input_data),
        capture_output=True, text=True,
        cwd=str(project_root),
        env=env,
        timeout=30,
    )
    parsed = None
    if result.stdout.strip():
        try:
            parsed = json.loads(result.stdout)
        except json.JSONDecodeError:
            pass
    return result.returncode, parsed, result.stderr


# ---------------------------------------------------------------------------
# Simple project for Stop, SubagentStop and watchdog tests
# ---------------------------------------------------------------------------

_GIT_ENV = {
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_AUTHOR_NAME": "W1-29 test",
    "GIT_AUTHOR_EMAIL": "test@example.invalid",
    "GIT_COMMITTER_NAME": "W1-29 test",
    "GIT_COMMITTER_EMAIL": "test@example.invalid",
    "LC_ALL": "C",
}


def _simple_git(root, *args):
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": str(root),
        **_GIT_ENV,
    }
    return subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True, text=True, env=env, check=True,
    )


@pytest.fixture()
def project(tmp_path):
    """A throwaway project for Stop, SubagentStop and watchdog tests."""
    _simple_git(tmp_path, "init", "-q", "-b", "main")
    (tmp_path / ".gitignore").write_text(
        ".gov-runtime/\n__pycache__/\n", encoding="utf-8",
    )
    (tmp_path / ".tickets").mkdir()
    (tmp_path / ".tickets" / "TEST-abcd.md").write_text(
        TICKET_TEXT, encoding="utf-8",
    )
    cp_dir = tmp_path / "docs" / "checkpoints" / "TEST-abcd"
    cp_dir.mkdir(parents=True)
    (cp_dir / "CP-TEST-abcd-0001.md").write_text(
        CHECKPOINT_RECORD_TEXT, encoding="utf-8",
    )
    _simple_git(tmp_path, "add", "-A")
    _simple_git(tmp_path, "commit", "-q", "-m", "init")
    return tmp_path
