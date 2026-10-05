"""KPI success 6 (DEC-386): the launcher starts a product-spec worker.

"gov launch starts a product-spec worker sandboxed, with an empty network
allowlist."

As W1-46 left it, ``gov launch product-spec <ticket>`` is refused: "not a
worker role". DEC-386 makes product-spec a launched role. Nothing of the
launcher is weakened for it: the session is what an engineer's is, under the
role's own name.

- **Sandboxed, fail closed** (DEC-231 to DEC-234): the strict sandbox settings
  W1-46 pins for every worker, and an allowlist with no host in it, whatever
  the research allowlist holds.
- **The same deny rules** (DEC-311, DEC-315): the protected runtime files, the
  acceptance tests, the tickets, ``.claude/``; the scratch folder stays
  writable. One Read deny rule per held-out path (DEC-218), built here from a
  stand-in directory this suite makes up.
- **Identity**: ``GOV_ROLE=product-spec`` and ``GOV_TICKET``, which the guard
  then decides by.
- **A temp folder of its own**, removed when the session ends (KPI success 5).
- **Its own ticket only.** DEC-242 refuses "a ticket of another role"; DEC-271
  lifts that for the two independent roles and for no other. The role file
  says the same: "the allowed_paths of its own in_progress ticket, whose role
  is product-spec". So a product-spec session is refused on an engineer's
  ticket.
- **Every refusal of W1-46 holds for the new role**: a representative of each
  kind is run with it. Each is preceded by its control, the same launch
  without the fault, so that none passes for the wrong reason.
- **A role nobody knows is still refused**, and so is the orchestrator.
- **The roster** (DEC-163) names the session and the profile of every launched
  role. The committed entry of product-spec must name them too. The ticket
  lead changes ``governance/project/roster.yaml``; the engineer cannot.
"""

from __future__ import annotations

import pytest

import w1_28_launch_support as support

w46, w47 = support.w46, support.w47

PRODUCT_SPEC = support.PRODUCT_SPEC
TICKET = support.PRODUCT_SPEC_TICKET
NEW_TICKET = "DAEO-zz98"
ACCEPTANCE = ("tests/acceptance/W1-90/test_fixture.py", "tests/acceptance/W1-99/test_new.py")
TICKETS = (f".tickets/{TICKET}.md", f".tickets/{support.ENGINEER_TICKET}.md", ".tickets/DAEO-zz99.md")
CLAUDE = (w46.SETTINGS_REL, w46.LOCAL_SETTINGS_REL, ".claude/agents/product-spec.md", ".claude/commands/new.md")


def _started(launch):
    result = launch(PRODUCT_SPEC)
    assert result.run.returncode == 0, f"gov launch {PRODUCT_SPEC} {TICKET} did not start a session\n{result.describe()}"
    result.session()
    return result


def _open(result, paths, project, sandbox):
    return [rel for rel in paths if not w46.edit_denied(result, rel, project, sandbox)]


# --------------------------------------------------------------------------
# A session is started, sandboxed, with no host
# --------------------------------------------------------------------------

def test_the_launcher_starts_one_product_spec_session(launch, launch_project):
    result = _started(launch)
    session = result.session()
    assert session["argv0"].endswith(w46.CLI_REL), f"the session was not started from ~/{w46.CLI_REL}: {session['argv0']}"
    assert session["cwd"] == str(launch_project.resolve()), f"the session runs in {session['cwd']}, not in the project"


def test_the_product_spec_session_is_sandboxed_and_fails_closed(launch):
    faults = w46.sandbox_faults(_started(launch).settings())
    assert faults == [], f"the settings of a launched {PRODUCT_SPEC} session are not the strict sandbox: {faults}"


def test_the_product_spec_session_has_an_empty_network_allowlist(launch):
    domains = w46.allowed_domains(_started(launch).settings())
    assert domains == [], f"a launched {PRODUCT_SPEC} session may reach {domains}; its allowlist is empty (DEC-386)"


def test_the_research_allowlist_gives_the_product_spec_session_no_host(launch, launch_project):
    """The research allowlist is research's alone: a host the owner adds there reaches no product-spec session."""
    w46.rewrite_allowlist(launch_project, lambda hosts: hosts + [w46.ADDED_HOST])
    domains = w46.allowed_domains(_started(launch).settings())
    assert domains == [], f"a launched {PRODUCT_SPEC} session may reach {domains}"


def test_the_extra_cli_arguments_reach_the_product_spec_session(launch):
    """DEC-183: what follows ``--`` is the session's, after the launcher's own ``--settings``."""
    result = launch(PRODUCT_SPEC, None, "-p", "Do the ticket's work.", "--max-turns", "8")
    assert result.session()["args"][-4:] == ["-p", "Do the ticket's work.", "--max-turns", "8"], result.describe()
    assert w46.sandbox_faults(result.settings()) == []


# --------------------------------------------------------------------------
# The same deny rules
# --------------------------------------------------------------------------

def test_the_product_spec_settings_deny_edits_of_the_protected_runtime_files(launch, launch_project, sandbox):
    """DEC-311."""
    result = _started(launch)
    opened = _open(result, w46.PROTECTED_RUNTIME, launch_project, sandbox)
    assert opened == [], f"no Edit deny rule of a launched {PRODUCT_SPEC}'s settings covers {opened}"
    closed = [rel for rel in w46.SCRATCH_PATHS if w46.edit_denied(result, rel, launch_project, sandbox)]
    assert closed == [], f"the scratch folder is denied to a launched {PRODUCT_SPEC}: {closed}"


@pytest.mark.parametrize("paths", (ACCEPTANCE, TICKETS, CLAUDE), ids=("acceptance-tests", "tickets", "dot-claude"))
def test_the_product_spec_settings_deny_edits_of_the_three_trees(launch, launch_project, sandbox, paths):
    """DEC-315: every role but the independent test designer is denied the acceptance tests; every role the rest."""
    result = _started(launch)
    opened = _open(result, paths, launch_project, sandbox)
    assert opened == [], (
        f"no Edit deny rule of a launched {PRODUCT_SPEC}'s settings covers {opened}; rules: "
        f"{w46.deny_rules(result.settings(), 'Edit')}"
    )


def test_a_ticket_that_names_the_three_trees_opens_none_of_them(launch, launch_project, sandbox):
    """Fail closed: the product-spec ticket's ``allowed_paths`` take nothing out of the built rules."""
    ticket = w46.write_ticket(launch_project, NEW_TICKET, PRODUCT_SPEC,
                              allowed_paths=("docs/spec/**", ".claude/agents/**", ".tickets/**", "tests/acceptance/**"))
    result = launch(PRODUCT_SPEC, ticket)
    assert result.run.returncode == 0, f"gov launch refused the ticket\n{result.describe()}"
    opened = _open(result, (CLAUDE[2], TICKETS[0], ACCEPTANCE[0]), launch_project, sandbox)
    assert opened == [], f"a product-spec ticket that names {opened} took them out of the Edit deny rules"


def test_the_product_spec_settings_carry_the_read_deny_rule_for_the_held_out_path(launch, stand_in):
    """DEC-218, on a stand-in path made up by this suite."""
    built = _started(launch).settings()
    assert len(w47.held_out_read_rules(built, str(stand_in))) == 1, (
        f"the built settings do not carry exactly one Read deny rule for the configured stand-in path; Read rules: "
        f"{w46.deny_rules(built, 'Read')}"
    )


def test_a_broken_held_out_file_refuses_the_product_spec_launch(launch, launch_project):
    _started(launch)
    w47.write_config(launch_project, f"{w47.CONFIG_KEY}: []\n")
    w46.assert_refused(launch(PRODUCT_SPEC), "held-out", w47.CONFIG_KEY)


# --------------------------------------------------------------------------
# Identity, and the temp folder
# --------------------------------------------------------------------------

def test_the_product_spec_session_knows_its_role_and_ticket(launch):
    result = _started(launch)
    assert result.variable("GOV_ROLE") == PRODUCT_SPEC, f"GOV_ROLE is {result.variable('GOV_ROLE')!r}"
    assert result.variable("GOV_TICKET") == TICKET, f"GOV_TICKET is {result.variable('GOV_TICKET')!r}"
    block = result.settings().get("env") or {}
    assert block.get("GOV_ROLE") == PRODUCT_SPEC and block.get("GOV_TICKET") == TICKET, (
        f"the identity is not in the settings' env block, where the session's own environment cannot replace it "
        f"(DEC-183): {sorted(block)}"
    )


@pytest.mark.parametrize("tool", ("Write", "Edit"))
def test_the_guard_decides_by_the_identity_the_launcher_gave(launch, launch_project, sandbox, tool):
    """The role and the ticket of the session, handed to the guard: its own path is allowed, another is denied."""
    result = _started(launch)
    role, ticket = result.variable("GOV_ROLE"), result.variable("GOV_TICKET")
    own = w46.ask_guard(launch_project, sandbox, tool,
                        w47.write_input(tool, launch_project / support.PRODUCT_SPEC_OWN_PATH), role, ticket)
    w47.assert_allowed(own, f"{tool} to {support.PRODUCT_SPEC_OWN_PATH} by the launched {PRODUCT_SPEC} session")
    other = w46.ask_guard(launch_project, sandbox, tool,
                          w47.write_input(tool, launch_project / support.PRODUCT_SPEC_OTHER_PATH), role, ticket)
    w47.assert_denied_by_rule(other, f"{tool} to {support.PRODUCT_SPEC_OTHER_PATH}, outside the ticket's paths")


def test_the_product_spec_session_has_a_temp_folder_of_its_own_and_may_write_there(launch, cli):
    """DEC-159: the folder is the session's ``TMPDIR`` and the one place outside the project its sandbox may write."""
    support.plan(cli, files={"work/notes.txt": "notes\n"})
    result = _started(launch)
    folder = support.temp_folder(result)
    assert result.variable("TMPDIR") == str(folder), f"TMPDIR of the session is {result.variable('TMPDIR')!r}"
    writable = (result.settings().get("sandbox") or {}).get("filesystem", {}).get("allowWrite", [])
    assert any(str(entry).rstrip("/").endswith(str(folder)) for entry in writable), (
        f"the sandbox of the session may not write its own temp folder {folder}: allowWrite is {writable}"
    )
    support.assert_removed(folder, f"after the {PRODUCT_SPEC} session ended")


# --------------------------------------------------------------------------
# Its own ticket only, and every refusal of W1-46
# --------------------------------------------------------------------------

@pytest.mark.parametrize("ticket_role", (support.ENGINEER, w46.RESEARCH, w46.AUDITOR))
def test_a_product_spec_session_is_refused_on_a_ticket_of_another_role(launch, launch_project, ticket_role):
    """DEC-242, and DEC-271 exempts the two independent roles alone."""
    _started(launch)
    ticket = w46.TICKET_OF[ticket_role]
    w46.assert_refused(launch(PRODUCT_SPEC, ticket), "role", ticket_role)


@pytest.mark.parametrize("role", (support.ENGINEER, w46.RESEARCH))
def test_no_implementing_role_is_launched_on_the_product_spec_ticket(launch, role):
    """The other direction of the same rule, with the control: product-spec is launched on it."""
    _started(launch)
    w46.assert_refused(launch(role, TICKET), "role", PRODUCT_SPEC)


@pytest.mark.parametrize("role", (w46.TEST_DESIGNER, w46.AUDITOR))
def test_the_independent_roles_are_launched_on_a_product_spec_ticket(launch, role):
    """DEC-271, unchanged: "any ticket that is in_progress". Their work on product-spec's ticket needs it."""
    _started(launch)
    result = launch(role, TICKET)
    assert result.run.returncode == 0, f"gov launch {role} {TICKET} was refused\n{result.describe()}"
    assert result.variable("GOV_ROLE") == role and result.variable("GOV_TICKET") == TICKET


def test_an_unknown_ticket_refuses_the_product_spec_launch(launch):
    _started(launch)
    w46.assert_refused(launch(PRODUCT_SPEC, "DAEO-zz00"), "ticket", "DAEO-zz00")


@pytest.mark.parametrize("status", ("open", "closed"))
def test_a_ticket_that_is_not_in_progress_refuses_the_product_spec_launch(launch, launch_project, status):
    _started(launch)
    ticket = w46.write_ticket(launch_project, NEW_TICKET, PRODUCT_SPEC, status=status)
    w46.assert_refused(launch(PRODUCT_SPEC, ticket), "in_progress", "status", status)


CLI_ARGUMENTS = {
    "skip-permissions": ("--dangerously-skip-permissions",),
    "bypass-mode": ("--permission-mode", "bypassPermissions"),
    "bypass-mode-joined": ("--permission-mode=bypassPermissions",),
    "add-dir": ("--add-dir", "/w1-28-added-directory"),
    "settings": ("--settings", '{"sandbox": {"enabled": false}}'),
    "bare": ("--bare",),
}
REASON = ("bypass", "skip-permissions", "permission", "add-dir", "director", "settings", "bare", "hook")


@pytest.mark.parametrize("name", sorted(CLI_ARGUMENTS))
def test_the_launcher_refuses_the_same_cli_arguments_for_product_spec(launch, name):
    """DEC-313 and W1-46: no bypass, no added directory, no settings but the launcher's, no skipped hooks."""
    _started(launch)
    w46.assert_refused(launch(PRODUCT_SPEC, None, "-p", "Do the ticket's work.", *CLI_ARGUMENTS[name]), *REASON)


def _no_guard(data):
    data.pop("hooks", None)


def _all_hooks_off(data):
    data["disableAllHooks"] = True


def _sandbox_key(data):
    data["sandbox"] = {"enabled": False}


def _bypass_mode(data):
    data.setdefault("permissions", {})["defaultMode"] = "bypassPermissions"


REPOSITORY_SETTINGS = {"no-guard-hook": _no_guard, "all-hooks-off": _all_hooks_off, "sandbox-key": _sandbox_key,
                       "bypass-default-mode": _bypass_mode}


@pytest.mark.parametrize("name", sorted(REPOSITORY_SETTINGS))
def test_repository_settings_that_would_unwire_the_session_refuse_the_product_spec_launch(launch, launch_project,
                                                                                         name):
    _started(launch)
    w46.rewrite_settings(launch_project, REPOSITORY_SETTINGS[name])
    w46.assert_refused(launch(PRODUCT_SPEC), "guard", "hook", "sandbox", "bypass", "permission")


def test_the_launcher_refuses_product_spec_without_the_cli_at_its_place(launch, cli):
    """DEC-205: the CLI is started from ``~/.local/bin/claude`` or not at all; never the bare name on PATH."""
    _started(launch)
    cli.path.unlink()
    w46.assert_refused(launch(PRODUCT_SPEC), "claude", "CLI")


# --------------------------------------------------------------------------
# Who is still not launched
# --------------------------------------------------------------------------

@pytest.mark.parametrize("role", ("orchestrator", "no-such-role", "Product-Spec", "product_spec", "product-spec "))
def test_a_role_that_is_not_launched_is_still_refused(launch, role):
    """The control first. Then the orchestrator (DEC-161), a role nobody knows, and near-spellings of the new one."""
    _started(launch)
    w46.assert_refused(launch(role, TICKET), "role")


# --------------------------------------------------------------------------
# The roster
# --------------------------------------------------------------------------

def test_the_committed_roster_names_the_product_spec_session_and_its_profile():
    """DEC-163: the roster names how each launched role is started and with which network profile.

    Red until the ticket lead changes ``governance/project/roster.yaml``: the
    file is outside the engineer's paths.
    """
    entry = support.committed_roster_entry(PRODUCT_SPEC)
    assert entry.get("session") == support.ROSTER_SESSION, (
        f"{support.ROSTER_REL}: the entry of {PRODUCT_SPEC} has session {entry.get('session')!r}, not "
        f"{support.ROSTER_SESSION!r}"
    )
    assert entry.get("network_profile") == support.ROSTER_PROFILE, (
        f"{support.ROSTER_REL}: the entry of {PRODUCT_SPEC} has network_profile {entry.get('network_profile')!r}, "
        f"not {support.ROSTER_PROFILE!r}"
    )
    for key in ("role_file", "agent"):
        assert (support.REPO_ROOT / str(entry.get(key, ""))).is_file(), f"the entry's {key} names no file"
