"""Support code for the tenth batch of the W1-50 acceptance tests: DEC-410.

DEC-410 (delegated, stricter-only) decides the packages DP-21 to DP-28. Four of its points change behaviour:

- **DP-21.** A change to a file under ``.tickets/**`` that a merge commit itself makes (its own change, by the
  helper) is a finding whatever the merge commit's trailers, also with the orchestrator's trailers or none.
- **DP-27.** The same for ``tests/acceptance/**``: a merge commit's own change there is a finding whatever its
  trailers, a test designer's included.
- **DP-24** (with DP-26). Under ``tests/acceptance/**``, a path that more than one parent changed against the
  merge base is the merge commit's own, whichever side's content it holds.
- **DP-22.** ``brought`` is the complement of ``own`` over every parent: each path where the merge commit
  differs from some parent and that is not its own.

This module builds the histories of that batch. Every history is a real one, made in the throw-away project
with commits, ``git merge`` and, where a shape needs it, ``git commit-tree`` (through the builders of
``w1_50_symmetric_support.py``). The guards here read git, never the check or the helper: they show that the
history a test built is the one its literal expectation describes.
"""

from __future__ import annotations

import importlib
import os
import shlex
from dataclasses import dataclass

import w1_50_support as support
import w1_50_symmetric_support as symmetric

check_support = support.check_support

AS_DESIGNER = support.AS_DESIGNER
AS_ENGINEER = support.AS_ENGINEER
AS_ORCHESTRATOR = support.AS_ORCHESTRATOR
NO_TRAILERS = support.NO_TRAILERS
ORCHESTRATOR_ON_MAIN = support.ORCHESTRATOR_ON_MAIN

TICKET_BRANCH = support.TICKET_BRANCH

TICKET_FILE = symmetric.NARROWED_FILE                        # .tickets/DAEO-zz94.md: no trailers here name it
LONG_TEST = f"{support.ACCEPTANCE}/{support.WBS}/test_long.py"   # an acceptance test of twenty lines
LONG_TEST_LINES = 20

MODULE = "gov.guard.containment_merge"
SOURCES = check_support.REPO_ROOT / check_support.GOV_PACKAGE_PARENT_REL


# --------------------------------------------------------------------------
# The helper, by its public name (DEC-398)
# --------------------------------------------------------------------------

def helper_module(monkeypatch):
    """A function that returns the module ``gov.guard.containment_merge``, imported from this repository's
    ``src`` when it is first called, in a process that says nothing of a caller. For a fixture of a test file."""
    for name in (check_support.ROLE_ENV, check_support.TICKET_ENV, "CLAUDE_PROJECT_DIR"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", os.devnull)
    monkeypatch.setenv("GIT_CONFIG_SYSTEM", os.devnull)
    monkeypatch.syspath_prepend(str(SOURCES))

    def _module():
        import pytest
        try:
            module = importlib.import_module(MODULE)
        except ImportError as exc:
            pytest.fail(f"the helper that reads a merge (DEC-398) cannot be imported: `import {MODULE}` fails: "
                        f"{exc}", pytrace=False)
        if not callable(getattr(module, "read_merge", None)):
            pytest.fail(f"{MODULE} has no function `read_merge` (DEC-398)", pytrace=False)
        assert str(module.__file__).startswith(str(SOURCES)), (
            f"`{MODULE}` was imported from {module.__file__}, not from this repository's {SOURCES}"
        )
        return module

    return _module


def built(project, sandbox, command):
    """Run ``command`` with no hook around it. Returns the state a reading must leave as it is."""
    support.run(project, sandbox, command)
    return check_support.state(project, support.WATCHED), check_support.finding_lines(project)


def read(project, helper, commit, what):
    """The helper's reading of ``commit``: two sorted lists of distinct paths with no path in both."""
    commit_id = check_support.git(project, "rev-parse", commit).strip()
    reading = helper().read_merge(str(project), commit_id)
    for name in ("own", "brought"):
        paths = getattr(reading, name)
        assert isinstance(paths, list) and paths == sorted(paths) and len(set(paths)) == len(paths), (
            f"read_merge on {what}: `{name}` is no sorted list of distinct paths: {paths!r}"
        )
    both = sorted(set(reading.own) & set(reading.brought))
    assert not both, f"read_merge on {what}: `own` and `brought` both hold {both}"
    return reading


def assert_left(project, state, what):
    left, findings = state
    check_support.assert_left_as_the_call_left_it(project, left, f"read_merge on {what}")
    assert check_support.finding_lines(project) == findings, f"read_merge on {what}: reading added a finding"


def complement(project, own, commit_id="HEAD"):
    """DEC-410, DP-22, from git's own answers: every path where the commit differs from some parent and that
    is not in ``own``, sorted."""
    return sorted(set(symmetric.differing_from_any_parent(project, commit_id)) - set(own))


def assert_brought_is_the_complement(project, reading, what, commit_id="HEAD"):
    """DEC-410, DP-22: ``brought`` is exactly the paths where the merge commit differs from some parent and
    that are not in ``own``."""
    expected = complement(project, reading.own, commit_id)
    assert reading.brought == expected, (
        f"read_merge on {what}: `brought` is {reading.brought!r}, not {expected!r}: every path where the merge "
        f"commit differs from some parent and that is not in `own` {reading.own!r} (DEC-410, DP-22)"
    )


# --------------------------------------------------------------------------
# A merge commit with a change of its own: a hand edit, a conflict resolution
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class OwnChange:
    """A history that ends with a merge commit, made by ``command``, that changed ``path`` itself."""
    command: str
    path: str                 # the path a finding is to name
    brought: tuple            # paths the merged branch brought: no finding names them
    what: str


def hand_edit(project, sandbox, path, trailers):
    """An ordinary ticket branch (a test designer's new test, an engineer's source file); ``main`` moved on. The
    merge commit, with ``trailers``, appends a line to ``path``, which neither side changed since the fork."""
    support.ticket_branch(project, sandbox, (support.NEW_TEST, AS_DESIGNER), (support.SOURCE, AS_ENGINEER))
    return OwnChange(support.merge_with_own_change(path, trailers=trailers), path,
                     brought=(support.NEW_TEST, support.SOURCE),
                     what=f"a --no-ff merge of {TICKET_BRANCH} with trailers {trailers} whose merge commit "
                          f"itself appends a line to {path}")


def conflict_resolved_to_new_content(project, sandbox, path, by, trailers):
    """Both sides appended a line to ``path``, each by a commit with the trailers ``by``. The merge conflicts;
    the merge commit, with ``trailers``, holds the first parent's content with one more line: content neither
    parent holds."""
    support.ticket_branch_of(
        project, sandbox,
        f"echo branch-side >> {shlex.quote(path)} && " + support.commit_paths([path], by, subject="the branch's"),
        main_moves_on=False)
    support.run(project, sandbox,
                f"echo main-side >> {shlex.quote(path)} && " + support.commit_paths([path], by, subject="main's"))
    command = (
        f"( git merge -q --no-ff --no-commit {shlex.quote(TICKET_BRANCH)} > /dev/null 2>&1 || true ) "
        f"&& test -n \"$(git diff --name-only --diff-filter=U)\" "
        f"&& git checkout --ours -- {shlex.quote(path)} && echo resolved-by-the-merge >> {shlex.quote(path)} "
        f"&& git add -- {shlex.quote(path)} && git commit -q -m {shlex.quote('Merge ' + TICKET_BRANCH)}"
        + support._trailer_options(trailers))
    return OwnChange(command, path, brought=(),
                     what=f"a --no-ff merge of {TICKET_BRANCH} with trailers {trailers}; both sides changed "
                          f"{path} (commits with trailers {by}) and the conflict is resolved to content neither "
                          f"parent holds")


def assert_content_no_parent_holds(project, path):
    """Guard against an empty test: ``HEAD`` is a merge commit on one merge base that holds content of ``path``
    none of its parents holds."""
    parents = support.parents_of(project)
    assert len(parents) == 2 and len(support.merge_bases(project, *parents)) == 1, (
        f"the fixture is wrong: HEAD has the parents {parents}, or they do not have one merge base"
    )
    held = support.content_at(project, "HEAD", path)
    for parent in parents:
        assert held is not None and held != support.content_at(project, parent, path), (
            f"the fixture is wrong: the parent {parent[:12]} already holds the merge commit's content of {path}"
        )


# --------------------------------------------------------------------------
# An orchestrator's ticket-file change on one side only, brought by an ordinary merge
# --------------------------------------------------------------------------

def ticket_files_on_one_side(project, sandbox, on_the_branch, trailers):
    """An orchestrator narrows one ticket's allowed paths and closes another ticket, in two commits, on the
    ticket branch or on ``main``; the other side got one commit of another path since the fork. An ordinary
    ``git merge --no-ff`` with ``trailers``: the merge commit holds both sides' changes."""
    tickets = symmetric.TICKETS
    if on_the_branch:
        support.ticket_branch_of(project, sandbox, tickets.work)
        where = f"{TICKET_BRANCH} holds {tickets.what}; main moved on"
    else:
        support.ticket_branch(project, sandbox, (support.SOURCE, AS_ENGINEER), main_moves_on=False)
        symmetric.do_the_work(project, sandbox, tickets)
        where = f"main got {tickets.what} since the fork; {TICKET_BRANCH} brings an engineer's {support.SOURCE}"
    return symmetric.TakingMerge(support.merge(trailers=trailers),
                                 differs=(*tickets.paths, support.BOOTSTRAP if on_the_branch else support.SOURCE),
                                 what=f"an ordinary --no-ff merge of {TICKET_BRANCH} with trailers {trailers}: "
                                      f"{where}")


# --------------------------------------------------------------------------
# DP-24: one path that both sides changed since their one merge base
# --------------------------------------------------------------------------

FIRST = "the-first-parent-s"
SECOND = "the-second-parent-s"


@dataclass(frozen=True)
class BothChanged:
    """A history that ends with a merge commit, made by ``command``, of two sides that both changed ``path``."""
    command: str
    path: str                 # the path both sides changed
    holds: str | None         # FIRST or SECOND: the parent whose content of ``path`` the merge commit holds whole
    also: str                 # a path only the ticket branch changed: brought, whatever the reading of ``path``
    turned_round: bool        # the merge commit's first parent is the ticket branch, its second ``HEAD``
    what: str


def changed_on_both_sides(project, sandbox, path, by, holds, turned_round=False, trailers=AS_ORCHESTRATOR):
    """The ticket branch and ``main`` each appended a line of their own to ``path`` since the fork, each by a
    commit with the trailers ``by``; the branch also got an engineer's commit of ``pyproject.toml``.

    The merge commit, with ``trailers``, holds for ``path`` the content of one parent whole (``holds``), and
    the branch's ``pyproject.toml``.

    Ordinary: ``git merge --no-ff`` of the branch into ``main``, which conflicts in ``path``; the conflict is
    resolved with ``git checkout --ours`` (the first parent's content) or ``--theirs`` (the second parent's).
    Turned round: a merge commit made with ``git commit-tree`` whose first parent is the branch and whose
    second parent is ``HEAD``, with the tree a merge that takes one side's content of ``path`` gives; ``main``
    is moved forward to it.
    """
    also = support.SECOND_SOURCE
    assert path != also and holds in (FIRST, SECOND)
    support.ticket_branch_of(
        project, sandbox,
        f"echo branch-side >> {shlex.quote(path)} && " + support.commit_paths([path], by, subject="the branch's"),
        support.commit(also, AS_ENGINEER, subject="the branch's other work"),
        main_moves_on=False)
    support.run(project, sandbox,
                f"echo main-side >> {shlex.quote(path)} && " + support.commit_paths([path], by, subject="main's"))
    if not turned_round:
        side = "--ours" if holds == FIRST else "--theirs"
        command = (
            f"( git merge -q --no-ff --no-commit {shlex.quote(TICKET_BRANCH)} > /dev/null 2>&1 || true ) "
            f"&& test -n \"$(git diff --name-only --diff-filter=U)\" "
            f"&& git checkout {side} -- {shlex.quote(path)} && git add -- {shlex.quote(path)} "
            f"&& git commit -q -m {shlex.quote('Merge ' + TICKET_BRANCH)}" + support._trailer_options(trailers))
        order = f"an ordinary --no-ff merge of {TICKET_BRANCH} into main"
    else:
        # The prepared merge is made on a branch cut from main: there "ours" is main, the second parent.
        side = "-X theirs" if holds == FIRST else "-X ours"
        symmetric.prepare_tree(project, sandbox,
                               f"git merge -q --no-ff {side} -m merged {shlex.quote(TICKET_BRANCH)}")
        merge_commit = support.commit_object(symmetric.PREPARED + "^{tree}", [TICKET_BRANCH, "HEAD"], trailers)
        command = symmetric._move_to(merge_commit)
        order = f"a merge commit with the parents {TICKET_BRANCH} and HEAD (main) in that order"
    return BothChanged(command, path, holds, also, turned_round,
                       what=f"{order}, with trailers {trailers}; both sides changed {path} since the fork "
                            f"(commits with trailers {by}) and the merge commit holds {holds} content of it whole")


def changed_on_both_sides_in_different_parts(project, sandbox, trailers=AS_ORCHESTRATOR):
    """DP-26. An acceptance test of twenty lines is on ``main`` before the fork (a test designer's commit). A
    test designer's commit changes its second line on the ticket branch, another its nineteenth line on
    ``main``. An ordinary ``git merge --no-ff``: git combines the two edits itself, without a conflict."""
    path = LONG_TEST
    text = "".join(f"LINE_{n} = {n}\n" for n in range(1, LONG_TEST_LINES + 1))
    directory = os.path.dirname(path)
    support.run(project, sandbox,
                f"mkdir -p {shlex.quote(directory)} && printf %s {shlex.quote(text)} > {shlex.quote(path)} && "
                + support.commit_paths([path], AS_DESIGNER, subject="a long acceptance test"))
    support.ticket_branch_of(
        project, sandbox,
        f"sed -i '2s/.*/LINE_2 = \"the branch\"/' {shlex.quote(path)} && "
        + support.commit_paths([path], AS_DESIGNER, subject="the branch's edit"),
        support.commit(support.SECOND_SOURCE, AS_ENGINEER, subject="the branch's other work"),
        main_moves_on=False)
    support.run(project, sandbox,
                f"sed -i '19s/.*/LINE_19 = \"main\"/' {shlex.quote(path)} && "
                + support.commit_paths([path], AS_DESIGNER, subject="main's edit"))
    return BothChanged(support.merge(trailers=trailers), path, None, support.SECOND_SOURCE, False,
                       what=f"an ordinary --no-ff merge of {TICKET_BRANCH} with trailers {trailers}; a test "
                            f"designer changed line 2 of {path} on the branch and line 19 on main, and git "
                            f"combined the two edits without a conflict")


def assert_both_changed(project, shape, before, branch):
    """Guard against an empty test, from git's own answers.

    ``HEAD`` is a merge commit of ``before`` (``main`` as the call found it) and ``branch`` in the order the
    shape names; the two have one merge base; each holds for ``shape.path`` content other than the merge
    base's and other than the other's; the merge commit holds the content of the parent ``shape.holds`` names
    (with ``None``: content neither parent holds); and it holds the branch's content of ``shape.also``, which
    ``main`` did not change.
    """
    expected = [branch, before] if shape.turned_round else [before, branch]
    parents = support.parents_of(project)
    assert parents == expected, f"the fixture is wrong: the merge commit's parents are {parents}, not {expected}"
    bases = support.merge_bases(project, *parents)
    assert len(bases) == 1, f"the fixture is wrong: the parents have the merge bases {bases}"
    at_base, at_first, at_second, held = (support.content_at(project, revision, shape.path)
                                          for revision in (bases[0], parents[0], parents[1], "HEAD"))
    assert len({at_base, at_first, at_second}) == 3 and None not in (at_first, at_second), (
        f"the fixture is wrong: not both parents changed {shape.path} against the merge base, each in its own way"
    )
    wanted = {FIRST: at_first, SECOND: at_second}.get(shape.holds)
    if wanted is None:
        assert held not in (at_base, at_first, at_second), (
            f"the fixture is wrong: the merge commit holds for {shape.path} content a parent or the base holds"
        )
    else:
        assert held == wanted, (
            f"the fixture is wrong: the merge commit does not hold {shape.holds} content of {shape.path}"
        )
    assert support.content_at(project, "HEAD", shape.also) == support.content_at(
        project, branch, shape.also) != support.content_at(project, before, shape.also), (
        f"the fixture is wrong: the merge commit does not hold the branch's change of {shape.also}"
    )
    differs = symmetric.differing_from_any_parent(project)
    assert differs == sorted([shape.path, shape.also]), (
        f"the fixture is wrong: the merge commit differs from its parents in {differs}"
    )


def each_side_changed_another_acceptance_test(project, sandbox, trailers=AS_ORCHESTRATOR):
    """A test designer added a new acceptance test on the ticket branch; another test designer's commit changed
    an existing one on ``main`` since the fork. An ordinary ``git merge --no-ff`` holds both."""
    support.ticket_branch(project, sandbox, (support.NEW_TEST, AS_DESIGNER), main_moves_on=False)
    support.run(project, sandbox, support.commit(support.ACCEPTANCE_FILE, AS_DESIGNER, subject="main's own test"))
    return symmetric.TakingMerge(support.merge(trailers=trailers), (support.NEW_TEST, support.ACCEPTANCE_FILE),
                                 what=f"an ordinary --no-ff merge of {TICKET_BRANCH} (a test designer's "
                                      f"{support.NEW_TEST}) into main, which got a test designer's change of "
                                      f"{support.ACCEPTANCE_FILE} since the fork")


# --------------------------------------------------------------------------
# DP-22: a criss-cross merge in the ordinary order, after the first parent got a commit of its own
# --------------------------------------------------------------------------

def criss_cross_after_main_moved_on(project, sandbox):
    """``main`` and ``crossing`` cross (two merge bases); ``crossing`` then gets an engineer's commit of a
    source file and ``main`` an orchestrator's commit of ``governance/project/bootstrap.md``. An ordinary
    ``git merge --no-ff`` of ``crossing`` into ``main``: the merge commit holds both."""
    shape = support.criss_cross_merge(project, sandbox, (support.SOURCE, AS_ENGINEER), AS_ORCHESTRATOR)
    support.run(project, sandbox, support.commit(support.BOOTSTRAP, ORCHESTRATOR_ON_MAIN,
                                                 subject="main after the crossing"))
    return symmetric.ReadMerge(shape.command,
                               what=f"an ordinary --no-ff merge of {support.CROSSING} into main (two merge "
                                    f"bases); since the crossing {support.CROSSING} got an engineer's "
                                    f"{support.SOURCE} and main an orchestrator's {support.BOOTSTRAP}")
