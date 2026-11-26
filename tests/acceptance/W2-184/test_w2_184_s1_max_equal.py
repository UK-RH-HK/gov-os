"""W2-184, interface 3.2a (amended by the lead, 2026-11-14) -- a max after ``--`` that equals the resolved effort needs no
``--reason``.

Interface 3.2a: a max given after ``--`` that equals the effort already resolved for this launch (the table's max, or the
probe's max on a FULL ticket's round 2 or later) is not the launch's own choice and needs no ``--reason``. Only a max
after ``--`` that differs from the resolved effort, or a trial's max, needs ``--reason``. When the given max equals the
probe's, ``effort_source`` is ``probe``; when it equals the table's, ``after --`` (section 8). A model after ``--`` that
equals the resolved one is accepted (4.1).

Why it matters: ``launch_worker.sh`` and every scripted launch pass ``--effort`` after ``--``; without 3.2a a FULL
ticket's probe could not be launched through ``gov launch``.

These cases are the KPI success-1 (max and ``--reason``) and success-4 (the probe) lines, as amended. Where a case needs
no ``--reason`` and no other new option it drives ``gov launch`` itself, as W2-60a's cases do; where it gives ``reason``,
``trial`` or ``owner_named`` it calls ``launcher.launch`` (7.2).

Red, per case, on a launcher that applies 3.2 without 3.2a: the launch is refused (``LAUNCH_REFUSED`` naming max and
``--reason``) where these cases expect it accepted. The guard cases (``..._still_refused...``) are green on such a
launcher: they stop 3.2a from being read wider than it is.
"""

from __future__ import annotations

import pytest

# Rewrite-Reason: DEC-1225 / DEC-1236 (2): F19, no launch takes a model the rubric does not give; the planted tables and
# the launch models expected below were Opus or Haiku and are Sonnet now (the efforts and records still tell the cases apart).
import w2_184_support as s

AUD, ENG, TD = s.AUDITOR, s.ENGINEER, s.TEST_DESIGNER
FULL = "DAEO-mx01"
TRIAL = "trial-max"
OPUS, SONNET = s.OPUS, s.SONNET


def _max_table(role, cls):
    """The role's fixture table with the entry of ``cls`` set to Opus, max."""
    return {**s.TABLES[role], cls: (SONNET, "max")}


# --------------------------------------------------------------------------
# A max after -- equal to the table's max (success-1)
# --------------------------------------------------------------------------

@pytest.mark.parametrize("passed", [("--effort", "max"), ("--effort=max",)], ids=["spaced", "joined"])
def test_s1_a_max_after_the_double_dash_equal_to_the_table_s_max_needs_no_reason(project, launch, passed):
    """KPI success-1 / 3.2a: the table (test designer, C3) says Opus max; ``--effort max`` is not the launch's choice."""
    tk = s.ticket(project, TD, "C3")
    record = s.assert_session(launch(TD, tk, *passed), SONNET, "max", criticality="C3", model_source="by criticality",
                              effort_source="after --")
    assert record["effort_reason"] is None


def test_s1_a_max_after_the_double_dash_equal_to_the_table_s_max_with_the_model_too(project, launch):
    """The shape ``launch_worker.sh`` passes: ``-p <prompt> --model <resolved> --effort max``, no reason."""
    tk = s.ticket(project, TD, "C3")
    s.assert_session(launch(TD, tk, "-p", "Do the work.", "--model", SONNET, "--effort", "max"), SONNET, "max",
                     criticality="C3", model_source="after --", effort_source="after --")


@pytest.mark.parametrize("role,cls,profile", [(ENG, "C2", "STANDARD"), (AUD, "C2", "STANDARD"), (ENG, "C0", "LITE")],
                         ids=["engineer-C2", "auditor-C2-not-full", "engineer-C0"])
def test_s1_any_table_entry_of_max_makes_a_max_after_the_double_dash_free_of_a_reason(
        project, launch, role, cls, profile):
    s.write_role(project, role, table=_max_table(role, cls))
    tk = s.ticket(project, role, cls, profile, tk=f"DAEO-mx{s.CODE[role]}{cls[1]}")
    s.assert_session(launch(role, tk, "--effort", "max"), SONNET, "max", criticality=cls,
                     model_source="by criticality", effort_source="after --", review_round=None)


def test_s1_the_full_form_s_first_pair_of_max_is_a_table_max_on_a_full_ticket(project, launch):
    """The FULL form: Opus max on FULL, Sonnet high otherwise; on a FULL ticket ``--effort max`` equals the table's."""
    s.write_role(project, ENG, table=s.TABLES[ENG], full={"C2": ((SONNET, "max"), (SONNET, "high"))})
    full = s.ticket(project, ENG, "C2", "FULL", tk="DAEO-mx02")
    s.assert_session(launch(ENG, full, "--effort", "max"), SONNET, "max", criticality="C2",
                     model_source="by criticality", effort_source="after --")
    other = s.ticket(project, ENG, "C2", "STANDARD", tk="DAEO-mx03")
    s.refused(launch(ENG, other, "--effort", "max"), "max", "reason")  # there the resolved effort is high


def test_s1_a_max_after_the_double_dash_equal_to_a_role_default_of_max_needs_no_reason(project, launch):
    s.write_role(project, ENG, table=None, default=(SONNET, "max"))
    tk = s.ticket(project, ENG, "C2")
    s.assert_session(launch(ENG, tk, "--effort", "max"), SONNET, "max", criticality="C2",
                     model_source="role default", effort_source="after --")


def test_s1_a_reason_given_beside_an_equal_max_is_accepted_and_recorded(project, launch):
    """3.3: ``--reason`` is recorded whatever the effort; an equal max does not forbid one."""
    tk = s.ticket(project, TD, "C3")
    text = "the owner wants this on the record"
    s.assert_session(launch(TD, tk, "--effort", "max", reason=text), SONNET, "max", criticality="C3",
                     model_source="by criticality", effort_source="after --", effort_reason=text)


# --------------------------------------------------------------------------
# A FULL ticket's probe through gov launch, as launch_worker.sh passes it (success-4)
# --------------------------------------------------------------------------

@pytest.fixture()
def full(project):
    """A FULL ticket in C2: the auditor's table says Sonnet, high."""
    return s.ticket(project, ENG, "C2", "FULL", tk=FULL)


# Rewrite-Reason: DEC-1246 (3)(b): MR-2: the probe (a FULL ticket's round 2 on max, `effort_source` probe, needing no
# `--reason`) is retired; its cases moved to test_w2_184_s4_reviews.py (every round is the table's setting). The cases
# below keep the rule that a `max` is the launch's own choice and needs a `--reason` on every round.

# --------------------------------------------------------------------------
# Still refused: a max after -- that is the launch's own choice (failure-1 side of 3.2)
# --------------------------------------------------------------------------

def test_s1_still_refused_3_2a_a_max_after_the_double_dash_on_a_first_review_of_a_full_ticket(full, launch):
    """Round 1: the resolved effort is high, so ``--effort max`` is the launch's own choice."""
    s.refused(launch(AUD, FULL, "--effort", "max"), "max", "reason")
    s.refused(launch(AUD, FULL, "--model", SONNET, "--effort", "max"), "max", "reason")


@pytest.mark.parametrize("profile", ["STANDARD", "LITE"])
def test_s1_still_refused_3_2a_a_max_after_the_double_dash_on_a_ticket_that_is_not_full(project, launch, profile):
    """Not FULL: there is no probe; the resolved effort is the table's high, so a max is the launch's own choice."""
    tk = s.ticket(project, ENG, "C2", profile, tk=f"DAEO-mx4{profile[0].lower()}")
    for role in (AUD, ENG):
        s.refused(launch(role, tk, "--effort", "max"), "max", "reason")


def test_s1_still_refused_3_2a_a_max_after_the_double_dash_for_an_engineer_on_a_high_table(project, launch):
    tk = s.ticket(project, ENG, "C2", "FULL", tk="DAEO-mx05")
    s.refused(launch(ENG, tk, "--effort", "max"), "max", "reason")
    s.refused(launch(ENG, tk, "--model", s.TABLES[ENG]["C2"][0], "--effort=max"), "max", "reason")


def test_s1_still_refused_3_2a_the_probe_applies_to_the_auditor_alone(project, launch):
    """Round 2 of an engineer's launches on a FULL ticket is no probe: the table's high stays, a max needs a reason."""
    tk = s.ticket(project, ENG, "C2", "FULL", tk="DAEO-mx06")
    s.assert_session(launch(ENG, tk), *s.TABLES[ENG]["C2"], criticality="C2", model_source="by criticality",
                     effort_source="by criticality")
    s.refused(launch(ENG, tk, "--effort", "max"), "max", "reason")


def test_s1_still_refused_3_2a_a_max_that_differs_from_a_table_of_xhigh(project, launch):
    tk = s.ticket(project, TD, "C2")  # the test designer's C2 entry is xhigh
    s.refused(launch(TD, tk, "--effort", "max"), "max", "reason")


def test_s1_still_refused_3_2a_a_trial_s_max_after_the_double_dash_needs_a_reason(project, launch):
    """A trial's max is the launch's own choice (3.2, 3.2a): ``--effort max`` equal to the trial's changes nothing."""
    tk = s.ticket(project, ENG, "C2")
    s.plant_trial(project, TRIAL, tk=tk, effort="max")
    s.refused(launch(ENG, tk, "--effort", "max", trial=TRIAL), "max", "reason")
    text = "the trial's deepest setting, named"
    s.assert_session(launch(ENG, tk, "--effort", "max", trial=TRIAL, reason=text), s.TRIAL_MODEL, "max", criticality="C2",
                     model_source="trial", effort_source="trial", trial=TRIAL, effort_reason=text)


def test_s1_still_refused_3_2a_an_empty_reason_beside_a_max_that_differs_from_the_resolved_effort(project, launch):
    tk = s.ticket(project, ENG, "C2")
    for reason in ("", "   "):
        s.refused(launch(ENG, tk, "--effort", "max", reason=reason), "reason")
