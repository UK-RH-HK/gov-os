"""W2-50, the launcher's half of success 1 and 2, and success 3 (survival).

"[...] known to the guard and to the launcher's sandbox", "The folder is
created on first use", and "Survival. A clone made there survives the
session's end and a restart" [DEC-728, W2-M355]. Emergency 2 (release 0.1.2):
the launcher writes no sandbox block, and "The launcher adds exactly that
folder (not the root) to the sandbox write list" is retired with it.

``gov launch <role> <ticket>`` runs in the fixture project with a temporary
HOME; the CLI is a stand-in at ``<HOME>/.local/bin/claude`` that records the
settings the session would get and does what the plan file asks of a session
(look at folders, clone, write). No session is started.

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


def _launched(sandbox, cli, role, ticket):
    result = support.launch(sandbox, cli, role, ticket)
    result.session()
    return result


# --------------------------------------------------------------------------
# The folder's name
# --------------------------------------------------------------------------
# Emergency 2 (release 0.1.2): the launcher writes no sandbox block, so the write-list cases (the own folder on it,
# nothing wider, the temp folder on it) are retired; the folder's name is still the launcher's.

def test_a_ticket_without_a_w2_id_gets_the_folder_named_by_its_tk_id(project, sandbox, cli):
    own = sandbox.root / support.NO_W2_ID.tk
    support.set_plan(cli, check=(own,))
    session = _launched(sandbox, cli, support.ENGINEER, support.NO_W2_ID).session()
    assert session["seen"][str(own)] is True, (
        f"the session on {support.NO_W2_ID.tk} (no external-ref) started without the folder {own}")


def test_a_w2_id_with_a_letter_suffix_names_the_folder_as_written(project, sandbox, cli):
    own = sandbox.root / support.SUFFIXED.wbs
    support.set_plan(cli, check=(own,))
    session = _launched(sandbox, cli, support.ENGINEER, support.SUFFIXED).session()
    assert session["seen"][str(own)] is True, f"the session on {support.SUFFIXED.tk} started without the folder {own}"


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
