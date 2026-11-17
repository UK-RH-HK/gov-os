"""KPI success 6 (DEC-386): the launcher starts a product-spec worker.

"gov launch starts a product-spec worker sandboxed, with an empty network
allowlist." Emergency 2 (docs/emergency-2/EMERGENCY-2.md 2.1-2.4, 6.1; release
0.1.2) took the sandbox, the launcher's deny rules, the held-out ``Read`` rules and
the guard's wiring out of ``gov launch``: the cases that asserted them for
product-spec are retired (the strict sandbox, the empty allowlist, the deny rules,
the held-out rule and its refusal, the refusal of unwired repository settings), and
so are the refusals of ``--dangerously-skip-permissions``, ``--permission-mode
bypassPermissions``, ``--add-dir`` and ``--bare``. What stays is below.

As W1-46 left it, ``gov launch product-spec <ticket>`` is refused: "not a
worker role". DEC-386 makes product-spec a launched role. Nothing of the
launcher is weakened for it: the session is what an engineer's is, under the
role's own name.

- **Identity**: ``GOV_ROLE=product-spec`` and ``GOV_TICKET``, which the guard
  then decides by.
- **A temp folder of its own**, removed when the session ends (KPI success 5).
- **Its own ticket only.** DEC-242 refuses "a ticket of another role"; DEC-271
  lifts that for the two independent roles and for no other. The role file
  says the same: "the allowed_paths of its own in_progress ticket, whose role
  is product-spec". So a product-spec session is refused on an engineer's
  ticket.
- **Every refusal of W1-46 that Emergency 2 keeps holds for the new role**: a
  second ``--settings`` after ``--``. Each is preceded by its control, the same launch
  without the fault, so that none passes for the wrong reason.
- **A role nobody knows is still refused**, and so is the orchestrator.
- **The roster** (DEC-163) names the session and the profile of every launched
  role. The committed entry of product-spec must name them too. The ticket
  lead changes ``governance/project/roster.yaml``; the engineer cannot.

Rewrite-Reason: DEC-953 item 2 (W2-90, DEC-957, DEC-906). The case that asked this repository's live guard about the
launched session's identity now asks the kernel's: the ``kernel_launch*`` fixtures below are the same launch project
built on a project generated from the template, whose ``.claude/settings.json`` rulesync generates from the
template's sources; the guard is the PreToolUse line those settings register, run from ``governance/kernel/hooks/``
(``tests/acceptance/W2-90/README.md``).
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

import w1_28_launch_support as support

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "W2-90"))

import w2_90_kernel_wiring as kernel_wiring  # noqa: E402

w46, w47 = support.w46, support.w47

PRODUCT_SPEC = support.PRODUCT_SPEC
TICKET = support.PRODUCT_SPEC_TICKET
NEW_TICKET = "DAEO-zz98"


def _started(launch):
    result = launch(PRODUCT_SPEC)
    assert result.run.returncode == 0, f"gov launch {PRODUCT_SPEC} {TICKET} did not start a session\n{result.describe()}"
    result.session()
    return result


# --------------------------------------------------------------------------
# A session is started
# --------------------------------------------------------------------------

def test_the_launcher_starts_one_product_spec_session(launch, launch_project):
    result = _started(launch)
    session = result.session()
    assert session["argv0"].endswith(w46.CLI_REL), f"the session was not started from ~/{w46.CLI_REL}: {session['argv0']}"
    assert session["cwd"] == str(launch_project.resolve()), f"the session runs in {session['cwd']}, not in the project"


def test_the_extra_cli_arguments_reach_the_product_spec_session(launch):
    """DEC-183: what follows ``--`` is the session's, after the launcher's own ``--settings``. W2-153 (DEC-1050) appends
    one more pair after the caller's arguments, ``--append-system-prompt-file <root>/.claude/templates/<stem>.md``:
    the caller's four stay one ordered run, followed by that pair and nothing else (W1-46's helper)."""
    passed = ["-p", "Do the ticket's work.", "--max-turns", "8"]
    result = launch(PRODUCT_SPEC, None, *passed)
    assert w46.caller_args_then_template_pair(result.session()["args"], passed), result.describe()


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


@pytest.fixture(scope="module")
def kernel_launch_base(tmp_path_factory):
    """The launcher's project (DEC-386) on a project generated from the template, built once (W2-90)."""
    try:
        return kernel_wiring.w1_28_project(tmp_path_factory.mktemp("w2-90-w1-28-kernel"))
    except kernel_wiring.GenerationFailed as exc:
        pytest.fail(str(exc), pytrace=False)


@pytest.fixture()
def kernel_launch_project(kernel_launch_base, tmp_path, sandbox):
    """This test's own copy of it, with a ``held-out.yaml`` made up here, and this worktree's ``gov`` package
    importable for the sandbox's home as an install makes it (the kernel's line starts ``python3``)."""
    target = tmp_path / "launch-repo"
    shutil.copytree(kernel_launch_base, target, symlinks=True)
    stand_in = w47.make_stand_in(sandbox.elsewhere / "held-out-stand-in")
    w47.configure_stand_in(target, stand_in)
    kernel_wiring.install_gov_for(sandbox.home)
    return target


@pytest.fixture()
def kernel_launch(kernel_launch_project, sandbox, cli):
    """``launch(role, ticket=None, *cli_args)`` in the project on a generated project."""

    def _launch(role, ticket=None, *cli_args):
        return w46.launch(kernel_launch_project, sandbox, cli, role,
                          ticket or support.TICKET_OF.get(role, support.ENGINEER_TICKET), *cli_args)

    return _launch


@pytest.mark.parametrize("tool", ("Write", "Edit"))
def test_the_guard_decides_by_the_identity_the_launcher_gave(kernel_launch, kernel_launch_project, sandbox, tool):
    """The role and the ticket of the session, handed to the guard: its own path is allowed, another is denied."""
    launch, launch_project = kernel_launch, kernel_launch_project
    result = _started(launch)
    role, ticket = result.variable("GOV_ROLE"), result.variable("GOV_TICKET")
    own = w46.ask_guard(launch_project, sandbox, tool,
                        w47.write_input(tool, launch_project / support.PRODUCT_SPEC_OWN_PATH), role, ticket)
    w47.assert_allowed(own, f"{tool} to {support.PRODUCT_SPEC_OWN_PATH} by the launched {PRODUCT_SPEC} session")
    other = w46.ask_guard(launch_project, sandbox, tool,
                          w47.write_input(tool, launch_project / support.PRODUCT_SPEC_OTHER_PATH), role, ticket)
    w47.assert_denied_by_rule(other, f"{tool} to {support.PRODUCT_SPEC_OTHER_PATH}, outside the ticket's paths")


def test_the_product_spec_session_has_a_temp_folder_of_its_own_and_may_write_there(launch, cli):
    """DEC-159: the folder is the session's ``TMPDIR``, and it is removed when the session ends (Emergency 2: there is no
    sandbox, so no write allowance to check)."""
    support.plan(cli, files={"work/notes.txt": "notes\n"})
    result = _started(launch)
    folder = support.temp_folder(result)
    assert result.variable("TMPDIR") == str(folder), f"TMPDIR of the session is {result.variable('TMPDIR')!r}"
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
    "settings": ("--settings", '{"sandbox": {"enabled": false}}'),
    "settings-joined": ('--settings={"env": {"GOV_ROLE": "engineer"}}',),
}
REASON = ("settings",)


@pytest.mark.parametrize("name", sorted(CLI_ARGUMENTS))
def test_the_launcher_refuses_the_same_cli_arguments_for_product_spec(launch, name):
    """W1-46: no settings but the launcher's (Emergency 2 keeps this refusal; the bypass, ``--add-dir`` and ``--bare``
    refusals are gone)."""
    _started(launch)
    w46.assert_refused(launch(PRODUCT_SPEC, None, "-p", "Do the ticket's work.", *CLI_ARGUMENTS[name]), *REASON)


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
