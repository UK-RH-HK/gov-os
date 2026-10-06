"""Support code for the W1-02 acceptance tests (standard library only).

The guard is driven the way the harness drives it: the PreToolUse hook script
is started as a process, one JSON object arrives on stdin, and the exit code
and stdout carry the decision.

- The hook is the file matching ``template/governance/kernel/hooks/pretooluse*``.
  It is copied into a throw-away project at ``governance/kernel/hooks/``, the
  place Copier puts it in a product repository (ADR-0002 section 5).
- ``src/`` of this repository is put on ``PYTHONPATH``; that stands in for the
  installed ``gov`` package.
- The project is named three ways, as the harness does: the working directory
  of the process, ``cwd`` in the stdin object, and ``CLAUDE_PROJECT_DIR``.
- The environment is built from scratch. Nothing of the calling session leaks
  in, and ``HOME`` is an empty temporary directory. A role and an active ticket
  are declared only when a test passes them: ``GOV_ROLE`` and ``GOV_TICKET``
  (owner answer to KD-1). A test may add variables of its own, which the guard
  expands in a Bash write target (DEC-115).
- ``TMPDIR`` points at a directory of its own next to the project, so
  ``tempfile.gettempdir()`` inside the hook returns that directory (owner
  answer to KD-2) and the project is not inside it.

Decisions (register DEC-025, "path guard via exit 2 / permissionDecision: deny"):

- ``deny``  exit code 2, or exit code 0 with
  ``hookSpecificOutput.permissionDecision == "deny"`` on stdout;
- ``ask``   exit code 0 with ``permissionDecision == "ask"``;
- ``allow`` exit code 0 with neither;
- ``error`` any other exit code. The harness treats it as a hook error and lets
  the call through, so it is neither a denial nor an allowance;
- ``timeout`` no exit within the time limit.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import stat
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
HOOK_DIR_REL = "template/governance/kernel/hooks"
HOOK_GLOB = "pretooluse*"
PRODUCT_HOOK_DIR_REL = "governance/kernel/hooks"
GOV_PACKAGE_PARENT_REL = "src"

ROLE_ENV = "GOV_ROLE"
TICKET_ENV = "GOV_TICKET"
FREEZE_FLAG_REL = ".gov-runtime/freeze"
# DEC-402: a real flag carries the marker line ``gov pause`` writes; a made-up caller and time.
FREEZE_MARKER_LINE = "FROZEN owner 2026-10-05T00:00:00Z\n"
FINDINGS_REL = ".gov-runtime/findings.jsonl"
SCRATCH_REL = ".gov-runtime/scratch"

ENGINEER = "engineer"
ORCHESTRATOR = "orchestrator"
PRODUCT_SPEC = "product-spec"
TEST_DESIGNER = "independent-test-designer"
AUDITOR = "independent-auditor"
KNOWN_ROLES = (ORCHESTRATOR, PRODUCT_SPEC, TEST_DESIGNER, ENGINEER, AUDITOR)
UNKNOWN_ROLES = ("developer", "implementer", "admin", "owner", "engineer,orchestrator", "*")

HOOK_TIMEOUT_S = 20.0
SESSION_ID = "w1-02-acceptance-session"

# The engineer ticket most tests work on.
TICKET_ID = "DAEO-zz90"
TICKET_WBS_ID = "W1-90"
TICKET_ALLOWED_PATHS = (
    "src/gov/guard/**",
    "tests/unit/guard/**",
    "template/governance/kernel/hooks/pretooluse*",
    "pyproject.toml",
)
# One ticket per other role that works on tickets, and a second engineer ticket.
ORCHESTRATOR_TICKET_ID = "DAEO-zz91"
PRODUCT_SPEC_TICKET_ID = "DAEO-zz92"
DOCS_TICKET_ID = "DAEO-zz95"


class HookMissing(AssertionError):
    """The guard hook is not in the repository, or its entry point is unclear."""


# --------------------------------------------------------------------------
# The hook
# --------------------------------------------------------------------------

def _is_executable(path):
    return bool(path.stat().st_mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH))


def hook_files(root=REPO_ROOT):
    """Every regular file matching ``template/governance/kernel/hooks/pretooluse*``."""
    hook_dir = Path(root) / HOOK_DIR_REL
    if not hook_dir.is_dir():
        return []
    return sorted(p for p in hook_dir.glob(HOOK_GLOB) if p.is_file())


def hook_entry(root=REPO_ROOT):
    """The one file the harness is to run.

    One matching file: that file. Several: the only executable one. Anything
    else is unclear and fails.
    """
    files = hook_files(root)
    if not files:
        raise HookMissing(
            f"no file matches {HOOK_DIR_REL}/{HOOK_GLOB}: the PreToolUse guard hook does not exist"
        )
    if len(files) == 1:
        return files[0]
    executables = [p for p in files if _is_executable(p)]
    if len(executables) == 1:
        return executables[0]
    names = ", ".join(p.name for p in files)
    raise HookMissing(
        f"{HOOK_DIR_REL}/{HOOK_GLOB} matches {names}; exactly one of them must be executable "
        f"so the entry point is clear ({len(executables)} are)"
    )


def _argv(entry):
    if _is_executable(entry):
        return [str(entry)]
    if entry.suffix == ".py":
        return [sys.executable, str(entry)]
    if entry.suffix in (".sh", ".bash"):
        return ["bash", str(entry)]
    raise HookMissing(
        f"{entry.name} is not executable and is neither a .py nor a .sh file; cannot tell how to run it"
    )


def installed_hook_rel():
    """Repository-relative path of the hook entry point inside a fixture project."""
    return f"{PRODUCT_HOOK_DIR_REL}/{hook_entry().name}"


# --------------------------------------------------------------------------
# A throw-away project
# --------------------------------------------------------------------------

def git(project, *args):
    proc = subprocess.run(
        [
            "git", "-C", str(project),
            "-c", "user.name=W1-02 acceptance", "-c", "user.email=w1-02@example.invalid",
            "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null",
            *args,
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed in the test project: {proc.stderr.strip()}")
    return proc.stdout


def ticket_text(ticket_id=TICKET_ID, wbs_id=TICKET_WBS_ID, status="in_progress", role=ENGINEER,
                allowed_paths=TICKET_ALLOWED_PATHS):
    """A ticket file with the frontmatter shape of the Wave 1 tickets."""
    paths = "".join(f"- {p}\n" for p in allowed_paths)
    return (
        "---\n"
        f"id: {ticket_id}\n"
        f"status: {status}\n"
        "deps: []\n"
        "links: []\n"
        "created: 2026-09-30T22:49:58Z\n"
        "type: task\n"
        "priority: 1\n"
        f"assignee: {role}\n"
        f"external-ref: {wbs_id}\n"
        "tags: [wave-1, implementation, full]\n"
        f"wbs_id: {wbs_id}\n"
        "title: Guard fixture ticket\n"
        "class: implementation\n"
        f"role: {role}\n"
        "depends_on: []\n"
        "allowed_paths:\n"
        f"{paths}"
        "kpis:\n"
        "  success:\n"
        "  - The fixture component exists\n"
        "  failure:\n"
        "  - The fixture component is missing\n"
        "profile: FULL\n"
        "acceptance_tests:\n"
        f"  path: tests/acceptance/{wbs_id}/\n"
        "---\n"
        f"# {wbs_id} Guard fixture ticket\n"
    )


def default_tickets():
    """The tickets of the standard fixture project, all in progress."""
    return {
        f"{TICKET_ID}.md": ticket_text(),
        f"{ORCHESTRATOR_TICKET_ID}.md": ticket_text(
            ticket_id=ORCHESTRATOR_TICKET_ID, wbs_id="W1-91", role=ORCHESTRATOR,
            allowed_paths=(".claude/settings.json", "governance/project/bootstrap.md"),
        ),
        f"{PRODUCT_SPEC_TICKET_ID}.md": ticket_text(
            ticket_id=PRODUCT_SPEC_TICKET_ID, wbs_id="W1-92", role=PRODUCT_SPEC,
            allowed_paths=("template/governance/kernel/roles/**", "docs/spec/**"),
        ),
        f"{DOCS_TICKET_ID}.md": ticket_text(
            ticket_id=DOCS_TICKET_ID, wbs_id="W1-95", role=ENGINEER,
            allowed_paths=("docs/**",),
        ),
    }


PROJECT_FILES = {
    "README.md": "# Fixture project\n",
    ".gitignore": ".gov-runtime/\n__pycache__/\n",
    "pyproject.toml": "[project]\nname = \"fixture\"\n",
    "docs/notes.md": "notes\n",
    "docs/spec/feature.md": "VALUE = 1\n",
    "src/gov/__init__.py": "VALUE = 1\n",
    "src/gov/guard/decide.py": "VALUE = 1\n",
    "src/gov/guard/analysis.ipynb": '{"cells": [], "metadata": {}, "nbformat": 4, "nbformat_minor": 5}\n',
    "src/gov/guardian/other.py": "VALUE = 1\n",
    "src/app/main.py": "VALUE = 1\n",
    "tests/unit/guard/test_decide.py": "VALUE = 1\n",
    "tests/unit/other/test_other.py": "VALUE = 1\n",
    f"tests/acceptance/{TICKET_WBS_ID}/test_fixture.py": "VALUE = 1\n",
    "template/governance/kernel/hooks/pretooluse.py": "VALUE = 1\n",
    "template/governance/kernel/hooks/posttooluse.py": "VALUE = 1\n",
    "template/governance/kernel/roles/engineer.md": "VALUE = 1\n",
    "governance/project/bootstrap.md": "VALUE = 1\n",
    ".claude/settings.json": "{}\n",
}

# Committed symbolic links: (link, target relative to the link's directory).
PROJECT_SYMLINKS = (
    ("src/gov/guard/acceptance_link", "../../../tests/acceptance"),
    ("src/gov/guard/docs_link", "../../../docs"),
)


def make_project(directory, tickets=None):
    """Create a committed git project with the guard hook installed.

    ``tickets`` maps a file name under ``.tickets/`` to its text. ``None`` gives
    the standard tickets; an empty mapping leaves the project without a
    ``.tickets/`` directory.
    """
    project = Path(directory)
    project.mkdir(parents=True, exist_ok=True)
    files = dict(PROJECT_FILES)
    for name, text in (default_tickets() if tickets is None else tickets).items():
        files[f".tickets/{name}"] = text
    for rel, text in files.items():
        path = project / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    for link, target in PROJECT_SYMLINKS:
        (project / link).symlink_to(target, target_is_directory=True)
    hook_dir = project / PRODUCT_HOOK_DIR_REL
    hook_dir.mkdir(parents=True, exist_ok=True)
    for source in hook_files():
        shutil.copy2(source, hook_dir / source.name)
    git(project, "init", "-q", "-b", "main")
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "fixture project")
    return project


def porcelain(project):
    """``git status --porcelain`` of the project."""
    return git(project, "status", "--porcelain")


def set_freeze(project, content=""):
    """Set the freeze flag the way ``gov pause`` does (owner answer to KD-3; the marker line, DEC-402).

    ``content`` follows the marker line.
    """
    flag = Path(project) / FREEZE_FLAG_REL
    flag.parent.mkdir(parents=True, exist_ok=True)
    flag.write_text(FREEZE_MARKER_LINE + content, encoding="utf-8")
    return flag


def findings(project):
    """Lines of ``.gov-runtime/findings.jsonl``; empty when the file is absent."""
    path = Path(project) / FINDINGS_REL
    if not path.is_file():
        return []
    return [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def real_ticket_text(wbs_id="W1-02", root=REPO_ROOT):
    """(ticket id, text) of this repository's ticket for ``wbs_id``, set in progress."""
    for path in sorted((Path(root) / ".tickets").glob("*.md")):
        text = path.read_text(encoding="utf-8")
        if re.search(rf"(?m)^wbs_id:\s*{re.escape(wbs_id)}\s*$", text):
            return path.stem, re.sub(r"(?m)^status:.*$", "status: in_progress", text, count=1)
    raise AssertionError(f"no ticket with wbs_id {wbs_id} in .tickets/")


# --------------------------------------------------------------------------
# One hook call
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Sandbox:
    """Directories outside the project that the hook process sees."""
    home: Path
    pycache: Path
    tmpdir: Path      # what tempfile.gettempdir() returns inside the hook
    elsewhere: Path   # outside the project, outside the scratch set


def make_sandbox(base):
    base = Path(base)
    box = Sandbox(base / "home", base / "pycache", base / "systmp", base / "elsewhere")
    for directory in (box.home, box.pycache, box.tmpdir, box.elsewhere):
        directory.mkdir(parents=True, exist_ok=True)
    return box


@dataclass(frozen=True)
class HookResult:
    decision: str          # deny | ask | allow | error | timeout
    returncode: int | None
    stdout: str
    stderr: str
    seconds: float

    def describe(self):
        return (
            f"decision={self.decision} exit={self.returncode} "
            f"stdout={self.stdout.strip()[:300]!r} stderr={self.stderr.strip()[:300]!r}"
        )


def classify(returncode, stdout):
    if returncode == 2:
        return "deny"
    if returncode != 0:
        return "error"
    text = stdout.strip()
    if not text:
        return "allow"
    try:
        data = json.loads(text)
    except ValueError:
        return "allow"
    specific = data.get("hookSpecificOutput") if isinstance(data, dict) else None
    decision = specific.get("permissionDecision") if isinstance(specific, dict) else None
    if decision in ("deny", "ask"):
        return decision
    return "allow"


def hook_environment(project, sandbox, role=None, ticket=None, extra_env=None):
    """A minimal environment: no variable of the calling session is inherited.

    ``extra_env`` adds or replaces variables. The target-resolution tests use it
    to give the hook a variable to expand, or another ``HOME`` (DEC-115).
    """
    env = {
        "PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"),
        "HOME": str(sandbox.home),
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "TZ": "UTC",
        "TMPDIR": str(sandbox.tmpdir),
        "PYTHONPATH": str(REPO_ROOT / GOV_PACKAGE_PARENT_REL),
        "PYTHONPYCACHEPREFIX": str(sandbox.pycache),
        "CLAUDE_PROJECT_DIR": str(project),
    }
    if role is not None:
        env[ROLE_ENV] = role
    if ticket is not None:
        env[TICKET_ENV] = ticket
    if extra_env:
        env.update({name: str(value) for name, value in extra_env.items()})
    return env


def payload(project, tool_name, tool_input, sandbox, subagent=None):
    """The PreToolUse stdin object of the harness.

    ``subagent`` is the subagent type name. When given, the object carries
    ``agent_id`` and ``agent_type``, as the harness sends them for a call made
    inside a subagent.
    """
    data = {
        "session_id": SESSION_ID,
        "transcript_path": str(sandbox.home / ".claude" / "projects" / "fixture" / f"{SESSION_ID}.jsonl"),
        "cwd": str(project),
        "permission_mode": "default",
        "hook_event_name": "PreToolUse",
        "tool_name": tool_name,
        "tool_input": tool_input,
        "tool_use_id": "toolu_w1_02_acceptance",
    }
    if subagent is not None:
        data["agent_id"] = "agent-w1-02-acceptance"
        data["agent_type"] = subagent
    return data


def _installed_entry(project):
    return Path(project) / PRODUCT_HOOK_DIR_REL / hook_entry().name


def run_hook_raw(project, stdin_text, sandbox, role=None, ticket=None, extra_env=None):
    """Run the installed hook once with ``stdin_text`` exactly as given."""
    project = Path(project)
    started = time.perf_counter()
    try:
        proc = subprocess.run(
            _argv(_installed_entry(project)),
            input=stdin_text,
            capture_output=True,
            text=True,
            cwd=str(project),
            env=hook_environment(project, sandbox, role, ticket, extra_env),
            timeout=HOOK_TIMEOUT_S,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return HookResult("timeout", None, str(exc.stdout or ""), str(exc.stderr or ""),
                          time.perf_counter() - started)
    seconds = time.perf_counter() - started
    return HookResult(classify(proc.returncode, proc.stdout), proc.returncode, proc.stdout, proc.stderr, seconds)


def run_hook(project, tool_name, tool_input, sandbox, role=None, ticket=None, subagent=None, extra_env=None):
    """Run the installed hook once on a well-formed call and classify the decision."""
    stdin = json.dumps(payload(project, tool_name, tool_input, sandbox, subagent))
    return run_hook_raw(project, stdin, sandbox, role, ticket, extra_env)


def run_hook_with_open_stdin(project, sandbox, limit_s, role=None, ticket=None):
    """Run the installed hook with a stdin that never ends; wait at most ``limit_s``."""
    project = Path(project)
    started = time.perf_counter()
    proc = subprocess.Popen(
        _argv(_installed_entry(project)),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=str(project),
        env=hook_environment(project, sandbox, role, ticket),
    )
    try:
        proc.wait(timeout=limit_s)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
        proc.stdin.close()
        proc.stdout.close()
        proc.stderr.close()
        return HookResult("timeout", None, "", "", time.perf_counter() - started)
    seconds = time.perf_counter() - started
    stdout, stderr = proc.stdout.read(), proc.stderr.read()
    for stream in (proc.stdin, proc.stdout, proc.stderr):
        try:
            stream.close()
        except OSError:
            pass
    return HookResult(classify(proc.returncode, stdout), proc.returncode, stdout, stderr, seconds)


# --------------------------------------------------------------------------
# Tool inputs
# --------------------------------------------------------------------------

def edit_tool_input(tool_name, path):
    """The tool input of a file-writing tool aimed at the absolute ``path``."""
    path = str(path)
    if tool_name == "Edit":
        return {"file_path": path, "old_string": "VALUE = 1", "new_string": "VALUE = 2"}
    if tool_name == "Write":
        return {"file_path": path, "content": "written by the acceptance test\n"}
    if tool_name == "NotebookEdit":
        return {"notebook_path": path, "new_source": "print('edited')", "cell_type": "code", "edit_mode": "insert"}
    raise ValueError(tool_name)


def bash_tool_input(command):
    return {"command": command, "description": "W1-02 acceptance attempt"}


def assert_denied(result, what):
    assert result.decision == "deny", f"{what} was not denied: {result.describe()}"


def assert_allowed(result, what):
    assert result.decision == "allow", f"{what} was not allowed: {result.describe()}"


def p95(samples):
    ordered = sorted(samples)
    index = max(0, -(-95 * len(ordered) // 100) - 1)
    return ordered[index]
