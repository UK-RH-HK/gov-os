"""W2-184, interface 1.4 as amended (the lead, 2026-11-14) -- a project with NO ``governance/project/criticality.yaml``
launches as before W2-184.

Interface 1.4: with no file the role's ``Launch default`` line serves every role and class (a ``Launch by criticality``
line is still read, a malformed one still refuses, but it is not applied); no promotion; no review count, no probe and
no same-setting refusal; ``criticality``, ``promotion`` and ``review_round`` are null; ``model_source`` and
``effort_source`` are ``role default`` or ``after --``. Still applied with no file: a model after ``--`` other than the
resolved (default) one is refused naming both (4.1); the floor and max/``--reason`` (3.1, 3.2, 3.2a), judged on the
default line's effort; the forms of ``--reason``, ``--trial`` and ``--owner-named`` (section 9); ``effort_reason`` and
``owner_named`` recorded. ``--trial`` with no file is refused naming the file.

Why: under the earlier 1.4 every engineer and test designer launch of a project holding the kernel role files (which
carry a ``Launch by criticality`` line) and no file was refused, against DEC-1167 (2). Each case here fails on a launcher
that applies the earlier 1.4 (a refusal naming ``governance/project/criticality.yaml``, or a promotion, a probe, a
review count or a same-setting refusal with no file), and on the base ``54afbf9a8`` for want of the section 8 keys, the
floor, the max rule or the options (the base has none of them), except the cases named ``green_on_base``.

Options the CLI does not carry yet (``--reason``, ``--trial``, ``--owner-named``, 7.2) are given by calling
``launcher.launch`` (``w2_184_support.launch``).
"""

from __future__ import annotations

import re

import pytest

import w2_184_support as s

ENG, TD, AUD = s.ENGINEER, s.TEST_DESIGNER, s.AUDITOR
SONNET, OPUS, HAIKU5 = s.SONNET, s.OPUS, s.HAIKU5
DEFAULT = s.DEFAULT                       # (Sonnet, medium): the fixture role files' default line
HIGH_DEFAULT = (SONNET, "high")
TRIAL = "trial-nf"
FULL = "DAEO-nf01"
PLAIN = dict(criticality=None, model_source="role default", effort_source="role default")


@pytest.fixture()
def bare(project):
    """The fixture project with its role files' tables and no ``criticality.yaml``."""
    s.drop_criticality(project)
    return project


def _real_lines(role):
    """The kernel role file's own ``Launch default`` line and ``Launch by criticality`` line, which is ``None`` since
    DEC-1225 (R1: the role files carry none; it was the shape the 76 refused cases of W1-28, W1-32, W1-46 and W1-50 had).

    Rewrite-Reason: DEC-1225: the helper asserted that the file has a table line. It has none; the line is optional here
    and the case below launches on the default line, with the table line where the file has one."""
    text = (s.b.REPO_ROOT / s.b.ROLES_REL / f"{role}.md").read_text()
    default = re.search(r"^- \*\*Launch default:\*\* model (\S+), effort (\w+)$", text, re.M)
    table = re.search(r"^- \*\*Launch by criticality:\*\*.*$", text, re.M)
    assert default, f"{role}.md has no default line"
    return (default.group(1), default.group(2)), table.group(0) if table else None


# --------------------------------------------------------------------------
# (a) A well-formed table line is read but not applied: the default line serves every role and class
# --------------------------------------------------------------------------

@pytest.mark.parametrize("cls", ["C3", "C0"])
@pytest.mark.parametrize("role", s.WORKER_ROLES)
def test_nf_a_role_with_a_table_line_launches_on_its_default_line_with_no_criticality_file(bare, launch, role, cls):
    """Fails on the earlier 1.4: refused naming criticality.yaml. Fails on a launcher that applies the table: Opus or
    Haiku (the fixture tables differ from the default line)."""
    tk = s.ticket(bare, role, cls)
    s.assert_session(launch(role, tk), *DEFAULT, **PLAIN)


def test_nf_a_the_full_form_table_line_is_not_applied_either(bare, launch):
    s.write_role(bare, AUD, full={"C2": ((OPUS, "high"), (HAIKU5, "low"))})
    tk = s.ticket(bare, ENG, "C2", "FULL", tk=FULL)
    s.assert_session(launch(AUD, tk), *DEFAULT, **PLAIN, review_round=None)


@pytest.mark.parametrize("role", [ENG, TD])
def test_nf_a_the_kernel_role_file_s_own_lines_launch_on_the_default_line(project, launch, role):
    """The regression itself: the kernel engineer and test designer lines, no criticality.yaml, a C3 ticket."""
    default, table_line = _real_lines(role)
    s.write_role(project, role, table=None, lines=[table_line] if table_line else [], default=default)
    s.drop_criticality(project)
    tk = s.ticket(project, role, "C3")
    s.assert_session(launch(role, tk), *default, **PLAIN)


# --------------------------------------------------------------------------
# (b) A malformed table line still refuses with no file
# --------------------------------------------------------------------------

E = s.TABLES[ENG]
C3, C2, C1, C0 = (f"{c} model {m}, effort {e}" for c, (m, e) in ((c, E[c]) for c in s.CLASSES))
BAD_LINE = {
    "c0-missing": s.HEAD + " " + "; ".join((C3, C2, C1)),
    "class-twice": s.HEAD + " " + "; ".join((C3, C3, C1, C0)),
    "out-of-order": s.HEAD + " " + "; ".join((C2, C3, C1, C0)),
    "unknown-effort": s.HEAD + " " + "; ".join((C3, C2, C1.replace("xhigh", "extreme"), C0)),
    "alias-model": s.HEAD + " " + "; ".join((C3.replace(OPUS, "opus"), C2, C1, C0)),
}


@pytest.mark.parametrize("case", sorted(BAD_LINE))
def test_nf_b_a_malformed_table_line_still_refuses_naming_the_role_file(bare, launch, case):
    """Fails on a launcher that skips the line when there is no file (it would launch)."""
    s.write_role(bare, ENG, table=None, lines=[BAD_LINE[case]])
    tk = s.ticket(bare, ENG, "C2")
    s.refused(launch(ENG, tk), "engineer.md", "Launch by criticality")


def test_nf_b_a_second_table_line_still_refuses_with_no_file(bare, launch):
    s.write_role(bare, ENG, table=None, lines=[s.table_line(E), s.table_line(E)])
    tk = s.ticket(bare, ENG, "C2")
    s.refused(launch(ENG, tk), "engineer.md", "Launch by criticality")


@pytest.mark.parametrize("role", s.WORKER_ROLES)
def test_nf_b_a_malformed_table_line_refuses_every_role_with_no_file(bare, launch, role):
    s.write_role(bare, role, table=None, lines=[BAD_LINE["c0-missing"]])
    tk = s.ticket(bare, role, "C1")
    s.refused(launch(role, tk), f"{role}.md", "Launch by criticality")


# --------------------------------------------------------------------------
# (c) A FULL ticket's two auditor launches: no round, no probe, no same-setting refusal
# --------------------------------------------------------------------------

@pytest.mark.parametrize("table", ["with-a-table-line", "default-line-only"])
def test_nf_c_a_full_ticket_s_auditor_launches_all_start_on_the_default_line(bare, launch, table):
    """Fails on a launcher that counts reviews with no file (round 2 would be the Opus max probe; round 3, or an
    equal setting, a refusal), or that still refuses naming the file."""
    if table == "default-line-only":
        s.write_role(bare, AUD, table=None)
    tk = s.ticket(bare, ENG, "C2", "FULL", tk=FULL)
    sessions = []
    for _ in range(3):
        result = launch(AUD, tk)
        s.assert_session(result, *DEFAULT, **PLAIN, review_round=None)
        sessions.append(result.session_id())
    assert len(set(sessions)) == 3, f"three launches, {len(set(sessions))} distinct sessions: {sessions}"


# --------------------------------------------------------------------------
# (d) Probe records plant no promotion with no file
# --------------------------------------------------------------------------

def _plant(project, tk, kind):
    if kind in ("two-failed", "both"):
        s.promote_two_failed(project, tk)
    if kind in ("fail-open", "both"):
        s.plant_probe(project, tk, "00-open.md", "fail", verdict=s.verdict_block("fails open"))


@pytest.mark.parametrize("kind", ["two-failed", "fail-open", "both"])
@pytest.mark.parametrize("role", [ENG, TD])
def test_nf_d_probe_records_promote_nothing_with_no_file(bare, launch, role, kind):
    """Fails on the earlier 1.4 (refused naming the file) and on a launcher that promotes with no file (Opus,
    ``model_source: promotion``, a non-null ``promotion``)."""
    tk = s.ticket(bare, role, "C2")
    _plant(bare, tk, kind)
    s.assert_session(launch(role, tk), *DEFAULT, **PLAIN, promotion=None)


@pytest.mark.parametrize("kind", ["two-failed", "fail-open"])
def test_nf_d_probe_records_on_a_full_ticket_change_no_auditor_launch(bare, launch, kind):
    tk = s.ticket(bare, ENG, "C2", "FULL", tk=FULL)
    _plant(bare, tk, kind)
    for _ in range(2):
        s.assert_session(launch(AUD, tk), *DEFAULT, **PLAIN, promotion=None, review_round=None)


# --------------------------------------------------------------------------
# (e) --trial needs the file
# --------------------------------------------------------------------------

@pytest.mark.parametrize("table", ["with-a-table-line", "default-line-only"])
def test_nf_e_a_trial_with_no_criticality_file_is_refused_naming_the_file(bare, launch, table):
    """A trial planted and well formed; the refusal names the file, not the trial. Fails on a launcher that admits the
    trial with no file."""
    if table == "default-line-only":
        s.write_role(bare, ENG, table=None)
    tk = s.ticket(bare, ENG, "C2")
    s.plant_trial(bare, TRIAL, tk=tk)
    s.refused(launch(ENG, tk, trial=TRIAL), s.CRITICALITY_REL)


# --------------------------------------------------------------------------
# (f) What is still applied with no file: the model, the floor, max and --reason, judged on the default line
# --------------------------------------------------------------------------

@pytest.mark.parametrize("given", [OPUS, HAIKU5])
def test_nf_f_a_model_after_the_double_dash_that_is_not_the_default_is_refused_naming_both(bare, launch, given):
    tk = s.ticket(bare, ENG, "C2")
    s.refused(launch(ENG, tk, "--model", given), "--model", given, SONNET)


def test_nf_f_the_table_s_model_after_the_double_dash_is_refused_naming_both_with_no_file(bare, launch):
    """The C3 table entry is Opus, but with no file the resolved model is the default line's Sonnet: a launcher that
    applies the table would accept it."""
    tk = s.ticket(bare, ENG, "C3")
    s.refused(launch(ENG, tk, "--model", OPUS), OPUS, SONNET)


def test_nf_f_the_default_model_after_the_double_dash_is_accepted_and_recorded_as_after(bare, launch):
    tk = s.ticket(bare, ENG, "C2")
    s.assert_session(launch(ENG, tk, "--model", SONNET), *DEFAULT, criticality=None, model_source="after --",
                     effort_source="role default")


@pytest.mark.parametrize("given", ["low", "medium"])
def test_nf_f_an_effort_below_the_floor_of_a_high_default_is_refused(bare, launch, given):
    s.write_role(bare, ENG, default=HIGH_DEFAULT)
    tk = s.ticket(bare, ENG, "C2")
    s.refused(launch(ENG, tk, "--effort", given), "effort", given, "high")


def test_nf_f_the_floor_follows_the_default_line_not_a_lower_table_entry(bare, launch):
    """The C0 entry is low, the default line is high: the floor is high."""
    s.write_role(bare, ENG, default=HIGH_DEFAULT)
    tk = s.ticket(bare, ENG, "C0")
    s.refused(launch(ENG, tk, "--effort", "medium"), "effort", "medium", "high")


@pytest.mark.parametrize("given", ["low", "medium"])
def test_nf_f_there_is_no_floor_under_a_medium_default_whatever_the_table_says(bare, launch, given):
    """The engineer's C2 table entry is high: a launcher that applies it with no file would refuse."""
    tk = s.ticket(bare, ENG, "C2")
    s.assert_session(launch(ENG, tk, "--effort", given), SONNET, given, criticality=None, model_source="role default",
                     effort_source="after --")


@pytest.mark.parametrize("given", ["high", "xhigh"])
def test_nf_f_an_effort_of_high_or_more_after_the_double_dash_is_the_launch_s_own(bare, launch, given):
    s.write_role(bare, ENG, default=HIGH_DEFAULT)
    tk = s.ticket(bare, ENG, "C2")
    s.assert_session(launch(ENG, tk, "--effort", given), SONNET, given, criticality=None,
                     model_source="role default", effort_source="after --")


@pytest.mark.parametrize("default", ["medium", "high"])
def test_nf_f_max_after_the_double_dash_on_a_default_below_max_needs_a_reason(bare, launch, default):
    s.write_role(bare, ENG, default=(SONNET, default))
    tk = s.ticket(bare, ENG, "C2")
    s.refused(launch(ENG, tk, "--effort", "max"), "max", "reason")


def test_nf_f_max_after_the_double_dash_with_a_reason_is_accepted_and_the_reason_recorded(bare, launch):
    s.write_role(bare, ENG, default=HIGH_DEFAULT)
    tk = s.ticket(bare, ENG, "C2")
    s.assert_session(launch(ENG, tk, "--effort", "max", reason="the owner wants a deep look"), SONNET, "max",
                     criticality=None, model_source="role default", effort_source="after --",
                     effort_reason="the owner wants a deep look")


def test_nf_f_max_equal_to_a_default_of_max_needs_no_reason(bare, launch):
    """Interface 3.2a with no file: the resolved effort is the default line's max."""
    s.write_role(bare, ENG, default=(SONNET, "max"))
    tk = s.ticket(bare, ENG, "C2")
    s.assert_session(launch(ENG, tk, "--effort", "max"), SONNET, "max", criticality=None,
                     model_source="role default", effort_source="after --")


def test_nf_f_an_empty_reason_is_refused_with_no_file(bare, launch):
    tk = s.ticket(bare, ENG, "C2")
    s.refused(launch(ENG, tk, reason="   "), "reason")


def test_nf_f_a_reason_is_recorded_with_no_file_whatever_the_effort(bare, launch):
    tk = s.ticket(bare, ENG, "C2")
    s.assert_session(launch(ENG, tk, reason="a note"), *DEFAULT, **PLAIN, effort_reason="a note")


def test_nf_f_owner_named_is_recorded_with_no_file(bare, launch):
    tk = s.ticket(bare, ENG, "C2")
    s.assert_session(launch(ENG, tk, owner_named="DEC-1167"), *DEFAULT, **PLAIN, owner_named="DEC-1167")


@pytest.mark.parametrize("bad", ["1167", "dec-1167", "DEC-", "DEC-12a"])
def test_nf_f_a_malformed_owner_named_is_refused_with_no_file(bare, launch, bad):
    tk = s.ticket(bare, ENG, "C2")
    s.refused(launch(ENG, tk, owner_named=bad), "owner")


# --------------------------------------------------------------------------
# A present but malformed file still refuses, even a role with only a default line (interface 1.4)
# --------------------------------------------------------------------------

@pytest.mark.parametrize("text", ["version: 1\ndefault: [C2\n", "", "version: 1\ndefault: C2\nopus: claude-opus-5-5\n"],
                         ids=["not-yaml", "empty", "rules-missing"])
def test_nf_a_present_malformed_file_refuses_a_role_with_only_a_default_line(project, launch, text):
    s.write_role(project, ENG, table=None)
    s.write_criticality(project, text)
    tk = s.ticket(project, ENG, "C2")
    s.refused(launch(ENG, tk), s.CRITICALITY_REL)
