"""Support code for the W1-50 freeze tests (DEC-402, DEC-399): ``test_w1_50_freeze_*.py``.

Three public interfaces are driven, each the way the suite that first tested
it drives it:

- **the guard**, as a process: the PreToolUse hook of the kernel template,
  installed in W1-02's fixture project, one JSON object on stdin
  (``w1_02_support``). Both readers of the flag sit behind it: the guard's
  decision, and the hook's own reading for an install;
- **``gov pause``**, through the command line with ``--json``, as W1-28's suite
  runs it (``w1_28_support``): this worktree's ``src/``, a temporary project as
  ``--root`` and as the working directory, an environment built from scratch;
- **``gov launch``**, through the settings it hands to a stand-in CLI, as
  W1-46's suite reads them (``w1_46_support``).

**Every test builds its own temporary project.** Nothing here creates, writes
or removes ``.gov-runtime/freeze`` of this worktree, and ``gov pause`` is never
run on it (``w1_28_support.gov`` refuses a project inside this repository).

The fixtures of this module carry the prefix ``freeze_``: the folder's
``conftest.py`` belongs to the other half of the ticket, and a test file of
this half imports the fixtures it uses from here.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import sys
import time
from pathlib import Path

import pytest

_TESTS = Path(__file__).resolve().parent.parent
for _suite in ("W1-02", "W1-28", "W1-46"):
    _directory = str(_TESTS / _suite)
    if _directory not in sys.path:
        sys.path.insert(0, _directory)

import w1_02_support as guard_support   # noqa: E402  the guard hook as a process, and the fixture project
import w1_28_support as pause_support   # noqa: E402  ``gov pause`` through the command line
import w1_46_support as launch_support  # noqa: E402  ``gov launch`` and what the built settings say

cli_support = pause_support.cli_support
w47 = launch_support.w47

REPO_ROOT = Path(__file__).resolve().parents[3]
RUNTIME_REL = ".gov-runtime"
FLAG_REL = ".gov-runtime/freeze"          # DEC-109; ``FREEZE_FLAG`` of ``src/gov/guard/decide.py``
RECORDS_REL = ".gov-runtime/records.jsonl"  # DEC-177
FINDINGS_REL = ".gov-runtime/findings.jsonl"

ENGINEER = guard_support.ENGINEER
ORCHESTRATOR = guard_support.ORCHESTRATOR
OWNER_NAME = "owner"
TICKET = guard_support.TICKET_ID
ORCHESTRATOR_TICKET = guard_support.ORCHESTRATOR_TICKET_ID
OWN_REL = "src/gov/guard/decide.py"       # inside the engineer ticket's allowed_paths

# --------------------------------------------------------------------------
# The marker (DEC-402), as pinned in w1_50_freeze_README.md
# --------------------------------------------------------------------------

MARKER_WORD = "FROZEN"
# What ``gov pause`` writes as the flag's first line: the word, the caller of DEC-365, the time in the form the
# project's records use (``src/gov/guard/containment.py``: ``%Y-%m-%dT%H:%M:%SZ``, UTC).
TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
MARKER_LINE = re.compile(r"FROZEN (owner|orchestrator) (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)")
# A flag as ``gov pause`` writes it, with a made-up time: what a test puts at the path to freeze a project.
A_MARKER_LINE = "FROZEN owner 2026-10-05T00:00:00Z\n"

# The fields of a record line: DEC-122's, with DEC-177's action.
RECORD_FIELDS = ("time", "session_id", "agent_type", "role", "ticket", "tool", "command", "paths", "action", "reason")
RECORDED = "recorded"


def flag(project):
    return Path(project) / FLAG_REL


def first_line(path):
    """The first line of the file at ``path``, without its line end; None when the file is empty."""
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    return lines[0] if lines else None


def assert_marker(path, who, what):
    """The flag at ``path`` is a regular file whose first line is the marker line, written for ``who``."""
    path = Path(path)
    assert path.is_file() and not path.is_symlink(), f"{what}: {FLAG_REL} is not a regular file"
    line = first_line(path)
    found = MARKER_LINE.fullmatch(line or "")
    assert found, (
        f"{what}: the first line of {FLAG_REL} is {line!r}, not the marker line "
        f"`{MARKER_WORD} <owner|orchestrator> <YYYY-MM-DDTHH:MM:SSZ>` (DEC-402)"
    )
    assert found.group(1) == who, f"{what}: the marker names {found.group(1)!r} as the caller, not {who!r} (DEC-365)"
    time.strptime(found.group(2), TIME_FORMAT)   # a real date and time, whatever its value
    return found


# --------------------------------------------------------------------------
# What may sit at the flag's path
# --------------------------------------------------------------------------

def put_text(project, text, mode=None):
    """A regular file at the flag's path holding ``text`` (bytes are written as they are)."""
    path = flag(project)
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(text, bytes):
        path.write_bytes(text)
    else:
        path.write_text(text, encoding="utf-8", newline="")
    if mode is not None:
        path.chmod(mode)
    return path


def put_placeholder(project):
    """What the sandbox leaves at a denied name that does not exist, seen from outside: empty, regular, 0444."""
    return put_text(project, "", mode=0o444)


def put_link(project, target):
    path = flag(project)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.symlink_to(target)
    return path


def put_directory(project):
    path = flag(project)
    path.mkdir(parents=True)
    return path


# --------------------------------------------------------------------------
# Asking the guard
# --------------------------------------------------------------------------

def guard_write(project, sandbox, tool_name="Write", rel=OWN_REL, role=ENGINEER, ticket=TICKET):
    """The guard's answer to one file-tool write; by default one the engineer may make when nothing is frozen."""
    tool_input = guard_support.edit_tool_input(tool_name, Path(project) / rel)
    return guard_support.run_hook(project, tool_name, tool_input, sandbox, role=role, ticket=ticket)


def guard_bash(project, sandbox, command, role=ENGINEER, ticket=TICKET):
    return guard_support.run_hook(project, "Bash", guard_support.bash_tool_input(command), sandbox, role=role,
                                  ticket=ticket)


def assert_frozen(result, what):
    """A denial the guard decided, for the freeze: not an internal failure that happens to block (exit code 2)."""
    assert result.decision == "deny", f"{what}: the write was not denied: {result.describe()}"
    assert result.returncode == 0, f"{what}: the guard failed instead of deciding: {result.describe()}"
    assert "frozen" in result.stdout.lower(), f"{what}: the denial does not name the freeze: {result.describe()}"


def assert_not_frozen(result, what):
    assert result.decision == "allow" and result.returncode == 0, \
        f"{what}: the engineer's write inside its ticket's paths was not allowed: {result.describe()}"


def json_lines(project, rel):
    path = Path(project) / rel
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def flag_records(project):
    """The lines of ``records.jsonl`` that name the flag's path."""
    return [record for record in json_lines(project, RECORDS_REL)
            if isinstance(record, dict) and FLAG_REL in (record.get("paths") or [])]


def flag_findings(project):
    """The lines of ``findings.jsonl`` that speak of the flag's path in any field."""
    return [finding for finding in json_lines(project, FINDINGS_REL) if FLAG_REL in json.dumps(finding)]


# --------------------------------------------------------------------------
# Fixtures (imported by the test files)
# --------------------------------------------------------------------------

@pytest.fixture(scope="session")
def freeze_interface():
    """The envelope fields and exit codes of ``docs/interfaces/API-0002.yaml``."""
    return cli_support.load_interface(REPO_ROOT)


@pytest.fixture()
def freeze_sandbox(tmp_path):
    """HOME, TMPDIR, the console script's directory, the bytecode cache and an unrelated directory."""
    return cli_support.make_sandbox(tmp_path / "freeze-sandbox")


@pytest.fixture()
def freeze_project(tmp_path):
    """This test's own temporary git repository: W1-02's fixture project, the guard hook installed, nothing frozen."""
    project = pause_support.make_project(tmp_path / "freeze-project")
    assert not os.path.lexists(flag(project)), "the fixture project starts with something at the flag's path"
    return project


@pytest.fixture()
def freeze_pause(freeze_project, freeze_sandbox):
    """``pause(*args, role=None)`` runs ``gov pause <args> --json`` on this test's project; None is the owner."""

    def _pause(*args, role=pause_support.OWNER):
        return pause_support.pause(freeze_project, freeze_sandbox, *args, role=role)

    return _pause


@pytest.fixture(scope="session")
def freeze_launch_base(tmp_path_factory):
    """W1-46's launch fixture project, built once. Every test works on its own copy of it."""
    return launch_support.make_project(tmp_path_factory.mktemp("w1-50-freeze-launch-base") / "repo")


@pytest.fixture()
def freeze_launch_project(freeze_launch_base, tmp_path, freeze_sandbox):
    """This test's own copy of the launch project, with a ``held-out.yaml`` made up here (a stand-in directory)."""
    target = tmp_path / "launch-repo"
    shutil.copytree(freeze_launch_base, target, symlinks=True)
    stand_in = w47.make_stand_in(freeze_sandbox.elsewhere / "held-out-stand-in")
    w47.configure_stand_in(target, stand_in)
    assert not os.path.lexists(flag(target)), "the launch fixture project starts with something at the flag's path"
    return target


@pytest.fixture()
def freeze_launch(freeze_launch_project, freeze_sandbox):
    """``launch(role)`` runs ``gov launch <role> <ticket>`` in the project, with the stand-in CLI: no session starts."""
    cli = launch_support.install_stand_in_cli(freeze_sandbox)

    def _launch(role=ENGINEER):
        return launch_support.launch(freeze_launch_project, freeze_sandbox, cli, role, launch_support.TICKET_OF[role])

    return _launch


def literal_runtime_names(result, project, sandbox):
    """The names directly under ``.gov-runtime/`` that the built settings deny by a literal ``Edit`` rule."""
    runtime = os.path.join(os.path.realpath(project), RUNTIME_REL)
    return sorted(os.path.basename(path) for path in launch_support.literal_edit_denials(result, project, sandbox)
                  if os.path.dirname(path) == runtime)
