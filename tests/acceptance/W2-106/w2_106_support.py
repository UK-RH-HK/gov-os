"""W2-106 acceptance support: the template's three guard lines, the pinned form they must take, and their runs.

Everything is read relative to the repository this file sits in (``REPO_ROOT``), so that merged into the ticket's
worktree the cases judge that worktree's template and code (DEC-732; README, "How the cases run the code of the
worktree they sit in").

- **The lines under test**: the three guard lines of the template, in ``template/governance/kernel/settings.json``
  (Claude Code's form: ``hooks.<Event>[].hooks[].command``) and in their rulesync source
  ``template/.rulesync/hooks.jsonc`` (``hooks.<event>[].command``): PreToolUse runs ``pretooluse.py``, PostToolUse and
  PostToolUseFailure on Bash run ``posttooluse.py``.
- **The pinned form, by reference** (DEC-822, W2-59; KPI success 1): this repository's own guard line, the
  ``preToolUse`` entry of ``.rulesync/hooks.jsonc``. The template's line is that line with the template's program path
  in the place of its own.
- **A stand-in pin** (W2-59's ``make_stand_in``): a wheel of this repository's ``src/``, installed non-editable in a
  ``--system-site-packages`` environment in a short temporary folder, instrumented after its install (a ``pin-python-``
  marker when its interpreter starts, ``pin-gov-`` when its package is imported). It is reached as the owner's pin is:
  a link at ``<HOME>/.local/bin/gov``, or a ``gov`` on ``PATH``, ``HOME`` a temporary folder.
- **A line runs as Claude Code runs it**: ``sh -c <line>`` in the project's root, the event's JSON on standard input,
  ``CLAUDE_PROJECT_DIR`` set, an engineer's role and a ticket, a temporary ``HOME`` and a ``PATH`` the case writes,
  with a decoy ``python3`` (and ``python``) first on it that leaves a marker and goes on to the real interpreter.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
_TESTS = REPO_ROOT / "tests" / "acceptance"
for _suite in ("W2-59", "W2-90"):
    if str(_TESTS / _suite) not in sys.path:
        sys.path.insert(0, str(_TESTS / _suite))

import w2_59_support as pin_support  # noqa: E402  (the stand-in pin, the refused write, the edited gov)

TEMPLATE_SETTINGS_REL = "template/governance/kernel/settings.json"
TEMPLATE_SOURCE_REL = "template/.rulesync/hooks.jsonc"
REFERENCE_SOURCE_REL = ".rulesync/hooks.jsonc"          # this repository's own lines: the pinned form (DEC-822)
REFERENCE_EVENT = "preToolUse"
KERNEL_HOOKS_REL = "governance/kernel/hooks"            # where Copier puts the hook programs in a project
PROGRAM_PATH = re.compile(r"\$\{?CLAUDE_PROJECT_DIR\}?/[^\"' ;|&)]+\.py")
PROGRAM_PLACE = "<the hook program's path>"
REAL_PYTHON = os.path.realpath(sys.executable)
SYSTEM_PATH = "/usr/bin:/bin"
TICKET = "DAEO-w2106"

FILES = {"settings": TEMPLATE_SETTINGS_REL, "source": TEMPLATE_SOURCE_REL}
# The three guard lines: the harness's event name, the rulesync key, the program, the matcher.
GUARD_LINES = (
    ("PreToolUse", "preToolUse", "pretooluse.py", None),
    ("PostToolUse", "postToolUse", "posttooluse.py", "Bash"),
    ("PostToolUseFailure", "postToolUseFailure", "posttooluse.py", "Bash"),
)
EVENTS = tuple(event for event, _key, _program, _matcher in GUARD_LINES)
PROGRAM_OF = {event: program for event, _key, program, _matcher in GUARD_LINES}
RULESYNC_KEY = {event: key for event, key, _program, _matcher in GUARD_LINES}
# Each of the three lines in both files: (file, event), with an id.
LINE_PARAMS = [(name, event) for name in FILES for event in EVENTS]
LINE_IDS = [f"{name}-{event}" for name, event in LINE_PARAMS]


# ---------------------------------------------------------------------------------------------------------------
# Reading the lines
# ---------------------------------------------------------------------------------------------------------------

def load_jsonc(path: Path):
    """A JSON file, or a JSON-with-comments file whose comments are whole lines (as the rulesync sources are)."""
    text = Path(path).read_text(encoding="utf-8")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        kept = [line for line in text.splitlines() if not line.lstrip().startswith("//")]
        return json.loads("\n".join(kept))


def settings_commands(settings: dict, event: str, program: str) -> list:
    """The commands a Claude Code settings object registers under ``event`` that run ``program``."""
    found = []
    for group in (settings.get("hooks") or {}).get(event) or []:
        for hook in (group.get("hooks") or []) if isinstance(group, dict) else []:
            command = hook.get("command") if isinstance(hook, dict) else None
            if isinstance(command, str) and program in command:
                found.append(command)
    return found


def source_commands(source: dict, key: str, program: str) -> list:
    """The commands a rulesync hooks source holds under ``key`` that run ``program``."""
    return [entry.get("command") for entry in (source.get("hooks") or {}).get(key) or []
            if isinstance(entry, dict) and isinstance(entry.get("command"), str) and program in entry["command"]]


def template_line(name: str, event: str) -> str:
    """The one guard line the template's ``name`` file (``settings`` or ``source``) holds under ``event``."""
    rel = FILES[name]
    data = load_jsonc(REPO_ROOT / rel)
    program = PROGRAM_OF[event]
    if name == "settings":
        commands = settings_commands(data, event, program)
    else:
        commands = source_commands(data, RULESYNC_KEY[event], program)
    assert len(commands) == 1, f"{rel} holds {len(commands)} {event} lines running {program}; one is expected: {commands}"
    return commands[0]


def reference_line() -> str:
    """This repository's own guard line: the pinned form the KPI names by reference (DEC-822, W2-59)."""
    source = load_jsonc(REPO_ROOT / REFERENCE_SOURCE_REL)
    commands = source_commands(source, REFERENCE_EVENT, "pretooluse.py")
    assert len(commands) == 1, f"{REFERENCE_SOURCE_REL} holds {len(commands)} preToolUse guard lines: {commands}"
    return commands[0]


def program_paths(command: str) -> list:
    return PROGRAM_PATH.findall(command)


def form_of(command: str) -> str:
    """The line with its one hook program's path exchanged for ``PROGRAM_PLACE``."""
    paths = program_paths(command)
    assert len(set(paths)) == 1, f"the line names {sorted(set(paths)) or 'no'} hook program path(s); one is expected"
    return command.replace(paths[0], PROGRAM_PLACE)


def expected_program_path(event: str) -> str:
    return f"$CLAUDE_PROJECT_DIR/{KERNEL_HOOKS_REL}/{PROGRAM_OF[event]}"


BARE_PYTHON = re.compile(r"(?<![\w/.$-])python3?(?![\w./-])")
MINUS_E = re.compile(r"(?<![\w-])-E(?![\w-])")


# ---------------------------------------------------------------------------------------------------------------
# A box: a temporary home, a decoy python3 first on PATH, a project holding a program, a marker folder
# ---------------------------------------------------------------------------------------------------------------

@dataclass(frozen=True)
class Box:
    base: Path
    home: Path
    local_bin: Path      # <HOME>/.local/bin
    decoy_bin: Path      # a decoy python3 and python, which leave markers and go on to the real interpreter
    path_bin: Path       # a folder the case may put first on PATH (for a gov on PATH)
    markers: Path
    project: Path

    @property
    def home_gov(self) -> Path:
        return self.local_bin / "gov"

    def marks(self, prefix: str) -> list:
        return sorted(path.name for path in self.markers.iterdir() if path.name.startswith(prefix))

    def record(self, program: str):
        """What the stand-in program recorded when it ran (``None`` when it never ran)."""
        path = self.markers / f"program-{program}.json"
        return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None


def script(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    path.chmod(0o755)
    return path


def make_box(base: Path) -> Box:
    base = Path(base)
    home, decoy_bin, path_bin, markers, project = (base / "home", base / "decoy-bin", base / "path-bin",
                                                    base / "markers", base / "project")
    local_bin = home / ".local" / "bin"
    for folder in (local_bin, decoy_bin, path_bin, markers, project):
        folder.mkdir(parents=True)
    for name in ("python3", "python"):
        script(decoy_bin / name, f'#!/bin/sh\n: > "{markers}/path-{name}-$$"\nexec "{REAL_PYTHON}" "$@"\n')
    return Box(base, home, local_bin, decoy_bin, path_bin, markers, project)


def link_gov(target: Path, link: Path) -> Path:
    link.parent.mkdir(parents=True, exist_ok=True)
    os.symlink(target, link)
    return link


def other_gov(box: Box) -> Path:
    """A second installed ``gov`` (on ``PATH``), whose first line names an interpreter of its own that leaves an
    ``other-python-`` marker and goes on to the real interpreter."""
    interpreter = script(box.base / "other-env" / "bin" / "python",
                         f'#!/bin/sh\n: > "{box.markers}/other-python-$$"\nexec "{REAL_PYTHON}" "$@"\n')
    return script(box.path_bin / "gov", f"#!{interpreter}\nimport sys\nfrom gov.cli.main import main\nsys.exit(main())\n")


# What the stand-in program does once it has recorded how it was started.
DENY = {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                               "permissionDecisionReason": "w2106 stand-in program's refusal"}}
ENDINGS = {
    "exit-0-with-output": "sys.stdout.write(%r)\nsys.exit(0)\n" % json.dumps(DENY),
    "exit-2-with-refusal": "sys.stderr.write('w2106 refused ' + str(call.get('tool_use_id')))\nsys.exit(2)\n",
    "exit-1": "sys.exit(1)\n",
    "killed": "import signal\nos.kill(os.getpid(), signal.SIGKILL)\n",
    "allow": "sys.exit(0)\n",
}


def place_program(box: Box, program: str, ending: str = "allow") -> Path:
    """A stand-in for the kernel's hook program at ``<project>/governance/kernel/hooks/<program>``: it records how
    it was started (interpreter, prefix, whether ``-E`` is in force, its import path) and ends as ``ending`` says."""
    record = box.markers / f"program-{program}.json"
    text = (
        "import json, os, sys\n"
        "call = json.loads(sys.stdin.read() or '{}')\n"
        f"with open({str(record)!r}, 'w') as handle:\n"
        "    json.dump({'executable': sys.executable, 'prefix': sys.prefix,\n"
        "               'ignore_environment': sys.flags.ignore_environment, 'path': sys.path}, handle)\n"
        + ENDINGS[ending]
    )
    return script(box.project / KERNEL_HOOKS_REL / program, text)


def hook_input(event: str, project: Path) -> dict:
    common = {"session_id": "w2106-session", "transcript_path": str(project / "transcript.jsonl"),
              "cwd": str(project), "permission_mode": "default", "hook_event_name": event}
    bash = {"tool_name": "Bash", "tool_input": {"command": "true", "description": "w2106"},
            "tool_use_id": "toolu_w2106_0001"}
    extra = {"PreToolUse": {}, "PostToolUse": {"tool_response": {"stdout": "", "stderr": "", "interrupted": False}},
             "PostToolUseFailure": {"error": "Exit code 1"}}[event]
    return {**common, **bash, **extra}


@dataclass(frozen=True)
class Run:
    command: str
    returncode: object
    stdout: str
    stderr: str

    def describe(self) -> str:
        return (f"$ sh -c <line>\nexit: {self.returncode}\nstdout:\n{self.stdout[-2000:]}\n"
                f"stderr:\n{self.stderr[-2000:]}")


def line_env(box: Box, project: Path, path: str, inherited: dict | None = None) -> dict:
    env = {"HOME": str(box.home), "PATH": path, "LANG": "C.UTF-8", "TMPDIR": os.environ.get("TMPDIR", "/tmp"),
           "CLAUDE_PROJECT_DIR": str(project), "GOV_ROLE": "engineer", "GOV_TICKET": TICKET,
           "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull}
    env.update(inherited or {})
    return env


def run_line(command: str, box: Box, *, path: str, project: Path | None = None, payload: dict | None = None,
             event: str = "PreToolUse", inherited: dict | None = None, timeout: int = 120) -> Run:
    """One line through ``sh -c``, as Claude Code runs a hook's command, in the project's root."""
    project = Path(project or box.project)
    stdin = json.dumps(payload if payload is not None else hook_input(event, project))
    try:
        done = subprocess.run(["sh", "-c", command], cwd=str(project), env=line_env(box, project, path, inherited),
                              input=stdin, capture_output=True, text=True, timeout=timeout)
        return Run(command, done.returncode, done.stdout, done.stderr)
    except subprocess.TimeoutExpired:
        return Run(command, None, "", f"timed out after {timeout} s")


def path_of(*folders) -> str:
    return ":".join([*(str(folder) for folder in folders), SYSTEM_PATH])


def assert_no_gov_on(path: str) -> None:
    found = shutil.which("gov", path=path)
    assert found is None, f"the case's PATH must hold no gov, and {found} is on it: the case would measure nothing"


def denies(done: Run) -> bool:
    """Whether a PreToolUse answer blocks the call (Claude Code's contract): exit 2, or a deny decision with exit 0."""
    return pin_support.denies(pin_support.Run(("sh",), "", done.returncode, done.stdout, done.stderr))
