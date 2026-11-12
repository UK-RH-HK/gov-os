"""S3: the pinned prompts, schemas, cut and tests of the fresh 80's reader run, recomputed against the hash list of
Interface item 7 (the list is the pin). Text is UTF-8; a schema is ``json.dumps(schema)`` (the bytes ``--json-schema``
carries); a function is its source text from ``def`` to its last line, no final newline."""

from __future__ import annotations

import hashlib
import inspect
import json

import pytest

from gov.memaudit import prompts

PINNED = {
    "READER_SYS": "a0e222af4a0f9a6ca2cb8e31dd44dc7c21e684c5a0de0e0d081947eacef85e08",
    "READER_SCHEMA": "216897d1c451e34033fafd75d1f6be408b0f82dacd5ff885dcad37351c578e5d",
    "GRADER_SYS": "58d1ad87b24064b28bb09c498a9915f66f0867ffa1e09565f59fd33c7e2ac6d4",
    "GRADER_SCHEMA": "7bfc5786b59231cb7576cdbeeef713ca3524e18205189f73c598ac323c8370a8",
    "GRADER_PROMPT": "c12bc5ee7fe303c4e83d6c8803683e2697b1e2f595ecd382e771e61ead15879e",
    "prompt_of": "4a8c1c65619d7111c6dbdc7aae8de6164306ea0366d9410f8ea5095a04fb8c42",
    "items_of": "38cb4b5de225235759064e88027287fd8de4c1fa48e24007e1e573d048aa19f1",
    "outcome": "41a930d83aa170bb33e703b7daa39d6f9f489db9767c52a152cd1cae23899f13",
    "mcnemar": "48e0099533762dd0b2df6f80e7b1f42c0ae214de94d76ea13964cfbe641557d7",
}


def digest(name: str) -> str:
    obj = getattr(prompts, name)
    if callable(obj):
        text = inspect.getsource(obj).rstrip("\n")
    elif isinstance(obj, dict):
        text = json.dumps(obj)
    else:
        text = obj
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@pytest.mark.parametrize("name", sorted(PINNED))
def test_each_pinned_item_hashes_to_item_7s_list(name):
    assert digest(name) == PINNED[name]


@pytest.mark.parametrize("name", ["prompt_of", "items_of", "outcome", "mcnemar"])
def test_a_function_hashes_alike_by_its_syntax_tree_text(name):
    import ast
    src = open(prompts.__file__, encoding="utf-8").read()
    node = next(n for n in ast.parse(src).body if isinstance(n, ast.FunctionDef) and n.name == name)
    assert hashlib.sha256(ast.get_source_segment(src, node).encode("utf-8")).hexdigest() == PINNED[name]


def test_the_cap_is_3_and_the_refine_strings_are_not_copied():
    assert prompts.CAP == 3
    assert not any(n.startswith("REFINE") or n == "UNRANKED_NOTE" for n in dir(prompts))


def test_the_grader_prompt_form_formats_with_question_gold_and_said():
    text = prompts.GRADER_PROMPT.format(question="Q?", gold="G.", said="S.")
    assert text == "Question: Q?\n\nGold answer: G.\n\nAnswer to grade: S."


def test_outcome_cuts_as_the_fresh_80_ran_it():
    row = {"apart": False, "answered_at": 2, "final_verdict": "answer", "attempts": [1, 2], "citation_right": True,
           "grades": {"grader": {"grade": "correct"}}}
    assert prompts.outcome(row, 2) == {"right": True, "correct": True, "wrong": False, "nf": False}
    assert prompts.outcome(row, 1)["nf"] is True and prompts.outcome(row, 1)["right"] is False
    apart = {"apart": True, "answered_at": None, "final_verdict": "not_found", "attempts": [1], "citation_right": False,
             "grades": {"grader": {"grade": "correct"}}}
    assert prompts.outcome(apart, 2)["right"] is True


def test_mcnemar_counts_gains_losses_and_the_exact_p():
    assert prompts.mcnemar([False, False, True], [True, True, True]) == (2, 0, 0.5)
    assert prompts.mcnemar([True], [True]) == (0, 0, 1.0)
