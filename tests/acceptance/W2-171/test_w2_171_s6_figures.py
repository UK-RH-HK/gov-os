"""S6: ``runs/<audit>/FIGURES.json`` carries counts only (Interface 10; S6's Verify: schema check over a planted run;
grep for a planted question word, a planted gold path and a planted answer finds none), and ``classes`` adds the
auditor's class counts after its run (Interface 1, 2).

Readings: ``n_gold`` is the number of questions with a gold place (39: the nonexistent-id question runs through the
measure but is outside the retrieval figures); ``verdict.not_run`` has no stated form and is only required to be
falsy in a run in which every question ran; ``control.last_audit`` is null when no earlier audit has a ``FIGURES.json``.
"""

from __future__ import annotations

import json

import pytest

import w2_171_scenario as S
import w2_171_world as W

TOP = {"audit", "n", "n_gold", "bar", "verdict", "beside", "misses", "control", "pool", "classes", "spend"}
VERDICT = {"right", "wrong", "passes", "right_ok", "wrong_ok", "target_ok", "interval_exact", "not_run"}
BESIDE = {"hit5", "hit10", "hit20", "mrr", "in_bundle", "full_evidence", "correct_citation_aside", "not_found",
          "a1_right", "a3_right", "mcnemar_a1_a2", "grader_agree", "graded", "search_failures"}
MISSES = {"total", "by_outcome", "by_rank", "by_namespace", "by_category", "by_route"}
CLASSES = ("gold_wrong", "question_ambiguous", "out_of_scope", "retrieval_miss", "answer_wrong")


def same(want, got, path="figures"):
    if isinstance(want, dict):
        assert isinstance(got, dict) and set(got) == set(want), (path, sorted(got), sorted(want))
        for k in want:
            same(want[k], got[k], f"{path}.{k}")
    elif isinstance(want, float):
        assert isinstance(got, (int, float)) and got == pytest.approx(want, abs=1e-4), (path, got, want)
    elif isinstance(want, list):
        assert isinstance(got, list) and len(got) == len(want), (path, got, want)
        for i, (a, b) in enumerate(zip(want, got)):
            same(a, b, f"{path}[{i}]")
    else:
        assert got == want and type(got) is type(want), (path, got, want)


@pytest.mark.parametrize("name", ["five", "clean", "below", "five37"])
def test_s6_figures_json_has_exactly_the_keys_of_item_10_and_the_planted_values(make_world, name):
    world = make_world(f"judged:{name}")
    figures = world.json_of("FIGURES.json")
    assert set(figures) == TOP
    assert set(figures["verdict"]) == VERDICT and set(figures["beside"]) == BESIDE
    assert set(figures["misses"]) == MISSES
    assert set(figures["misses"]["by_category"]) == set(W.CATEGORIES) and len(W.CATEGORIES) == 12
    assert set(figures["misses"]["by_route"]) == {"lexical", "semantic", "both", "other", "none"}
    assert set(figures["misses"]["by_rank"]) == {"rank_1_5", "rank_6_20", "not_in_20"}
    assert set(figures["misses"]["by_namespace"]) == {"embedded", "keyword_only"}
    assert set(figures["misses"]["by_outcome"]) == {"wrong", "incomplete", "not_found"}
    assert set(figures["control"]) == {"hit5", "of", "last", "last_audit"} and not figures["control"]["last_audit"]
    assert set(figures["spend"]) == {"usd", "projection", "brake"}
    assert figures["pool"] is None and figures["classes"] is None
    assert not figures["verdict"]["not_run"], "every question ran"
    assert len(figures["verdict"]["interval_exact"]) == 2
    spent = sum(c["usd"] for c in world.claude_calls())
    want = S.Expected(S.SCENARIOS[name], world).figures(spent=spent)
    got = {k: v for k, v in figures.items() if k not in ("pool", "classes")}
    del got["verdict"]["not_run"]
    del got["control"]["last_audit"]
    same(want, got)
    assert figures["verdict"]["interval_exact"] == [pytest.approx(round(x, 4), abs=1e-9) for x in
                                                    S.exact_interval(figures["verdict"]["right"], figures["n"])], \
        "interval_exact is [lo, hi] as fractions to 4 places"
    assert all(len(str(x).split(".")[-1]) <= 4 for x in figures["verdict"]["interval_exact"])


def test_s6_the_misses_are_counted_by_rank_namespace_category_and_route(make_world):
    """The five planted misses: gold at rank 3, 8, none, 14 and 25; ``q19`` carries ``keyword: true``; routes lexical,
    (none), semantic and other (``graph``)."""
    misses = make_world("judged:five").json_of("FIGURES.json")["misses"]
    assert misses["total"] == 5
    assert misses["by_outcome"] == {"wrong": 1, "incomplete": 1, "not_found": 3}
    assert misses["by_rank"] == {"rank_1_5": 1, "rank_6_20": 2, "not_in_20": 2}
    assert misses["by_namespace"] == {"embedded": 4, "keyword_only": 1}
    assert {k: v for k, v in misses["by_category"].items() if v} == {
        "decision": 1, "exact-string": 1, "callers": 1, "code-paraphrase": 1, "multi-file": 1}, misses["by_category"]
    assert misses["by_route"] == {"both": 1, "lexical": 1, "semantic": 1, "other": 1, "none": 1}


def test_s6_figures_json_holds_no_planted_word_gold_path_or_answer(make_world):
    world = make_world("judged:words")
    text = (world.run_dir / "FIGURES.json").read_text(encoding="utf-8")
    forbidden = [*W.UNIQUE, W.HWORD, "Where is the rule", "It is stated in the planted file", "Answer for q"]
    forbidden += sorted({d["sources"][0]["path"] for d in world.docs().values()})
    forbidden += [d["question"] for d in world.docs().values()] + [d["gold_answer"] for d in world.docs().values()]
    found = [w for w in forbidden if w in text]
    assert found == [], found
    assert set(json.loads(text)) == TOP


def _plant_classes(world, classes: dict[str, str], reason="reasonwordxyz"):
    (world.run_dir / "miss-classes.json").write_text(json.dumps(
        {qid: {"class": cls, "reason": f"{reason} for {qid}"} for qid, cls in classes.items()}), encoding="utf-8")


FIVE = {"q03": "gold_wrong", "q19": "retrieval_miss", "q25": "answer_wrong", "q28": "answer_wrong",
        "q33": "out_of_scope"}


def test_s6_classes_adds_the_five_counts_to_the_figures_and_nothing_else(make_world):
    world = make_world("judged:five")
    before = world.json_of("FIGURES.json")
    _plant_classes(world, FIVE)
    run = world.classes()
    assert run.code == 0, run
    after = world.json_of("FIGURES.json")
    assert after["classes"] == {"gold_wrong": 1, "question_ambiguous": 0, "out_of_scope": 1, "retrieval_miss": 1,
                                "answer_wrong": 2}
    assert set(after["classes"]) == set(CLASSES) and sum(after["classes"].values()) == after["misses"]["total"]
    assert {k: v for k, v in after.items() if k != "classes"} == {k: v for k, v in before.items() if k != "classes"}
    assert "reasonwordxyz" not in run.out + run.err and "reasonwordxyz" not in (world.run_dir / "FIGURES.json").read_text()


@pytest.mark.parametrize("name,classes", [
    ("a miss without a class", {k: v for k, v in FIVE.items() if k != "q33"}),
    ("a class for a question that is no miss", {**FIVE, "q01": "gold_wrong"}),
    ("other ids altogether", {"q01": "gold_wrong", "q02": "gold_wrong"}),
])
def test_s6_classes_refuses_ids_other_than_the_misses_with_ms_classes(make_world, name, classes):
    world = make_world("judged:five")
    _plant_classes(world, classes)
    before = (world.run_dir / "FIGURES.json").read_bytes()
    run = world.classes()
    assert run.code == 1 and "MS-CLASSES" in run.lines, (name, run)
    assert (world.run_dir / "FIGURES.json").read_bytes() == before


def test_s6_classes_without_figures_is_ms_nofigures(make_world):
    world = make_world("measured:five")
    _plant_classes(world, FIVE)
    run = world.classes()
    assert run.code == 1 and "MS-NOFIGURES" in run.lines, run
    assert not (world.run_dir / "FIGURES.json").exists()
