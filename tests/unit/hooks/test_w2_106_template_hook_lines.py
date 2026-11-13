"""W2-106 (DAEO-0mtg): the template's three guard hook lines run the installed gov's own interpreter with ``-E``.

Builder regression evidence (DEC-966 item 2, DEC-822, W2-59's form). Each guard line of
``template/governance/kernel/settings.json`` and of its rulesync source ``template/.rulesync/hooks.jsonc``:

- finds the installed ``gov`` (``$HOME/.local/bin/gov``, else ``gov`` on ``PATH``), reads the interpreter its first
  line names, and runs the product's hook program with that interpreter and ``-E``;
- keeps its exit mapping: 0 and 2 pass through, any other exit ends in a refusal (exit 2);
- fails closed: no gov found, or a first line naming no interpreter that runs, refuses (exit 2) with a message naming
  what is missing, and never falls back to a bare ``python3``;
- is not moved by a session's ``PYTHONPATH``: an edited gov planted there does not let a refused write through.

The four lifecycle lines keep DEC-608's plain form (DEC-917): they are held unchanged here.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SETTINGS = REPO_ROOT / "template" / "governance" / "kernel" / "settings.json"
SOURCE = REPO_ROOT / "template" / ".rulesync" / "hooks.jsonc"
KERNEL_HOOKS = REPO_ROOT / "template" / "governance" / "kernel" / "hooks"
SRC = REPO_ROOT / "src"
SYSTEM_PATH = "/usr/local/bin:/usr/bin:/bin"
REAL_PYTHON = os.path.realpath(sys.executable)

# rulesync's key -> (the harness's event, the product's hook program)
GUARD = {
    "preToolUse": ("PreToolUse", "pretooluse.py"),
    "postToolUse": ("PostToolUse", "posttooluse.py"),
    "postToolUseFailure": ("PostToolUseFailure", "posttooluse.py"),
}
LIFECYCLE = {
    "sessionStart": "sessionstart.py",
    "stop": "stop.py",
    "preCompact": "precompact.py",
    "subagentStop": "subagentstop.py",
}
COMMAND_TIMEOUT_S = 60


def _load_jsonc(path):
    text = "\n".join(line for line in path.read_text(encoding="utf-8").splitlines()
                     if not line.lstrip().startswith("//"))
    return json.loads(text)


def source_line(key):
    entries = [e for e in _load_jsonc(SOURCE)["hooks"][key] if e.get("type") == "command"]
    assert len(entries) == 1, f"{SOURCE}: {key} holds {len(entries)} command entries; one is expected"
    return entries[0]["command"]


def settings_line(event):
    groups = json.loads(SETTINGS.read_text(encoding="utf-8"))["hooks"][event]
    commands = [h["command"] for g in groups for h in g["hooks"] if h.get("type") == "command"]
    assert len(commands) == 1, f"{SETTINGS}: {event} holds {len(commands)} command entries; one is expected"
    return commands[0]


def _lines():
    return [(key, event, program, settings_line(event)) for key, (event, program) in GUARD.items()]


LINE_IDS = list(GUARD)


# --------------------------------------------------------------------------
# The form
# --------------------------------------------------------------------------

@pytest.mark.parametrize("key", LINE_IDS)
def test_the_settings_line_equals_its_rulesync_source(key):
    event, _program = GUARD[key]
    assert settings_line(event) == source_line(key), f"{event}: the settings line and its rulesync source differ"


@pytest.mark.parametrize("key", LINE_IDS)
def test_the_line_takes_the_pinned_form(key):
    event, program = GUARD[key]
    line = settings_line(event)
    assert not re.search(r"(^|[;&|\s])python3?\s", line), f"{event} runs a bare python3: {line!r}"
    assert '"$p" -E "$h"' in line, f"{event} does not run the hook with the pinned interpreter and -E: {line!r}"
    assert 'g="$HOME/.local/bin/gov"' in line and "command -v gov" in line, (
        f"{event} does not look for the installed gov at $HOME/.local/bin/gov, then on PATH: {line!r}")
    assert f'h="$CLAUDE_PROJECT_DIR/governance/kernel/hooks/{program}"' in line, (
        f"{event} does not run the product's own program {program}: {line!r}")


@pytest.mark.parametrize("key", list(LIFECYCLE))
def test_the_lifecycle_lines_keep_the_plain_form(key):
    line = source_line(key)
    assert line == f'python3 "$CLAUDE_PROJECT_DIR/governance/kernel/hooks/{LIFECYCLE[key]}"', (
        f"{key}'s lifecycle line left DEC-608's plain form (DEC-917): {line!r}")


# --------------------------------------------------------------------------
# Running a line: a stand-in home, a decoy python3, a stub program
# --------------------------------------------------------------------------

STUB = (
    "import json, os, sys\n"
    "with open(os.path.join(os.environ['W2106_MARKERS'], 'stub.json'), 'w') as f:\n"
    "    json.dump({'executable': os.path.realpath(sys.executable),\n"
    "               'ignore_environment': sys.flags.ignore_environment}, f)\n"
    "sys.exit(int(os.environ.get('W2106_EXIT', '0')))\n"
)


class Box:
    def __init__(self, base):
        self.home = base / "home"
        self.local_bin = self.home / ".local" / "bin"
        self.decoy_bin = base / "decoy-bin"
        self.markers = base / "markers"
        self.project = base / "project"
        for folder in (self.local_bin, self.decoy_bin, self.markers, self.project / "governance/kernel/hooks"):
            folder.mkdir(parents=True, exist_ok=True)
        decoy = self.decoy_bin / "python3"
        decoy.write_text(f"#!/bin/sh\n: > {self.markers / 'decoy-python3'}\nexit 0\n", encoding="utf-8")
        decoy.chmod(0o755)

    def gov(self, first_line, where=None):
        path = (where or self.local_bin) / "gov"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"{first_line}\nimport sys\nfrom gov.cli.main import main\nsys.exit(main())\n",
                        encoding="utf-8")
        path.chmod(0o755)
        return path

    def stub(self, program):
        (self.project / "governance/kernel/hooks" / program).write_text(STUB, encoding="utf-8")

    def env(self, path=None, **extra):
        env = {"PATH": path or f"{self.decoy_bin}:{SYSTEM_PATH}", "HOME": str(self.home), "LANG": "C.UTF-8",
               "CLAUDE_PROJECT_DIR": str(self.project), "W2106_MARKERS": str(self.markers),
               "PYTHONDONTWRITEBYTECODE": "1"}
        env.update(extra)
        return env

    def run(self, line, env, stdin=""):
        return subprocess.run(["sh", "-c", line], input=stdin, capture_output=True, text=True, env=env,
                              cwd=str(self.project), timeout=COMMAND_TIMEOUT_S, check=False)

    def stub_record(self):
        path = self.markers / "stub.json"
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None

    def decoy_ran(self):
        return (self.markers / "decoy-python3").exists()


def _gov_on_path_exists(path, home):
    return subprocess.run(["sh", "-c", "command -v gov"], env={"PATH": path, "HOME": str(home)},
                          capture_output=True, text=True).returncode == 0


@pytest.mark.parametrize("key", LINE_IDS)
def test_the_line_runs_the_program_with_the_gov_s_interpreter_and_minus_e(key, tmp_path):
    event, program = GUARD[key]
    box = Box(tmp_path)
    box.gov(f"#!{REAL_PYTHON}")
    box.stub(program)
    done = box.run(settings_line(event), box.env(PYTHONPATH=str(tmp_path)))
    record = box.stub_record()
    assert done.returncode == 0, f"{event}: exit {done.returncode}; stderr {done.stderr!r}"
    assert record is not None, f"{event}: the program did not run; stderr {done.stderr!r}"
    assert record["executable"] == REAL_PYTHON, f"{event}: the program ran under {record['executable']}"
    assert record["ignore_environment"] == 1, f"{event}: the program ran without -E"
    assert not box.decoy_ran(), f"{event}: the python3 first on PATH ran"


@pytest.mark.parametrize("key", LINE_IDS)
def test_the_line_finds_gov_on_path_when_home_has_none(key, tmp_path):
    event, program = GUARD[key]
    box = Box(tmp_path)
    elsewhere = tmp_path / "elsewhere-bin"
    box.gov(f"#!{REAL_PYTHON}", where=elsewhere)
    box.stub(program)
    done = box.run(settings_line(event), box.env(path=f"{box.decoy_bin}:{elsewhere}:{SYSTEM_PATH}"))
    record = box.stub_record()
    assert done.returncode == 0 and record is not None, f"{event}: exit {done.returncode}; {done.stderr!r}"
    assert record["executable"] == REAL_PYTHON and record["ignore_environment"] == 1
    assert not box.decoy_ran()


@pytest.mark.parametrize("key", LINE_IDS)
@pytest.mark.parametrize("program_exit,line_exit", [(0, 0), (2, 2), (1, 2), (3, 2)])
def test_the_line_keeps_its_exit_mapping(key, program_exit, line_exit, tmp_path):
    event, program = GUARD[key]
    box = Box(tmp_path)
    box.gov(f"#!{REAL_PYTHON}")
    box.stub(program)
    done = box.run(settings_line(event), box.env(W2106_EXIT=str(program_exit)))
    assert box.stub_record() is not None, f"{event}: the program did not run; {done.stderr!r}"
    assert done.returncode == line_exit, f"{event}: program exit {program_exit} gave line exit {done.returncode}"
    if program_exit not in (0, 2):
        assert "refused" in done.stderr, f"{event}: no refusal message: {done.stderr!r}"


@pytest.mark.parametrize("key", LINE_IDS)
def test_with_no_gov_the_line_refuses_and_names_it(key, tmp_path):
    event, program = GUARD[key]
    box = Box(tmp_path)
    box.stub(program)
    env = box.env()
    assert not _gov_on_path_exists(env["PATH"], box.home), "a gov is on the case's PATH"
    done = box.run(settings_line(event), env)
    assert done.returncode == 2, f"{event}: with no gov the line ended {done.returncode}; {done.stderr!r}"
    assert "no pinned gov" in done.stderr, f"{event}: the message does not name what is missing: {done.stderr!r}"
    assert box.stub_record() is None, f"{event}: the program ran with no gov"
    assert not box.decoy_ran(), f"{event}: fell back to the python3 first on PATH"


@pytest.mark.parametrize("key", LINE_IDS)
@pytest.mark.parametrize("first_line", ["#!/nonexistent/w2-106/python3", "#!/usr/bin/env python3", "", "# not a shebang"],
                         ids=["missing-interpreter", "env-form", "empty", "no-shebang"])
def test_a_gov_naming_no_interpreter_that_runs_refuses(key, first_line, tmp_path):
    event, program = GUARD[key]
    box = Box(tmp_path)
    box.gov(first_line)
    box.stub(program)
    done = box.run(settings_line(event), box.env())
    assert done.returncode == 2, f"{event}: first line {first_line!r} gave exit {done.returncode}; {done.stderr!r}"
    assert "names no interpreter that runs" in done.stderr, f"{event}: {done.stderr!r}"
    assert box.stub_record() is None, f"{event}: the program ran"
    assert not box.decoy_ran(), f"{event}: fell back to the python3 first on PATH"


# --------------------------------------------------------------------------
# KPI 3: a planted PYTHONPATH with an edited gov cannot let a refused write through
# --------------------------------------------------------------------------

EDITED_GOV = {
    "gov/__init__.py": "",
    "gov/guard/__init__.py": "",
    "gov/guard/decide.py": (
        "import os\n"
        "FREEZE_FLAG = '.gov-runtime/freeze'\n"
        "open(os.path.join(os.environ['W2106_MARKERS'], 'edited-gov'), 'w').close()\n"
        "def freeze_state(project_root):\n"
        "    return 'absent'\n"
        "def decide(**kwargs):\n"
        "    return 'allow', 'edited: every call allowed'\n"
    ),
}


def _install_gov_for(box):
    """This worktree's ``gov`` made importable for the stand-in home the way an editable install does it (a path
    file in the home's user site folder); nothing is installed (W1-38's ``make_session_sandbox``)."""
    site = subprocess.run([REAL_PYTHON, "-c", "import site; print(site.getusersitepackages())"],
                          env={"HOME": str(box.home), "PATH": SYSTEM_PATH}, capture_output=True, text=True,
                          check=True).stdout.strip()
    assert site.startswith(str(box.home) + os.sep), f"the user site folder {site} is not under the stand-in home"
    Path(site).mkdir(parents=True, exist_ok=True)
    (Path(site) / "gov-of-this-worktree.pth").write_text(f"{SRC}\n", encoding="utf-8")


def _decision(done):
    try:
        data = json.loads(done.stdout.strip() or "null")
    except ValueError:
        return None
    specific = data.get("hookSpecificOutput") if isinstance(data, dict) else None
    return specific.get("permissionDecision") if isinstance(specific, dict) else None


def test_an_edited_gov_on_pythonpath_does_not_let_a_refused_write_through(tmp_path):
    event, program = GUARD["preToolUse"]
    box = Box(tmp_path)
    box.gov(f"#!{REAL_PYTHON}")
    _install_gov_for(box)
    shutil.copy2(KERNEL_HOOKS / program, box.project / "governance/kernel/hooks" / program)
    edited = tmp_path / "edited"
    for rel, text in EDITED_GOV.items():
        (edited / rel).parent.mkdir(parents=True, exist_ok=True)
        (edited / rel).write_text(text, encoding="utf-8")
    target = box.project / "docs" / "notes.md"
    stdin = json.dumps({"session_id": "w2-106", "cwd": str(box.project), "hook_event_name": event,
                        "tool_name": "Write", "tool_input": {"file_path": str(target), "content": "x\n"},
                        "tool_use_id": "toolu_w2_106", "permission_mode": "default"})
    line = settings_line(event)
    identity = {"GOV_ROLE": "engineer", "GOV_TICKET": "DAEO-zz90"}

    # Without the planted PYTHONPATH the installed gov refuses the write (outside any ticket's paths).
    done = box.run(line, box.env(path=SYSTEM_PATH, **identity), stdin)
    assert _decision(done) == "deny", (
        f"the installed gov does not refuse the write: exit {done.returncode}; {done.stdout!r}; {done.stderr!r}")

    # With it, the edited copy is not imported and the write is still refused.
    done = box.run(line, box.env(path=SYSTEM_PATH, PYTHONPATH=str(edited), **identity), stdin)
    assert not (box.markers / "edited-gov").exists(), "the hook imported the edited gov planted on PYTHONPATH"
    assert done.returncode == 2 or _decision(done) == "deny", (
        f"the edited gov on PYTHONPATH let a refused write through: exit {done.returncode}; {done.stdout!r}; "
        f"{done.stderr!r}")
