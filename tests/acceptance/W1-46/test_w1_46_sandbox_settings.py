"""W1-46 -- the launcher starts a worker session only inside a strict, fail-closed sandbox.

KPI success 1 [CAP-61.a]: "gov launch refuses to start a worker session, with a
non-zero exit and a named reason, unless the settings it built have the sandbox
enabled, failIfUnavailable true, allowUnsandboxedCommands false and network
strictAllowlist; it passes them through --settings and reads no sandbox setting
from the repository; the settings it builds carry no excludedCommands (DEC-164)".
KPI failure 1: "A worker session starts with the sandbox off, not strict or not
fail-closed". Failure 2: "A sandbox setting is read from the repository's
settings". Failure 8: "The settings the launcher builds carry an
excludedCommands entry".

DEC-233: ``gov launch`` refuses to start, with a non-zero exit and a named
reason, when the repository's ``.claude/settings.json`` or
``.claude/settings.local.json`` carries a ``sandbox`` key.

DEC-205: the launcher starts the CLI by its absolute path ``~/.local/bin/claude``,
never a bare ``claude``.

Described behaviour from the review of W1-47 (DEC-136): the launcher's settings
do not depend on any file a worker can replace by a symbolic link.

No session is started: the CLI at ``<HOME>/.local/bin/claude`` is a stand-in
that records how it was called.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

import w1_46_support as support

WEAK_SANDBOX = {
    "enabled": False,
    "failIfUnavailable": False,
    "allowUnsandboxedCommands": True,
    "excludedCommands": ["git"],
    "network": {"strictAllowlist": False, "allowedDomains": [support.NOT_A_RESEARCH_HOST]},
}


def _assert_strict(result):
    faults = support.sandbox_faults(result.settings())
    assert faults == [], f"a worker session was started with a sandbox that is not on, strict and fail-closed: {faults}"


# --------------------------------------------------------------------------
# Success 1, failures 1 and 8: what the session is started with
# --------------------------------------------------------------------------

@pytest.mark.parametrize("role", support.WORKER_ROLES)
def test_a_worker_session_is_started_with_the_sandbox_on_strict_and_fail_closed(launch, role):
    result = launch(role)
    assert result.run.returncode == 0, f"gov launch {role} failed\n{result.describe()}"
    _assert_strict(result)


@pytest.mark.parametrize("role", support.WORKER_ROLES)
def test_the_built_settings_carry_no_excluded_commands(launch, role):
    """DEC-164, failure 8."""
    block = launch(role).settings().get("sandbox", {})
    assert not block.get("excludedCommands"), f"the built settings carry excludedCommands: {block['excludedCommands']}"


@pytest.mark.parametrize("role", support.WORKER_ROLES)
def test_the_configuration_is_passed_through_one_settings_argument(launch, role):
    """ "It passes them through --settings": one ``--settings`` value on the CLI's command line holds the sandbox block."""
    result = launch(role)
    session = result.session()
    assert any(arg == "--settings" or arg.startswith("--settings=") for arg in session["args"]), (
        f"the CLI was started without --settings: {session['args']}"
    )
    assert isinstance(result.settings().get("sandbox"), dict), "the --settings value carries no sandbox block"


@pytest.mark.parametrize("role", support.WORKER_ROLES)
def test_the_cli_is_started_by_its_absolute_path(launch, sandbox, role):
    """DEC-205: ``~/.local/bin/claude``, never the ``claude`` that ``PATH`` finds first."""
    result = launch(role)
    assert not result.bare, f"the launcher started a bare `claude` from PATH\n{result.describe()}"
    assert result.session()["argv0"] == str(sandbox.home / support.CLI_REL), (
        f"the CLI was started as {result.session()['argv0']!r}, not by the absolute path ~/.local/bin/claude"
    )


@pytest.mark.parametrize("role", support.WORKER_ROLES)
def test_the_session_is_started_in_the_repository_root(launch, project, role):
    """A worker session is "started in the repository root" (DEC-162, DEC-183): the hooks and the tickets are there."""
    assert os.path.realpath(launch(role).session()["cwd"]) == os.path.realpath(project)


# --------------------------------------------------------------------------
# "Reads no sandbox setting from the repository" (failure 2): a sandbox key there refuses the launch (DEC-233)
# --------------------------------------------------------------------------

def _plant(project, how):
    """Put a weak sandbox block in the repository's settings, the way ``how`` names."""
    if how == "committed-settings":
        path = project / support.SETTINGS_REL
        data = json.loads(path.read_text(encoding="utf-8"))
        data["sandbox"] = WEAK_SANDBOX
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        support.check_support.commit_all(project, "a sandbox block in the committed settings")
    elif how == "local-settings":
        support.write(project, support.LOCAL_SETTINGS_REL, json.dumps({"sandbox": WEAK_SANDBOX}))
    else:   # a link a worker could have left: the local settings resolve to a file in scratch
        target = support.write(project, ".gov-runtime/scratch/w1-46/planted.json", json.dumps({"sandbox": WEAK_SANDBOX}))
        (project / support.LOCAL_SETTINGS_REL).symlink_to(target)


@pytest.mark.parametrize("role", (support.ENGINEER, support.RESEARCH))
@pytest.mark.parametrize("how", ("committed-settings", "local-settings", "local-settings-linked-to-scratch"))
def test_the_launcher_refuses_when_the_repositorys_settings_carry_a_sandbox_key(launch, project, role, how):
    """DEC-233: non-zero exit, a named reason, nothing started. The CLI may merge the repository's settings.

    The same project launches before the key is planted, so the key is the reason.
    """
    launch(role).session()
    _plant(project, how)
    support.assert_refused(launch(role), "sandbox")


@pytest.mark.parametrize("block", (
    {"enabled": True, "failIfUnavailable": True, "allowUnsandboxedCommands": False,
     "network": {"strictAllowlist": True, "allowedDomains": []}},
    {},
), ids=("a-strict-block", "an-empty-block"))
def test_the_key_itself_refuses_the_launch_whatever_it_holds(launch, project, block):
    """DEC-233: "carries a `sandbox` key". The launcher does not judge the block; it refuses it."""
    support.write(project, support.LOCAL_SETTINGS_REL, json.dumps({"sandbox": block}))
    support.assert_refused(launch(support.ENGINEER), "sandbox")


def test_this_repositorys_settings_carry_no_sandbox_block():
    """DEC-161: "The repository's settings carry no sandbox block". Holds before implementation."""
    for rel in (support.SETTINGS_REL, support.w47.TEMPLATE_SETTINGS_REL):
        data = support.w47.load_json_object(support.REPO_ROOT / rel, rel)
        assert "sandbox" not in data, f"{rel} carries a sandbox block"


# --------------------------------------------------------------------------
# The refusal (success 1, failure 1)
# --------------------------------------------------------------------------

@pytest.mark.parametrize("extra", (
    {"sandbox": {"enabled": False}},
    {"sandbox": {"allowUnsandboxedCommands": True}},
    {"sandbox": {"failIfUnavailable": False}},
    {"sandbox": {"network": {"strictAllowlist": False}}},
    {"sandbox": {"excludedCommands": ["git"]}},
), ids=("enabled-false", "unsandboxed-commands-allowed", "not-fail-closed", "allowlist-not-strict", "excluded-commands"))
def test_the_launcher_refuses_when_the_caller_hands_it_a_weaker_sandbox(launch, extra):
    """A second ``--settings`` after ``--`` would weaken what the session gets: no session, non-zero exit, a reason."""
    result = launch(support.ENGINEER, None, "--settings", json.dumps(extra))
    support.assert_refused(result, "sandbox", "settings")


@pytest.mark.parametrize("role", support.NOT_LAUNCHED)
def test_only_the_four_worker_roles_are_launched(launch, role):
    """The launcher "starts worker sessions only"; the orchestrator's session "is not launched through it" (DEC-161)."""
    result = launch(role, support.check_support.ORCHESTRATOR_TICKET_ID)
    support.assert_refused(result, "role", role)


# --------------------------------------------------------------------------
# Described behaviour (DEC-136): no dependence on a file a worker can replace by a link
# --------------------------------------------------------------------------

@pytest.mark.parametrize("role", (support.ENGINEER, support.RESEARCH))
def test_the_settings_reach_the_session_from_a_place_no_worker_can_write(launch, project, sandbox, role):
    """Inline JSON, or a file outside the repository, outside the session's temp directory, and not a link."""
    result = launch(role)
    entry = result.session()["settings"][0]
    if entry["inline"]:
        return
    assert not entry["is_symlink"], f"the --settings value is a symbolic link: {entry['value']}"
    real = Path(entry["realpath"])
    writable = [Path(os.path.realpath(project))]
    shared = os.path.realpath(sandbox.tmpdir)   # the test's own TMPDIR; the session's directory is another one
    writable += [Path(os.path.realpath(path)) for path in result.session()["directories"]
                 if os.path.realpath(path) != shared]
    extra = result.settings().get("sandbox", {}).get("filesystem", {})
    for path in extra.get("allowWrite", []) if isinstance(extra, dict) else []:
        if isinstance(path, str) and path.startswith("/"):
            writable.append(Path(os.path.realpath(path.replace("//", "/", 1))))
    inside = [str(place) for place in writable if real == place or place in real.parents]
    assert inside == [], f"the settings file {real} is inside a place a sandboxed worker can write: {inside}"
