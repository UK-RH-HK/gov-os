"""W2-201 fix X3 (DEC-1219 (5)): a lead launches the same way.

``gov launch orchestrator|lead <ticket> --fix "<line>"`` and ``gov launch orchestrator --chore "<line>"`` on W2-184's
fixture project and the stand-in CLI. The plan (a ready list, ``governance/project/orchestration/ready.txt``, line form
``<W2> <id> <brief> <log>``) names one in_progress ticket, ``DAEO-lrdy``; a closed ticket outside it, ``DAEO-ldfx``,
launches with ``--fix`` (the plan's check is not applied to a fix) and is refused without it. A lead writes no launch
record, so its kind is in its environment: ``GOV_LAUNCH_KIND`` and ``GOV_LAUNCH_LINE`` in the ``--settings`` env block
and the CLI process's environment, for a fix or a chore only; ``GOV_TICKET`` the owning ticket for a fix, absent for a
chore (``gov launch`` is run with a caller's ``GOV_TICKET``, as a lead launching would have); a chore lead's inbox
address (``GOV_MSG_ADDRESS``, ``<GOV_ROLE>:<ticket>`` today) has ``chore-<8 hex>`` where the ticket would be. A lead
launch without the flags is unchanged; the lead's refused options stay refused with ``--fix`` and ``--chore``; ``gov
pause`` and the gate stop it.
"""

from __future__ import annotations

import re

import pytest

import w2_201_x_support as x

s, b = x.s, x.b
FIX_TK, READY_TK = "DAEO-ldfx", "DAEO-lrdy"
CALLER = {"GOV_TICKET": x.CALLER_TICKET}
CHORE_ADDRESS = re.compile(rf"{x.LEAD_GOV_ROLE}:chore-[0-9a-f]{{8}}")


@pytest.fixture()
def plan(project):
    """The closed ticket outside the plan, the planned ticket and the ready list, committed (W2-201 S7's form)."""
    x.ticket(project, x.ENGINEER, "C2", "closed", tk=FIX_TK)
    s.ticket(project, x.ENGINEER, "C2", tk=READY_TK)
    b.write(project / x.READY_REL, f"# batch 1\nW2-201-ready {READY_TK} brief.md log.json\n")
    x.commit(project, "the leads' tickets and the ready list")
    return project


def _no_record(result):
    assert not result.new_records, f"a lead's launch wrote a launch record: {sorted(result.new_records)}"


@pytest.mark.parametrize("role", x.LEAD_ROLES)
def test_x3_a_lead_launches_with_fix_on_a_closed_ticket_outside_the_ready_list(sandbox, cli, plan, role):
    result = x.launch(sandbox, cli, role, FIX_TK, "--fix", x.FIX_LINE, extra_env=CALLER)
    x.launched(result)
    want = {"GOV_ROLE": x.LEAD_GOV_ROLE, "GOV_TICKET": FIX_TK, x.LAUNCH_KIND: "fix", x.LAUNCH_LINE: x.FIX_LINE}
    for name, env in zip(("--settings env block", "CLI process environment"), x.lead_env_pair(result)):
        got = {key: env.get(key) for key in want}
        assert got == want, f"the fix lead's {name} holds {got}, not {want}"
    _no_record(result)


def test_x3_the_same_lead_without_fix_is_refused_by_the_plan(sandbox, cli, plan):
    """Guard on the base: the plan's check refuses a ticket outside the ready list."""
    s.refused(x.launch(sandbox, cli, "orchestrator", FIX_TK), FIX_TK)


def test_x3_a_lead_fix_on_an_unknown_ticket_is_refused(sandbox, cli, plan):
    s.refused(x.launch(sandbox, cli, "orchestrator", "DAEO-none", "--fix", x.FIX_LINE), "DAEO-none")


def test_x3_a_lead_launches_with_chore_and_no_ticket(sandbox, cli, plan):
    result = x.launch(sandbox, cli, "orchestrator", "--chore", x.CHORE_LINE, extra_env=CALLER)
    x.launched(result)
    want = {"GOV_ROLE": x.LEAD_GOV_ROLE, x.LAUNCH_KIND: "chore", x.LAUNCH_LINE: x.CHORE_LINE}
    block, env = x.lead_env_pair(result)
    for name, held in (("--settings env block", block), ("CLI process environment", env)):
        got = {key: held.get(key) for key in want}
        assert got == want, f"the chore lead's {name} holds {got}, not {want}"
        assert "GOV_TICKET" not in held, f"the chore lead's {name} holds GOV_TICKET: {held.get('GOV_TICKET')!r}"
    address = env.get("GOV_MSG_ADDRESS")
    assert isinstance(address, str) and CHORE_ADDRESS.fullmatch(address), (
        f"the chore lead's inbox address is {address!r}, not {x.LEAD_GOV_ROLE}:chore-<8 hex>")
    _no_record(result)


def test_x3_a_lead_launch_without_the_flags_is_unchanged(sandbox, cli, plan):
    """Guard on the base: the planned ticket starts; its env has no GOV_LAUNCH_* key."""
    result = x.launch(sandbox, cli, "orchestrator", READY_TK)
    x.launched(result)
    for name, held in zip(("--settings env block", "CLI process environment"), x.lead_env_pair(result)):
        assert held.get("GOV_TICKET") == READY_TK, f"the lead's {name} GOV_TICKET is {held.get('GOV_TICKET')!r}"
        added = sorted(key for key in held if key.startswith("GOV_LAUNCH_"))
        assert not added, f"a lead launched without --fix or --chore has {added} in its {name}"
    _no_record(result)


REFUSED_FOR_A_LEAD = {
    "reason": ("--reason", "why the effort"),
    "trial": ("--trial", "t-1"),
    "owner-named": ("--owner-named", "DEC-1219"),
    "projection-usd": ("--projection-usd", "5"),
}


@pytest.mark.parametrize("kind", ["fix", "chore"])
@pytest.mark.parametrize("option", list(REFUSED_FOR_A_LEAD))
def test_x3_a_lead_s_refused_options_stay_refused_with_fix_and_chore(sandbox, cli, plan, kind, option):
    head = (FIX_TK, "--fix", x.FIX_LINE) if kind == "fix" else ("--chore", x.CHORE_LINE)
    x.usage_error(x.launch(sandbox, cli, "orchestrator", *head, *REFUSED_FOR_A_LEAD[option]))


@pytest.mark.parametrize("how", ["pause", "gate"])
def test_x3_the_planted_pause_and_gate_stop_a_planned_lead(sandbox, cli, plan, how):
    """Guard on the base, the plants' own check: what stops a fix or chore lead below stops a planned lead today."""
    env, words = x.stop(sandbox, how)
    x.stopped(x.launch(sandbox, cli, "orchestrator", READY_TK, extra_env=env), words)


@pytest.mark.parametrize("kind", ["fix", "chore"])
@pytest.mark.parametrize("how", ["pause", "gate"])
def test_x3_gov_pause_and_the_gate_stop_a_lead_fix_and_chore(sandbox, cli, plan, kind, how):
    env, words = x.stop(sandbox, how)
    head = (FIX_TK, "--fix", x.FIX_LINE) if kind == "fix" else ("--chore", x.CHORE_LINE)
    x.stopped(x.launch(sandbox, cli, "orchestrator", *head, extra_env=env), words)
