"""Fixtures for the W1-29 acceptance tests (session hooks).

The hooks under test are scripts in ``src/gov/hooks/``.  They receive JSON on
stdin and produce JSON on stdout.  Every test that runs a hook asserts the
script exists first; while ``src/gov/hooks/`` is empty, the assertion fails and
that is the stated red reason.

The watchdog tests (failure line 3, CAP-37.c) call ``gov.checkpoint.record``
directly because ``gov close`` (W1-30) is not built.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
HOOKS_DIR = REPO_ROOT / "src" / "gov" / "hooks"

# Add src/ so the watchdog tests can import gov.checkpoint.record.
sys.path.insert(0, str(REPO_ROOT / "src"))

# Token counter from W1-24 (src/gov/context/__init__.py).
TOKEN_CHARS = 4
BRIEF_TOKEN_LIMIT = 2500  # tokens, per CAP-15.g / DEC-025

TWELVE_FIELDS = (
    "task", "status", "work_completed", "files_changed",
    "evidence", "tests", "discoveries", "risks",
    "lessons", "proposed_decisions", "unresolved",
    "recommended_next_action",
)


def _tokens(text: str) -> int:
    """ceil(len(text) / 4), the counter W1-24 uses."""
    return -(-len(text) // TOKEN_CHARS)


# ---------------------------------------------------------------------------
# git helpers (isolated environment, no user config)
# ---------------------------------------------------------------------------

_GIT_ENV = {
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_AUTHOR_NAME": "W1-29 test",
    "GIT_AUTHOR_EMAIL": "test@example.invalid",
    "GIT_COMMITTER_NAME": "W1-29 test",
    "GIT_COMMITTER_EMAIL": "test@example.invalid",
    "LC_ALL": "C",
}


def _git(root, *args):
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"),
           "HOME": str(root), **_GIT_ENV}
    return subprocess.run(["git", "-C", str(root), *args],
                          capture_output=True, text=True, env=env, check=True)


# ---------------------------------------------------------------------------
# Hook runner
# ---------------------------------------------------------------------------

def run_hook(name, input_data, project_root, env_extra=None):
    """Run a W1-29 hook script from ``src/gov/hooks/``.

    Asserts the script exists.  While the module is not built, every call
    fails with ``AssertionError`` naming the missing file.

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
# Fixtures
# ---------------------------------------------------------------------------

def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "local_only: needs dev tiers (GOV_DEV_TIERS) or a real session; not for CI",
    )


@pytest.fixture()
def project(tmp_path):
    """A throwaway temporary project with a ticket, a checkpoint and git history.

    Good enough for both hook tests (which fail at the hook-existence check)
    and watchdog tests (which exercise ``gov.checkpoint.record.watch``).
    """
    _git(tmp_path, "init", "-q", "-b", "main")

    # A ticket.
    tickets = tmp_path / ".tickets"
    tickets.mkdir()
    (tickets / "TEST-abcd.md").write_text(
        "---\n"
        "id: TEST-abcd\n"
        "status: in_progress\n"
        "title: Test ticket\n"
        "sources: []\n"
        "depends_on: []\n"
        "---\n"
        "# TEST-abcd Test ticket\n",
        encoding="utf-8",
    )

    # A checkpoint (created in the past so the watchdog can judge age).
    cp_dir = tmp_path / "docs" / "checkpoints" / "TEST-abcd"
    cp_dir.mkdir(parents=True)
    (cp_dir / "CP-TEST-abcd-0001.md").write_text(
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
        "Continue implementation\n",
        encoding="utf-8",
    )

    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-q", "-m", "init")

    return tmp_path
