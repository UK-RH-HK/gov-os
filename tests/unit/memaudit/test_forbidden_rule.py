"""The strict forbidden-citation rule (DEC-1227 D5 (a)): form, matcher and the judge row, in process."""

from __future__ import annotations

import pytest

from gov.memaudit import matcher, preflight

GOOD = {"id": "q01", "question": "What?", "gold_answer": "That.", "commit": "a" * 40, "category": "decision",
        "drawn": "none", "sources": [{"path": "docs/gold.md"}]}
CATS = ["decision"]


def gold_q(forbidden=(), apart=False):
    """A question as ``matcher.questions`` returns it: one gold place, docs/gold.md lines 1 to 3."""
    return {"sources": [[("docs/gold.md", 1, 3, [], "")]], "apart": apart, "forbidden": list(forbidden)}


@pytest.mark.parametrize("value", [[], ["docs/old.md"], ["docs/old.md", "docs/older.md"]])
def test_form_ok_accepts_forbidden_absent_or_a_list_of_paths(value):
    assert preflight.form_ok({**GOOD, "forbidden": value}, "q01", CATS) is True
    assert preflight.form_ok(GOOD, "q01", CATS) is True


@pytest.mark.parametrize("value", [None, "docs/old.md", {"a": 1}, 3, True, [""], ["  "], ["docs/old.md", ""], [4],
                                   [None], [["x"]], [{"p": 1}]])
def test_form_ok_refuses_a_forbidden_that_is_not_a_list_of_non_empty_strings(value):
    assert preflight.form_ok({**GOOD, "forbidden": value}, "q01", CATS) is False


def test_forbidden_cited_is_path_equality_whatever_the_lines():
    q = gold_q(["docs/old.md"])
    assert matcher.forbidden_cited(q, [("docs/old.md", 90, 99)]) is True
    assert matcher.forbidden_cited(q, [("docs/gold.md", 1, 3), ("docs/old.md", 1, 1)]) is True
    assert matcher.forbidden_cited(q, [("docs/gold.md", 1, 3), ("docs/old.md.bak", 1, 1)]) is False
    assert matcher.forbidden_cited(q, []) is False
    assert matcher.forbidden_cited(gold_q(), [("docs/old.md", 1, 1)]) is False


def test_citation_right_is_gold_cited_and_no_forbidden_cited(tmp_path):
    q = gold_q(["docs/old.md"])
    assert matcher.citation_right(tmp_path, q, [("docs/gold.md", 2, 2)]) is True
    assert matcher.citation_right(tmp_path, q, [("docs/gold.md", 2, 2), ("docs/old.md", 1, 1)]) is False
    assert matcher.citation_right(tmp_path, q, [("docs/old.md", 1, 1)]) is False
    assert matcher.citation_right(tmp_path, q, [("docs/other.md", 1, 1)]) is False
    assert matcher.citation_right(tmp_path, gold_q(), [("docs/gold.md", 2, 2), ("docs/old.md", 1, 1)]) is True


def test_citation_right_is_false_for_an_apart_question(tmp_path):
    assert matcher.citation_right(tmp_path, gold_q(apart=True), [("docs/gold.md", 2, 2)]) is False
