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
  in, and ``HOME`` is an empty temporary directory, so no role is declared
  through any channel unless a test declares one.

Decisions (register DEC-025, "path guard via exit 2 / permissionDecision: deny"):

- ``deny``  exit code 2, or exit code 0 with
  ``hookSpecificOutput.permissionDecision == "deny"`` on stdout;
- ``ask``   exit code 0 with ``permissionDecision == "ask"``;
- ``allow`` exit code 0 with neither;
- ``error`` any other exit code. The harness treats it as a hook error and lets
  the call through, so it is neither a denial nor an allowance;
- ``timeout`` no exit within ``HOOK_TIMEOUT_S``.
"""

from __future__ import annotations

import json
import os
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

HOOK_TIMEOUT_S = 20.0
SESSION_ID = "w1-02-acceptance-session"

TICKET_ID = "DAEO-zz90"
TICKET_WBS_ID = "W1-90"
TICKET_ALLOWED_PATHS = ("src/gov/guard/**", "tests/unit/guard/**")


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


# --------------------------------------------------------------------------
# A throw-away project
# --------------------------------------------------------------------------

def _git(project, *args):
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


def ticket_text(ticket_id=TICKET_ID, wbs_id=TICKET_WBS_ID, status="in_progress", role="engineer",
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


PROJECT_FILES = {
    "README.md": "# Fixture project\n",
    ".gitignore": ".gov-runtime/\n__pycache__/\n",
    "docs/notes.md": "notes\n",
    "src/gov/guard/decide.py": "VALUE = 1\n",
    "src/gov/guard/analysis.ipynb": '{"cells": [], "metadata": {}, "nbformat": 4, "nbformat_minor": 5}\n',
    "src/app/main.py": "print('app')\n",
    "tests/unit/guard/test_decide.py": "def test_value():\n    assert True\n",
    f"tests/acceptance/{TICKET_WBS_ID}/test_fixture.py": "def test_fixture():\n    assert True\n",
    ".claude/settings.json": "{}\n",
}


def make_project(directory, tickets):
    """Create a committed git project with the guard hook installed.

    ``tickets`` maps a file name under ``.tickets/`` to its text; an empty
    mapping leaves the project without a ``.tickets/`` directory.
    """
    project = Path(directory)
    project.mkdir(parents=True, exist_ok=True)
    files = dict(PROJECT_FILES)
    for name, text in tickets.items():
        files[f".tickets/{name}"] = text
    for rel, text in files.items():
        path = project / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    hook_dir = project / PRODUCT_HOOK_DIR_REL
    hook_dir.mkdir(parents=True, exist_ok=True)
    for source in hook_files():
        shutil.copy2(source, hook_dir / source.name)
    _git(project, "init", "-q", "-b", "main")
    _git(project, "add", "-A")
    _git(project, "commit", "-q", "-m", "fixture project")
    return project


def porcelain(project):
    """``git status --porcelain`` of the project."""
    return _git(project, "status", "--porcelain")


# --------------------------------------------------------------------------
# One hook call
# --------------------------------------------------------------------------

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


def hook_environment(project, home, pycache):
    """A minimal environment: no variable of the calling session is inherited."""
    return {
        "PATH": os.environ.get("PATH", "/usr/local/bin:/usr/bin:/bin"),
        "HOME": str(home),
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "TZ": "UTC",
        "PYTHONPATH": str(REPO_ROOT / GOV_PACKAGE_PARENT_REL),
        "PYTHONPYCACHEPREFIX": str(pycache),
        "CLAUDE_PROJECT_DIR": str(project),
    }


def payload(project, tool_name, tool_input, home):
    """The PreToolUse stdin object of the harness. It names no role."""
    return {
        "session_id": SESSION_ID,
        "transcript_path": str(Path(home) / ".claude" / "projects" / "fixture" / f"{SESSION_ID}.jsonl"),
        "cwd": str(project),
        "permission_mode": "default",
        "hook_event_name": "PreToolUse",
        "tool_name": tool_name,
        "tool_input": tool_input,
        "tool_use_id": "toolu_w1_02_acceptance",
    }


def run_hook(project, tool_name, tool_input, home, pycache):
    """Run the installed hook once and classify what it decided."""
    project = Path(project)
    entry = project / PRODUCT_HOOK_DIR_REL / hook_entry().name
    stdin = json.dumps(payload(project, tool_name, tool_input, home))
    started = time.perf_counter()
    try:
        proc = subprocess.run(
            _argv(entry),
            input=stdin,
            capture_output=True,
            text=True,
            cwd=str(project),
            env=hook_environment(project, home, pycache),
            timeout=HOOK_TIMEOUT_S,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return HookResult("timeout", None, str(exc.stdout or ""), str(exc.stderr or ""),
                          time.perf_counter() - started)
    seconds = time.perf_counter() - started
    return HookResult(classify(proc.returncode, proc.stdout), proc.returncode, proc.stdout, proc.stderr, seconds)


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


def p95(samples):
    ordered = sorted(samples)
    index = max(0, -(-95 * len(ordered) // 100) - 1)
    return ordered[index]
