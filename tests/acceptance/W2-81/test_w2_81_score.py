"""The scorer: memory judged end to end, per repository, at 95 % (DEC-1221 (1), DEC-1210 (1), EMERGENCY-2 5.2 and 5.3).

A question is right only when the reader's answer and its citation are both right (the grader says correct, a cited
place holds a gold line, no cited path is forbidden). hit@5 and the stacked share are diagnostics with no floor. A run
record states that the adopter, the reader and the grader ran Sonnet. Results name questions by id only.
"""

from __future__ import annotations

import itertools
import json

import pytest

import w2_81_judge as judge
import w2_81_score as score
from gov.memaudit import prompts
from w2_81_questions import Question

STALE = "docs/old.md"
GOLD = [("src/a.py", 8, 12)]       # a citation that holds the gold line
SAID = {"verdict": "answer", "citations": GOLD, "attempts": 1}


def _q(n, forbidden=(STALE,)):
    return Question(f"r-q{n:02d}", "visible", "what-value", f"secret question text {n}", f"secret answer {n}",
                    [("src/a.py", 10, "A = 1")], list(forbidden))


def _reader(**more):
    return {**SAID, **more}


def _verdict(q, reader=None, grader="correct"):
    return {q.id: {"reader": SAID if reader is None else reader, "grader": grader}}


def test_a_right_answer_with_a_right_citation_is_judged_right():
    result = score.judge_question(_q(1), SAID, "correct")
    assert result["right"] is True and result["id"] == "r-q01" and result["reason"] == "right"
    assert result["citation_right"] and not result["forbidden_cited"]


def test_a_right_answer_citing_the_forbidden_stale_spec_is_wrong_and_the_figure_drops_by_that_question():
    asked = [_q(n) for n in range(1, 21)]
    verdicts = {q.id: {"reader": SAID, "grader": "correct"} for q in asked}
    assert score.end_to_end("r", asked, verdicts)["end_to_end"] == 100.0
    stale_only = _reader(citations=[(STALE, 1, 3)])                 # the stale spec alone: no gold cited either
    stale_beside = _reader(citations=[*GOLD, (STALE, 1, 3)])         # the right place, and the stale spec beside it
    for cited in (stale_only, stale_beside):
        one = score.judge_question(asked[0], cited, "correct")
        assert one["right"] is False and one["forbidden_cited"] and one["reason"] == "forbidden citation", one
        verdicts["r-q01"] = {"reader": cited, "grader": "correct"}
        result = score.end_to_end("r", asked, verdicts)
        assert result["right"] == 19 and result["end_to_end"] == 95.0 and result["met"]  # exactly that one question
        by_id = {r["id"]: r for r in result["per_question"]}
        assert by_id["r-q01"]["right"] is False and all(by_id[i]["right"] for i in by_id if i != "r-q01")


def test_the_same_answer_with_a_right_citation_instead_is_right():
    q = _q(1)
    assert score.judge_question(q, _reader(citations=GOLD), "correct")["right"]
    elsewhere = score.judge_question(q, _reader(citations=[("docs/fine.md", 1, 3), *GOLD]), "correct")
    assert elsewhere["right"], "a citation that is not forbidden and not gold does no harm beside the gold one"


@pytest.mark.parametrize("grade", ["wrong", "incorrect", "not_found", None, "", "Correct", "correct "])
def test_a_right_citation_with_a_grade_that_is_not_correct_is_wrong(grade):
    result = score.judge_question(_q(1), SAID, grade)
    assert result["right"] is False and result["citation_right"] is True
    assert result["reason"] == "the grade is not correct"


def test_a_citation_must_hold_a_gold_line():
    q = _q(1)  # the gold line is src/a.py line 10
    for cites, right in (([("src/a.py", 10, 10)], True), ([("src/a.py", 1, 10)], True), ([("src/a.py", 10, 99)], True),
                         ([("src/a.py", 11, 20)], False), ([("src/a.py", 1, 9)], False),
                         ([("src/b.py", 1, 99)], False), ([], False), ([("src/a.py",)], False),
                         ([None, "src/a.py"], False), ([("src/a.py", "x", 12)], False)):
        result = score.judge_question(q, _reader(citations=cites), "correct")
        assert result["right"] is right, cites
        if not right:
            assert result["reason"] == "citation misses the gold sources", cites


def test_a_missing_verdict_is_wrong_and_never_dropped():
    asked = [_q(n) for n in range(1, 5)]
    result = score.end_to_end("r", asked, {"r-q01": {"reader": SAID, "grader": "correct"}})
    assert result["questions"] == 4 and result["right"] == 1 and result["end_to_end"] == 25.0
    assert {r["id"]: r["reason"] for r in result["per_question"] if not r["right"]} == {
        "r-q02": "no verdict", "r-q03": "no verdict", "r-q04": "no verdict"}
    assert score.judge_question(_q(1), None, "correct")["reason"] == "no verdict"
    assert score.judge_question(_q(1), {}, "correct")["right"] is False
    no_grade = score.judge_question(_q(1), SAID, None)  # the grader gave nothing: wrong, not right by default
    assert no_grade["right"] is False
    assert score.end_to_end("r", asked, {})["end_to_end"] == 0.0 and score.end_to_end("r", asked, None)["right"] == 0


def test_a_reader_error_or_not_found_is_wrong_for_an_answerable_question():
    q = _q(1)
    error = score.judge_question(q, {"verdict": "error", "citations": GOLD}, "correct")
    assert error["right"] is False and error["reason"] == "reader error"
    nothing = score.judge_question(q, {"verdict": "not_found", "citations": []}, "correct")
    assert nothing["right"] is False and nothing["reason"] == "reader not found"
    graded = score.judge_question(q, {"verdict": "not_found", "citations": GOLD}, "not_found")
    assert graded["right"] is False
    unknown = score.judge_question(q, {"verdict": "search_again", "citations": GOLD}, "correct")
    assert unknown["right"] is False and unknown["reason"] == "no verdict"


def test_an_answer_that_comes_after_the_one_more_search_is_not_right():
    """The product's cut 2: the answer comes by the second attempt (the first, or the one more search)."""
    q = _q(1)
    assert score.judge_question(q, _reader(attempts=1), "correct")["right"]
    assert score.judge_question(q, _reader(attempts=2), "correct")["right"]
    late = score.judge_question(q, _reader(attempts=3), "correct")
    assert late["right"] is False and late["reason"] == "answered after the one more search"


def test_the_judgement_is_the_products_rule_on_every_combination():
    """``gov.memaudit.prompts.outcome(row, 2)`` is the product's end-to-end rule; the judgement reads it, so the two
    agree on every reader verdict, attempt count and grade, with the citation check W2-81's own."""
    q = _q(1)
    for verdict, attempts, grade, cites in itertools.product(
            ("answer", "not_found", "error"), (1, 2, 3), ("correct", "wrong", "not_found", None),
            (GOLD, [(STALE, 1, 3)], [])):
        reader = {"verdict": verdict, "citations": cites, "attempts": attempts}
        holds, forbidden = score.cited(q, cites)
        row = {"final_verdict": verdict, "attempts": [None] * attempts, "apart": False,
               "answered_at": attempts if verdict == "answer" else None, "citation_right": holds and not forbidden,
               "grades": {"grader": {"grade": grade}}}
        assert score.judge_question(q, reader, grade)["right"] == prompts.outcome(row, 2)["right"], reader


def test_the_figure_is_right_over_asked_and_never_rounded_into_the_bar():
    def figure(right, asked):
        qs = [_q(n) for n in range(1, asked + 1)]
        said = {q.id: {"reader": SAID, "grader": "correct" if n <= right else "wrong"} for n, q in enumerate(qs, 1)}
        return score.end_to_end("r", qs, said)
    assert score.E2E_BAR == 95.0
    for right, asked, value, met in ((47, 50, 94.0, False), (94, 100, 94.0, False), (19, 20, 95.0, True),
                                     (95, 100, 95.0, True), (38, 40, 95.0, True), (50, 50, 100.0, True),
                                     (0, 7, 0.0, False)):
        result = figure(right, asked)
        assert (result["end_to_end"], result["met"], result["right"], result["questions"]) == (value, met, right, asked)
    near = figure(189, 199)  # 94.97 %: it would round to 95.0, and it is below the bar
    assert near["end_to_end"] < 95.0 and near["met"] is False


def test_no_question_gives_no_figure():
    result = score.score_repository("r", [], {}, {})
    assert result["end_to_end"] is None and result["met"] is False and result["questions"] == 0
    assert score.figures([result]) == {}
    empty = score.end_to_end("r", [], {})
    assert empty["end_to_end"] is None and empty["met"] is False


def test_hit_at_5_and_the_stacked_share_are_diagnostics_with_no_floor():
    asked = [_q(n) for n in range(1, 5)]
    answers = {"r-q01": GOLD, "r-q02": [(STALE, 1, 3)] + GOLD, "r-q03": [("x", 1, 1)] * 5 + GOLD, "r-q04": None}
    said = {q.id: {"reader": SAID, "grader": "correct"} for q in asked}
    result = score.score_repository("r", asked, answers, said)
    assert result["diagnostic"] == {"hit_at_5": 25.0, "stacked_share": 50.0}
    assert result["end_to_end"] == 100.0 and result["met"], "the end-to-end figure does not read the diagnostics"
    assert "hit_at_5" not in result and "stacked_share" not in result, "no top-level figure to read as a bar"
    by_id = {r["id"]: r for r in result["per_question"]}
    assert by_id["r-q02"]["diagnostic"]["forbidden_in_top_5"] and not by_id["r-q02"]["diagnostic"]["hit_at_5"]
    assert not by_id["r-q03"]["diagnostic"]["hit_at_5"] and by_id["r-q03"]["diagnostic"]["full_evidence"]
    assert not by_id["r-q04"]["diagnostic"]["answered"]
    assert by_id["r-q03"]["right"] and by_id["r-q04"]["right"]  # right end to end whatever the retrieval diagnostics say
    for gone in ("HIT_AT_5_FLOOR", "STACKED_SHARE_TARGET", "FLOORS"):
        assert not hasattr(score, gone) and not hasattr(judge, gone), f"{gone} is a floor: it is removed"
    after = score.score_repository("r", asked, answers)  # answers alone: nothing measured end to end
    assert after["end_to_end"] is None and after["diagnostic"]["hit_at_5"] == 25.0 and not after["met"]


def test_the_result_names_questions_by_id_only():
    asked = [_q(n) for n in range(1, 4)]
    said = {q.id: {"reader": SAID, "grader": "correct"} for q in asked[:2]}  # the third has no verdict
    result = score.score_repository("r", asked, {q.id: GOLD for q in asked}, said)
    text = json.dumps(result)
    for q in asked:
        assert q.question not in text and q.gold_answer not in text and q.id in text
    assert "secret" not in repr(asked[0]) and "secret" not in text
    verdict = score.judge_question(asked[0], {**SAID, "answer": "secret answer 1 in full"}, "correct")
    assert "secret" not in json.dumps(verdict), "the judgement carries the reader's verdict, never its answer"
    assert set(verdict) == {"id", "right", "reason", "citation_right", "forbidden_cited", "grade", "reader"}


def test_the_figure_the_judge_reads_is_the_end_to_end_figure_alone():
    asked = [_q(n) for n in range(1, 21)]
    said = {q.id: {"reader": SAID, "grader": "correct"} for q in asked}
    one = score.score_repository("r", asked, {}, said)  # no stacked context at all: hit@5 is 0
    assert one["diagnostic"]["hit_at_5"] == 0.0
    given = score.figures([one])
    assert given["r"]["end_to_end"] == 100.0
    assert score.figures([{"repository": "r", "diagnostic": {"hit_at_5": 100.0, "stacked_share": 100.0}}]) == {}, \
        "diagnostics alone are no figure"
    assert score.figures([{"repository": "r", "end_to_end": True}]) == {} \
        and score.figures([{"repository": "r", "end_to_end": float("nan")}]) == {}
    assert judge.E2E_BAR == score.E2E_BAR, "the judge reads the scorer's bar"


def test_a_repository_at_94_percent_is_not_ready_naming_it_and_at_95_percent_it_is_met():
    """The scorer's figure through the judge: 47 of 50 and 94 of 100 are 94 and NOT_READY; 19 of 20 is 95 and met."""
    empty = {"repository": "r", "planted": [], "controls": [], "stages": {}, "not_built": []}
    for right, asked in ((47, 50), (94, 100), (189, 199)):
        qs = [_q(n) for n in range(1, asked + 1)]
        said = {q.id: {"reader": SAID, "grader": "correct" if n <= right else "wrong"} for n, q in enumerate(qs, 1)}
        result = score.score_repository("r", qs, {q.id: GOLD for q in qs}, said)  # hit@5 and stacked share at 100
        verdict = judge.overall([empty], score.figures([result]), ["r"])
        assert verdict["verdict"] == judge.NOT_READY, (right, asked)
        assert len(verdict["reasons"]) == 1 and verdict["reasons"][0].startswith("r: the end-to-end figure is 94")
        assert verdict["reasons"][0].endswith("below its bar of 95"), verdict["reasons"]
    qs = [_q(n) for n in range(1, 21)]
    said = {q.id: {"reader": SAID, "grader": "correct" if n <= 19 else "wrong"} for n, q in enumerate(qs, 1)}
    at_95 = score.score_repository("r", qs, {}, said)  # 19 of 20: exactly 95, and no retrieval diagnostic at all
    assert at_95["end_to_end"] == 95.0 and at_95["met"]
    assert judge.overall([empty], score.figures([at_95]), ["r"])["verdict"] == judge.READY


# --------------------------------------------------------------------------
# The model line of the run record (every session on Sonnet)
# --------------------------------------------------------------------------

SONNET = "claude-sonnet-5-5"


def _record(**models):
    return {"seed": 1, "release": "0.1.4", "models": {"adopter": SONNET, "reader": SONNET, "grader": SONNET, **models}}


def test_a_run_record_with_the_sonnet_model_line_and_a_release_version_passes():
    assert score.E2E_MODEL == SONNET
    assert score.check_models(_record()) == []


def test_a_run_record_without_the_sonnet_model_line_is_refused():
    assert score.check_models({"seed": 1, "release": "0.1.4"}) == ["the run record has no model line"]
    assert score.check_models({"seed": 1, "release": "0.1.4", "models": ["claude-sonnet-5-5"]})
    assert score.check_models(None)
    for role in ("adopter", "reader", "grader"):
        record = _record()
        del record["models"][role]
        reasons = score.check_models(record)
        assert reasons and any(role in r for r in reasons), (role, reasons)
    no_release = _record()
    del no_release["release"]
    assert any("release" in r for r in score.check_models(no_release))
    assert any("release" in r for r in score.check_models({**_record(), "release": ""}))


@pytest.mark.parametrize("role", ["adopter", "reader", "grader"])
@pytest.mark.parametrize("model", ["claude-opus-5-5", "claude-haiku-5-5", "claude-sonnet-5", "Claude-Sonnet-5-5", "", 5])
def test_a_run_record_naming_another_model_for_any_session_is_refused(role, model):
    reasons = score.check_models(_record(**{role: model}))
    assert reasons and all(role in r for r in reasons), reasons
    assert score.check_models(_record()) == [], "and the same record on Sonnet passes"
