"""The scorer: both figures always, a forbidden citation in the top five a miss, ids only; and the judge's floors."""

from __future__ import annotations

import json

import w2_81_judge as judge
import w2_81_score as score
from w2_81_questions import Question


def _q(n, forbidden=("docs/old.md",)):
    return Question(f"r-q{n:02d}", "visible", "what-value", f"secret question text {n}", f"secret answer {n}",
                    [("src/a.py", 10, "A = 1")], list(forbidden))


GOLD = [("src/a.py", 8, 12)]


def test_both_figures_are_reported_and_a_forbidden_citation_in_the_top_five_is_a_miss():
    asked = [_q(1), _q(2), _q(3), _q(4)]
    answers = {"r-q01": GOLD, "r-q02": [("docs/old.md", 1, 3)] + GOLD,
               "r-q03": [("x", 1, 1)] * 5 + GOLD, "r-q04": None}
    result = score.score_repository("r", asked, answers)
    by_id = {r["id"]: r for r in result["per_question"]}
    assert by_id["r-q01"]["hit_at_5"] and by_id["r-q01"]["full_evidence"]
    assert not by_id["r-q02"]["hit_at_5"] and not by_id["r-q02"]["full_evidence"]
    assert by_id["r-q02"]["forbidden_in_top_5"]
    assert not by_id["r-q03"]["hit_at_5"] and by_id["r-q03"]["full_evidence"]  # rank 6: in the stack, not the top 5
    assert not by_id["r-q04"]["answered"] and not by_id["r-q04"]["full_evidence"]
    assert result["hit_at_5"] == 25.0 and result["stacked_share"] == 50.0
    assert set(result) == {"repository", "questions", "hit_at_5", "stacked_share", "per_question"}


def test_a_forbidden_citation_after_the_top_five_does_not_count():
    result = score.score_question(_q(1), [("x", 1, 1)] * 5 + [("docs/old.md", 1, 1)] + GOLD)
    assert not result["forbidden_in_top_5"] and result["full_evidence"]


def test_the_result_names_questions_by_id_only():
    asked = [_q(n) for n in range(1, 4)]
    text = json.dumps(score.score_repository("r", asked, {q.id: GOLD for q in asked}))
    for q in asked:
        assert q.question not in text and q.gold_answer not in text and q.id in text
    assert "secret" not in repr(asked[0])


def test_a_scorer_at_84_on_hit_at_5_or_one_figure_alone_is_not_ready():
    asked = [_q(n) for n in range(1, 26)]
    answers = {q.id: GOLD for q in asked[:21]}  # 21 of 25: 84 %
    at_84 = score.score_repository("r", asked, answers)
    assert at_84["hit_at_5"] == 84.0
    empty = {"repository": "r", "planted": [], "controls": [], "stages": {}, "not_built": []}
    result = judge.overall([empty], score.figures([at_84]), ["r"])
    assert result["verdict"] == judge.NOT_READY and any("hit_at_5 is 84" in r for r in result["reasons"])
    single = {"repository": "r", "hit_at_5": 100.0}
    assert score.figures([single]) == {}, "one figure alone is no figure"
    alone = judge.overall([empty], {"r": {"hit_at_5": 100.0}}, ["r"])
    assert alone["verdict"] == judge.NOT_READY and any("stacked_share is missing" in r for r in alone["reasons"])
    at_floor = score.score_repository("r", asked[:20], {q.id: GOLD for q in asked[:17]})  # 85 %
    assert judge.overall([empty], {"r": {"hit_at_5": at_floor["hit_at_5"], "stacked_share": 99.0}},
                         ["r"])["verdict"] == judge.READY


def test_no_question_gives_no_figure():
    result = score.score_repository("r", [], {})
    assert result["hit_at_5"] is None and result["stacked_share"] is None and score.figures([result]) == {}


def test_the_thresholds_are_one_constant_each_and_the_judge_reads_them():
    assert score.HIT_AT_5_FLOOR == 85.0 and score.STACKED_SHARE_TARGET == 99.0
    assert judge.FLOORS is score.FLOORS
