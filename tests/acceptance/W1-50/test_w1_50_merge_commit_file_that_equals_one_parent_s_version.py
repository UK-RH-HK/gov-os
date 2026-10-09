"""W1-50 — a merge commit's file that equals one parent's version is not its own change (DEC-572).

Added after implementation; reason: owner decision, DEC-572.

DEC-572: "a merge commit's file is not its own change when it equals one parent's version and every commit
that brought that version passes the check. The existing rules stay as they are: a merge commit's own change
under ``tests/acceptance/**`` or ``.tickets/**`` remains a finding, and so do both sides changing the same
acceptance test (DEC-410)."

**The shape the rule's words give:** a ticket's branch and the integration branch both changed one ticket
file since their one merge base, and the merge commit holds the file exactly as one of the two committed it.
Until DEC-572 that was a finding by DEC-421. Commit ``803f731c`` of this repository, which DEC-572 names, is
not that shape: its ticket file is git's clean combination of both sides and equals neither parent's version.
The last two cases of the first part hold that, and the README returns it as a package.

**How the cases read the rule** (the README's section on DEC-572 states it in full):

- *Lifted:* a path under ``.tickets/**`` that the merge commit holds exactly as one parent has it, where that
  parent's version differs from the one merge base of the two parents, and every commit that brought the
  version passes.
- *The commits that brought the version:* every commit in that parent's history that is not in the merge
  base's, whose content of the path differs from that of one of its own parents. For a merge commit among
  them: from any of its parents.
- *Passes:* judged alone, as the judgement of a list of commits judges it, the commit is no finding at all.
  A merge commit among them passes only when the path is not that merge commit's own change as the check read
  merges before DEC-572: the lift is not applied inside the lift.
- *Refused, so the path stays a finding:* a version that is the merge base's own; several merge bases, or
  none; more than ``MOST_COMMITS`` commits that brought the version; the merge commit holds the version of
  several parents and one of those sides does not pass.
- *Not lifted at all:* a path under ``tests/acceptance/**`` (DEC-572's third point, DEC-410 DP-24), and
  content no parent holds.

Every case drives both public interfaces with one history: the post-command check around an orchestrator
session's own Bash call, and ``gov.guard.containment.judge_commits`` for the merge commit alone (DEC-453),
which ``gov close`` calls for a ticket's commits.
"""

from __future__ import annotations

import shlex
import subprocess

import pytest

import w1_50_own_change_support as own_change
import w1_50_support as support

check_support = support.check_support

ORCHESTRATOR = support.ORCHESTRATOR
TICKET = support.TICKET
AS_ORCHESTRATOR = support.AS_ORCHESTRATOR
AS_ENGINEER = support.AS_ENGINEER
AS_DESIGNER = support.AS_DESIGNER
ORCHESTRATOR_ON_MAIN = support.ORCHESTRATOR_ON_MAIN

BRANCH = support.TICKET_BRANCH                 # the merged side: the second parent
INNER = "inner"                                # a branch that the merged side itself merged
TICKET_FILE = own_change.TICKET_FILE           # .tickets/DAEO-zz94.md
ACCEPTANCE_FILE = support.ACCEPTANCE_FILE
SOURCE = support.SOURCE

FIRST = own_change.FIRST
SECOND = own_change.SECOND

# The most commits that brought one version for which the check still tells. Proposed by the test designer
# (README, "The bound"); the integration side of `803f731c` has four.
MOST_COMMITS = 50

# The commit DEC-572 names, in this repository: the orchestrator's merge of `w1/integrate` into `w1/W1-41`.
WORKED_EXAMPLE = "803f731c5f053fcc0513bc4336779532e14f41b8"
WORKED_EXAMPLE_FILE = ".tickets/DAEO-cdoi.md"


@pytest.fixture()
def judge(monkeypatch):
    """``judge(root, commit_ids)`` -> the findings of ``gov.guard.containment.judge_commits``, imported from
    this repository's ``src`` in a process that says nothing of a caller."""
    for name in (check_support.ROLE_ENV, check_support.TICKET_ENV, "CLAUDE_PROJECT_DIR"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.syspath_prepend(str(check_support.REPO_ROOT / check_support.GOV_PACKAGE_PARENT_REL))

    def _judge(root, commit_ids):
        from gov.guard.containment import judge_commits

        return judge_commits(str(root), list(commit_ids))

    return _judge


# --------------------------------------------------------------------------
# Shell: the commits of a side, and the merge commit
# --------------------------------------------------------------------------

def _change(word, trailers, path=TICKET_FILE, also=None):
    """Shell: append the line ``word`` to ``path`` (and to ``also``) and commit, with ``trailers``."""
    paths = [path] + ([also] if also else [])
    appended = " && ".join(f"echo {shlex.quote(word)} >> {shlex.quote(p)}" for p in paths)
    return appended + " && " + support.commit_paths(paths, trailers, subject=f"the line {word}")


def _back(trailers, path=TICKET_FILE):
    """Shell: a commit that puts ``path`` back as the commit before the newest holds it."""
    return (f"git checkout -q HEAD~1 -- {shlex.quote(path)} && "
            + support.commit_paths([path], trailers, subject="put back"))


def _many_changes(count, trailers=AS_ORCHESTRATOR, path=TICKET_FILE):
    """Shell: ``count`` commits, each of which appends one line to ``path``."""
    return (f"for n in $(seq 1 {count}); do echo line-$n >> {shlex.quote(path)} && git add -- {shlex.quote(path)} "
            f"&& git commit -q -m \"change $n\"" + support._trailer_options(trailers) + " || exit 1; done")


def _merge_of(other, takes=None, path=TICKET_FILE, trailers=AS_ORCHESTRATOR):
    """Shell, on the checked-out branch: merge ``other`` with a merge commit. With ``takes`` (a revision), the
    merge commit holds ``path`` exactly as that revision has it, whatever git made of the two sides."""
    command = f"( git merge -q --no-ff --no-commit {shlex.quote(other)} > /dev/null 2>&1 || true )"
    if takes is not None:
        command += f" && git checkout -q {shlex.quote(takes)} -- {shlex.quote(path)} && git add -- {shlex.quote(path)}"
    return (command + " && test -z \"$(git diff --name-only --diff-filter=U)\""
            f" && git commit -q -m {shlex.quote('Merge ' + other)}" + support._trailer_options(trailers))


def _ordinary_merge_on_the_side():
    """Shell, on the merged side: a branch cut at the fork gets an engineer's source file and is merged with a
    merge commit. That merge commit holds the ticket file as the side has it, which the merged branch does not:
    it differs from one of its parents in the ticket file, and the file is not its own change."""
    return (f"git checkout -q -b {INNER} main && " + support.commit(SOURCE, AS_ENGINEER, subject="other work")
            + f" && git checkout -q {shlex.quote(BRANCH)} && " + _merge_of(INNER))


def _merge_on_the_side_that_takes_the_other_s_version():
    """Shell, on the merged side: a branch cut at the fork gets an orchestrator's change of the ticket file and
    is merged; the merge commit holds that branch's version. Both of its sides changed the file: it is that
    merge commit's own change as the check read merges before DEC-572."""
    return (f"git checkout -q -b {INNER} main && " + _change("inner-side", AS_ORCHESTRATOR)
            + f" && git checkout -q {shlex.quote(BRANCH)} && " + _merge_of(INNER, takes=INNER))


def _history(project, sandbox, *side, main=None):
    """The merged side is built by ``side`` on a branch cut from ``main``; ``main`` then gets the commit
    ``main`` (by default an orchestrator's line of its own in the ticket file). ``main`` is checked out."""
    support.ticket_branch_of(project, sandbox, *side, main_moves_on=False)
    support.run(project, sandbox, _change("main-side", ORCHESTRATOR_ON_MAIN) if main is None else main)


def _brought(project, parent, base, path):
    """From git's own answers: the commits in the history of ``parent`` and not in that of ``base`` whose
    content of ``path`` differs from that of one of their own parents, newest first."""
    listing = check_support.git(project, "rev-list", "--parents", f"{base}..{parent}").splitlines()
    found = []
    for line in listing:
        commit_id, *parents = line.split()
        held = support.content_at(project, commit_id, path)
        if any(support.content_at(project, p, path) != held for p in parents):
            found.append(commit_id)
    return found


def _assert_holds(project, before, branch, path, holds, brought, base_s_own=False):
    """Guard against an empty test, from git's own answers: ``HEAD`` is a merge commit of ``before`` and
    ``branch`` with one merge base; it holds ``path`` exactly as each parent in ``holds`` has it and unlike any
    other parent; that version differs from the merge base's (with ``base_s_own``: it is the merge base's and
    the other parent's differs); and ``brought`` commits brought it on each of those sides."""
    parents = support.parents_of(project)
    assert parents == [before, branch], f"the fixture is wrong: the merge commit's parents are {parents}"
    bases = support.merge_bases(project, *parents)
    assert len(bases) == 1, f"the fixture is wrong: the parents have the merge bases {bases}"
    held = support.content_at(project, "HEAD", path)
    at_base = support.content_at(project, bases[0], path)
    at = {FIRST: support.content_at(project, before, path), SECOND: support.content_at(project, branch, path)}
    assert held is not None and sorted(name for name in at if at[name] == held) == sorted(holds), (
        f"the fixture is wrong: the merge commit does not hold {path} exactly as {holds} parent has it"
    )
    assert (held == at_base) == base_s_own and len(set(at.values()) | {at_base}) > 1, (
        f"the fixture is wrong: the version of {path} the merge commit holds "
        f"{'is not' if base_s_own else 'is'} the merge base's"
    )
    for name, count in zip(holds, brought):
        found = _brought(project, {FIRST: before, SECOND: branch}[name], bases[0], path)
        assert len(found) == count, (
            f"the fixture is wrong: {len(found)} commits brought {name} version of {path}, not {count}"
        )


def _assert_own_change_as_read_before(project, commit_id, path):
    """Guard against an empty test, from git's own answers: ``commit_id`` is a merge commit of two parents with
    one merge base, both parents changed ``path`` since that merge base and differ in it, and the merge commit
    holds it as one of them has it. That is the merge commit's own change as the check read merges before
    DEC-572 (DEC-421), and the shape DEC-572 lifts: judged alone the commit may be no finding, so the
    judgement of the commit alone cannot tell that it does not pass."""
    parents = support.parents_of(project, commit_id)
    assert len(parents) == 2, f"the fixture is wrong: the commit {commit_id[:12]} has the parents {parents}"
    bases = support.merge_bases(project, *parents)
    assert len(bases) == 1, f"the fixture is wrong: the parents of {commit_id[:12]} have the merge bases {bases}"
    held = support.content_at(project, commit_id, path)
    at_base = support.content_at(project, bases[0], path)
    at = [support.content_at(project, parent, path) for parent in parents]
    assert at_base not in at and at[0] != at[1] and held is not None and held in at, (
        f"the fixture is wrong: {path} is not the own change of the merge commit {commit_id[:12]} as merges "
        f"were read before DEC-572 (both sides changed it and the merge commit holds one side's version)"
    )


def _merge_in_the_call(project, call, judge, command):
    """One call of the orchestrator makes the merge commit; the judgement of a list of commits then judges
    the merge commit alone. Returns (hook result, state after, merge commit id, the function's findings,
    ``main`` before the call, the merged branch's head)."""
    before = check_support.git(project, "rev-parse", "HEAD").strip()
    branch = check_support.git(project, "rev-parse", BRANCH).strip()
    result, left = call(project, command, ORCHESTRATOR, TICKET)
    merge_id = check_support.git(project, "rev-parse", "HEAD").strip()
    assert support.is_merge(project), f"the fixture is wrong: `{command}` made no merge commit"
    return result, left, merge_id, judge(project, [merge_id]), before, branch


def _assert_no_finding(project, result, left, findings, what):
    check_support.assert_silent(result, f"{what}, in the orchestrator's own call")
    check_support.assert_left_as_the_call_left_it(project, left, what)
    assert findings == [], (
        f"{what}: the judgement of the merge commit alone is "
        f"{[(f.commit[:12], f.paths, f.reason) for f in findings]}, not no finding (DEC-572)"
    )


def _assert_finding(project, result, left, findings, merge_id, path, what, names=None):
    """The check flags ``path`` and moves nothing; the function returns one finding, for the merge commit,
    whose ``paths`` hold ``path``. With ``names`` (a commit id): one finding of the check names ``path``, the
    merge commit and that commit together, and so does the function's finding."""
    check_support.assert_caught(result, path, what=f"{what}, in the orchestrator's own call",
                                action=check_support.FLAGGED)
    check_support.assert_left_as_the_call_left_it(project, left, what)
    assert [f.commit for f in findings] == [merge_id] and path in findings[0].paths, (
        f"{what}: the judgement of the merge commit alone is "
        f"{[(f.commit[:12], f.paths, f.reason) for f in findings]}, not one finding that names {path}"
    )
    if names is None:
        return
    reasons = [f["reason"] for f in support.findings_naming(result, path, what)]
    assert any(support.names_commit(r, merge_id) and support.names_commit(r, names) for r in reasons), (
        f"{what}: no finding of the check that names {path} holds in its `reason` both the merge commit "
        f"{merge_id[:12]} and the commit {names[:12]} that brought the version and does not pass (DEC-572): "
        f"{reasons}"
    )
    assert support.names_commit(findings[0].reason, names), (
        f"{what}: the `reason` of the function's finding does not name the commit {names[:12]} that brought "
        f"the version and does not pass (DEC-572): {findings[0].reason!r}"
    )


# --------------------------------------------------------------------------
# 1. Lifted: the ticket file equals one parent's version, and every commit that brought it passes
# --------------------------------------------------------------------------

LIFTED = {
    # as on the integration side of `803f731c`: three orchestrator's commits and an ordinary merge commit
    "several-commits-and-an-ordinary-merge-on-the-merged-side": (
        (_change("one", AS_ORCHESTRATOR), _ordinary_merge_on_the_side(), _change("two", AS_ORCHESTRATOR),
         _change("three", AS_ORCHESTRATOR)), SECOND, 4),
    "one-commit-on-the-merged-side": ((_change("one", AS_ORCHESTRATOR),), SECOND, 1),
    "the-first-parent-s-version": ((_change("one", AS_ORCHESTRATOR),), FIRST, 1),
    "as-many-commits-as-the-bound": ((_many_changes(MOST_COMMITS),), SECOND, MOST_COMMITS),
}


@pytest.mark.parametrize("case", sorted(LIFTED), ids=sorted(LIFTED))
def test_a_ticket_file_a_merge_commit_holds_as_one_parent_has_it_is_no_finding_when_its_commits_pass(
        project, sandbox, call, judge, case):
    """DEC-572. Both sides changed the ticket file since the fork, by orchestrator's commits that pass; the
    merge commit holds it exactly as one parent has it. No finding: silent in the orchestrator's own call, and
    the merge commit judged alone is no finding."""
    side, holds, brought = LIFTED[case]
    _history(project, sandbox, *side)
    command = _merge_of(BRANCH, takes=BRANCH if holds == SECOND else "HEAD")
    what = (f"a --no-ff merge of {BRANCH} into main after both changed {TICKET_FILE} by orchestrator's commits "
            f"({case}); the merge commit holds {holds} version whole")
    result, left, merge_id, findings, before, branch = _merge_in_the_call(project, call, judge, command)
    _assert_holds(project, before, branch, TICKET_FILE, [holds], [brought])
    _assert_no_finding(project, result, left, findings, what)


def test_a_ticket_file_both_sides_changed_in_the_same_way_is_no_finding_when_both_sides_commits_pass(
        project, sandbox, call, judge):
    """DEC-572. An orchestrator's commit made the same change of the ticket file on each side; the merge commit
    holds that version, which is each parent's. The commits of both sides pass: no finding."""
    _history(project, sandbox, support.commit(TICKET_FILE, AS_ORCHESTRATOR, subject="the same change"),
             main=support.commit(TICKET_FILE, ORCHESTRATOR_ON_MAIN, subject="the same change on main"))
    what = (f"a --no-ff merge of {BRANCH} into main after an orchestrator made the same change of {TICKET_FILE} "
            f"on both")
    result, left, merge_id, findings, before, branch = _merge_in_the_call(project, call, judge, _merge_of(BRANCH))
    _assert_holds(project, before, branch, TICKET_FILE, [FIRST, SECOND], [1, 1])
    _assert_no_finding(project, result, left, findings, what)


# --------------------------------------------------------------------------
# Git's own clean combination of the two sides equals no parent's version: it stays a finding
# --------------------------------------------------------------------------

def test_a_clean_combination_of_two_sides_edits_of_a_ticket_file_stays_a_finding(project, sandbox, call, judge):
    """An orchestrator's commit changed a line near the top of the ticket file on ``main`` and another
    appended a line on the merged side; git combines the two without a conflict. The merge commit holds the
    file as neither parent has it: DEC-572 speaks of a file that equals one parent's version, so this stays
    the merge commit's own change (DEC-421; for an acceptance test DEC-410, DP-26). It is the shape of commit
    ``803f731c``, the next case."""
    _history(project, sandbox, _change("one", AS_ORCHESTRATOR),
             main=(f"sed -i 's/^priority: 1$/priority: 2/' {TICKET_FILE} && "
                   + support.commit_paths([TICKET_FILE], ORCHESTRATOR_ON_MAIN, subject="a line near the top")))
    what = (f"a --no-ff merge of {BRANCH} into main; an orchestrator's commit changed one line of {TICKET_FILE} "
            f"on main and another appended a line on the branch, and git combined the two without a conflict")
    result, left, merge_id, findings, before, branch = _merge_in_the_call(
        project, call, judge, support.merge(trailers=AS_ORCHESTRATOR))
    own_change.assert_content_no_parent_holds(project, TICKET_FILE)
    _assert_finding(project, result, left, findings, merge_id, TICKET_FILE, what)


def test_the_merge_commit_decided_as_a_named_exception_equals_no_parent_s_version_and_stays_a_finding(judge):
    """Commit ``803f731c`` of this repository (the orchestrator's merge of ``w1/integrate`` into ``w1/W1-41``),
    judged in place and read-only. It holds the ticket file with the status line of its first parent and the
    path and KPI lines of its second: a clean combination, equal to neither. By the words of DEC-572's rule it
    is the merge commit's own change; DEC-572's first point lists it as a named exception. See the package in
    the README."""
    root = check_support.REPO_ROOT

    def git(*args):
        return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=False)

    if git("cat-file", "-e", WORKED_EXAMPLE + "^{commit}").returncode != 0:
        pytest.skip(f"this repository does not hold the commit {WORKED_EXAMPLE[:12]} (a shallow or partial copy)")
    held, at_first, at_second = (git("rev-parse", f"{WORKED_EXAMPLE}{revision}:{WORKED_EXAMPLE_FILE}").stdout.strip()
                                 for revision in ("", "^1", "^2"))
    assert held and at_first and at_second and held not in (at_first, at_second), (
        f"the fixture is wrong: {WORKED_EXAMPLE[:12]} holds {WORKED_EXAMPLE_FILE} as one of its parents has it"
    )
    seen = git("rev-parse", "HEAD").stdout, git("status", "--porcelain").stdout
    findings = judge(root, [WORKED_EXAMPLE])
    assert (git("rev-parse", "HEAD").stdout, git("status", "--porcelain").stdout) == seen, (
        f"judging {WORKED_EXAMPLE[:12]} changed HEAD, the index or the working tree of this repository"
    )
    assert [f.commit for f in findings] == [WORKED_EXAMPLE] and WORKED_EXAMPLE_FILE in findings[0].paths, (
        f"the judgement of {WORKED_EXAMPLE[:12]} is {[(f.paths, f.reason) for f in findings]}, not one finding "
        f"that names {WORKED_EXAMPLE_FILE}: the file equals no parent's version"
    )


# --------------------------------------------------------------------------
# 4. A version brought by a commit that itself fails the check: a finding, named with that commit
# --------------------------------------------------------------------------

NOT_PASSING = {
    # the side's commits, and which commit the finding names: the n-th newest of the side that changed the path
    "a-worker-s-commit-brought-it": ((_change("one", AS_ENGINEER),), 0),
    "a-worker-s-commit-then-an-orchestrator-s": (
        (_change("one", AS_ENGINEER), _change("two", AS_ORCHESTRATOR)), 1),
    "an-orchestrator-s-commit-that-also-changes-an-acceptance-test": (
        (_change("one", AS_ORCHESTRATOR, also=ACCEPTANCE_FILE),), 0),
    "a-merge-commit-on-that-side-whose-own-change-it-is": (
        (_change("one", AS_ORCHESTRATOR), _merge_on_the_side_that_takes_the_other_s_version()), 0),
}


@pytest.mark.parametrize("case", sorted(NOT_PASSING), ids=sorted(NOT_PASSING))
def test_a_version_brought_by_a_commit_that_does_not_pass_stays_a_finding_named_with_that_commit(
        project, sandbox, call, judge, case):
    """DEC-572: "every commit that brought that version passes the check". The merge commit holds the ticket
    file exactly as its second parent has it, and one commit that brought that version does not pass: it is
    itself a finding when it is judged alone, or it is a merge commit whose own change the file is as merges
    were read before DEC-572 (the lift is not applied inside the lift, so that one is told from git's own
    answers: judged alone it is the lifted shape). The ticket file stays a finding of the merge commit, and
    the finding names that commit."""
    side, nth = NOT_PASSING[case]
    _history(project, sandbox, *side)
    what = (f"a --no-ff merge of {BRANCH} into main after both changed {TICKET_FILE}; the merge commit holds the "
            f"second parent's version, which {case}")
    result, left, merge_id, findings, before, branch = _merge_in_the_call(
        project, call, judge, _merge_of(BRANCH, takes=BRANCH))
    base = support.merge_bases(project, before, branch)[0]
    brought = _brought(project, branch, base, TICKET_FILE)
    _assert_holds(project, before, branch, TICKET_FILE, [SECOND], [len(brought)])
    fails = brought[nth]
    if support.is_merge(project, fails):
        _assert_own_change_as_read_before(project, fails, TICKET_FILE)
    else:
        alone = judge(project, [fails])
        assert [f.commit for f in alone] == [fails], (
            f"the fixture is wrong: judged alone, the commit {fails[:12]} is no finding: {alone}"
        )
    passing = [c for c in brought if c != fails]
    assert not passing or judge(project, passing) == [], (
        f"the fixture is wrong: another commit that brought the version is a finding too"
    )
    _assert_finding(project, result, left, findings, merge_id, TICKET_FILE, what, names=fails)


def test_the_same_change_on_both_sides_stays_a_finding_when_one_side_s_commit_does_not_pass(
        project, sandbox, call, judge):
    """The merge commit holds the version of both parents: every commit of both sides that brought it must
    pass. An engineer's commit made the change on the merged side and an orchestrator's the same change on
    ``main``: the ticket file stays a finding, named with the engineer's commit."""
    _history(project, sandbox, support.commit(TICKET_FILE, AS_ENGINEER, subject="the same change, a worker's"),
             main=support.commit(TICKET_FILE, ORCHESTRATOR_ON_MAIN, subject="the same change on main"))
    what = (f"a --no-ff merge of {BRANCH} into main after an engineer's commit on the branch and an "
            f"orchestrator's on main made the same change of {TICKET_FILE}")
    result, left, merge_id, findings, before, branch = _merge_in_the_call(project, call, judge, _merge_of(BRANCH))
    _assert_holds(project, before, branch, TICKET_FILE, [FIRST, SECOND], [1, 1])
    _assert_finding(project, result, left, findings, merge_id, TICKET_FILE, what, names=branch)


# --------------------------------------------------------------------------
# Where the check cannot tell, it refuses: the path stays a finding
# --------------------------------------------------------------------------

def test_a_version_that_is_the_merge_base_s_own_stays_a_finding(project, sandbox, call, judge):
    """The merged side changed the ticket file and changed it back (two orchestrator's commits that pass);
    ``main`` changed it. The merge commit holds the merged side's version, which is the merge base's: it drops
    ``main``'s change. No commit brought that version: a finding (DEC-410, DP-21, as before)."""
    _history(project, sandbox, _change("one", AS_ORCHESTRATOR), _back(AS_ORCHESTRATOR))
    what = (f"a --no-ff merge of {BRANCH} into main; the branch changed {TICKET_FILE} and changed it back, main "
            f"changed it, and the merge commit holds the branch's version, which is the merge base's")
    result, left, merge_id, findings, before, branch = _merge_in_the_call(
        project, call, judge, _merge_of(BRANCH, takes=BRANCH))
    _assert_holds(project, before, branch, TICKET_FILE, [SECOND], [2], base_s_own=True)
    _assert_finding(project, result, left, findings, merge_id, TICKET_FILE, what)


def test_a_version_brought_by_more_commits_than_the_bound_stays_a_finding(project, sandbox, call, judge):
    """The bound, as behaviour: one more orchestrator's commit than ``MOST_COMMITS`` brought the version the
    merge commit holds, and each passes. The check does not walk further than the bound: a finding. (At the
    bound the same history is no finding: ``as-many-commits-as-the-bound``.)"""
    count = MOST_COMMITS + 1
    _history(project, sandbox, _many_changes(count))
    what = (f"a --no-ff merge of {BRANCH} into main after both changed {TICKET_FILE}; the merge commit holds the "
            f"second parent's version, which {count} orchestrator's commits brought")
    result, left, merge_id, findings, before, branch = _merge_in_the_call(
        project, call, judge, _merge_of(BRANCH, takes=BRANCH))
    _assert_holds(project, before, branch, TICKET_FILE, [SECOND], [count])
    _assert_finding(project, result, left, findings, merge_id, TICKET_FILE, what)


def test_a_version_one_parent_brought_across_two_merge_bases_stays_a_finding(project, sandbox, call, judge):
    """With several merge bases every path that differs from a parent is the merge commit's own (DEC-410,
    DP-23), and DEC-572 lifts nothing there: which commits brought a version is told against one merge base.
    An orchestrator's commit after the crossing changed the ticket file on the merged side only."""
    shape = support.criss_cross_merge(project, sandbox, (TICKET_FILE, ORCHESTRATOR_ON_MAIN), AS_ORCHESTRATOR)
    before = check_support.git(project, "rev-parse", "HEAD").strip()
    result, left = call(project, shape.command, ORCHESTRATOR, TICKET)
    support.assert_shape(project, shape, before)
    merge_id = check_support.git(project, "rev-parse", "HEAD").strip()
    assert support.content_at(project, "HEAD", TICKET_FILE) == support.content_at(project, "HEAD^2", TICKET_FILE)
    _assert_finding(project, result, left, judge(project, [merge_id]), merge_id, TICKET_FILE, shape.what)


# --------------------------------------------------------------------------
# 2. Content no parent holds stays a finding (DEC-410, DP-21 and DP-27)
# --------------------------------------------------------------------------

NO_PARENT_S = {
    "a-ticket-file": (TICKET_FILE, AS_ORCHESTRATOR),
    "an-acceptance-test": (ACCEPTANCE_FILE, AS_DESIGNER),
}


@pytest.mark.parametrize("case", sorted(NO_PARENT_S), ids=sorted(NO_PARENT_S))
def test_a_file_a_merge_commit_holds_as_no_parent_has_it_stays_a_finding(project, sandbox, call, judge, case):
    """Both sides changed the path by commits that pass; the merge commit holds content neither parent holds.
    DEC-572 speaks of a file that equals one parent's version: this one equals none."""
    path, by = NO_PARENT_S[case]
    shape = own_change.conflict_resolved_to_new_content(project, sandbox, path, by, AS_ORCHESTRATOR)
    result, left, merge_id, findings, before, branch = _merge_in_the_call(project, call, judge, shape.command)
    own_change.assert_content_no_parent_holds(project, path)
    _assert_finding(project, result, left, findings, merge_id, path, shape.what)


# --------------------------------------------------------------------------
# 3. An acceptance test both sides changed, held as one side has it, stays a finding (DEC-410, DP-24)
# --------------------------------------------------------------------------

ONE_SIDE_WHOLE = {
    "holds-the-first-parent-s-version": FIRST,
    "holds-the-second-parent-s-version": SECOND,
}


@pytest.mark.parametrize("case", sorted(ONE_SIDE_WHOLE), ids=sorted(ONE_SIDE_WHOLE))
def test_an_acceptance_test_both_sides_changed_held_as_one_parent_has_it_stays_a_finding(
        project, sandbox, call, judge, case):
    """DEC-572's third point: "and so do both sides changing the same acceptance test (DEC-410)". The same
    history as the lifted one, for an acceptance test and test designer's commits that pass: a finding, as
    before."""
    shape = own_change.changed_on_both_sides(project, sandbox, ACCEPTANCE_FILE, AS_DESIGNER, ONE_SIDE_WHOLE[case])
    result, left, merge_id, findings, before, branch = _merge_in_the_call(project, call, judge, shape.command)
    own_change.assert_both_changed(project, shape, before, branch)
    _assert_finding(project, result, left, findings, merge_id, ACCEPTANCE_FILE, shape.what)
