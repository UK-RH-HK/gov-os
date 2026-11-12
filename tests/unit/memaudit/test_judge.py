"""S3, S5, S6, S8, F1, F2: ``judge`` on a planted measured audit with a fake ``claude`` and a fake ``gov`` (never a real
model call, search or the real sets root)."""

from __future__ import annotations

import json
import re

from gov.memaudit import ledger, prompts, tables
from gov.memaudit.claude import argv_of

from .conftest import AUDIT, UNIQUE
from .fakes import FakeClaude, judge_args, measure_args, measured, prepare
from .test_measure import events, snapshot

FIGURE_KEYS = {"audit", "n", "n_gold", "bar", "verdict", "beside", "misses", "control", "pool", "classes", "spend"}
MISS_KEYS = ["id", "question", "gold_answer", "gold_sources", "answer", "outcome", "evidence_in_bundle"]


def plant_verdicts(claude):
    """Two wrong claims, two not found, one right answer citing no gold place, one answered only at the third attempt,
    one that needs the second: right 34 (A1 33, A3 35), wrong claims 2."""
    for qid in ("q03", "q07"):
        claude.script(qid, "wrong")
    for qid in ("q10", "q12"):
        claude.script(qid, "notfound")
    claude.script("q15", "uncited")
    claude.script("q20", "again")
    claude.script("q21", "late")
    claude.save()


def run_judge(plant, claude, *extra):
    return plant.cli(*judge_args(plant, claude, *extra))


def test_the_verdict_lines_show_the_planted_right_wrong_interval_and_the_bar(plant):
    fake, ranks, claude = measured(plant)
    plant_verdicts(claude)
    done = run_judge(plant, claude)
    assert done.returncode == 0, done.stdout
    out = done.stdout.splitlines()
    assert out[0].startswith("VERDICT ") and len(out) == 5  # the five lines of item 8, nothing before them
    verdict = [line for line in out if line.startswith(("VERDICT", "BAR", "BESIDE"))]
    assert verdict[0] == ("VERDICT right end to end 34 of 40 (85.0 %; exact 95 % interval 70.2 to 94.3 %); "
                          "wrong claims 2 of 40 (5.0 %)")
    assert verdict[1] == ("BAR at least 34 right (met) and at most 2 wrong claims (met): PASSES; "
                          "target at least 38: not reached")
    n_hit5 = sum(1 for qid, r in ranks.items() if qid != "q40" and r is not None and r <= 5)
    in_bundle = sum(1 for qid, r in ranks.items() if qid != "q40" and r is not None)
    assert verdict[2].startswith(f"BESIDE hit@5 {n_hit5} of 39 ({100 * n_hit5 / 39:.1f} %); in the first bundle "
                                 f"{in_bundle}; full evidence {in_bundle}; answer correct, citation aside ")
    assert verdict[2].endswith("answer correct, citation aside 35 of 40; not found 4")
    assert verdict[3] == "BESIDE one search against two: A1 right 33, A2 right 34: 1 gains, 0 losses, exact McNemar p 1.0000"
    assert re.fullmatch(r"BESIDE grader agreement \d+ of \d+; search failures 0; calls run once more 0; "
                        r"spent \d+\.\d\d USD \(projection 6\.28, brake 12\.56\)", verdict[4])
    assert len(verdict) == 5


def test_figures_json_holds_exactly_item_10s_keys_and_counts(plant):
    fake, ranks, claude = measured(plant)
    plant_verdicts(claude)
    assert run_judge(plant, claude).returncode == 0
    f = json.loads((plant.run_dir / "FIGURES.json").read_text())
    assert set(f) == FIGURE_KEYS and f["audit"] == AUDIT and f["n"] == 40 and f["n_gold"] == 39
    assert f["bar"] == {"need_right": 34, "max_wrong": 2, "target_right": 38}
    assert f["verdict"] == {"right": 34, "wrong": 2, "passes": True, "right_ok": True, "wrong_ok": True,
                            "target_ok": False, "interval_exact": [0.7016, 0.9429], "not_run": 0}
    b = f["beside"]
    assert set(b) == {"hit5", "hit10", "hit20", "mrr", "in_bundle", "full_evidence", "correct_citation_aside",
                      "not_found", "a1_right", "a3_right", "mcnemar_a1_a2", "grader_agree", "graded", "search_failures"}
    assert (b["a1_right"], b["a3_right"]) == (33, 35) and b["mcnemar_a1_a2"] == {"gains": 1, "losses": 0, "p": 1.0}
    assert b["correct_citation_aside"] == 35 and b["not_found"] == 4  # q15 is correct, citation aside; q21 not found at A2
    assert b["graded"] == 40 and b["grader_agree"] == 40 and b["search_failures"] == 0
    m = f["misses"]
    assert m["total"] == 6 and m["by_outcome"] == {"wrong": 2, "incomplete": 1, "not_found": 3}
    assert sum(m["by_rank"].values()) == 6 and set(m["by_rank"]) == {"rank_1_5", "rank_6_20", "not_in_20"}
    assert m["by_namespace"] == {"embedded": 6, "keyword_only": 0}
    assert set(m["by_category"]) == set(tables.QUOTAS) and sum(m["by_category"].values()) == 6
    assert set(m["by_route"]) == {"lexical", "semantic", "both", "other", "none"} and sum(m["by_route"].values()) == 6
    assert f["control"] == {"hit5": 34, "of": 40, "last": 34, "last_audit": None}
    assert f["pool"] is None and f["classes"] is None
    assert set(f["spend"]) == {"usd", "projection", "brake"} and f["spend"]["projection"] == 6.28
    assert f["spend"]["brake"] == 12.56 and f["spend"]["usd"] > 0
    assert "figures" in [e["event"] for e in events(plant)]


def test_misses_jsonl_has_one_line_a_miss_in_the_briefs_form_with_json_booleans(plant):
    fake, ranks, claude = measured(plant)
    plant_verdicts(claude)
    assert run_judge(plant, claude).returncode == 0
    rows = [json.loads(x) for x in (plant.run_dir / "misses.jsonl").read_text().splitlines()]
    assert [r["id"] for r in rows] == ["q03", "q07", "q10", "q12", "q15", "q21"]  # file-name order
    assert all(list(r) == MISS_KEYS for r in rows)
    by = {r["id"]: r for r in rows}
    assert {k: by[k]["outcome"] for k in by} == {"q03": "wrong", "q07": "wrong", "q10": "not_found", "q12": "not_found",
                                                  "q15": "incomplete", "q21": "not_found"}
    q = plant.questions["q03"]
    assert by["q03"]["question"] == q["question"] and by["q03"]["gold_answer"] == q["gold_answer"]
    assert by["q03"]["gold_sources"] == q["sources"] and by["q03"]["answer"] == "WRONG answer"
    assert by["q10"]["answer"] == "Not found." and by["q21"]["answer"] == "RIGHT answer"  # q21's third-attempt answer
    for r in rows:
        assert isinstance(r["evidence_in_bundle"], bool)
        assert r["evidence_in_bundle"] == (ranks[r["id"]] is not None)  # the measure's own in-the-bundle
    assert set(MISS_KEYS) == {"id", "question", "gold_answer", "gold_sources", "answer", "outcome", "evidence_in_bundle"}


def test_an_audit_with_no_miss_writes_an_empty_misses_file(plant):
    fake, ranks, claude = measured(plant)
    assert run_judge(plant, claude).returncode == 0
    assert (plant.run_dir / "misses.jsonl").read_text() == ""
    f = json.loads((plant.run_dir / "FIGURES.json").read_text())
    assert f["verdict"]["right"] == 40 and f["verdict"]["wrong"] == 0 and f["verdict"]["target_ok"] is True
    assert f["misses"]["total"] == 0


def test_a_verdict_below_the_bar_stands_is_never_run_again_and_misses_is_byte_identical(plant):
    fake, ranks, claude = measured(plant)
    for qid in ("q01", "q02", "q03"):
        claude.script(qid, "wrong")
    claude.save()
    done = run_judge(plant, claude)
    assert done.returncode == 0  # a miss is a result, not a refusal
    out = done.stdout.splitlines()
    assert any(line.startswith("BAR at least 34 right (met) and at most 2 wrong claims (NOT met): MISSES") for line in out)
    f = json.loads((plant.run_dir / "FIGURES.json").read_text())
    assert f["verdict"]["passes"] is False and f["verdict"]["wrong"] == 3
    before, calls = snapshot(plant.run_dir), len(claude.calls())
    misses = (plant.run_dir / "misses.jsonl").read_bytes()
    again = run_judge(plant, claude)
    assert again.returncode == 3 and again.stdout == "USED\n"
    assert snapshot(plant.run_dir) == before and (plant.run_dir / "misses.jsonl").read_bytes() == misses
    assert len(claude.calls()) == calls  # no model call
    assert plant.cli("measure", "--sets-root", str(plant.root), "--audit", AUDIT, "--repo", str(plant.repo["path"]),
                     "--commit", plant.repo["head"], "--store", str(plant.store), "--gov", str(plant.gov)).returncode == 3


def test_judge_without_a_counting_attempt_is_ms_nocount_exit_1(plant):
    prepare(plant)
    done = run_judge(plant, FakeClaude(plant))
    assert done.returncode == 1 and done.stdout == "MS-NOCOUNT\n"
    assert not (plant.run_dir / "reader").exists()


def test_a_gov_whose_pin_is_not_the_declarations_is_ms_pin(plant, tmp_path):
    fake, ranks, claude = measured(plant)
    other = tmp_path / "other/pin-ffffffffffff/bin"
    other.mkdir(parents=True)
    (other / "gov").write_text("#!/bin/sh\n")
    args = judge_args(plant, claude)
    args[args.index("--gov") + 1] = str(other / "gov")
    done = plant.cli(*args)
    assert done.returncode == 1 and done.stdout == "MS-PIN\n" and not (plant.run_dir / "reader").exists()


def test_a_set_changed_since_the_declaration_is_ms_digest(plant):
    fake, ranks, claude = measured(plant)
    (plant.hidden / "q01.yaml").write_text((plant.hidden / "q01.yaml").read_text() + "# edited\n")
    done = run_judge(plant, claude)
    assert done.returncode == 1 and done.stdout == "MS-DIGEST\n"


def test_a_question_without_a_measured_first_call_is_ms_firsts(plant):
    fake, ranks, claude = measured(plant)
    path = plant.run_dir / "attempt-1/measure.txt"
    path.write_text("\n".join(line for line in path.read_text().splitlines() if not line.startswith("q05 ")) + "\n")
    done = run_judge(plant, claude)
    assert done.returncode == 1 and done.stdout == "MS-FIRSTS\n"


def test_the_calls_are_the_fresh_80s_form_one_search_failure_is_counted_and_named(plant):
    fake, ranks, claude = measured(plant)
    claude.script("q20", "again")
    claude.save()
    fake.override("again words", 1, rerank_by="private")  # q20's later search is not answered as declared
    fake.save()
    done = run_judge(plant, claude)
    assert done.returncode == 0
    out = done.stdout.splitlines()
    assert out[-1] == "SEARCH FAILED 1: q20"
    later = [e for e in events(plant, "search") if e["phase"] == "later"]
    assert [(e["qid"], e["ok"], e["call"], e["attempt"]) for e in later] == [("q20", False, None, None)]
    f = json.loads((plant.run_dir / "FIGURES.json").read_text())
    assert f["beside"]["search_failures"] == 1
    # the reader got an empty bundle for it: it answered at attempt 2, the row says so
    row = json.loads((plant.run_dir / "reader/q20.json").read_text())
    assert row["kind"] == "audit" and row["search_failures"] == 1 and row["answered_at"] == 2
    assert row["searches"][0]["ok"] is False and row["gold_in_bundle"][1] is False


def test_each_call_is_the_fresh_80s_argv_with_no_tools_and_the_models_of_item_7(plant):
    fake, ranks, claude = measured(plant)
    assert run_judge(plant, claude).returncode == 0
    calls = claude.calls()
    assert {c["tools"] for c in calls} == {""} and {c["first"][0] for c in calls} == {"-p"}
    readers = [c for c in calls if not c["grader"]]
    graders = [c for c in calls if c["grader"]]
    assert {(c["model"], c["budget"]) for c in readers} == {("claude-opus-5-5", "1.5")}
    assert {(c["model"], c["budget"]) for c in graders} == {("claude-opus-5-5", "0.5"), ("claude-sonnet-5-5", "0.5")}
    assert len(readers) == 40 and len(graders) == 80
    argv = argv_of("claude", "claude-opus-5-5", prompts.READER_SYS, prompts.READER_SCHEMA, 1.5)
    assert argv[1:8] == ["-p", "--safe-mode", "--tools", "", "--no-session-persistence", "--output-format", "json"]
    assert argv[-2:] == ["--json-schema", json.dumps(prompts.READER_SCHEMA)] and "--effort" in argv


def test_a_call_that_returns_nothing_is_run_once_more_never_a_third_time(plant):
    fake, ranks, claude = measured(plant)
    claude.script("q04", "nothing")
    claude.save()
    assert run_judge(plant, claude).returncode == 0
    row = json.loads((plant.run_dir / "reader/q04.json").read_text())
    assert row["final_verdict"] == "error" and row["calls_retried"] == 1 and len(row["attempts"]) == 1
    assert len(claude.calls()) == 40 * 3 - 1  # q04: two reader calls and no grading, the others three each
    f = json.loads((plant.run_dir / "FIGURES.json").read_text())
    miss = [json.loads(x) for x in (plant.run_dir / "misses.jsonl").read_text().splitlines()]
    assert [m["id"] for m in miss] == ["q04"] and miss[0]["outcome"] == "not_found" and miss[0]["answer"] == ""
    assert f["verdict"]["right"] == 39


def test_the_second_grader_disagreeing_is_counted_beside_the_verdict(plant):
    fake, ranks, claude = measured(plant)
    claude.plan["rules"].insert(0, {"said": ["RIGHT"], "model": "claude-sonnet-5-5", "grade": "wrong"})
    claude.save()
    assert run_judge(plant, claude).returncode == 0
    f = json.loads((plant.run_dir / "FIGURES.json").read_text())
    assert f["beside"]["graded"] == 40 and f["beside"]["grader_agree"] == 1  # only the not-found nonexistent-id one agrees
    assert f["verdict"]["right"] == 40  # the named grader judges; the second is beside it


def test_the_misses_are_counted_by_rank_bucket_namespace_category_and_route(plant):
    q3 = dict(plant.questions["q03"], keyword=True)
    plant.put(q3)
    fake, _ = prepare(plant)
    spec = {"q03": (3, ["lexical"]), "q07": (8, ["semantic"]), "q10": (12, ["lexical", "semantic"]),
            "q12": (1, ["rerank"]), "q15": (None, ["lexical"]), "q21": (None, ["lexical"])}
    for qid, (rank, routes) in spec.items():
        fake.rank(plant.questions[qid], rank, routes=routes)
    fake.save()
    assert plant.cli(*measure_args(plant)).returncode == 0
    claude = FakeClaude(plant)
    plant_verdicts(claude)
    assert run_judge(plant, claude).returncode == 0
    m = json.loads((plant.run_dir / "FIGURES.json").read_text())["misses"]
    assert m["by_rank"] == {"rank_1_5": 2, "rank_6_20": 2, "not_in_20": 2}
    assert m["by_namespace"] == {"embedded": 5, "keyword_only": 1}
    assert m["by_route"] == {"lexical": 1, "semantic": 1, "both": 1, "other": 1, "none": 2}
    want = {c: 0 for c in tables.QUOTAS}
    for qid in ("q03", "q07", "q10", "q12", "q15", "q21"):
        want[plant.questions[qid]["category"]] += 1
    assert m["by_category"] == want
    rows = {json.loads(x)["id"]: json.loads(x) for x in (plant.run_dir / "misses.jsonl").read_text().splitlines()}
    assert [rows[i]["evidence_in_bundle"] for i in ("q03", "q15", "q21")] == [True, False, False]


# ---- F1: only ids, counts and digests leave

def test_a_unique_word_in_a_question_gold_answer_answer_and_path_is_found_nowhere_but_misses_and_reader(plant):
    q = dict(plant.questions["q05"])
    q.update(question=f"{UNIQUE['question']} what is stated in the planted file?", gold_answer=f"It says {UNIQUE['gold']}.",
             sources=[{"path": UNIQUE["path"], "heading": UNIQUE["heading"], "lines": [82, 82]}])
    plant.put(q)
    fake, _ = prepare(plant)
    measured_out = plant.cli(*measure_args(plant))
    assert measured_out.returncode == 0, measured_out.stdout
    claude = FakeClaude(plant)
    claude.plan["readers"][q["question"]] = {"steps": [{"verdict": "answer", "answer": "WRONG about zephyrbadger",
                                                       "citations": [], "search": ""}]}
    claude.save()
    done = run_judge(plant, claude)
    assert done.returncode == 0, done.stdout
    words = [UNIQUE["question"], UNIQUE["gold"], "fjordnarwhal", "zephyrbadger"]
    texts = {"stdout": done.stdout, "stderr": done.stderr, "measure stdout": measured_out.stdout,
             "measure stderr": measured_out.stderr}
    for p in plant.run_dir.rglob("*"):
        rel = p.relative_to(plant.run_dir)
        # misses.jsonl and the reader's rows are where they belong; the kept outputs are the retriever's own
        if not p.is_file() or p.name == "misses.jsonl" or "kept" in rel.parts or (
                rel.parts[0] == "reader" and p.suffix == ".json"):
            continue
        texts[str(rel)] = p.read_text(errors="replace")
    assert any(name.endswith("ledger.jsonl") for name in texts) and "FIGURES.json" in texts
    assert {(name, w) for name, text in texts.items() for w in words if w in text} == set()
    miss = (plant.run_dir / "misses.jsonl").read_text()
    assert UNIQUE["question"] in miss and UNIQUE["gold"] in miss and "zephyrbadger" in miss and "fjordnarwhal" in miss
    assert "zephyrbadger" in (plant.run_dir / "reader/q05.json").read_text()


# ---- S8: spend, the brake and the resume

def spends(plant):
    return [e for e in events(plant, "spend")]


def test_every_calls_cost_is_a_spend_event_with_the_runs_running_total(plant):
    fake, ranks, claude = measured(plant)
    claude.plan["cost"] = 0.02
    claude.save()
    assert run_judge(plant, claude).returncode == 0
    sp = spends(plant)
    assert len(sp) == 120 and {e["call"] for e in sp} == {"reader-1", "grader", "check"}
    assert all(e["usd"] == 0.02 for e in sp)
    totals = [e["total"] for e in sp]
    assert totals == sorted(totals) and abs(totals[-1] - 2.4) < 1e-6
    f = json.loads((plant.run_dir / "FIGURES.json").read_text())
    assert abs(f["spend"]["usd"] - 2.4) < 1e-6
    assert [e["seq"] for e in ledger.read(plant.run_dir)] == list(range(1, len(ledger.read(plant.run_dir)) + 1))


def stop_for_brake(plant, claude):
    claude.plan["cost"] = 0.2  # a question is 3 calls: 0.6; the brake at --projection 1.0 is 2.0
    claude.plan["sleep"] = 0.05
    claude.save()
    return run_judge(plant, claude, "--projection", "1.0")


def test_the_run_stops_at_twice_its_projection_to_the_owner_and_writes_no_misses_or_figures(plant):
    fake, ranks, claude = measured(plant)
    done = stop_for_brake(plant, claude)
    assert done.returncode == 2 and done.stdout.splitlines()[-1] == "STOPPED brake"
    assert (plant.run_dir / "STOPPED").read_text() == "brake\n"
    assert not (plant.run_dir / "misses.jsonl").exists() and not (plant.run_dir / "FIGURES.json").exists()
    rows = [p for p in (plant.run_dir / "reader").glob("q*.json")]
    assert 0 < len(rows) < 40
    assert events(plant, "stopped")[-1]["cause"] == "brake"
    assert spends(plant)[-1]["total"] > 2.0


def test_a_stopped_run_resumes_asking_only_the_unfinished_questions_from_the_ledger_total(plant):
    fake, ranks, claude = measured(plant)
    assert stop_for_brake(plant, claude).returncode == 2
    done_before = {p.name for p in (plant.run_dir / "reader").glob("q*.json")}
    total_before = spends(plant)[-1]["total"]
    readers_before = sum(1 for c in claude.calls() if not c["grader"])
    stale = (plant.run_dir / "reader/q01.json").read_bytes()
    claude.plan["cost"] = 0.01
    claude.plan["sleep"] = 0
    claude.save()
    done = run_judge(plant, claude, "--resume", "--projection", "20")
    assert done.returncode == 0, done.stdout
    assert (plant.run_dir / "STOPPED-1").read_text() == "brake\n" and not (plant.run_dir / "STOPPED").exists()
    assert sum(1 for c in claude.calls() if not c["grader"]) - readers_before == 40 - len(done_before)
    assert (plant.run_dir / "reader/q01.json").read_bytes() == stale  # a finished question's row is kept
    assert spends(plant)[-1]["total"] > total_before  # it starts from the ledger's total
    first_new = next(e for e in spends(plant) if e["total"] > total_before)
    assert abs(first_new["total"] - (total_before + first_new["usd"])) < 1e-6
    f = json.loads((plant.run_dir / "FIGURES.json").read_text())
    assert f["n"] == 40 and f["spend"]["projection"] == 20 and f["spend"]["brake"] == 40
    assert len(list((plant.run_dir / "reader").glob("q*.json"))) == 40


def test_resume_needs_a_raised_projection_and_a_brake_stop_else_it_is_refused(plant):
    fake, ranks, claude = measured(plant)
    assert stop_for_brake(plant, claude).returncode == 2
    before = snapshot(plant.run_dir)
    for extra in (["--resume"], ["--resume", "--projection", "1.0"], ["--resume", "--projection", "0.5"]):
        done = run_judge(plant, claude, *extra)
        assert done.returncode == 4 and done.stdout == "ERROR: UsageError\n"
    assert snapshot(plant.run_dir) == before
    assert run_judge(plant, claude).returncode == 3  # without --resume: the stopped run stands
    assert run_judge(plant, claude, "--projection", "20").returncode == 3


def test_resume_is_refused_with_exit_3_when_nothing_was_stopped_by_the_brake(plant):
    fake, ranks, claude = measured(plant)
    assert run_judge(plant, claude, "--resume", "--projection", "20").returncode == 3  # nothing to resume
    assert run_judge(plant, claude).returncode == 0
    assert run_judge(plant, claude, "--resume", "--projection", "20").returncode == 3  # figures exist


def test_the_default_projection_is_0_157_a_question_and_the_flag_overrides_it(plant):
    fake, ranks, claude = measured(plant)
    assert run_judge(plant, claude, "--projection", "9.5").returncode == 0
    f = json.loads((plant.run_dir / "FIGURES.json").read_text())
    assert f["spend"]["projection"] == 9.5 and f["spend"]["brake"] == 19.0


def test_judge_answers_with_the_wrapper_never_used_for_later_searches_and_no_search_before_used(plant):
    fake, ranks, claude = measured(plant)
    claude.script("q20", "again")
    claude.save()
    assert run_judge(plant, claude).returncode == 0
    ev = events(plant)
    idx = [e["event"] for e in ev]
    assert idx.index("used") < idx.index("search")
    later = [c for c in fake.calls() if c["q"] == "again words"]
    assert len(later) == 1 and later[0]["role"] == "orchestrator" and later[0]["store"] is None
    assert later[0]["ticket"] is None


def test_a_flag_inside_the_sets_root_is_refused(plant):
    fake, ranks, claude = measured(plant)
    args = judge_args(plant, claude)
    args[args.index("--claude") + 1] = str(plant.root / "claude")
    done = plant.cli(*args)
    assert done.returncode == 4 and done.stdout == "ERROR: UsageError\n"


def test_a_planted_ledger_over_the_brake_stops_before_any_call_and_resume_starts_from_its_total(plant):
    from gov.memaudit import events as ledger_events
    fake, ranks, claude = measured(plant)
    ledger_events.append(plant.run_dir, "spend", call="reader-1", qid="q01", usd=20.0, total=20.0)
    done = run_judge(plant, claude, "--projection", "5")  # the brake is 10, the run's total already 20
    assert done.returncode == 2 and done.stdout.splitlines()[-1] == "STOPPED brake" and claude.calls() == []
    assert not (plant.run_dir / "misses.jsonl").exists() and not (plant.run_dir / "FIGURES.json").exists()
    (plant.run_dir / "reader/plan.json").unlink()  # the figure the stopped run began on is not recorded: the default
    done = run_judge(plant, claude, "--resume", "--projection", "50")
    assert done.returncode == 0, done.stdout
    sp = [e for e in events(plant, "spend") if e["call"] != "reader-1" or e["qid"] != "q01" or e["usd"] != 20.0]
    assert abs(sp[0]["total"] - 20.01) < 1e-6 and len(claude.calls()) == 120
