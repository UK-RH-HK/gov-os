"""S5 and F2: a miss is a result (Interface 9, 11; S5's and F2's Verify).

A verdict below either limit stands as recorded, is never run again and never re-scored to pass. ``judge`` writes
``runs/<audit>/misses.jsonl``, one line per miss (a question not right end to end at A2) with exactly the keys of item 9
in order; an audit with no miss writes an empty file; the file is the auditor brief's input form (parsed by the brief's
own field list, ``governance/project/indep-briefs/memory-audit/auditor.md`` section 2). A second ``measure`` or ``judge``
on the same audit is refused (exit 3, printed ``USED``), writing nothing: ``misses.jsonl`` is byte-identical.
"""

from __future__ import annotations

import json
import re

import w2_171_scenario as S
import w2_171_world as W

BRIEF = W.TREE / "governance" / "project" / "indep-briefs" / "memory-audit" / "auditor.md"
KEYS = ["id", "question", "gold_answer", "gold_sources", "answer", "outcome", "evidence_in_bundle"]


def brief_fields() -> list[str]:
    """The auditor brief's own field list for ``input/misses.jsonl`` (its section 2)."""
    text = BRIEF.read_text(encoding="utf-8")
    section = text.split("## 2. Your folder and your tree", 1)[1].split("\n## ", 1)[0]
    line = re.search(r"`(\{\"id\"[^`]*\})`", section)
    assert line, "the brief's field list was not found"
    return re.findall(r'"(\w+)"', line.group(1))


def read_misses(world) -> list[tuple[list[str], dict]]:
    """Each line as ``(its top-level keys in file order, the object)``."""
    text = (world.run_dir / "misses.jsonl").read_text(encoding="utf-8")
    assert text == "" or text.endswith("\n")
    return [([k for k, _ in json.loads(x, object_pairs_hook=list)], json.loads(x)) for x in text.splitlines()]


def test_s5_the_briefs_field_list_is_the_one_the_interface_names():
    assert brief_fields() == KEYS


def test_s5_five_misses_are_five_lines_in_the_auditor_briefs_form(make_world):
    world = make_world("judged:five")
    expected = S.Expected(S.SCENARIOS["five"], world).misses()
    assert [m["id"] for m in expected] == ["q03", "q19", "q25", "q28", "q33"]
    lines = read_misses(world)
    assert len(lines) == 5, lines
    fields = brief_fields()
    for (order, got), want in zip(lines, expected):
        assert order == KEYS == fields, "exactly these keys, in this order"
        assert got["id"] == want["id"] and got["outcome"] == want["outcome"], got["id"]
        assert got["question"] == want["question"] and got["gold_answer"] == want["gold_answer"]
        assert got["gold_sources"] == want["gold_sources"], "the question's sources exactly as parsed from its YAML"
        assert got["answer"] == want["answer"], (got["id"], got["answer"])
        assert got["evidence_in_bundle"] is want["evidence_in_bundle"], "the JSON true or false, not yes or no"
        assert got["outcome"] in ("wrong", "incomplete", "not_found")
    outcomes = {got["id"]: got["outcome"] for _, got in lines}
    assert outcomes == {"q03": "wrong", "q19": "incomplete", "q25": "not_found", "q28": "not_found",
                        "q33": "not_found"}
    assert {got["id"]: got["evidence_in_bundle"] for _, got in lines} == {
        "q03": True, "q19": True, "q25": False, "q28": False, "q33": False}, \
        "the measure's own answer on whether a gold place was in the first bundle"


def test_s5_misses_are_written_whole_before_the_figures(make_world):
    world = make_world("judged:five")
    assert (world.run_dir / "misses.jsonl").stat().st_mtime_ns <= (world.run_dir / "FIGURES.json").stat().st_mtime_ns
    assert not [p for p in world.run_dir.rglob("*") if p.name.endswith(".tmp")], "written by temporary name, renamed"


def test_s5_an_audit_with_no_miss_writes_an_empty_file(make_world):
    world = make_world("judged:clean")
    path = world.run_dir / "misses.jsonl"
    assert path.is_file() and path.stat().st_size == 0
    assert world.json_of("FIGURES.json")["misses"]["total"] == 0


def test_s5_a_verdict_below_the_bar_stands_as_recorded_and_is_a_result(make_world):
    world = make_world("judged:below")
    assert world.staged["judge"]["code"] == 0, "a miss is a result: exit 0, FIGURES.json written"
    out = world.staged["judge"]["out"].splitlines()
    assert any(x.startswith("BAR at least 34 right (NOT met)") and ": MISSES;" in x for x in out), out
    figures = world.json_of("FIGURES.json")
    assert figures["verdict"]["right"] == 33 and figures["verdict"]["passes"] is False
    assert figures["verdict"]["right_ok"] is False and figures["verdict"]["wrong_ok"] is True
    ids = [got["id"] for _, got in read_misses(world)]
    assert ids == sorted(["q03", "q19", "q25", "q28", "q33", "q10", "q15"]), ids
    before = {p: p.read_bytes() for p in (world.run_dir / "misses.jsonl", world.run_dir / "FIGURES.json")}
    snap, calls = W.snapshot(world.sets), (len(world.gov_calls()), len(world.claude_calls()))
    for args in (("judge",), ("judge", "--resume", "--projection", "99")):
        run = world.judge(*args[1:])
        assert run.code == 3 and "USED" in run.lines, (args, run)
    assert {p: p.read_bytes() for p in before} == before
    assert W.snapshot(world.sets) == snap and (len(world.gov_calls()), len(world.claude_calls())) == calls


def test_f2_a_second_measure_or_judge_is_refused_and_writes_nothing(make_world):
    world = make_world("judged:five")
    misses = (world.run_dir / "misses.jsonl").read_bytes()
    snap, calls = W.snapshot(world.sets), (len(world.gov_calls()), len(world.claude_calls()))
    for run in (world.measure(), world.judge(), world.judge("--resume", "--projection", "99")):
        assert run.code == 3 and "USED" in run.lines, run
    assert (world.run_dir / "misses.jsonl").read_bytes() == misses
    assert W.snapshot(world.sets) == snap, "a refused run wrote something"
    assert (len(world.gov_calls()), len(world.claude_calls())) == calls, "a refused run searched or asked the models"


def test_f2_a_second_measure_over_a_measured_audit_is_refused_by_used(make_world):
    world = make_world("measured:five")
    snap, calls = W.snapshot(world.sets), len(world.gov_calls())
    run = world.measure()
    assert run.code == 3 and "USED" in run.lines, run
    assert W.snapshot(world.sets) == snap and len(world.gov_calls()) == calls
    assert not list(world.run_dir.glob("attempt-2")) and not list(world.run_dir.glob("control-2"))


def test_f2_a_label_changed_after_its_figures_exist_is_refused(make_world):
    world = make_world("judged:five")
    path = world.hidden / "q05.yaml"
    path.write_bytes(path.read_bytes() + b"# a label changed after its figures exist\n")
    snap = W.snapshot(world.run_dir)
    run = world.judge()      # two refusals hold at once (figures exist, the digest moved): the tool's order decides
    assert (run.code, "USED" in run.lines, "MS-DIGEST" in run.lines) in ((3, True, False), (1, False, True)), run
    run = world.pool_run()
    assert run.code == 1 and "MS-DIGEST" in run.lines, run
    assert not (world.run_dir / "POOL.json").exists()
    assert W.snapshot(world.run_dir) == snap
