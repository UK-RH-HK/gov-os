"""W2-88a -- the matchers' own checks, on made-up skill texts (never the real skill).

These pass today by design: they guard the tests' tolerance (a faithful rendering in either form passes) and their
strictness (a dropped or reordered step, a missing "once", a one-copy section fails), so a red on the real text means
the text and not an over-strict matcher. They read no repository file.
"""

from __future__ import annotations

import re

import w2_88a_support as support

POINTER = "docs/research/W2-88-memory-practice.md"

STEPS_TEXT = [
    "Assess the repository and plan its refactoring.",
    "Census the stated links and build the graph from them.",
    "Build the store with the standard (S10) and its refresh (S11).",
    "Have the verdict set and the tuning set written (S13, S12).",
    "Measure the tuning set and fix only the structure, never a named question, until its halves agree within 5 points.",
    "Declare and measure the verdict set once (S14).",
    "Record every method and figure.",
]


def _heading_form(steps=STEPS_TEXT, pointer=True):
    body = "\n".join(f"{i}. {step}" for i, step in enumerate(steps, 1))
    return ("# Adopt\n\n## Wave 1 scope\n\n- **A0** — safety baseline.\n\n## A9 — the memory practice\n\n"
            f"The practice record is `{POINTER}`.\n\n{body}\n\n## Governing sources\n\nDEC-006.\n"
            if pointer else
            f"# Adopt\n\n## A9 — the memory practice\n\n{body}\n\n## Governing sources\n\nDEC-006.\n")


def _bullet_form(steps=STEPS_TEXT):
    nested = "\n".join(f"  {i}. {step}" for i, step in enumerate(steps, 1))
    return ("# Adopt\n\n## Wave 1 scope\n\n- **A0** — safety baseline.\n- **A8** — legacy memory.\n"
            f"- **A9** — Wave 0 memory practice, in order (see `{POINTER}`):\n{nested}\n"
            "- **A10** — independent memory verification.\n\nEach stage writes an evidence record.\n")


def _problems(text):
    regions = support.a9_regions(text)
    assert regions, "no A9 region found"
    joined = "\n\n".join(regions)
    return support.check_steps(joined) + support.check_pointer(joined)


def test_matcher_a_heading_form_in_the_kpi_words_passes():
    assert _problems(_heading_form()) == []


def test_matcher_a_stage_bullet_with_nested_steps_passes_and_stops_at_the_next_stage():
    text = _bullet_form()
    assert _problems(text) == []
    assert "A10" not in support.a9_regions(text)[0]


def test_matcher_a_faithful_paraphrase_passes_and_the_s_numbers_are_not_required():
    paraphrase = [
        "Assess the repository, then plan the refactoring it needs.",
        "Take a census of its stated links; the graph is built from them.",
        "Build the store to the standard, with its refresh.",
        "Have the two sets written: the verdict set and the tuning set.",
        "Measure the tuning set; fix only the structure and never a named question, until its two halves agree "
        "within 5 points.",
        "Declare the configuration, then measure the verdict set once.",
        "Record every method and every figure.",
    ]
    assert _problems(_heading_form(paraphrase)) == []


def test_matcher_a_dropped_step_is_named():
    steps = [step for index, step in enumerate(STEPS_TEXT) if index != 1]
    problems = _problems(_heading_form(steps))
    assert any(p.startswith("step 2") and "missing" in p for p in problems), problems


def test_matcher_a_reordered_step_is_named():
    steps = list(STEPS_TEXT)
    steps[2], steps[3] = steps[3], steps[2]
    problems = _problems(_heading_form(steps))
    assert any("step 3" in p or "step 4" in p for p in problems), problems


def test_matcher_a_step_five_without_never_a_named_question_is_named():
    steps = list(STEPS_TEXT)
    steps[4] = "Measure the tuning set and fix the structure until its halves agree within 5 points."
    problems = _problems(_heading_form(steps))
    assert any(p.startswith("step 5") and "named question" in p for p in problems), problems


def test_matcher_a_step_five_without_5_points_is_named():
    steps = list(STEPS_TEXT)
    steps[4] = "Measure the tuning set and fix only the structure, never a named question, until its halves agree."
    problems = _problems(_heading_form(steps))
    assert any(p.startswith("step 5") and "5 points" in p for p in problems), problems


def test_matcher_a_step_six_without_once_is_named():
    steps = list(STEPS_TEXT)
    steps[5] = "Declare and measure the verdict set (S14)."
    problems = _problems(_heading_form(steps))
    assert any(p.startswith("step 6") and "once" in p for p in problems), problems


def test_matcher_no_pointer_is_named_and_a_bare_mention_of_a9_is_no_step():
    assert any("does not point" in p for p in _problems(_heading_form(pointer=False)))
    assert support.a9_regions("# Adopt\n\nWave 3: A9 itself and A11.\n") == []


VERIFY_OK = """## Verify clauses for adopted tickets

The pass runs for a ticket about to launch, never for the whole tracker. A product-spec session writes the clauses.
They are checked by the tool, by the ticket's test designer and by the auditor's sample. The owner approves the rule
once.

### Detail

Deeper headings belong to the section.

## Next
"""


def test_matcher_the_verify_section_with_four_statements_passes():
    (section,) = support.verify_sections("# Adopt\n\n" + VERIFY_OK)
    text = support.flat(section)
    assert any(re.search(p, text) for p in support.WHEN_ABOUT_TO_LAUNCH)
    assert any(re.search(p, text) for p in support.WHEN_NOT_WHOLE_TRACKER)
    assert support.sentence_with(section, support.WHO_WRITES)
    assert support.window_hits(section, support.WHAT_CHECKS_TRIGGER, support.WHAT_CHECKS_TERMS)[1] == []
    assert support.sentence_with(section, support.OWNER_APPROVES_ONCE)
    assert "Deeper headings belong" in section and "## Next" not in section


def test_matcher_a_checker_list_missing_the_auditors_sample_is_named():
    section = ("## Verify clauses for adopted tickets\n\nChecked by the tool and by the ticket's test designer.\n")
    _, missing = support.window_hits(section, support.WHAT_CHECKS_TRIGGER, support.WHAT_CHECKS_TERMS)
    assert missing == ["the auditor's sample"]


def test_matcher_a_level_four_or_a_wrong_title_is_no_verify_section():
    assert support.verify_sections("#### Verify clauses for adopted tickets\n\ntext\n") == []
    assert support.verify_sections("## Verify clauses\n\ntext\n") == []
    assert len(support.verify_sections("### Verify clauses for adopted tickets:\n\ntext\n")) == 1


def test_matcher_the_stated_counts_read_the_usual_forms():
    assert support.stated_counts("15 lines added, none removed") == ({15}, {0})
    assert support.stated_counts("lines added: 15; lines removed: 2") == ({15}, {2})
    assert support.stated_counts("+53 -3") == ({53}, {3})
    assert support.stated_counts("15 insertions(+), 0 deletions(-)") == ({15}, {0})
    assert support.stated_counts("`git diff --numstat`: `15 0`") == ({15}, {0})


def test_matcher_the_verdict_reader_takes_the_last_one():
    assert support.verdicts("Round 1 verdict: FAIL.\nRound 2 verdict: PASS") == ["FAIL", "PASS"]
    assert support.verdicts("**Verdict:** PASS") == ["PASS"]
    assert support.verdicts("verdict: to be recorded") == ["TO BE RECORDED"]
