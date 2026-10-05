"""Support code for the W1-50 acceptance tests (standard library only).

W1-50 changes how the post-command containment check (W1-03) judges a forward
``HEAD`` move: commit by commit, each commit by its own ``Role`` and ``Task``
trailers (DEC-255, DEC-182). The tests drive the check the way the W1-03 suite
does, through the kernel's hooks around one Bash call in a throw-away project,
and reuse that suite's support module (``tests/acceptance/W1-03/w1_03_support.py``)
for the project, the hook runs and the assertions.

This module adds only what the W1-50 cases need: shell fragments that make
commits with or without trailers, a ticket branch to merge, a closed ticket
with its close commit (DEC-318, DEC-358), and what a finding says about a
commit (DEC-270).
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
SPEC_TICKET = check_support.PRODUCT_SPEC_TICKET_ID          # product-spec ticket DAEO-zz92: docs/spec/**
SPEC_FILE = "docs/spec/feature.md"                          # inside DAEO-zz92's allowed paths
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

OWNER = "owner"                    # no agent role: the owner's commits carry ``Role: owner`` (DEC-360)
NO_TICKET = "decision-record"      # a ``Task`` value that is no ticket (DEC-359)


def undone(path, trailers):
    """Shell: a commit that changes ``path``, then a commit that puts ``path`` back; both carry ``trailers``."""
    command = (
        commit(path, trailers, subject="outside")
        + f" && git checkout -q HEAD~1 -- {shlex.quote(path)} && git commit -q -m undo"
    )
    if trailers is not None:
        role, task = trailers
        command += f" --trailer {shlex.quote('Task: ' + task)} --trailer {shlex.quote('Role: ' + role)}"
    return command


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


def commit_with(path, *arguments, subject="work"):
    """Shell: change ``path`` and commit it alone; ``arguments`` are passed to ``git commit`` word for word."""
    directory = os.path.dirname(path) or "."
    command = (
        f"mkdir -p {shlex.quote(directory)} && echo changed >> {shlex.quote(path)} "
        f"&& git add -- {shlex.quote(path)} && git commit -q -m {shlex.quote(subject)}"
    )
    for argument in arguments:
        command += " " + shlex.quote(argument)
    return command


def trailer_arguments(*lines):
    """``git commit`` arguments that put each of ``lines`` in the final trailer block (DEC-182)."""
    arguments = []
    for line in lines:
        arguments += ["--trailer", line]
    return arguments


def merge_with_own_change(path, trailers=AS_ORCHESTRATOR, branch=TICKET_BRANCH):
    """Shell: merge ``branch`` and, before the merge is committed, change ``path`` by hand (DEC-269).

    Neither side of the merge changes ``path`` in the fixtures that use this,
    so the merge commit holds content of ``path`` that none of its parents holds.
    """
    directory = os.path.dirname(path) or "."
    command = (
        f"git merge -q --no-ff --no-commit {shlex.quote(branch)} "
        f"&& mkdir -p {shlex.quote(directory)} && echo by-the-merge >> {shlex.quote(path)} "
        f"&& git add -- {shlex.quote(path)} && git commit -q -m {shlex.quote('Merge ' + branch)}"
    )
    if trailers is not None:
        role, task = trailers
        command += f" --trailer {shlex.quote('Task: ' + task)} --trailer {shlex.quote('Role: ' + role)}"
    return command


def merge_resolving(path, resolution, trailers=AS_ORCHESTRATOR, branch=TICKET_BRANCH):
    """Shell: merge ``branch``, which conflicts in ``path``, and commit the merge with a resolution (DEC-269).

    ``resolution`` is ``"theirs"`` (the merged side's content, which a parent
    holds) or ``"new"`` (content neither parent holds).
    """
    if resolution == "theirs":
        resolve = f"git checkout --theirs -- {shlex.quote(path)}"
    else:
        resolve = f"echo resolved-by-the-merge > {shlex.quote(path)}"
    command = (
        f"( git merge -q --no-ff --no-commit {shlex.quote(branch)} > /dev/null 2>&1 || true ) "
        f"&& test -n \"$(git diff --name-only --diff-filter=U)\" "
        f"&& {resolve} && git add -- {shlex.quote(path)} "
        f"&& git commit -q -m {shlex.quote('Merge ' + branch)}"
    )
    if trailers is not None:
        role, task = trailers
        command += f" --trailer {shlex.quote('Task: ' + task)} --trailer {shlex.quote('Role: ' + role)}"
    return command


# --------------------------------------------------------------------------
# A closed ticket with its close commit, and a ticket that was never started (DEC-318)
# --------------------------------------------------------------------------

CLOSED_TICKET = "DAEO-zz97"        # engineer ticket, closed by ``closed_ticket``
CLOSED_WBS = "W1-97"
CLOSED_SOURCE = "lib/closed/work.py"                         # inside DAEO-zz97's allowed paths
CLOSED_LATE_SOURCE = "lib/closed/late.py"                    # inside DAEO-zz97's allowed paths
CLOSED_TEST = f"{ACCEPTANCE}/{CLOSED_WBS}/test_closed.py"
CLOSED_LATE_TEST = f"{ACCEPTANCE}/{CLOSED_WBS}/test_late.py"
OPEN_TICKET = "DAEO-zz98"          # engineer ticket with status ``open``: never started
OPEN_WBS = "W1-98"
OPEN_SOURCE = "lib/open/work.py"                             # inside DAEO-zz98's allowed paths
OPEN_TEST = f"{ACCEPTANCE}/{OPEN_WBS}/test_open.py"
LEAD_BRANCH = "lead"               # stays where ``main`` was before the closed ticket's work
LATE_BRANCH = "late"               # cut before the close commit; never merged before the close

_CLOSED_PATHS = ("lib/closed/**",)
_OPEN_PATHS = ("lib/open/**",)


def _write_ticket(project, ticket, wbs, status, paths):
    text = check_support.ticket_text(ticket_id=ticket, wbs_id=wbs, status=status, role=ENGINEER,
                                     allowed_paths=paths)
    (project / ".tickets" / f"{ticket}.md").write_text(text, encoding="utf-8")


def two_more_tickets(project, sandbox, closed_status="in_progress"):
    """One commit adds ``DAEO-zz97`` (with ``closed_status``) and ``DAEO-zz98`` (open); ``lead`` and ``late`` are cut."""
    _write_ticket(project, CLOSED_TICKET, CLOSED_WBS, closed_status, _CLOSED_PATHS)
    _write_ticket(project, OPEN_TICKET, OPEN_WBS, "open", _OPEN_PATHS)
    run(project, sandbox,
        "git add -- .tickets && git commit -q -m 'two more tickets'"
        f" --trailer 'Task: {ORCHESTRATOR_TICKET}' --trailer 'Role: {ORCHESTRATOR}'")
    check_support.git(project, "branch", LEAD_BRANCH)
    check_support.git(project, "branch", LATE_BRANCH)


def set_status(project, sandbox, status, subject, also=None):
    """Commit ``status`` to ``DAEO-zz97``'s file, as the orchestrator naming that ticket. Returns the commit's id.

    With ``also``, the same commit changes that path too: a status change
    inside a larger commit.
    """
    _write_ticket(project, CLOSED_TICKET, CLOSED_WBS, status, _CLOSED_PATHS)
    paths = f".tickets/{CLOSED_TICKET}.md"
    change = ""
    if also is not None:
        directory = os.path.dirname(also) or "."
        change = f"mkdir -p {shlex.quote(directory)} && echo changed >> {shlex.quote(also)} && "
        paths += " " + shlex.quote(also)
    run(project, sandbox,
        f"{change}git add -- {paths} && git commit -q -m {shlex.quote(subject)}"
        f" --trailer 'Task: {CLOSED_TICKET}' --trailer 'Role: {ORCHESTRATOR}'")
    return check_support.git(project, "rev-parse", "HEAD").strip()


def status_changes(project, ticket=CLOSED_TICKET, revision="HEAD"):
    """The ids of the commits in the history of ``revision`` that change the ticket's file, newest first."""
    return check_support.git(project, "rev-list", revision, "--", f".tickets/{ticket}.md").split()


def closed_ticket(project, sandbox, *steps, late_steps=()):
    """Give the project a closed ticket ``DAEO-zz97`` and an open one ``DAEO-zz98``. Returns the close commit's id.

    History on ``main``, in order:

    1. one commit adds both ticket files: ``DAEO-zz97`` in progress, ``DAEO-zz98`` open;
       the branches ``lead`` and ``late`` are cut here;
    2. one commit per ``(path, trailers)`` step: the closed ticket's work;
    3. the close commit, in the form the repository's closes have had since the
       parallel run (README, "The ticket's close commit"): it changes only
       ``.tickets/DAEO-zz97.md``, from ``status: in_progress`` to
       ``status: closed``, and carries ``Task: DAEO-zz97`` and
       ``Role: orchestrator`` in its final trailer block.

    ``late_steps`` are committed on ``late``: work that names the ticket and is
    not in the close commit's history. ``main`` is checked out at the end.
    """
    two_more_tickets(project, sandbox)
    if steps:
        run(project, sandbox, commits(*steps))
    if late_steps:
        check_support.git(project, "checkout", "-q", LATE_BRANCH)
        run(project, sandbox, commits(*late_steps))
        check_support.git(project, "checkout", "-q", "main")
    _write_ticket(project, CLOSED_TICKET, CLOSED_WBS, "closed", _CLOSED_PATHS)
    run(project, sandbox,
        f"git add -- .tickets/{CLOSED_TICKET}.md"
        f" && git commit -q -m '{CLOSED_WBS} closed: fixture work; suites green after the merge'"
        f" --trailer 'Task: {CLOSED_TICKET}' --trailer 'Role: {ORCHESTRATOR}'")
    close_commit = check_support.git(project, "rev-parse", "HEAD").strip()
    changed = check_support.git(project, "show", "--name-only", "--format=", close_commit).split()
    assert changed == [f".tickets/{CLOSED_TICKET}.md"], f"the fixture's close commit changes {changed}"
    return close_commit


def is_ancestor(project, commit_id, of):
    """True when ``commit_id`` is in the history of ``of`` (``git merge-base --is-ancestor``)."""
    import subprocess
    proc = subprocess.run(["git", "-C", str(project), "merge-base", "--is-ancestor", commit_id, of],
                          capture_output=True, check=False)
    assert proc.returncode in (0, 1), f"git merge-base --is-ancestor failed: {proc.stderr!r}"
    return proc.returncode == 0


def commit_of(project, path, revision="HEAD"):
    """The id of the latest commit in the history of ``revision`` that changes ``path``."""
    commit_id = check_support.git(project, "rev-list", "-n", "1", revision, "--", path).strip()
    assert commit_id, f"no commit in the history of {revision} changes {path}"
    return commit_id


# --------------------------------------------------------------------------
# What a finding says about the commit it is for (DEC-270)
# --------------------------------------------------------------------------

def findings_naming(result, path, what):
    """The findings this call added whose ``paths`` name ``path``."""
    findings = check_support.new_findings(result, what)
    matching = [f for f in findings if path in check_support.finding_paths(result, f)]
    assert matching, f"{what}: no finding names {path!r}; recorded paths: {[f['paths'] for f in findings]}"
    return matching


def names_commit(reason, commit_id):
    """True when ``reason`` holds the commit's id, in full or as an abbreviation of at least 7 characters."""
    import re
    return any(commit_id.startswith(word) for word in re.findall(r"[0-9a-f]{7,40}", reason))


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
