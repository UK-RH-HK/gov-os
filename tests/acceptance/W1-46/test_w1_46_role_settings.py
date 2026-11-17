"""W1-46 -- per-role settings: the role and the ticket, and the temp directory.

Emergency 2 (docs/emergency-2/EMERGENCY-2.md 2.2, 2.4, 6.1; release 0.1.2): the launcher writes no sandbox block
and no deny rule of its own, so the cases of KPI success 3 (the empty network allowlist) and success 10 (the
``Edit`` deny rules for ``.gov-runtime/**`` and the guard's refusal there) are retired. The lines below are kept as
the KPI wrote them.

KPI success 2 [CAP-61.b]: "For each worker role (engineer,
independent-test-designer, independent-auditor, research; a research or
experiment session runs as GOV_ROLE=research) it builds a --settings file with
the sandbox block and the role's Edit deny rules, and sets GOV_ROLE and
GOV_TICKET; an acceptance test shows that a launched worker is sandboxed and
that both variables reach the guard (DEC-161)".

KPI success 3 [CAP-61.c]: "engineer, independent test designer and independent
auditor get an empty allowlist; research or experiment work gets an allowlist
built from an owner-extensible list (GitHub, PyPI, npm, Hugging Face, arXiv,
documentation sites)". The empty allowlist is here; the research allowlist
(DEC-241) is in ``test_w1_46_research_allowlist.py``.

KPI success 7 [CAP-61.d]: "It sets a per-session temp directory for each worker
session".

KPI success 10 (DEC-180, DEC-176): "The settings it builds for every worker role
carry an Edit deny rule for .gov-runtime/** except .gov-runtime/scratch/**".

No session is started. The parts of these lines that need one ("a launched
worker is sandboxed", "the profile applies", "whether the session uses it") are
in ``test_w1_46_live_sessions.py``.

Rewrite-Reason: DEC-953 item 2 (W2-90, DEC-957, DEC-906). The cases that asked this repository's live guard now
ask the kernel's: the ``kernel_*`` fixtures are W1-46's launch project built on a project generated from the
template, whose ``.claude/settings.json`` rulesync generates from the template's sources, and the PreToolUse
lines those settings register, run from ``governance/kernel/hooks/`` (``tests/acceptance/W2-90/README.md``).
Each moved case names its fixtures by their old names in its first line; its verdict is the same.
"""

from __future__ import annotations

import os

import pytest

import w1_46_support as support


# --------------------------------------------------------------------------
# Success 2: GOV_ROLE and GOV_TICKET
# --------------------------------------------------------------------------

@pytest.mark.parametrize("role", support.WORKER_ROLES)
def test_the_session_is_given_its_role_and_its_ticket(launch, role):
    result = launch(role)
    assert result.variable("GOV_ROLE") == role, f"GOV_ROLE is {result.variable('GOV_ROLE')!r}, not {role!r}"
    assert result.variable("GOV_TICKET") == support.TICKET_OF[role], (
        f"GOV_TICKET is {result.variable('GOV_TICKET')!r}, not {support.TICKET_OF[role]!r}"
    )


@pytest.mark.parametrize("role", support.WORKER_ROLES)
def test_the_role_and_the_ticket_are_in_the_settings_env_block(launch, project, role):
    """DEC-183: the ``env`` block of ``--settings`` "overrides the env block in .claude/settings.local.json".

    The project's local settings name the orchestrator, as this repository's do.
    A variable set in the process environment alone would lose to them.
    """
    support.write(project, support.LOCAL_SETTINGS_REL,
                  '{"env": {"GOV_ROLE": "orchestrator", "GOV_TICKET": "DAEO-zz91"}}\n')
    block = launch(role).settings().get("env")
    assert isinstance(block, dict), "the built settings carry no env block"
    assert (block.get("GOV_ROLE"), block.get("GOV_TICKET")) == (role, support.TICKET_OF[role]), (
        f"the env block of the built settings is {block}"
    )


@pytest.mark.parametrize("role", support.WORKER_ROLES)
def test_both_variables_reach_the_guard(kernel_launch, kernel_guard, kernel_project, kernel_sandbox, role):
    """The guard, run with exactly the two values the session was given, decides as that role on that ticket."""
    guard, project, launch, sandbox = kernel_guard, kernel_project, kernel_launch, kernel_sandbox
    result = launch(role)
    given_role, given_ticket = result.variable("GOV_ROLE"), result.variable("GOV_TICKET")
    assert given_role and given_ticket, "the session was given no GOV_ROLE or no GOV_TICKET"
    own = guard("Write", support.w47.write_input("Write", project / support.OWN_PATH[role]), given_role, given_ticket)
    support.w47.assert_allowed(own, f"a Write inside the ticket's paths by a launched {role}")
    other = guard("Write", support.w47.write_input("Write", project / "docs/notes.md"), given_role, given_ticket)
    support.w47.assert_denied_by_rule(other, f"a Write outside the ticket's paths by a launched {role}")


# --------------------------------------------------------------------------
# Success 7: a per-session temp directory (DEC-159)
# --------------------------------------------------------------------------

def _session_directories(result, sandbox):
    shared = os.path.realpath(sandbox.tmpdir)
    return {path: exists for path, exists in result.session()["directories"].items()
            if os.path.realpath(path) != shared}


@pytest.mark.parametrize("role", support.WORKER_ROLES)
def test_the_launcher_sets_a_temp_directory_of_the_sessions_own(launch, sandbox, role):
    """A temp-directory variable of the session names a directory other than the shared one, and it exists."""
    found = _session_directories(launch(role), sandbox)
    assert found, "the session's temp-directory variables all name the shared temp directory, or none is set"
    assert all(found.values()), f"a temp directory the launcher set does not exist when the CLI starts: {found}"


def test_two_sessions_get_two_temp_directories(launch, sandbox):
    """ "Per-session": two launches of the same role on the same ticket do not share one."""
    first = set(_session_directories(launch(support.ENGINEER), sandbox))
    second = set(_session_directories(launch(support.ENGINEER), sandbox))
    assert first and second, "no temp directory of the session's own was set"
    assert not (first & second), f"two sessions were given the same temp directory: {sorted(first & second)}"
