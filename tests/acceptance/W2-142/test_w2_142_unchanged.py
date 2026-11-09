"""The failure line: any change to a skill beyond the two named lines, or W2-138's step-5 line lost (README).

Each skill is compared, whole, with the reference commit's text (``w2_142_support.reference``):
- the retrieval skill with its step 7 paragraph (from the line starting ``7.`` to the blank line after it) taken
  out and its ``version:`` line set aside must equal the reference with its ``version:`` line set aside;
- the discovery skill with line 55 cut back to the reference's text must equal the reference exactly (its version
  included: S2 names no version change, and the ticket applies §3.2 "exactly").
"""

from __future__ import annotations

import re

import w2_142_support as support

STEP_7 = re.compile(r"^7\.[^\n]*\n(?:[^\n]+\n)*\n", re.M)


def _versions_set_aside(text: str) -> str:
    assert len(support.VERSION_LINE.findall(text)) == 1, "premise: exactly one quoted version line"
    return support.VERSION_LINE.sub('version: "<set aside>"', text)


def test_f1_the_retrieval_skill_is_the_reference_but_for_step_7_and_its_version():
    before = support.reference(support.RETRIEVAL)
    now = STEP_7.sub("", support.current(support.RETRIEVAL), count=1)
    assert _versions_set_aside(now) == _versions_set_aside(before), (
        "the retrieval skill changed outside step 7 and its version line")


def test_f1_the_discovery_skill_is_the_reference_but_for_line_55_s_added_sentence():
    before = support.reference(support.DISCOVERY)
    lines = support.current(support.DISCOVERY).split("\n")
    held = [i for i, line in enumerate(lines) if line.startswith(support.LINE_55)]
    assert len(held) == 1, f"line 55's text no longer starts exactly one line ({len(held)})"
    lines[held[0]] = support.LINE_55
    assert "\n".join(lines) == before, "the discovery skill changed outside line 55's added sentence"
