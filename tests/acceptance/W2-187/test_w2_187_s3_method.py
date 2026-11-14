"""S3 and F4: the same method as Gov OS's memory (Interface I4).

A standing run uses the fresh 80's judged path unchanged: one code path, two modes. The suite shows it by a function spy (a
profile hook, ``fn_spy.py``) over the reader's, grader's, prompts' and matcher's modules in the ``judge`` child of a whole
standing run and of a whole fresh audit: every function the fresh judge calls, the standing judge calls too, with ``_Judge.one``
once per judged question; and by a source scan that names only modules and functions: nothing but ``prompts.py`` defines the
pinned prompts, schemas and cut, nothing but ``claude.py`` builds the model call, ``judge.py`` alone defines the reader.

Every search result carries ``result.store.commit`` (W2-138): one from another store makes the attempt a fault (``FAULT
attempt-<n>: store_commit``), one restart, then ``STOPPED fault`` (and the week may start once more, S2); a later search from
another commit is a counted search failure with an empty bundle (``why`` ``store``).

The searched store is the declared store (review round 1's F-A, the CTO's fix): with the repository's own store at another
commit than the store link's, a standing run's searches all run in the link's work tree and pass the store-commit check.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

import w2_187_world as W
from w2_187_world import S171, W171, W172

MEMAUDIT = W.SRC / "gov" / "memaudit"
BASE = "5336a6fca"


def judge_counts(world) -> dict:
    path = world.state / "fn_spy.jsonl"
    rows = [json.loads(x) for x in path.read_text().splitlines() if x.strip()] if path.exists() else []
    found = {}
    for row in rows:
        if row["argv"][1:4] == ["-m", "gov.memaudit", "judge"]:
            for name, count in row["counts"].items():
                found[name] = found.get(name, 0) + count
    return found


def test_s3_the_standing_judge_calls_every_function_the_fresh_judge_calls_one_reader_per_question(ran_std, ran_fresh):
    sworld, srun = ran_std("pass")
    fworld, frun = ran_fresh("not_yet")
    assert srun.code == 0 and frun.code == 0, (srun, frun)
    standing, fresh = judge_counts(sworld), judge_counts(fworld)
    assert fresh, "the spy saw the fresh judge"
    one = "gov.memaudit.judge._Judge.one"
    assert fresh[one] == 40 and standing[one] == 80, (fresh.get(one), standing.get(one))
    assert set(fresh) <= set(standing), f"the fresh judge calls what the standing judge does not: {sorted(set(fresh) - set(standing))}"
    for family in ("gov.memaudit.prompts.prompt_of", "gov.memaudit.claude.Caller.call"):
        assert fresh.get(family) and standing.get(family), family
    assert any(n.startswith("gov.memaudit.matcher.") for n in standing), "the measure's matcher is called"


def test_f4_the_pinned_prompts_schemas_and_cut_have_one_definition_and_the_reader_one_module():
    texts = {p.name: p.read_text(encoding="utf-8") for p in sorted(MEMAUDIT.glob("*.py"))}
    for marker, owner in (("READER_SYS =", "prompts.py"), ("GRADER_SYS =", "prompts.py"), ("def prompt_of", "prompts.py"),
                          ("def outcome(", "prompts.py"), ("def mcnemar(", "prompts.py"), ("class _Judge", "judge.py"),
                          ("--json-schema", "claude.py")):
        defining = sorted(name for name, text in texts.items() if marker in text)
        assert defining == [owner], f"{marker!r} is defined in {defining}, not in {owner} alone"


def test_f4_the_pinned_prompt_test_is_unchanged_and_passes():
    path = "tests/unit/memaudit/test_prompts.py"
    known = subprocess.run(["git", "-C", str(W.TREE), "cat-file", "-e", BASE], capture_output=True)
    if known.returncode == 0:
        same = subprocess.run(["git", "-C", str(W.TREE), "diff", "--quiet", BASE, "--", path, "src/gov/memaudit/prompts.py"])
        assert same.returncode == 0, "test_prompts.py and prompts.py are unchanged since the ticket's base"
    done = subprocess.run([sys.executable, "-m", "pytest", path, "-q", "-p", "no:cacheprovider"], cwd=W.TREE,
                          capture_output=True, text=True, env={"PYTHONPATH": str(W.SRC), "PATH": "/usr/bin:/bin",
                                                               "PYTHONDONTWRITEBYTECODE": "1"})
    assert done.returncode == 0, done.stdout[-600:]


def test_s3_a_later_search_from_another_store_commit_is_a_counted_failure_with_an_empty_bundle(ran_std):
    world, run = ran_std("pass")
    assert run.code == 0, run
    figures = world.std_json("FIGURES.json")
    assert figures["beside"]["search_failures"] == 1, figures["beside"]
    rows = {q: world.std_json(f"{q}.json", world.std_week / "reader") for q in ("q10", "q20", "q30")}
    assert rows["q10"]["searches"][0]["ok"] is False and rows["q10"]["searches"][0]["why"] == "store", rows["q10"]["searches"]
    assert all(rows[q]["searches"][0]["ok"] is True for q in ("q20", "q30"))
    assert figures["verdict"]["right"] == 80, "the failure is counted, the answer stands as the reader gave it"


def test_s3_a_result_from_another_store_commit_makes_the_attempt_a_fault_one_restart_then_stopped(make_world):
    world = make_world(std="pass")
    question = world.std_docs()["q05"]["question"]
    world.write_x_plan(other_commit={question: "e" * 40})
    run = world.standing_run()
    assert run.code == 2 and "STOPPED measure 2" in run.lines, run
    out = (world.std_state / "measure.out").read_text(encoding="utf-8")
    assert "FAULT attempt-1: store_commit" in out and "FAULT attempt-2: store_commit" in out, out
    assert (world.std_week / "attempt-1" / "FAULT").read_text().strip() == "store_commit"
    assert not (world.std_week / "COUNTS").exists() and (world.std_week / "STOPPED").is_file()
    assert not (world.std_week / "reader").exists(), "no reader run started"
    assert not (world.std_week / "FIGURES.json").exists()


def test_s2_s3_a_week_stopped_by_a_fault_may_start_once_more_and_then_never(make_world):
    world = make_world(std="pass")
    world.write_x_plan(other_commit={world.std_docs()["q05"]["question"]: "e" * 40})
    first = world.standing_run()
    assert first.code == 2, first
    second = world.standing_run()
    assert second.code == 2 and "STOPPED measure 2" in second.lines, "the week may start once more: " + repr(second)
    assert (world.std_runs / f"{world.week}.stopped" / "STOPPED").is_file(), "the first start's folder is kept"
    before = W.tree_state(world.sets, world.runs_env)
    third = world.standing_run()
    assert third.code == 3 and third.lines == ["USED"], third
    assert W.tree_state(world.sets, world.runs_env) == before


def test_s3_a_result_with_no_store_commit_is_a_fault(make_world):
    world = make_world(std="pass")
    world.write_x_plan(store_commit="")
    run = world.standing_run()
    assert run.code == 2, run
    assert "FAULT attempt-1: store_commit" in (world.std_state / "measure.out").read_text(encoding="utf-8")


# -- review round 1's F-A (the CTO's fix of 2026-11-14, DEC-1157 (12)): the searched store is the declared store ------------
def test_s3_every_search_of_a_standing_run_reaches_the_store_links_store_though_the_repositorys_own_is_at_another_commit(
        make_world):
    """The repository holds its own ``.gov-runtime/store.db`` built at another commit (the base commit) than the store link's
    (the audit commit), and the planted ``gov`` answers ``result.store.commit`` from the store of the folder it runs in, as the
    real one does. The ``preflight``, ``measure`` and ``judge`` children work in the link's work tree (I6), so every search
    reaches the link's store: no ``FAULT ... store_commit``, no ``STOPPED``, a verdict, and every logged search ran in the
    link's work tree, the declaration's ``store_commit`` being the link's."""
    world = make_world(std="pass")
    link_store = world.link_head()
    assert link_store == world.audit_commit != world.base_commit
    world.plant_repo_store(world.base_commit)
    world.write_x_plan(store_from="root")
    run = world.standing_run()
    measure_out = world.std_state / "measure.out"
    out = measure_out.read_text(encoding="utf-8") if measure_out.exists() else ""
    assert "store_commit" not in out, f"an attempt faulted on the store commit: {out[-600:]}"
    assert not (world.std_week / "STOPPED").exists(), run
    assert run.code == 0 and run.lines[-1] == f"STANDING {world.week} right 80 of 80: passes", run
    assert world.std_json("DECLARATION.json")["store_commit"] == link_store, "the declared store is the link's"
    roots = world.search_roots()
    link = os.path.realpath(world.link)
    assert len([s for s, _ in roots if s == "measure"]) >= 80, roots[:5]
    assert len([s for s, _ in roots if s == "judge"]) >= 3, "the three second searches (q10, q20, q30) are the judge's"
    assert {r for _, r in roots} == {link}, f"searches ran outside the link's work tree: {sorted({r for _, r in roots} - {link})}"
    assert world.std_json("FIGURES.json")["beside"]["search_failures"] == 0, "no later search came from another store"
