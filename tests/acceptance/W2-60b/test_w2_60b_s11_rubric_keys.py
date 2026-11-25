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


def _logged_on(model):
    """The rich log with every message of the session's own file stated as made by ``model`` (what the harness's log
    names is what the tier is derived from; the launcher itself only launches Sonnet now, DEC-1225)."""
    log = t.rich_log()
    for line in log.main.lines:
        if isinstance(line.get("message"), dict) and "model" in line["message"]:
            line["message"]["model"] = model
    return log


def _launched(cli, launch, project, tk, log=None):
    t.set_plan(cli, log=log or t.rich_log())
    result = launch(ENG, tk)
    assert result.run.returncode == 0 and len(result.calls) == 1, result.describe()
    sid = result.calls[0]["session_id"]
    record = t.session_record(project, sid)
    t.assert_form(record)
    return record, t.launch_record(project, sid), b.option_values(result.calls[0]["args"], "--model")[0]


def test_s11_a_launch_after_failed_reviews_records_no_promotion_the_tier_and_the_criticality(cli, launch, project):
    # Rewrite-Reason: DEC-1246 (3)(b): MR-2: promotion is retired; planted failed reviews change nothing, the launch
    # record's and the session record's `promotion` are null, the tier is Sonnet's and the criticality stays C2.
    tk = s.ticket(project, ENG, "C2", tk="DAEO-zq11")
    s.promote_two_failed(project, tk)
    record, launched, model = _launched(cli, launch, project, tk)
    assert launched["promotion"] is None and launched["criticality"] == "C2", "the launch promoted or lost the class"
    assert t.measured(record, "tier") == "sonnet", f"the tier of {model} is not 'sonnet'"
    t.copied(record, "criticality", "C2")
    t.copied(record, "promotion", None)


def test_s11_a_launch_without_a_promotion_or_a_criticality_has_the_keys_null_and_the_tier_given(cli, launch, project):
    s.drop_criticality(project)
    record, launched, model = _launched(cli, launch, project, b.T.tk)
    assert launched["criticality"] is None and launched["promotion"] is None, "the fixture gave a criticality"
    t.copied(record, "criticality", None)
    t.copied(record, "promotion", None)
    assert t.measured(record, "tier") == model.split("-")[1], f"the tier is not the one of {model}'s name"


# Rewrite-Reason: DEC-1225 (1), (5) (with fixes-015a F13, F14, F19): the launcher launches Sonnet for every role it
# launches, C3 work included, and replaces any model the rubric does not give; so a launch no longer runs on Opus, Haiku
# or another family. What success-11 asks (the tier is derived from the model's NAME, as opus, sonnet, haiku or other)
# is checked on the name the session's log states: the log is planted with each family's model, the launch itself is
# on Sonnet. No point is dropped; only the way the model of the name is produced changes.
@pytest.mark.parametrize("cls,name,tier", [("C3", "claude-opus-5-5", "opus"), ("C2", "claude-sonnet-5-5", "sonnet"),
                                           ("C0", "claude-haiku-4-5", "haiku")])
def test_s11_the_tier_is_derived_from_the_model_s_name(cli, launch, project, cls, name, tier):
    tk = s.ticket(project, ENG, cls)
    record, launched, _ = _launched(cli, launch, project, tk, log=_logged_on(name))
    assert t.measured(record, "model") == name, f"the fixture's log does not name {name}"
    assert t.measured(record, "tier") == tier, f"the tier of {name} is not {tier!r}"
    t.copied(record, "criticality", cls)
    t.copied(record, "promotion", None)


# Rewrite-Reason: DEC-1225 (3), (5): no session runs Fable and the launcher refuses a model the rubric does not give; the
# model of another family is therefore the one the session's log names, not the one the launch is given.
def test_s11_a_model_of_another_family_is_tier_other(cli, launch, project):
    s.drop_criticality(project)
    record, _, _ = _launched(cli, launch, project, b.T.tk, log=_logged_on("claude-fable-5-2"))
    assert t.measured(record, "model") == "claude-fable-5-2", "the fixture's log does not name claude-fable-5-2"
    assert t.measured(record, "tier") == "other", "a model that is not opus, sonnet or haiku is tier 'other'"
