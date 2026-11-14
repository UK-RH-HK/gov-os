"""F2, F3, F5 and the scope of the branch.

F2: a standing set is never judged without ``DECLARATION.json`` and ``USED`` first, never re-scored (``measure --kept`` on a
standing set, with or without ``--week``, prints ``USED`` and exits 3 writing nothing), and its digest is checked equal before
any search (``STANDING_DIGEST``, exit 1, nothing written, the week not spent); ``STANDING_NONE`` and ``STANDING_RETIRED``
refuse a run too. F3: a standing run offers no way to choose, adopt or reject a fix: it has no ``--decision``, ``--force`` or
data flag (argparse's exit 4), the tool has no command that compares two configurations or commits, and a nonstandard
``retrieval.yaml`` is a refusal (``DC-DECISION``, the week not used) with no way to allow it. F5: a fresh set's use-once
behaviour is unchanged (``declare`` of a measured fresh audit is ``USED``, exit 3, nothing written). The scope case judges the
branch ``w2/W2-187`` only and skips elsewhere.
"""

from __future__ import annotations

import fnmatch
import re
import subprocess

import pytest

import w2_187_world as W
from w2_187_world import W171

BUSY = {"GOV_MEMAUDIT_GATE_MAX_S": "0", "GOV_MEMAUDIT_GATE_POLL_S": "0"}
ALLOWED = [
    "src/gov/memaudit/**", "src/gov/adopt/memory_sets.py", "governance/project/orchestration/tools/memaudit_cron.sh",
    "tests/unit/memaudit/**", "tests/unit/adopt/test_w2_187*", "tests/acceptance/W2-170/test_w2_170_s3_declare.py",
    "tests/acceptance/W2-170/w2_170_world.py", "tests/acceptance/W2-171/test_w2_171_s3_judge.py",
    "tests/acceptance/W2-171/w2_171_world.py", "tests/acceptance/W2-171/w2_171_scenario.py",
    "tests/acceptance/W2-172/test_w2_172_s7_digest.py", "docs/changes/W2-187-evidence.md", "docs/probes/DAEO-0cd2/**",
    "tests/acceptance/W2-187/**", "tests/acceptance/W2-172/w2_172_world.py", "tests/acceptance/W2-172/w2_172_git.py",
]


def state(world):
    return W.tree_state(world.sets, world.runs_env)


# -- F2 -------------------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("with_week", [True, False])
def test_f2_measure_kept_on_a_standing_set_is_used_exit_3_and_writes_nothing(copy_std, with_week):
    world = copy_std("pass")
    before = state(world)
    extra = ["--week", world.week] if with_week else []
    run = world.drive("measure", "--sets-root", str(world.sets), "--audit", W.STD, *extra, "--repo", str(world.repo),
                      "--kept", "1")
    assert run.code == 3 and run.lines == ["USED"], run
    assert state(world) == before


@pytest.mark.parametrize("edit", ["gold_answer", "question"])
def test_f2_an_edit_of_the_set_after_the_declaration_is_refused_before_any_search_and_the_week_is_not_spent(make_world, edit):
    world = make_world(std="pass")
    path = world.std_hidden / "q05.yaml"
    path.write_text(path.read_text(encoding="utf-8").replace(f"{edit}: ", f"{edit}: an edit that changes the label of ", 1),
                    encoding="utf-8")
    before = state(world)
    run = world.standing_run()
    assert run.code == 1 and "STANDING_DIGEST" in run.lines, run
    assert state(world) == before, "nothing is written"
    assert world.searches() == [] and world.claude_calls() == []
    assert not (world.std_week / "USED").exists()


def test_f2_a_run_with_no_declared_set_or_a_retired_one_is_refused_and_writes_nothing(make_world):
    world = make_world()
    before = state(world)
    none = world.standing_run()
    assert none.code == 1 and "STANDING_NONE" in none.lines, none
    assert state(world) == before
    world.plant_standing(world.standing_record(), {"event": "retired", "set": W.STD, "reason": "fitted", "at": "2026-11-09"})
    before = state(world)
    gone = world.standing_run()
    assert gone.code == 1 and "STANDING_RETIRED" in gone.lines, gone
    assert state(world) == before and world.searches() == []


# -- F3 -------------------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("flag", [["--decision", "DEC-1"], ["--force"], ["--projection", "1.0"], ["--commit", "HEAD"],
                                  ["--kept", "1"], ["--audit", "memory-audit-20261101"], ["--runs-dir", "x"]])
def test_f3_a_standing_run_takes_no_decision_force_or_data_flag(make_world, flag):
    world = make_world(std="pass")
    assert world.drive("standing", "run", "--help").code == 0, "the subcommand exists"
    before = state(world)
    run = world.standing_run(extra=flag)
    assert run.code == 4, run
    assert state(world) == before and world.searches() == [] and world.stub_calls() == []


def test_f3_the_tool_offers_no_command_that_compares_two_configurations_or_two_commits(make_world):
    world = make_world()
    words = set()
    for args in (["--help"], ["standing", "--help"], ["standing", "run", "--help"], ["maintain", "--help"]):
        run = world.drive(*args)
        assert run.code == 0, (args, run)
        words |= set(re.findall(r"[a-z][a-z-]+", run.out.lower()))
    assert {"standing", "maintain", "declare", "live"} <= words
    assert not words & {"compare", "diff", "versus", "contrast", "bisect"}, words & {"compare", "diff", "versus"}


def test_f3_a_nonstandard_retrieval_yaml_is_a_refusal_with_no_way_to_allow_it(make_world):
    world = make_world(std="pass")
    commit = world.repo_commit("2026-11-10T06:00:00+00:00",
                               {"governance/project/retrieval.yaml": "# nonstandard\npool:\n  meaning_uncut: false\n"}, "off")
    world.relink(commit)
    run = world.standing_run()
    assert run.code == 2 and "STOPPED measure 1" in run.lines, run
    assert not (world.std_week / "USED").exists(), "a refusal before USED does not spend the week"
    assert world.searches() == []
    assert "DC-DECISION" in (world.std_state / "measure.out").read_text(encoding="utf-8")
    allowed = world.standing_run(extra=["--decision", "DEC-1"])
    assert allowed.code == 4, "there is no flag that allows it"


# -- F5 -------------------------------------------------------------------------------------------------------------------
def test_f5_a_measured_fresh_set_stays_used_declare_is_exit_3_and_writes_nothing(copy_fresh):
    world = copy_fresh("not_yet")
    before = W.tree_state(world.sets, world.runs_env)
    run = world.drive("declare", "--sets-root", str(world.sets), "--audit", world.audit, "--repo", str(world.repo), "--commit",
                      world.audit_commit, "--store", str(world.link / ".gov-runtime" / "store.db"), "--gov", str(world.gov))
    assert run.code == 3 and run.lines == ["USED"], run
    assert W.tree_state(world.sets, world.runs_env) == before


# -- the scope --------------------------------------------------------------------------------------------------------------
def test_scope_the_branch_changes_only_the_tickets_allowed_paths_and_its_acceptance_folder():
    """Judges the branch ``w2/W2-187`` only (the engineer's); it skips on any other branch or where ``w2/integrate`` is absent."""
    git = lambda *a: subprocess.run(["git", "-C", str(W.TREE), *a], capture_output=True, text=True)  # noqa: E731
    branch = git("rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    if branch != "w2/W2-187" or git("rev-parse", "--verify", "--quiet", "w2/integrate").returncode != 0:
        pytest.skip(f"judges the branch w2/W2-187 only (this is {branch})")
    base = git("merge-base", "HEAD", "w2/integrate").stdout.strip()
    changed = [p for p in git("diff", "--name-only", f"{base}...HEAD").stdout.splitlines() if p]
    stray = [p for p in changed if not any(fnmatch.fnmatchcase(p, g) for g in ALLOWED)]
    assert stray == [], f"changed outside the ticket's allowed paths: {stray}"
