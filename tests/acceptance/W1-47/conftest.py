"""Fixtures for the W1-47 acceptance tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w1_47_support as support  # noqa: E402

check_support = support.check_support
live_support = support.live_support


# -- The kernel hooks -----------------------------------------------------------

@pytest.fixture(scope="session")
def hooks():
    """Both kernel hooks exist in the template directory."""
    try:
        return check_support.guard_entry(), check_support.hook_entry()
    except check_support.HookMissing as exc:
        reason = str(exc)
    pytest.fail(reason, pytrace=False)


# -- The fixture project --------------------------------------------------------

@pytest.fixture()
def sandbox(tmp_path):
    """HOME, the system temporary directory and an unrelated directory, all outside the project."""
    return check_support.make_sandbox(tmp_path / "sandbox")


@pytest.fixture()
def project(hooks, tmp_path):
    """A committed project with both hooks installed and the fixture tickets in progress."""
    return check_support.make_project(tmp_path / "project")


@pytest.fixture()
def guard(sandbox):
    """``guard(project, tool_name, tool_input, who, mode="default")`` asks the PreToolUse hook about one call.

    ``who`` is ``(GOV_ROLE, GOV_TICKET, subagent type)``, an entry of
    ``support.EVERY_ACTOR``. No command is ever run.
    """

    def _guard(project, tool_name, tool_input, who=(None, None, None), mode="default", environment=None):
        role, ticket, subagent = who
        return support.run_guard(project, sandbox, tool_name, tool_input, role=role, ticket=ticket,
                                 subagent=subagent, permission_mode=mode, environment=environment)

    return _guard


# -- The oracle configuration and its stand-in -----------------------------------

@pytest.fixture(scope="session")
def configured():
    """The paths of the committed ``governance/project/held-out.yaml``, for the static checks. Never shown."""
    return support.load_configured()


@pytest.fixture(params=("in-the-temporary-directory", "in-the-repository"))
def stand_in(request, project, sandbox):
    """A stand-in directory, configured in the fixture project as the held-out path.

    Two places: the system temporary directory, where a role's writes are
    otherwise allowed (the scratch set), and the project itself, where the
    orchestrator's are. The project's ``held-out.yaml`` is built from the
    made-up path alone (DEC-218).
    """
    base = sandbox.tmpdir if request.param == "in-the-temporary-directory" else project
    directory = support.make_stand_in(base / "held-out-stand-in")
    support.configure_stand_in(project, directory)
    return directory


@pytest.fixture()
def temp_stand_in(project, sandbox):
    """The stand-in in the system temporary directory only."""
    directory = support.make_stand_in(sandbox.tmpdir / "held-out-stand-in")
    support.configure_stand_in(project, directory)
    return directory


# -- This repository's committed settings and the wired copy ---------------------

@pytest.fixture(scope="session")
def settings():
    """``.claude/settings.json`` of this repository."""
    return support.load_settings()


@pytest.fixture(scope="session")
def template_settings():
    """``template/governance/kernel/settings.json`` (DEC-217)."""
    return support.load_template_settings()


@pytest.fixture()
def installed(template_settings, live_sandbox):
    """``installed(project, event, tool_name, tool_input, role, ticket)``: the template's commands, run for one call.

    The commands of the kernel template's settings file are run through the
    shell, as the harness runs them, in a project that has the kernel
    installed (the fixture project). Returns one result for each command.
    """

    def _installed(project, event, tool_name, tool_input, role=None, ticket=None, **options):
        return support.run_registered(project, template_settings, live_sandbox, event, tool_name, tool_input,
                                      role=role, ticket=ticket, **options)

    return _installed


@pytest.fixture()
def live_sandbox(tmp_path):
    return live_support.make_sandbox(tmp_path / "live-sandbox")


@pytest.fixture()
def wired(hooks, tmp_path):
    """The guard's own files and the committed settings, in a new committed repository."""
    return support.make_wired_copy(tmp_path / "wired")


@pytest.fixture()
def live(settings, live_sandbox):
    """``live(project, tool_name, tool_input, role, ticket)``: what the committed settings decide about one call.

    The registered PreToolUse commands are run through the shell, as the
    harness runs them, with no ``PYTHONPATH`` from the test.
    """

    def _live(project, tool_name, tool_input, role=None, ticket=None, subagent=None, permission_mode="default"):
        return live_support.pre_tool_use(project, settings, live_sandbox, tool_name, tool_input, role=role,
                                         ticket=ticket, subagent=subagent, permission_mode=permission_mode)

    return _live
