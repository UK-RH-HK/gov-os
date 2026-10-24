"""Support code and fixtures for the W2-72 acceptance tests (the standard library and pytest).

W2-72 carries out DEC-918 (a1): containment's merge rule matches DEC-912. Under ``tests/acceptance/``, a path
both parents of a merge commit changed against their merge base is not the merge commit's own change when the
merge commit holds exactly git's own merge of that file: the blob ``git merge-tree --write-tree <first parent>
<other parent>`` writes for it, with no conflict on that file. Any file that differs from git's own merge is
still caught as before (DEC-410).

The tests drive the two public interfaces the W1-50 suite drives:

- the containment post-command check, through the kernel's hooks around one Bash call of an orchestrator
  session in a throw-away project (``tests/acceptance/W1-03/w1_03_support.py``, ``tests/acceptance/W1-50/``);
- ``gov.guard.containment.judge_commits`` (DEC-453), the close's read-only containment gate.

``gov.guard.containment_merge.read_merge``, through which the approval check reads merges, is read to show that
its answer is unchanged (DEC-918 item 4).

**The merges.** As a ticket lead merges ``w2/integrate`` back into its ticket's branch: the checked-out branch
(``main`` in the fixture project, the first parent) moves forward to a merge commit of the merged side
(``w1/W1-90``, the second parent; ``w2/integrate`` in a merge-back), made in an orchestrator session's own call
(DEC-266) and carrying ``Task: DAEO-zz90`` and ``Role: orchestrator`` in its final trailer block. Every commit a
merge brings is a test designer's or an engineer's commit inside the paths of its own trailers, unless a case
says otherwise.

Every guard here reads git, never the check or the helper: it shows that the history a test built is the one its
literal expectation describes, and in particular whether the merge commit holds git's own merge of a file.

The fixtures are at the end of this module; each test module imports those it uses by name. The folder has no
``conftest.py`` of its own (DEC-880, W2-66's KPI 12 case).
"""

from __future__ import annotations

import importlib
import os
import shlex
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "W1-50"))

import w1_50_support as support  # noqa: E402

check_support = support.check_support

REPO_ROOT = check_support.REPO_ROOT
SOURCES = REPO_ROOT / check_support.GOV_PACKAGE_PARENT_REL

ORCHESTRATOR = support.ORCHESTRATOR
TICKET = support.TICKET
AS_DESIGNER = support.AS_DESIGNER
AS_ENGINEER = support.AS_ENGINEER
AS_ORCHESTRATOR = support.AS_ORCHESTRATOR
ORCHESTRATOR_ON_MAIN = support.ORCHESTRATOR_ON_MAIN

BRANCH = support.TICKET_BRANCH                 # the merged side: the second parent
SECOND_BRANCH = support.SECOND_BRANCH          # the third parent of the octopus merge
CROSSING = support.CROSSING
ISLAND = support.ISLAND

ACCEPTANCE = support.ACCEPTANCE
MERGED_TEST = f"{ACCEPTANCE}/{support.WBS}/test_merged.py"     # twenty lines; added on main before the fork
ISLAND_TEST = f"{ACCEPTANCE}/{support.WBS}/test_island.py"     # the one file of the unrelated history
ALSO = support.SECOND_SOURCE                   # pyproject.toml: an engineer's commit on the merged side brings it
SOURCE = support.SOURCE                        # src/gov/guard/decide.py: inside DAEO-zz90's allowed paths
README = support.README                        # outside DAEO-zz90's allowed paths
TICKET_FILE = support.ticket_file(check_support.AUDITOR_TICKET_ID)   # .tickets/DAEO-zz94.md
LINES = 20

# The files whose content ``assert_left_as_the_call_left_it`` compares, besides HEAD, the index and the tree.
WATCHED = (*support.WATCHED, MERGED_TEST, ISLAND_TEST, TICKET_FILE)

MERGE_TREE = ("merge-tree", "--write-tree", "--name-only", "-z", "--no-messages")


# --------------------------------------------------------------------------
# Shell: twenty-line files and their edits
# --------------------------------------------------------------------------

def twenty_lines():
    return "".join(f"LINE_{n} = {n}\n" for n in range(1, LINES + 1))


def set_line(path, number, word):
    """Shell: line ``number`` of ``path`` becomes ``LINE_<number> = "<word>"``. Nothing is staged."""
    assert word.replace("-", "").isalnum(), "the helper takes a plain word"
    return f"sed -i '{number}s/.*/LINE_{number} = \"{word}\"/' {shlex.quote(path)}"


def edit(path, number, word, trailers, subject=None):
    """Shell: set line ``number`` of ``path`` and commit that path alone, with ``trailers``."""
    return set_line(path, number, word) + " && " + support.commit_paths(
        [path], trailers, subject=subject or f"line {number} of {os.path.basename(path)}")


def write_and_commit(path, text, trailers, subject):
    """Shell: ``path`` holds ``text``; commit it alone, with ``trailers``."""
    directory = os.path.dirname(path) or "."
    return (f"mkdir -p {shlex.quote(directory)} && printf %s {shlex.quote(text)} > {shlex.quote(path)} && "
            + support.commit_paths([path], trailers, subject=subject))


def merge_commit(branch=BRANCH, trailers=AS_ORCHESTRATOR, *, before_the_commit="", conflicted=None):
    """Shell: merge ``branch`` into the checked-out branch with a merge commit carrying ``trailers``.

    ``before_the_commit`` (shell) runs between the merge and its commit; what it changes it stages itself.
    With ``conflicted`` (a path), git is to report exactly that path as conflicted, and ``before_the_commit``
    resolves it; without, git's own merge is to be clean.
    """
    if conflicted is None:
        command = f"git merge -q --no-ff --no-commit {shlex.quote(branch)}"
    else:
        command = (f"( git merge -q --no-ff --no-commit {shlex.quote(branch)} > /dev/null 2>&1 || true ) "
                   f"&& test \"$(git diff --name-only --diff-filter=U)\" = {shlex.quote(conflicted)}")
    if before_the_commit:
        command += " && " + before_the_commit
    return command + f" && git commit -q -m {shlex.quote('Merge ' + branch)}" + support._trailer_options(trailers)


# --------------------------------------------------------------------------
# Git's own answers
# --------------------------------------------------------------------------

def git_run(root, *args):
    """``git`` in ``root`` (the real git on the test's ``PATH``), as a finished process."""
    env = dict(os.environ, GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_SYSTEM=os.devnull)
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, env=env, check=False)


@dataclass(frozen=True)
class GitMerge:
    """What ``git merge-tree --write-tree <first> <other>`` writes: its tree and the paths it reports as conflicted."""
    tree: str
    conflicted: tuple
    returncode: int


def git_s_own_merge(root, first, other, unrelated=False):
    """Git's own merge of two commits (``git merge-tree --write-tree``, DEC-912). It must run: 0 clean, 1 with
    conflicts."""
    args = list(MERGE_TREE) + (["--allow-unrelated-histories"] if unrelated else []) + [first, other]
    proc = git_run(root, *args)
    assert proc.returncode in (0, 1), f"the fixture is wrong: `git {' '.join(args)}` failed: {proc.stderr.strip()}"
    tree, *conflicted = [part for part in proc.stdout.split("\0") if part]
    return GitMerge(tree, tuple(sorted(set(conflicted))), proc.returncode)


def full_id(root, revision):
    proc = git_run(root, "rev-parse", "--verify", "--quiet", f"{revision}^{{commit}}")
    assert proc.returncode == 0 and proc.stdout.strip(), (
        f"the repository at {root} holds no commit {revision!r}: {proc.stderr.strip()}"
    )
    return proc.stdout.strip()


def parents_of(root, commit_id="HEAD"):
    proc = git_run(root, "rev-list", "--parents", "-n", "1", commit_id)
    assert proc.returncode == 0, f"git rev-list failed: {proc.stderr.strip()}"
    return proc.stdout.split()[1:]


def merge_bases(root, one, other):
    proc = git_run(root, "merge-base", "--all", one, other)
    assert proc.returncode in (0, 1), f"git merge-base --all failed: {proc.stderr.strip()}"
    return proc.stdout.split()


def content_at(root, tree_ish, path):
    """``<mode> <type> <id>`` of ``path`` in ``tree_ish`` (a commit or a tree); ``None`` when it holds no such path."""
    proc = git_run(root, "ls-tree", tree_ish, "--", path)
    assert proc.returncode == 0, f"git ls-tree {tree_ish} failed: {proc.stderr.strip()}"
    listing = proc.stdout.strip()
    return listing.split("\t", 1)[0] if listing else None


def changed_since(root, base, revision, under):
    """The paths under ``under`` whose content differs between ``base`` and ``revision``, without renames."""
    proc = git_run(root, "diff", "--no-renames", "--name-only", base, revision, "--", under)
    assert proc.returncode == 0, f"git diff failed: {proc.stderr.strip()}"
    return sorted(proc.stdout.split())


def tree_paths(root, revision="HEAD"):
    proc = git_run(root, "ls-tree", "-r", "--name-only", revision)
    assert proc.returncode == 0, f"git ls-tree -r failed: {proc.stderr.strip()}"
    return sorted(proc.stdout.split())


def trailer_values(root, commit_id, key):
    proc = git_run(root, "log", "-1", f"--format=%(trailers:key={key},valueonly,separator=%x00)", commit_id)
    assert proc.returncode == 0, f"git log failed: {proc.stderr.strip()}"
    return [value for value in proc.stdout.rstrip("\n").split("\0") if value]


# --------------------------------------------------------------------------
# The merges
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Merge:
    """A history that ends with a merge commit, made on ``main`` by ``command`` in the call."""
    name: str
    command: str
    path: str                 # the path the case is about
    own: tuple | None         # read_merge's ``own`` as it is today (DEC-410); None: every path of the merge tree
    brought: tuple            # read_merge's ``brought`` as it is today (DEC-410, DP-22)
    what: str
    parents: int = 2
    bases: int = 1
    git_s_own: bool = True    # the merge commit holds git's own merge of ``path``, with no conflict on it
    conflicted: tuple = ()    # the paths git's own merge reports as conflicted
    unrelated: bool = False


def _the_test_on_main(project, sandbox, path=MERGED_TEST, trailers=AS_DESIGNER):
    """``main``: one commit adds a twenty-line file (by default an acceptance test, by a test designer)."""
    support.run(project, sandbox, write_and_commit(path, twenty_lines(), trailers, f"twenty lines of {path}"))


def _two_sides(project, sandbox, branch_steps, main_steps):
    """The merged side gets the commands ``branch_steps`` on ``w1/W1-90`` cut from ``main``; ``main`` then gets
    ``main_steps``. ``main`` is checked out."""
    support.ticket_branch_of(project, sandbox, *branch_steps, main_moves_on=False)
    for step in main_steps:
        support.run(project, sandbox, step)


def _clean_combination_history(project, sandbox, by_on_the_branch=AS_DESIGNER):
    """A test designer's twenty-line acceptance test on ``main``; since the fork the merged side changed its line
    2 (a commit with ``by_on_the_branch``) and got an engineer's commit of ``pyproject.toml``; ``main`` changed
    its line 19 (a test designer's commit). Git combines the two edits without a conflict."""
    _the_test_on_main(project, sandbox)
    _two_sides(project, sandbox,
               (edit(MERGED_TEST, 2, "the-merged-side", by_on_the_branch),
                support.commit(ALSO, AS_ENGINEER, subject="the merged side's other work")),
               (edit(MERGED_TEST, 19, "main", AS_DESIGNER),))


def clean_combination(project, sandbox):
    """Success: git's own clean combination of two sides' edits of one acceptance test."""
    _clean_combination_history(project, sandbox)
    return Merge("a-clean-combination-of-two-sides-edits", merge_commit(), MERGED_TEST,
                 own=(MERGED_TEST,), brought=(ALSO,),
                 what=f"an ordinary --no-ff merge of {BRANCH} with orchestrator trailers; a test designer changed "
                      f"line 2 of {MERGED_TEST} on the merged side and line 19 on main, and git combined the two "
                      f"edits without a conflict; the merged side also brings an engineer's {ALSO}")


def same_change(project, sandbox):
    """Success: both sides made the same edit of one acceptance test."""
    _the_test_on_main(project, sandbox)
    _two_sides(project, sandbox,
               (edit(MERGED_TEST, 2, "both-sides", AS_DESIGNER, subject="the merged side's edit"),
                support.commit(ALSO, AS_ENGINEER, subject="the merged side's other work")),
               (edit(MERGED_TEST, 2, "both-sides", AS_DESIGNER, subject="the same edit on main"),))
    return Merge("the-same-edit-on-both-sides", merge_commit(), MERGED_TEST,
                 own=(MERGED_TEST,), brought=(ALSO,),
                 what=f"an ordinary --no-ff merge of {BRANCH} with orchestrator trailers; a test designer made the "
                      f"same edit of line 2 of {MERGED_TEST} on both sides; the merged side also brings an "
                      f"engineer's {ALSO}")


def conflict_on_another_file(project, sandbox):
    """Success, per file (the shape of ``03f470a5``): the clean combination of the acceptance test, and a
    conflict git reports on a source file, which both sides' engineers changed; it is resolved by hand."""
    _the_test_on_main(project, sandbox)
    _two_sides(project, sandbox,
               (edit(MERGED_TEST, 2, "the-merged-side", AS_DESIGNER),
                f"echo \"VALUE = 'the merged side'\" > {SOURCE} && "
                + support.commit_paths([SOURCE], AS_ENGINEER, subject="the merged side's engineer")),
               (edit(MERGED_TEST, 19, "main", AS_DESIGNER),
                f"echo \"VALUE = 'main'\" > {SOURCE} && "
                + support.commit_paths([SOURCE], AS_ENGINEER, subject="main's engineer")))
    resolve = f"echo \"VALUE = 'both'\" > {SOURCE} && git add -- {SOURCE}"
    return Merge("a-conflict-on-another-file-resolved-by-hand",
                 merge_commit(before_the_commit=resolve, conflicted=SOURCE), MERGED_TEST,
                 own=(SOURCE, MERGED_TEST), brought=(), conflicted=(SOURCE,),
                 what=f"a --no-ff merge of {BRANCH} with orchestrator trailers in which git combines two test "
                      f"designers' edits of {MERGED_TEST} cleanly and reports a conflict on {SOURCE} only "
                      f"(both sides' engineers changed it), which the merge commit resolves by hand")


def brought_by_an_engineer(project, sandbox):
    """Success for the merge commit: the clean combination, where the merged side's edit of the test is an
    engineer's commit. DEC-918 item 2 (not (a2)): the bringing commits are judged at their own closes and by
    W1-01; that commit is still judged by its own trailers wherever it is judged."""
    _clean_combination_history(project, sandbox, by_on_the_branch=AS_ENGINEER)
    return Merge("the-merged-side-s-edit-an-engineer-s", merge_commit(), MERGED_TEST,
                 own=(MERGED_TEST,), brought=(ALSO,),
                 what=f"an ordinary --no-ff merge of {BRANCH} with orchestrator trailers; an engineer's commit "
                      f"changed line 2 of {MERGED_TEST} on the merged side, a test designer's line 19 on main, and "
                      f"git combined the two edits without a conflict")


def hand_edit_of_a_clean_merge(project, sandbox):
    """Failure: the clean combination, and one more line changed by hand before the merge is committed."""
    _clean_combination_history(project, sandbox)
    by_hand = set_line(MERGED_TEST, 10, "by-hand") + f" && git add -- {MERGED_TEST}"
    return Merge("a-hand-edit-on-top-of-a-clean-merge", merge_commit(before_the_commit=by_hand), MERGED_TEST,
                 own=(MERGED_TEST,), brought=(ALSO,), git_s_own=False,
                 what=f"the clean combination of two sides' edits of {MERGED_TEST}, with line 10 changed by hand "
                      f"before the merge commit")


def another_mode(project, sandbox):
    """Failure: the clean combination, committed with the executable mode."""
    _clean_combination_history(project, sandbox)
    mode = f"chmod +x {MERGED_TEST} && git add -- {MERGED_TEST}"
    return Merge("git-s-content-in-another-mode", merge_commit(before_the_commit=mode), MERGED_TEST,
                 own=(MERGED_TEST,), brought=(ALSO,), git_s_own=False,
                 what=f"the clean combination of two sides' edits of {MERGED_TEST}, committed with the mode 100755: "
                      f"git's content of the file in another mode")


# name: (shell that resolves the conflict in MERGED_TEST, or None for the blob git writes for it, in words)
RESOLUTIONS = {
    "resolved-by-hand": (set_line(MERGED_TEST, 2, "both-sides"), "resolved by hand to content neither side holds"),
    "the-merged-side-s-version-whole": (f"git checkout --theirs -- {MERGED_TEST}",
                                        "resolved by taking the merged side's version whole"),
    "the-first-parent-s-version-whole": (f"git checkout --ours -- {MERGED_TEST}",
                                         "resolved by taking the first parent's version whole"),
    "held-as-git-writes-it-with-its-markers": (None, "held exactly as git's own merge writes it, with its conflict "
                                                     "markers"),
}


def conflict_in_the_file(project, sandbox, resolution):
    """Failure: both sides changed line 2 of the acceptance test, each in its own way; git reports a conflict on
    it, and the merge commit holds one of ``RESOLUTIONS``."""
    _the_test_on_main(project, sandbox)
    _two_sides(project, sandbox,
               (edit(MERGED_TEST, 2, "the-merged-side", AS_DESIGNER),
                support.commit(ALSO, AS_ENGINEER, subject="the merged side's other work")),
               (edit(MERGED_TEST, 2, "main", AS_DESIGNER),))
    resolve, words = RESOLUTIONS[resolution]
    if resolve is None:
        own = git_s_own_merge(project, full_id(project, "HEAD"), full_id(project, BRANCH))
        assert own.conflicted == (MERGED_TEST,), f"the fixture is wrong: git's own merge reports {own.conflicted}"
        blob = content_at(project, own.tree, MERGED_TEST).split()[2]
        resolve = f"git cat-file blob {blob} > {MERGED_TEST}"
    resolve += f" && git add -- {MERGED_TEST}"
    return Merge(f"a-conflict-in-the-file-{resolution}",
                 merge_commit(before_the_commit=resolve, conflicted=MERGED_TEST), MERGED_TEST,
                 own=(MERGED_TEST,), brought=(ALSO,), git_s_own=False, conflicted=(MERGED_TEST,),
                 what=f"a --no-ff merge of {BRANCH} with orchestrator trailers; both sides' test designers changed "
                      f"line 2 of {MERGED_TEST}, git reports the conflict, and the file is {words}")


def octopus(project, sandbox):
    """Failure: an octopus merge (three parents) of clean edits of one acceptance test: line 2 on the merged
    side, line 10 on a second branch, line 19 on ``main``, each a test designer's commit."""
    _the_test_on_main(project, sandbox)
    for branch, steps in ((BRANCH, (edit(MERGED_TEST, 2, "the-merged-side", AS_DESIGNER),
                                    support.commit(ALSO, AS_ENGINEER, subject="the merged side's other work"))),
                          (SECOND_BRANCH, (edit(MERGED_TEST, 10, "the-second-branch", AS_DESIGNER),))):
        check_support.git(project, "checkout", "-q", "-b", branch, "main")
        for step in steps:
            support.run(project, sandbox, step)
    check_support.git(project, "checkout", "-q", "main")
    support.run(project, sandbox, edit(MERGED_TEST, 19, "main", AS_DESIGNER))
    command = (f"git merge -q --no-ff --no-commit {shlex.quote(BRANCH)} {shlex.quote(SECOND_BRANCH)} "
               f"&& git commit -q -m 'Merge two branches'" + support._trailer_options(AS_ORCHESTRATOR))
    return Merge("an-octopus-merge-of-clean-edits", command, MERGED_TEST, own=(MERGED_TEST,), brought=(ALSO,),
                 parents=3, git_s_own=False,
                 what=f"an octopus merge (three parents) with orchestrator trailers of {BRANCH} and {SECOND_BRANCH}; "
                      f"test designers changed lines 2, 10 and 19 of {MERGED_TEST} on the three sides and git "
                      f"combined them without a conflict")


def criss_cross(project, sandbox):
    """Failure: the parents have two merge bases. ``main`` and ``crossing`` each made a commit and then merged
    the other's; since then ``crossing`` changed line 2 of the acceptance test and ``main`` line 19, each by a
    test designer's commit. Git's own merge combines them without a conflict, and the merge commit holds it."""
    _the_test_on_main(project, sandbox)
    check_support.git(project, "checkout", "-q", "-b", CROSSING)
    support.run(project, sandbox, support.commit(support.NOTES, ORCHESTRATOR_ON_MAIN, subject="the crossing's own"))
    check_support.git(project, "checkout", "-q", "main")
    support.run(project, sandbox, support.commit(README, ORCHESTRATOR_ON_MAIN, subject="main's own commit"))
    main_s_own = check_support.git(project, "rev-parse", "HEAD").strip()
    support.run(project, sandbox, support.merge(branch=CROSSING, trailers=ORCHESTRATOR_ON_MAIN))
    check_support.git(project, "checkout", "-q", CROSSING)
    support.run(project, sandbox, support.merge(branch=main_s_own, trailers=ORCHESTRATOR_ON_MAIN))
    support.run(project, sandbox, edit(MERGED_TEST, 2, "the-crossing", AS_DESIGNER))
    check_support.git(project, "checkout", "-q", "main")
    support.run(project, sandbox, edit(MERGED_TEST, 19, "main", AS_DESIGNER))
    return Merge("a-criss-cross-history-with-two-merge-bases", merge_commit(branch=CROSSING), MERGED_TEST,
                 own=(MERGED_TEST,), brought=(), bases=2,
                 what=f"a --no-ff merge of {CROSSING} with orchestrator trailers whose history crosses main's (two "
                      f"merge bases); test designers changed line 2 of {MERGED_TEST} there and line 19 on main, and "
                      f"the merge commit holds git's own clean merge of the file")


def unrelated(project, sandbox):
    """Failure: the parents have no merge base. A branch ``island`` whose one commit has no parent adds an
    acceptance test (a test designer's commit); ``git merge --allow-unrelated-histories`` brings it, and the
    merge commit holds git's own clean merge of it."""
    shape = support.unrelated_merge(project, sandbox, (ISLAND_TEST, AS_DESIGNER), AS_ORCHESTRATOR)
    return Merge("unrelated-histories-with-no-merge-base", shape.command, ISLAND_TEST, own=None, brought=(),
                 bases=0, unrelated=True,
                 what=f"a --no-ff merge with orchestrator trailers of {ISLAND}, a history with nothing in common "
                      f"with main's, whose one commit adds {ISLAND_TEST}; the merge commit holds git's own clean "
                      f"merge of the two")


def ticket_file_clean_combination(project, sandbox):
    """Nothing else changes (DEC-421): an orchestrator's commit appended a line to a ticket file on the merged
    side and another changed a line near its top on ``main``; git combines them without a conflict."""
    _two_sides(project, sandbox,
               (f"echo appended-on-the-merged-side >> {TICKET_FILE} && "
                + support.commit_paths([TICKET_FILE], AS_ORCHESTRATOR, subject="a line at the end"),
                support.commit(ALSO, AS_ENGINEER, subject="the merged side's other work")),
               (f"sed -i 's/^priority: 1$/priority: 2/' {TICKET_FILE} && "
                + support.commit_paths([TICKET_FILE], ORCHESTRATOR_ON_MAIN, subject="a line near the top"),))
    return Merge("a-clean-combination-of-two-sides-edits-of-a-ticket-file", merge_commit(), TICKET_FILE,
                 own=(TICKET_FILE,), brought=(ALSO,),
                 what=f"an ordinary --no-ff merge of {BRANCH} with orchestrator trailers; orchestrator's commits "
                      f"appended a line to {TICKET_FILE} on the merged side and changed its priority line on main, "
                      f"and git combined the two without a conflict")


def other_path_clean_combination(project, sandbox):
    """Nothing else changes (read_merge's rule, DEC-269): ``README.md`` (twenty lines, an orchestrator's
    commits on both sides) is cleanly combined by git; the merge commit carries an engineer's trailers, whose
    ticket's paths do not hold ``README.md``."""
    _the_test_on_main(project, sandbox, path=README, trailers=AS_ORCHESTRATOR)
    _two_sides(project, sandbox,
               (edit(README, 2, "the-merged-side", AS_ORCHESTRATOR),
                support.commit(ALSO, AS_ENGINEER, subject="the merged side's other work")),
               (edit(README, 19, "main", AS_ORCHESTRATOR),))
    return Merge("a-clean-combination-of-another-path-under-an-engineer-s-trailers",
                 merge_commit(trailers=AS_ENGINEER), README, own=(README,), brought=(ALSO,),
                 what=f"an ordinary --no-ff merge of {BRANCH} whose merge commit carries an engineer's trailers on "
                      f"{TICKET}; orchestrator's commits changed line 2 of {README} on the merged side and line 19 "
                      f"on main, and git combined the two without a conflict")


SUCCESS = {
    "a-clean-combination-of-two-sides-edits": clean_combination,
    "the-same-edit-on-both-sides": same_change,
    "a-conflict-on-another-file-resolved-by-hand": conflict_on_another_file,
}

FAILURE = {
    "a-hand-edit-on-top-of-a-clean-merge": hand_edit_of_a_clean_merge,
    "git-s-content-in-another-mode": another_mode,
    **{f"a-conflict-in-the-file-{name}": (lambda project, sandbox, name=name: conflict_in_the_file(
        project, sandbox, name)) for name in RESOLUTIONS},
    "an-octopus-merge-of-clean-edits": octopus,
    "a-criss-cross-history-with-two-merge-bases": criss_cross,
    "unrelated-histories-with-no-merge-base": unrelated,
}

UNCHANGED = {
    "a-clean-combination-of-two-sides-edits-of-a-ticket-file": ticket_file_clean_combination,
    "a-clean-combination-of-another-path-under-an-engineer-s-trailers": other_path_clean_combination,
}

EVERY_MERGE = {**SUCCESS, "the-merged-side-s-edit-an-engineer-s": brought_by_an_engineer, **FAILURE, **UNCHANGED}


# --------------------------------------------------------------------------
# Guards against an empty test
# --------------------------------------------------------------------------

def assert_shape(project, shape, before, merge_id):
    """From git's own answers: ``merge_id`` is a merge commit on top of ``before`` with ``shape.parents``
    parents and ``shape.bases`` merge bases; whether it holds git's own merge of ``shape.path``, and which paths
    git reports as conflicted, are as ``shape`` says."""
    parents = parents_of(project, merge_id)
    assert len(parents) == shape.parents and parents[0] == before, (
        f"the fixture is wrong: {shape.what}: the merge commit has the parents {parents}; {shape.parents} are "
        f"expected, the first {before}"
    )
    for other in parents[1:]:
        found = merge_bases(project, before, other)
        assert len(found) == shape.bases, (
            f"the fixture is wrong: {shape.what}: the first parent and {other[:12]} have the merge bases {found}"
        )
    held = content_at(project, merge_id, shape.path)
    assert held is not None, f"the fixture is wrong: {shape.what}: the merge commit holds no {shape.path}"
    if shape.parents == 3:
        assert all(content_at(project, parent, shape.path) != held for parent in parents), (
            f"the fixture is wrong: {shape.what}: a parent holds the merge commit's content of {shape.path}"
        )
        return
    merged = git_s_own_merge(project, parents[0], parents[1], unrelated=shape.unrelated)
    assert merged.conflicted == tuple(sorted(shape.conflicted)), (
        f"the fixture is wrong: {shape.what}: git's own merge reports the conflicts {merged.conflicted}"
    )
    if shape.bases == 1:
        base = merge_bases(project, *parents)[0]
        at_base = content_at(project, base, shape.path)
        assert all(content_at(project, parent, shape.path) != at_base for parent in parents), (
            f"the fixture is wrong: {shape.what}: not both parents changed {shape.path} against their merge base"
        )
    holds_git_s = held == content_at(project, merged.tree, shape.path) and shape.path not in merged.conflicted
    assert holds_git_s == shape.git_s_own, (
        f"the fixture is wrong: {shape.what}: the merge commit {'does not hold' if shape.git_s_own else 'holds'} "
        f"exactly git's own merge of {shape.path} ({held} against {content_at(project, merged.tree, shape.path)})"
    )


def expected_own(project, shape, merge_id):
    return sorted(shape.own) if shape.own is not None else tree_paths(project, merge_id)


# --------------------------------------------------------------------------
# A merge-tree run that cannot run: a ``git`` earlier on PATH
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class FailingMergeTree:
    """A directory holding a ``git`` that fails the ``merge-tree`` subcommand and passes every other call to the
    real git; each refused call adds one line to ``log``."""
    directory: Path
    log: Path
    exit_code: int

    def path_variable(self):
        return f"{self.directory}{os.pathsep}{os.environ.get('PATH', '')}"

    def refused(self):
        """The refused ``merge-tree`` calls so far, one line each."""
        return self.log.read_text(encoding="utf-8").splitlines() if self.log.is_file() else []


# name: (exit code, what the refused call prints on stderr)
CANNOT_RUN = {
    "a-fatal-error": (128, "fatal: git merge-tree cannot run here (W2-72 acceptance test)"),
    "a-git-without-write-tree": (129, "usage: git merge-tree <base-tree> <branch1> <branch2>"),
}


def failing_merge_tree(directory, case):
    """Write the failing ``git`` into ``directory`` (a new, empty folder) and return it."""
    exit_code, message = CANNOT_RUN[case]
    real = shutil.which("git")
    assert real and Path(real).resolve() != (Path(directory) / "git").resolve(), "no real git on PATH"
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    log = directory / "refused-merge-tree-calls.log"
    script = directory / "git"
    script.write_text(
        "#!/bin/sh\n"
        "for word in \"$@\"; do\n"
        "  if [ \"$word\" = merge-tree ]; then\n"
        f"    printf '%s\\n' \"$*\" >> {shlex.quote(str(log))}\n"
        f"    echo {shlex.quote(message)} >&2\n"
        f"    exit {exit_code}\n"
        "  fi\n"
        "done\n"
        f"exec {shlex.quote(real)} \"$@\"\n", encoding="utf-8")
    script.chmod(0o755)
    return FailingMergeTree(directory, log, exit_code)


def judge_in_a_process(root, commit_ids, environment):
    """``judge_commits(root, commit_ids)`` in a new Python process of this repository's ``src`` with
    ``environment`` over a caller-free environment. Returns [(commit, sorted paths, reason)]."""
    program = (
        "import json, sys\n"
        "from gov.guard.containment import judge_commits\n"
        "import gov.guard.containment as module\n"
        f"assert module.__file__.startswith({str(SOURCES)!r}), module.__file__\n"
        "findings = judge_commits(sys.argv[1], sys.argv[2:])\n"
        "print(json.dumps([[f.commit, sorted(f.paths), f.reason] for f in findings]))\n"
    )
    env = {key: value for key, value in os.environ.items()
           if key not in (check_support.ROLE_ENV, check_support.TICKET_ENV, "CLAUDE_PROJECT_DIR")}
    env.update({"PYTHONPATH": str(SOURCES), "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull,
                "PYTHONDONTWRITEBYTECODE": "1"})
    env.update(environment)
    proc = subprocess.run([sys.executable, "-c", program, str(root), *commit_ids], capture_output=True, text=True,
                          env=env, timeout=120, check=False)
    return proc


# --------------------------------------------------------------------------
# Findings of the check, by the commit they are for
# --------------------------------------------------------------------------

def findings_for(result, commit_id, what):
    """The findings this call added whose ``reason`` is for the commit (``commit <12 digits>``)."""
    return [f for f in check_support.new_findings(result, what) if f"commit {commit_id[:12]}" in f["reason"]]


# --------------------------------------------------------------------------
# Fixtures: each test module imports those it uses by name
# --------------------------------------------------------------------------

def _entry(find):
    try:
        return find()
    except check_support.HookMissing as exc:
        reason = str(exc)
    pytest.fail(reason, pytrace=False)


@pytest.fixture(scope="session")
def hook():
    """The containment check's PostToolUse hook script in the kernel template."""
    return _entry(check_support.hook_entry)


@pytest.fixture(scope="session")
def guard_hook(hook):
    """The kernel's PreToolUse hook script, where the check takes its before-snapshot (DEC-126)."""
    return _entry(check_support.guard_entry)


@pytest.fixture()
def sandbox(tmp_path):
    """``HOME``, the system temporary directory and an unrelated directory, all outside the project."""
    return check_support.make_sandbox(tmp_path / "sandbox")


@pytest.fixture()
def project(hook, guard_hook, tmp_path):
    """A committed project on ``main`` with a clean working tree and the fixture tickets, all in progress."""
    return check_support.make_project(tmp_path / "project")


@pytest.fixture()
def call(sandbox):
    """``call(project, command, role, ticket, check_environment=None)`` -> (result, state after).

    One whole Bash call that moves ``HEAD`` on the same branch and leaves a clean tree: the PreToolUse hook,
    the command for real, the PostToolUse hook (the containment check). ``state after`` is taken between the
    command and the check. ``check_environment`` replaces variables of the check's environment only.
    """

    def _call(project, command, role, ticket, check_environment=None):
        seen = len(check_support.finding_lines(project))
        before = check_support.head(project)
        the_call = check_support.script_call(sandbox, command)
        guard = check_support.run_guard(project, the_call, sandbox, role=role, ticket=ticket)
        check_support.assert_let_through(guard, the_call)
        bash = check_support.run_bash(project, the_call.command, sandbox)
        assert bash.returncode == 0, (
            f"the fixture command `{command}` failed: {bash.stdout.strip()!r} {bash.stderr.strip()!r}"
        )
        left = check_support.state(project, WATCHED)
        assert left[0][0] != before[0], f"the fixture command `{command}` did not move HEAD"
        assert left[0][1] == before[1], f"the fixture command `{command}` left the branch {before[1]!r}"
        assert left[1] == "", f"the fixture command `{command}` left uncommitted changes:\n{left[1]}"
        result = check_support.run_check(project, the_call, sandbox, role=role, ticket=ticket, bash=bash, seen=seen,
                                         environment=check_environment)
        return result, left

    return _call


def _caller_free(monkeypatch):
    for name in (check_support.ROLE_ENV, check_support.TICKET_ENV, "CLAUDE_PROJECT_DIR"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", os.devnull)
    monkeypatch.setenv("GIT_CONFIG_SYSTEM", os.devnull)
    monkeypatch.syspath_prepend(str(SOURCES))


def _imported(name, function):
    try:
        module = importlib.import_module(name)
    except ImportError as exc:
        pytest.fail(f"`import {name}` fails: {exc}", pytrace=False)
    assert str(module.__file__).startswith(str(SOURCES)), (
        f"`{name}` was imported from {module.__file__}, not from this worktree's {SOURCES}"
    )
    found = getattr(module, function, None)
    if not callable(found):
        pytest.fail(f"{name} has no function `{function}`", pytrace=False)
    return found


@pytest.fixture()
def judge(monkeypatch):
    """``judge(root, commit_ids)`` -> the findings of ``gov.guard.containment.judge_commits`` (DEC-453),
    imported from this worktree's ``src`` in a process that says nothing of a caller."""
    _caller_free(monkeypatch)

    def _judge(root, commit_ids):
        return _imported("gov.guard.containment", "judge_commits")(str(root), list(commit_ids))

    return _judge


@pytest.fixture()
def read_merge(monkeypatch):
    """``read_merge(root, commit_id)`` -> ``gov.guard.containment_merge.read_merge`` (DEC-398), the reader the
    approval check reads merges through, imported from this worktree's ``src``."""
    _caller_free(monkeypatch)

    def _read(root, commit_id):
        return _imported("gov.guard.containment_merge", "read_merge")(str(root), commit_id)

    return _read
