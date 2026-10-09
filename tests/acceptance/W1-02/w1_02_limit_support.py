"""Support code for the DEC-574 cases of W1-02: the held-out check and the system path limit.

DEC-574: "The held-out check skips path resolution for any string longer than
the system path limit, and keeps the literal substring check."

Everything here is a stand-in in a temporary folder, as in
``w1_02_protected_support``, whose project this module uses unchanged: a
committed temporary project with a stand-in held-out file that lists a stand-in
held-out folder (``World.listed``, a temporary folder with one file in it). No
file of this repository is opened, and the held-out file's path is never
spelled: it comes from the guard's own module through
``w1_02_protected_support``.

Added around that project:

- ``World.link``: a symbolic link to the stand-in held-out folder, outside the
  project;
- a symbolic link of the same name in the stand-in home folder (the ``HOME`` of
  the hook's environment), so that the home folder's short form reaches the
  stand-in held-out folder;
- ``World.other``: a folder beside the stand-in held-out folder that is not held
  out.

**The limit.** ``LIMIT`` is what the system reports for the length of a path
(``PC_PATH_MAX``, 4096 on Linux), and the cases count a string in characters: a
string is *past the limit* when it holds more than ``LIMIT`` characters. That is
the reading under which the fewest strings are past it (README, eighth batch).

**A string that reaches the stand-in held-out folder without holding its path**
is built to an exact length by ``via_link`` (an absolute path through the
symbolic link, padded with the current folder) and by ``via_dots`` (a relative
path from the session's folder through ``..``, padded with a folder and the way
back out of it).

Every decision is asked of the hook, run as a process on a hook input. A case's
id and a failure message name a form by a label, never by a path or a command.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

import pytest

import w1_02_protected_support as protected
import w1_02_round_support as rnd
import w1_02_support as support

# What the system reports for the length of a path; a string is counted in characters.
LIMIT = os.pathconf("/", "PC_PATH_MAX")
# The guard's bound on a Bash command (DEC-562), and a length near it.
MOST_COMMAND = 32768
NEAR_COMMAND = 32000
KB = 1024
MB = 1024 * 1024

# The bound of the time cases of this revision, unchanged (README, fifth batch).
BOUND_S = rnd.BOUND_S
PROCESS_LIMIT_S = rnd.PROCESS_LIMIT_S

ORCHESTRATOR = "orchestrator"
ENGINEER = "engineer"
NO_ROLE = "no-role"
# The orchestrator asks every case; these two ask a share.
OTHER_ROLES = (ENGINEER, NO_ROLE)

# A file of the project the orchestrator and the engineer of the standard ticket may write.
SOURCE_REL = "src/gov/guard/decide.py"
LINK_NAME = "a-link"
FILE_NAME = "answers.md"
HERE = "./"            # the current folder
IN_AND_OUT = "x/../"   # a folder and the way back out of it

# The held-out check's own refusal, as the guard words it: it names a held-out path, and no path.
HELD_OUT_CHECK_RE = re.compile(r"held-out path")
# The refusal of a file tool's path that is longer than the guard resolves (sixth batch).
LONG_PATH_RE = re.compile(r"\bDEC-562\b")


@dataclass(frozen=True)
class World:
    project: Path
    sandbox: support.Sandbox
    listed: Path     # the stand-in held-out folder the stand-in held-out file lists
    link: Path       # a symbolic link to it, outside the project
    other: Path      # a folder beside it that is not held out

    @property
    def elsewhere(self):
        return self.sandbox.elsewhere

    @property
    def relative(self):
        """The stand-in held-out folder as a relative path from the project, the session's folder."""
        return os.path.relpath(self.listed, self.project)

    def secrets(self):
        """What a refusal must not carry: the stand-in held-out path, the ways to it, the held-out file's place."""
        return (str(self.listed), str(self.link), self.relative, str(self.project), protected.HELD_REL,
                os.path.basename(protected.HELD_REL))


def make_world(base):
    guarded = protected.make_guarded(Path(base))
    sandbox = guarded.sandbox
    link = sandbox.elsewhere / LINK_NAME
    link.symlink_to(guarded.listed, target_is_directory=True)
    (sandbox.home / LINK_NAME).symlink_to(guarded.listed, target_is_directory=True)
    other = sandbox.elsewhere / "a-folder-that-is-not-held-out"
    other.mkdir()
    (other / FILE_NAME).write_text("not held out\n", encoding="utf-8")
    (sandbox.elsewhere / "detour").mkdir()
    return World(guarded.project, sandbox, guarded.listed, link, other)


def ask(world, tool_name, tool_input, who=ORCHESTRATOR, env=None, limit=support.HOOK_TIMEOUT_S):
    """One decision of the hook, run as a process; ``limit`` is the test's own limit on the process.

    The session stands in the project root. ``env`` adds or replaces variables of
    the hook's environment (a ``HOME`` of the case's own).
    """
    role, ticket, subagent = protected.ACTORS[who]
    project = Path(world.project)
    data = support.payload(project, tool_name, tool_input, world.sandbox, subagent)
    argv = support._argv(project / support.installed_hook_rel())
    started = time.perf_counter()
    try:
        proc = subprocess.run(argv, input=json.dumps(data), capture_output=True, text=True, cwd=str(project),
                              env=support.hook_environment(project, world.sandbox, role, ticket, env),
                              timeout=limit, check=False)
    except subprocess.TimeoutExpired:
        return support.HookResult("timeout", None, "", "", time.perf_counter() - started)
    seconds = time.perf_counter() - started
    return support.HookResult(support.classify(proc.returncode, proc.stdout), proc.returncode, proc.stdout,
                              proc.stderr, seconds)


def ask_timed(world, tool_name, tool_input, who=ORCHESTRATOR, env=None):
    """``ask`` with the time cases' limit on the process: a hook still running then has given no answer."""
    return ask(world, tool_name, tool_input, who, env, PROCESS_LIMIT_S)


# --------------------------------------------------------------------------
# Strings of an exact length
# --------------------------------------------------------------------------

def padded(prefix, unit, suffix, length):
    """``prefix``, then ``unit`` repeated, then ``suffix``: exactly ``length`` characters.

    What ``unit`` does not fill is filled with slashes, which change nothing of a path.
    """
    room = length - len(prefix) - len(suffix)
    if room < 0:
        pytest.fail(f"a string of {length} characters is too short for this form on this machine", pytrace=False)
    text = prefix + unit * (room // len(unit)) + "/" * (room % len(unit)) + suffix
    if len(text) != length:
        pytest.fail("the fixture string has not the length asked for", pytrace=False)
    return text


def via_link(world, length, unit=HERE):
    """An absolute path of ``length`` characters to a file of the stand-in held-out folder, through the link."""
    return holds_no_literal(world, padded(f"{world.elsewhere}/", unit, f"{LINK_NAME}/{FILE_NAME}", length))


def via_dots(world, length, unit=IN_AND_OUT):
    """A relative path of ``length`` characters from the session's folder to the same file, through ``..``."""
    return holds_no_literal(world, padded("", unit, f"{world.relative}/{FILE_NAME}", length))


def holds_no_literal(world, text):
    """The fixture's own check: the string does not hold the stand-in held-out path as literal text."""
    if str(world.listed) in text:
        pytest.fail("the fixture string holds the stand-in held-out path as literal text", pytrace=False)
    return text


def filler(unit, length):
    """``unit`` repeated and cut to exactly ``length`` characters."""
    return (unit * (length // len(unit) + 1))[:length]


# --------------------------------------------------------------------------
# The fields that are no path field
# --------------------------------------------------------------------------

def _source(world):
    return str(world.project / SOURCE_REL)


# label -> builder(world, text) -> (tool, input)
FIELDS = {
    "a-Write-s-content": lambda w, text: ("Write", {"file_path": _source(w), "content": text}),
    "an-Edit-s-old-string":
        lambda w, text: ("Edit", {"file_path": _source(w), "old_string": text, "new_string": "VALUE = 2"}),
    "an-Edit-s-new-string":
        lambda w, text: ("Edit", {"file_path": _source(w), "old_string": "VALUE = 1", "new_string": text}),
    "a-field-of-an-unknown-tool": lambda w, text: ("ToolAddedAfterThisTicket", {"target": text}),
    "a-list-inside-the-input": lambda w, text: ("mcp__notes__add", {"notes": ["a first note", text]}),
    "a-mapping-inside-the-input":
        lambda w, text: ("mcp__notes__add", {"note": {"title": "a note", "body": {"text": text}}}),
}
BASH_WORD = "a-word-of-a-Bash-command"
BASH_COMMAND = "a-Bash-command"


def call(world, field, text):
    """The call that carries ``text`` in ``field``; in a Bash command it is the one word after a reader."""
    if field == BASH_WORD:
        return "Bash", support.bash_tool_input("cat " + text)
    if field == BASH_COMMAND:
        return "Bash", support.bash_tool_input(text)
    return FIELDS[field](world, text)


# What the guard decides as a whole for a call the held-out check does not refuse: (field kind, role) -> decision.
# A Write or an Edit of the source file is the allow-list's: the two roles that may write it are allowed, a
# session with no role is denied. A tool the guard does not know and a command that writes nothing are allowed.
def as_a_whole(tool_name, who):
    return "deny" if tool_name in ("Write", "Edit") and who == NO_ROLE else "allow"


# --------------------------------------------------------------------------
# Assertions
# --------------------------------------------------------------------------

def assert_refused_by_the_held_out_check(result, world, what, said=()):
    """The held-out check's own decision: ``deny``, exit code 0, its own reason, and no path in anything it wrote.

    ``said`` are further pieces of the call the refusal must not carry.
    """
    protected.assert_refused_by_rule(result, what)
    reason = protected.reason_of(result)
    assert HELD_OUT_CHECK_RE.search(reason), f"{what} was denied, but not by the held-out check"
    rnd.assert_carries_none_of(result, world.secrets() + tuple(said), what)


def assert_not_refused_by_the_held_out_check(result, what):
    """A decision of a rule (never a hook error, never the limit), and not the held-out check's refusal."""
    assert result.decision in ("allow", "deny") and result.returncode == 0, (
        f"{what} got no decision of a rule: decision={result.decision} exit={result.returncode}"
    )
    assert not HELD_OUT_CHECK_RE.search(protected.reason_of(result)), (
        f"{what} was refused by the held-out check: the string is past the system path limit and holds no "
        f"held-out path as literal text (DEC-574)"
    )


def assert_decided_as_a_whole(result, tool_name, who, what):
    """Not refused by the held-out check, and decided as the same call with a short string is for the role."""
    assert_not_refused_by_the_held_out_check(result, what)
    expected = as_a_whole(tool_name, who)
    assert result.decision == expected, (
        f"{what} by '{who}' was not decided as a short string in its place is ({expected}): "
        f"decision={result.decision} exit={result.returncode}"
    )


def assert_in_time(result, what):
    rnd.assert_decided_in_time(result, what)
