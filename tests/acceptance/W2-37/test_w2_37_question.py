"""KPI 3: "What's the impact of X?" in plain language runs ``gov impact`` [CAP-33.g, DEC-167].

Reading R7: the command takes the question as its stated change (one argument) and answers it with the same
assessment as the id the question names. A question that names nothing known is refused, never answered with an
empty impact. Routing an agent's question to the command is the change skill's (``test_w2_37_skill_routing.py``).
"""

from __future__ import annotations

import pytest

import w2_37_support as support

QUESTIONS = [
    f"What's the impact of {support.CHANGED}?",
    f"what is the impact of {support.CHANGED}",
    f"What’s the impact of {support.CHANGED}?",
]


@pytest.mark.parametrize("question", QUESTIONS, ids=["whats", "what-is-lower-case", "typographic-apostrophe"])
def test_a_plain_language_question_gives_the_assessment_of_the_id_it_names(asked, question):
    by_question, by_id = asked(question), asked(support.CHANGED)
    assert [entry["id"] for entry in by_question["change"]] == [support.CHANGED], \
        f"the question's change is {by_question['change']}, not {support.CHANGED}"
    assert by_question["affected"] == by_id["affected"] and by_question["radius"] == by_id["radius"], \
        "the question and the id give different assessments"


def test_a_question_about_an_unknown_id_is_refused_and_names_it(graph, box):
    support.assert_refused(support.impact(graph, "What's the impact of DEC-999?", box), "DEC-999")


@pytest.mark.parametrize("question", ["What's the impact?", "What is the weather like today?"],
                         ids=["no-subject", "not-about-a-change"])
def test_a_question_that_names_no_change_is_refused(graph, box, question):
    support.assert_refused(support.impact(graph, question, box))


@pytest.mark.local_only
def test_a_plain_language_question_about_a_symbol(asked_code):
    by_question, by_id = asked_code(f"What's the impact of {support.HELPER}?"), asked_code(support.HELPER)
    assert by_question["affected"] == by_id["affected"], "the question and the symbol give different assessments"
