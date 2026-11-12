"""S1: the decision checker runs within the gov check budget on a 200-decision, 20k-commit repository [W2-H018].

Interface item 3: the budget of the decision checker is the time limit of the check that runs it, ``core-authority``
(60 s, the runner's default: its declaration states none). A planted repository of 200 decision records and 20,000
commits (built with ``git fast-import``) holds the real ``core-authority`` declaration; ``gov check --json`` ends,
and ``core-authority``'s entry has ``elapsed_s`` below ``time_limit_s``, both printed in the failure message.

This case is load-sensitive: it measures wall time on the machine it runs on.
"""

from __future__ import annotations

import shutil

import pytest

import w2_45_support as support

DECISIONS = 200
COMMITS = 20000


@pytest.fixture(scope="module")
def scale_run(tmp_path_factory):
    assert (support.SRC / "gov" / "__init__.py").is_file()
    base = tmp_path_factory.mktemp("s1")
    project = support.Project(base / "project")
    support.repo_with_decisions(project, decisions=DECISIONS, commits=COMMITS)
    declaration = project.root / support.CHECKS_REL / f"{support.CORE_AUTHORITY}.yaml"
    declaration.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(support.CORE_AUTHORITY_FILE, declaration)  # untracked: the repository's 20,000 commits stay as built
    run = project.check()
    return project, run


def test_s1_the_planted_repository_has_200_decisions_and_20000_commits(scale_run):
    project, _ = scale_run
    assert support.git(project.root, "rev-list", "--count", "HEAD").strip() == str(COMMITS)
    records = [path for path in (project.root / "docs" / "adr").glob("DEC-*.md")]
    assert len(records) == DECISIONS


def test_s1_decision_checker_runs_within_the_gov_check_budget_on_200_decisions_and_20000_commits(scale_run):
    _, run = scale_run
    entry = run.entry(support.CORE_AUTHORITY)
    elapsed, limit = entry.get("elapsed_s"), entry.get("time_limit_s")
    print(f"core-authority: elapsed_s={elapsed} time_limit_s={limit} (gov check ran {run.seconds:.1f} s)")
    assert "CHECK_TIMED_OUT" not in support.finding_codes(entry), \
        f"core-authority timed out: elapsed_s={elapsed} time_limit_s={limit}\n{run.describe()}"
    assert isinstance(elapsed, (int, float)) and isinstance(limit, (int, float)), \
        f"elapsed_s and time_limit_s are not both recorded: {elapsed!r}, {limit!r}\n{run.describe()}"
    assert limit == support.DEFAULT_LIMIT_S, f"the budget is {limit!r}, not 60\n{run.describe()}"
    assert elapsed < limit, f"core-authority took {elapsed} s, the budget is {limit} s\n{run.describe()}"
    assert run.body.get("time_limit_s") == support.DEFAULT_LIMIT_S, run.describe()


def test_s1_the_decision_checker_answered_and_did_not_fail(scale_run):
    """The check ran the decision checker over the planted store: it did not fail on it."""
    _, run = scale_run
    entry = run.entry(support.CORE_AUTHORITY)
    codes = support.finding_codes(entry)
    assert "DECISION_CHECKER_ERROR" not in codes, run.describe()
    assert "DECISIONS_GIT_FAILED" not in codes, run.describe()
    assert "CHECK_FAILED" not in codes and "CHECK_TIMED_OUT" not in codes, run.describe()
