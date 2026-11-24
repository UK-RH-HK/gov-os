"""W2-201 R2 (DEC-1225): ``gov launch`` picks the model by role.

On W2-184's fixture project and the stand-in CLI, as S3 and X3 run them (this repository's own kernel role file planted
for the worker launched; a ready list and a closed ticket for the lead). Every case reads what the stand-in CLI received
(``--model``), the launch record and the refusal's text.

* **A lead** (``orchestrator`` or ``lead``, a feature, ``--fix`` or ``--chore``) is started with ``--model
  claude-sonnet-5-5`` added by the launcher, once. ``--model`` after ``--`` naming another model is refused
  (``LAUNCH_REFUSED`` naming DEC-1225 and ``governance/project/model-exceptions.yaml``, no session); Fable (``fable`` or
  ``claude-fable-5-2``) is refused whatever the exceptions file holds; Sonnet is not doubled.
* **A worker**: Sonnet at every class (S3's cases), ``--model`` Opus refused, Fable refused with an entry naming it,
  Sonnet not doubled; a trial naming a model other than Sonnet is refused (Opus and Haiku here) unless an exceptions
  entry covers it; a promotion and the second review's probe launch Sonnet and keep their records and effort rules.
* **The skill evaluation harness's** ``DEFAULT_MODEL`` is Sonnet.

Reading, where R2 leaves it open: "a trial file naming a model other than Sonnet" is the trial's ``model`` key (its
``reviewer`` key is a different model by the trial file's own form and is not judged); the refusal of a trial names the
word ``trial`` and the model. The record's ``model_source`` of a promotion and of a probe is not pinned.
"""

from __future__ import annotations

import pytest

import w2_201_support as k
import w2_201_x_support as x

s, b = x.s, x.b
HAIKU = k.HAIKU
FIX_TK, READY_TK = "DAEO-ldfx", "DAEO-lrdy"
CALLER = {"GOV_TICKET": x.CALLER_TICKET}
ENG, TD, AUD = k.ENGINEER, k.TEST_DESIGNER, k.AUDITOR
DECIDED = "the owner (W2-201 R2 fixture)"
REFUSED_WORDS = ("DEC-1225", k.EXCEPTIONS_REL)


@pytest.fixture()
def plan(project):
    """The closed ticket outside the plan, the planned ticket and the ready list, committed (as X3 plants them)."""
    x.ticket(project, ENG, "C2", "closed", tk=FIX_TK)
    s.ticket(project, ENG, "C2", tk=READY_TK)
    b.write(project / x.READY_REL, f"# batch 1\nW2-201-ready {READY_TK} brief.md log.json\n")
    x.commit(project, "the leads' tickets and the ready list")
    return project


def _lead(sandbox, cli, role, kind, *after):
    head = {"feature": (READY_TK,), "fix": (FIX_TK, "--fix", x.FIX_LINE),
            "chore": ("--chore", x.CHORE_LINE)}[kind]
    return x.launch(sandbox, cli, role, *head, *(("--", *after) if after else ()), extra_env=CALLER)


# --------------------------------------------------------------------------
# A lead
# --------------------------------------------------------------------------

@pytest.mark.parametrize("kind", ["feature", "fix", "chore"])
@pytest.mark.parametrize("role", x.LEAD_ROLES)
def test_r2_a_lead_is_started_with_model_sonnet_added(sandbox, cli, plan, role, kind):
    """The CLI's own default (the CTO's Opus) is never a lead's model. Red on the base: the launcher adds no
    ``--model`` for a lead."""
    result = _lead(sandbox, cli, role, kind)
    x.launched(result)
    assert result.values("--model") == [k.SONNET], (
        f"the stand-in received --model {result.values('--model')}, not [{k.SONNET!r}] once\n{result.args}")


@pytest.mark.parametrize("model", [k.OPUS, "opus", HAIKU], ids=["opus-id", "opus-alias", "haiku"])
@pytest.mark.parametrize("kind", ["feature", "fix", "chore"])
@pytest.mark.parametrize("role", x.LEAD_ROLES)
def test_r2_a_lead_asking_another_model_after_the_double_dash_is_refused(sandbox, cli, plan, role, kind, model):
    """No session and no record; the refusal names DEC-1225 and the exceptions file. Red on the base: a lead's
    ``--model`` goes through unjudged."""
    s.refused(_lead(sandbox, cli, role, kind, "--model", model), *REFUSED_WORDS)


@pytest.mark.parametrize("model", k.FABLE_NAMES, ids=["alias-fable", "fable-id"])
@pytest.mark.parametrize("role", x.LEAD_ROLES)
def test_r2_a_lead_asking_fable_is_refused_whatever_the_exceptions_file_holds(sandbox, cli, plan, role, model):
    """Entries that name Fable for the role (as typed), for ``orchestrator`` and for every type. Red on the base."""
    entries = [{"subagent_type": who, "model": name, "decided": DECIDED} for who in (role, "orchestrator", "*")
               for name in k.FABLE_NAMES]
    k.write_exceptions(plan, {"exceptions": entries})
    s.refused(_lead(sandbox, cli, role, "feature", "--model", model), "DEC-1225")


@pytest.mark.parametrize("kind", ["feature", "fix", "chore"])
def test_r2_a_lead_asking_sonnet_after_the_double_dash_starts_with_one_model_flag(sandbox, cli, plan, kind):
    result = _lead(sandbox, cli, "orchestrator", kind, "--model", k.SONNET)
    x.launched(result)
    assert result.values("--model") == [k.SONNET], f"--model is not Sonnet once: {result.values('--model')}\n{result.args}"


# --------------------------------------------------------------------------
# A worker
# --------------------------------------------------------------------------

@pytest.mark.parametrize("cls", ["C3", "C2"])
@pytest.mark.parametrize("role", [ENG, TD])
def test_r2_a_worker_asking_opus_after_the_double_dash_is_refused_naming_dec_1225_and_the_exceptions_file(
        project, launch, role, cls):
    """No exceptions entry: refused at C3 as at C2. Red on the base: the refusal does not name DEC-1225."""
    k.plant_real_role(project, role)
    tk = s.ticket(project, role, cls)
    s.refused(launch(role, tk, "--model", k.OPUS), k.OPUS, *REFUSED_WORDS)


@pytest.mark.parametrize("model", k.FABLE_NAMES, ids=["alias-fable", "fable-id"])
@pytest.mark.parametrize("role", [ENG, TD])
def test_r2_a_worker_asking_fable_is_refused_also_with_an_entry_naming_it(project, launch, role, model):
    k.plant_real_role(project, role)
    entries = [{"subagent_type": who, "model": name, "decided": DECIDED} for who in (role, "*")
               for name in k.FABLE_NAMES]
    k.write_exceptions(project, {"exceptions": entries})
    tk = s.ticket(project, role, "C3")
    s.refused(launch(role, tk, "--model", model), "DEC-1225")


@pytest.mark.parametrize("role", [ENG, TD])
def test_r2_a_worker_asking_sonnet_after_the_double_dash_starts_one_session_with_one_model_flag(project, launch, role):
    k.plant_real_role(project, role)
    tk = s.ticket(project, role, "C3")
    result = launch(role, tk, "--model", k.SONNET)
    s.b.assert_launched(result)
    assert result.values("--model") == [k.SONNET], f"--model is not Sonnet once: {result.values('--model')}\n{result.args}"
    assert k.record_values(result, "model")["model"] == k.SONNET


# --------------------------------------------------------------------------
# A trial
# --------------------------------------------------------------------------

@pytest.mark.parametrize("model", [k.OPUS, HAIKU], ids=["opus", "haiku"])
def test_r2_a_trial_naming_a_model_other_than_sonnet_is_refused(project, launch, model):
    """Rewrite-Reason: DEC-1225 (W2-184's trial cases ran a Haiku trial; the trial's model is Sonnet now, S2 and the
    cases of W2-184 that plant one are revised the same way): a trial's model is the table's, Sonnet, unless an
    exceptions entry covers it."""
    k.plant_real_role(project, ENG)
    tk = s.ticket(project, ENG, "C2", tk="DAEO-tr01")
    s.plant_trial(project, "trial-1", tk=tk, model=model)
    s.refused(launch(ENG, tk, trial="trial-1"), "trial", model)


def test_r2_a_trial_naming_sonnet_starts_and_is_recorded_as_a_trial(project, launch):
    k.plant_real_role(project, ENG)
    tk = s.ticket(project, ENG, "C2", tk="DAEO-tr01")
    s.plant_trial(project, "trial-1", tk=tk, model=k.SONNET)
    result = launch(ENG, tk, trial="trial-1")
    s.b.assert_launched(result)
    assert result.values("--model") == [k.SONNET]
    assert k.record_values(result, "model", "model_source", "trial") == {
        "model": k.SONNET, "model_source": "trial", "trial": "trial-1"}


def test_r2_a_trial_naming_opus_starts_when_an_exceptions_entry_covers_it(project, launch):
    """R2: "unless an exceptions entry covers it". The entry names the role, Opus and the ticket's class."""
    k.plant_real_role(project, ENG)
    tk = s.ticket(project, ENG, "C2", tk="DAEO-tr01")
    k.write_exceptions(project, {"exceptions": [{"subagent_type": ENG, "model": "opus", "class": "C2",
                                                 "decided": DECIDED}]})
    s.plant_trial(project, "trial-1", tk=tk, model=k.OPUS)
    result = launch(ENG, tk, trial="trial-1")
    s.b.assert_launched(result)
    assert result.values("--model") == [k.OPUS], f"the stand-in did not receive --model {k.OPUS} once\n{result.args}"


# --------------------------------------------------------------------------
# A promotion and the second review's probe
# --------------------------------------------------------------------------

def test_r2_a_promotion_on_an_auditor_launches_sonnet_and_keeps_its_record(project, launch):
    # Rewrite-Reason: DEC-1246 (3)(b): MR-2: the promotion is retired; the planted records change nothing and `promotion` is null.
    """Two failed probe records: the next round is a promotion. It keeps its record (``promotion``: the reason and the
    second failed record) and the table's effort (high); the model is the table's, Sonnet, and no longer
    ``criticality.yaml``'s Opus. Red on the base: it launches Opus."""
    k.plant_real_role(project, AUD)
    tk = s.ticket(project, ENG, "C2", tk="DAEO-pr01")
    record = s.promote_two_failed(project, tk)
    result = launch(AUD, tk)
    s.b.assert_launched(result)
    assert {"--model": result.values("--model"), "--effort": result.values("--effort")} == {
        "--model": [k.SONNET], "--effort": ["high"]}, f"the line is not Sonnet, high\n{result.args}"
    got = k.record_values(result, "model", "effort", "promotion", "criticality")
    want = {"model": k.SONNET, "effort": "high", "promotion": None,
            "criticality": "C2"}
    assert got == want, f"the launch record states {got}, not {want}"


def test_r2_the_second_review_of_a_full_ticket_is_the_probe_on_sonnet_at_max(project, launch):
    # Rewrite-Reason: DEC-1246 (3)(b): MR-2: the probe is retired; round 2 is Sonnet at the table's high (round 1 ran on xhigh so no setting repeats).
    """The probe keeps its effort rule (max, source ``probe``, round 2) and its review-round rule; the model is the
    table's, Sonnet. Red on the base: round 2 launches Opus."""
    k.plant_real_role(project, AUD)
    tk = s.ticket(project, ENG, "C2", "FULL", tk="DAEO-pb01")
    first = launch(AUD, tk, "--effort", "xhigh")
    s.b.assert_launched(first)
    assert k.record_values(first, "model", "effort", "review_round") == {
        "model": k.SONNET, "effort": "xhigh", "review_round": 1}
    second = launch(AUD, tk)
    s.b.assert_launched(second)
    assert {"--model": second.values("--model"), "--effort": second.values("--effort")} == {
        "--model": [k.SONNET], "--effort": ["high"]}, f"round 2's line is not Sonnet, high\n{second.args}"
    assert k.record_values(second, "model", "effort", "effort_source", "review_round") == {
        "model": k.SONNET, "effort": "high", "effort_source": "role default", "review_round": 2}  # Rewrite-Reason: DEC-1246 (3)(b): MR-2: the real auditor file has no table line


# --------------------------------------------------------------------------
# The skill evaluation harness
# --------------------------------------------------------------------------

def test_r2_the_skill_evaluation_harness_defaults_to_sonnet():
    from gov.skilleval import harness

    assert harness.DEFAULT_MODEL == k.SONNET, f"DEFAULT_MODEL is {harness.DEFAULT_MODEL!r}, not {k.SONNET!r}"
