"""S4 and F1: counts only (Interface I2, I4, I12).

A standing run with five planted misses (each question, gold answer, source path, reader answer and citation holds a unique
word; the five ids are word-matched) writes no ``misses.jsonl`` and launches no auditor. The unique words and the five ids
are absent from standard output and error, from ``FIGURES.json`` and ``HISTORY.jsonl``, from the digest block (stdout and
``DIGEST.txt``), from every file under the key folder and the runs folder, and from every file under the sets root other than
the set itself and its own run folder (the files the run wrote, never the set it read). Before the grep means anything, every
path of the world that can appear on a printed line is checked to hold none of the words. What does leave the run folder is
counts: right end to end, wrong claims, not found, the misses by outcome and by the first gold place's rank in the first
bundle (1-5, 6-20, absent), the questions dropped, hit@5, gold in the first bundle, A1 against A2 with exact McNemar.

``classes``, ``pool`` and ``pool-import --sets`` refuse a standing set (``MS-STANDING``, exit 1): no code path hands a standing
run's rows to the auditor's classes or the pool.
"""

from __future__ import annotations

import json
import os
import re
import stat

import w2_187_world as W
from w2_187_world import W171

ID_RX = re.compile(r"(?<![A-Za-z0-9_])q(?:03|19|25|28|33)(?![A-Za-z0-9_])")
DIGEST_FORMS = {
    "STANDING": r"STANDING {set} week {week} commit [0-9a-f]{{12}}",
    "VERDICT": r"VERDICT right (\d+) of (\d+); wrong (\d+); not found (\d+); bar (\d+) right: (passes|misses)",
    "MISSES": r"MISSES outcome wrong (\d+) incomplete (\d+) not_found (\d+); rank 1-5 (\d+) 6-20 (\d+) absent (\d+)",
    "QUESTIONS": r"QUESTIONS live (\d+) of (\d+); dropped (\d+)",
    "BESIDE": r"BESIDE hit5 (\d+) of (\d+); first bundle (\d+); A1 (\d+) A2 (\d+): (\d+) gains (\d+) losses, "
              r"exact McNemar p ([0-9.]+)",
    "P1": r"P1 memory below 95 %: wrong (\d+) incomplete (\d+) not_found (\d+)",
    "REPAIR": r"REPAIR (open|none)",
    "NEXT": r"NEXT standing \d{4}-\d{2}-\d{2} (weekly|monthly); fresh \d{4}-\d{2}-\d{2}",
}


def match(lines: list[str], word: str, world=None):
    form = DIGEST_FORMS[word]
    if world is not None:
        form = form.format(set=W.STD, week=world.week)
    line = W.digest_line(lines, word)
    assert line is not None, f"no {word} line in {lines}"
    m = re.fullmatch(form, line)
    assert m, f"the {word} line does not fit I12: {line!r}"
    return m


def text_of(path) -> str:
    return path.read_bytes().decode("utf-8", "replace")


def written_texts(world, run):
    yield "stdout", run.out
    yield "stderr", run.err
    for path in world.scan_targets(world.runs_env):
        yield str(path.relative_to(world.base)), text_of(path)
    own = (world.std_set_dir, world.std_runs)
    for path in world.scan_targets(world.sets):
        if not any(parent in own for parent in path.parents):
            yield str(path.relative_to(world.base)), text_of(path)


def test_s4_the_planted_words_and_ids_leave_no_file_and_no_printed_line(ran_std):
    world, run = ran_std("five")
    assert run.code == 0, run
    for path in (world.base, world.sets, world.repo, world.link, world.runs_env, world.stub, world.gov, world.claude):
        assert not W.hits(str(path) + "/", W.UNIQUE), f"{path}: a planted word in a path that may be printed"
    for where, text in written_texts(world, run):
        assert W.hits(text, W.UNIQUE) == [], f"{where} holds a planted word"
        assert not ID_RX.search(text), f"{where} holds a planted question id"
    assert any(W.hits(text_of(p), W.UNIQUE) for p in world.std_hidden.glob("*.yaml")), "the grep means something: the set holds them"
    assert any(W.hits(text_of(p), W.UNIQUE) for p in (world.std_week / "reader").glob("*.json")), \
        "the run folder itself may hold them (the reader's rows)"


def test_s4_a_standing_run_writes_no_misses_file_and_launches_no_auditor(ran_std):
    world, run = ran_std("five")
    assert run.code == 0, run
    for root in (world.sets, world.runs_env):
        assert not list(root.rglob("misses.jsonl")) and not list(root.rglob("miss-classes.json")), root
    assert world.stub_calls() == [], "no launch of any kind"
    assert not [e for e in world.std_ledger() if "auditor" in json.dumps(e)]
    spawned = [classify_step(e["arg"]) for e in world.spy()
               if e["argv"][1:5] == ["-m", "gov.memaudit", "standing", "run"] and e["kind"] == "popen"]
    assert [s for s in spawned if s] == ["preflight", "measure", "judge", "figures"], spawned


def classify_step(args):
    return args[3] if args[1:3] == ["-m", "gov.memaudit"] else None


def test_s4_the_counts_in_figures_json_and_the_verdict_are_the_oracles(ran_std):
    world, run = ran_std("five")
    assert run.code == 0, run
    exp = W.StdExpected(world.sc)
    assert (exp.right, exp.wrong, exp.n) == (75, 2, 80), "the planted scenario: right = need_right - 1"
    fig = world.std_json("FIGURES.json")
    assert (fig["n"], fig["verdict"]["right"], fig["verdict"]["wrong"], fig["verdict"]["passes"]) == (80, 75, 2, False)
    assert fig["bar"] == {"need_right": 76, "max_wrong": 4, "target_right": 76}
    assert (fig["beside"]["hit5"], fig["beside"]["in_bundle"], fig["beside"]["not_found"]) == (exp.hit5, exp.in_bundle, exp.nf)
    assert fig["misses"]["by_outcome"] == exp.by_outcome and fig["misses"]["by_rank"] == exp.by_rank
    assert (fig["beside"]["a1_right"], fig["beside"]["mcnemar_a1_a2"]["gains"]) == (exp.a1, exp.gains)
    assert run.lines[-1] == f"STANDING {world.week} right 75 of 80: misses", run.lines[-2:]


def test_s4_the_digest_block_is_printed_as_written_and_holds_each_figure_as_counts(ran_std):
    world, run = ran_std("five")
    assert run.code == 0, run
    block = world.std_digest_lines()
    assert run.lines[-1 - len(block):-1] == block, "the block is printed line by line, as written"
    exp = W.StdExpected(world.sc)
    match(block, "STANDING", world)
    v = match(block, "VERDICT")
    assert tuple(map(int, v.groups()[:5])) == (75, 80, 2, exp.nf, 76) and v[6] == "misses", v.group(0)
    m = match(block, "MISSES")
    assert tuple(map(int, m.groups())) == (exp.by_outcome["wrong"], exp.by_outcome["incomplete"], exp.by_outcome["not_found"],
                                           exp.by_rank["rank_1_5"], exp.by_rank["rank_6_20"], exp.by_rank["not_in_20"])
    assert tuple(map(int, match(block, "QUESTIONS").groups())) == (80, 80, 0)
    b = match(block, "BESIDE")
    assert tuple(map(int, b.groups()[:7])) == (exp.hit5, 79, exp.in_bundle, exp.a1, 75, exp.gains, exp.losses)
    assert abs(float(b[8]) - exp.p) < 0.001
    p1 = match(block, "P1")
    assert tuple(map(int, p1.groups())) == (exp.by_outcome["wrong"], exp.by_outcome["incomplete"], exp.by_outcome["not_found"])
    match(block, "REPAIR")
    match(block, "NEXT")
    assert W.digest_line(block, "STOP") and W.digest_line(block, "OWNER")
    order = [next(i for i, x in enumerate(block) if x == w or x.startswith(w + " "))
             for w in ("STANDING", "VERDICT", "MISSES", "QUESTIONS", "BESIDE", "P1", "REPAIR", "NEXT", "STOP", "OWNER")]
    assert order == sorted(order), f"I12's order: {order}"


def test_s4_the_run_folder_is_mode_0700_and_the_runs_folder_of_the_set_holds_only_it(ran_std):
    world, run = ran_std("five")
    assert run.code == 0, run
    assert stat.S_IMODE(os.stat(world.std_week).st_mode) == 0o700
    assert sorted(p.name for p in world.std_runs.iterdir()) == [world.week], "everything the run wrote is in its week folder"


def test_f1_classes_and_pool_and_pool_import_refuse_a_standing_set(make_world):
    world = make_world(standing=True)
    pool = world.sets / "fixtures" / "evaluation" / "memory-pool" / "hidden"
    before = W.tree_state(pool, world.sets / "runs")
    for args in (("classes", "--sets-root", str(world.sets), "--audit", W.STD),
                 ("pool", "--sets-root", str(world.sets), "--audit", W.STD, "--repo", str(world.repo), "--gov", str(world.gov)),
                 ("pool-import", "--sets-root", str(world.sets), "--sets", W.STD)):
        run = world.drive(*args)
        assert run.code == 1 and "MS-STANDING" in run.lines, (args[0], run)
    assert W.tree_state(pool, world.sets / "runs") == before
