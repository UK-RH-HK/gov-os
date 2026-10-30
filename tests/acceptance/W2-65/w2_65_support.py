"""Shared helpers for W2-65's acceptance cases (DAEO-e82f).

The hook lines are read from this worktree's two hook sources at run time and run as Claude Code runs them: through
``sh -c``, with the event's JSON on standard input, ``CLAUDE_PROJECT_DIR`` set to a temporary project, and a
temporary ``HOME`` and ``PATH``. The program each line starts is replaced, in the temporary project, by a stand-in
that behaves as the case needs (a syntax error, an exit 1, a crash, a deny decision, ...): what is measured is the
line's own mapping of its program's exit, never the guard's judgement. Nothing here touches the live hooks, the live
settings, the real home or ``$HOME/.local/bin/gov``. Nothing is imported from another ticket's test folder; the way of
running a line follows W2-59's ``w2_59_support.run_hook_line``, rewritten here.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

WORKTREE = Path(__file__).resolve().parents[3]
SRC = WORKTREE / "src"
REPO_SOURCE_REL = ".rulesync/hooks.jsonc"
TEMPLATE_SOURCE_REL = "template/.rulesync/hooks.jsonc"
SOURCES = {"repo": REPO_SOURCE_REL, "template": TEMPLATE_SOURCE_REL}
SUBAGENTSTOP_REL = "template/governance/kernel/hooks/subagentstop.py"
REAL_PYTHON = os.path.realpath(sys.executable)
SYSTEM_PATH = "/usr/bin:/bin"

GUARD_PROGRAM = "hooks/pretooluse.py"        # how the launcher recognises the guard (I1 §2.3, launcher.py GUARD_HOOK)
CONTAINMENT_PROGRAM = "hooks/posttooluse.py"
PROGRAM_PATH = re.compile(r"\$\{?CLAUDE_PROJECT_DIR\}?/([^\"' ;|&)]+\.py)")

TWELVE_FIELDS = (
    "task", "status", "work_completed", "files_changed",
    "evidence", "tests", "discoveries", "risks",
    "lessons", "proposed_decisions", "unresolved",
    "recommended_next_action",
)


# ---------------------------------------------------------------------------------------------------------------
# The hook sources
# ---------------------------------------------------------------------------------------------------------------

def load_jsonc(path: Path):
    text = path.read_text(encoding="utf-8")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        kept = [line for line in text.splitlines() if not line.lstrip().startswith("//")]
        return json.loads("\n".join(kept))


def entries(source: str) -> list:
    """(event, index, command) for every command entry of one hook source (``repo`` or ``template``)."""
    data = load_jsonc(WORKTREE / SOURCES[source])
    found = []
    for event, listed in (data.get("hooks") or {}).items():
        for index, entry in enumerate(listed or []):
            if isinstance(entry, dict) and entry.get("type") == "command":
                found.append((event, index, entry.get("command", "")))
    return found


@dataclass
class Line:
    source: str     # "repo" or "template"
    event: str
    index: int
    command: str

    @property
    def id(self) -> str:
        return f"{self.source}-{self.event}[{self.index}]"

    @property
    def program_rel(self) -> str:
        """The program the line starts, relative to the project (``.../hooks/pretooluse.py``)."""
        found = PROGRAM_PATH.findall(self.command)
        assert found, f"{self.id} names no program under $CLAUDE_PROJECT_DIR: {self.command!r}"
        return found[-1]

    @property
    def program_name(self) -> str:
        return self.program_rel.rsplit("/", 1)[-1]


def guarded_lines() -> list:
    """Every line of both sources that runs the guard (preToolUse) or the containment program (postToolUse and
    postToolUseFailure): the lines DEC-880 item 3 makes fail closed."""
    lines = []
    for source in SOURCES:
        for event, index, command in entries(source):
            if (event == "preToolUse" and GUARD_PROGRAM in command) or CONTAINMENT_PROGRAM in command:
                lines.append(Line(source, event, index, command))
    return lines


# ---------------------------------------------------------------------------------------------------------------
# Running a line
# ---------------------------------------------------------------------------------------------------------------

@dataclass
class Run:
    command: str
    returncode: int | None
    stdout: str
    stderr: str

    def describe(self) -> str:
        return (f"$ sh -c {self.command!r}\nexit: {self.returncode}\n"
                f"stdout:\n{self.stdout[-2000:]}\nstderr:\n{self.stderr[-2000:]}")


@dataclass
class Box:
    home: Path
    local_bin: Path     # <HOME>/.local/bin, where the owner's pin is linked as ``gov``
    tool_bin: Path      # a folder with the ``python3`` the case chooses
    project: Path
    markers: Path

    @property
    def path(self) -> str:
        return f"{self.local_bin}:{self.tool_bin}:{SYSTEM_PATH}"


def _script(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    path.chmod(0o755)


def make_box(base: Path, *, interpreter: str = REAL_PYTHON) -> Box:
    """A temporary home whose ``.local/bin/gov`` names ``interpreter`` on its first line (the form of the owner's
    pin, or of the documented rollback's editable install), a ``python3`` first on ``PATH`` that goes on to
    ``interpreter``, a project folder and a marker folder."""
    base = Path(base)
    home, tool_bin, project, markers = base / "home", base / "tool-bin", base / "project", base / "markers"
    local_bin = home / ".local" / "bin"
    for folder in (local_bin, tool_bin, project, markers):
        folder.mkdir(parents=True)
    _script(local_bin / "gov", f"#!{interpreter}\nimport sys\nfrom gov.cli.main import main\nsys.exit(main())\n")
    _script(tool_bin / "python3", f'#!/bin/sh\nexec "{interpreter}" "$@"\n')
    return Box(home, local_bin, tool_bin, project, markers)


def hook_input(event: str, project: Path) -> dict:
    """What the harness gives each event on standard input, as much of it as a program reads."""
    common = {"session_id": "w265-session", "transcript_path": str(project / "transcript.jsonl"),
              "cwd": str(project)}
    bash = {"tool_name": "Bash", "tool_input": {"command": "true", "description": "w265"},
            "tool_use_id": "toolu_w265_0001"}
    return {
        "preToolUse": {**common, "hook_event_name": "PreToolUse", **bash},
        "postToolUse": {**common, "hook_event_name": "PostToolUse", **bash,
                        "tool_response": {"stdout": "", "stderr": "", "interrupted": False}},
        "postToolUseFailure": {**common, "hook_event_name": "PostToolUseFailure", **bash, "error": "exit code 1"},
    }[event]


def place_program(box: Box, line: Line, text: str | None) -> Path:
    """Put the stand-in program where the line looks for it (``None``: leave it absent)."""
    target = box.project / line.program_rel
    if text is not None:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    return target


def run_line(line: Line, box: Box, timeout: int = 60) -> Run:
    """The line, through ``sh -c`` as Claude Code runs it, in the project's root, with ``CLAUDE_PROJECT_DIR`` set, a
    temporary home and ``PATH``, an engineer's role and a ticket, and the event's JSON on standard input."""
    env = {
        "HOME": str(box.home), "PATH": box.path, "LANG": "C.UTF-8",
        "TMPDIR": os.environ.get("TMPDIR", "/tmp"), "CLAUDE_PROJECT_DIR": str(box.project),
        "GOV_ROLE": "engineer", "GOV_TICKET": "DAEO-w265", "PYTHONDONTWRITEBYTECODE": "1",
    }
    try:
        done = subprocess.run(["sh", "-c", line.command], cwd=str(box.project), env=env,
                              input=json.dumps(hook_input(line.event, box.project)),
                              capture_output=True, text=True, timeout=timeout)
        return Run(line.command, done.returncode, done.stdout, done.stderr)
    except subprocess.TimeoutExpired as exc:
        return Run(line.command, None, str(exc.stdout or ""), f"timed out after {timeout} s")


# ---------------------------------------------------------------------------------------------------------------
# The SubagentStop hook's answer, as Claude Code reads it
# ---------------------------------------------------------------------------------------------------------------

def delivered_block_reason(returncode: int, stdout: str, stderr: str) -> str | None:
    """The reason Claude Code gives a stopped helper, or ``None`` when the stop is not blocked
    (code.claude.com/docs/en/hooks): exit 2 blocks and its reason is standard error (standard output is not
    read); exit 0 blocks only with ``{"decision": "block", "reason": ...}`` on standard output, the reason being
    that ``reason``. Any other exit is a non-blocking error."""
    if returncode == 2:
        return stderr
    if returncode == 0 and stdout.strip():
        try:
            parsed = json.loads(stdout)
        except json.JSONDecodeError:
            return None
        if isinstance(parsed, dict) and parsed.get("decision") == "block":
            reason = parsed.get("reason")
            return reason if isinstance(reason, str) else ""
    return None
