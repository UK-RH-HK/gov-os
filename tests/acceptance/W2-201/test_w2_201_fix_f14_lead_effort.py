"""W2-201 fix F14: ticket leads (and fix and chore leads) run Sonnet at ``--effort medium``.

``gov launch orchestrator|lead`` (a feature, ``--fix`` or ``--chore``) starts the lead with ``--model claude-sonnet-5-5``
and ``--effort medium``, each once; the ``ticket-lead`` role file (kernel folder and its three generated copies) gives
Sonnet, medium as its launch default. Every worker keeps the effort its table gives (guard). Read: the arguments the
stand-in CLI received, the role reader (``gov.launch.role``) on each copy of the role file.
"""

from __future__ import annotations

import pytest

import w2_201_support as k
import w2_201_x_support as x

s, b = x.s, x.b
FIX_TK, READY_TK = "DAEO-ldfx", "DAEO-lrdy"
CALLER = {"GOV_TICKET": x.CALLER_TICKET}


@pytest.fixture()
def plan(project):
    x.ticket(project, x.ENGINEER, "C2", "closed", tk=FIX_TK)
    s.ticket(project, x.ENGINEER, "C2", tk=READY_TK)
    b.write(project / x.READY_REL, f"# batch 1\nW2-201-ready {READY_TK} brief.md log.json\n")
    x.commit(project, "the leads' tickets and the ready list")
    return project


def _lead(sandbox, cli, role, kind):
    head = {"feature": (READY_TK,), "fix": (FIX_TK, "--fix", x.FIX_LINE), "chore": ("--chore", x.CHORE_LINE)}[kind]
    return x.launch(sandbox, cli, role, *head, extra_env=CALLER)


@pytest.mark.parametrize("kind", ["feature", "fix", "chore"])
@pytest.mark.parametrize("role", x.LEAD_ROLES)
def test_a_lead_runs_sonnet_at_effort_medium(sandbox, cli, plan, role, kind):
    """Red on the base: the launcher gives a lead no ``--effort`` (the CLI's own default applies)."""
    result = x.launched(_lead(sandbox, cli, role, kind))
    x.assert_line(result, k.SONNET, "medium")


@pytest.mark.parametrize("cls,effort", [("C3", "high"), ("C2", "high"), ("C1", "xhigh"), ("C0", "low")])
def test_a_worker_keeps_the_effort_its_table_gives(project, launch, cls, effort):
    """Guard (green on the base): the engineer's effort per class is the table's; the lead's medium touches no worker."""
    tk = s.ticket(project, k.ENGINEER, cls)
    result = launch(k.ENGINEER, tk)
    b.assert_launched(result)
    assert result.values("--effort") == [effort], f"the engineer at {cls} got --effort {result.values('--effort')}"


@pytest.mark.parametrize("location", k.LOCATIONS)
def test_the_ticket_lead_role_file_gives_sonnet_medium(tmp_path, location):
    """The kernel file and each generated copy: ``Launch default`` model claude-sonnet-5-5, effort medium, no table line.
    Red on the base: the line says effort high."""
    from gov.launch import role

    tree = k.plant_role_copy(tmp_path, location, "ticket-lead")
    assert role.launch_default(tree, "ticket-lead") == (k.SONNET, "medium")
    assert role.read_by_criticality(tree, "ticket-lead") is None


@pytest.mark.parametrize("name", sorted(set(k.TABLE) - {"ticket-lead"}))
def test_every_other_role_file_keeps_its_launch_default(tmp_path, name):
    """Guard (green on the base): DEC-1225's model and effort for the other eight roles are unchanged."""
    from gov.launch import role

    tree = k.plant_role_copy(tmp_path, k.ROLES_REL, name)
    assert role.launch_default(tree, name) == k.TABLE[name][0]
