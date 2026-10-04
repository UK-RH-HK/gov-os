"""W1-46 -- per-role settings: the role and the ticket, ``.gov-runtime/``, the temp directory, the network profile.

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
def test_both_variables_reach_the_guard(launch, guard, project, sandbox, role):
    """The guard, run with exactly the two values the session was given, decides as that role on that ticket."""
    result = launch(role)
    given_role, given_ticket = result.variable("GOV_ROLE"), result.variable("GOV_TICKET")
    assert given_role and given_ticket, "the session was given no GOV_ROLE or no GOV_TICKET"
    own = guard("Write", support.w47.write_input("Write", project / support.OWN_PATH[role]), given_role, given_ticket)
    support.w47.assert_allowed(own, f"a Write inside the ticket's paths by a launched {role}")
    other = guard("Write", support.w47.write_input("Write", project / "docs/notes.md"), given_role, given_ticket)
    support.w47.assert_denied_by_rule(other, f"a Write outside the ticket's paths by a launched {role}")


# --------------------------------------------------------------------------
# Success 10: .gov-runtime/ (DEC-180)
# --------------------------------------------------------------------------

@pytest.mark.parametrize("role", support.WORKER_ROLES)
def test_the_built_settings_deny_edits_under_gov_runtime(launch, project, sandbox, role):
    """The freeze flag, the snapshots, the findings and the records, and a new entry such as a link."""
    result = launch(role)
    open_paths = [rel for rel in support.PROTECTED_RUNTIME if not support.edit_denied(result, rel, project, sandbox)]
    assert open_paths == [], (
        f"no Edit deny rule of the built settings covers {open_paths}; rules: "
        f"{support.deny_rules(result.settings(), 'Edit')}"
    )


@pytest.mark.parametrize("role", support.WORKER_ROLES)
def test_the_built_settings_leave_scratch_writable(launch, project, sandbox, role):
    result = launch(role)
    closed = [rel for rel in support.SCRATCH_PATHS if support.edit_denied(result, rel, project, sandbox)]
    assert closed == [], (
        f"an Edit deny rule of the built settings covers {closed} under .gov-runtime/scratch/; rules: "
        f"{support.deny_rules(result.settings(), 'Edit')}"
    )


@pytest.mark.parametrize("role", support.WORKER_ROLES)
@pytest.mark.parametrize("tool", ("Write", "Edit"))
def test_a_file_tool_write_under_gov_runtime_is_refused_by_the_guard(guard, project, role, tool):
    """Success 10, "through a file tool": the guard's side. Holds before implementation for the three older roles."""
    for rel in (".gov-runtime/freeze", ".gov-runtime/findings.jsonl", ".gov-runtime/records.jsonl",
                ".gov-runtime/snapshots/keep.json"):
        result = guard(tool, support.w47.write_input(tool, project / rel), role)
        support.w47.assert_stopped(result, f"{tool} to {rel} by {role}")


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


# --------------------------------------------------------------------------
# Success 3: network profiles (DEC-158)
# --------------------------------------------------------------------------

@pytest.mark.parametrize("role", support.EMPTY_ALLOWLIST_ROLES)
def test_engineer_test_designer_and_auditor_get_an_empty_allowlist(launch, role):
    domains = support.allowed_domains(launch(role).settings())
    assert domains == [], f"the allowlist of a launched {role} is not empty: {domains}"


# The research allowlist (DEC-241) is in ``test_w1_46_research_allowlist.py``.
