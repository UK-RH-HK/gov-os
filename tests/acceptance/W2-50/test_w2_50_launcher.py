"""W2-50, the launcher's half of success 1 and 2, and success 3 (survival).

"[...] known to the guard and to the launcher's sandbox", "The launcher adds
exactly that folder (not the root) to the sandbox write list", "The folder is
created on first use", and "Survival. A clone made there survives the
session's end and a restart" [DEC-728, W2-M355].

``gov launch <role> <ticket>`` runs in the fixture project with a temporary
HOME; the CLI is a stand-in at ``<HOME>/.local/bin/claude`` that records the
settings the session would get and does what the plan file asks of a session
(look at folders, clone, write). No session is started.

The sandbox's write list is ``sandbox.filesystem.allowWrite`` of the settings
the session is started with, as earlier suites read it (W1-28, W1-46). An entry
may be written ``//abs``, ``/abs`` or ``~/rel``, with or without a trailing
``/**``; the tests compare the real paths.

"A restart" is read as: a later session of the same ticket, started after the
first one ended and its temp folder was removed, finds the clone as it was, and
the clone lies in no temp folder (W2-M355: clones under /tmp are lost on a
reboot). A reboot of the machine is not made.
"""

from __future__ import annotations

import os
import subprocess

import pytest

import w2_50_support as support

MAIN, OTHER = support.MAIN, support.OTHER


def _real_entries(result, sandbox):
    return [(entry, support.entry_path(entry, sandbox)) for entry in result.allow_write()]


def _launched(sandbox, cli, role, ticket):
    result = support.launch(sandbox, cli, role, ticket)
    result.session()
    return result


# --------------------------------------------------------------------------
# The sandbox write list
# --------------------------------------------------------------------------

@pytest.mark.parametrize("role", support.LAUNCHED_ROLES)
def test_the_sandbox_may_write_the_sessions_own_folder(project, sandbox, cli, role):
    ticket = support.TICKET_OF[role]
    result = _launched(sandbox, cli, role, ticket)
    own = sandbox.own(ticket)
    entries = _real_entries(result, sandbox)
    assert any(support.covers(real, own / "clone" / "file.txt") for _, real in entries), (
        f"the sandbox of a {role} session on {ticket.tk} may not write its own folder {own}: "
        f"allowWrite is {result.allow_write()}")


@pytest.mark.parametrize("role", support.LAUNCHED_ROLES)
def test_the_sandbox_adds_exactly_the_own_folder_under_the_root(project, sandbox, cli, role):
    """Exactly that folder: one entry under the root, the own folder itself; never the root, never a wider one."""
    ticket = support.TICKET_OF[role]
    result = _launched(sandbox, cli, role, ticket)
    own = os.path.realpath(sandbox.own(ticket))
    root = os.path.realpath(sandbox.root)
    entries = _real_entries(result, sandbox)
    wide = [entry for entry, real in entries if support.covers(real, root)]
    assert wide == [], f"the sandbox may write the root itself or a folder above it: {wide}"
    under = [real for _, real in entries if real is not None and real.startswith(root + "/")]
    assert under == [own], (
        f"the sandbox's entries under the root are {under}, not exactly the own folder {own}: "
        f"allowWrite is {result.allow_write()}")


def test_the_sandbox_may_not_write_another_tickets_folder_the_workbench_or_other_worktrees(project, sandbox, cli):
    result = _launched(sandbox, cli, support.ENGINEER, MAIN)
    places = {
        "another ticket's folder": sandbox.own(OTHER) / "f.txt",
        "a file directly in the root": sandbox.root / "f.txt",
        "HOME": sandbox.home / "f.txt",
        "the workbench": sandbox.home / support.WORKBENCH / "examin" / "f.txt",
        "another worktree": sandbox.home / support.WORKTREES / OTHER.folder / "f.txt",
        "elsewhere": sandbox.elsewhere / "f.txt",
    }
    for name, path in places.items():
        holding = [entry for entry, real in _real_entries(result, sandbox) if support.covers(real, path)]
        assert holding == [], f"the sandbox may write {name} ({path}) through {holding}"


def test_the_sandbox_keeps_the_sessions_temp_folder(project, sandbox, cli):
    """No regression of DEC-159: the session's own temp folder stays in the list beside the own folder."""
    result = _launched(sandbox, cli, support.ENGINEER, MAIN)
    folder = result.variable("TMPDIR")
    assert folder and os.path.realpath(folder) != os.path.realpath(sandbox.tmpdir), (
        f"the session has no temp folder of its own: TMPDIR={folder!r}")
    assert any(support.covers(real, os.path.join(folder, "f.txt")) for _, real in _real_entries(result, sandbox)), (
        f"the sandbox may not write the session's temp folder {folder}: {result.allow_write()}")


def test_a_ticket_without_a_w2_id_gets_the_folder_named_by_its_tk_id(project, sandbox, cli):
    result = _launched(sandbox, cli, support.ENGINEER, support.NO_W2_ID)
    own = sandbox.root / support.NO_W2_ID.tk
    assert any(support.covers(real, own / "f.txt") for _, real in _real_entries(result, sandbox)), (
        f"the sandbox of a session on {support.NO_W2_ID.tk} (no external-ref) may not write {own}: "
        f"{result.allow_write()}")


def test_a_w2_id_with_a_letter_suffix_names_the_folder_as_written(project, sandbox, cli):
    result = _launched(sandbox, cli, support.ENGINEER, support.SUFFIXED)
    own = sandbox.root / support.SUFFIXED.wbs
    assert any(support.covers(real, own / "f.txt") for _, real in _real_entries(result, sandbox)), (
        f"the sandbox of a session on {support.SUFFIXED.tk} may not write {own}: {result.allow_write()}")


# --------------------------------------------------------------------------
# Created on first use
# --------------------------------------------------------------------------

def test_the_own_folder_exists_when_the_session_starts(project, sandbox, cli):
    """First use: neither the root nor the folder exists before the launch; the session finds its folder made."""
    assert not sandbox.root.exists(), "the fixture's HOME already holds the root"
    support.set_plan(cli, check=(sandbox.own(MAIN), sandbox.own(OTHER)))
    session = _launched(sandbox, cli, support.ENGINEER, MAIN).session()
    assert session["seen"][str(sandbox.own(MAIN))] is True, (
        f"the session started without its own folder {sandbox.own(MAIN)}: the sandbox cannot bind a folder that "
        "does not exist, so the first use would fail")
    assert session["seen"][str(sandbox.own(OTHER))] is False, "the launch made another ticket's folder too"
    assert sandbox.own(MAIN).is_dir() and not sandbox.own(MAIN).is_symlink(), (
        f"{sandbox.own(MAIN)} is not a directory after the launch")


def test_a_launch_keeps_what_the_folder_already_holds(project, sandbox, cli):
    own = sandbox.own(MAIN)
    support.write(own / "earlier" / "notes.txt", "from an earlier session\n")
    support.set_plan(cli, listing=(own,))
    session = _launched(sandbox, cli, support.ENGINEER, MAIN).session()
    assert session["listed"][str(own)] == ["earlier"], f"the session found {session['listed'][str(own)]} in {own}"
    assert (own / "earlier" / "notes.txt").read_text(encoding="utf-8") == "from an earlier session\n"


# --------------------------------------------------------------------------
# Survival
# --------------------------------------------------------------------------

def _source_repository(sandbox):
    """A small repository outside the root to clone from, by its exact path."""
    source = sandbox.elsewhere / "source"
    support.write(source / "README.md", "# source\n")
    support.git(source, "init", "-q", "-b", "main")
    support.git(source, "add", "-A")
    support.git(source, "commit", "-q", "-m", "source")
    return source, support.git(source, "rev-parse", "HEAD").strip()


def test_a_clone_made_in_the_own_folder_survives_the_sessions_end_and_the_next_session_finds_it(project, sandbox,
                                                                                             cli):
    source, head = _source_repository(sandbox)
    clone = sandbox.own(MAIN) / "clone"
    support.set_plan(cli, clone=((source, clone),),
                     files={sandbox.own(MAIN) / "results.txt": "kept\n"})
    first = _launched(sandbox, cli, support.ENGINEER, MAIN)
    # The stand-in is not sandboxed: a real session could make the clone only if its sandbox may write there.
    assert any(support.covers(real, clone / ".git" / "HEAD") for _, real in _real_entries(first, sandbox)), (
        f"a sandboxed session could not make the clone {clone}: allowWrite is {first.allow_write()}")
    destination, code, stderr = first.session()["cloned"][0]
    assert code == 0, f"the stand-in session could not clone into {destination}: {stderr}"
    session_temp = first.variable("TMPDIR")

    # The session has ended: its temp folder is gone (DEC-159), the clone is not.
    assert not os.path.exists(session_temp), f"the session's temp folder {session_temp} outlived the session"
    assert (clone / ".git").is_dir(), f"the clone {clone} did not survive the session's end"
    assert support.git(clone, "rev-parse", "HEAD").strip() == head, "the clone's history changed"
    assert (sandbox.own(MAIN) / "results.txt").read_text(encoding="utf-8") == "kept\n"

    # The clone lies in no temp folder: not the launcher's, not the session's.
    real = os.path.realpath(clone)
    for folder in (sandbox.tmpdir, session_temp):
        assert not real.startswith(os.path.realpath(folder) + "/"), f"the clone {real} lies in the temp folder {folder}"

    # A later session of the same ticket finds it as it was.
    support.set_plan(cli, listing=(sandbox.own(MAIN),), check=(clone,))
    second = _launched(sandbox, cli, support.ENGINEER, MAIN).session()
    assert second["seen"][str(clone)] is True, "the next session of the ticket did not find the clone"
    assert "clone" in (second["listed"][str(sandbox.own(MAIN))] or []), "the next session's folder lost the clone"
    assert subprocess.run(["git", "-C", str(clone), "fsck", "--no-progress"], capture_output=True,
                          env=support.base_environment(sandbox), check=False).returncode == 0, (
        "the clone is no longer a sound repository after the second session")


def test_a_launch_of_another_ticket_leaves_the_folder_alone(project, sandbox, cli):
    own = sandbox.own(MAIN)
    support.write(own / "clone" / "README.md", "kept\n")
    before = support.snapshot(own)
    _launched(sandbox, cli, support.ENGINEER, OTHER)
    assert support.snapshot(own) == before, "a session of W2-91 changed W2-90's folder"
