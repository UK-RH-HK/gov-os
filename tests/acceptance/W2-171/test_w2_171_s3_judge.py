"""S3: the judged reader run (Interface 1, 7, 8, 11 and the row form of 3).

The reader answers each question from its searches with search again once (A2); a named grader judges right end to end
with a second grader's agreement beside it; the prompts are the fresh 80's, pinned by hash (item 7); the verdict, bar and
beside lines are printed as item 8 gives them. ``judge`` runs on the counting attempt's kept outputs, and the readers
and graders are the planted ``claude`` (``--claude``): called as the fresh 80 calls it, one JSON on standard output.

Readings taken where the Interface leaves a choice (named in the README and the return's ``unresolved``):

* ``answer correct, citation aside <d> of <n>`` and ``not found <e>`` count over all ``n`` = 40 questions, the
  nonexistent-id question included (its ``outcome`` branch: not found is right), the same population as every other
  "of <n>" on these lines;
* ``calls run once more <k>`` counts the reader and grader calls that returned nothing and were run once more;
* ``spent`` is the sum of every model call's ``total_cost_usd`` (read here from the planted ``claude``'s own log).
"""

from __future__ import annotations

import hashlib
import importlib
import inspect
import json

import pytest

import w2_171_scenario as S
import w2_171_world as W

PINNED = {
    "READER_SYS": "a0e222af4a0f9a6ca2cb8e31dd44dc7c21e684c5a0de0e0d081947eacef85e08",
    "READER_SCHEMA": "216897d1c451e34033fafd75d1f6be408b0f82dacd5ff885dcad37351c578e5d",
    "GRADER_SYS": "58d1ad87b24064b28bb09c498a9915f66f0867ffa1e09565f59fd33c7e2ac6d4",
    "GRADER_SCHEMA": "7bfc5786b59231cb7576cdbeeef713ca3524e18205189f73c598ac323c8370a8",
    "grader prompt": "c12bc5ee7fe303c4e83d6c8803683e2697b1e2f595ecd382e771e61ead15879e",
    "prompt_of": "4a8c1c65619d7111c6dbdc7aae8de6164306ea0366d9410f8ea5095a04fb8c42",
    "items_of": "38cb4b5de225235759064e88027287fd8de4c1fa48e24007e1e573d048aa19f1",
    "outcome": "41a930d83aa170bb33e703b7daa39d6f9f489db9767c52a152cd1cae23899f13",
    "mcnemar": "48e0099533762dd0b2df6f80e7b1f42c0ae214de94d76ea13964cfbe641557d7",
}
GRADER_FORM = "Question: {question}\n\nGold answer: {gold}\n\nAnswer to grade: {said}"
ROW_KEYS = {"id", "kind", "apart", "final_verdict", "attempts", "answered_at", "gold_in_bundle", "citation_right",
            "grades", "searches", "search_failures", "citations", "citations_outside",
            "citation_right_only_outside", "calls_retried", "first_stopping_reason", "first_gaps_name_ids"}


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def flag(argv, name):
    return argv[argv.index(name) + 1]


def spent_of(world) -> float:
    return sum(c["usd"] for c in world.claude_calls())


def fake_result(world, words: str) -> dict:
    """What the planted gov answers for ``words`` (the later searches' bundles), asked once more here."""
    done = W.subprocess.run([str(world.gov), "retrieve", words, "--json"], capture_output=True, text=True,
                            env=W.child_env(world.home, world.env()), timeout=60)
    return json.loads(done.stdout)["result"]


def items(result):
    return [(e["path"], int(e["start_line"]), int(e["end_line"]), str(e.get("text", ""))) for e in result["evidence"]]


def prompt_of(question, bundles) -> str:
    """The fresh 80's ``prompt_of`` (pinned by hash in item 7), restated from its text."""
    parts = [f"Question: {question}"]
    for k, b in enumerate(bundles, 1):
        parts.append(f"\n=== Bundle {k} ===")
        for path, a, z, text in b:
            parts.append(f"--- {path} lines {a}-{z}\n{text}")
    return "\n".join(parts)


def first_bundle(world, qid):
    """The counting attempt's first call's evidence for ``qid``, from its kept outputs."""
    number = 1
    for q, _part, *_ in world.question_lines(world.attempt_dir(1)):
        rank = S.SCENARIOS["five"].ranks[q]
        if q == qid:
            return items(json.loads((world.attempt_dir(1) / "kept" / f"{number:05d}.json").read_text())["result"])
        number += 1 if rank is None or rank <= 10 else (2 if rank <= 20 else 3)
    raise AssertionError(qid)


@pytest.mark.parametrize("name", ["five", "clean", "below", "five37"])
def test_s3_the_verdict_bar_and_beside_lines_are_printed_as_item_8_gives_them(make_world, name):
    world = make_world(f"judged:{name}")
    expected = S.Expected(S.SCENARIOS[name], world).verdict_lines(spent=spent_of(world))
    out = world.staged["judge"]["out"].splitlines()
    for line in expected:
        assert line in out, (line, [x for x in out if x.startswith(("VERDICT", "BAR", "BESIDE"))])
    positions = [out.index(line) for line in expected]
    assert positions == sorted(positions), "the lines come in item 8's order"
    right, wrong = S.Expected(S.SCENARIOS[name], world).right_wrong()
    assert (right, wrong) == {"five": (35, 2), "clean": (40, 0), "below": (33, 2), "five37": (33, 1)}[name]
    assert ("PASSES" in expected[1]) == (name != "below")


def test_s3_the_verdict_names_the_scaled_bar_34_and_2_with_target_38(make_world):
    world = make_world("judged:five")
    out = world.staged["judge"]["out"]
    assert "BAR at least 34 right (met) and at most 2 wrong claims (met): PASSES; target at least 38: not reached" in out
    assert "exact 95 % interval 73.2 to 95.8 %" in out and "right end to end 35 of 40 (87.5 %" in out


def test_s3_the_scaled_bar_for_a_set_of_37_is_32_right_1_wrong_target_36(make_world):
    """The bar scales with n (ceil(0.85 n) right, floor(0.05 n) wrong claims, target ceil(0.95 n)): a set of 37 after the
    checker's drops has its bar at 32, 1 and 36; ``n`` is 37 on every line and in the figures, the apart question inside."""
    world = make_world("judged:five37")
    out = world.staged["judge"]["out"]
    assert "BAR at least 32 right (met) and at most 1 wrong claims (met): PASSES; target at least 36: not reached" in out
    assert "right end to end 33 of 37 (89.2 %" in out and "wrong claims 1 of 37 (2.7 %)" in out
    figures = world.json_of("FIGURES.json")
    assert (figures["n"], figures["n_gold"], figures["bar"]) == (37, 36, {"need_right": 32, "max_wrong": 1,
                                                                          "target_right": 36})
    assert world.json_of("DECLARATION.json")["n"] == 37
    assert not [p for p in world.hidden.glob("q*.yaml") if p.stem in ("q27", "q33", "q34")]


def test_s3_the_pinned_prompts_are_the_fresh_80s_by_hash():
    """Item 7: ``gov.memaudit.prompts`` holds the strings, schemas and functions copied verbatim; each is recomputed
    as the item says (UTF-8 text; a schema as ``json.dumps(schema)``; a function as its source text from ``def`` to its
    last line, no final newline) and compared with the list."""
    prompts = importlib.import_module("gov.memaudit.prompts")
    assert prompts.__file__.startswith(str(W.SRC) + "/"), prompts.__file__
    got = {}
    for name in ("READER_SYS", "GRADER_SYS"):
        got[name] = sha(getattr(prompts, name))
    for name in ("READER_SCHEMA", "GRADER_SCHEMA"):
        got[name] = sha(json.dumps(getattr(prompts, name)))
    for name in ("prompt_of", "items_of", "outcome", "mcnemar"):
        got[name] = sha(inspect.getsource(getattr(prompts, name)).rstrip("\n"))
    assert sha(GRADER_FORM) == PINNED["grader prompt"], "the test's own copy of the grader's prompt form"
    for name, digest in got.items():
        assert digest == PINNED[name], name
    assert prompts.CAP == 3


def test_s3_the_calls_carry_the_fresh_80s_prompts_models_budgets_and_flags(make_world):
    world = make_world("judged:five")
    calls = world.claude_calls()
    assert {c["kind"] for c in calls} == {"reader", "grader", "check"}
    want = {"reader": ("claude-opus-5-5", "1.5", PINNED["READER_SYS"], PINNED["READER_SCHEMA"]),
            "grader": ("claude-opus-5-5", "0.5", PINNED["GRADER_SYS"], PINNED["GRADER_SCHEMA"]),
            "check": ("claude-sonnet-5-5", "0.5", PINNED["GRADER_SYS"], PINNED["GRADER_SCHEMA"])}
    for call in calls:
        argv = call["argv"]
        model, budget, system, schema = want[call["kind"]]
        assert argv[0] == "-p" and "--safe-mode" in argv and "--no-session-persistence" in argv, argv[:6]
        assert flag(argv, "--tools") == "" and flag(argv, "--output-format") == "json"
        assert flag(argv, "--effort") == "high" and flag(argv, "--model") == model
        assert flag(argv, "--max-budget-usd") == budget, (call["kind"], argv)
        assert sha(flag(argv, "--system-prompt")) == system and sha(flag(argv, "--json-schema")) == schema


def test_s3_the_reader_prompts_hold_the_kept_first_bundle_then_each_later_bundle(make_world):
    world = make_world("judged:five")
    docs = world.docs()
    reader = {}
    for call in world.claude_calls():
        if call["kind"] == "reader":
            reader.setdefault(call["qid"], []).append(call)
    q = lambda qid: docs[qid]["question"]  # noqa: E731
    # an answer at the first search
    assert reader["q01"][0]["prompt"] == prompt_of(q("q01"), [first_bundle(world, "q01")])
    # search again once, the later search answered: a second bundle
    later = items(fake_result(world, S.search_words("q04")))
    assert reader["q04"][1]["prompt"] == prompt_of(q("q04"), [first_bundle(world, "q04"), later])
    # a later search that failed gives an empty bundle
    assert reader["q02"][1]["prompt"] == prompt_of(q("q02"), [first_bundle(world, "q02"), []])
    # the cap: the third call holds three bundles and is the last
    assert len(reader["q33"]) == 3
    assert reader["q33"][2]["prompt"] == prompt_of(q("q33"), [first_bundle(world, "q33"), later_for(world, "q33"),
                                                            later_for(world, "q33")])
    # a call that returned nothing is run once more with the same prompt
    assert [c["empty"] for c in reader["q08"]] == [True, False]
    assert reader["q08"][0]["prompt"] == reader["q08"][1]["prompt"]


def later_for(world, qid):
    return items(fake_result(world, S.search_words(qid)))


def test_s3_the_graders_are_shown_the_question_the_gold_answer_and_the_answer_in_the_fresh_80s_form(make_world):
    world = make_world("judged:five")
    docs, sc = world.docs(), S.SCENARIOS["five"]
    grading = {}
    for call in world.claude_calls():
        if call["kind"] in ("grader", "check"):
            grading.setdefault(call["qid"], {})[call["kind"]] = call
    assert set(grading) == set(docs), "every question is graded by both"
    for qid, calls in grading.items():
        said = sc.answer_text(qid) if sc.row(qid)["final_verdict"] == "answer" else "Not found."
        want = GRADER_FORM.format(question=docs[qid]["question"], gold=docs[qid]["gold_answer"], said=said)
        assert calls["grader"]["prompt"] == want and calls["check"]["prompt"] == want, qid


def test_s3_the_reader_is_run_three_times_at_most_and_a_call_without_output_once_more(make_world):
    five, below = make_world("judged:five"), make_world("judged:below")
    count = lambda w, qid: [c for c in w.claude_calls() if c["qid"] == qid and c["kind"] == "reader"]  # noqa: E731
    assert len(count(five, "q33")) == 3, "the cap is 3 attempts"
    assert [e["qid"] for e in five.events("search", phase="later")].count("q33") == 2, \
        "no search follows the third reader call"
    assert len(count(five, "q08")) == 2 and five.staged["judge"]["code"] == 0
    assert len(count(below, "q15")) == 2, "a call that returns nothing is run once more, never a third time"
    assert len(count(below, "q10")) == 3, "A3: answered at the third attempt"


def test_s3_a_failed_later_search_is_counted_named_by_id_and_is_not_an_attempt_fault(make_world):
    world = make_world("judged:five")
    later = world.events("search", phase="later")
    assert sorted(e["qid"] for e in later) == ["q02", "q04", "q31", "q33", "q33"], later
    assert all(e["call"] is None and e["rc"] == 0 for e in later), later
    out = world.staged["judge"]["out"]
    assert any("q02" in line for line in out.splitlines()), "the failed search is named by id on standard output"
    assert not list(world.run_dir.glob("attempt-*/FAULT")) and not (world.run_dir / "STOPPED").exists()
    assert "search failures 1;" in out


def test_s3_each_question_has_a_row_in_the_fresh_80s_form(make_world):
    world = make_world("judged:five")
    sc = S.SCENARIOS["five"]
    folder = world.run_dir / "reader"
    assert (folder / "plan.json").is_file()
    rows = {p.stem: json.loads(p.read_text()) for p in folder.glob("q*.json")}
    assert sorted(rows) == [f"q{i:02d}" for i in range(1, 41)]
    for qid, row in rows.items():
        assert set(row) == ROW_KEYS, (qid, sorted(set(row) ^ ROW_KEYS))
        assert row["id"] == qid and row["kind"] == "audit" and row["apart"] is (qid == W.NONEXISTENT)
        planted = sc.row(qid)
        assert row["final_verdict"] == planted["final_verdict"] and row["answered_at"] == planted["answered_at"], qid
        assert len(row["attempts"]) == planted["attempts"], qid
        assert row["citation_right"] is planted["citation_right"] or qid == W.NONEXISTENT, qid
        assert {k: v["grade"] for k, v in row["grades"].items()} == {"grader": planted["grade"], "check": planted["check"]}
        assert row["first_stopping_reason"] == ("UNRESOLVED_IDS" if qid == W.NONEXISTENT else "BUDGET")
        assert row["first_gaps_name_ids"] is (True if qid == W.NONEXISTENT else None), qid
    assert rows["q08"]["calls_retried"] == 1 and rows["q02"]["search_failures"] == 1


def test_s3_four_workers_and_ledger_lines_that_never_interleave(make_world):
    world = make_world("measured:five")
    sc = S.Scenario("five-slow", sleep=0.15, **{k: getattr(S.SCENARIOS["five"], k) for k in (
        "behaviour", "ranks", "routes", "disagree", "retried", "later_fail", "control_hits")})
    sc.install(world)
    run = world.judge()
    assert run.code == 0, run
    spans = sorted((c["t0"], c["t1"]) for c in world.claude_calls())
    peak = max(sum(1 for a, b in spans if a <= t0 < b) for t0, _ in spans)
    assert 2 <= peak <= 4, f"four workers: at most four calls at a time, more than one at a time (saw {peak})"
    raw = (world.run_dir / "ledger.jsonl").read_text().splitlines()
    parsed = [json.loads(x) for x in raw]       # every line one whole JSON object
    assert [e["seq"] for e in parsed] == list(range(1, len(parsed) + 1)), "seq consecutive, none twice"


def test_s3_judge_refuses_a_run_that_has_no_counting_attempt(world):
    """``MS-NOCOUNT``: ``declare`` (W2-170) has run, no attempt counts."""
    S.SCENARIOS["five"].install(world)
    assert world.declare().code == 0
    run = world.judge()
    assert run.code == 1 and "MS-NOCOUNT" in run.lines, run
    assert not (world.run_dir / "reader").exists() and not (world.run_dir / "FIGURES.json").exists()
    assert world.claude_calls() == []


def test_s3_judge_refuses_a_gov_whose_pin_is_not_the_declared_one(make_world):
    world = make_world("measured:five")
    before = W.snapshot(world.sets)
    run = world.judge(gov=world.gov_other)
    assert run.code == 1 and "MS-PIN" in run.lines, run
    assert W.snapshot(world.sets) == before and world.claude_calls() == []


def test_s3_judge_refuses_a_set_whose_digest_moved(make_world):
    world = make_world("measured:five")
    path = world.hidden / "q05.yaml"
    path.write_bytes(path.read_bytes() + b"# a label changed after the declaration\n")
    before = W.snapshot(world.sets)
    run = world.judge()
    assert run.code == 1 and "MS-DIGEST" in run.lines, run
    assert W.snapshot(world.sets) == before and world.claude_calls() == []


def test_s3_judge_refuses_a_question_without_a_measured_first_call(make_world):
    world = make_world("measured:five")
    path = world.attempt_dir(1) / "measure.txt"
    path.write_text("".join(x for x in path.read_text().splitlines(keepends=True) if not x.startswith("q05 ")))
    run = world.judge()
    assert run.code == 1 and "MS-FIRSTS" in run.lines, run
    assert not (world.run_dir / "reader").exists() and not (world.run_dir / "FIGURES.json").exists()
    assert world.claude_calls() == []
