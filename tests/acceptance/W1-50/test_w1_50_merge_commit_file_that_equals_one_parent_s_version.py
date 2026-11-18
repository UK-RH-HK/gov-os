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
session's own Bash call, and ``gov.containment.commits.judge_commits`` for the merge commit alone (DEC-453),
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
    """``judge(root, commit_ids)`` -> the findings of ``gov.containment.commits.judge_commits``, imported from
    this repository's ``src`` in a process that says nothing of a caller."""
    for name in (check_support.ROLE_ENV, check_support.TICKET_ENV, "CLAUDE_PROJECT_DIR"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.syspath_prepend(str(check_support.REPO_ROOT / check_support.GOV_PACKAGE_PARENT_REL))

    def _judge(root, commit_ids):
        from gov.containment.commits import judge_commits

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


# --------------------------------------------------------------------------
# Git's own clean combination of the two sides equals no parent's version: it stays a finding
# --------------------------------------------------------------------------



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


# --------------------------------------------------------------------------
# Where the check cannot tell, it refuses: the path stays a finding
# --------------------------------------------------------------------------



# --------------------------------------------------------------------------
# 2. Content no parent holds stays a finding (DEC-410, DP-21 and DP-27)
# --------------------------------------------------------------------------

NO_PARENT_S = {
    "a-ticket-file": (TICKET_FILE, AS_ORCHESTRATOR),
    "an-acceptance-test": (ACCEPTANCE_FILE, AS_DESIGNER),
}


# --------------------------------------------------------------------------
# 3. An acceptance test both sides changed, held as one side has it, stays a finding (DEC-410, DP-24)
# --------------------------------------------------------------------------

ONE_SIDE_WHOLE = {
    "holds-the-first-parent-s-version": FIRST,
    "holds-the-second-parent-s-version": SECOND,
}

