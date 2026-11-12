"""KPI success 3 and failure 4 ("sudo, the research exception or the freeze changed").

Nothing else in the install rule changes (DEC-971 item 4, DEC-163, DEC-083): sudo is refused to every session, the
CTO's included; the research role's one exception holds, with or without the key; a frozen product refuses installs,
the CTO's included; a Bash call that installs nothing is decided as before, in a product whose key cannot be read
too; a call the guard refuses for what it writes stays refused for the CTO. The owner's prompt for the CTO's install
is held in ``test_w2_110_cto_asked.py``.

Each of these holds on the base and must still hold after the change (README, "Green on the base").
"""

from __future__ import annotations

import pytest

import w2_110_support as support
from w2_110_support import (COORDINATION, ENGINEER, ENGINEERING, EXPERIMENT, EXPERIMENT_REL, ORCHESTRATOR, RESEARCH,
                            Session, cto)
from w1_04_support import command_id

LEAD = Session("lead-on-an-engineer-s-ticket", ORCHESTRATOR, ENGINEERING.id)
ENGINEER_SESSION = Session("engineer-on-its-own-ticket", ENGINEER, ENGINEERING.id)
RESEARCH_IN_ITS_FOLDER = Session("research-in-its-experiment-folder", RESEARCH, EXPERIMENT.id, cwd_rel=EXPERIMENT_REL)
CTO_SUBAGENT = Session("orchestrator-subagent-in-the-cto-s-session", ORCHESTRATOR, COORDINATION.id, ORCHESTRATOR)


# --- sudo -----------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("command", support.SUDO, ids=[command_id(c) for c in support.SUDO])
def test_sudo_is_refused_to_the_cto(ask, command):
    """The hook itself refuses, whatever the generated settings' own ``sudo *`` rule does (DEC-083)."""
    answer = ask("key-by-id", cto(), command)
    assert answer.decision == "deny", f"`{command}` by the CTO was {answer.decision}, not refused: {answer.describe()}"


SUDO_SESSIONS = [
    ("key-by-id", LEAD),
    ("key-by-id", ENGINEER_SESSION),
    ("key-by-id", RESEARCH_IN_ITS_FOLDER),
    ("key-by-id", Session("no-role-on-the-coordination-ticket", None, COORDINATION.id)),
    ("key-by-id", CTO_SUBAGENT),
    ("no-roster", cto()),
    ("unparsable", cto()),
]


@pytest.mark.parametrize("configuration,session", SUDO_SESSIONS, ids=[f"{c}-{s}" for c, s in SUDO_SESSIONS])
def test_sudo_is_refused_to_every_other_session(ask, configuration, session):
    command = "sudo pip install requests"
    answer = ask(configuration, session, command)
    assert answer.decision == "deny", (
        f"`{command}` by {session} in {configuration} was {answer.decision}, not refused: {answer.describe()}")


# --- the research role's one exception (DEC-163) --------------------------------------------------------------

RESEARCH_FORMS = {
    "in-its-folder": (RESEARCH_IN_ITS_FOLDER, support.INSTALL),
    "cd-into-its-folder": (Session("research-at-the-project-root", RESEARCH, EXPERIMENT.id),
                           f"cd {EXPERIMENT_REL} && {support.INSTALL}"),
}
RESEARCH_CASES = [(c, f) for c in ("key-by-id", "no-roster", "no-key", "unparsable") for f in RESEARCH_FORMS]


@pytest.mark.parametrize("configuration,form", RESEARCH_CASES, ids=[f"{c}-{f}" for c, f in RESEARCH_CASES])
def test_the_research_exception_holds_with_or_without_the_key(ask, configuration, form):
    """An install inside the research ticket's own experiment folder is let through (no decision from the hook; the
    sandbox's write fence holds it to the folder), with the key set or not."""
    session, command = RESEARCH_FORMS[form]
    answer = ask(configuration, session, command)
    assert answer.decision == "allow", (
        f"`{command}` by the research session inside its experiment folder, in {configuration}, was "
        f"{answer.decision}: the research role's one exception (DEC-163) changed: {answer.describe()}")


# --- the freeze -----------------------------------------------------------------------------------------------

FROZEN_SESSIONS = [cto(), cto(COORDINATION.wbs, "cto-by-wbs-id"), CTO_SUBAGENT, LEAD, ENGINEER_SESSION,
                   RESEARCH_IN_ITS_FOLDER]


@pytest.mark.parametrize("session", FROZEN_SESSIONS, ids=str)
def test_a_frozen_product_refuses_every_install_the_cto_s_included(ask, session):
    answer = ask("key-by-id-frozen", session, support.INSTALL)
    assert answer.decision == "deny", (
        f"`{support.INSTALL}` by {session} in a frozen product was {answer.decision}, not refused: "
        f"{answer.describe()}")


# --- a Bash call that installs nothing ------------------------------------------------------------------------

ORDINARY_CASES = [(c, s, command) for c, s in (("key-by-id", cto()), ("key-by-id", LEAD), ("no-roster", cto()),
                                                ("unparsable", ENGINEER_SESSION))
                  for command in support.ORDINARY]


@pytest.mark.parametrize("configuration,session,command", ORDINARY_CASES,
                         ids=[f"{c}-{s}-{command_id(m)}" for c, s, m in ORDINARY_CASES])
def test_a_bash_call_that_installs_nothing_is_decided_as_before(ask, configuration, session, command):
    """No decision from the hook (the harness's own rules apply), as before; a roster that cannot be read changes
    only installs."""
    answer = ask(configuration, session, command)
    assert answer.decision == "allow", (
        f"`{command}` by {session} in {configuration} was {answer.decision}: a call that installs nothing is "
        f"decided as before: {answer.describe()}")


def test_the_cto_s_install_that_writes_where_the_guard_refuses_stays_refused(ask):
    """The install rule only escalates: a call the guard refuses for its write is not turned into an ask."""
    command = f"{support.INSTALL} > .gov-runtime/records.jsonl"
    answer = ask("key-by-id", cto(), command)
    assert answer.decision == "deny", (
        f"`{command}` by the CTO was {answer.decision}: the guard's refusal of the write must stand: "
        f"{answer.describe()}")
