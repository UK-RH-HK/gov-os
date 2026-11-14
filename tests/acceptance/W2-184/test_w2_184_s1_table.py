"""W2-184, KPI success 1 (part 1) -- the session's model and effort come from the role file's table line for the
ticket's criticality; a missing or malformed line, or a malformed criticality.yaml, refuses.

KPI success-1 [DEC-1120 (2)-(3)]: the model and effort are read from the role file's ``Launch default`` line and its
``Launch by criticality`` line (C3, C2, C1, C0), the ticket's criticality derived from its profile and ``allowed_paths``
by ``governance/project/criticality.yaml`` (never from the ticket's ``class``); applied on the launch line and recorded
with ``tier``, ``criticality`` and ``model_source``; a missing or malformed line refuses the launch. Verify: a case per
role and criticality on fixture role files.

Interface 2.2-2.3 settle "missing": a role file with NO ``Launch by criticality`` line takes its ``Launch default`` line
for every class (recorded ``role default``); what refuses is a line that is present and malformed, a class missing from
it included.
"""

from __future__ import annotations

import pytest

import w2_184_support as s

ENG = s.ENGINEER
SESSION = dict(effort_source="by criticality", model_source="by criticality")


@pytest.mark.parametrize("cls", s.CLASSES)
@pytest.mark.parametrize("role", s.WORKER_ROLES)
def test_s1_the_session_takes_its_role_s_table_line_for_the_ticket_s_criticality(project, launch, role, cls):
    tk = s.ticket(project, role, cls)
    model, effort = s.TABLES[role][cls]
    s.assert_session(launch(role, tk), model, effort, criticality=cls, **SESSION)


@pytest.mark.parametrize("kind,cls", [("C3", "C0"), ("C0", "C3"), ("critical", "C1"), ("research", "C2")])
def test_s1_the_ticket_s_class_never_changes_the_result(project, launch, kind, cls):
    """``class`` is the ticket's kind: a misleading value does not move the ticket's criticality."""
    tk = s.ticket(project, ENG, cls, kind=kind)
    model, effort = s.TABLES[ENG][cls]
    record = s.assert_session(launch(ENG, tk), model, effort, criticality=cls, **SESSION)
    assert record["ticket_class"] == kind, f"the record's ticket_class is not the ticket's class {kind!r}"


# --------------------------------------------------------------------------
# The FULL form: "C<n> model M, effort E on FULL, model M, effort E otherwise"
# --------------------------------------------------------------------------

FULL_FORM = {"C2": ((s.OPUS, "high"), (s.SONNET, "xhigh")), "C0": ((s.SONNET, "low"), (s.HAIKU5, "low"))}


@pytest.mark.parametrize("cls,profile,expected", [
    ("C2", "FULL", (s.OPUS, "high")), ("C2", "STANDARD", (s.SONNET, "xhigh")), ("C2", "LITE", (s.SONNET, "xhigh")),
    ("C0", "FULL", (s.SONNET, "low")), ("C0", "STANDARD", (s.HAIKU5, "low")),
    ("C3", "FULL", s.TABLES[ENG]["C3"]), ("C1", "FULL", s.TABLES[ENG]["C1"]),
])
def test_s1_the_full_form_takes_its_first_pair_on_a_full_ticket_and_its_second_otherwise(
        project, launch, cls, profile, expected):
    s.write_role(project, ENG, full=FULL_FORM)
    tk = s.ticket(project, ENG, cls, profile)
    s.assert_session(launch(ENG, tk), *expected, criticality=cls, **SESSION)


# --------------------------------------------------------------------------
# A role file with no table line: its default line, for every class
# --------------------------------------------------------------------------

@pytest.mark.parametrize("cls", s.CLASSES)
def test_s1_a_role_file_with_no_table_line_takes_its_default_line_for_every_class(project, launch, cls):
    s.write_role(project, ENG, table=None)
    tk = s.ticket(project, ENG, cls)
    s.assert_session(launch(ENG, tk), *s.DEFAULT, criticality=cls, model_source="role default",
                     effort_source="role default")


def test_s1_green_on_base_a_default_only_role_with_no_criticality_file_launches_as_before(project, launch):
    """Compatibility (interface 1.4, 3.2): nothing new is needed by a project that has not adopted RUBRIC-2."""
    s.write_role(project, ENG, table=None)
    s.drop_criticality(project)
    tk = s.ticket(project, ENG, "C2")
    result = launch(ENG, tk)
    s.b.assert_launched(result)
    assert (result.one("--model"), result.one("--effort")) == s.DEFAULT
    assert (result.record()["model_source"], result.record()["effort_source"]) == ("role default", "role default")


def test_s1_green_on_base_gov_launch_plan_prints_the_default_line_alone(project, sandbox, cli):
    """DEC-1167 (2): ``--plan`` keeps printing the role file's ``Launch default`` line, whatever the table says."""
    tk = s.ticket(project, ENG, "C3")
    done = s.b.run_gov(sandbox, project, "launch", "--plan", ENG, tk)
    assert done.returncode == 0 and done.stdout.strip() == f"model {s.DEFAULT[0]}, effort {s.DEFAULT[1]}", (
        done.describe())
    assert not s.b.calls(cli), "--plan started the CLI"


# --------------------------------------------------------------------------
# A missing or malformed `Launch by criticality` line refuses
# --------------------------------------------------------------------------

E = s.TABLES[ENG]


def _entries(*items):
    return s.HEAD + " " + "; ".join(items)


C3, C2, C1, C0 = (f"{c} model {m}, effort {e}" for c, (m, e) in ((c, E[c]) for c in s.CLASSES))
MALFORMED_TABLE = {
    "c0-missing": _entries(C3, C2, C1),
    "c3-missing": _entries(C2, C1, C0),
    "c2-missing": _entries(C3, C1, C0),
    "one-entry": _entries(C3),
    "no-entries": s.HEAD,
    "class-twice": _entries(C3, C3, C1, C0),
    "out-of-order": _entries(C2, C3, C1, C0),
    "ascending-order": _entries(C0, C1, C2, C3),
    "unknown-class": _entries(C3, C2, C1, C0.replace("C0", "C4")),
    "five-entries": _entries(C3, C2, C1, C0, C0),
    "alias-model": _entries(C3.replace(s.OPUS, "opus"), C2, C1, C0),
    "not-a-claude-model": _entries(C3.replace(s.OPUS, "gpt-5"), C2, C1, C0),
    "upper-case-model": _entries(C3, C2.replace(s.SONNET, "Claude-Sonnet-5-5"), C1, C0),
    "unknown-effort": _entries(C3, C2, C1.replace("xhigh", "extreme"), C0),
    "no-effort": _entries(C3, C2, C1, f"C0 model {s.HAIKU5}"),
    "comma-between-entries": s.HEAD + " " + ", ".join((C3, C2, C1, C0)),
    "no-space-after-semicolon": s.HEAD + " " + ";".join((C3, C2, C1, C0)),
    "no-space-after-the-comma": _entries(C3, C2.replace(", effort", ",effort"), C1, C0),
    "text-after-the-last-entry": _entries(C3, C2, C1, C0) + " (for now)",
    "full-form-without-otherwise": _entries(C3, f"C2 model {s.OPUS}, effort high on FULL", C1, C0),
    "full-form-without-its-second-pair": _entries(C3, f"C2 model {s.OPUS}, effort high on FULL, otherwise", C1, C0),
    "full-form-with-a-bad-model": _entries(
        C3, f"C2 model {s.OPUS}, effort high on FULL, model sonnet, effort high otherwise", C1, C0),
}


@pytest.mark.parametrize("case", sorted(MALFORMED_TABLE))
def test_s1_a_malformed_table_line_is_refused_naming_the_role_file(project, launch, case):
    s.write_role(project, ENG, table=None, lines=[MALFORMED_TABLE[case]])
    tk = s.ticket(project, ENG, "C2")
    s.refused(launch(ENG, tk), "engineer.md", "Launch by criticality")


def test_s1_a_second_table_line_is_refused(project, launch):
    s.write_role(project, ENG, table=None, lines=[s.table_line(E), s.table_line(E)])
    tk = s.ticket(project, ENG, "C2")
    s.refused(launch(ENG, tk), "engineer.md", "Launch by criticality")


@pytest.mark.parametrize("role", s.WORKER_ROLES)
def test_s1_a_malformed_table_line_refuses_every_role(project, launch, role):
    s.write_role(project, role, table=None, lines=[MALFORMED_TABLE["c0-missing"]])
    tk = s.ticket(project, role, "C1")
    s.refused(launch(role, tk), f"{role}.md", "Launch by criticality")
