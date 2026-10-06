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


# --------------------------------------------------------------------------
# Bytes a commit's author chooses: trailer values and file names (batch after the post-green review)
# --------------------------------------------------------------------------

def shell_word(text):
    """Shell: one word that is exactly ``text``, every byte written as an octal escape of ``printf``.

    The fixture scripts stay plain ASCII, whatever control character or
    non-ASCII letter ``text`` holds. ``text`` must not end with a newline.
    """
    escapes = "".join("\\%03o" % byte for byte in text.encode("utf-8"))
    return "\"$(printf '" + escapes + "')\""


def commit_changes(paths, trailer_lines=(), subject="work"):
    """Shell: change every one of ``paths`` and commit them together, with ``trailer_lines`` in the final block.

    Paths and trailer lines may hold any byte git accepts there.
    """
    steps = []
    for path in paths:
        directory = os.path.dirname(path) or "."
        steps.append(f"mkdir -p {shell_word(directory)} && echo changed >> {shell_word(path)} "
                     f"&& git add -- {shell_word(path)}")
    command = " && ".join(steps) + f" && git commit -q -m {shlex.quote(subject)}"
    for line in trailer_lines:
        command += f" --trailer {shell_word(line)}"
    return command


def ticket_branch_of(project, sandbox, *commands, main_moves_on=True):
    """A branch ``w1/W1-90`` built by ``commands``, one after the other. With ``main_moves_on``, ``main`` gets a
    commit too."""
    check_support.git(project, "checkout", "-q", "-b", TICKET_BRANCH)
    for command in commands:
        run(project, sandbox, command)
    check_support.git(project, "checkout", "-q", "main")
    if main_moves_on:
        run(project, sandbox, commit(BOOTSTRAP, (ORCHESTRATOR, ORCHESTRATOR_TICKET), subject="main moves on"))


def changed_paths(project, commit_id):
    """The paths ``commit_id`` changes against its first parent, as git names them byte for byte (``-z``)."""
    listing = check_support.git(project, "diff-tree", "-r", "-z", "--no-commit-id", "--name-only",
                                "--root", commit_id)
    return [name for name in listing.split("\0") if name]


def trailer_values(project, commit_id, key):
    """The values git itself reads for the trailer ``key`` from the commit's final trailer block."""
    listing = check_support.git(project, "log", "-1", f"--format=%(trailers:key={key},valueonly,separator=%x00)",
                                commit_id)
    return [value for value in listing.rstrip("\n").split("\0") if value]


def set_status_in_the_working_tree(ticket, status):
    """Shell: rewrite the ``status`` line of the ticket's file in the working tree. Nothing is committed."""
    return f"sed -i 's/^status: .*$/status: {status}/' .tickets/{ticket}.md"


def is_merge(project, commit_id="HEAD"):
    return len(check_support.git(project, "rev-list", "--parents", "-n", "1", commit_id).split()) > 2


# --------------------------------------------------------------------------
# The real objects, whatever the repository's own settings and replacement refs say (fifth batch)
# --------------------------------------------------------------------------

def real(project, *args):
    """``git`` in the project with replacement refs switched off (``--no-replace-objects``)."""
    return check_support.git(project, "--no-replace-objects", *args)


def message_bytes(project, commit_id="HEAD"):
    """The commit's message byte for byte, from the real object: no setting and no replacement ref is applied."""
    import subprocess
    proc = subprocess.run(["git", "-C", str(project), "--no-replace-objects", "cat-file", "commit", commit_id],
                          capture_output=True, check=False)
    assert proc.returncode == 0, f"git cat-file commit {commit_id} failed: {proc.stderr!r}"
    return proc.stdout.split(b"\n\n", 1)[1]


def final_block(project, commit_id="HEAD"):
    """The lines of the last paragraph of the commit's message, as bytes: its final trailer block (DEC-182)."""
    return message_bytes(project, commit_id).rstrip(b"\n").split(b"\n\n")[-1].split(b"\n")


def local_setting(project, key):
    """The value of ``key`` in the project's local git configuration; ``None`` when it is not set there."""
    import subprocess
    proc = subprocess.run(["git", "-C", str(project), "config", "--local", "--get", key],
                          capture_output=True, text=True, check=False)
    return proc.stdout.rstrip("\n") if proc.returncode == 0 else None


def replacement_refs(project):
    """The ids of the objects the project's ``refs/replace/`` replaces."""
    listing = check_support.git(project, "for-each-ref", "--format=%(refname)", "refs/replace/")
    return [name.rsplit("/", 1)[1] for name in listing.split()]


def set_locally(key, value):
    """Shell: write ``key`` into the repository's local git configuration (``.git/config``)."""
    return f"git config --local {shlex.quote(key)} {shlex.quote(value)}"


def commit_tree(tree, parents, trailers, subject="Merge"):
    """Shell: the id of a new commit object made with ``git commit-tree``; the trailers are its final block.

    ``tree`` is a revision or a shell variable (``$tree``); it is put in double quotes.
    """
    message = subject + "\\n"
    if trailers is not None:
        role, task = trailers
        message += f"\\nTask: {task}\\nRole: {role}\\n"
    parent_arguments = " ".join(f"-p {shlex.quote(parent)}" for parent in parents)
    return f"$(printf '{message}' | git commit-tree {parent_arguments} \"{tree}\")"


# --------------------------------------------------------------------------
# Sixth batch (DEC-390): ticket files in a commit, and `.git/info/grafts`
# --------------------------------------------------------------------------

EVERYTHING = '"**"'                # an ``allowed_paths`` entry that allows every path
NEW_TICKET = "DAEO-zz99"           # no fixture has this ticket; a test creates its file
NEW_TICKET_WBS = "W1-99"
GRAFTS = ".git/info/grafts"


def ticket_file(ticket):
    return f".tickets/{ticket}.md"


def widen_paths(ticket):
    """Shell: add ``**`` to the ``allowed_paths`` of the ticket's file in the working tree. Nothing is committed."""
    return f"sed -i 's/^allowed_paths:$/allowed_paths:\\n- {EVERYTHING}/' {ticket_file(ticket)}"


def drop_path(ticket, entry):
    """Shell: take the entry ``entry`` out of the ``allowed_paths`` of the ticket's file in the working tree."""
    assert "/" not in entry and "*" not in entry, "the helper takes a plain file name"
    return f"sed -i '/^- {entry}$/d' {ticket_file(ticket)}"


def new_ticket_file(ticket=NEW_TICKET, wbs=NEW_TICKET_WBS, role=ENGINEER, status="in_progress",
                    paths=(EVERYTHING,)):
    """Shell: write a ticket file that no commit holds yet, by default in progress and allowing every path."""
    text = check_support.ticket_text(ticket_id=ticket, wbs_id=wbs, status=status, role=role, allowed_paths=paths)
    return f"printf %s {shlex.quote(text)} > {ticket_file(ticket)}"


def change(path):
    """Shell: change ``path`` in the working tree. Nothing is staged."""
    directory = os.path.dirname(path) or "."
    return f"mkdir -p {shlex.quote(directory)} && echo changed >> {shlex.quote(path)}"


def commit_paths(paths, trailers, subject="work"):
    """Shell: stage ``paths`` as the working tree holds them and commit them together, with ``trailers``."""
    names = " ".join(shlex.quote(path) for path in paths)
    command = f"git add -- {names} && git commit -q -m {shlex.quote(subject)}"
    if trailers is not None:
        role, task = trailers
        command += f" --trailer {shlex.quote('Task: ' + task)} --trailer {shlex.quote('Role: ' + role)}"
    return command


def allowed_paths_at(project, ticket, revision="HEAD"):
    """The ``allowed_paths`` entries of the ticket's file as committed at ``revision``."""
    return _path_entries(check_support.git(project, "show", f"{revision}:{ticket_file(ticket)}"))


def allowed_paths_in_tree(project, ticket):
    """The ``allowed_paths`` entries of the ticket's file in the working tree."""
    return _path_entries(check_support.read(project, ticket_file(ticket)))


def _path_entries(text):
    lines = text.split("allowed_paths:\n", 1)[1].splitlines()
    entries = []
    for line in lines:
        if not line.startswith("- "):
            break
        entries.append(line[2:])
    return entries


def status_at(project, ticket, revision="HEAD"):
    """The ``status`` lines of the ticket's file as committed at ``revision``."""
    text = check_support.git(project, "show", f"{revision}:{ticket_file(ticket)}")
    return [line for line in text.splitlines() if line.startswith("status:")]


def status_in_tree(project, ticket):
    """The ``status`` lines of the ticket's file in the working tree."""
    text = check_support.read(project, ticket_file(ticket))
    return [line for line in text.splitlines() if line.startswith("status:")]


def is_tracked(project, path, revision="HEAD"):
    """True when the tree of ``revision`` holds ``path``."""
    return bool(check_support.git(project, "ls-tree", "-r", "--name-only", revision, "--", path).strip())


def graft_newest_onto(parent):
    """Shell: write ``.git/info/grafts`` so that git takes ``parent`` for the only parent of the newest commit.

    ``parent`` is a commit id or a shell variable (``$old``).
    """
    return f"mkdir -p .git/info && echo \"$(git rev-parse HEAD) {parent}\" > {GRAFTS}"


def ungrafted(project, *args):
    """``git`` in the project reading the real objects: no grafts file and no replacement refs are applied."""
    import subprocess
    env = dict(os.environ, GIT_GRAFT_FILE=os.devnull)
    proc = subprocess.run(["git", "-C", str(project), "--no-replace-objects", *args], env=env,
                          capture_output=True, text=True, check=False)
    assert proc.returncode == 0, f"git {' '.join(args)} failed in the test project: {proc.stderr.strip()}"
    return proc.stdout


def new_commits(project, before, real=True):
    """The ids of the commits in ``before..HEAD``, newest first: as the real objects give them, or as git reads
    them with the project's grafts file applied."""
    read = ungrafted if real else check_support.git
    return read(project, "rev-list", f"{before}..HEAD").split()


def grafts(project):
    """The lines of the project's ``.git/info/grafts``; empty when there is no such file."""
    path = Path(project) / GRAFTS
    return path.read_text(encoding="utf-8").splitlines() if path.is_file() else []


# --------------------------------------------------------------------------
# Seventh batch (DEC-394 as amended by DEC-398): a merge commit read by the merge base
# --------------------------------------------------------------------------

from dataclasses import dataclass  # noqa: E402

ORCHESTRATOR_ON_MAIN = (ORCHESTRATOR, ORCHESTRATOR_TICKET)   # the trailers of ``main``'s own commits
SECOND_BRANCH = "w1/W1-95"         # a second branch to merge
CROSSING = "crossing"              # the other side of a criss-cross history
ISLAND = "island"                  # a branch whose only commit has no parent
OTHER_TEST = f"{ACCEPTANCE}/W1-95/test_other.py"             # another ticket's acceptance test; does not exist yet
AS_OTHER_DESIGNER = (DESIGNER, DOCS_TICKET)                  # the test designer on that other ticket
ISLAND_NOTES = "docs/island.md"                              # does not exist yet; the orchestrator may write it


def _trailer_options(trailers):
    if trailers is None:
        return ""
    role, task = trailers
    return f" --trailer {shlex.quote('Task: ' + task)} --trailer {shlex.quote('Role: ' + role)}"


def commit_object(tree, parents, trailers, subject="Merge"):
    """Shell: the id of a new commit object made with ``git commit-tree``; the trailers are its final block.

    ``tree`` and every parent are a revision or a shell variable (``$empty``); each is put in double quotes.
    """
    message = subject + "\\n"
    if trailers is not None:
        role, task = trailers
        message += f"\\nTask: {task}\\nRole: {role}\\n"
    parent_arguments = " ".join(f"-p \"{parent}\"" for parent in parents)
    return f"$(printf '{message}' | git commit-tree {parent_arguments} \"{tree}\")"


def parents_of(project, commit_id="HEAD"):
    """The ids of the commit's parents, in order."""
    return check_support.git(project, "rev-list", "--parents", "-n", "1", commit_id).split()[1:]


def merge_bases(project, one, other):
    """Every merge base of the two commits (``git merge-base --all``): none, one or several."""
    import subprocess
    proc = subprocess.run(["git", "-C", str(project), "merge-base", "--all", one, other],
                          capture_output=True, text=True, check=False)
    assert proc.returncode in (0, 1), f"git merge-base --all failed: {proc.stderr!r}"
    return proc.stdout.split()


def content_at(project, revision, path):
    """The id of the content ``revision`` holds at ``path``, with its mode; ``None`` when it holds no such path."""
    listing = check_support.git(project, "ls-tree", revision, "--", path).strip()
    return listing.split("\t", 1)[0] if listing else None


def changes_against_first_parent(project, commit_id="HEAD"):
    """The sorted paths the commit changes against its first parent; a rename is two paths."""
    listing = check_support.git(project, "diff", "--no-renames", "--name-only", f"{commit_id}^1", commit_id)
    return sorted(listing.split())


def read_by_the_words(project, commit_id="HEAD"):
    """(own, brought) of a merge commit, worked out from git's own answers by the words of DEC-394 and DEC-398.

    A guard for the fixtures only: it shows that the history a test built is the one its literal expectation
    describes. A path is brought by another parent when the merge commit holds that parent's content of it and
    that content differs from the one merge base of the first parent and that parent. With several merge bases,
    or none, nothing is brought.
    """
    first, *others = parents_of(project, commit_id)
    assert others, f"the fixture is wrong: {commit_id} is no merge commit"
    bases = {other: merge_bases(project, first, other) for other in others}
    fail_closed = [other for other in others if len(bases[other]) != 1]
    assert not fail_closed or len(others) == 1, (
        "the fixture is wrong: an octopus merge with several merge bases, or none, is no case of this suite"
    )
    own, brought = [], []
    for path in changes_against_first_parent(project, commit_id):
        held = content_at(project, commit_id, path)
        from_a_parent = not fail_closed and any(
            content_at(project, other, path) == held and held != content_at(project, bases[other][0], path)
            for other in others
        )
        (brought if from_a_parent else own).append(path)
    return own, brought


@dataclass(frozen=True)
class MergeShape:
    """One history that ends with a merge commit made by ``command``, and how DEC-394 and DEC-398 read it."""
    command: str              # shell: makes the merge commit on ``main`` and moves ``main`` forward to it
    own: tuple                # the paths the merge commit changed itself
    brought: tuple            # the paths another parent brought
    what: str                 # the history, in words
    parents: int = 2
    bases: int = 1            # merge bases of the first parent and each other parent


def assert_shape(project, shape, before):
    """Guard against an empty test: ``HEAD`` is the merge commit ``shape`` describes, made on top of ``before``."""
    parents = parents_of(project)
    assert len(parents) == shape.parents and parents[0] == before, (
        f"the fixture is wrong: HEAD has the parents {parents}; {shape.parents} are expected, the first {before}"
    )
    for other in parents[1:]:
        found = merge_bases(project, before, other)
        assert len(found) == shape.bases, (
            f"the fixture is wrong: the first parent and {other[:12]} have the merge bases {found}, "
            f"not {shape.bases} of them"
        )
    changed = changes_against_first_parent(project)
    assert changed == sorted(shape.own + shape.brought), (
        f"the fixture is wrong: against its first parent the merge commit changes {changed}"
    )
    assert read_by_the_words(project) == (sorted(shape.own), sorted(shape.brought)), (
        f"the fixture is wrong: by the words of DEC-394 and DEC-398 the merge commit's own changes and the "
        f"paths brought are {read_by_the_words(project)}"
    )


def ordinary_integration_merge(project, sandbox, trailers=AS_ORCHESTRATOR):
    """A ticket branch with a test designer's new test and an engineer's source file; ``main`` moved on."""
    ticket_branch(project, sandbox, (NEW_TEST, AS_DESIGNER), (SOURCE, AS_ENGINEER))
    return MergeShape(merge(trailers=trailers), own=(), brought=(NEW_TEST, SOURCE),
                      what=f"an ordinary --no-ff merge of {TICKET_BRANCH}, which brings a test designer's "
                           f"{NEW_TEST} and an engineer's {SOURCE}")


def merge_through_a_new_empty_commit(project, sandbox, trailers):
    """The third review's F1: two test designer's commits are undone through a parent that is new in the move.

    ``main`` holds a test designer's edit of an existing acceptance test and a test designer's new test. The
    command makes an empty commit on top of the commit before those two (the same tree, orchestrator trailers),
    then a merge commit with the parents ``HEAD`` and that empty commit and the earlier commit's tree.
    """
    run(project, sandbox, commits((ACCEPTANCE_FILE, AS_DESIGNER), (NEW_TEST, AS_DESIGNER)))
    empty = commit_object("HEAD~2^{tree}", ["HEAD~2"], AS_ORCHESTRATOR, subject="An empty commit")
    merge_commit = commit_object("HEAD~2^{tree}", ["HEAD", "$empty"], trailers)
    return MergeShape(f"empty={empty} && git merge -q --ff-only {merge_commit}",
                      own=(ACCEPTANCE_FILE, NEW_TEST), brought=(),
                      what=f"a merge commit with trailers {trailers} whose parents are HEAD and a new empty commit "
                           f"on top of HEAD~2, and whose tree is that of HEAD~2: it undoes the test designer's "
                           f"commits of {ACCEPTANCE_FILE} and {NEW_TEST}")


def merge_setting_a_test_back_by_hand(project, sandbox, trailers):
    """A real merge in which an acceptance test is set back to the merged branch's content, which is the merge
    base's: the branch changed a source file only, and ``main`` got a test designer's change of the test."""
    ticket_branch(project, sandbox, (SOURCE, AS_ENGINEER), main_moves_on=False)
    run(project, sandbox, commit(ACCEPTANCE_FILE, AS_DESIGNER, subject="main's test designer commit"))
    command = (f"git merge -q --no-ff --no-commit {shlex.quote(TICKET_BRANCH)} "
               f"&& git checkout -q {shlex.quote(TICKET_BRANCH)} -- {shlex.quote(ACCEPTANCE_FILE)} "
               f"&& git commit -q -m {shlex.quote('Merge ' + TICKET_BRANCH)}" + _trailer_options(trailers))
    return MergeShape(command, own=(ACCEPTANCE_FILE,), brought=(SOURCE,),
                      what=f"a merge of {TICKET_BRANCH} (an engineer's {SOURCE}) with trailers {trailers}, in which "
                           f"{ACCEPTANCE_FILE} is set back to the branch's content; the branch never changed it and "
                           f"main's test designer commit did")


def merge_holding_the_branch_s_whole_tree(project, sandbox, trailers):
    """``-s ours`` turned round: the merge commit's tree is the merged branch's tree. The branch changed a source
    file only; ``main`` got a test designer's edit of an existing test and a test designer's new test."""
    ticket_branch(project, sandbox, (SOURCE, AS_ENGINEER), main_moves_on=False)
    run(project, sandbox, commits((ACCEPTANCE_FILE, AS_DESIGNER), (NEW_TEST, AS_DESIGNER)))
    merge_commit = commit_object(TICKET_BRANCH + "^{tree}", ["HEAD", TICKET_BRANCH], trailers)
    return MergeShape(f"git merge -q --ff-only {merge_commit}",
                      own=(ACCEPTANCE_FILE, NEW_TEST), brought=(SOURCE,),
                      what=f"a merge commit with trailers {trailers}, the parents HEAD and {TICKET_BRANCH} and the "
                           f"tree of {TICKET_BRANCH} (an engineer's {SOURCE}): it drops main's test designer "
                           f"commits of {ACCEPTANCE_FILE} and {NEW_TEST}")


def merge_resolved_by_hand(project, sandbox, trailers=AS_ORCHESTRATOR):
    """Both sides changed an acceptance test by test designer's commits; the conflict is resolved to content
    neither parent holds. The branch also brings a test designer's new test."""
    check_support.git(project, "checkout", "-q", "-b", TICKET_BRANCH)
    run(project, sandbox, commits((ACCEPTANCE_FILE, AS_DESIGNER), (NEW_TEST, AS_DESIGNER)))
    check_support.git(project, "checkout", "-q", "main")
    run(project, sandbox, f"echo main-side >> {ACCEPTANCE_FILE} && "
        + commit_paths([ACCEPTANCE_FILE], AS_DESIGNER, subject="main side"))
    return MergeShape(merge_resolving(ACCEPTANCE_FILE, "new", trailers=trailers),
                      own=(ACCEPTANCE_FILE,), brought=(NEW_TEST,),
                      what=f"a merge of {TICKET_BRANCH} whose conflict in {ACCEPTANCE_FILE} is resolved to content "
                           f"neither parent holds; the branch also brings {NEW_TEST}")


def octopus_merge(project, sandbox, trailers=AS_ORCHESTRATOR):
    """Two branches merged by one commit with three parents: a test designer's new test on one, an engineer's
    source file on the other; ``main`` moved on."""
    for branch, step in ((TICKET_BRANCH, (NEW_TEST, AS_DESIGNER)), (SECOND_BRANCH, (SOURCE, AS_ENGINEER))):
        check_support.git(project, "checkout", "-q", "-b", branch)
        run(project, sandbox, commit(*step))
        check_support.git(project, "checkout", "-q", "main")
    run(project, sandbox, commit(BOOTSTRAP, ORCHESTRATOR_ON_MAIN, subject="main moves on"))
    command = (f"git merge -q --no-ff --no-commit {shlex.quote(TICKET_BRANCH)} {shlex.quote(SECOND_BRANCH)} "
               f"&& git commit -q -m 'Merge two branches'" + _trailer_options(trailers))
    return MergeShape(command, own=(), brought=(NEW_TEST, SOURCE), parents=3,
                      what=f"an octopus merge of {TICKET_BRANCH} (a test designer's {NEW_TEST}) and "
                           f"{SECOND_BRANCH} (an engineer's {SOURCE})")


def criss_cross_merge(project, sandbox, last, trailers):
    """A criss-cross history: ``main`` and ``crossing`` each made a commit, then each merged the other's.

    The two merges are made before the call and hold the same tree. ``crossing`` then gets one more commit,
    ``last`` (a path and its trailers). The command merges ``crossing`` into ``main``: the merge commit's
    parents have two merge bases, and against its first parent it changes exactly ``last``'s path, holding the
    other parent's content of it.
    """
    path, _ = last
    check_support.git(project, "checkout", "-q", "-b", CROSSING)
    run(project, sandbox, commit(NOTES, ORCHESTRATOR_ON_MAIN, subject="the crossing side's own commit"))
    check_support.git(project, "checkout", "-q", "main")
    run(project, sandbox, commit(README, ORCHESTRATOR_ON_MAIN, subject="main's own commit"))
    main_s_own = check_support.git(project, "rev-parse", "HEAD").strip()
    run(project, sandbox, merge(branch=CROSSING, trailers=ORCHESTRATOR_ON_MAIN))
    check_support.git(project, "checkout", "-q", CROSSING)
    run(project, sandbox, merge(branch=main_s_own, trailers=ORCHESTRATOR_ON_MAIN))
    assert (check_support.git(project, "rev-parse", "HEAD^{tree}")
            == check_support.git(project, "rev-parse", "main^{tree}")), (
        "the fixture is wrong: the two crossing merges hold different trees"
    )
    run(project, sandbox, commit(*last, subject="after the crossing"))
    check_support.git(project, "checkout", "-q", "main")
    return MergeShape(merge(branch=CROSSING, trailers=trailers), own=(path,), brought=(), bases=2,
                      what=f"a --no-ff merge with trailers {trailers} of {CROSSING}, whose history crosses main's "
                           f"(two merge bases) and whose last commit changes {path} with trailers {last[1]}")


def unrelated_merge(project, sandbox, root, trailers):
    """A branch ``island`` whose only commit has no parent and adds one file, ``root`` (a path and its
    trailers). The command merges it into ``main`` with ``--allow-unrelated-histories``: no merge base."""
    path, root_trailers = root
    directory = os.path.dirname(path)
    run(project, sandbox,
        f"git checkout -q --orphan {ISLAND} && git rm -rfq . && mkdir -p {shlex.quote(directory)} "
        f"&& echo island > {shlex.quote(path)} && git add -- {shlex.quote(path)} && git commit -q -m 'a root commit'"
        + _trailer_options(root_trailers) + " && git checkout -q main")
    held = check_support.git(project, "ls-tree", "-r", "--name-only", ISLAND).split()
    assert parents_of(project, ISLAND) == [] and held == [path], (
        f"the fixture is wrong: the commit on {ISLAND} has the parents {parents_of(project, ISLAND)} and holds {held}"
    )
    command = (f"git merge -q --no-ff --no-commit --allow-unrelated-histories {ISLAND} "
               f"&& git commit -q -m 'Merge {ISLAND}'" + _trailer_options(trailers))
    return MergeShape(command, own=(path,), brought=(), bases=0,
                      what=f"a --no-ff merge with trailers {trailers} of {ISLAND}, a history with nothing in common "
                           f"with main's, whose one commit adds {path} with trailers {root_trailers}")


def merge_back_after_taking_main(project, sandbox, main_moves_on, trailers=AS_ORCHESTRATOR):
    """The third review's F2: a ticket branch that earlier merged ``main`` into itself is merged back.

    The branch gets an engineer's commit; ``main`` gets a test designer's commit of another ticket's acceptance
    test; the lead merges ``main`` into the branch (orchestrator trailers); the branch then gets an engineer's
    commit and a test designer's. With ``main_moves_on``, ``main`` gets one more commit before the merge-back.
    """
    check_support.git(project, "checkout", "-q", "-b", TICKET_BRANCH)
    run(project, sandbox, commit(SOURCE, AS_ENGINEER, subject="the ticket's first work"))
    check_support.git(project, "checkout", "-q", "main")
    run(project, sandbox, commit(OTHER_TEST, AS_OTHER_DESIGNER, subject="another ticket's acceptance test"))
    check_support.git(project, "checkout", "-q", TICKET_BRANCH)
    run(project, sandbox, merge(branch="main", trailers=AS_ORCHESTRATOR))
    run(project, sandbox, commits((SECOND_SOURCE, AS_ENGINEER), (NEW_TEST, AS_DESIGNER)))
    check_support.git(project, "checkout", "-q", "main")
    if main_moves_on:
        run(project, sandbox, commit(BOOTSTRAP, ORCHESTRATOR_ON_MAIN, subject="main moves on"))
    return MergeShape(merge(trailers=trailers), own=(), brought=(NEW_TEST, SECOND_SOURCE, SOURCE),
                      what=f"a --no-ff merge-back of {TICKET_BRANCH}, which earlier merged main into itself (that "
                           f"merge brought the test designer's {OTHER_TEST}) and then did its own work; main "
                           f"{'moved on' if main_moves_on else 'did not move'} meanwhile")


def second_merge_of_the_same_branch(project, sandbox, trailers=AS_ORCHESTRATOR):
    """The ticket branch is merged once before the call, gets an engineer's commit and a test designer's, and
    is merged again."""
    ticket_branch(project, sandbox, (NEW_TEST, AS_DESIGNER), (SOURCE, AS_ENGINEER))
    run(project, sandbox, merge())
    check_support.git(project, "checkout", "-q", TICKET_BRANCH)
    run(project, sandbox, commits((SECOND_SOURCE, AS_ENGINEER), (SECOND_NEW_TEST, AS_DESIGNER)))
    check_support.git(project, "checkout", "-q", "main")
    return MergeShape(merge(trailers=trailers), own=(), brought=(SECOND_SOURCE, SECOND_NEW_TEST),
                      what=f"a second --no-ff merge of {TICKET_BRANCH}, after two more commits on it")


def merge_taking_theirs(project, sandbox, trailers=AS_ORCHESTRATOR):
    """Both sides changed an acceptance test (test designer's commits) and a source file (engineer's commits);
    the merge takes the merged side's content of both (``-X theirs``)."""
    steps = ((ACCEPTANCE_FILE, AS_DESIGNER), (SOURCE, AS_ENGINEER))
    check_support.git(project, "checkout", "-q", "-b", TICKET_BRANCH)
    run(project, sandbox, commits(*steps))
    check_support.git(project, "checkout", "-q", "main")
    for path, step_trailers in steps:
        run(project, sandbox, f"echo main-side >> {path} && "
            + commit_paths([path], step_trailers, subject="main side"))
    command = (f"git merge -q --no-ff --no-commit -X theirs {shlex.quote(TICKET_BRANCH)} "
               f"&& git commit -q -m {shlex.quote('Merge ' + TICKET_BRANCH)}" + _trailer_options(trailers))
    return MergeShape(command, own=(), brought=(ACCEPTANCE_FILE, SOURCE),
                      what=f"a merge of {TICKET_BRANCH} with -X theirs: both sides changed {ACCEPTANCE_FILE} and "
                           f"{SOURCE}, and the merge commit holds the merged side's content of both")
