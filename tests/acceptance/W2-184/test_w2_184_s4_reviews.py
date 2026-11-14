"""W2-184, KPI success 4 -- a FULL ticket's two reviews: the first Opus high, the second the probe, Opus max; the same
setting twice is refused unless the owner named it; max on any other review needs ``--reason``.

KPI success-4 [DEC-1014 item 1, SMART-WORK-5 A, DEC-1015 item 3, DEC-1120 (2)]. Verify: a planted FULL ticket: the two
launch records differ as stated; the same setting twice is refused.

Interface 6: for ``independent-auditor`` on a FULL ticket the launcher counts the launch records in the shared record
folder (``record: gov-launch``, this ticket, this role, ``resumes: null``, leaving out the session being resumed);
``review_round`` is that count plus one. Round 1 takes the table; round 2 and later is the probe: the model is
``criticality.yaml``'s ``opus``, the effort max, ``effort_source: probe`` (``model_source: probe`` only if the probe
changed the model), with no ``--reason``. A launch whose final (model, effort) equals a counted record's is refused naming
that record's session id and the setting, unless ``--owner-named DEC-<n>``. Not FULL: no count, no probe, no refusal.
``--owner-named`` is not a ``gov launch`` option yet (7.2): its cases call ``launcher.launch``.
"""

from __future__ import annotations

import json

import pytest

import w2_184_support as s

AUD, ENG, TD = s.AUDITOR, s.ENGINEER, s.TEST_DESIGNER
FULL = "DAEO-rv01"


@pytest.fixture()
def full(project):
    """A FULL ticket in C2: the auditor's table says Opus, high."""
    return s.ticket(project, ENG, "C2", "FULL", tk=FULL)


def _first(launch, tk=FULL, **kw):
    result = launch(AUD, tk, **kw)
    s.assert_session(result, s.OPUS, "high", criticality="C2", model_source="by criticality",
                     effort_source="by criticality", review_round=1)
    return result


def _second(launch, tk=FULL):
    result = launch(AUD, tk)
    s.assert_session(result, s.OPUS, "max", criticality="C2", model_source="by criticality", effort_source="probe",
                     review_round=2)
    return result


def test_s4_the_first_review_is_opus_high_and_the_second_is_the_probe_opus_max(full, launch):
    first, second = _first(launch), _second(launch)
    assert first.session_id() != second.session_id()


def test_s4_the_probe_names_no_reason_and_the_line_carries_max(full, launch):
    _first(launch)
    second = _second(launch)
    assert second.values("--effort") == ["max"] and second.record()["effort_reason"] is None


def test_s4_a_probe_that_changes_the_model_is_recorded_as_the_model_s_source(project, full, launch):
    """The auditor's table says Sonnet for C2: round 1 Sonnet, round 2 the probe on ``criticality.yaml``'s Opus."""
    s.write_role(project, AUD, table={**s.TABLES[AUD], "C2": (s.SONNET, "high")})
    s.assert_session(launch(AUD, full), s.SONNET, "high", criticality="C2", model_source="by criticality",
                     effort_source="by criticality", review_round=1)
    s.assert_session(launch(AUD, full), s.OPUS, "max", criticality="C2", model_source="probe",
                     effort_source="probe", review_round=2)


def test_s4_the_probe_s_model_is_the_criticality_file_s_opus(project, full, launch):
    s.write_role(project, AUD, table={**s.TABLES[AUD], "C2": (s.SONNET, "high")})
    s.write_criticality(project, s.crit_text(opus="claude-opus-9-9"))
    launch(AUD, full)
    s.assert_session(launch(AUD, full), "claude-opus-9-9", "max", criticality="C2", model_source="probe",
                     effort_source="probe", review_round=2)


# --------------------------------------------------------------------------
# The same setting twice
# --------------------------------------------------------------------------

def test_s4_the_same_setting_twice_is_refused_naming_the_first_record_and_the_setting(full, launch):
    first = _first(launch)
    s.refused(launch(AUD, FULL, "--effort", "high"), first.session_id(), s.OPUS, "high")


def test_s4_the_owner_naming_a_decision_admits_the_same_setting_twice(full, launch):
    _first(launch)
    s.assert_session(launch(AUD, FULL, "--effort", "high", owner_named="DEC-1010"), s.OPUS, "high",
                     criticality="C2", model_source="by criticality", effort_source="after --",
                     owner_named="DEC-1010", review_round=2)


def test_s4_a_third_review_repeats_the_probe_and_is_refused_without_the_owner(full, launch):
    _first(launch)
    second = _second(launch)
    s.refused(launch(AUD, FULL), second.session_id(), s.OPUS, "max")


def test_s4_a_third_review_the_owner_named_is_admitted_and_recorded(full, launch):
    _first(launch)
    _second(launch)
    s.assert_session(launch(AUD, FULL, owner_named="DEC-1010"), s.OPUS, "max", criticality="C2",
                     model_source="by criticality", effort_source="probe", owner_named="DEC-1010", review_round=3)


@pytest.mark.parametrize("named", ["DEC-", "dec-1010", "1010", "DEC-10x", "DEC 1010", "DEC-1010 ", "DEC--1", ""])
def test_s4_a_malformed_owner_named_is_refused_where_the_owner_is_needed(full, launch, named):
    _first(launch)
    s.refused(launch(AUD, FULL, "--effort", "high", owner_named=named), "owner")


@pytest.mark.parametrize("named", ["DEC-", "1010", ""])
def test_s4_a_malformed_owner_named_is_refused_on_any_launch(project, launch, named):
    tk = s.ticket(project, ENG, "C2", tk="DAEO-rv02")
    s.refused(launch(ENG, tk, owner_named=named), "owner")


def test_s4_a_well_formed_owner_named_is_recorded_on_any_launch(project, launch):
    tk = s.ticket(project, ENG, "C2", tk="DAEO-rv02")
    s.assert_session(launch(ENG, tk, owner_named="DEC-1167"), *s.TABLES[ENG]["C2"], criticality="C2",
                     model_source="by criticality", effort_source="by criticality", owner_named="DEC-1167")


# --------------------------------------------------------------------------
# Max on any review that is not the probe needs --reason
# --------------------------------------------------------------------------

def test_s4_max_on_a_first_review_needs_a_reason(full, launch):
    s.refused(launch(AUD, FULL, "--effort", "max"), "max", "reason")
    text = "the owner asked for the deepest first look"
    s.assert_session(launch(AUD, FULL, "--effort", "max", reason=text), s.OPUS, "max", criticality="C2",
                     model_source="by criticality", effort_source="after --", effort_reason=text, review_round=1)


def test_s4_max_on_a_review_that_is_not_the_probe_needs_a_reason(project, launch):
    standard = s.ticket(project, ENG, "C2", "STANDARD", tk="DAEO-rv03")
    s.refused(launch(AUD, standard, "--effort", "max"), "max", "reason")
    text = "an extra deep look at a STANDARD ticket"
    s.assert_session(launch(AUD, standard, "--effort", "max", reason=text), s.OPUS, "max", criticality="C2",
                     model_source="by criticality", effort_source="after --", effort_reason=text)


# --------------------------------------------------------------------------
# Not FULL, other roles, other tickets: no count, no probe, no refusal
# --------------------------------------------------------------------------

@pytest.mark.parametrize("profile", ["STANDARD", "LITE"])
def test_s4_a_ticket_that_is_not_full_has_no_review_round_no_probe_and_no_refusal(project, launch, profile):
    tk = s.ticket(project, ENG, "C2", profile, tk="DAEO-rv04")
    for _ in range(3):
        s.assert_session(launch(AUD, tk), s.OPUS, "high", criticality="C2", model_source="by criticality",
                         effort_source="by criticality")


@pytest.mark.parametrize("role", [ENG, TD])
def test_s4_another_role_on_a_full_ticket_has_no_review_round_and_repeats_its_setting(project, launch, role):
    tk = s.ticket(project, role, "C2", "FULL", tk="DAEO-rv05")
    model, effort = s.TABLES[role]["C2"]
    for _ in range(2):
        s.assert_session(launch(role, tk), model, effort, criticality="C2", model_source="by criticality",
                         effort_source="by criticality")


def test_s4_another_roles_launch_on_the_same_ticket_is_not_a_review(full, launch):
    s.assert_session(launch(TD, FULL), *s.TABLES[TD]["C2"], criticality="C2", model_source="by criticality",
                     effort_source="by criticality")
    _first(launch)


def test_s4_the_reviews_of_another_ticket_are_not_counted(project, full, launch):
    other = s.ticket(project, ENG, "C2", "FULL", tk="DAEO-rv06")
    _first(launch, other)
    _first(launch)


def test_s4_a_record_that_is_not_a_launch_record_is_not_counted(project, full, launch):
    folder = project / ".gov-runtime" / "launches"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "not-a-launch.json").write_text(json.dumps(
        {"record": "something-else", "ticket": FULL, "role": AUD, "resumes": None, "model": s.OPUS,
         "effort": "high"}), encoding="utf-8")
    _first(launch)


def test_s4_a_resumed_review_is_not_a_second_review(full, launch):
    first = _first(launch)
    resumed = launch(AUD, FULL, "--resume", first.session_id())
    s.assert_session(resumed, s.OPUS, "high", criticality="C2", model_source="by criticality",
                     effort_source="by criticality", review_round=1)
    _second(launch)


# --------------------------------------------------------------------------
# A record that cannot be read
# --------------------------------------------------------------------------

def test_s4_a_launch_record_that_is_not_json_refuses_a_review_of_a_full_ticket_naming_it(project, full, launch):
    folder = project / ".gov-runtime" / "launches"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "garbled-record.json").write_text("{ not json", encoding="utf-8")
    s.refused(launch(AUD, FULL), "garbled-record.json")


def test_s4_a_launch_record_that_is_not_json_does_not_matter_where_nothing_is_counted(project, launch):
    """Revised in td-5 (interface 5.1a; DEC-1010, P-W2-184-1 (a)). With a ``criticality.yaml`` every worker launch now
    reads the record folder for the roots the ticket's launch records name, so a record that is not JSON refuses this
    setting too: ``test_w2_184_f1_tests_worktree.py::test_f1_a_launch_record_that_is_not_json_refuses_the_s4_setting_now_that_every_launch_reads_the_folder``.
    Nothing is counted or read where the project has no ``criticality.yaml``: the launch is as before W2-184, "whatever
    its role files and records" (interface 1.4)."""
    standard = s.ticket(project, ENG, "C2", "STANDARD", tk="DAEO-rv07")
    s.drop_criticality(project)
    folder = project / ".gov-runtime" / "launches"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "garbled-record.json").write_text("{ not json", encoding="utf-8")
    s.assert_session(launch(AUD, standard), *s.DEFAULT, criticality=None, model_source="role default",
                     effort_source="role default")
