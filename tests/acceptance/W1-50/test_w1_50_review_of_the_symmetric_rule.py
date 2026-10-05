"""W1-50 — a merge commit with very many parents is judged, and a ``commit`` argument that names something
other than that commit is refused.

Added after implementation; reason: review finding, DEC-403.

A review of the DEC-403 rule found two behaviours the suite did not hold. They came to the test designer as
described behaviours, never as code.

**1. A merge commit with very many parents is judged, never passed over in silence.** DEC-403: a merge that
keeps one parent's content and drops what another parent changed is judged. In an orchestrator session's own
call, a merge commit with 150 parents (``HEAD`` and 149 side commits made with ``git commit-tree``) holds the
tree from before a test designer's change under ``tests/acceptance/**``, and the branch is moved to it. As
reviewed, the post-command hook does not end within the harness's time limit for that move, it is stopped, no
finding is recorded, and the test stays undone: the check fails open.

- *Through the check.* The hook ends by itself within the harness's limit, as the suite's support applies it
  (``HOOK_TIMEOUT_S`` of the W1-03 support module; it is not raised here), and this call adds a finding. Either
  form of finding is accepted: one that names the undone test's path, or one for the move as a whole, as the
  check records a move it cannot read. Nothing else in the move could be a finding: the 149 side commits carry
  the orchestrator's trailers and change nothing.
- *Through the helper.* ``read_merge`` answers for that merge commit within ``READ_BOUND_S``: a reading whose
  ``own`` holds the undone test's path and whose ``brought`` does not, or its public error.
- *The other side.* An ordinary octopus merge of eight branches, each with a commit inside its own trailers'
  paths (one a test designer's under ``tests/acceptance/**``), made with one ``git merge`` in an orchestrator's
  own call, is silent, and ``read_merge`` gives it an empty ``own``. A fix that refuses or flags every merge
  commit with more than two or three parents fails these.

**Not pinned:** a number of parents at which anything changes, a number of git processes, how the time is
kept, which form the finding has, and what the check does to the move beyond recording it.

**``READ_BOUND_S``** is a third of the harness's hook limit. It is safe on a loaded machine because the work
asked for is small: the merge commit has 150 parents, and one git process for each of them, or a refusal
before any, is a fraction of a second on an idle machine. The bound leaves room for that to be many times
slower, and leaves the hook two thirds of its limit for the rest of its work.

**2. A ``commit`` argument that names something other than that commit is refused.** DEC-403: the helper
"refuses a ``commit`` argument that is not a commit id". Two arguments have a commit id's form and are not the
id of a commit: the object id of an annotated tag that points at a merge commit, and a string of 64 lower-case
hexadecimal digits that is the name of a branch (pointing at a merge commit) in an ordinary SHA-1 repository.
Each is refused with the helper's public error, found as ``test_w1_50_read_merge_every_parent.py`` finds it,
and no reading is returned. The other side: the merge commit's own full id is still read, in a repository that
holds that tag and that branch.

As in the other helper cases, the helper is imported when a test first needs it, after its history is built
and guarded, in a process that says nothing of a caller; no hook runs around any command of a helper case.
"""

from __future__ import annotations

import importlib
import os
import signal
import time

import pytest

import w1_50_support as support
import w1_50_symmetric_support as symmetric

check_support = support.check_support

ORCHESTRATOR = support.ORCHESTRATOR
TICKET = support.TICKET
AS_ORCHESTRATOR = support.AS_ORCHESTRATOR
NO_TRAILERS = support.NO_TRAILERS

MODULE = "gov.guard.containment_merge"
SOURCES = check_support.REPO_ROOT / check_support.GOV_PACKAGE_PARENT_REL

READ_BOUND_S = check_support.HOOK_TIMEOUT_S / 3


@pytest.fixture()
def helper(monkeypatch):
    """``helper()`` -> the module ``gov.guard.containment_merge``, imported from this repository's ``src`` when
    it is first called, in a process that says nothing of a caller."""
    for name in (check_support.ROLE_ENV, check_support.TICKET_ENV, "CLAUDE_PROJECT_DIR"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", os.devnull)
    monkeypatch.setenv("GIT_CONFIG_SYSTEM", os.devnull)
    monkeypatch.syspath_prepend(str(SOURCES))

    def _module():
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


def _built(project, sandbox, command):
    """Run the command with no hook around it. Returns the state the reading must leave as it is."""
    support.run(project, sandbox, command)
    return check_support.state(project, support.WATCHED), check_support.finding_lines(project)


def _assert_left(project, built, what):
    left, findings = built
    check_support.assert_left_as_the_call_left_it(project, left, f"read_merge on {what}")
    assert check_support.finding_lines(project) == findings, f"read_merge on {what}: reading added a finding"


def _checked(reading, what):
    """The reading's ``own`` and ``brought``: two sorted lists of distinct paths with no path in both."""
    for name in ("own", "brought"):
        paths = getattr(reading, name)
        assert isinstance(paths, list) and paths == sorted(paths) and len(set(paths)) == len(paths), (
            f"read_merge on {what}: `{name}` is no sorted list of distinct paths: {paths!r}"
        )
    both = sorted(set(reading.own) & set(reading.brought))
    assert not both, f"read_merge on {what}: `own` and `brought` both hold {both}"
    return reading


def _public_names(module, exception):
    """The names without a leading underscore under which ``module`` holds a class of ``exception``, other
    than ``Exception`` and ``BaseException`` themselves."""
    return sorted(
        name for name, value in vars(module).items()
        if not name.startswith("_") and isinstance(value, type) and issubclass(value, BaseException)
        and value not in (Exception, BaseException) and isinstance(exception, value)
    )


def _refusal(module, root, commit, what):
    """Call ``read_merge(root, commit)``; it must raise. Returns the exception and its public names."""
    try:
        reading = module.read_merge(root, commit)
    except Exception as exc:   # noqa: BLE001 - the class is what the test is about
        names = _public_names(module, exc)
        assert names, (
            f"read_merge on {what} raised {type(exc).__module__}.{type(exc).__qualname__} ({exc}), which "
            f"{MODULE} holds under no public name: the error is not public (DEC-403, F3)"
        )
        return exc, names
    raise AssertionError(f"read_merge on {what} raised nothing and returned {reading!r} (DEC-403)")


# --------------------------------------------------------------------------
# 1. A merge commit with very many parents, through the check
# --------------------------------------------------------------------------

# name: the merge commit's trailers. Neither the orchestrator's nor the caller's allow a path under
# tests/acceptance/**; with none the caller decides, and the caller is the orchestrator.
WITH_OR_WITHOUT_TRAILERS = {
    "orchestrator-trailers": AS_ORCHESTRATOR,
    "no-trailers": NO_TRAILERS,
}


@pytest.mark.parametrize("case", sorted(WITH_OR_WITHOUT_TRAILERS), ids=sorted(WITH_OR_WITHOUT_TRAILERS))
def test_a_move_to_a_merge_commit_with_very_many_parents_that_undoes_a_test_is_a_finding_within_the_hook_s_limit(
        project, sandbox, call, case):
    """Review finding, DEC-403. In the orchestrator's own call a merge commit with 150 parents holds the tree
    from before a test designer's change of an acceptance test, and ``main`` is moved to it. The post-command
    hook ends by itself within the harness's limit and the call adds a finding: one that names the undone test,
    or one for the move as a whole. Which of the two is not pinned."""
    shape = symmetric.merge_commit_with_very_many_parents(project, sandbox, WITH_OR_WITHOUT_TRAILERS[case])
    before = check_support.git(project, "rev-parse", "HEAD").strip()
    result, _ = call(project, shape.command, ORCHESTRATOR, TICKET)
    symmetric.assert_very_many_parents(project, shape, before)
    what = f"{shape.what}, in the orchestrator's own call on {TICKET}"
    assert result.returncode is not None, (
        f"{what}: the post-command hook did not end within the harness's limit of "
        f"{check_support.HOOK_TIMEOUT_S:g} s and was stopped; the findings it added until then: "
        f"{list(result.new_lines)}. A hook that is stopped judges nothing: the test stays undone, unseen"
    )
    findings = check_support.new_findings(result, what)
    assert findings, (
        f"{what}: the hook ended after {result.seconds:.1f} s and no finding was added to "
        f"{check_support.FINDINGS_REL}, neither one that names {shape.undone} nor one for the move as a whole: "
        f"{result.describe()}"
    )


# --------------------------------------------------------------------------
# 1. A merge commit with very many parents, through the helper
# --------------------------------------------------------------------------

class _TookTooLong(BaseException):
    """Raised in the test's own process when ``read_merge`` has not answered within the bound. No subclass of
    ``Exception``: the helper's own handling of errors does not take it for one of its own."""


def _answer_within(seconds, read):
    """Call ``read()`` and return ("reading", its result) or ("error", the exception it raised), with the
    seconds it took; ("stopped", None) when it had not answered after ``seconds`` and was interrupted."""

    def _stop(signum, frame):
        raise _TookTooLong()

    previous = signal.signal(signal.SIGALRM, _stop)
    started = time.monotonic()
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        try:
            answer = ("reading", read())
        except _TookTooLong:
            answer = ("stopped", None)
        except Exception as exc:   # noqa: BLE001 - the class is checked by the caller
            answer = ("error", exc)
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)
    return answer, time.monotonic() - started


def test_read_merge_answers_for_a_merge_commit_with_very_many_parents_in_time_and_never_calls_the_undone_test_brought(
        project, sandbox, helper):
    """Review finding, DEC-403. For the merge commit with 150 parents that undoes a test designer's change,
    ``read_merge`` answers within ``READ_BOUND_S``. Its answer is a reading whose ``own`` holds the undone
    test's path, or its public error. It is never a reading with an empty ``own`` or with that path in
    ``brought``."""
    shape = symmetric.merge_commit_with_very_many_parents(project, sandbox, AS_ORCHESTRATOR)
    before = check_support.git(project, "rev-parse", "HEAD").strip()
    built = _built(project, sandbox, shape.command)
    symmetric.assert_very_many_parents(project, shape, before)
    merge_commit = check_support.git(project, "rev-parse", "HEAD").strip()
    module = helper()
    (kind, value), seconds = _answer_within(READ_BOUND_S, lambda: module.read_merge(str(project), merge_commit))
    assert kind != "stopped" and seconds < READ_BOUND_S, (
        f"read_merge on {shape.what} had not answered after {seconds:.1f} s (the bound is {READ_BOUND_S:g} s, a "
        f"third of the harness's hook limit of {check_support.HOOK_TIMEOUT_S:g} s)"
    )
    if kind == "error":
        assert _public_names(module, value), (
            f"read_merge on {shape.what} raised {type(value).__module__}.{type(value).__qualname__} ({value}), "
            f"which {MODULE} holds under no public name: it is not the helper's public error (DEC-403)"
        )
    else:
        reading = _checked(value, shape.what)
        assert shape.undone in reading.own, (
            f"read_merge on {shape.what}: `own` is {reading.own!r}; it does not hold the undone {shape.undone}"
        )
        assert shape.undone not in reading.brought, (
            f"read_merge on {shape.what}: `brought` holds the undone {shape.undone}"
        )
    _assert_left(project, built, shape.what)


# --------------------------------------------------------------------------
# 1. The other side: an ordinary octopus merge of eight branches
# --------------------------------------------------------------------------

def test_an_ordinary_octopus_merge_of_eight_branches_with_commits_inside_their_own_paths_is_silent(project, sandbox,
                                                                                                  call):
    """One ``git merge`` of eight branches in the orchestrator's own call: a merge commit with nine parents
    that holds every side's change. Each branch has one commit inside the allowed paths of its own trailers;
    one is a test designer's new acceptance test. Every path that differs from a parent is brought by the
    parent that changed it: the check is silent."""
    shape = symmetric.octopus_of_eight_branches(project, sandbox)
    before = check_support.git(project, "rev-parse", "HEAD").strip()
    result, left = call(project, shape.command, ORCHESTRATOR, TICKET)
    symmetric.assert_octopus_of_eight(project, shape, before)
    assert check_support.read(project, support.NEW_TEST), f"the merge did not bring in {support.NEW_TEST}"
    what = f"{shape.what}, in the orchestrator's own call on {TICKET}"
    check_support.assert_silent(result, what)
    check_support.assert_left_as_the_call_left_it(project, left, what)


def test_read_merge_finds_no_own_change_in_an_ordinary_octopus_merge_of_eight_branches(project, sandbox, helper):
    """For the same merge commit ``read_merge`` returns a reading; its ``own`` is empty, and its ``brought``
    is every path where the merge commit differs from one of its nine parents.

    Rewritten after implementation; reason: delegated decision, DEC-410 (DP-22). Until then ``brought`` was
    not compared."""
    shape = symmetric.octopus_of_eight_branches(project, sandbox)
    before = check_support.git(project, "rev-parse", "HEAD").strip()
    built = _built(project, sandbox, shape.command)
    symmetric.assert_octopus_of_eight(project, shape, before)
    merge_commit = check_support.git(project, "rev-parse", "HEAD").strip()
    reading = _checked(helper().read_merge(str(project), merge_commit), shape.what)
    assert reading.own == [], f"read_merge on {shape.what}: `own` is {reading.own!r}, not empty"
    brought = symmetric.differing_from_any_parent(project)
    assert len(brought) >= 8, f"the fixture is wrong: the merge commit differs from its parents in {brought}"
    assert reading.brought == brought, (
        f"read_merge on {shape.what}: `brought` is {reading.brought!r}, not {brought!r}: every path where the "
        f"merge commit differs from some parent and that is not its own (DEC-410, DP-22)"
    )
    _assert_left(project, built, shape.what)


# --------------------------------------------------------------------------
# 2. A `commit` argument that has a commit id's form and is not the id of a commit
# --------------------------------------------------------------------------

TAG = "merged"
HEX_NAMED_BRANCH = "0123456789abcdef" * 4      # 64 lower-case hexadecimal digits: the name of a branch
UNKNOWN_COMMIT = "0" * 40                      # an id that names no object, as in the eighth batch's cases


def _a_merge_with_a_tag_and_a_hex_named_branch(project, sandbox):
    """An ordinary integration merge on ``main``, an annotated tag that points at the merge commit, and a
    branch at the merge commit whose name is 64 lower-case hexadecimal digits. Returns (the merge commit's id,
    the tag object's id, the state a reading must leave as it is)."""
    shape = support.ordinary_integration_merge(project, sandbox)
    support.run(project, sandbox, shape.command)
    assert support.is_merge(project), "the fixture is wrong: HEAD is no merge commit"
    merge_commit = check_support.git(project, "rev-parse", "HEAD").strip()
    check_support.git(project, "tag", "-a", "-m", "an annotated tag", TAG, merge_commit)
    check_support.git(project, "branch", HEX_NAMED_BRANCH, merge_commit)
    tag_object = check_support.git(project, "rev-parse", f"refs/tags/{TAG}").strip()
    assert check_support.git(project, "rev-parse", "--show-object-format").strip() == "sha1" and len(
        merge_commit) == 40, "the fixture is wrong: the repository is no ordinary SHA-1 repository"
    assert tag_object != merge_commit and len(tag_object) == 40 and check_support.git(
        project, "cat-file", "-t", tag_object).strip() == "tag" and check_support.git(
        project, "rev-parse", f"{tag_object}^{{commit}}").strip() == merge_commit, (
        f"the fixture is wrong: {tag_object} is no annotated tag object that points at the merge commit"
    )
    assert check_support.git(project, "rev-parse", f"refs/heads/{HEX_NAMED_BRANCH}").strip() == merge_commit, (
        f"the fixture is wrong: the branch {HEX_NAMED_BRANCH} does not point at the merge commit"
    )
    return merge_commit, tag_object, (check_support.state(project, support.WATCHED),
                                      check_support.finding_lines(project))


# name: (the `commit` argument, given the tag object's id; what it is)
NOT_THE_ID_OF_A_COMMIT = {
    "the-object-id-of-an-annotated-tag-that-points-at-a-merge-commit": (
        lambda tag_object: tag_object, "the object id of an annotated tag that points at a merge commit"),
    "sixty-four-hex-digits-that-are-the-name-of-a-branch-at-a-merge-commit": (
        lambda tag_object: HEX_NAMED_BRANCH,
        "64 lower-case hexadecimal digits that are the name of a branch at a merge commit, in a SHA-1 repository"),
}


@pytest.mark.parametrize("case", sorted(NOT_THE_ID_OF_A_COMMIT), ids=sorted(NOT_THE_ID_OF_A_COMMIT))
def test_read_merge_refuses_a_commit_argument_with_a_commit_id_s_form_that_is_not_the_id_of_a_commit(
        project, sandbox, helper, case):
    """Review finding, DEC-403: the helper "refuses a ``commit`` argument that is not a commit id". The
    argument is made of hexadecimal digits only, and git resolves it to a merge commit; it is not that commit's
    id. It is refused with the public error, the same as for an unknown commit id, and no reading is
    returned."""
    argument, description = NOT_THE_ID_OF_A_COMMIT[case]
    merge_commit, tag_object, built = _a_merge_with_a_tag_and_a_hex_named_branch(project, sandbox)
    commit = argument(tag_object)
    assert commit != merge_commit and set(commit) <= set("0123456789abcdef"), (
        f"the fixture is wrong: the argument {commit!r} is the merge commit's id, or is not made of lower-case "
        f"hexadecimal digits"
    )
    what = f"the commit argument {commit!r} ({description})"
    module = helper()
    _, names = _refusal(module, str(project), commit, what)
    _, of_an_unknown_id = _refusal(module, str(project), UNKNOWN_COMMIT, "an unknown commit id")
    assert set(names) & set(of_an_unknown_id), (
        f"read_merge on {what} raised an error with the public names {names}; an unknown commit id raises one "
        f"with {of_an_unknown_id}: no public error is common to both"
    )
    _assert_left(project, built, what)


def test_read_merge_still_reads_the_merge_commit_s_own_full_id_beside_a_tag_and_a_hex_named_branch(project, sandbox,
                                                                                                 helper):
    """The other side. In the repository that holds the annotated tag and the hex-named branch, the merge
    commit's own full id is read: ``own`` is empty, and ``brought`` is the two paths the merged branch
    brought and the path ``main`` changed since the fork, which the first parent brought.

    Rewritten after implementation; reason: delegated decision, DEC-410 (DP-22). Until then ``brought`` only
    had to hold the merged branch's two paths."""
    merge_commit, _, built = _a_merge_with_a_tag_and_a_hex_named_branch(project, sandbox)
    what = "the merge commit's own full id, beside an annotated tag and a hex-named branch that point at it"
    reading = _checked(helper().read_merge(str(project), merge_commit), what)
    assert reading.own == [], f"read_merge on {what}: `own` is {reading.own!r}, not empty"
    brought = symmetric.differing_from_any_parent(project, merge_commit)
    assert {support.NEW_TEST, support.SOURCE} < set(brought), (
        f"the fixture is wrong: the merge commit differs from its parents in {brought}"
    )
    assert reading.brought == brought, (
        f"read_merge on {what}: `brought` is {reading.brought!r}, not {brought!r}: every path where the merge "
        f"commit differs from some parent and that is not its own (DEC-410, DP-22)"
    )
    _assert_left(project, built, what)
