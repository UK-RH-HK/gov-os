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
# Review 1 (DEC-918): a merge made over two Bash calls, renames, a file replaced by a directory
# --------------------------------------------------------------------------

NEW_TEST = support.NEW_TEST                                    # only the merged side adds it
RENAMED_TEST = f"{ACCEPTANCE}/{support.WBS}/test_renamed.py"   # MERGED_TEST's name after a ``git mv``
INNER_TEST = f"{MERGED_TEST}/test_inner.py"                    # the one file of the directory put at MERGED_TEST
FOLDER = f"{ACCEPTANCE}/{support.WBS}/"                        # the folder of every acceptance test of these cases

# The files whose content a snapshot of a call compares, besides HEAD, ``git status`` and the index.
WATCHED_ACROSS = (*WATCHED, RENAMED_TEST, INNER_TEST)


def new_test_text():
    return "".join(f"NEW_{n} = {n}\n" for n in range(1, LINES + 1))


def merge_head(root):
    """The commit a merge in progress merges (``MERGE_HEAD``); ``None`` when no merge is in progress."""
    proc = git_run(root, "rev-parse", "-q", "--verify", "MERGE_HEAD")
    return proc.stdout.strip() if proc.returncode == 0 else None


def unmerged_paths(root):
    """The paths the index holds unmerged (conflicted), sorted."""
    proc = git_run(root, "ls-files", "-u", "-z")
    assert proc.returncode == 0, f"git ls-files -u failed: {proc.stderr.strip()}"
    return tuple(sorted({entry.split("\t", 1)[1] for entry in proc.stdout.split("\0") if entry}))


def index_entries(root):
    """``git ls-files -s``: every entry of the index with its mode, blob and stage."""
    proc = git_run(root, "ls-files", "-s")
    assert proc.returncode == 0, f"git ls-files -s failed: {proc.stderr.strip()}"
    return proc.stdout


def folder_listing(root, tree_ish, folder=FOLDER):
    """``git ls-tree -r`` of ``folder`` in ``tree_ish``: every file under it with its mode and blob."""
    proc = git_run(root, "ls-tree", "-r", tree_ish, "--", folder)
    assert proc.returncode == 0, f"git ls-tree -r {tree_ish} failed: {proc.stderr.strip()}"
    return proc.stdout


def snapshot(root):
    """HEAD, ``git status`` with every file listed, the watched files' content, and the index."""
    return check_support.state(root, WATCHED_ACROSS), index_entries(root)


@dataclass(frozen=True)
class Observed:
    """One Bash call between the kernel's two hooks, as it went."""
    command: str
    exit_code: int            # the command's own; not 0: the harness sends PostToolUseFailure
    result: object            # the containment check's result (``check_support.HookResult``)
    left: tuple               # ``snapshot`` between the command and the check
    after: tuple              # ``snapshot`` after the check
    merging: str | None       # MERGE_HEAD between the command and the check
    unmerged: tuple           # the unmerged paths between the command and the check

    def kept(self):
        """The check moved nothing: HEAD, the index, the working tree as the command left them."""
        return self.after == self.left

    def told(self, label):
        """What the agent was told and what was recorded, for a message."""
        return (f"{label} (`{self.command}`, exit {self.exit_code}): the agent was told {self.result.report!r} "
                f"(hook exit {self.result.returncode}); findings recorded: {list(self.result.new_lines)}")

    def change(self):
        """What the check changed, for a message."""
        (_, status_left, contents_left), index_left = self.left
        (_, status_after, contents_after), index_after = self.after
        changed = [path for path in contents_left if contents_left[path] != contents_after[path]]
        lines_left, lines_after = set(index_left.splitlines()), set(index_after.splitlines())
        return (f"files changed by the check: {changed}; git status after the command:\n{status_left}"
                f"after the check:\n{status_after}index entries the check took out: {sorted(lines_left - lines_after)}"
                f"; put in: {sorted(lines_after - lines_left)}")


def bash_call(project, sandbox, command, role, ticket):
    """One Bash call of a session: the PreToolUse hook, ``command`` for real, the containment check (PostToolUse,
    or PostToolUseFailure when the command failed, as the harness sends it). Nothing is asked of where the call
    leaves HEAD or the tree; the caller's guards read that from ``Observed``."""
    seen = len(check_support.finding_lines(project))
    the_call = check_support.script_call(sandbox, command)
    guard = check_support.run_guard(project, the_call, sandbox, role=role, ticket=ticket)
    check_support.assert_let_through(guard, the_call)
    bash = check_support.run_bash(project, the_call.command, sandbox)
    left = snapshot(project)
    merging, unmerged = merge_head(project), unmerged_paths(project)
    result = check_support.run_check(project, the_call, sandbox, role=role, ticket=ticket, bash=bash,
                                     failed=bash.returncode != 0, seen=seen)
    return Observed(command, bash.returncode, result, left, snapshot(project), merging, unmerged)


def commit_the_merge(trailers=AS_ORCHESTRATOR, before_the_commit=""):
    """Shell: commit the merge in progress with ``trailers``; ``before_the_commit`` (shell) runs first."""
    command = (before_the_commit + " && ") if before_the_commit else ""
    return command + f"git commit -q -m {shlex.quote('Merge ' + BRANCH)}" + support._trailer_options(trailers)


START_THE_MERGE = f"git merge -q --no-ff --no-commit {shlex.quote(BRANCH)}"
STAGE_THE_TESTS = f"git add -A -- {shlex.quote(ACCEPTANCE)}"


@dataclass(frozen=True)
class TwoCalls:
    """A history whose merge of ``w1/W1-90`` is made over two Bash calls: ``first`` starts it and stops before
    the commit (exiting ``first_exit``), ``second`` commits it."""
    name: str
    first: str
    second: str
    paths: tuple              # the acceptance paths the merge combines or brings: git's own merge of each is kept
    what: str
    first_exit: int = 0
    conflicted: tuple = ()    # the paths git's own merge reports as conflicted


def _merge_back_history(project, sandbox, conflict_on_the_source):
    """A test designer's twenty-line acceptance test on ``main``. Since the fork the merged side changed its
    line 2 and added a new acceptance test (test designer's commits); ``main`` changed its line 19 (a test
    designer's commit). With ``conflict_on_the_source``, engineers changed the source file on both sides, each
    in its own way; without, the merged side has an engineer's ``pyproject.toml``."""
    _the_test_on_main(project, sandbox)
    branch = [edit(MERGED_TEST, 2, "the-merged-side", AS_DESIGNER),
              write_and_commit(NEW_TEST, new_test_text(), AS_DESIGNER, "a new acceptance test on the merged side")]
    main = [edit(MERGED_TEST, 19, "main", AS_DESIGNER)]
    if conflict_on_the_source:
        branch.append(f"echo \"VALUE = 'the merged side'\" > {SOURCE} && "
                      + support.commit_paths([SOURCE], AS_ENGINEER, subject="the merged side's engineer"))
        main.append(f"echo \"VALUE = 'main'\" > {SOURCE} && "
                    + support.commit_paths([SOURCE], AS_ENGINEER, subject="main's engineer"))
    else:
        branch.append(support.commit(ALSO, AS_ENGINEER, subject="the merged side's other work"))
    _two_sides(project, sandbox, branch, main)


def two_calls_with_a_conflict_on_the_source(project, sandbox):
    """F1 (a), as in ``03f470a5``: the first call's merge stops on a conflict in the source file; git combines
    the acceptance test both sides changed and brings the new one cleanly. The second call resolves the source
    file by hand, stages it and commits the merge."""
    _merge_back_history(project, sandbox, conflict_on_the_source=True)
    resolve = f"echo \"VALUE = 'both'\" > {SOURCE} && git add -- {SOURCE}"
    return TwoCalls("a-conflict-on-the-source-file-resolved-in-the-second-call", START_THE_MERGE,
                    commit_the_merge(before_the_commit=resolve), (MERGED_TEST, NEW_TEST),
                    first_exit=1, conflicted=(SOURCE,),
                    what=f"a merge-back of {BRANCH} over two calls: `git merge --no-ff --no-commit` stops on a "
                         f"conflict in {SOURCE} (both sides' engineers changed it), while git combines two test "
                         f"designers' edits of {MERGED_TEST} and brings the merged side's new {NEW_TEST}; the "
                         f"second call resolves {SOURCE} by hand and commits the merge")


def two_calls_with_no_conflict(project, sandbox):
    """F1 (b): the same with no conflict at all; the second call is ``git commit`` with the trailers."""
    _merge_back_history(project, sandbox, conflict_on_the_source=False)
    return TwoCalls("no-conflict-and-the-commit-in-the-second-call", START_THE_MERGE, commit_the_merge(),
                    (MERGED_TEST, NEW_TEST),
                    what=f"a merge-back of {BRANCH} over two calls: `git merge --no-ff --no-commit` combines two "
                         f"test designers' edits of {MERGED_TEST} and brings the merged side's new {NEW_TEST} "
                         f"without a conflict; the second call is `git commit` with the trailers")


def renamed(line_2=None):
    """Shell: a test designer's commit that renames MERGED_TEST to RENAMED_TEST (``git mv``); with ``line_2``
    (a word), the same commit changes its line 2."""
    command = f"git mv -- {MERGED_TEST} {RENAMED_TEST}"
    if line_2 is not None:
        command += " && " + set_line(RENAMED_TEST, 2, line_2) + f" && git add -- {RENAMED_TEST}"
    return command + " && git commit -q -m 'the test renamed'" + support._trailer_options(AS_DESIGNER)


def _rename_on_the_merged_side_history(project, sandbox):
    """F4: a test designer's twenty-line acceptance test on ``main``. Since the fork the merged side renamed it
    (``git mv``, a test designer's commit) and got an engineer's ``pyproject.toml``; ``main`` changed its line 2
    (a test designer's commit). Git's own merge is clean: the edit at the new name, the old path gone."""
    _the_test_on_main(project, sandbox)
    _two_sides(project, sandbox,
               (renamed(),
                support.commit(ALSO, AS_ENGINEER, subject="the merged side's other work")),
               (edit(MERGED_TEST, 2, "main", AS_DESIGNER),))


RENAMED_ON_THE_MERGED_SIDE = (f"an ordinary --no-ff merge of {BRANCH} with orchestrator trailers; a test designer "
                              f"renamed {MERGED_TEST} to {RENAMED_TEST} on the merged side and changed line 2 of "
                              f"{MERGED_TEST} on main, and git's own merge is clean: the edit at the new name, the "
                              f"old path gone")


def clean_merge_across_a_rename(project, sandbox):
    """F4 in one call: the merge commit holds git's own merge exactly."""
    _rename_on_the_merged_side_history(project, sandbox)
    return Moved("git-s-own-merge-across-a-rename", merge_commit(), (MERGED_TEST, RENAMED_TEST), git_s_own=True,
                 what=RENAMED_ON_THE_MERGED_SIDE)


def two_calls_across_a_rename(project, sandbox):
    """F4 over two calls (the form of F1 (b)): ``git merge --no-ff --no-commit``, then ``git commit``."""
    _rename_on_the_merged_side_history(project, sandbox)
    return TwoCalls("git-s-own-merge-across-a-rename-over-two-calls", START_THE_MERGE, commit_the_merge(),
                    (MERGED_TEST, RENAMED_TEST), what=RENAMED_ON_THE_MERGED_SIDE + ", made over two calls")


TWO_CALLS = {
    "a-conflict-on-the-source-file-resolved-in-the-second-call": two_calls_with_a_conflict_on_the_source,
    "no-conflict-and-the-commit-in-the-second-call": two_calls_with_no_conflict,
}


def history_of_two_calls_with_no_conflict(project, sandbox):
    """The history of F1 (b), for the cases that change something in the flow."""
    _merge_back_history(project, sandbox, conflict_on_the_source=False)


def by_hand(path=MERGED_TEST):
    """Shell: line 10 of ``path`` changed by hand in the working tree; nothing is staged."""
    return set_line(path, 10, "by-hand")


@dataclass(frozen=True)
class HandWrite:
    """Where the hand write of ``MERGED_TEST`` falls in a merge made over several calls: ``calls`` in order, the
    last one commits the merge; the check of call ``caught_in`` (0 the first) sees the hand write."""
    calls: tuple
    caught_in: int
    words: str


# The merge of F1 (b) with one more line of MERGED_TEST changed by hand: content that differs from git's own merge
# of HEAD and w1/W1-90. A call that commits stages the acceptance tests as the tree holds them.
HAND_WRITES = {
    "in-the-first-call-after-the-merge": HandWrite(
        (f"{START_THE_MERGE} && {by_hand()}", commit_the_merge(before_the_commit=STAGE_THE_TESTS)), 0,
        "the first call starts the merge and then changes line 10 by hand; the second commits the merge"),
    "in-a-call-of-its-own-between": HandWrite(
        (START_THE_MERGE, by_hand(), commit_the_merge(before_the_commit=STAGE_THE_TESTS)), 1,
        "the first call starts the merge, a second changes line 10 by hand, a third commits the merge"),
    "in-the-commit-s-call-before-the-commit": HandWrite(
        (START_THE_MERGE, commit_the_merge(before_the_commit=f"{by_hand()} && {STAGE_THE_TESTS}")), 1,
        "the first call starts the merge; the second changes line 10 by hand and commits the merge"),
}


def history_of_a_conflict_in_the_test(project, sandbox):
    """Both sides' test designers changed line 2 of the acceptance test, each in its own way; the merged side
    also got an engineer's ``pyproject.toml``. Git reports the conflict on the test."""
    _the_test_on_main(project, sandbox)
    _two_sides(project, sandbox,
               (edit(MERGED_TEST, 2, "the-merged-side", AS_DESIGNER),
                support.commit(ALSO, AS_ENGINEER, subject="the merged side's other work")),
               (edit(MERGED_TEST, 2, "main", AS_DESIGNER),))


def resolution_of_the_conflicted_test(project, name):
    """Shell for the second call: ``MERGED_TEST`` written as ``name`` says, whatever the index holds for it."""
    if name == "the-first-parent-s-version-whole":
        return f"git show HEAD:{MERGED_TEST} > {MERGED_TEST}"
    if name == "the-merged-side-s-version-whole":
        return f"git show {shlex.quote(BRANCH)}:{MERGED_TEST} > {MERGED_TEST}"
    assert name == "held-as-git-writes-it-with-its-markers", name
    own = git_s_own_merge(project, full_id(project, "HEAD"), full_id(project, BRANCH))
    blob = content_at(project, own.tree, MERGED_TEST).split()[2]
    return f"git cat-file blob {blob} > {MERGED_TEST}"


RESOLUTIONS_OVER_TWO_CALLS = ("the-first-parent-s-version-whole", "the-merged-side-s-version-whole",
                              "held-as-git-writes-it-with-its-markers")


def merge_back_over_two_calls(project, sandbox, judge, shape):
    """Run ``shape``'s two calls in the orchestrator's session and return what DEC-918 item 1 finds wrong: each
    call's check must stay silent and move nothing; the merge commit must hold git's own merge of every path of
    ``shape.paths``, with the tree and the index equal to it; ``judge_commits`` must return no finding for it.

    Returns (problems, a message that shows both calls' agent-facing text and finding records)."""
    before, side = full_id(project, "HEAD"), full_id(project, BRANCH)
    own = git_s_own_merge(project, before, side)
    assert own.conflicted == shape.conflicted, (
        f"the fixture is wrong: {shape.what}: git's own merge reports the conflicts {own.conflicted}"
    )
    assert any(content_at(project, own.tree, path) for path in shape.paths), (
        f"the fixture is wrong: {shape.what}: git's own merge holds none of {shape.paths}"
    )
    first = bash_call(project, sandbox, shape.first, ORCHESTRATOR, TICKET)
    assert (first.exit_code, first.merging, first.unmerged, first.left[0][0]) == (
        shape.first_exit, side, shape.conflicted, (before, "main")), (
        f"the fixture is wrong: {shape.what}: the first call exits {first.exit_code}, leaves MERGE_HEAD "
        f"{first.merging}, the unmerged paths {first.unmerged} and HEAD {first.left[0][0]}"
    )
    second = bash_call(project, sandbox, shape.second, ORCHESTRATOR, TICKET)
    assert second.exit_code == 0, f"the fixture is wrong: {shape.what}: the second call failed: {second.told('')}"
    merge_id = full_id(project, "HEAD")
    assert parents_of(project, merge_id) == [before, side] and trailer_values(project, merge_id, "Role") == [
        ORCHESTRATOR] and trailer_values(project, merge_id, "Task") == [TICKET], (
        f"the fixture is wrong: {shape.what}: the second call did not commit the merge with the trailers"
    )
    problems = []
    for label, seen in (("the first call", first), ("the second call", second)):
        result = seen.result
        if result.outcome != "silent" or result.returncode != 0 or result.new_lines:
            problems.append(f"{label}'s check did not stay silent ({result.describe()})")
        if not seen.kept():
            problems.append(f"{label}'s check changed the tree or the index ({seen.change()})")
    for path in shape.paths:
        held, git_s = content_at(project, merge_id, path), content_at(project, own.tree, path)
        if held != git_s:
            problems.append(f"the merge commit holds {held} for {path}, git's own merge {git_s}")
    status = check_support.porcelain_all(project)
    if status:
        problems.append(f"the tree or the index differs from the merge commit:\n{status}")
    findings = judge(project, [merge_id])
    if findings:
        problems.append(f"judge_commits on the merge commit returns "
                        f"{[(f.commit[:12], f.paths, f.reason) for f in findings]}")
    return problems, f"{first.told('The first call')}. {second.told('The second call')}"


# --------------------------------------------------------------------------
# A drop hidden behind a rename or a file replaced by a directory; git's clean merge across a rename
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Moved:
    """A history that ends with a merge commit, made on ``main`` by ``command`` in one call, around an
    acceptance test that one side renamed or replaced by a directory."""
    name: str
    command: str
    paths: tuple              # the acceptance paths of the test: its names before and after, the directory's file
    what: str
    git_s_own: bool           # the merge commit holds exactly git's own merge of the folder, with no conflict there
    conflicted: tuple = ()    # the paths git's own merge reports as conflicted; a moved-aside name is MERGED_TEST~
    keeps: str | None = None  # BRANCH or "main": the side whose version of the folder the merge commit holds whole


def is_the_test_s(path, paths):
    """True when ``path`` is one of the test's ``paths`` or a moved-aside name of one (``<path>~<commit>``)."""
    return path in paths or any(path.startswith(name + "~") for name in paths)


def _renamed_on_main_history(project, sandbox, main_also_changes_line_2):
    """F2: a test designer's twenty-line acceptance test on ``main``. Since the fork the merged side changed its
    line 2 (a test designer's commit) and got an engineer's ``pyproject.toml``; on ``main`` a test designer's
    commit renamed it (``git mv``), changing its line 2 too when ``main_also_changes_line_2``."""
    _the_test_on_main(project, sandbox)
    _two_sides(project, sandbox,
               (edit(MERGED_TEST, 2, "the-merged-side", AS_DESIGNER),
                support.commit(ALSO, AS_ENGINEER, subject="the merged side's other work")),
               (renamed("main" if main_also_changes_line_2 else None),))


def drop_behind_a_clean_rename(project, sandbox):
    """F2 (a): git's own merge is clean, with the merged side's edit at the new name; the merge commit holds the
    first parent's renamed file whole instead."""
    _renamed_on_main_history(project, sandbox, main_also_changes_line_2=False)
    drop = f"git checkout -q HEAD -- {RENAMED_TEST}"
    return Moved("a-clean-rename-the-first-parent-s-renamed-file-whole", merge_commit(before_the_commit=drop),
                 (MERGED_TEST, RENAMED_TEST), git_s_own=False, keeps="main",
                 what=f"a --no-ff merge of {BRANCH} with orchestrator trailers; a test designer renamed "
                      f"{MERGED_TEST} to {RENAMED_TEST} on main and changed its line 2 on the merged side; git's own "
                      f"merge is clean, with the edit at the new name, and the merge commit holds main's renamed "
                      f"file whole: the merged side's edit dropped")


def drop_behind_a_conflicted_rename(project, sandbox):
    """F2 (b): ``main`` changed the same line in its rename, so git reports the conflict at the new name; the
    merge commit resolves it by taking the first parent's version."""
    _renamed_on_main_history(project, sandbox, main_also_changes_line_2=True)
    resolve = f"git checkout --ours -- {RENAMED_TEST} && git add -- {RENAMED_TEST}"
    return Moved("a-conflict-at-the-new-name-the-first-parent-s-version-whole",
                 merge_commit(before_the_commit=resolve, conflicted=RENAMED_TEST), (MERGED_TEST, RENAMED_TEST),
                 git_s_own=False, conflicted=(RENAMED_TEST,), keeps="main",
                 what=f"a --no-ff merge of {BRANCH} with orchestrator trailers; a test designer renamed "
                      f"{MERGED_TEST} to {RENAMED_TEST} on main, changing its line 2, and changed its line 2 on the "
                      f"merged side; git reports the conflict at the new name and the merge commit takes main's "
                      f"version whole")


def _replaced_by_a_directory(path=MERGED_TEST, inner=INNER_TEST):
    """Shell: delete the file ``path`` and put a directory of that name holding ``inner`` (a test designer's
    commit)."""
    return (f"git rm -q -- {path} && mkdir -p {path} && printf %s {shlex.quote(new_test_text())} > {inner} && "
            + support.commit_paths([inner], AS_DESIGNER, subject="the test replaced by a directory"))


# Shell: drop the one conflicted path, which must be the moved-aside copy of MERGED_TEST, and keep the directory.
DROP_THE_MOVED_ASIDE_COPY = (
    "moved=\"$(git diff --name-only --diff-filter=U)\" && "
    f"case \"$moved\" in {MERGED_TEST}~?*) ;; *) exit 1 ;; esac && git rm -q -- \"$moved\""
)
REPLACED_MERGE = ("( git merge -q --no-ff --no-commit " + shlex.quote(BRANCH) + " > /dev/null 2>&1 || true ) && "
                  + DROP_THE_MOVED_ASIDE_COPY + " && git commit -q -m " + shlex.quote("Merge " + BRANCH)
                  + support._trailer_options(AS_ORCHESTRATOR))


def directory_on_main(project, sandbox):
    """F3, the merged side's edit dropped: ``main`` deleted the acceptance test and put a directory of the same
    name holding one file; the merged side changed one of its lines. The merge commit keeps the directory and
    drops the moved-aside edited copy."""
    _the_test_on_main(project, sandbox)
    _two_sides(project, sandbox,
               (edit(MERGED_TEST, 2, "the-merged-side", AS_DESIGNER),
                support.commit(ALSO, AS_ENGINEER, subject="the merged side's other work")),
               (_replaced_by_a_directory(),))
    return Moved("a-directory-on-main-the-merged-side-s-edit-dropped", REPLACED_MERGE, (MERGED_TEST, INNER_TEST),
                 git_s_own=False, conflicted=(MERGED_TEST + "~",), keeps="main",
                 what=f"a --no-ff merge of {BRANCH} with orchestrator trailers; a test designer replaced "
                      f"{MERGED_TEST} by a directory holding {INNER_TEST} on main and changed its line 2 on the "
                      f"merged side; git reports the conflict under the moved-aside name only, and the merge "
                      f"commit keeps the directory and drops the merged side's edited copy")


def directory_on_the_merged_side(project, sandbox):
    """F3, the first parent's edit dropped: the merged side deleted the acceptance test and put a directory of
    the same name holding one file; ``main`` changed one of its lines. The merge commit keeps the directory and
    drops the moved-aside edited copy."""
    _the_test_on_main(project, sandbox)
    _two_sides(project, sandbox,
               (_replaced_by_a_directory(),
                support.commit(ALSO, AS_ENGINEER, subject="the merged side's other work")),
               (edit(MERGED_TEST, 2, "main", AS_DESIGNER),))
    return Moved("a-directory-on-the-merged-side-the-first-parent-s-edit-dropped", REPLACED_MERGE,
                 (MERGED_TEST, INNER_TEST), git_s_own=False, conflicted=(MERGED_TEST + "~",), keeps=BRANCH,
                 what=f"a --no-ff merge of {BRANCH} with orchestrator trailers; a test designer replaced "
                      f"{MERGED_TEST} by a directory holding {INNER_TEST} on the merged side and changed its line 2 "
                      f"on main; git reports the conflict under the moved-aside name only, and the merge commit "
                      f"keeps the directory and drops main's edited copy")


DROPPED = {
    "a-clean-rename-the-first-parent-s-renamed-file-whole": drop_behind_a_clean_rename,
    "a-conflict-at-the-new-name-the-first-parent-s-version-whole": drop_behind_a_conflicted_rename,
    "a-directory-on-main-the-merged-side-s-edit-dropped": directory_on_main,
    "a-directory-on-the-merged-side-the-first-parent-s-edit-dropped": directory_on_the_merged_side,
}


def assert_moved_shape(project, shape, before, merge_id):
    """From git's own answers: ``merge_id`` is a merge commit of ``before`` and ``w1/W1-90`` on one merge base;
    git's own merge reports the conflicts ``shape.conflicted`` (a name ending in ``~`` stands for one moved-aside
    name); the merge commit holds git's own merge of the folder exactly or not, as ``shape.git_s_own`` says, and
    the folder as ``shape.keeps`` has it."""
    side = full_id(project, BRANCH)
    parents = parents_of(project, merge_id)
    assert parents == [before, side] and len(merge_bases(project, before, side)) == 1, (
        f"the fixture is wrong: {shape.what}: the merge commit has the parents {parents}"
    )
    merged = git_s_own_merge(project, before, side)
    expected = shape.conflicted
    found = merged.conflicted
    assert len(found) == len(expected) and all(
        name == want or (want.endswith("~") and name.startswith(want) and len(name) > len(want))
        for name, want in zip(found, expected)), (
        f"the fixture is wrong: {shape.what}: git's own merge reports the conflicts {found}"
    )
    holds = folder_listing(project, merge_id) == folder_listing(project, merged.tree) and not any(
        name.startswith(FOLDER) for name in found)
    assert holds == shape.git_s_own, (
        f"the fixture is wrong: {shape.what}: the merge commit {'does not hold' if shape.git_s_own else 'holds'} "
        f"git's own merge of {FOLDER}:\n{folder_listing(project, merge_id)}against\n"
        f"{folder_listing(project, merged.tree)}"
    )
    if shape.keeps is not None:
        kept = before if shape.keeps == "main" else side
        assert folder_listing(project, merge_id) == folder_listing(project, kept), (
            f"the fixture is wrong: {shape.what}: the merge commit does not hold {shape.keeps}'s {FOLDER} whole"
        )


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
