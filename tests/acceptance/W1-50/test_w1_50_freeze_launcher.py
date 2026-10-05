"""W1-50, KPI line 2 (DEC-402): the launcher and the flag's path.

"gov launch does not deny the freeze flag's path when the flag does not exist
at launch, so a launched session leaves no placeholder there."

Cause, confirmed on a live session on 2026-10-05: the sandbox puts an empty
file at every name its settings deny by a literal rule when that name does not
exist, for as long as a command of the session runs. The guard of every other
session, outside the sandbox, read the one at ``.gov-runtime/freeze`` as a
freeze.

Three parts:

- **The built settings**, read as W1-46's suite reads them (the ``--settings``
  value a stand-in CLI is started with): no literal ``Edit`` rule names the
  flag when nothing is at its path; a flag that exists at launch keeps its
  literal rule, as every name under ``.gov-runtime/`` does (DEC-311); the
  patterns still cover the path for the file tools; the launcher's other
  by-name rules are as they were. What the launcher does with an *unmarked*
  file at the path is an open package (README) and is not tested.
- **What the guard still holds** once the literal rule is gone: a worker's
  Write, Edit and recognisable Bash writes to the flag's path are denied
  whether nothing, a placeholder or a real flag is there. These hold today.
- **One live session** (``local_only``, as W1-46 marks its own; the ticket
  lead runs it): no file appears at the path while a worker's Bash runs.
"""

from __future__ import annotations

import os
import shutil
import threading
import time
from pathlib import Path

import pytest

import w1_50_freeze_support as support
from w1_50_freeze_support import (  # noqa: F401  fixtures
    freeze_launch, freeze_launch_base, freeze_launch_project, freeze_project, freeze_sandbox)

launch_support = support.launch_support
ENGINEER = support.ENGINEER
FLAG_NAME = "freeze"
# The launcher's by-name rules for the names that would otherwise be matched as ``scratch`` (W1-46): unchanged.
OTHER_NAMES = ["s", "sc", "scr", "scra", "scrat", "scratc"]


# --------------------------------------------------------------------------
# The built settings
# --------------------------------------------------------------------------

@pytest.mark.parametrize("role", launch_support.WORKER_ROLES)
def test_no_literal_rule_names_the_flag_when_nothing_is_at_its_path(freeze_launch, freeze_launch_project,
                                                                    freeze_sandbox, role):
    result = freeze_launch(role)
    names = support.literal_runtime_names(result, freeze_launch_project, freeze_sandbox)
    assert FLAG_NAME not in names, (
        f"the settings built for a launched {role} deny {support.FLAG_REL} by a literal Edit rule although nothing "
        f"is there: the sandbox will put a placeholder at the path (DEC-402). Literal names: {names}"
    )


def test_no_literal_rule_names_the_flag_when_the_runtime_directory_does_not_exist(freeze_launch,
                                                                                  freeze_launch_project,
                                                                                  freeze_sandbox):
    shutil.rmtree(freeze_launch_project / support.RUNTIME_REL)
    result = freeze_launch(ENGINEER)
    names = support.literal_runtime_names(result, freeze_launch_project, freeze_sandbox)
    assert FLAG_NAME not in names, f"a literal Edit rule names the flag in a project with no runtime directory: {names}"


def test_a_flag_that_exists_at_launch_keeps_its_literal_rule(freeze_launch, freeze_launch_project, freeze_sandbox):
    """DEC-311: every name that exists at launch. A real flag stays protected inside the sandbox."""
    support.put_text(freeze_launch_project, support.A_MARKER_LINE)
    result = freeze_launch(ENGINEER)
    names = support.literal_runtime_names(result, freeze_launch_project, freeze_sandbox)
    assert FLAG_NAME in names, (
        f"a marked flag exists at launch and no literal Edit rule names it: a worker's Bash could remove it. "
        f"Literal names: {names}"
    )


@pytest.mark.parametrize("at_launch", ("nothing", "a-marked-flag"))
def test_the_patterns_still_deny_the_flag_to_the_file_tools(freeze_launch, freeze_launch_project, freeze_sandbox,
                                                            at_launch):
    """DEC-180: the pattern rules bind Write and Edit whatever exists. Only the literal rule changes."""
    if at_launch == "a-marked-flag":
        support.put_text(freeze_launch_project, support.A_MARKER_LINE)
    result = freeze_launch(ENGINEER)
    assert launch_support.edit_denied(result, support.FLAG_REL, freeze_launch_project, freeze_sandbox), (
        f"no Edit deny rule of the built settings covers {support.FLAG_REL}; rules: "
        f"{launch_support.deny_rules(result.settings(), 'Edit')}"
    )


def test_the_other_by_name_rules_are_as_they_were(freeze_launch, freeze_launch_project, freeze_sandbox):
    """DEC-402 names the flag alone: the names at launch and the six prefixes of ``scratch`` keep their rules."""
    at_launch = sorted(name for name in os.listdir(freeze_launch_project / support.RUNTIME_REL) if name != "scratch")
    result = freeze_launch(ENGINEER)
    names = support.literal_runtime_names(result, freeze_launch_project, freeze_sandbox)
    missing = [name for name in at_launch + OTHER_NAMES if name not in names]
    assert not missing, f"the built settings lost the literal Edit rule of {missing}; literal names: {names}"
    assert "scratch" not in names, f"a literal Edit rule closes scratch: {names}"


# --------------------------------------------------------------------------
# What the guard still holds
# --------------------------------------------------------------------------

FLAG = support.FLAG_REL
SCRATCH_FILE = ".gov-runtime/scratch/w1-50-held.txt"
BASH_WRITES = (
    f"rm {FLAG}",
    f"rm -f {FLAG}",
    f"mv {FLAG} {SCRATCH_FILE}",
    f"mv {support.OWN_REL} {FLAG}",
    f"cp {support.OWN_REL} {FLAG}",
    f"touch {FLAG}",
    f"echo 'FROZEN owner 2026-10-05T00:00:00Z' > {FLAG}",
    f": > {FLAG}",
    f"echo x >> {FLAG}",
    f"ln -s {{root}}/{support.OWN_REL} {FLAG}",
    f"ln {support.OWN_REL} {FLAG}",
)
AT_THE_PATH = {
    "nothing": lambda project: None,
    "a-placeholder": support.put_placeholder,
    "a-marked-flag": lambda project: support.put_text(project, support.A_MARKER_LINE),
}


@pytest.mark.parametrize("state", sorted(AT_THE_PATH))
@pytest.mark.parametrize("role", (ENGINEER, support.guard_support.TEST_DESIGNER))
def test_the_guard_denies_a_worker_s_write_to_the_flag_s_path(freeze_project, freeze_sandbox, state, role):
    """DEC-176, DEC-311: ``.gov-runtime/`` outside scratch is denied to every role, flag or no flag.

    With a placeholder at the path the project is not frozen (DEC-402), so
    these denials are the path rule's own.
    """
    AT_THE_PATH[state](freeze_project)
    before = os.lstat(support.flag(freeze_project)) if state != "nothing" else None
    for tool_name in ("Write", "Edit"):
        result = support.guard_write(freeze_project, freeze_sandbox, tool_name, rel=FLAG, role=role)
        assert result.decision == "deny", f"with {state} at the path, {tool_name} on {FLAG} by {role}: " \
                                          f"{result.describe()}"
    for command in BASH_WRITES:
        command = command.format(root=freeze_project)
        result = support.guard_bash(freeze_project, freeze_sandbox, command, role=role)
        assert result.decision == "deny", f"with {state} at the path, Bash `{command}` by {role}: {result.describe()}"
    after = os.lstat(support.flag(freeze_project)) if os.path.lexists(support.flag(freeze_project)) else None
    assert (before is None) == (after is None), f"asking the guard changed what is at {FLAG}"


# --------------------------------------------------------------------------
# One live session
# --------------------------------------------------------------------------

SCRATCH = ".gov-runtime/scratch/w1-50"
SESSION_TIMEOUT_S = 420.0
NOT_INHERITED = ("GOV_ROLE", "GOV_TICKET", "CLAUDECODE", "CLAUDE_CODE_ENTRYPOINT", "CLAUDE_PROJECT_DIR",
                 "CLAUDE_CODE_SSE_PORT")
PROBE = f"""#!/bin/bash
# W1-50 acceptance probe: what a launched worker's Bash sees at the flag's path, and time for the test to look.
OUT={SCRATCH}/results.txt
: > "$OUT"
if [ -e {FLAG} ] || [ -L {FLAG} ]; then echo "inside=present" >> "$OUT"; else echo "inside=absent" >> "$OUT"; fi
sleep 10
if [ -e {FLAG} ] || [ -L {FLAG} ]; then echo "inside_later=present" >> "$OUT"; else echo "inside_later=absent" >> "$OUT"; fi
echo "end=1" >> "$OUT"
"""
PROMPT = ("Do exactly this one step, once, and nothing else. If it is refused or fails, do not retry it and do not "
          f"work around it. Run this Bash command as written: bash {SCRATCH}/probe.sh  Then answer DONE.")


def _watch(paths, seen, stop):
    """Note every moment something is at one of ``paths``, as the file system outside the sandbox shows it."""
    while not stop.is_set():
        for name, path in paths.items():
            try:
                status = os.lstat(path)
            except OSError:
                continue
            seen.setdefault(name, (oct(status.st_mode), status.st_size))
        time.sleep(0.05)


@pytest.mark.local_only
def test_a_launched_session_leaves_no_placeholder_at_the_flag_s_path(freeze_launch_base, tmp_path):
    """A real engineer session, one Bash call of about ten seconds, watched from outside the sandbox.

    ``.gov-runtime/s`` is the control: it keeps its by-name rule and does not
    exist, so the sandbox's placeholder is expected there while the command
    runs. It shows that the watcher sees a placeholder when there is one.
    """
    missing = [name for name in ("bwrap", "socat") if shutil.which(name) is None]
    if not (Path.home() / launch_support.CLI_REL).is_file():
        missing.append("~/.local/bin/claude")
    if missing:
        pytest.fail(f"a launched session needs {missing} on this machine", pytrace=False)

    project = tmp_path / "repo"
    shutil.copytree(freeze_launch_base, project, symlinks=True)
    sandbox = launch_support.cli_support.make_sandbox(tmp_path / "sandbox")
    support.w47.configure_stand_in(project, support.w47.make_stand_in(sandbox.elsewhere / "held-out-stand-in"))
    launch_support.write(project, f"{SCRATCH}/probe.sh", PROBE)
    runtime = project / support.RUNTIME_REL
    assert not os.path.lexists(runtime / FLAG_NAME) and not os.path.lexists(runtime / "s")

    seen, stop = {}, threading.Event()
    watcher = threading.Thread(target=_watch, args=({"flag": runtime / FLAG_NAME, "control": runtime / "s"}, seen,
                                                    stop), daemon=True)
    env = {key: value for key, value in os.environ.items() if key not in NOT_INHERITED}
    env.update({"PYTHONPATH": str(project / "src"), "PYTHONPYCACHEPREFIX": str(sandbox.pycache)})
    watcher.start()
    try:
        run = launch_support.run_gov(project, sandbox, "launch", ENGINEER, launch_support.TICKET_OF[ENGINEER], "--",
                                     "-p", PROMPT, "--permission-mode", "acceptEdits", "--model", "haiku",
                                     "--max-turns", "6", "--allowedTools", "Bash", env=env, timeout=SESSION_TIMEOUT_S)
    finally:
        stop.set()
        watcher.join(timeout=5)

    results_path = project / SCRATCH / "results.txt"
    if not results_path.is_file() or "end=1" not in results_path.read_text(encoding="utf-8"):
        pytest.fail(f"the launched session did not run the probe to its end\n{run.describe()[-1500:]}", pytrace=False)
    results = dict(line.split("=", 1) for line in results_path.read_text(encoding="utf-8").splitlines() if "=" in line)

    assert "flag" not in seen, (
        f"while the session's Bash ran, something was at {FLAG} outside the sandbox (mode, size: {seen['flag']}): "
        f"the launcher still denies the path by name (DEC-402)"
    )
    assert (results.get("inside"), results.get("inside_later")) == ("absent", "absent"), (
        f"inside the sandbox the worker's Bash saw something at {FLAG}: {results}"
    )
    assert not os.path.lexists(runtime / FLAG_NAME), f"the session left something at {FLAG}"
    assert "control" in seen, (
        "the watcher saw no placeholder at .gov-runtime/s, which keeps its by-name rule: this case did not observe "
        "the sandbox, so it shows nothing about the flag's path"
    )
