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
