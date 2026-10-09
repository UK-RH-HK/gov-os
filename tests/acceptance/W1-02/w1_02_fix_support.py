"""Support code for the fix round of W1-02's root-search round (DEC-570).

Everything here is a stand-in in a temporary folder: the world, the starts, the
bound and the assertions are those of ``w1_02_round_support`` (no line of it is
changed). No file of this repository is opened, and the held-out file's path is
never spelled: it comes from the guard's own module through
``w1_02_protected_support``.

**Where a command is asked.** Every shell form of this round is asked in a
session that *stands in* its start (the hook input's working folder):

- ``root``: the session's project root;
- ``sibling``, ``nested``, ``home``: the folder ``<P>`` a copy lies under (a
  sibling checkout, a folder below the root, the stand-in home folder);
- one of ``HOLDING``: the folder of the session's project that holds a
  protected file itself. The rule from before the round refuses a listing or
  a search with no path there.

**Templates.** A command is a plain text with three marks, filled by
``ask_command``: ``<ABS>`` the start (absolute), ``<NAMED>`` a named source file
of the session's project (absolute), ``<SCRATCH>`` the project's scratch folder
(absolute), ``<F>`` a name filter. Braces and dollar signs stand as a shell
reads them.

A case's id and a failure message name a form and a start by a label, never by
a path, a filter or a command.
"""

from __future__ import annotations

import os
import re

import w1_02_copies_support as batch
import w1_02_folders_support as folders
import w1_02_protected_support as protected
import w1_02_round_support as rnd

SETTINGS = rnd.SETTINGS
HELD = rnd.HELD
FILES = rnd.FILES
ROOT = rnd.ROOT
SITES = rnd.SITES
WIDEST = rnd.WIDEST
OTHER_ROLES = rnd.OTHER_ROLES

make_world = rnd.make_world

# The other search program of the fifth batch: it searches the folder it runs in by default.
PROG = "rg"
# A named file that is neither protected file nor a copy: a source file of the session's project.
NAMED_REL = "src/app/main.py"

# The folders of the session's project that hold a protected file: label -> the file.
HOLDING = {"the-folder-that-holds-the-settings-file": SETTINGS,
           "the-folder-that-holds-the-held-out-file": HELD}

# The read rule's decisions a refusal may name: those the earlier batches accept, and the one that orders this round.
RULE_RE = re.compile(r"\bDEC-(508|525|548|553|557|562|570)\b")

# A search with no path, in the kinds the fifth batch holds.
NO_PATH = {
    "the-other-program-with-a-word": PROG + " VALUE",
    "grep-with-a-recursive-option-and-a-word": "grep -rn VALUE",
    "ls-with-its-recursive-option": "ls -R",
}
LISTS_FILES = {"the-other-program-with-its-option-that-lists-files": PROG + " --files"}


def base_of(name):
    return os.path.basename(protected.PROTECTED[name])


# The name filters that take a file in, as the fifth batch holds them: label -> the filter for the file ``name``.
FILTERS = {
    "its-own-name": base_of,
    "its-extension": lambda name: "*" + os.path.splitext(base_of(name))[1],
}


def folder_of(world, start):
    """The folder a session stands in for ``start``."""
    if start in HOLDING:
        return world.site("own").folder(HOLDING[start])
    return rnd.start_of(world, start)


def _site_and_files(start):
    if start in HOLDING or start == ROOT:
        return "own", tuple(FILES)
    return start, rnd.files_under(start)


def fill(world, command, start=ROOT, f=""):
    return (command.replace("<ABS>", str(folder_of(world, start)))
            .replace("<NAMED>", str(world.project / NAMED_REL))
            .replace("<SCRATCH>", str(world.project / folders.SCRATCH_REL))
            .replace("<F>", f))


def ask_command(world, command, start=ROOT, who=WIDEST, f=""):
    """One shell command by ``who`` in a session that stands in ``start``."""
    return folders.ask_bash(world, fill(world, command, start, f), who, folder_of(world, start))


def ask_tool(world, tool_name, tool_input, start=ROOT, who=WIDEST):
    """One call of a tool by ``who`` in a session that stands in ``start``; a Bash input is ``{"command": ...}``."""
    if tool_name == "Bash":
        return folders.ask_bash(world, tool_input["command"], who, folder_of(world, start))
    return folders.ask(world, tool_name, tool_input, who, folder_of(world, start))


def assert_refused(result, world, start, what, said=()):
    """The read rule's own decision, and what it says.

    ``deny`` with exit code 0 (never the hook's failure report, DEC-110), a
    reason that names a decision of the read rule and words beside it, and
    nothing of the call: no protected file's path, folder or value, not the
    folder the session stands in, and none of ``said`` (the command, a word).
    """
    protected.assert_refused_by_rule(result, what)
    assert RULE_RE.search(protected.reason_of(result)), (
        f"{what} was denied, but not as a read of the two files: the reason names none of DEC-508, DEC-525, "
        f"DEC-548, DEC-553, DEC-557, DEC-562, DEC-570"
    )
    rnd.assert_names_a_rule_and_a_decision(result, what)
    site, names = _site_and_files(start)
    for name in names:
        batch.assert_says_nothing_of_the_file(result, world, site, name, what)
    rnd.assert_carries_none_of(result, (folder_of(world, start),) + tuple(said), what)


def assert_refused_command(result, world, command, start, what, f=""):
    """``assert_refused`` for a shell command: the refusal does not echo the command either."""
    echoed = [text for text in (fill(world, command, start, f), "VALUE") if len(text) >= 5]
    assert_refused(result, world, start, what, echoed)


def assert_allowed(result, what):
    protected.assert_allowed(result, what)


def assert_not_refused_as_a_read(result, what):
    """Decided as today by whichever rule decides it; the read rule is not the one that refuses it."""
    assert result.decision in ("allow", "deny") and result.returncode == 0, (
        f"{what} got no decision of a rule: decision={result.decision} exit={result.returncode}"
    )
    assert not RULE_RE.search(protected.reason_of(result)), f"{what} was refused as a read of the two files"


def share(labels, roles=OTHER_ROLES, each=2):
    """A share of ``labels`` for the roles beside the orchestrator: ``each`` labels per role, in turn."""
    labels = sorted(labels)
    return [(who, labels[(row * each + step) * 3 % len(labels)])
            for row, who in enumerate(roles) for step in range(each)]


def ids(pairs):
    return ["-".join(str(part) for part in pair) for pair in pairs]
