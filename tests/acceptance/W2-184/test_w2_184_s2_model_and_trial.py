"""W2-184, KPI success 2 -- a model after ``--`` that is not the resolved one is refused naming both, unless
``--trial <id>`` names a recorded trial; the subagent model is the session's final model.

KPI success-2 [DEC-1120 (3), lens E F14]: a model after ``--`` that is not the resolved tier's is refused, naming both,
unless ``--trial <id>`` names a recorded trial (role, criticality, model and effort, two or more tickets that include this
one, its Opus reviewer) and the launch records the trial id. The subagent model is the session's model
(``CLAUDE_CODE_SUBAGENT_MODEL`` in the settings' env), recorded. Verify: a planted trial: accepted, id recorded; a model
after ``--`` with no trial: refused naming both.

Interface 4: the table's model is the session's, unless a promotion, a probe or a trial sets it (4.1); a model after
``--`` equal to the resolved one is accepted; a trial is ``governance/project/trials/<id>.yaml`` holding exactly role,
criticality, model, effort, tickets, reviewer.model (4.3); a trial's effort below the floor is accepted, its max needs
``--reason``. ``--trial`` is not a ``gov launch`` option yet (7.2): its cases call ``launcher.launch``.
"""

from __future__ import annotations

import pytest

import w2_184_support as s

ENG = s.ENGINEER
TK = "DAEO-tr01"
TRIAL = "trial-1"


@pytest.fixture()
def tk(project):
    """An engineer ticket in C2: the table says Sonnet, high."""
    return s.ticket(project, ENG, "C2", tk=TK)


# --------------------------------------------------------------------------
# A model after -- : the resolved one is accepted, any other refused naming both
# --------------------------------------------------------------------------

@pytest.mark.parametrize("passed", [("--model", s.SONNET), (f"--model={s.SONNET}",)], ids=["spaced", "joined"])
def test_s2_the_resolved_model_after_the_double_dash_is_accepted_and_recorded_as_after(launch, tk, passed):
    s.assert_session(launch(ENG, tk, *passed), s.SONNET, "high", criticality="C2", model_source="after --",
                     effort_source="by criticality")


@pytest.mark.parametrize("role,cls,given", [
    (ENG, "C3", s.SONNET), (ENG, "C3", s.HAIKU5), (ENG, "C0", s.SONNET), (ENG, "C0", s.OPUS),
    (s.AUDITOR, "C2", s.SONNET), (s.RESEARCH, "C3", "opus"), (s.PRODUCT_SPEC, "C1", s.SONNET)])
def test_s2_a_model_after_the_double_dash_that_is_not_the_resolved_one_is_refused_naming_both(
        project, launch, role, cls, given):
    """C3's table says Opus, so Sonnet (the role's default line) is below its tier; C0's says Haiku, so any other is
    refused: the model is the one of the criticality, not of the default line."""
    tk = s.ticket(project, role, cls)
    resolved = s.TABLES[role][cls][0]
    s.refused(launch(role, tk, "-p", "Do the work.", "--model", given), "--model", given, resolved)


@pytest.mark.parametrize("given", [s.OPUS, s.HAIKU5, "sonnet"])
def test_s2_green_on_base_a_model_that_is_not_the_default_line_s_is_still_refused_naming_both(launch, tk, given):
    """Compatibility: where the table's model is the default line's (C2 engineer: Sonnet), W2-60a's refusal stands."""
    s.refused(launch(ENG, tk, "--model", given), "--model", given, s.SONNET)


def test_s2_the_resolved_model_after_the_double_dash_on_a_role_with_no_table_is_its_default(project, launch):
    s.write_role(project, ENG, table=None)
    tk = s.ticket(project, ENG, "C2")
    s.assert_session(launch(ENG, tk, "--model", s.SONNET), s.SONNET, "medium", criticality="C2",
                     model_source="after --", effort_source="role default")
    s.refused(launch(ENG, tk, "--model", s.OPUS), s.OPUS, s.SONNET)


# --------------------------------------------------------------------------
# A recorded trial
# --------------------------------------------------------------------------

def test_s2_a_planted_trial_admits_the_launch_and_the_record_holds_its_id(project, launch, tk):
    s.plant_trial(project, TRIAL, tk=tk)
    s.assert_session(launch(ENG, tk, trial=TRIAL), s.TRIAL_MODEL, "high", criticality="C2", model_source="trial",
                     effort_source="trial", trial=TRIAL)


def test_s2_a_trial_s_effort_below_the_floor_is_accepted(project, launch, tk):
    s.plant_trial(project, TRIAL, tk=tk, effort="low")
    s.assert_session(launch(ENG, tk, trial=TRIAL), s.TRIAL_MODEL, "low", criticality="C2", model_source="trial",
                     effort_source="trial", trial=TRIAL)


def test_s2_a_trial_s_max_needs_a_reason(project, launch, tk):
    s.plant_trial(project, TRIAL, tk=tk, effort="max")
    s.refused(launch(ENG, tk, trial=TRIAL), "max", "reason")
    text = "the trial measures the deepest setting"
    s.assert_session(launch(ENG, tk, trial=TRIAL, reason=text), s.TRIAL_MODEL, "max", criticality="C2",
                     model_source="trial", effort_source="trial", trial=TRIAL, effort_reason=text)


def test_s2_a_trial_id_may_hold_dots_underscores_and_hyphens(project, launch, tk):
    s.plant_trial(project, "t.1_a-b", tk=tk)
    s.assert_session(launch(ENG, tk, trial="t.1_a-b"), s.TRIAL_MODEL, "high", criticality="C2", model_source="trial",
                     effort_source="trial", trial="t.1_a-b")


def test_s2_the_trial_s_own_model_and_effort_after_the_double_dash_are_accepted_once(project, launch, tk):
    s.plant_trial(project, TRIAL, tk=tk)
    s.assert_session(launch(ENG, tk, "--model", s.TRIAL_MODEL, "--effort", "high", trial=TRIAL), s.TRIAL_MODEL, "high",
                     criticality="C2", model_source="trial", effort_source="trial", trial=TRIAL)


@pytest.mark.parametrize("passed,words", [
    (("--model", s.OPUS), (s.OPUS, s.TRIAL_MODEL)), (("--model", s.HAIKU5), (s.HAIKU5, s.TRIAL_MODEL)),
    (("--effort", "xhigh"), ("xhigh", "high")), (("--effort", "medium"), ("medium", "high"))])
def test_s2_a_model_or_effort_after_the_double_dash_that_differs_from_the_trial_s_is_refused_naming_both(
        project, launch, tk, passed, words):
    s.plant_trial(project, TRIAL, tk=tk)
    s.refused(launch(ENG, tk, *passed, trial=TRIAL), *words)


# --------------------------------------------------------------------------
# A trial that does not fit
# --------------------------------------------------------------------------

def _set(**changes):
    def mutate(data):
        data.update(changes)
    return mutate


def _drop(*keys):
    def mutate(data):
        for key in keys:
            data.pop(key)
    return mutate


BAD_TRIALS = {  # name: (change to a good trial's data, words the refusal names besides the trial's file)
    "role-missing": (_drop("role"), ("role",)),
    "criticality-missing": (_drop("criticality"), ("criticality",)),
    "model-missing": (_drop("model"), ("model",)),
    "effort-missing": (_drop("effort"), ("effort",)),
    "tickets-missing": (_drop("tickets"), ("tickets",)),
    "reviewer-missing": (_drop("reviewer"), ("reviewer",)),
    "reviewer-without-a-model": (_set(reviewer={}), ("reviewer",)),
    "reviewer-not-a-map": (_set(reviewer=s.OPUS), ("reviewer",)),
    "the-wrong-role": (_set(role=s.RESEARCH), ("role",)),
    "the-wrong-criticality": (_set(criticality="C3"), ("criticality",)),
    "criticality-unknown": (_set(criticality="C9"), ("criticality",)),
    "one-ticket": (_set(tickets=[TK]), ("tickets",)),
    "no-tickets": (_set(tickets=[]), ("tickets",)),
    "the-same-ticket-twice": (_set(tickets=[TK, TK]), ("tickets",)),
    "this-ticket-missing": (_set(tickets=["DAEO-aaaa", "DAEO-bbbb"]), ("tickets",)),
    "a-reviewer-that-is-not-opus": (_set(reviewer={"model": s.SONNET}), ("reviewer",)),
    "an-opus-alias-reviewer": (_set(reviewer={"model": "opus"}), ("reviewer",)),
    "a-model-alias": (_set(model="haiku"), ("model",)),
    "an-unknown-effort": (_set(effort="extreme"), ("effort",)),
    "an-extra-key": (_set(note="x"), ()),
}


@pytest.mark.parametrize("case", sorted(BAD_TRIALS))
def test_s2_a_trial_that_does_not_fit_is_refused_naming_the_trial_file_and_the_field(project, launch, tk, case):
    change, words = BAD_TRIALS[case]
    data = s.trial_data(tk)
    change(data)
    s.plant_trial(project, TRIAL, data=data)
    s.refused(launch(ENG, tk, trial=TRIAL), f"{TRIAL}.yaml", *words)


FILE_FAULTS = {
    "not-yaml": "role: [engineer\n",
    "not-a-map": "- engineer\n",
    "empty": "",
    "a-key-written-twice": "role: engineer\nrole: engineer\ncriticality: C2\nmodel: claude-haiku-5-5\neffort: high\n"
                           "tickets: [DAEO-aaaa, DAEO-tr01]\nreviewer: {model: claude-opus-5-5}\n",
}


@pytest.mark.parametrize("case", sorted(FILE_FAULTS))
def test_s2_a_trial_file_that_is_not_a_map_of_the_form_is_refused_naming_it(project, launch, tk, case):
    s.plant_trial(project, TRIAL, raw=FILE_FAULTS[case])
    s.refused(launch(ENG, tk, trial=TRIAL), f"{TRIAL}.yaml")


def test_s2_a_trial_with_no_file_is_refused_naming_it(launch, tk):
    s.refused(launch(ENG, tk, trial="trial-none"), "trial-none.yaml")


def test_s2_an_unreadable_trial_file_is_refused_naming_it(project, launch, tk):
    (project / s.TRIALS_REL / f"{TRIAL}.yaml").mkdir(parents=True)
    s.refused(launch(ENG, tk, trial=TRIAL), f"{TRIAL}.yaml")


@pytest.mark.parametrize("bad_id", ["../x", "a b", "-x", ".x", "x/y", "", "x;y", "té"])
def test_s2_a_trial_id_that_does_not_match_the_form_is_refused(project, launch, tk, bad_id):
    s.plant_trial(project, "x", tk=tk)
    s.refused(launch(ENG, tk, trial=bad_id), "trial")


def test_s2_a_trial_needs_the_criticality_file(project, launch):
    """Interface 1.4: ``--trial`` reads criticality.yaml even for a role with only a default line."""
    s.write_role(project, ENG, table=None)
    s.drop_criticality(project)
    tk = s.ticket(project, ENG, "C2", tk=TK)
    s.plant_trial(project, TRIAL, tk=tk)
    s.refused(launch(ENG, tk, trial=TRIAL), s.CRITICALITY_REL)


def test_s2_a_trial_planted_for_another_ticket_s_criticality_does_not_admit_this_launch(project, launch):
    other = s.ticket(project, ENG, "C3", tk="DAEO-tr02")
    s.plant_trial(project, TRIAL, tk=other, criticality="C2", tickets=["DAEO-aaaa", other])
    s.refused(launch(ENG, other, trial=TRIAL), f"{TRIAL}.yaml", "criticality")


# --------------------------------------------------------------------------
# The subagent model is the session's final model, whatever set it
# --------------------------------------------------------------------------

@pytest.mark.parametrize("how", ["table", "after"])
def test_s2_green_on_base_the_subagent_model_is_the_final_model_in_the_settings_and_the_record(launch, tk, how):
    """Compatibility with W2-60a (C2 engineer: the table's Sonnet is the default line's)."""
    result = launch(ENG, tk, *(("--model", s.SONNET) if how == "after" else ()))
    s.b.assert_launched(result)
    assert result.env_block().get("CLAUDE_CODE_SUBAGENT_MODEL") == s.SONNET, result.env_block()
    assert result.record().get("subagent_model") == s.SONNET and result.record().get("model") == s.SONNET


def test_s2_the_subagent_model_is_a_trial_s_model_in_the_settings_and_the_record(project, launch, tk):
    s.plant_trial(project, TRIAL, tk=tk)
    result = launch(ENG, tk, trial=TRIAL)
    s.b.assert_launched(result)
    assert result.env_block().get("CLAUDE_CODE_SUBAGENT_MODEL") == s.TRIAL_MODEL, result.env_block()
    assert result.record().get("subagent_model") == s.TRIAL_MODEL and result.record().get("model") == s.TRIAL_MODEL
