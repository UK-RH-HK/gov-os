"""S2: the discovery skill's line 55 gains one sentence: search again once before routing a question to the owner as
unanswered (README).

Line 55 is found by its text as the reference holds it (it must stay the start of its line); what follows it on
the same line is the added sentence.
"""

from __future__ import annotations

import re

import w2_142_support as support


def test_s2_line_55_gains_one_sentence_to_search_once_more_before_treating_a_question_as_unanswered():
    lines = [line for line in support.current(support.DISCOVERY).splitlines() if line.startswith(support.LINE_55)]
    assert len(lines) == 1, f"premise: line 55's text starts exactly one line of {support.DISCOVERY}, not {len(lines)}"
    added = lines[0][len(support.LINE_55):]
    assert added.strip(), "line 55 gained no sentence"
    assert added.startswith(" "), f"the added text does not follow line 55 as a new sentence: {added!r}"
    sentence = added.strip()
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z`\"(])", sentence)
    assert len(parts) == 1 and sentence.endswith("."), f"line 55 gained more or less than one sentence: {sentence!r}"
    folded = support.fold(sentence)
    assert "search" in folded and "once" in folded, f"the sentence does not say to search once more: {sentence!r}"
    assert "unanswered" in folded, f"the sentence does not say before treating the question as unanswered: {sentence!r}"
