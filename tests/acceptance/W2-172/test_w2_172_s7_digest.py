"""S7 and F2: the digest block (Interface items 4, 6, 7) of three whole planted audits.

After an audit the driver writes ``<R>/<A>/DIGEST.txt`` whole and prints it: exactly 12 lines in order (the audit name and
commit; the mode and why; the verdict line; hit@5 and gold in the first bundle; the misses by class, rank bucket and
namespace; the pool beside the last audit's; the retrieval paths changed; the questions kept and dropped by code; the cost
per step; the next due date; the stop line; the owner line), counts and ids only. The schema is ``w2_172_digest`` (one
regular expression a line, written from item 7). The figures are checked against W2-171's oracle (``Expected``), the files
the children wrote (``DROPS.json``, ``FIGURES.json``) and git; the three runs cover a set of 40 with revisions and a pool
regression (``words``), a clean set with no miss (``clean``), and a set of 37 with the scaled bar and no earlier pool
(``five37``).

F2: a planted question word, gold answer, answer and source path (W2-171's ``UNIQUE`` words: the question holds one, the gold
answer one, the gold path ``docs/contract/<word>.md`` one, the reader's answer one) never reach the digest, standard
output or error, or any file of the runs folder (item 4: counts, codes, ids, hashes and repository paths only).

Readings: the exact interval is printed in percent (``exact 64.4 to 90.9 %``): compared to the oracle within 0.06 points,
whatever its decimals; ``COST`` lists the launch steps (the counts' ``session.cost_usd``, 0.25 each here) and ``judge``
(the ``spent <usd> USD`` of its own line); the other steps may be listed at 0.00.
"""

from __future__ import annotations

import fnmatch
import json
import re

import pytest

import w2_172_world as W
from w2_172_checks import assert_ok
from w2_172_digest import by_word, cost_steps
from w2_172_world import S171, W171

RUNS = ["words", "clean", "five37"]
LAUNCH_STEPS = {"words": ["writer-1", "checker-1", "writer-2", "checker-2", "auditor"],
                "clean": ["writer-1", "checker-1", "auditor"],
                "five37": ["writer-1", "checker-1", "writer-2", "checker-2", "auditor"]}


def oracle(name, world):
    return S171.Expected(S171.SCENARIOS[name], world)


@pytest.mark.parametrize("name", RUNS)
def test_s7_the_digest_is_twelve_lines_in_order_each_matching_its_form_and_is_printed(ran, name):
    world, run = ran(name)
    assert_ok(run)
    lines = world.digest()
    by_word(lines, strict=True)
    assert run.lines[-12:] == lines, "the block is printed line by line, as written"
    before = run.out.splitlines()[:-12]
    assert before and all(x.startswith("STEP ") for x in before), "nothing else is printed before it"
    assert (world.audit_dir / "DIGEST.txt").read_text().endswith("\n")
    assert not [p for p in world.audit_dir.iterdir() if p.name.startswith(".") and "DIGEST" in p.name], \
        "written whole by rename: no temporary file is left"


@pytest.mark.parametrize("name", RUNS)
def test_s7_the_audit_the_mode_the_verdict_and_the_retrieval_figures(ran, name):
    world, run = ran(name)
    assert_ok(run)
    d = by_word(world.digest())
    exp = oracle(name, world)
    assert d["AUDIT"].group(0) == f"AUDIT {world.audit} commit {world.audit_commit[:12]}"
    assert d["MODE"].group(0) == "MODE weekly reason start", "no measured line yet: weekly from the start"
    right, wrong = exp.right_wrong()
    bar = W171.bar(exp.n)
    lo, hi = S171.exact_interval(right, exp.n)
    v = d["VERDICT"]
    assert (int(v["right"]), int(v["n"]), int(v["wrong"])) == (right, exp.n, wrong)
    assert abs(float(v["lo"]) - 100 * lo) <= 0.06 and abs(float(v["hi"]) - 100 * hi) <= 0.06, v.group(0)
    assert (int(v["need"]), int(v["max"])) == (bar["need_right"], bar["max_wrong"])
    assert v["word"] == ("passes" if right >= bar["need_right"] and wrong <= bar["max_wrong"] else "misses")
    e = exp.retrieval()
    h = d["HIT5"]
    assert (int(h["a"]), int(h["ng"]), int(h["b"])) == (e["hit5"], e["ng"], e["in_bundle"]), h.group(0)


def test_s7_a_set_of_37_prints_the_scaled_bar(ran):
    world, run = ran("five37")
    assert_ok(run)
    v = by_word(world.digest())["VERDICT"]
    assert (v["n"], v["need"], v["max"]) == ("37", "32", "1"), v.group(0)


@pytest.mark.parametrize("name", RUNS)
def test_s7_the_misses_by_class_rank_bucket_and_namespace(ran, name):
    world, run = ran(name)
    assert_ok(run)
    exp = oracle(name, world)
    misses = exp.misses()
    ids = sorted(m["id"] for m in misses)
    classes = {c: 0 for c in W.CLASSES}
    for k, _ in enumerate(ids):
        classes[W.CLASSES[k % 5]] += 1  # the planted auditor assigns the five classes in turn over the sorted ids
    fig = exp.figures(spent=0.0)["misses"]
    m = by_word(world.digest())["MISSES"]
    assert {c: int(m[c]) for c in W.CLASSES} == classes, m.group(0)
    assert (int(m["r15"]), int(m["r620"]), int(m["rnone"])) == (
        fig["by_rank"]["rank_1_5"], fig["by_rank"]["rank_6_20"], fig["by_rank"]["not_in_20"]), m.group(0)
    assert (int(m["embedded"]), int(m["keyword_only"])) == (fig["by_namespace"]["embedded"],
                                                           fig["by_namespace"]["keyword_only"]), m.group(0)
    if name == "clean":
        assert not misses and set(m.groupdict().values()) == {"0"}, m.group(0)
    else:
        assert sum(classes.values()) == len(misses) > 0


@pytest.mark.parametrize("name,last,regression", [("words", (2, 2), "yes"), ("clean", (0, 0), "no"),
                                                  ("five37", None, "no")])
def test_s7_the_pool_beside_the_last_audits_and_any_regression(ran, name, last, regression):
    world, run = ran(name)
    assert_ok(run)
    pool = world.figures()["pool"]
    p = by_word(world.digest())["POOL"]
    assert (int(p["hit5"]), int(p["n"]), int(p["full"])) == (pool["hit5"], pool["n"], pool["full"]), p.group(0)
    want = ("none", "none") if last is None else (str(last[0]), str(last[1]))
    assert (p["last_hit5"], p["last_full"]) == want, p.group(0)
    assert p["regression"] == regression
    assert world.history()[-1]["pool_regression"] is (regression == "yes")


@pytest.mark.parametrize("name", RUNS)
def test_s7_the_retrieval_paths_changed_since_the_last_audit_come_from_git(ran, name):
    world, run = ran(name)
    assert_ok(run)
    diff = world.git_out("diff", "--name-only", world.base_commit, world.audit_commit).split()
    want = sorted(p for p in diff if any(fnmatch.fnmatchcase(p, g.replace("**", "*")) for g in W.GLOBS))
    assert want, "the planted history changes retrieval paths between the last audit and the audit commit"
    r = by_word(world.digest())["RETRIEVAL"]
    assert int(r["k"]) == len(want)
    assert sorted((r["paths"] or "").split()) == want, r.group(0)


@pytest.mark.parametrize("name,kept,dropped,codes", [("words", 40, 0, {}), ("clean", 40, 0, {}),
                                                    ("five37", 37, 3, {"R1-WRONG": 3})])
def test_s7_the_questions_kept_and_dropped_by_code(ran, name, kept, dropped, codes):
    world, run = ran(name)
    assert_ok(run)
    q = by_word(world.digest())["QUESTIONS"]
    assert (int(q["kept"]), int(q["dropped"])) == (kept, dropped)
    assert {c: int(n) for c, n in re.findall(r"([A-Z][A-Z0-9-]*) (\d+)", q["codes"])} == codes, q.group(0)
    drops = json.loads((world.run_dir / "DROPS.json").read_text())
    assert (drops["kept"], drops["dropped"], drops["by_code"]) == (kept, dropped, codes)


@pytest.mark.parametrize("name", RUNS)
def test_s7_the_cost_per_step_in_usd(ran, name):
    world, run = ran(name)
    assert_ok(run)
    c = by_word(world.digest())["COST"]
    steps = cost_steps(c)
    for step in LAUNCH_STEPS[name]:
        assert steps.get(step) == 0.25, (step, c.group(0))
    spent = re.search(r"spent (\d+\.\d\d) USD", (world.audit_dir / "judge.out").read_text())
    assert spent and steps.get("judge") == float(spent[1]) > 0, c.group(0)
    assert all(v == 0.0 for k, v in steps.items() if k not in LAUNCH_STEPS[name] + ["judge"]), c.group(0)
    assert float(c["total"]) == pytest.approx(sum(steps.values()), abs=0.0051)
    counts_cost = world.counts()["cost"]
    for step, usd in steps.items():
        assert counts_cost[step] == pytest.approx(usd, abs=0.006)


@pytest.mark.parametrize("name", RUNS)
def test_s7_the_next_due_date_and_the_closing_lines(ran, name):
    world, run = ran(name)
    assert_ok(run)
    d = by_word(world.digest())
    assert d["NEXT"].group(0) == "NEXT due 2026-11-16 weekly", "6 days after this audit's start, weekly"
    assert d["STOP"].group(0) == "STOP none" and d["OWNER"].group(0) == "OWNER none"


@pytest.mark.parametrize("name", RUNS)
def test_s7_the_counts_the_history_and_the_start_of_a_whole_audit(ran, name):
    world, run = ran(name)
    assert_ok(run)
    counts = world.counts()
    assert counts["audit"] == world.audit and counts["commit"] == world.audit_commit
    assert counts["force"] is False and counts["mode"] == "weekly" and counts["stop"] is None
    assert counts.get("refused") in (None, False)
    names = [s["step"] for s in counts["steps"]]
    assert names == [s for s in W.STEPS if not (name == "clean" and s in ("writer-2", "checker-2"))], names
    assert all(s["exit"] == 0 and s["retried"] is False for s in counts["steps"]), counts["steps"]
    exp = oracle(name, world)
    right, wrong = exp.right_wrong()
    bar = W171.bar(exp.n)
    history = world.history()
    assert len(history) == 1
    h = history[0]
    assert set(h) == {"audit", "commit", "at", "mode", "churn", "retrieval_28d", "passes", "pool_regression", "measured",
                      "used"}, h
    assert (h["audit"], h["commit"], h["mode"], h["measured"], h["used"]) == (world.audit, world.audit_commit,
                                                                              "weekly", True, True)
    assert h["passes"] is (right >= bar["need_right"] and wrong <= bar["max_wrong"])
    assert h["retrieval_28d"] is True, "retrieval paths changed inside the 28 days before the audit commit"
    assert h["churn"] == 1.0, "every tracked path is in the history of the 28 days before the audit commit"
    starts = world.starts()
    assert len(starts) == 1 and starts[0]["audit"] == world.audit and starts[0]["commit"] == world.audit_commit


# -- F2 ----------------------------------------------------------------------------------------------------------------
def test_f2_no_question_gold_answer_answer_or_source_path_reaches_the_digest_the_output_or_a_log(ran):
    world, run = ran("words")
    assert_ok(run)
    words = [w.encode() for w in W171.UNIQUE]
    planted = {"question": (world.delivery / "hidden" / "q07.yaml").read_bytes(),
               "answers": (world.run_dir / "misses.jsonl").read_bytes()}
    assert W171.QWORD.encode() in planted["question"] and W171.GWORD.encode() in planted["question"]
    assert W171.PWORD.encode() in planted["question"] and W171.AWORD.encode() in planted["answers"], \
        "the words are really planted: the question, its gold answer, its gold path and the reader's answer"
    assert W171.QWORD.encode() in planted["answers"] and W171.GWORD.encode() in planted["answers"]
    targets = {"stdout": run.out.encode(), "stderr": run.err.encode()}
    for path in sorted(world.runs.rglob("*")):
        if path.is_file():
            targets[str(path.relative_to(world.runs))] = path.read_bytes() + path.name.encode()
    assert "indep/memaudit/%s/DIGEST.txt" % world.audit in targets
    for where, data in targets.items():
        for word in words:
            assert word not in data, f"{word.decode()} found in {where}"
