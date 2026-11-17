"""W1-46 -- how the launcher starts a worker session: one ``--settings`` value, the CLI by its path, the root.

Emergency 2 (docs/emergency-2/EMERGENCY-2.md 2.2, 6.1; release 0.1.2): the launcher writes no sandbox block and
does not refuse a ``sandbox`` key in the repository's settings (DEC-233 superseded); the cases that asserted the
strict sandbox, its excluded commands and the refusal of the key are retired. What stays:

- the built settings reach the session through one ``--settings`` argument, and a second ``--settings`` after
  ``--`` is refused: the session's settings come from the launcher alone;
- DEC-205: the launcher starts the CLI by its absolute path ``~/.local/bin/claude``, never a bare ``claude``;
- the session is started in the repository root, and only the worker roles are launched;
- described behaviour from the review of W1-47 (DEC-136): the launcher's settings do not depend on any file a
  worker can replace by a symbolic link.

No session is started: the CLI at ``<HOME>/.local/bin/claude`` is a stand-in
that records how it was called.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

import w1_46_support as support


@pytest.mark.parametrize("role", support.WORKER_ROLES)
def test_the_configuration_is_passed_through_one_settings_argument(launch, role):
    """ "It passes them through --settings": one ``--settings`` value on the CLI's command line holds the built
    settings, with the session's role in their env block (Emergency 2: no sandbox block any more)."""
    result = launch(role)
    session = result.session()
    assert any(arg == "--settings" or arg.startswith("--settings=") for arg in session["args"]), (
        f"the CLI was started without --settings: {session['args']}"
    )
    assert (result.settings().get("env") or {}).get("GOV_ROLE") == role, "the --settings value carries no env block"


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
# A second --settings after -- is refused
# --------------------------------------------------------------------------

@pytest.mark.parametrize("extra", (
    {"sandbox": {"enabled": False}},
    {"sandbox": {"allowUnsandboxedCommands": True}},
    {"sandbox": {"failIfUnavailable": False}},
    {"sandbox": {"network": {"strictAllowlist": False}}},
    {"sandbox": {"excludedCommands": ["git"]}},
), ids=("enabled-false", "unsandboxed-commands-allowed", "not-fail-closed", "allowlist-not-strict", "excluded-commands"))
def test_the_launcher_refuses_when_the_caller_hands_it_a_weaker_sandbox(launch, extra):
    """A second ``--settings`` after ``--`` would replace what the launcher built: no session, non-zero exit, a reason.
    Still refused under Emergency 2, whatever the value holds."""
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
