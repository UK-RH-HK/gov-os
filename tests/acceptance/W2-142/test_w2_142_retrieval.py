"""S1: the retrieval skill gains step 7, after step 6, with SEARCH-AGAIN-PRACTICE §2's practice; W2-138's step-5
line kept; version 1.0.0 to 1.1.0; the skills check passes (README).

A text check of ``template/governance/kernel/skills/retrieval/SKILL.md`` (the generated ``.claude`` copy follows
at the lift's re-pin ACT, S3, not here). The phrases are the ticket's Verify line, read case-insensitively with
white space folded.
"""

from __future__ import annotations

import re

import w2_142_support as support

PHRASES = ("search again once", "own, different words", "not found", "two searches")


def _step_7() -> str:
    text = support.current(support.RETRIEVAL)
    assert len(re.findall(r"^7\.", text, re.M)) == 1, f"{support.RETRIEVAL} has no step 7, or more than one"
    found = re.search(r"^6\.[^\n]*\n\n(7\..*?)\n\n## Key constraints\n", text, re.S | re.M)
    assert found, f"step 7 in {support.RETRIEVAL} does not come right after step 6, before '## Key constraints'"
    return support.fold(found.group(1))


def test_s1_step_7_after_step_6_carries_the_search_again_practice():
    step = _step_7()
    missing = [phrase for phrase in PHRASES if phrase not in step]
    assert not missing, f"step 7 lacks {missing}: {step!r}"


def test_s1_the_retrieval_skill_s_version_is_1_1_0():
    found = support.version(support.current(support.RETRIEVAL))
    assert found == "1.1.0", f"the retrieval skill's version is {found!r}, not '1.1.0'"


def test_s1_guard_w2_138_s_step_5_line_is_kept_in_step_5():
    text = support.current(support.RETRIEVAL)
    step_5 = re.search(r"^5\..*?^6\.", text, re.S | re.M)
    assert step_5, f"premise: {support.RETRIEVAL} has a step 5 followed by a step 6"
    assert support.STEP_5_LINE in step_5.group(0), "W2-138's step-5 line is no longer in step 5, word for word"
