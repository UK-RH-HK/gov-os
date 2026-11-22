"""W2-60b, KPI success-11 -- RUBRIC-2's three keys in the session record.

success-11 [DEC-1120 (3), added by DEC-1120 (5)]: "The session record carries RUBRIC-2's three keys: the tier (opus,
sonnet, haiku or other, derived from the model's name), the ticket's criticality class (C0 to C3) and any promotion
reason, the last two read from W2-60a's launch record; each is null when it is not given, never a guess." Verify: a
planted launch with a promotion: the record holds all three; a planted launch without one: the three keys are present
and null.

Interface: ``criticality`` and ``promotion`` are copied from the launch record (its ``criticality`` and ``promotion``);
``promotion`` is "the reason", so its value is the launch record's promotion or that promotion's ``reason``; ``tier`` is
from the model's name, so it is always given. A promotion is made as W2-184 makes one: two failed probe records of the
ticket. A launch without one runs with no ``criticality.yaml`` (W2-184 1.4: the launch record's ``criticality`` and
``promotion`` are null).
"""

from __future__ import annotations

import pytest

import w2_60b_support as t

b, s = t.b, t.s
ENG = t.ENGINEER


def _launched(cli, launch, project, tk):
    t.set_plan(cli, log=t.rich_log())
    result = launch(ENG, tk)
    assert result.run.returncode == 0 and len(result.calls) == 1, result.describe()
    sid = result.calls[0]["session_id"]
    record = t.session_record(project, sid)
    t.assert_form(record)
    return record, t.launch_record(project, sid), b.option_values(result.calls[0]["args"], "--model")[0]


def test_s11_a_launch_with_a_promotion_records_the_tier_the_criticality_and_the_promotion(cli, launch, project):
    tk = s.ticket(project, ENG, "C2", tk="DAEO-zq11")
    s.promote_two_failed(project, tk)
    record, launched, model = _launched(cli, launch, project, tk)
    assert launched["promotion"] is not None and launched["criticality"] == "C2", "the fixture made no promotion"
    # Rewrite-Reason: DEC-1225 (R2): a promotion launched on Opus (tier "opus"); it launches the table's model now, here the
    # engineer's C2 entry, Sonnet (tier "sonnet"): the tier is derived from the model's name as before
    assert t.measured(record, "tier") == "sonnet", f"the tier of {model} is not 'sonnet'"
    t.copied(record, "criticality", "C2")
    promotion = t.measured(record, "promotion")
    assert promotion in (launched["promotion"], launched["promotion"]["reason"]), (
        f"the record's promotion {promotion!r} is not the launch record's {launched['promotion']!r} or its reason")


def test_s11_a_launch_without_a_promotion_or_a_criticality_has_the_keys_null_and_the_tier_given(cli, launch, project):
    s.drop_criticality(project)
    record, launched, model = _launched(cli, launch, project, b.T.tk)
    assert launched["criticality"] is None and launched["promotion"] is None, "the fixture gave a criticality"
    t.copied(record, "criticality", None)
    t.copied(record, "promotion", None)
    assert t.measured(record, "tier") == model.split("-")[1], f"the tier is not the one of {model}'s name"


@pytest.mark.parametrize("cls,tier", [("C3", "opus"), ("C2", "sonnet"), ("C0", "haiku")])
def test_s11_the_tier_is_derived_from_the_model_s_name(cli, launch, project, cls, tier):
    tk = s.ticket(project, ENG, cls)
    record, launched, model = _launched(cli, launch, project, tk)
    assert t.measured(record, "tier") == tier, f"the tier of {model} is not {tier!r}"
    t.copied(record, "criticality", cls)
    t.copied(record, "promotion", None)


def test_s11_a_model_of_another_family_is_tier_other(cli, launch, project):
    s.drop_criticality(project)
    s.write_role(project, ENG, table=None, default=("claude-fable-5-2", "high"))
    record, _, model = _launched(cli, launch, project, b.T.tk)
    assert model == "claude-fable-5-2", "the fixture's engineer does not run on claude-fable-5-2"
    assert t.measured(record, "tier") == "other", "a model that is not opus, sonnet or haiku is tier 'other'"
