"""W1-01: an integration merge and the rule "only the test designer commits acceptance tests" (DEC-253).

KPI failure 1: "Any implementer commit touching tests/acceptance/** before W1-05 lands".

Owner decision DEC-253 (2026-10-04), after the first integration merge of the
parallel run (DEC-235):

- an integration merge commit passes when every change it brings under
  ``tests/acceptance/`` comes from commits on the merged side carrying
  ``Role: independent-test-designer``;
- every non-merge commit is checked exactly as before.

Each test builds a small git repository in a temporary directory and asks the
rule of ``test_only_the_test_designer_commits_to_acceptance_tests``
(``w1_01_support.acceptance_test_offenders``) which commits offend. The last
test asks it about the history of this repository.
"""

from __future__ import annotations

import subprocess

import pytest

import w1_01_support as support

DESIGNER = support.TEST_DESIGNER_ROLE
ACCEPTANCE = "tests/acceptance"
TEST_FILE = f"{ACCEPTANCE}/W1-90/test_fixture.py"
OTHER_TEST_FILE = f"{ACCEPTANCE}/W1-91/test_other.py"
SOURCE_FILE = "src/app/main.py"

_GIT = (
    "-c", "user.name=W1-01 acceptance", "-c", "user.email=w1-01@example.invalid",
    "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null",
)


def _git(repo, *args):
    proc = subprocess.run(["git", "-C", str(repo), *_GIT, *args], capture_output=True, text=True, check=False)
    assert proc.returncode == 0, f"git {' '.join(args)} failed in the test repository: {proc.stderr.strip()}"
    return proc.stdout.strip()


def _commit(repo, files, subject, role=None):
    """Write ``files`` and commit them; ``role`` goes in the final trailer block (DEC-182)."""
    for rel, text in files.items():
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    _git(repo, "add", "-A")
    args = ["commit", "-q", "-m", subject, "--trailer", "Task: DAEO-zz90"]
    if role:
        args += ["--trailer", f"Role: {role}"]
    _git(repo, *args)
    return _git(repo, "rev-parse", "HEAD")


def _merge(repo, branch, role="orchestrator", own_change=None):
    """Merge ``branch`` with a merge commit. ``own_change`` is written into the merge commit itself."""
    _git(repo, "merge", "-q", "--no-ff", "--no-commit", branch)
    for rel, text in (own_change or {}).items():
        (repo / rel).write_text(text, encoding="utf-8")
    _git(repo, "add", "-A")
    args = ["commit", "-q", "-m", f"Merge {branch}", "--trailer", "Task: DAEO-zz90"]
    if role:
        args += ["--trailer", f"Role: {role}"]
    _git(repo, *args)
    merge = _git(repo, "rev-parse", "HEAD")
    assert len(support.commit_parents(merge, repo)) == 2, "the fixture made no merge commit"
    return merge


@pytest.fixture()
def repo(tmp_path):
    """``integrate`` holds a source file and a test-designer commit; HEAD is on ``integrate``."""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "integrate")
    _commit(repo, {SOURCE_FILE: "VALUE = 1\n"}, "source", role="engineer")
    _commit(repo, {TEST_FILE: "VALUE = 1\n"}, "tests", role=DESIGNER)
    return repo


def _ticket_branch(repo, *commits):
    """A branch ``ticket`` with ``commits`` ((files, role), ...), while ``integrate`` moves on by one commit."""
    _git(repo, "checkout", "-q", "-b", "ticket")
    shas = [_commit(repo, files, f"ticket commit {n}", role=role) for n, (files, role) in enumerate(commits)]
    _git(repo, "checkout", "-q", "integrate")
    _commit(repo, {"README.md": "# fixture\n"}, "integrate moves on", role="orchestrator")
    return shas


def _offenders(repo):
    return support.acceptance_test_offenders(repo)


# --------------------------------------------------------------------------
# Merges that pass
# --------------------------------------------------------------------------

def test_a_merge_of_test_designer_commits_passes(repo):
    """The case of 2026-10-04: a ticket branch with a test-designer commit and an engineer commit."""
    _ticket_branch(repo, ({TEST_FILE: "VALUE = 2\n", OTHER_TEST_FILE: "NEW = 1\n"}, DESIGNER),
                   ({SOURCE_FILE: "VALUE = 2\n"}, "engineer"))
    merge = _merge(repo, "ticket", role="orchestrator")
    assert merge in support.commits_touching(ACCEPTANCE, repo), (
        "the fixture is empty: the merge commit is not among the commits touching tests/acceptance"
    )
    assert _offenders(repo) == [], "an integration merge of test-designer commits is taken for an offender"


def test_a_merge_that_removes_a_test_as_the_test_designer_did_passes(repo):
    _ticket_branch(repo, ({OTHER_TEST_FILE: "NEW = 1\n"}, DESIGNER))
    _git(repo, "checkout", "-q", "ticket")
    (repo / TEST_FILE).unlink()
    _commit(repo, {}, "the designer removes a test", role=DESIGNER)
    _git(repo, "checkout", "-q", "integrate")
    _merge(repo, "ticket")
    assert not (repo / TEST_FILE).exists(), "the fixture merge did not remove the test"
    assert _offenders(repo) == []


def test_a_merge_of_the_integration_branch_into_a_ticket_branch_passes(repo):
    """The other direction (a conflict is resolved in the ticket's worktree): both sides hold designer commits."""
    _ticket_branch(repo, ({OTHER_TEST_FILE: "NEW = 1\n"}, DESIGNER))
    _commit(repo, {f"{ACCEPTANCE}/W1-92/test_third.py": "NEW = 1\n"}, "another ticket's tests", role=DESIGNER)
    _git(repo, "checkout", "-q", "ticket")
    _merge(repo, "integrate", role="orchestrator")
    assert _offenders(repo) == []


def test_a_merge_commit_without_any_role_passes_on_the_same_terms(repo):
    """DEC-253 judges the merge by what it brings, not by the merge commit's own trailers."""
    _ticket_branch(repo, ({OTHER_TEST_FILE: "NEW = 1\n"}, DESIGNER))
    _merge(repo, "ticket", role=None)
    assert _offenders(repo) == []


# --------------------------------------------------------------------------
# Merges that still fail
# --------------------------------------------------------------------------

@pytest.mark.parametrize("role", ["engineer", "orchestrator", None], ids=["engineer", "orchestrator", "no-role"])
def test_a_merge_that_brings_a_change_from_a_commit_without_the_role_fails(repo, role):
    good, bad = _ticket_branch(repo, ({OTHER_TEST_FILE: "NEW = 1\n"}, DESIGNER),
                               ({TEST_FILE: "VALUE = 3\n", SOURCE_FILE: "VALUE = 3\n"}, role))
    merge = _merge(repo, "ticket")
    offenders = _offenders(repo)
    text = "\n".join(offenders)
    assert merge[:12] in text, f"the merge that brings {bad[:12]} is not an offender: {offenders}"
    assert bad[:12] in text, f"the commit without the role, {bad[:12]}, is not named: {offenders}"
    assert good[:12] not in text, f"the test designer's commit {good[:12]} is named as an offender: {offenders}"


def test_a_merge_that_changes_an_acceptance_test_itself_fails(repo):
    """An "evil merge": the merge commit holds content that none of its parents holds."""
    _ticket_branch(repo, ({OTHER_TEST_FILE: "NEW = 1\n"}, DESIGNER))
    merge = _merge(repo, "ticket", own_change={OTHER_TEST_FILE: "NEW = 'changed in the merge'\n"})
    offenders = _offenders(repo)
    assert len(offenders) == 1 and merge[:12] in offenders[0] and OTHER_TEST_FILE in offenders[0], (
        f"the merge changes {OTHER_TEST_FILE} beyond what its parents hold and is not the one offender: {offenders}"
    )


def test_a_merge_that_adds_an_acceptance_test_itself_fails(repo):
    _ticket_branch(repo, ({SOURCE_FILE: "VALUE = 2\n", OTHER_TEST_FILE: "NEW = 1\n"}, DESIGNER))
    added = f"{ACCEPTANCE}/W1-90/test_added_in_the_merge.py"
    merge = _merge(repo, "ticket", own_change={added: "NEW = 1\n"})
    offenders = _offenders(repo)
    assert len(offenders) == 1 and merge[:12] in offenders[0] and added in offenders[0], (
        f"the merge adds {added}, which no parent holds, and is not the one offender: {offenders}"
    )


def test_a_merge_that_drops_the_merged_side_s_change_to_a_test_fails(repo):
    """Both sides changed the same test; the merge keeps neither side's file. That is the merge's own change."""
    _git(repo, "checkout", "-q", "-b", "ticket")
    _commit(repo, {TEST_FILE: "VALUE = 2\n"}, "ticket tests", role=DESIGNER)
    _git(repo, "checkout", "-q", "integrate")
    _commit(repo, {TEST_FILE: "VALUE = 3\n"}, "integrate tests", role=DESIGNER)
    proc = subprocess.run(["git", "-C", str(repo), *_GIT, "merge", "-q", "--no-ff", "--no-commit", "ticket"],
                          capture_output=True, text=True, check=False)
    assert proc.returncode != 0, "the fixture merge did not conflict"
    (repo / TEST_FILE).write_text("VALUE = 'resolved by hand'\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "Merge ticket", "--trailer", "Role: orchestrator")
    merge = _git(repo, "rev-parse", "HEAD")
    offenders = _offenders(repo)
    assert len(offenders) == 1 and merge[:12] in offenders[0], (
        f"a conflict resolved in the merge commit by a non-designer is not the one offender: {offenders}"
    )


# --------------------------------------------------------------------------
# Non-merge commits: exactly as before
# --------------------------------------------------------------------------

@pytest.mark.parametrize("role", ["engineer", "orchestrator", None], ids=["engineer", "orchestrator", "no-role"])
def test_a_non_merge_commit_without_the_role_still_fails(repo, role):
    bad = _commit(repo, {TEST_FILE: "VALUE = 9\n"}, "an implementer changes a test", role=role)
    assert _offenders(repo) == [bad[:12]]


def test_a_non_merge_commit_with_the_role_still_passes(repo):
    _commit(repo, {TEST_FILE: "VALUE = 9\n"}, "the designer changes a test", role=DESIGNER)
    assert _offenders(repo) == []


# --------------------------------------------------------------------------
# The history of this repository
# --------------------------------------------------------------------------

def test_the_integration_merges_of_this_repository_pass(repo_root):
    """Every merge commit on HEAD's history that touches tests/acceptance/** passes the DEC-253 rule."""
    merges = [sha for sha in support.commits_touching(ACCEPTANCE, repo_root)
              if len(support.commit_parents(sha, repo_root)) > 1
              and DESIGNER not in support.commit_roles(sha, repo_root)]
    assert merges, "no merge commit on HEAD's history touches tests/acceptance/**: 00e3d539 is expected there"
    failing = {sha[:12]: support.merge_offences(sha, ACCEPTANCE, repo_root) for sha in merges}
    failing = {sha: why for sha, why in failing.items() if why}
    assert not failing, f"integration merges on HEAD's history do not pass the DEC-253 rule: {failing}"
