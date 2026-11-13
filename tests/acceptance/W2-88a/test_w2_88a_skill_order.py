"""W2-88a, success 1 -- the Wave 0 order in the adopt skill (W2-88's S17, moved word for word).

KPI line: "A9's step in template/governance/kernel/skills/adopt/SKILL.md states the practice in order and points to
the practice record. The order: assess and plan; census the stated links and build the graph from them; build the
store with the standard (S10) and its refresh (S11); have the verdict set and the tuning set written (S13, S12);
measure the tuning set and fix only the structure, never a named question, until its halves agree within 5 points;
declare and measure the verdict set once (S14); record every method and figure. Verify: a string test on the skill
for the steps in that order, and the skills check."

Readings (also in the README):
* The ticket does not say whether A9's step is a heading or a stage bullet. Either is accepted: a heading that names
  A9 (its section, up to the next heading of the same or a higher level) or a bullet led by A9, as the A0 to A8
  bullets are written (the bullet and what belongs to it, up to the next heading, the next bullet at its own or a
  shallower indent, or a blank line followed by text at its own indent). Both forms present: the two are joined.
* Each step is matched by the KPI line's own words, case-insensitively, whitespace-normalised, markdown emphasis
  dropped. The seven steps must be found left to right, each inside its own stretch (its first words up to the next
  step's). A text that drops, reorders or merges away a step fails, and each failure names the step.
* The S-numbers (S10 to S14) are NOT required: they name W2-88's KPI lines, which do not exist in a repository
  that adopts the skill, so the words carry the step ("the standard", "its refresh", "the verdict set", "the tuning
  set"). The practice record the step points to holds what they define.
* "never a named question" is accepted in the KPI's words or the same meaning (never/not/no/without a named,
  particular, specific, single or individual question). "5 points" is read as "within 5 points" (or five points).
"""

from __future__ import annotations

import pytest

import w2_88a_support as support


def _a9_text():
    skill = support.read(support.KERNEL_REL)
    regions = support.a9_regions(skill)
    if not regions:
        pytest.fail(f"{support.KERNEL_REL} has no step for A9: no heading that names A9 and no bullet led by A9",
                    pytrace=False)
    return "\n\n".join(regions)


def test_s1_the_skill_has_a_step_for_a9():
    """A9's step exists, as a heading naming A9 or as a bullet led by A9."""
    assert _a9_text().strip()


def test_s1_a9s_step_states_the_seven_steps_in_the_kpi_order():
    """Assess and plan; census the links and build the graph; build the store with the standard and its refresh;
    the verdict set and the tuning set written; measure the tuning set; declare and measure the verdict set once;
    record every method and figure: all seven, in that order."""
    problems = support.check_steps(_a9_text())
    assert not problems, "A9's step does not state the seven steps in order: " + "; ".join(problems)


def test_s1_step_5_fixes_only_the_structure_never_a_named_question():
    """Step 5: fix only the structure, never a named question (the KPI's words or the same meaning)."""
    problems = [p for p in support.check_steps(_a9_text())
                if p.startswith("step 5") and ("named question" in p or "structure" in p or "is missing" in p
                                               or "out of order" in p)]
    assert not problems, "A9's step 5 is wrong: " + "; ".join(problems)


def test_s1_step_5_until_the_halves_agree_within_5_points():
    """Step 5: until the tuning set's halves agree within 5 points."""
    problems = [p for p in support.check_steps(_a9_text())
                if p.startswith("step 5") and ("halves" in p or "5 points" in p or "is missing" in p
                                               or "out of order" in p)]
    assert not problems, "A9's step 5 is wrong: " + "; ".join(problems)


def test_s1_step_6_declares_and_measures_the_verdict_set_once():
    """Step 6: declare and measure the verdict set, once."""
    problems = [p for p in support.check_steps(_a9_text()) if p.startswith("step 6")]
    assert not problems, "A9's step 6 is wrong: " + "; ".join(problems)


def test_s1_a9s_step_points_to_the_practice_record():
    """A9's step names docs/research/W2-88-memory-practice.md."""
    problems = support.check_pointer(_a9_text())
    assert not problems, "; ".join(problems)


def test_s1_the_skills_check_passes_on_the_kernel_adopt_skill():
    """`python3 -m gov.check.skill_validator --both-layouts template/governance/kernel/skills/adopt` exits 0 with no
    findings: front matter, a description of at most 60 tokens, a body of at most 2,500 tokens, only known gov
    commands. (Holds on the base; it guards the added step and section against the body limit.)"""
    code, output = support.run_skill_validator()
    assert code == 0, f"the skills check exited {code}: {output.strip()[:400]}"
    assert '"findings": []' in output, f"the skills check reported findings: {output.strip()[:400]}"
