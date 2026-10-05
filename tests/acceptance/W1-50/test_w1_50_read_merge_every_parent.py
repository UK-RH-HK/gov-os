"""W1-50 — the helper that reads a merge reads every parent, and refuses what it cannot read.

Added after implementation; reason: delegated decision, DEC-403 (packages DP-20
option (a) and DP-19 option (a), and the review's F3).

DEC-403, through the helper's public name
(``from gov.guard.containment_merge import read_merge``, DEC-398):

- **DP-20.** ``read_merge`` reads every parent the way it reads the first. A
  path where the merge commit's content differs from any parent's is in
  ``own``, unless another parent brought it by the three-way rule. So ``own``
  also holds the paths where the merge drops a parent's change. With several
  merge bases, or none, ``own`` holds every path that differs from any parent,
  and nothing is brought.
- **DP-19.** An octopus merge in which one other parent has several merge
  bases, or none, with the first parent fails closed as a whole. An octopus
  whose other parents cross only each other is read parent by parent, as
  built.
- **F3.** ``read_merge`` raises a public, documented error; a ``commit``
  argument that is not a commit id (for example one that begins with ``-``) is
  refused, never passed to git as an option.

**What these cases require of the error**, and no more: the exception
``read_merge`` raises is an instance of a class that ``gov.guard.containment_merge``
holds under a name without a leading underscore, and that class is neither
``Exception`` nor ``BaseException``. The class's name is the engineer's to
choose. "Documented" is read as: that name stands in the docstring of
``read_merge`` or of the module, or the class has a docstring of its own.

**Rewritten after implementation; reason: delegated decision, DEC-410 (DP-22).**
``brought`` is the complement of ``own`` over every parent: each path where the
merge commit differs from some parent and that is not its own. Four cases here
that compared ``brought`` only in part compare it exactly now; each says so.

**What is not pinned.** Whether a branch name or an abbreviated id is accepted
for ``commit``; what the helper does for a commit that is no merge; and, for an
octopus whose other parents cross only each other, whether a path that only
one of the crossing parents changed after the crossing is in ``own`` or in
``brought`` (DEC-410, DP-25: read as built, "that pair brings nothing against
each other"; this batch's brief leaves the DP-25 cases as they stand).

As in ``test_w1_50_read_merge_helper.py``, the helper is imported when a test
first needs it, after its history is built and guarded, in a process that says
nothing of a caller; no hook runs around any command.
"""

from __future__ import annotations

import importlib
import os

import pytest

import w1_50_support as support
import w1_50_symmetric_support as symmetric

check_support = support.check_support

AS_ORCHESTRATOR = support.AS_ORCHESTRATOR
TESTS = symmetric.TESTS

MODULE = "gov.guard.containment_merge"
SOURCES = check_support.REPO_ROOT / check_support.GOV_PACKAGE_PARENT_REL


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


def _built(project, sandbox, shape):
    """Run the shape's command with no hook around it. Returns the state the reading must leave as it is."""
    support.run(project, sandbox, shape.command)
    return check_support.state(project, support.WATCHED), check_support.finding_lines(project)


def _read(project, helper, commit, what):
    """The helper's reading of ``commit``: two sorted lists of paths with no path in both."""
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


def _assert_left(project, built, what):
    left, findings = built
    check_support.assert_left_as_the_call_left_it(project, left, f"read_merge on {what}")
    assert check_support.finding_lines(project) == findings, f"read_merge on {what}: reading added a finding"


def _assert_own(reading, own, what):
    assert reading.own == sorted(own), f"read_merge on {what}: `own` is {reading.own!r}, not {sorted(own)!r}"


def _assert_brought(reading, brought, what):
    """DEC-410, DP-22: ``brought`` is each path where the merge commit differs from some parent and that is not
    its own."""
    assert reading.brought == sorted(brought), (
        f"read_merge on {what}: `brought` is {reading.brought!r}, not {sorted(brought)!r}: every path where the "
        f"merge commit differs from some parent and that is not its own (DEC-410, DP-22)"
    )


# --------------------------------------------------------------------------
# DP-20: a dropped change is the merge commit's own
# --------------------------------------------------------------------------

def test_read_merge_puts_the_paths_a_turned_round_merge_commit_drops_in_own(project, sandbox, helper):
    """Shape B: the parents are ``HEAD~2`` and ``HEAD`` in that order and the tree is ``HEAD~2``'s. The merge
    commit changes nothing against its first parent. ``own`` is the two paths it drops; ``brought`` holds
    neither."""
    shape = symmetric.parents_turned_round(project, sandbox, TESTS, AS_ORCHESTRATOR)
    built = _built(project, sandbox, shape)
    assert symmetric.differing(project, "HEAD", "HEAD^1") == [], (
        "the fixture is wrong: the merge commit does not hold its first parent's tree"
    )
    symmetric.assert_own(project, "HEAD", TESTS.paths, shape.what)
    reading = _read(project, helper, "HEAD", shape.what)
    _assert_own(reading, TESTS.paths, shape.what)
    assert reading.brought == [], f"read_merge on {shape.what}: `brought` is {reading.brought!r}, not empty"
    _assert_left(project, built, shape.what)


def test_read_merge_puts_what_an_ours_merge_drops_in_its_own_and_not_in_the_ordinary_merge_s_after_it(
        project, sandbox, helper):
    """Shape N. The ``-s ours`` merge commit on the branch: ``own`` is the two paths ``main`` changed and the
    branch dropped; ``brought`` is the branch's source file, which its first parent brought against ``main``.
    The ordinary merge of the branch after it: ``own`` is empty, and ``brought`` is the dropped paths and the
    branch's source file, each the second parent's content and other than the merge base's.

    Rewritten after implementation; reason: delegated decision, DEC-410 (DP-22). Until then ``brought`` was
    compared in part: of the first merge that it holds no dropped path, of the second that it lacks none of
    the three. Both are compared exactly."""
    shape = symmetric.branch_that_took_main_with_ours(project, sandbox, TESTS, AS_ORCHESTRATOR,
                                                      take_in_the_call=True)
    built = _built(project, sandbox, shape)
    symmetric.assert_own(project, "HEAD^2", TESTS.paths, shape.what)
    symmetric.assert_own(project, "HEAD", (), "the final merge commit")
    assert sorted(symmetric.differing(project, "HEAD", "HEAD^1")) == sorted([*TESTS.paths, support.SOURCE]), (
        f"the fixture is wrong: the final merge commit differs from its first parent in "
        f"{symmetric.differing(project, 'HEAD', 'HEAD^1')}"
    )
    what = f"the `-s ours` merge commit of {shape.what}"
    dropping = _read(project, helper, "HEAD^2", what)
    _assert_own(dropping, TESTS.paths, what)
    assert symmetric.differing_from_any_parent(project, "HEAD^2") == sorted([*TESTS.paths, support.SOURCE]), (
        f"the fixture is wrong: the `-s ours` merge commit differs from its parents in "
        f"{symmetric.differing_from_any_parent(project, 'HEAD^2')}"
    )
    _assert_brought(dropping, [support.SOURCE], what)

    what = f"the final merge commit of {shape.what}"
    final = _read(project, helper, "HEAD", what)
    _assert_own(final, (), what)
    _assert_brought(final, [*TESTS.paths, support.SOURCE], what)
    _assert_left(project, built, shape.what)


# name: (which side holds the test designer's commit, the merge commit's first parent is the branch)
EACH_SIDE = {
    "an-ordinary-merge": ("the-test-designer-s-commit-on-main", False),
    "the-parents-turned-round": ("the-test-designer-s-commit-on-main", True),
}


@pytest.mark.parametrize("case", sorted(EACH_SIDE), ids=sorted(EACH_SIDE))
def test_read_merge_finds_no_own_change_in_a_merge_that_takes_each_side_s_change(project, sandbox, helper, case):
    """The branch changed a source file and ``main`` an acceptance test; the merge commit holds both. It
    differs from each parent in one path, and the other parent brought it: ``own`` is empty, and ``brought``
    is both paths, whichever parent comes first.

    Rewritten after implementation; reason: delegated decision, DEC-410 (DP-22). Until then only the path the
    other parent brought against the first parent was required in ``brought``."""
    sides, turned_round = EACH_SIDE[case]
    shape = symmetric.each_side_changed_its_own_path(project, sandbox, sides, turned_round)
    built = _built(project, sandbox, shape)
    symmetric.assert_taking(project, shape)
    reading = _read(project, helper, "HEAD", shape.what)
    _assert_own(reading, (), shape.what)
    assert len(shape.differs) == 2 and all(
        len(symmetric.differing(project, "HEAD", parent)) == 1 for parent in ("HEAD^1", "HEAD^2")), (
        "the fixture is wrong: the merge commit does not differ from each parent in one path"
    )
    _assert_brought(reading, shape.differs, shape.what)
    _assert_left(project, built, shape.what)


# --------------------------------------------------------------------------
# Several merge bases, or none, with a dropped change
# --------------------------------------------------------------------------

def test_read_merge_with_several_merge_bases_puts_every_path_that_differs_from_any_parent_in_own(project,
                                                                                                sandbox, helper):
    """A criss-cross history turned round: the parents are ``crossing`` and ``HEAD`` in that order (two merge
    bases) and the tree is ``crossing``'s. The merge commit changes nothing against its first parent. Against
    its second it differs in the engineer's source file of ``crossing`` and in the acceptance test a test
    designer changed on ``main``: both are in ``own``, and nothing is brought."""
    shape = symmetric.criss_cross_turned_round(project, sandbox)
    built = _built(project, sandbox, shape)
    assert len(support.merge_bases(project, "HEAD^1", "HEAD^2")) == 2 and symmetric.differing(
        project, "HEAD", "HEAD^1") == [], (
        "the fixture is wrong: the parents do not have two merge bases, or the merge commit does not hold its "
        "first parent's tree"
    )
    own = [support.ACCEPTANCE_FILE, support.SOURCE]
    assert symmetric.differing_from_any_parent(project) == sorted(own), (
        f"the fixture is wrong: the merge commit differs from its parents in "
        f"{symmetric.differing_from_any_parent(project)}"
    )
    reading = _read(project, helper, "HEAD", shape.what)
    _assert_own(reading, own, shape.what)
    assert reading.brought == [], f"read_merge on {shape.what}: `brought` is {reading.brought!r}, not empty"
    _assert_left(project, built, shape.what)


def test_read_merge_with_no_merge_base_puts_every_path_that_differs_from_any_parent_in_own(project, sandbox,
                                                                                          helper):
    """Shape NB2: the first parent is a commit without a parent and with an empty tree, the second is ``HEAD``,
    and the tree is ``HEAD``'s without ``tests/acceptance/``. ``own`` is every path the tree holds (each
    differs from the first parent) and every path it deletes (each differs from the second); nothing is
    brought."""
    shape = symmetric.unrelated_first_parent(project, sandbox, TESTS, AS_ORCHESTRATOR)
    before = check_support.git(project, "rev-parse", "HEAD").strip()
    built = _built(project, sandbox, shape)
    assert support.merge_bases(project, "HEAD^1", "HEAD^2") == [] and support.parents_of(project)[1] == before, (
        "the fixture is wrong: the parents have a merge base, or the second parent is not HEAD"
    )
    deleted = [symmetric.ACCEPTANCE_README, *TESTS.paths]
    own = sorted([*symmetric.tree_paths(project), *deleted])
    assert symmetric.differing_from_any_parent(project) == own and sorted(shape.own) == own, (
        f"the fixture is wrong: the merge commit differs from its parents in "
        f"{symmetric.differing_from_any_parent(project)}"
    )
    reading = _read(project, helper, "HEAD", shape.what)
    _assert_own(reading, own, shape.what)
    assert reading.brought == [], f"read_merge on {shape.what}: `brought` is {reading.brought!r}, not empty"
    _assert_left(project, built, shape.what)


# --------------------------------------------------------------------------
# DP-19: octopus merges
# --------------------------------------------------------------------------

def _crossing_octopus(project, sandbox):
    shape = symmetric.octopus_with_a_crossing_parent(project, sandbox)
    # The engineer's file and the new test differ from the first parent; the new test from the crossing parent;
    # what the two crossing sides changed and the engineer's file from the ordinary branch.
    return shape, [support.NEW_TEST, support.SOURCE, support.NOTES, support.README], (2, 1)


def _unrelated_octopus(project, sandbox):
    shape = symmetric.octopus_with_an_unrelated_parent(project, sandbox)
    # Every path the tree holds differs from a parent: the island's file from the first parent, and every
    # other path from the island.
    return shape, None, (1, 0)


# name: the history. Each builder returns the shape, `own` as a literal list (None: every path the merge
# commit's tree holds) and the number of merge bases the first parent has with each other parent.
OCTOPUS_THAT_FAILS_CLOSED = {
    "one-other-parent-has-several-merge-bases-with-the-first": _crossing_octopus,
    "one-other-parent-has-no-merge-base-with-the-first": _unrelated_octopus,
}


@pytest.mark.parametrize("case", sorted(OCTOPUS_THAT_FAILS_CLOSED), ids=sorted(OCTOPUS_THAT_FAILS_CLOSED))
def test_read_merge_fails_closed_for_a_whole_octopus_merge_when_one_parent_has_several_merge_bases_or_none(
        project, sandbox, helper, case):
    """DEC-403, DP-19 with DP-20. One other parent has several merge bases, or none, with the first parent; the
    third parent is an ordinary ticket branch with a test designer's new test. Nothing is brought, the ordinary
    branch's test included, and ``own`` is every path that differs from any of the three parents."""
    shape, own, bases = OCTOPUS_THAT_FAILS_CLOSED[case](project, sandbox)
    built = _built(project, sandbox, shape)
    parents = support.parents_of(project)
    found = tuple(len(support.merge_bases(project, parents[0], other)) for other in parents[1:])
    assert len(parents) == 3 and found == bases, (
        f"the fixture is wrong: the merge commit has the parents {parents}; the first has {found} merge bases "
        f"with the others, not {bases}"
    )
    if own is None:
        own = symmetric.tree_paths(project)
    assert symmetric.differing_from_any_parent(project) == sorted(own), (
        f"the fixture is wrong: the merge commit differs from its parents in "
        f"{symmetric.differing_from_any_parent(project)}"
    )
    assert support.content_at(project, "HEAD", support.NEW_TEST) == support.content_at(
        project, support.TICKET_BRANCH, support.NEW_TEST) is not None, (
        f"the fixture is wrong: the merge commit does not hold the ordinary branch's {support.NEW_TEST}"
    )
    reading = _read(project, helper, "HEAD", shape.what)
    assert reading.brought == [], f"read_merge on {shape.what}: `brought` is {reading.brought!r}, not empty"
    _assert_own(reading, own, shape.what)
    _assert_left(project, built, shape.what)


def test_read_merge_reads_an_octopus_whose_other_parents_cross_only_each_other_parent_by_parent(project, sandbox,
                                                                                               helper):
    """DEC-403, DP-19: "an octopus whose other parents cross only each other is read parent by parent, as
    built". Each of the two branches has one merge base with the first parent; they have two with each other.

    Pinned, as it holds as built and under DP-20 alike: the test designer's new test and the engineer's source
    file, which both branches hold and which differ from the first parent only, are in ``brought``; the file
    ``main`` changed, which the first parent brought, is not in ``own``. Not pinned: the source file one
    branch changed after the crossing, which may be in ``own`` or in ``brought`` (DEC-410, DP-25: as built).

    Rewritten after implementation; reason: delegated decision, DEC-410 (DP-22). Until then ``brought`` only
    had to hold the new test and the source file. Now it is exactly the paths where the merge commit differs
    from a parent that are not in ``own``: the file ``main`` changed is in it too.
    """
    shape = symmetric.octopus_whose_other_parents_cross_each_other(project, sandbox)
    built = _built(project, sandbox, shape)
    first, one, other = support.parents_of(project)
    bases = [len(support.merge_bases(project, *pair)) for pair in ((first, one), (first, other), (one, other))]
    assert bases == [1, 1, 2], f"the fixture is wrong: the pairs of parents have {bases} merge bases"
    assert symmetric.differing(project, "HEAD", first) == sorted(
        [support.NEW_TEST, support.SECOND_SOURCE, support.SOURCE]) and symmetric.differing(
        project, "HEAD", other) == [support.BOOTSTRAP] and sorted(symmetric.differing(
            project, "HEAD", one)) == sorted([support.BOOTSTRAP, support.SECOND_SOURCE]), (
        "the fixture is wrong: the merge commit does not differ from its parents as the test describes"
    )
    reading = _read(project, helper, "HEAD", shape.what)
    missing = sorted({support.NEW_TEST, support.SOURCE} - set(reading.brought))
    assert not missing, f"read_merge on {shape.what}: `brought` lacks {missing}: {reading.brought!r}"
    unexpected = sorted(set(reading.own) - {support.SECOND_SOURCE})
    assert not unexpected, f"read_merge on {shape.what}: `own` holds {unexpected}"
    _assert_brought(reading, set(symmetric.differing_from_any_parent(project)) - set(reading.own), shape.what)
    _assert_left(project, built, shape.what)


# --------------------------------------------------------------------------
# F3: the public error, and a `commit` argument that is no commit id
# --------------------------------------------------------------------------

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
    raise AssertionError(f"read_merge on {what} raised nothing and returned {reading!r} (DEC-403, F3)")


def _a_merge(project, sandbox):
    """An ordinary integration merge on ``main``: the repository the refusals are asked of."""
    shape = support.ordinary_integration_merge(project, sandbox)
    support.run(project, sandbox, shape.command)
    assert support.is_merge(project), "the fixture is wrong: HEAD is no merge commit"
    return check_support.state(project, support.WATCHED), check_support.finding_lines(project)


# name: a `commit` argument that names no commit of the repository
UNKNOWN_COMMITS = {
    "forty-hex-digits-that-name-no-object": "0123456789abcdef0123456789abcdef01234567",
    "all-zeros": "0" * 40,
}


@pytest.mark.parametrize("case", sorted(UNKNOWN_COMMITS), ids=sorted(UNKNOWN_COMMITS))
def test_read_merge_raises_a_public_error_for_an_unknown_commit_id(project, sandbox, helper, case):
    """DEC-403, F3. The id has the form of a commit id and names no object of the repository."""
    commit = UNKNOWN_COMMITS[case]
    built = _a_merge(project, sandbox)
    assert check_support.git(project, "rev-list", "--all").find(commit) == -1, (
        "the fixture is wrong: the repository holds a commit with that id"
    )
    what = f"the commit id {commit!r}, which names no object"
    _refusal(helper(), str(project), commit, what)
    _assert_left(project, built, what)


def test_read_merge_raises_a_public_error_for_a_path_that_is_no_repository(project, sandbox, helper, tmp_path):
    """DEC-403, F3. ``root`` is an existing directory outside every git repository."""
    _a_merge(project, sandbox)
    merge_commit = check_support.git(project, "rev-parse", "HEAD").strip()
    elsewhere = tmp_path / "no-repository"
    elsewhere.mkdir()
    import subprocess
    inside = subprocess.run(["git", "-C", str(elsewhere), "rev-parse", "--git-dir"], capture_output=True,
                            text=True, check=False)
    assert inside.returncode != 0, f"the fixture is wrong: {elsewhere} is inside the repository {inside.stdout!r}"
    what = f"the directory {elsewhere}, which is no repository"
    _refusal(helper(), str(elsewhere), merge_commit, what)
    assert sorted(elsewhere.iterdir()) == [], f"read_merge on {what} wrote {sorted(elsewhere.iterdir())}"


def test_the_error_read_merge_raises_is_documented(project, sandbox, helper):
    """DEC-403, F3: "a public, documented error". One of the error's public names stands in the docstring of
    ``read_merge`` or of the module, or the class has a docstring of its own."""
    _a_merge(project, sandbox)
    module = helper()
    _, names = _refusal(module, str(project), UNKNOWN_COMMITS["all-zeros"], "an unknown commit id")
    texts = (module.read_merge.__doc__ or "") + "\n" + (module.__doc__ or "")
    documented = [name for name in names
                  if name in texts or (vars(getattr(module, name)).get("__doc__") or "").strip()]
    assert documented, (
        f"the error read_merge raises ({names}) stands in no docstring of read_merge or of {MODULE}, and has no "
        f"docstring of its own"
    )


def test_the_docstring_of_read_merge_speaks_of_own_and_brought(helper):
    """DEC-403, F3: "the docstring says exactly what ``own`` and ``brought`` hold". The words themselves are
    the engineer's; the test asks only that the docstring names both."""
    text = helper().read_merge.__doc__ or ""
    missing = [word for word in ("own", "brought") if word not in text]
    assert not missing, f"the docstring of read_merge does not name {missing}: {text!r}"


# name: a `commit` argument that is no commit id
NO_COMMIT_IDS = {
    "the-option-all": "--all",
    "the-option-1": "-1",
    "an-option-with-a-value": "--output=read_merge_wrote_this",
    "the-empty-string": "",
}


@pytest.mark.parametrize("case", sorted(NO_COMMIT_IDS), ids=sorted(NO_COMMIT_IDS))
def test_read_merge_refuses_a_commit_argument_that_is_no_commit_id(project, sandbox, helper, case):
    """DEC-403, F3: "a ``commit`` argument that is not a commit id (for example one that begins with ``-``) is
    refused, never passed to git as an option". The refusal is the public error; no reading is returned, and
    the repository is left as it was. In the repository ``HEAD`` is a merge commit, so an argument git took
    for an option could still be answered with a reading."""
    commit = NO_COMMIT_IDS[case]
    built = _a_merge(project, sandbox)
    what = f"the commit argument {commit!r}"
    module = helper()
    _, names = _refusal(module, str(project), commit, what)
    _, of_an_unknown_id = _refusal(module, str(project), UNKNOWN_COMMITS["all-zeros"], "an unknown commit id")
    assert set(names) & set(of_an_unknown_id), (
        f"read_merge on {what} raised an error with the public names {names}; an unknown commit id raises one "
        f"with {of_an_unknown_id}: no public error is common to both"
    )
    assert check_support.read(project, "read_merge_wrote_this") is None, (
        f"read_merge on {what}: git took the argument for an option and wrote a file"
    )
    _assert_left(project, built, what)
