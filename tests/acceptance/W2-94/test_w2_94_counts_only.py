"""W2-94, the counts-only rule of S4 -- the script prints only counts and ids, never a question, an answer, a heading or
a path, not even in an error.

S4: "a counts-only script ... prints only counts and ids". This is S3's planted-word check applied to the script: every
planted question, answer, heading and source path holds the word ``zqxw94``, and every case of every table (the good
sets, the refused ones, the reported ones, the unreadable ones) must print nothing but lines of four fixed shapes
(``N questions (V visible, H hidden); draw ok|FAIL; release ok|FAIL|pending``, ``n of N hold``, ``FAIL <id|draw|release|
set> <CODE> [<id or k>]``, ``REFUSED <CODE> [<id>]``), nothing on stderr, and none of the planted words.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_94_cases as c  # noqa: E402
import w2_94_support as s  # noqa: E402

TABLES = {"s1-form": c.S1_FORM, "s1-draw": c.S1_DRAW, "s1-release": c.S1_RELEASE, "s4": c.S4_BREAKS,
          "s4-nonexistent": c.NONEXISTENT_BREAKS, "fail-closed": c.FAIL_CLOSED}
CASES = sorted((table, name) for table, entries in TABLES.items() for name in entries)


def _count(table):
    return 20 if table.startswith("s4") else 10


@pytest.mark.parametrize("table,name", CASES, ids=[f"{t}:{n}" for t, n in CASES])
def test_the_output_of_every_planted_case_is_counts_and_ids_only(tmp_path, table, name):
    build_kwargs, case, rc = TABLES[table][name]
    world = s.build(tmp_path, count=_count(table), **build_kwargs)
    _, kwargs = case(world)
    run = s.run_check(world, **kwargs)
    assert run.returncode == rc, run.describe()
    assert run.stdout.strip(), "a run says something"
    assert s.shape_faults(run) == [], f"{table}:{name}: output outside the four shapes: {s.shape_faults(run)}"
    assert s.planted_hits(run, world) == [], f"{table}:{name}: planted text shown: {s.planted_hits(run, world)}\n{run.describe()}"


@pytest.mark.parametrize("count", [10, 13, 20])
def test_the_output_of_a_good_set_is_two_lines_of_counts(tmp_path, count):
    world = s.build(tmp_path, count=count)
    run = s.run_check(world)
    assert run.returncode == 0 and len(run.lines) == 2, run.describe()
    assert s.shape_faults(run) == [] and s.planted_hits(run, world) == [], run.describe()


def test_the_planted_words_are_in_every_planted_question_answer_heading_and_path(tmp_path):
    """The check's own premise: each planted question file carries the word the other cases look for."""
    world = s.build(tmp_path, count=20)
    for qid in sorted(world.cats):
        data = world.load(qid)
        assert s.WORD in data["question"], qid
        if world.cats[qid] != "nonexistent":
            assert s.WORD in data["gold_answer"] and s.WORD in data["sources"][0]["heading"], qid
        assert s.WORD in data["sources"][0]["path"], qid


def test_an_internal_exception_prints_a_reason_code_and_no_text_of_the_set(tmp_path):
    """Fail closed: the program is run with one of its own functions made to raise an exception whose message holds a
    planted word; it exits non-zero with ``REFUSED INTERNAL_ERROR`` and nothing else."""
    import subprocess

    world = s.build(tmp_path, count=10)
    driver = (
        "import importlib.util, sys\n"
        f"spec = importlib.util.spec_from_file_location('check_gold_under_test', {str(s.SCRIPT)!r})\n"
        "module = importlib.util.module_from_spec(spec)\n"
        "spec.loader.exec_module(module)\n"
        f"def boom(*args, **kwargs):\n    raise ValueError('{s.WORD} a question text')\n"
        "module.judge_question = boom\n"
        f"sys.exit(module.main(['--sets-root', {str(world.root)!r}, '--copy', {str(world.copy)!r}]))\n"
    )
    env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "HOME": str(world.home),
           **{k: v for k, v in os.environ.items() if k in ("PYTHONUSERBASE", "PYTHONPATH")}}
    done = subprocess.run([sys.executable, "-c", driver], capture_output=True, text=True, timeout=s.TIMEOUT_S,
                          cwd=str(world.base), env=env)
    assert done.returncode == 3, (done.returncode, done.stdout, done.stderr)
    assert done.stdout.strip() == "REFUSED INTERNAL_ERROR", done.stdout
    assert done.stderr.strip() == "", done.stderr
