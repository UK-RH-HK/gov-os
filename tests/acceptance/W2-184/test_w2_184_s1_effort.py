"""W2-184, KPI success 1 (part 3) -- the effort floor and ``--reason``.

Interface 3: when the table's effort is high, xhigh or max, an effort after ``--`` of low or medium is refused naming the
given effort and the floor ``high``; when the table's effort is low or medium there is no floor (3.1). An effort of max
that is the launch's own choice (after ``--``, or a trial's) is refused unless ``--reason "<text>"`` (non-empty after
stripping) is given; a max the table itself names needs no reason (3.2). ``--reason`` is recorded as ``effort_reason``,
whatever the effort (3.3). ``--reason`` is not a ``gov launch`` option yet (7.2): its cases call ``launcher.launch``.
"""

from __future__ import annotations

import pytest

# Rewrite-Reason: DEC-1225 / DEC-1236 (2): F19, no launch takes a model the rubric does not give; the planted tables and
# the launch models expected below were Opus or Haiku and are Sonnet now (the efforts and records still tell the cases apart).
import w2_184_support as s

ENG, TD = s.ENGINEER, s.TEST_DESIGNER
T = s.TABLES

# (role, class) pairs whose table effort is high or more: floor high
HIGH_TABLES = [(ENG, "C3"), (ENG, "C2"), (ENG, "C1"), (TD, "C3"), (TD, "C2"), (s.AUDITOR, "C3"), (s.RESEARCH, "C3"),
               (s.PRODUCT_SPEC, "C3")]
# (role, class) pairs whose table effort is low or medium: no floor
LOW_TABLES = [(ENG, "C0"), (TD, "C0"), (s.PRODUCT_SPEC, "C1"), (s.PRODUCT_SPEC, "C0"), (s.AUDITOR, "C0")]


@pytest.mark.parametrize("given", ["low", "medium"])
@pytest.mark.parametrize("role,cls", HIGH_TABLES)
def test_s1_an_effort_below_high_after_the_double_dash_is_refused_when_the_table_is_high_or_more(
        project, launch, role, cls, given):
    tk = s.ticket(project, role, cls)
    s.refused(launch(role, tk, "--effort", given), "effort", given, "high")


def test_s1_the_floor_is_refused_in_the_joined_spelling_too(project, launch):
    tk = s.ticket(project, ENG, "C2")
    s.refused(launch(ENG, tk, "--effort=low"), "effort", "low", "high")


def test_s1_the_floor_is_not_waived_by_a_reason(project, launch):
    tk = s.ticket(project, ENG, "C2")
    s.refused(launch(ENG, tk, "--effort", "low", reason="the owner wants a quick look"), "effort", "low", "high")


@pytest.mark.parametrize("given", ["high", "xhigh"])
@pytest.mark.parametrize("role,cls", [(ENG, "C2"), (ENG, "C1"), (TD, "C3"), (s.AUDITOR, "C3")])
def test_s1_an_effort_of_high_or_more_after_the_double_dash_is_applied_and_recorded_as_the_launch_s_own(
        project, launch, role, cls, given):
    tk = s.ticket(project, role, cls)
    model, _ = T[role][cls]
    s.assert_session(launch(role, tk, "--effort", given), model, given, criticality=cls,
                     model_source="by criticality", effort_source="after --")


@pytest.mark.parametrize("given", ["low", "medium"])
@pytest.mark.parametrize("role,cls", LOW_TABLES)
def test_s1_there_is_no_floor_when_the_table_effort_is_low_or_medium(project, launch, role, cls, given):
    tk = s.ticket(project, role, cls)
    model, _ = T[role][cls]
    s.assert_session(launch(role, tk, "--effort", given), model, given, criticality=cls,
                     model_source="by criticality", effort_source="after --")


def test_s1_the_floor_follows_the_default_line_of_a_role_with_no_table(project, launch):
    s.write_role(project, ENG, table=None, default=(s.SONNET, "high"))
    tk = s.ticket(project, ENG, "C2")
    s.refused(launch(ENG, tk, "--effort", "low"), "effort", "low", "high")


def test_s1_there_is_no_floor_under_a_role_default_of_medium(project, launch):
    s.write_role(project, ENG, table=None)
    tk = s.ticket(project, ENG, "C2")
    s.assert_session(launch(ENG, tk, "--effort", "low"), s.DEFAULT[0], "low", criticality="C2",
                     model_source="role default", effort_source="after --")


# --------------------------------------------------------------------------
# Max, and --reason
# --------------------------------------------------------------------------

@pytest.mark.parametrize("role,cls", [(ENG, "C2"), (TD, "C2"), (ENG, "C0")])
def test_s1_max_after_the_double_dash_without_a_reason_is_refused(project, launch, role, cls):
    tk = s.ticket(project, role, cls)
    s.refused(launch(role, tk, "--effort", "max"), "max", "reason")


@pytest.mark.parametrize("passed", [("--effort", "max"), ("--effort=max",)], ids=["spaced", "joined"])
def test_s1_max_after_the_double_dash_with_a_reason_is_accepted_and_the_reason_recorded(project, launch, passed):
    tk = s.ticket(project, ENG, "C2")
    text = "the owner asked for the deepest check of the guard"
    s.assert_session(launch(ENG, tk, *passed, reason=text), s.TABLES[ENG]["C2"][0], "max", criticality="C2",
                     model_source="by criticality", effort_source="after --", effort_reason=text)


@pytest.mark.parametrize("reason", ["", "   ", "\t\n"])
def test_s1_an_empty_reason_is_refused_with_max(project, launch, reason):
    tk = s.ticket(project, ENG, "C2")
    s.refused(launch(ENG, tk, "--effort", "max", reason=reason), "reason")


@pytest.mark.parametrize("reason", ["", "   "])
def test_s1_an_empty_reason_is_refused_on_any_launch(project, launch, reason):
    """Interface section 9 lists an empty ``--reason`` as a refusal, whatever the effort."""
    tk = s.ticket(project, ENG, "C2")
    s.refused(launch(ENG, tk, reason=reason), "reason")


def test_s1_a_reason_is_recorded_whatever_the_effort(project, launch):
    tk = s.ticket(project, ENG, "C2")
    text = "a note on this launch"
    s.assert_session(launch(ENG, tk, reason=text), *s.TABLES[ENG]["C2"], criticality="C2",
                     model_source="by criticality", effort_source="by criticality", effort_reason=text)


def test_s1_a_max_the_table_names_needs_no_reason(project, launch):
    tk = s.ticket(project, TD, "C3")
    s.assert_session(launch(TD, tk), s.SONNET, "max", criticality="C3", model_source="by criticality",
                     effort_source="by criticality")


def test_s1_a_max_the_role_default_names_needs_no_reason(project, launch):
    """Existing fixtures whose role default is max still launch (interface 3.2, settled)."""
    s.write_role(project, ENG, table=None, default=(s.SONNET, "max"))
    tk = s.ticket(project, ENG, "C2")
    s.assert_session(launch(ENG, tk), s.SONNET, "max", criticality="C2", model_source="role default",
                     effort_source="role default")
