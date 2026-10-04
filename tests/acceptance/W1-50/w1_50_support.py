"""Support code for the W1-50 acceptance tests (standard library only).

W1-50 changes how the post-command containment check (W1-03) judges a forward
``HEAD`` move: commit by commit, each commit by its own ``Role`` and ``Task``
trailers (DEC-255, DEC-182). The tests drive the check the way the W1-03 suite
does, through the kernel's hooks around one Bash call in a throw-away project,
and reuse that suite's support module (``tests/acceptance/W1-03/w1_03_support.py``)
for the project, the hook runs and the assertions.

This module adds only what the W1-50 cases need: shell fragments that make
commits with or without trailers, and a ticket branch to merge.
"""

from __future__ import annotations

import os
import shlex
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "W1-03"))

import w1_03_support as check_support  # noqa: E402

ENGINEER = check_support.ENGINEER
ORCHESTRATOR = check_support.ORCHESTRATOR
DESIGNER = check_support.TEST_DESIGNER

TICKET = check_support.TICKET_ID                            # engineer ticket DAEO-zz90, W1-90, in progress
ORCHESTRATOR_TICKET = check_support.ORCHESTRATOR_TICKET_ID  # orchestrator ticket DAEO-zz91, in progress
DOCS_TICKET = check_support.DOCS_TICKET_ID                  # engineer ticket DAEO-zz95: docs/**
WBS = check_support.TICKET_WBS_ID

ACCEPTANCE = check_support.ACCEPTANCE_REL
ACCEPTANCE_FILE = check_support.ACCEPTANCE_FILE             # exists in the fixture project
NEW_TEST = f"{ACCEPTANCE}/{WBS}/test_new.py"                # does not exist yet
SECOND_NEW_TEST = f"{ACCEPTANCE}/{WBS}/test_second.py"
SOURCE = check_support.SOURCE_FILE                          # inside DAEO-zz90's allowed paths
SECOND_SOURCE = "pyproject.toml"                            # inside DAEO-zz90's allowed paths
README = "README.md"                                        # outside every fixture ticket's paths
NOTES = "docs/notes.md"                                     # inside DAEO-zz95's paths only
BOOTSTRAP = "governance/project/bootstrap.md"               # inside the orchestrator ticket's paths

WATCHED = (README, ACCEPTANCE_FILE, NEW_TEST, SECOND_NEW_TEST, SOURCE, SECOND_SOURCE, NOTES)

TICKET_BRANCH = f"w1/{WBS}"

# (Role trailer, Task trailer) of a commit; ``None`` is a commit with neither trailer.
AS_DESIGNER = (DESIGNER, TICKET)
AS_ENGINEER = (ENGINEER, TICKET)
AS_ORCHESTRATOR = (ORCHESTRATOR, TICKET)
NO_TRAILERS = None


def commit(path, trailers, subject="work"):
    """Shell: change ``path`` and commit it alone, with ``trailers`` in the final trailer block (DEC-182)."""
    directory = os.path.dirname(path) or "."
    command = (
        f"mkdir -p {shlex.quote(directory)} && echo changed >> {shlex.quote(path)} "
        f"&& git add -- {shlex.quote(path)} && git commit -q -m {shlex.quote(subject)}"
    )
    if trailers is not None:
        role, task = trailers
        command += f" --trailer {shlex.quote('Task: ' + task)} --trailer {shlex.quote('Role: ' + role)}"
    return command


def commits(*steps):
    """Shell: one commit per ``(path, trailers)`` step, in order."""
    return " && ".join(commit(path, trailers, subject=f"commit {n}") for n, (path, trailers) in enumerate(steps, 1))


def merge(branch=TICKET_BRANCH, trailers=AS_ORCHESTRATOR):
    """Shell: merge ``branch`` with a merge commit, as the main orchestrator merges a ticket branch (DEC-235)."""
    command = (
        f"git merge -q --no-ff --no-commit {shlex.quote(branch)} "
        f"&& git commit -q -m {shlex.quote('Merge ' + branch)}"
    )
    if trailers is not None:
        role, task = trailers
        command += f" --trailer {shlex.quote('Task: ' + task)} --trailer {shlex.quote('Role: ' + role)}"
    return command


def run(project, sandbox, command):
    """Run ``command`` in the project with no hook around it; it must succeed."""
    bash = check_support.run_bash(project, command, sandbox)
    assert bash.returncode == 0, (
        f"the fixture command `{command}` failed: {bash.stdout.strip()!r} {bash.stderr.strip()!r}"
    )
    return bash


def ticket_branch(project, sandbox, *steps, main_moves_on=True):
    """A branch ``w1/W1-90`` with one commit per step. With ``main_moves_on``, ``main`` gets a commit too."""
    check_support.git(project, "checkout", "-q", "-b", TICKET_BRANCH)
    run(project, sandbox, commits(*steps))
    check_support.git(project, "checkout", "-q", "main")
    if main_moves_on:
        run(project, sandbox, commit(BOOTSTRAP, (ORCHESTRATOR, ORCHESTRATOR_TICKET), subject="main moves on"))


def is_merge(project, commit_id="HEAD"):
    return len(check_support.git(project, "rev-list", "--parents", "-n", "1", commit_id).split()) > 2
