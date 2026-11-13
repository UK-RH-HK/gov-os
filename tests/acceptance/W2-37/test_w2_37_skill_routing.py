"""KPI 3's routing and CAP-33.f: the change skill sends the plain-language impact question to the assessment.

**Outside the ticket's ``allowed_paths``** (package P-1): the skill lives in
``template/governance/kernel/skills/change/SKILL.md`` and its copy ``.claude/skills/change/SKILL.md``. The rest of
the suite does not depend on this file.

- CAP-33.f (Wave 1, regression, green today): the skill states that the question triggers the impact assessment
  (DEC-167).
- CAP-33.g (Wave 2, red today): from Wave 2 the same question runs ``gov impact``.
"""

from __future__ import annotations

import re

import pytest

import w2_37_support as support

COPIES = [support.SKILL_TEMPLATE, support.SKILL_COPY]


def section(path):
    """The skill's section on the impact assessment: from its heading to the next heading of the same level."""
    text = path.read_text(encoding="utf-8")
    match = re.search(r"^(#+) Impact assessment\s*$", text, re.MULTILINE)
    assert match, f"{path} has no section `Impact assessment`"
    level = len(match.group(1))
    rest = text[match.end():]
    end = re.search(rf"^#{{1,{level}}} ", rest, re.MULTILINE)
    return rest[:end.start()] if end else rest


@pytest.mark.parametrize("path", COPIES, ids=["template", "claude-copy"])
def test_regression_the_skill_says_the_question_triggers_the_impact_assessment(path):
    """CAP-33.f, met by W1-35: green today."""
    text = section(path)
    assert re.search(r"impact of X", text, re.IGNORECASE) and "DEC-167" in text, \
        f"{path}: the section does not say the plain-language question triggers the assessment (DEC-167)"


@pytest.mark.parametrize("path", COPIES, ids=["template", "claude-copy"])
def test_the_skill_runs_gov_impact_for_the_question(path):
    """CAP-33.g: from Wave 2 the question runs ``gov impact``."""
    text = section(path)
    assert "gov impact" in text, f"{path}: the impact-assessment section does not run `gov impact`"
