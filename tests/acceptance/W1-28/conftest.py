"""Fixtures for the W1-28 acceptance tests."""

from __future__ import annotations

import os
import stat
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w1_28_support as support  # noqa: E402

cli_support = support.cli_support


def pytest_configure(config):
    config.addinivalue_line("markers", "local_only: needs the dev tiers on this machine (GOV_DEV_TIERS); not for CI")


@pytest.fixture(autouse=True)
def this_repository_is_never_paused():
    """The freeze flag of this worktree is the owner's: no test sets it, and none clears it.

    In a launched worker session the OS sandbox shows the flag's path as a
    character device (its deny rule on the flag, DEC-311, binds ``/dev/null``
    there) whether or not a flag exists. That placeholder is not a flag and
    nothing can be written through it; anything else at the path is one.
    """
    real = support.REPO_ROOT / support.FREEZE_FLAG_REL
    before = _flag_state(real)
    assert before in (None, "sandbox placeholder"), \
        f"{real} exists: this worktree is frozen; the tests do not run on it"
    yield
    assert _flag_state(real) == before, \
        f"{real} changed during the test: gov pause wrote outside its --root. The owner removes the flag, not a test."


def _flag_state(path):
    """None when nothing is at ``path``; "sandbox placeholder" for a character device; else what is there.

    Owner decision DEC-402: an empty regular file is no flag either. It is the
    placeholder as it shows outside the sandbox while a launched session's
    command runs, and it comes and goes with that command, so it reads as
    nothing here. It is never opened: its size says it.
    """
    try:
        status = os.lstat(path)
    except FileNotFoundError:
        return None
    if stat.S_ISCHR(status.st_mode):
        return "sandbox placeholder"
    if stat.S_ISREG(status.st_mode) and status.st_size == 0:
        return None
    return (status.st_mode, status.st_ino, status.st_size, status.st_mtime_ns)


@pytest.fixture(scope="session")
def interface():
    """The envelope fields and exit codes of ``docs/interfaces/API-0002.yaml``."""
    return cli_support.load_interface(support.REPO_ROOT)


@pytest.fixture(scope="session")
def hook():
    """The guard's PreToolUse hook (W1-02), which reads the flag."""
    return support.guard_support.hook_entry()


@pytest.fixture()
def sandbox(tmp_path):
    """HOME, TMPDIR, the launcher's directory, the bytecode cache and an unrelated directory, outside the project."""
    return cli_support.make_sandbox(tmp_path / "sandbox")


@pytest.fixture()
def raw_project(hook, tmp_path):
    """This test's own temporary git repository, whether or not ``gov pause`` is built."""
    return support.make_project(tmp_path / "project")


@pytest.fixture(scope="session")
def built(hook, tmp_path_factory):
    """``gov pause`` is built. Until then every test of its behaviour fails here.

    The probe is a worker's call (``GOV_ROLE=engineer``) on a throw-away
    project: a built command refuses it, so it pauses nothing.
    """
    base = tmp_path_factory.mktemp("w1-28-built")
    run = support.pause(support.make_project(base / "project"), cli_support.make_sandbox(base / "sandbox"),
                        role=support.ENGINEER)
    if support.NOT_IMPLEMENTED in run.stdout:
        pytest.fail("gov pause is not built yet: it returns NOT_IMPLEMENTED", pytrace=False)
    return True


@pytest.fixture()
def project(built, raw_project):
    """This test's own temporary git repository, with ``gov pause`` built. Removed with ``tmp_path``, frozen or not."""
    return raw_project


@pytest.fixture()
def pause(project, sandbox):
    """``pause(*args, role=None, flag_role=None, cwd=None)`` runs ``gov pause <args> --json`` on this test's project.

    ``role`` is the command's ``GOV_ROLE``; None is the owner, who has none (DEC-365).
    """

    def _pause(*args, role=support.OWNER, flag_role=None, cwd=None):
        return support.pause(project, sandbox, *args, role=role, flag_role=flag_role, cwd=cwd)

    return _pause


@pytest.fixture()
def lift(project, sandbox):
    """``lift()`` lifts this test's project as the owner in person does (DEC-409): ``support.lift``."""

    def _lift():
        return support.lift(project, sandbox)

    return _lift


@pytest.fixture()
def paused(project, pause, interface):
    """The project, paused by its owner."""
    support.succeeded(pause(), interface)
    assert support.is_paused(project), f"gov pause succeeded and {support.FREEZE_FLAG_REL} does not exist"
    return project


@pytest.fixture(scope="session")
def launch_base(tmp_path_factory):
    """The launcher's temporary project (DEC-386), built once. Every test works on its own copy of it."""
    import w1_28_launch_support as launch_support

    return launch_support.make_project(tmp_path_factory.mktemp("w1-28-launch-base") / "repo")


@pytest.fixture()
def launch_project(launch_base, tmp_path, sandbox):
    """This test's own copy of the launcher's project, with a ``held-out.yaml`` made up here (a stand-in directory)."""
    import shutil

    import w1_28_launch_support as launch_support

    target = tmp_path / "launch-repo"
    shutil.copytree(launch_base, target, symlinks=True)
    stand_in = launch_support.w47.make_stand_in(sandbox.elsewhere / "held-out-stand-in")
    launch_support.w47.configure_stand_in(target, stand_in)
    return target


@pytest.fixture()
def stand_in(launch_project, sandbox):
    """The stand-in directory this test's project names as held out. Never the real one."""
    return sandbox.elsewhere / "held-out-stand-in"


@pytest.fixture()
def cli(sandbox):
    """The stand-in CLI at ``<HOME>/.local/bin/claude``: it starts nothing and uses its temp folder as planned."""
    import w1_28_launch_support as launch_support

    return launch_support.install_stand_in_cli(sandbox)


@pytest.fixture()
def launch(launch_project, sandbox, cli):
    """``launch(role, ticket=None, *cli_args)`` runs ``gov launch <role> <ticket> [-- cli_args]`` in the project."""
    import w1_28_launch_support as launch_support

    def _launch(role, ticket=None, *cli_args):
        return launch_support.w46.launch(launch_project, sandbox, cli, role,
                                         ticket or launch_support.TICKET_OF.get(role, launch_support.ENGINEER_TICKET),
                                         *cli_args)

    return _launch


@pytest.fixture()
def claims(project, sandbox):
    """Two tickets claimed by two sessions, through ``gov.tasks.claim``; ``{ticket: holder}``."""
    held = {support.TICKET: support.HOLDER, support.OTHER_TICKET: support.OTHER_HOLDER}
    for ticket, holder in held.items():
        support.tasks(project, sandbox, "claim", ticket, holder)
    return held


@pytest.fixture()
def history(project):
    """Two commits of the ticket around one of another ticket; ``(first, other, second)``."""
    return support.ticket_history(project)
