"""Support code for the DEC-553 cases of W1-02: a wildcard-only glob from a copy's folder, a move of a holding folder.

Everything here is a stand-in in a temporary folder, as in
``w1_02_copies_support``, whose world this module builds on: no file of this
repository is opened, and the held-out file's path is never spelled (it comes
from the guard's own module through ``w1_02_protected_support.HELD_REL``; the
folders above it are computed from it).

Added to that world:

- a ticket of an engineer whose ``allowed_paths`` name every folder that holds
  either stand-in file, the folder ``template/`` and the folder ``docs/``: a
  role other than the orchestrator that may write those folders today;
- folders under which no copy lies: ``src/`` of the session's project (it is
  there already), ``src/`` of the sibling checkout with a package below it, and
  a work folder below the stand-in home.

A copy at ``<P>/<the file's project-relative path>`` has the site ``<P>``. A
**holding folder** of a copy is a folder strictly between ``<P>`` and the copy:
the folder the rule as built already refuses in a listing or a search.
"""

from __future__ import annotations

import os
import re

import w1_02_copies_support as batch
import w1_02_protected_support as protected
import w1_02_support as support

SETTINGS = batch.SETTINGS
HELD = batch.HELD
FILES = batch.FILES
SCRATCH_REL = batch.SCRATCH_REL

FOLDER_WRITER_TICKET_ID = "DAEO-zz98"
# Folders of the session's project that hold neither file and no copy.
NEUTRAL_REL = "docs/spec"
NEUTRAL_PARENT_REL = "docs"
OTHER_FOLDER_REL = "src/app"
SOURCE_REL = "src"
# A folder below the stand-in home that is not the home folder and holds no settings file.
HOME_WORK_REL = "w1-02-work"

# Who makes a call: name -> (GOV_ROLE, GOV_TICKET, subagent type).
ACTORS = dict(batch.ACTORS)
ACTORS["engineer-who-may-write-the-folders"] = (support.ENGINEER, FOLDER_WRITER_TICKET_ID, None)
ORCHESTRATOR = "orchestrator"
FOLDER_WRITER = "engineer-who-may-write-the-folders"
NOT_A_WRITER = "engineer-who-may-not-write-the-file"
NO_ROLE = "no-role"

# The rule's decisions: the three the refusal may name today, and the one that orders these cases.
RULE_RE = re.compile(r"\bDEC-(508|525|548|553)\b")


def holding_folders(name):
    """The folders strictly between ``<P>`` and the file ``name``, outermost first, relative to ``<P>``."""
    parts = protected.PROTECTED[name].split("/")[:-1]
    return ["/".join(parts[:count]) for count in range(1, len(parts) + 1)]


# Every (file, holding folder): the held-out file lies below more than one folder.
HOLDING = [(name, folder) for name in FILES for folder in holding_folders(name)]
# A case's id says which folder by its level below ``<P>``, never by its path.
HOLDING_IDS = [f"{name}-level-{folder.count('/') + 1}" for name, folder in HOLDING]
# The folder that holds the file itself, for each file: the innermost one.
INNERMOST = [(name, holding_folders(name)[-1]) for name in FILES]


def depth_glob(name):
    """The wildcard-only glob over every file at the depth where the file ``name`` lies below ``<P>``."""
    return "/".join("*" * (protected.PROTECTED[name].count("/") + 1))


def make_world(base):
    """The world of ``w1_02_copies_support`` with the folder writer's ticket and the folders that hold no copy."""
    world = batch.make_world(base)
    paths = ["template/**", f"{NEUTRAL_PARENT_REL}/**", NEUTRAL_PARENT_REL]
    for _, folder in HOLDING:
        paths += [folder, f"{folder}/**"]
    ticket = world.project / ".tickets" / f"{FOLDER_WRITER_TICKET_ID}.md"
    ticket.write_text(support.ticket_text(ticket_id=FOLDER_WRITER_TICKET_ID, wbs_id="W1-98", role=support.ENGINEER,
                                          allowed_paths=tuple(dict.fromkeys(paths))), encoding="utf-8")
    support.git(world.project, "add", "-A")
    support.git(world.project, "commit", "-q", "-m", "a ticket that names the folders above both stand-in files")
    for path in (world.site("sibling").root / SOURCE_REL / "pkg" / "module.py",
                 world.sandbox.home / HOME_WORK_REL / "notes" / "day.md"):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("VALUE = 1\n", encoding="utf-8")
    return world


def ask(world, tool_name, tool_input, who, cwd=None):
    return batch.ask(world, tool_name, tool_input, ACTORS[who], cwd)


def ask_bash(world, command, who, cwd=None):
    return batch.ask_bash(world, command, ACTORS[who], cwd)


def rel_from_project(world, path):
    """``path`` as a relative path from the session's project root."""
    return os.path.relpath(str(path), str(world.project))


def assert_refused_by_the_rule(result, what):
    """The read rule's own decision: ``deny``, exit code 0, a reason that names one of the rule's decisions.

    Exit code 2 (the guard's report of its own failure) and a denial by the
    allow-list (it names no decision of the rule) do not pass.
    """
    protected.assert_refused_by_rule(result, what)
    assert RULE_RE.search(protected.reason_of(result)), (
        f"{what} was denied, but not as a read of the two files: the reason names none of DEC-508, DEC-525, "
        f"DEC-548, DEC-553"
    )


def assert_denied_but_not_by_the_rule(result, what):
    """A write the role may not make: denied by the allow-list, as today, and not as a read of the two files."""
    protected.assert_refused_by_rule(result, what)
    assert not RULE_RE.search(protected.reason_of(result)), (
        f"{what} was refused as a read of the two files; it takes neither in and is the allow-list's to deny"
    )


def assert_says_nothing(result, world, site, name, what, more=()):
    """A refusal names the rule and the decision: no path, no folder, not ``<P>``, no value of the file.

    ``more`` are further paths the refusal must not carry (the folder moved, the destination).
    """
    batch.assert_says_nothing_of_the_file(result, world, site, name, what)
    said = protected.output_of(result)
    shown = [index for index, value in enumerate(more) if str(value) in said]
    # Positions only: a failure must not print what a refusal must not print.
    assert not shown, f"the refusal of {what} carries {len(shown)} path(s) of the call (positions {shown})"
