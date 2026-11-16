"""W2-60b, KPI success-7, success-8 and failure-1 -- the launchable roles are read from the kernel's role files.

success-7 [DEC-946 (W3-P09), DEC-826 Q1]: "The launcher's set of launchable roles (today the fixed WORKER_ROLES and
OWN_TICKET_ROLES tuples in launcher.py) is read from the kernel's role files, so a new role is a file, not a code
change; a role file that is missing or unreadable refuses the launch; the five roles launch exactly as before." Verify:
a planted kernel role file for a sixth role launches with no code change; a planted missing or unreadable role file
refuses the launch; the five roles launch as before (the existing launcher tests pass unchanged).

success-8 [DEC-946 (W3-P09)]: "A role named in a ticket but with no role file is refused at launch, naming the role."
Verify: a planted ticket naming a role with no role file: ``gov launch`` refuses and its message names the role.

failure-1: "A fixed list of launchable roles left in code." Verify: a search of ``launcher.py`` finds no fixed
WORKER_ROLES or OWN_TICKET_ROLES tuple; the S7 planted sixth role launches with no code change.

Interface: the role files ``gov.launch.role`` reads (``template/governance/kernel/roles/<role>.md``); the CTO's
(``orchestrator.md``), the Senior Engineer's and the ticket lead's files do not become launchable by ``gov launch``; a
sixth worker role file launches with no code change. Every refusal here follows a control launch that starts, so that
a refusal is shown to come from the role file and not from a fixed list. The planted sixth role's file is of the
kernel's worker form (``worker_role_text``); its template is planted as ``.claude/templates/role-<role>.md`` and
``<role>.md`` (how a new role's template is found is an open question, see the README).
"""

from __future__ import annotations

import re

import w2_60b_support as t

b, s = t.b, t.s
SIXTH, QA, ABSENT = t.SIXTH, t.QA, t.ABSENT
TK6, TKQ, TKA = "DAEO-zq06", "DAEO-zq07", "DAEO-zq08"


def _launched(result, role):
    b.assert_launched(result)
    assert result.record()["role"] == role, f"the launch record's role is not {role!r}"
    assert result.env_block().get("GOV_ROLE") == role, f"the session's GOV_ROLE is not {role!r}: {result.env_block()}"
    return result


def test_s7_a_planted_sixth_worker_role_file_launches_with_no_code_change(project, launch):
    t.plant_roles(project, (SIXTH,))
    t.ticket(project, TK6, SIXTH)
    result = _launched(launch(SIXTH, TK6), SIXTH)
    assert b.option_values(result.args, "--model") == [t.SONNET], (
        f"the sixth role's session does not run on its role file's default model: {result.args}")


def test_s7_the_kernel_s_qa_engineer_role_file_launches_as_a_sixth_role(project, launch):
    t.plant_roles(project, (QA,))
    t.ticket(project, TKQ, QA)
    _launched(launch(QA, TKQ), QA)


def test_s7_a_missing_role_file_refuses_where_the_same_role_with_its_file_launches(project, launch):
    t.plant_roles(project, (SIXTH,))
    t.ticket(project, TK6, SIXTH)
    _launched(launch(SIXTH, TK6), SIXTH)
    b.role_path(project, SIXTH).unlink()
    s.refused(launch(SIXTH, TK6), SIXTH)


def test_s7_an_unreadable_role_file_refuses_where_the_same_role_readable_launches(project, launch):
    t.plant_roles(project, (SIXTH,))
    t.ticket(project, TK6, SIXTH)
    _launched(launch(SIXTH, TK6), SIXTH)
    path = b.role_path(project, SIXTH)
    path.chmod(0o000)
    try:
        s.refused(launch(SIXTH, TK6), SIXTH)
    finally:
        path.chmod(0o644)


def test_s7_a_missing_role_file_of_one_of_the_five_roles_still_refuses_naming_it(project, launch):
    """A guard: what refuses today keeps refusing (green on the base)."""
    _launched(launch(t.ENGINEER, b.T.tk), t.ENGINEER)
    b.role_path(project, t.ENGINEER).unlink()
    s.refused(launch(t.ENGINEER, b.T.tk), t.ENGINEER)


def test_s8_a_ticket_naming_a_role_with_no_role_file_is_refused_naming_the_role(project, launch):
    t.plant_roles(project, (SIXTH,))
    t.ticket(project, TK6, SIXTH)
    t.ticket(project, TKA, ABSENT)
    _launched(launch(SIXTH, TK6), SIXTH)
    assert not b.role_path(project, ABSENT).exists()
    s.refused(launch(ABSENT, TKA), ABSENT)


def test_s7_the_cto_s_senior_engineer_s_and_ticket_lead_s_files_do_not_become_launchable(project, launch):
    t.plant_roles(project, (SIXTH,))
    t.plant_coordinators(project)
    t.ticket(project, TK6, SIXTH)
    _launched(launch(SIXTH, TK6), SIXTH)
    for role, tk in (("senior-engineer", "DAEO-zq0s"), ("ticket-lead", "DAEO-zq0l")):
        t.ticket(project, tk, role)
        s.refused(launch(role, tk), role)


def test_f1_the_launcher_holds_no_fixed_tuple_of_launchable_roles():
    text = (t.REPO_ROOT / t.LAUNCHER_REL).read_text(encoding="utf-8")
    found = [line.strip() for line in text.splitlines()
             if re.match(r"\s*(WORKER_ROLES|OWN_TICKET_ROLES)\s*(:[^=]*)?=", line)]
    assert not found, f"{t.LAUNCHER_REL} still holds a fixed list of launchable roles: {found}"
