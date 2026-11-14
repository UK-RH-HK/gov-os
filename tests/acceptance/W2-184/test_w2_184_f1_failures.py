"""W2-184, KPI failure 1 -- a model below its tier with no trial, a promotion not applied, an effort below the floor.

KPI failure-1 [from W2-60a F4, DEC-1167]: "A model below its tier with no trial; a promotion not applied; an effort below
the floor. Verify: a model below its tier with no trial is refused; a promotion is recorded and applied; an effort below
high for a judgement role is refused." One named case for each of the three, with the variants that show the line is not
met by a lucky value. A refusal is exit code 1 with LAUNCH_REFUSED, no session started and no launch record left.
"""

from __future__ import annotations

import pytest

import w2_184_support as s

ENG, AUD = s.ENGINEER, s.AUDITOR


@pytest.mark.parametrize("role,cls,below", [
    (ENG, "C3", s.SONNET),            # C3's tier is Opus: Sonnet is below it
    (ENG, "C3", s.HAIKU5),
    (s.RESEARCH, "C2", s.SONNET),     # C2's tier for research is Opus
    (AUD, "C2", s.HAIKU_DATED),       # the auditor's tier is Opus
    (s.TEST_DESIGNER, "C3", s.SONNET),  # the test designer's C3 tier is Opus
])
def test_f1_a_model_below_its_tier_with_no_trial_is_refused(project, launch, role, cls, below):
    tk = s.ticket(project, role, cls)
    s.refused(launch(role, tk, "--model", below), "--model", below, s.TABLES[role][cls][0])


def test_f1_a_promotion_is_recorded_and_applied(project, launch):
    tk = s.ticket(project, ENG, "C2", tk="DAEO-f101")
    record = s.promote_two_failed(project, tk)
    result = launch(ENG, tk)
    s.assert_session(result, s.OPUS, "high", criticality="C2", model_source="promotion",
                     effort_source="by criticality", promotion={"reason": "two failed reviews", "record": record})
    assert result.env_block().get("CLAUDE_CODE_SUBAGENT_MODEL") == s.OPUS


@pytest.mark.parametrize("given", ["low", "medium"])
@pytest.mark.parametrize("cls", ["C3", "C2", "C1"])
def test_f1_an_effort_below_high_for_a_judgement_role_is_refused(project, launch, cls, given):
    """The independent auditor judges: its table is high or more at C3, C2 and C1, so low and medium are below the floor."""
    tk = s.ticket(project, AUD, cls)
    s.refused(launch(AUD, tk, "--effort", given), "effort", given, "high")
