"""S2: one attempt measures the kept questions with ``gov.retrieval.measure``'s matcher and source families (hit@5, full
evidence, the first gold rank per question; hit@10, hit@20 and MRR beside them), each search's ranked output kept so a
label is never re-scored by searching again (Interface 1, 3, 8, 12).

Reading: S2's Verify names "a planted set of 12 questions". A set that W2-170's ``preflight`` accepts holds 36 to 40
questions (``PF-COUNT``), and ``measure`` goes through ``declare``, so the planted set is the clean 40 of W2-170 with
the first gold rank of each question planted (``w2_171_scenario.CYCLE`` and the five overrides): ranks 1 to 5, 8, 12, 14,
17, 25 and none, in one call or two or three calls (``continuation``). Thirty-nine questions have a gold place; the
fortieth is the nonexistent-id question (category ``nonexistent-id``), which runs through the measure but is outside
the retrieval figures (``of 39``).
"""

from __future__ import annotations

import json

import w2_171_scenario as S
import w2_171_world as W

SC = S.SCENARIOS["five"]


def test_s2_the_counting_attempt_prints_the_planted_figures_and_keeps_every_output(world):
    SC.install(world)
    run = world.measure()
    assert run.code == 0, run
    expected = S.Expected(SC, world)
    retrieval = [x for x in run.lines if x.startswith("RETRIEVAL")]
    assert retrieval == [expected.retrieval_line(1)], (retrieval, expected.retrieval_line(1))
    attempt = world.attempt_dir(1)
    # the measure's own question lines carry the planted ranks, in file-name order
    lines = world.question_lines(attempt)
    assert [q for q, *_ in lines] == [f"q{i:02d}" for i in range(1, 41)]
    assert all(part == "hidden" for _, part, *_ in lines)
    assert {q: rank for q, _, _, rank, _, _ in lines} == dict(SC.ranks)
    assert {q: bundle for q, _, _, _, bundle, _ in lines} == {q: SC.in_bundle(q) for q in SC.ranks}
    # every search's output kept, in call order
    kept = sorted((attempt / "kept").glob("*.json"))
    calls_per_question = {q: len(S.calls_for(r)) for q, r in SC.ranks.items()}
    assert len(kept) == sum(calls_per_question.values())
    assert [p.name for p in kept] == [f"{i:05d}.json" for i in range(1, len(kept) + 1)]
    for path in kept:
        doc = json.loads(path.read_text())
        assert isinstance(doc["result"]["evidence"], list)
    ms = (attempt / "ms").read_text().split()
    assert len(ms) == len(kept) and all(x.replace(".", "", 1).isdigit() for x in ms)
    for name in ("measure.txt", "measure.err", "ENDED", "DONE"):
        assert (attempt / name).is_file(), name
    assert not (attempt / "FAULT").exists()
    assert (world.run_dir / "COUNTS").read_text().strip() == "attempt-1"
    assert world.events("counts")[0]["attempt"] == "attempt-1"


def test_s2_the_kept_outputs_hold_the_gold_item_where_it_was_planted(world):
    """The first call of each question with a gold place within the first call holds it at its planted position:
    the output is kept as the retriever gave it."""
    SC.install(world)
    assert world.measure().code == 0
    attempt = world.attempt_dir(1)
    docs = world.docs()
    number = 1
    for q in sorted(SC.ranks):
        calls = 1 if SC.ranks[q] is None or SC.ranks[q] <= 10 else (2 if SC.ranks[q] <= 20 else 3)
        rank = SC.ranks[q]
        if q != W.NONEXISTENT and rank is not None and rank <= 10:
            evidence = json.loads((attempt / "kept" / f"{number:05d}.json").read_text())["result"]["evidence"]
            src = docs[q]["sources"][0]
            item = evidence[rank - 1]
            assert (item["path"], item["start_line"], item["end_line"]) == (src["path"], *src["lines"]), (q, item)
        number += calls


def test_s2_the_kept_outputs_rescore_to_the_same_figures_with_kept_and_write_nothing(make_world):
    world = make_world("measured:five")
    expected = S.Expected(SC, world)
    before_sets, before_calls = W.snapshot(world.sets), len(world.gov_calls())
    run = world.measure_kept(1)
    assert run.code == 0, run
    assert [x for x in run.lines if x.startswith("RETRIEVAL")] == [expected.retrieval_line(1)]
    assert not any(x.startswith("STOPPED") for x in run.lines)
    assert W.snapshot(world.sets) == before_sets, "measure --kept wrote something"
    assert len(world.gov_calls()) == before_calls, "measure --kept searched again"
    assert world.git_status() == ""


def _remove_kept_10(world):
    (world.attempt_dir(1) / "kept" / "00010.json").unlink()
    return world.measure_kept(1)


def _add_kept_99(world):
    (world.attempt_dir(1) / "kept" / "00099.json").write_text("{}")
    return world.measure_kept(1)


def test_s2_kept_refuses_with_ms_kept_and_never_exits_3(make_world):
    """An attempt that does not exist, a kept output missing and a kept output left over: ``MS-KEPT``, exit 1."""
    cases = {"no such attempt": lambda w: w.measure_kept(2), "a kept output missing": _remove_kept_10,
             "a kept output left over": _add_kept_99}
    for name, act in cases.items():
        world = make_world("measured:five")
        before = W.snapshot(world.sets / "fixtures", world.sets / "governance")
        run = act(world)
        assert run.code == 1 and "MS-KEPT" in run.lines, (name, run)
        assert not any(x.startswith("RETRIEVAL") for x in run.lines), name
        assert W.snapshot(world.sets / "fixtures", world.sets / "governance") == before, name


def test_s2_the_unresolved_ids_stop_of_the_nonexistent_id_question_is_not_a_degraded_answer(world):
    """The nonexistent-id question's bundle is empty with ``stopping_reason`` ``UNRESOLVED_IDS`` and no rerank: it is
    not degraded (item 12), so a run in which it is asked goes through as a whole attempt."""
    SC.install(world)
    run = world.measure()
    assert run.code == 0 and not (world.attempt_dir(1) / "FAULT").exists(), run
    assert world.question_lines(world.attempt_dir(1))[-1][0] == W.NONEXISTENT
    doc = json.loads((world.attempt_dir(1) / "kept" / f"{len(list((world.attempt_dir(1) / 'kept').glob('*.json'))):05d}.json").read_text())
    assert doc["result"]["stopping_reason"] == "UNRESOLVED_IDS" and doc["result"]["evidence"] == []
