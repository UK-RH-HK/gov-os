"""Support code and fixtures for the W2-72 acceptance tests (the standard library and pytest).

W2-72 carries out DEC-918 (a1): containment's merge rule matches DEC-912. Under ``tests/acceptance/``, a path
both parents of a merge commit changed against their merge base is not the merge commit's own change when the
merge commit holds exactly git's own merge of that file: the blob ``git merge-tree --write-tree <first parent>
<other parent>`` writes for it, with no conflict on that file. Any file that differs from git's own merge is
still caught as before (DEC-410).

The tests drive the public interface the W1-50 suite drives: ``gov.containment.commits.judge_commits`` (DEC-453), the
close's read-only containment gate. (The post-command check, through the kernel's hooks, is retired with them,
EMERGENCY-2 6.1, DAEO-gr7t: the cases that ran it are deleted.)

``gov.containment.merge.read_merge``, through which the approval check reads merges, is read to show that
its answer is unchanged (DEC-918 item 4).

**The merges.** As a ticket lead merges ``w2/integrate`` back into its ticket's branch: the checked-out branch
(``main`` in the fixture project, the first parent) moves forward to a merge commit of the merged side
(the planted ``BRANCH``, the second parent; ``w2/integrate`` in a merge-back), made in an orchestrator session's own call
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
    """The merged side gets the commands ``branch_steps`` on ``BRANCH`` cut from ``main``; ``main`` then gets
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


def by_hand(path=MERGED_TEST):
    """Shell: line 10 of ``path`` changed by hand in the working tree; nothing is staged."""
    return set_line(path, 10, "by-hand")


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
    """From git's own answers: ``merge_id`` is a merge commit of ``before`` and ``BRANCH`` on one merge base;
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
# A merge-tree run that cannot run: the folder containment takes git from (DEC-802 P-B1-2)
# --------------------------------------------------------------------------
#
# Rewrite-Reason: DEC-802 (P-B1-2): containment takes git by absolute path from the system's own folders, the
# module-level tuple ``gov.util.gitenv.GIT_DIRS`` read at each call, never by name from the inherited ``PATH``.
# A ``git`` first on ``PATH`` (the seam these cases had, ``failing_merge_tree``) is no longer started, so it is
# gone. The process that runs the check now names, in ``GIT_DIRS``, a folder holding a ``git`` of the case's own:
#
# - ``a-fatal-error``: a recording git that passes every call to the real git by its absolute path. The failure is
#   the real git's: the merge base's blob of the test is taken out of the object store, so ``git merge-tree
#   --write-tree`` answers ``fatal: unable to read blob object <id>`` and 128 (measured, git 2.43.0);
# - ``a-git-without-write-tree``: a stand-in that answers ``merge-tree --write-tree`` with 129 and a usage line,
#   as a git older than 2.38 answers, and passes every other call to the real git by its absolute path.
#
# Either way the ``git`` logs each ``merge-tree`` call it answered, with the exit code and git's ``fatal:`` (or
# ``error:``) line on stderr, past any ``hint:`` (or the stand-in's usage line), so a case shows that its check met
# the failing merge-tree and nothing else.

# name: the exit code the check's ``git merge-tree --write-tree`` gets
CANNOT_RUN = {
    "a-fatal-error": 128,              # the real git: the merge base's blob of the test is missing
    "a-git-without-write-tree": 129,   # the stand-in: a git older than 2.38
}
NOTHING_FAILING = "nothing-failing"    # the control: the recording git, every object there
ANSWERS = {**CANNOT_RUN, NOTHING_FAILING: 0}
USAGE = "usage: git merge-tree <base-tree> <branch1> <branch2>"
GIT_DIRS_ENV = "W2_72_GIT_DIRS"        # read by the hook process's ``sitecustomize`` (``GitSeam.hook_environment``)

# Put first on the PostToolUse hook's PYTHONPATH (as W1-03's ``clock`` puts its own): before the hook runs, the
# helper's folder list names the case's folder alone; a line in ``installed.log`` says so, or why it could not.
_SITECUSTOMIZE = '''"""W2-72: containment in this process takes git from the folder W2_72_GIT_DIRS names (DEC-802 P-B1-2)."""
import os as _os

_FOLDERS = _os.environ.get("W2_72_GIT_DIRS")
if _FOLDERS:
    _LOG = _os.path.join(_FOLDERS.split(_os.pathsep)[0], "installed.log")
    try:
        import gov.util.gitenv as _gitenv
        _gitenv.GIT_DIRS = tuple(_FOLDERS.split(_os.pathsep))
        _LINE = "GIT_DIRS=%r in process %d, gov.util.gitenv from %s" % (
            _gitenv.GIT_DIRS, _os.getpid(), _gitenv.__file__)
    except Exception as _error:   # the case reports it: the log of answered calls stays empty
        _LINE = "not set in process %d: %r" % (_os.getpid(), _error)
    with open(_LOG, "a", encoding="utf-8") as _out:
        _out.write(_LINE + "\\n")
'''


def _real_git():
    """The real git, by its absolute path (the one this test process runs)."""
    real = shutil.which("git")
    assert real and os.path.isabs(real), "no real git on PATH"
    return real


@dataclass(frozen=True)
class Answered:
    """One ``merge-tree`` call the case's ``git`` answered."""
    exit_code: int
    stderr: str     # the first ``fatal:`` or ``error:`` line on stderr (else its first line, in brackets)
    words: str      # the call's words


@dataclass(frozen=True)
class GitSeam:
    """A folder holding the ``git`` the process that runs the check takes (``gov.util.gitenv.GIT_DIRS``)."""
    directory: Path
    log: Path       # one line per ``merge-tree`` call answered: exit code, its stderr line (``Answered``), words
    exit_code: int  # what the case's ``git merge-tree --write-tree`` answers

    def answered(self):
        """The ``merge-tree`` calls answered so far."""
        if not self.log.is_file():
            return []
        out = []
        for line in self.log.read_text(encoding="utf-8").splitlines():
            code, stderr, words = line.split("\t", 2)
            out.append(Answered(int(code), stderr, words))
        return out

    def installed(self):
        """What the hook process's ``sitecustomize`` wrote: the folder list it set, or why it could not."""
        path = self.directory / "installed.log"
        return path.read_text(encoding="utf-8").strip() if path.is_file() else "(no line: sitecustomize never ran)"

    def hook_environment(self):
        """The PostToolUse hook's ``PYTHONPATH`` and the variable its ``sitecustomize`` reads: the hook's
        containment takes git from this folder alone."""
        site = self.directory.parent / f"{self.directory.name}-site"
        site.mkdir(exist_ok=True)
        (site / "sitecustomize.py").write_text(_SITECUSTOMIZE, encoding="utf-8")
        return {"PYTHONPATH": os.pathsep.join([str(site), str(SOURCES)]), GIT_DIRS_ENV: str(self.directory)}


def git_seam(directory, case):
    """Write the case's ``git`` into ``directory`` (a new, empty folder) and return it. ``a-fatal-error`` and
    ``nothing-failing``: a recording git that passes every call to the real git; ``a-git-without-write-tree``: a
    stand-in that answers ``merge-tree --write-tree`` with 129 and a usage line and passes every other call to the
    real git."""
    exit_code = ANSWERS[case]
    real, cat = _real_git(), shutil.which("cat")
    assert cat and os.path.isabs(cat), "no cat on PATH"
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    log = directory / "answered-merge-tree-calls.log"
    q = shlex.quote
    if exit_code == 129:
        answer = (
            "    case \" $* \" in *\" --write-tree \"*)\n"
            f"      printf '129\\t%s\\t%s\\n' {q(USAGE)} \"$*\" >> {q(str(log))}\n"
            f"      echo {q(USAGE)} >&2\n"
            "      exit 129 ;;\n"
            "    esac\n")
    else:
        answer = (
            f"    out={q(str(directory))}/out.$$ err={q(str(directory))}/err.$$\n"
            f"    {q(real)} \"$@\" > \"$out\" 2> \"$err\"\n"
            "    code=$?\n"
            "    first=''\n"
            "    while IFS= read -r line; do\n"   # git's own `fatal:` or `error:` line, past any `hint:`
            "      case \"$line\" in fatal:*|error:*) first=$line; break ;; esac\n"
            "      [ -n \"$first\" ] || first=\"($line)\"\n"
            "    done < \"$err\"\n"
            f"    printf '%s\\t%s\\t%s\\n' \"$code\" \"$first\" \"$*\" >> {q(str(log))}\n"
            f"    {q(cat)} \"$out\"\n"
            f"    {q(cat)} \"$err\" >&2\n"
            "    exit \"$code\"\n")
    script = directory / "git"
    script.write_text(
        "#!/bin/sh\n"
        "for word in \"$@\"; do\n"
        "  if [ \"$word\" = merge-tree ]; then\n"
        + answer +
        "  fi\n"
        "done\n"
        f"exec {q(real)} \"$@\"\n", encoding="utf-8")
    script.chmod(0o755)
    return GitSeam(directory, log, exit_code)


def remove_the_merge_base_s_blob(root, merge_id, path):
    """Take the blob of ``path`` at the merge base of ``merge_id``'s two parents out of the object store, so that
    the real ``git merge-tree --write-tree`` of the two parents fails (``fatal:``, 128). The blob is held by no
    tree of the merge commit or of its parents, so no other git call of the check needs it. Returns its id."""
    parents = parents_of(root, merge_id)
    bases = merge_bases(root, *parents)
    assert len(parents) == 2 and len(bases) == 1, (
        f"the fixture is wrong: the merge commit has the parents {parents} and the merge bases {bases}"
    )
    held = content_at(root, bases[0], path)
    assert held is not None, f"the fixture is wrong: the merge base holds no {path}"
    blob = held.split()[2]
    for commit_id in (merge_id, *parents):
        listing = git_run(root, "ls-tree", "-r", commit_id)
        assert listing.returncode == 0 and blob not in listing.stdout, (
            f"the fixture is wrong: {commit_id[:12]}'s tree holds the merge base's blob {blob[:12]} of {path}"
        )
    loose = Path(root) / ".git" / "objects" / blob[:2] / blob[2:]
    assert loose.is_file(), f"the fixture is wrong: the blob {blob[:12]} is not a loose object at {loose}"
    loose.unlink()
    assert git_run(root, "cat-file", "-e", blob).returncode != 0, f"the blob {blob[:12]} is still readable"
    merged = git_run(root, *MERGE_TREE, *parents)
    assert merged.returncode == 128 and "fatal:" in merged.stderr and blob in merged.stderr, (
        f"the fixture is wrong: with the blob {blob[:12]} gone, the real `git merge-tree --write-tree` answers "
        f"{merged.returncode}: {merged.stderr.strip()!r}"
    )
    return blob


def judge_in_a_process(root, commit_ids, environment=None, git_dirs=None):
    """``judge_commits(root, commit_ids)`` in a new Python process of this repository's ``src`` with
    ``environment`` over a caller-free environment. With ``git_dirs`` (folders), that process first sets
    ``gov.util.gitenv.GIT_DIRS`` to them, so containment takes git from there (DEC-802 P-B1-2). Returns
    [(commit, sorted paths, reason)]."""
    seam = (
        "import gov.util.gitenv as gitenv\n"
        f"assert gitenv.__file__.startswith({str(SOURCES)!r}), gitenv.__file__\n"
        f"gitenv.GIT_DIRS = {tuple(str(folder) for folder in git_dirs)!r}\n"
    ) if git_dirs else ""
    program = (
        "import json, sys\n"
        + seam +
        "from gov.containment.commits import judge_commits\n"
        "import gov.containment.commits as module\n"
        f"assert module.__file__.startswith({str(SOURCES)!r}), module.__file__\n"
        "findings = judge_commits(sys.argv[1], sys.argv[2:])\n"
        "print(json.dumps([[f.commit, sorted(f.paths), f.reason] for f in findings]))\n"
    )
    env = {key: value for key, value in os.environ.items()
           if key not in (check_support.ROLE_ENV, check_support.TICKET_ENV, "CLAUDE_PROJECT_DIR")}
    env.update({"PYTHONPATH": str(SOURCES), "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull,
                "PYTHONDONTWRITEBYTECODE": "1"})
    env.update(environment or {})
    proc = subprocess.run([sys.executable, "-c", program, str(root), *commit_ids], capture_output=True, text=True,
                          env=env, timeout=120, check=False)
    return proc


# --------------------------------------------------------------------------
# Findings of the check, by the commit they are for
# --------------------------------------------------------------------------


# --------------------------------------------------------------------------
# Fixtures: each test module imports those it uses by name
# --------------------------------------------------------------------------


@pytest.fixture()
def sandbox(tmp_path):
    """``HOME``, the system temporary directory and an unrelated directory, all outside the project."""
    return check_support.make_sandbox(tmp_path / "sandbox")


@pytest.fixture()
def project(tmp_path):
    """A committed project on ``main`` with a clean working tree and the fixture tickets, all in progress."""
    return check_support.make_project(tmp_path / "project")


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
    """``judge(root, commit_ids)`` -> the findings of ``gov.containment.commits.judge_commits`` (DEC-453),
    imported from this worktree's ``src`` in a process that says nothing of a caller."""
    _caller_free(monkeypatch)

    def _judge(root, commit_ids):
        return _imported("gov.containment.commits", "judge_commits")(str(root), list(commit_ids))

    return _judge


@pytest.fixture()
def read_merge(monkeypatch):
    """``read_merge(root, commit_id)`` -> ``gov.containment.merge.read_merge`` (DEC-398), the reader the
    approval check reads merges through, imported from this worktree's ``src``."""
    _caller_free(monkeypatch)

    def _read(root, commit_id):
        return _imported("gov.containment.merge", "read_merge")(str(root), commit_id)

    return _read
