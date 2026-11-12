"""S1 on a history with merges: the decision checker runs within the gov check budget [W2-H018], review round 1 (F1).

Interface item 3: the budget of the decision checker is the time limit of the check that runs it, ``core-authority``
(60 s). The first S1 case plants a linear history; real histories hold merges. Here the planted repository of 200
decision records and 20,000 commits has one commit in six a merge (3,300 merges of ordinary branch work: side branches
whose commits touch files under ``src/`` and, now and then, the owner's revision of a decision, merged into ``main``
by an engineer's merge). ``gov check --json`` holding the real ``core-authority`` declaration ends, and
``core-authority``'s entry has ``elapsed_s`` below ``time_limit_s`` (60), both printed in the message; it does not time
out and does not fail.

The guard cases hold what is reported on a merge history, at a small scale (the same builder, 40 blocks), by the rules
of ``tests/unit/decisions/test_decisions.py``: a decision whose ACTIVE status is set on a side branch by an engineer's
commit is no approval, and an engineer's ordinary merge of it sets nothing: the decision checker still reports it
(``ACTIVE_UNAPPROVED``); one the owner added on a side branch and an engineer merged is not reported. The decision
checker is called as ``tests/acceptance/W1-26`` calls it (``gov.decisions.checker.check`` in a new process on this
tree's code). Through ``gov check``, ``core-authority`` is still RED on a pair of decisions both ACTIVE while one
supersedes the other, which the owner added on a side branch and an engineer merged.

The big case is load-sensitive: it measures wall time on the machine it runs on.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import time

import pytest

import w2_45_support as support

DECISIONS = 200
COMMITS = 20000
MERGES_LOW, MERGES_HIGH = 3000, 3700

SMALL_DECISIONS, SMALL_BLOCKS = 12, 40
CHECKER_CODE = ("import json, sys\nfrom gov.decisions.checker import check\n"
                "print(json.dumps(check(sys.argv[1]), default=str))\n")


def _with_core_authority(project):
    declaration = project.root / support.CHECKS_REL / f"{support.CORE_AUTHORITY}.yaml"
    declaration.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(support.CORE_AUTHORITY_FILE, declaration)  # untracked: the history stays as built


@pytest.fixture(scope="module")
def merge_scale_run(tmp_path_factory):
    assert (support.SRC / "gov" / "__init__.py").is_file()
    base = tmp_path_factory.mktemp("s1-merges")
    project = support.Project(base / "project")
    started = time.perf_counter()
    built_merges = support.repo_with_merge_history(project, decisions=DECISIONS, commits=COMMITS)
    build_seconds = time.perf_counter() - started
    print(f"the fixture: {COMMITS} commits, {built_merges} merges built in {build_seconds:.1f} s")
    _with_core_authority(project)
    run = project.check()
    return project, run


def test_s1_merges_the_planted_repository_has_200_decisions_20000_commits_and_a_merge_in_six(merge_scale_run):
    project, _ = merge_scale_run
    assert support.git(project.root, "rev-list", "--count", "HEAD").strip() == str(COMMITS)
    merges = int(support.git(project.root, "rev-list", "--merges", "--count", "HEAD").strip())
    assert MERGES_LOW <= merges <= MERGES_HIGH, f"{merges} merges, not about one commit in six"
    records = [path for path in (project.root / "docs" / "adr").glob("DEC-*.md")]
    assert len(records) == DECISIONS


def test_s1_merges_decision_checker_runs_within_the_gov_check_budget_on_a_history_with_merges(merge_scale_run):
    _, run = merge_scale_run
    entry = run.entry(support.CORE_AUTHORITY)
    elapsed, limit = entry.get("elapsed_s"), entry.get("time_limit_s")
    print(f"core-authority: elapsed_s={elapsed} time_limit_s={limit} (gov check ran {run.seconds:.1f} s)")
    codes = support.finding_codes(entry)
    for refused in ("CHECK_TIMED_OUT", "CHECK_FAILED", "DECISION_CHECKER_ERROR", "DECISIONS_GIT_FAILED"):
        assert refused not in codes, \
            f"core-authority has {refused}: elapsed_s={elapsed} time_limit_s={limit}\n{run.describe()}"
    assert isinstance(elapsed, (int, float)) and isinstance(limit, (int, float)), \
        f"elapsed_s and time_limit_s are not both recorded: {elapsed!r}, {limit!r}\n{run.describe()}"
    assert limit == support.DEFAULT_LIMIT_S, f"the budget is {limit!r}, not 60\n{run.describe()}"
    assert elapsed < limit, f"core-authority took {elapsed} s, the budget is {limit} s\n{run.describe()}"


def _record(number, role_note="", **keys):
    extra = "".join(f"{key}: {value}\n" for key, value in keys.items())
    return (f"---\nid: DEC-{number}\ntype: decision\nstatus: ACTIVE\ntitle: Decision {number}\n{extra}---\n"
            f"# DEC-{number}\n{role_note}")


@pytest.fixture(scope="module")
def small_history(tmp_path_factory):
    """A small history with merges (the builder's) and three side branches of this case, each merged by an engineer's
    ordinary merge while ``main`` carried other work: an engineer's ACTIVE decision (901), the owner's ACTIVE decision
    (902), and the owner's pair of decisions ACTIVE while one supersedes the other (903, 904)."""
    base = tmp_path_factory.mktemp("s1-merges-small")
    project = support.Project(base / "project")
    support.repo_with_merge_history(project, decisions=SMALL_DECISIONS, commits=SMALL_DECISIONS + 6 * SMALL_BLOCKS)
    root = project.root
    sides = (("agent-side", "engineer", {901: _record(901)}),
             ("owner-side", "owner", {902: _record(902)}),
             ("pair-side", "owner", {903: _record(903, superseded_by="DEC-904"),
                                     904: _record(904, supersedes="[DEC-903]")}))
    for branch, role, records in sides:
        support.git(root, "checkout", "-q", "-b", branch, "main")
        for number, text in records.items():
            project.write(f"docs/adr/DEC-{number}.md", text)
        project.commit_all(f"decisions of {branch}", trailers=("Task: work", f"Role: {role}"))
        support.git(root, "checkout", "-q", "main")
        project.write(f"src/beside-{branch}.txt", f"work beside {branch}\n")
        project.commit_all(f"work beside {branch}", trailers=("Task: work", "Role: engineer"))
        support.git(root, "merge", "-q", "--no-ff", "--no-gpg-sign", "-m",
                    f"Merge {branch}\n\nTask: work\nRole: engineer", branch)
    assert int(support.git(root, "rev-list", "--merges", "--count", "HEAD").strip()) >= SMALL_BLOCKS
    _with_core_authority(project)
    project.commit_all("declare core-authority")
    return project


def test_s1_merges_the_decision_checker_still_reports_an_agent_s_decision_merged_from_a_side_branch(small_history):
    """Guard: it passes on the base and must stay true when the checker is made faster over merges."""
    root = small_history.root
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(small_history.home),
           "LC_ALL": "C.UTF-8", "PYTHONPATH": str(support.SRC), "PYTHONPYCACHEPREFIX": str(small_history.home / "pycache")}
    done = subprocess.run([sys.executable, "-c", CHECKER_CODE, str(root)], cwd=str(root), env=env,
                          capture_output=True, text=True, timeout=300, stdin=subprocess.DEVNULL)
    assert done.returncode == 0, f"the decision checker did not run:\n{done.stderr}"
    found = json.loads(done.stdout)
    unapproved = sorted({number for finding in found if finding.get("code") == "ACTIVE_UNAPPROVED"
                         for number in re.findall(r"DEC-\d+", json.dumps(finding))})
    assert unapproved == ["DEC-901"], \
        f"ACTIVE_UNAPPROVED must name the engineer's DEC-901 and no other decision; the findings:\n{found}"


def test_s1_merges_core_authority_is_still_red_on_an_active_pair_merged_from_a_side_branch(small_history):
    """Guard: it passes on the base. ``core-authority`` carries the decision checker's findings, by code and message."""
    run = small_history.check()
    entry = run.entry(support.CORE_AUTHORITY)
    assert entry["status"] == support.RED, run.describe()
    named = [finding for finding in entry.get("findings", []) if "DEC-903" in json.dumps(finding)]
    assert named, f"no finding of core-authority names the decision superseded while ACTIVE\n{run.describe()}"
    assert not support.finding_codes(entry).count("CHECK_FAILED"), run.describe()
