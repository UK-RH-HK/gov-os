"""S8: the spend is bounded and recorded (Interface 3, 11; S8's Verify: planted ledger over the brake: stops; resume asks
only the unfinished).

Each model call's ``total_cost_usd`` is a ``spend`` event of the audit's ``ledger.jsonl`` (``call``: ``reader-<k>``,
``grader`` or ``check``; ``total`` the run's sum so far, read back from the ledger at start). The projection is
``0.157 x n`` (6.28 for 40), or ``--projection <usd>``; the brake is twice it. Before each question starts, a total above
the brake writes ``STOPPED`` ``brake``, prints ``STOPPED brake``, ends exit 2 once the running questions finish and writes
no ``misses.jsonl`` and no ``FIGURES.json``. ``judge --resume`` is allowed only while ``STOPPED`` holds ``brake`` and no
``FIGURES.json`` exists, with a ``--projection`` above the last one (else exit 4); it keeps every row (a question with a
row is never asked again) and starts from the ledger's total.
"""

from __future__ import annotations

import json
import re
from collections import Counter

import w2_171_scenario as S
import w2_171_world as W

COST = {"reader": 0.10, "grader": 0.02, "check": 0.01}


def calls_by_question(world) -> Counter:
    return Counter((c["qid"], c["kind"]) for c in world.claude_calls())


def test_s8_every_model_call_s_cost_is_a_spend_event_with_the_running_total(make_world):
    world = make_world("judged:five")
    spend = world.events("spend")
    paid = [c for c in world.claude_calls() if not c["empty"]]
    assert len(spend) == len(paid) > 100
    for event in spend:
        assert set(event) >= {"seq", "at", "event", "call", "qid", "usd", "total"}, event
        assert re.fullmatch(r"reader-\d+|grader|check", event["call"]), event
        assert re.fullmatch(r"q\d\d", event["qid"])
    assert Counter(e["call"].split("-")[0] for e in spend) == Counter(c["kind"] for c in paid)
    assert sum(e["usd"] for e in spend) == sum(c["usd"] for c in paid) or abs(
        sum(e["usd"] for e in spend) - sum(c["usd"] for c in paid)) < 1e-9
    running = 0.0
    for event in spend:      # in ledger order: the lock makes the total a true running sum
        running += event["usd"]
        assert abs(event["total"] - running) < 1e-9, event
    assert abs(world.json_of("FIGURES.json")["spend"]["usd"] - running) < 1e-6


def test_s8_the_default_projection_is_0_157_a_question_and_the_brake_twice_it(make_world):
    world = make_world("judged:five")
    assert world.json_of("FIGURES.json")["spend"]["projection"] == 6.28 or abs(
        world.json_of("FIGURES.json")["spend"]["projection"] - 6.28) < 1e-9
    assert "projection 6.28, brake 12.56)" in world.staged["judge"]["out"]


def _brake_run(world, projection="1.0"):
    S.SCENARIOS["five"].install(world)
    return world.judge("--projection", projection)


def test_s8_the_run_stops_at_twice_its_projection_and_goes_to_the_owner(make_world):
    world = make_world("measured:five")
    run = _brake_run(world)
    assert run.code == 2 and "STOPPED brake" in run.lines, run
    assert (world.run_dir / "STOPPED").read_text().strip() == "brake"
    assert not (world.run_dir / "misses.jsonl").exists() and not (world.run_dir / "FIGURES.json").exists()
    rows = sorted((world.run_dir / "reader").glob("q*.json"))
    assert 0 < len(rows) < 40, len(rows)
    assert all(isinstance(json.loads(p.read_text()), dict) for p in rows), "rows are written whole"
    total = sum(c["usd"] for c in world.claude_calls())
    assert total > 2.0, "the run went past the brake before it stopped"
    assert total < 2.0 + 5 * 0.7, "no new question starts past the brake: only the running ones finish"
    assert world.events("stopped")[0]["cause"] == "brake" and not world.events("figures")
    # a stopped run is never run again without --resume
    snap = W.snapshot(world.sets)
    again = world.judge("--projection", "1.0")
    assert again.code == 3 and "USED" in again.lines, again
    assert W.snapshot(world.sets) == snap


def test_s8_resume_asks_only_the_unfinished_questions_and_starts_from_the_ledger_total(make_world):
    full = make_world("judged:five")
    per_question = calls_by_question(full)        # what a whole run asks, question by question
    world = make_world("measured:five")
    assert _brake_run(world).code == 2
    finished = {p.stem for p in (world.run_dir / "reader").glob("q*.json")}
    before = calls_by_question(world)
    assert finished and len(finished) < 40
    for args, note in ((("--resume",), "no --projection"), (("--resume", "--projection", "1.0"), "not above the last"),
                       (("--resume", "--projection", "0.5"), "below the last")):
        run = world.judge(*args)
        assert run.code == 4, (note, run)
        assert (world.run_dir / "STOPPED").read_text().strip() == "brake" and not list(world.run_dir.glob("STOPPED-*"))
    run = world.judge("--resume", "--projection", "100")
    assert run.code == 0, run
    assert (world.run_dir / "STOPPED-1").read_text().strip() == "brake" and not (world.run_dir / "STOPPED").exists()
    after = calls_by_question(world)
    for qid in finished:
        for kind in ("reader", "grader", "check"):
            assert after[(qid, kind)] == before[(qid, kind)], f"{qid} had a row and was asked again"
    assert after == per_question, "every unfinished question asked exactly as a whole run asks it"
    assert sorted(p.stem for p in (world.run_dir / "reader").glob("q*.json")) == [f"q{i:02d}" for i in range(1, 41)]
    total = sum(c["usd"] for c in world.claude_calls())
    spend = sum(e["usd"] for e in world.events("spend"))
    assert abs(spend - total) < 1e-6 and abs(world.json_of("FIGURES.json")["spend"]["usd"] - total) < 1e-6, \
        "the ledger's total carries over the stop"
    assert "projection 100.00, brake 200.00)" in run.out
    assert world.json_of("FIGURES.json")["spend"]["projection"] == 100


def test_s8_a_planted_ledger_over_the_brake_stops_before_any_question_then_resumes(make_world):
    world = make_world("measured:five")
    events = world.ledger()
    line = {"seq": max(e["seq"] for e in events) + 1, "at": events[-1]["at"], "event": "spend", "call": "reader-1",
            "qid": "q01", "usd": 13.0, "total": 13.0}
    with open(world.run_dir / "ledger.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(line, sort_keys=True) + "\n")
    run = world.judge()
    assert run.code == 2 and "STOPPED brake" in run.lines, run
    assert world.claude_calls() == [], "13.00 USD is over the brake of 12.56: no question starts"
    assert not list((world.run_dir / "reader").glob("q*.json"))
    assert not (world.run_dir / "misses.jsonl").exists() and not (world.run_dir / "FIGURES.json").exists()
    run = world.judge("--resume", "--projection", "20")
    assert run.code == 0, run
    figures = world.json_of("FIGURES.json")
    assert abs(figures["spend"]["usd"] - (13.0 + sum(c["usd"] for c in world.claude_calls()))) < 1e-6
    assert len(list((world.run_dir / "reader").glob("q*.json"))) == 40


def test_s8_resume_is_refused_once_figures_exist_or_when_nothing_was_stopped(make_world):
    done = make_world("judged:five")
    snap = W.snapshot(done.sets)
    run = done.judge("--resume", "--projection", "99")
    assert run.code == 3 and "USED" in run.lines, run
    assert W.snapshot(done.sets) == snap
    fresh = make_world("measured:five")
    run = fresh.judge("--resume", "--projection", "99")
    assert run.code == 3, "no STOPPED holds brake: the resume's conditions do not hold"
    assert not (fresh.run_dir / "reader").exists() and fresh.claude_calls() == []
