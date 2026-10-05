"""Shared helpers for the launcher half of the W1-28 acceptance tests (DEC-386).

``gov launch`` is driven as W1-46's tests drive it: the project's own ``gov``
package, a temporary project, a temporary HOME, and a stand-in for the Claude
Code CLI at ``<HOME>/.local/bin/claude``. No CLI session is ever started and
nothing reaches the network.

The stand-in of this suite does what W1-46's does (it records its arguments,
its environment and the settings it was started with, in the same form) and it
also *uses* the session's temp folder, as a session would: it leaves files and
links there, waits, and ends with a chosen exit code. What it does is read
from a plan file the test writes.

**The session's temp folder** is found as W1-46 finds it: every variable of the
session whose name holds ``TMP`` (the settings' ``env`` block wins over the
process environment, DEC-183) and whose value is a directory other than the
``TMPDIR`` the launcher itself was started with. The launcher of W1-46 names
one such directory, in ``TMPDIR`` and ``CLAUDE_CODE_TMPDIR``.
"""

from __future__ import annotations

import json
import os
import signal
import stat
import subprocess
import sys
import time
from pathlib import Path

import yaml

_TESTS = Path(__file__).resolve().parent.parent
for _name in ("W1-46",):
    _directory = str(_TESTS / _name)
    if _directory not in sys.path:
        sys.path.insert(0, _directory)

import w1_46_support as w46   # noqa: E402  the temporary project, the launch, what the built settings say

w47 = w46.w47
check_support = w46.check_support
cli_support = w46.cli_support

REPO_ROOT = Path(__file__).resolve().parents[3]
ROSTER_REL = w46.ROSTER_REL

ENGINEER, RESEARCH = w46.ENGINEER, w46.RESEARCH
PRODUCT_SPEC = check_support.PRODUCT_SPEC
PRODUCT_SPEC_TICKET = check_support.PRODUCT_SPEC_TICKET_ID      # in progress, role product-spec
ENGINEER_TICKET = check_support.TICKET_ID                       # in progress, role engineer
TICKET_OF = {**w46.TICKET_OF, PRODUCT_SPEC: PRODUCT_SPEC_TICKET}
LAUNCHED_ROLES = w46.WORKER_ROLES + (PRODUCT_SPEC,)             # DEC-386: the four of W1-46 and product-spec
# Inside and outside the fixture ticket's allowed_paths (template/governance/kernel/roles/**, docs/spec/**).
PRODUCT_SPEC_OWN_PATH = "docs/spec/feature.md"
PRODUCT_SPEC_OTHER_PATH = "docs/notes.md"

# What the roster entry of product-spec must hold once the launcher starts the role (DEC-386, DEC-163).
ROSTER_SESSION = "gov launch product-spec <ticket>"
ROSTER_PROFILE = "empty"

WAIT_S = 30.0


# --------------------------------------------------------------------------
# The temporary project
# --------------------------------------------------------------------------

def make_project(directory):
    """W1-46's launch fixture project, with the roster entry DEC-386 asks for.

    The entry is written here because the committed roster is the ticket lead's
    to change: a launcher that reads the roster to know the launched roles then
    finds the role in this project, and a launcher that does not is unaffected.
    """
    project = w46.make_project(directory)
    path = project / ROSTER_REL
    roster = yaml.safe_load(path.read_text(encoding="utf-8"))
    roster["roles"][PRODUCT_SPEC].update({"session": ROSTER_SESSION, "network_profile": ROSTER_PROFILE})
    path.write_text(yaml.safe_dump(roster, sort_keys=False), encoding="utf-8")
    check_support.commit_all(project, "roster: product-spec is launched (DEC-386)")
    return project


def committed_roster_entry(role, root=REPO_ROOT):
    """The entry of ``role`` in this repository's roster."""
    roster = yaml.safe_load((Path(root) / ROSTER_REL).read_text(encoding="utf-8"))
    entry = (roster or {}).get("roles", {}).get(role)
    assert isinstance(entry, dict), f"{ROSTER_REL} has no entry for {role}"
    return entry


# --------------------------------------------------------------------------
# The stand-in CLI that uses its temp folder
# --------------------------------------------------------------------------

_STUB = r'''#!@PYTHON@
"""Stand-in for the Claude Code CLI (W1-28 acceptance tests). Starts nothing; records its call; uses its temp folder."""
import json, os, sys, time

args = sys.argv[1:]
settings = []
i = 0
while i < len(args):
    value = None
    if args[i] == "--settings" and i + 1 < len(args):
        value = args[i + 1]
        i += 1
    elif args[i].startswith("--settings="):
        value = args[i].split("=", 1)[1]
    if value is not None:
        entry = {"value": value, "inline": value.lstrip().startswith("{")}
        if entry["inline"]:
            entry["text"] = value
        else:
            entry["realpath"] = os.path.realpath(value)
            entry["is_symlink"] = os.path.islink(value)
            try:
                with open(value, encoding="utf-8") as handle:
                    entry["text"] = handle.read()
            except OSError as exc:
                entry["text"] = None
                entry["error"] = str(exc)
        settings.append(entry)
    i += 1
named = dict(os.environ)
for entry in settings:
    try:
        block = json.loads(entry["text"]).get("env")
    except Exception:
        block = None
    if isinstance(block, dict):
        named.update({k: v for k, v in block.items() if isinstance(v, str)})
directories = {v: os.path.isdir(v) for k, v in named.items() if "TMP" in k.upper() and v.startswith("/")}
shared = os.path.realpath(@SHARED@)
folders = sorted(v for v, is_directory in directories.items() if is_directory and os.path.realpath(v) != shared)
plan = {}
if os.path.isfile(@PLAN@):
    with open(@PLAN@, encoding="utf-8") as handle:
        plan = json.load(handle)
for folder in folders:
    for rel, text in plan.get("files", {}).items():
        path = os.path.join(folder, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(text)
    for rel, target in plan.get("links", {}).items():
        path = os.path.join(folder, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        os.symlink(target, path)
record = {"kind": "session", "argv0": sys.argv[0], "args": args, "cwd": os.getcwd(), "env": dict(os.environ),
          "settings": settings, "directories": directories, "folders": folders}
with open(@LOG@, "a", encoding="utf-8") as handle:
    handle.write(json.dumps(record) + "\n")
if plan.get("ready"):
    with open(plan["ready"] + ".part", "w", encoding="utf-8") as handle:
        json.dump(folders, handle)
    os.replace(plan["ready"] + ".part", plan["ready"])
if plan.get("wait"):
    time.sleep(float(plan["wait"]))
sys.exit(int(plan.get("exit", 0)))
'''


def _plan_file(cli):
    return Path(str(cli.log) + ".plan")


def install_stand_in_cli(sandbox):
    """W1-46's stand-in on PATH (the bare-name decoy) and this suite's stand-in at ``<HOME>/.local/bin/claude``."""
    cli = w46.install_stand_in_cli(sandbox)
    text = (_STUB.replace("@PYTHON@", sys.executable).replace("@SHARED@", repr(str(sandbox.tmpdir)))
            .replace("@PLAN@", repr(str(_plan_file(cli)))).replace("@LOG@", repr(str(cli.log))))
    cli.path.write_text(text, encoding="utf-8")
    cli.path.chmod(cli.path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return cli


def plan(cli, files=None, links=None, exit_code=0, ready=None, wait=None):
    """What the next stand-in sessions do in their temp folder, and how they end."""
    data = {"files": dict(files or {}), "links": {rel: str(target) for rel, target in (links or {}).items()},
            "exit": int(exit_code)}
    if ready is not None:
        data["ready"] = str(ready)
    if wait is not None:
        data["wait"] = float(wait)
    _plan_file(cli).write_text(json.dumps(data), encoding="utf-8")


def temp_folder(result):
    """The one temp folder of its own the session was given; it was a directory while the session ran."""
    folders = result.session().get("folders")
    assert folders is not None, "the session was not started through this suite's stand-in CLI"
    assert len(folders) == 1, (
        f"the session was not given exactly one temp folder of its own (found {folders}); temp variables it saw: "
        f"{result.session()['directories']}"
    )
    return Path(folders[0])


def entries(directory):
    """Every entry under ``directory``, by its relative path; links are not followed."""
    found = []
    for current, names, files in os.walk(directory):
        for name in names + files:
            found.append(os.path.relpath(os.path.join(current, name), directory))
    return sorted(found)


def assert_removed(folder, when):
    assert not os.path.lexists(folder), (
        f"{when}, the session's temp folder is still there: {folder} holds {entries(folder)[:10]}"
    )


# --------------------------------------------------------------------------
# A launch that is interrupted while its session runs
# --------------------------------------------------------------------------

def _own_group_with_default_interrupt():
    """Runs in the child before ``gov`` starts: a process group of its own, and SIGINT handled as a terminal's is.

    A test runner started in the background has SIGINT ignored, and a child
    inherits that. The launcher under test is started as a foreground command
    is: SIGINT at its default.
    """
    os.setsid()
    signal.signal(signal.SIGINT, signal.SIG_DFL)


def interrupted_launch(project, sandbox, cli, role, ticket, target):
    """Start ``gov launch``, wait until its session runs, send SIGINT, wait for the launcher to end.

    ``target`` is ``"group"`` (the signal goes to the launcher's process group,
    launcher and session alike, as Ctrl-C in a terminal sends it) or
    ``"launcher"`` (to the launcher's process alone, as ``kill -INT <pid>``).
    Returns ``(folder, return code)``: the session's temp folder, seen as a
    directory while the session ran.
    """
    ready = sandbox.elsewhere / "session-is-running.json"
    plan(cli, files={"work/left-behind.txt": "left by the session\n"}, ready=ready, wait=120)
    script = cli_support.write_launcher(project, sandbox)
    process = subprocess.Popen([sys.executable, str(script), "launch", role, ticket], cwd=str(project),
                               env=w46.gov_environment(project, sandbox, cli), stdin=subprocess.DEVNULL,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                               preexec_fn=_own_group_with_default_interrupt)
    try:
        deadline = time.monotonic() + WAIT_S
        while not ready.is_file():
            if process.poll() is not None or time.monotonic() > deadline:
                out, err = process.communicate(timeout=WAIT_S) if process.poll() is not None else ("", "")
                raise AssertionError(f"gov launch {role} {ticket} started no session within {WAIT_S:.0f} s "
                                     f"(exit code {process.poll()}): {(out + err).strip()[-400:]}")
            time.sleep(0.02)
        folders = json.loads(ready.read_text(encoding="utf-8"))
        assert len(folders) == 1, f"the session was not given exactly one temp folder of its own: {folders}"
        folder = Path(folders[0])
        assert (folder / "work" / "left-behind.txt").is_file(), "the session could not write in its temp folder"
        if target == "group":
            os.killpg(process.pid, signal.SIGINT)
        else:
            os.kill(process.pid, signal.SIGINT)
        try:
            process.communicate(timeout=WAIT_S)
        except subprocess.TimeoutExpired:
            raise AssertionError(f"gov launch did not end within {WAIT_S:.0f} s of SIGINT") from None
        return folder, process.returncode
    finally:
        try:
            os.killpg(process.pid, signal.SIGKILL)   # whatever of the launch is left: nothing outlives the test
        except (ProcessLookupError, PermissionError):
            pass
        if process.poll() is None:
            process.wait(timeout=WAIT_S)
        for stream in (process.stdout, process.stderr):
            if stream is not None:
                stream.close()
