"""W2-50, the last review's findings (DEC-751), as described behaviour (DEC-136): tests added after implementation.

The second review of the implemented ticket found two behaviours the suite did
not hold; the orchestrator decided them (DEC-751, stricter only). Each is
tested through the interfaces the suite already drives: the guard's PreToolUse
hook with the call on stdin, ``gov launch`` with the stand-in CLI, and the
secrets-indexing check as a command.

1. **A folder belongs to the one repository whose launch made it.** When
   ``gov launch`` makes a ticket's own folder, it records in that folder which
   repository made it: the repository's git common directory, so every
   worktree of one repository is the same repository and a clone is another.
   - The session of that repository's ticket keeps its folder; a later launch
     keeps the folder, its content and its entry; a second worktree of the
     same repository gets the same folder.
   - A session of another repository whose ``in_progress`` ticket has the same
     name gets nothing there: the guard refuses its Write, Edit and judged Bash,
     and its ``gov launch`` neither adds the folder nor changes what it holds.
   - A folder that holds no record (made by hand, or there before any launch)
     and a folder that does not exist yet give no session anything; the
     launcher neither adds nor records a folder that exists without a record.

   The record is made only the public way, by ``gov launch`` in the project
   whose folder it is. No case writes, names or reads it, or assumes its name
   or form (DEC-462): what a folder holds is compared by name, kind, size and
   modification time, without reading a file of it.
2. **A project's own secrets check follows a link that stays inside the
   project, also under the root.** A clone at ``~/gov-os-runs/W2-90/clone``
   whose ``.gov-runtime/`` links to a folder or file of that same clone outside
   ``.gov-runtime/`` holding a planted secret: its own check goes red, as it
   does for the same layout outside the root. A link from its ``.gov-runtime/``
   to a place under the root but outside the clone is still not followed
   (DEC-743 3).

Every location is the suite's: a temporary HOME, a temp folder disjoint from
it, fixture projects built from scratch or cloned from one, inside the test's
own folder.
"""

from __future__ import annotations

import dataclasses
import os
import shutil
import stat
from pathlib import Path

import pytest

import w2_50_support as support

q = support.q
MAIN, OTHER = support.MAIN, support.OTHER
ENGINEER = support.ENGINEER

needs_gitleaks = pytest.mark.skipif(shutil.which("gitleaks") is None,
                                    reason="gitleaks is not on PATH: the check cannot run")


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

@dataclasses.dataclass(frozen=True)
class _ProjectAt(support.Sandbox):
    """The suite's sandbox (the same HOME, temp folder and elsewhere), with the project at ``location``."""
    location: Path = None

    @property
    def project(self):
        return self.location


def _at(box, location):
    fields = {field.name: getattr(box, field.name) for field in dataclasses.fields(support.Sandbox)}
    return _ProjectAt(**fields, location=Path(location))


def _refused(result, what, box, *paths):
    names = []
    for path in paths:
        names += support.why_words(path, box)
    support.assert_refused(result, what, *names)


def _ask(box, project, tool_name, target, ticket, role=ENGINEER):
    return support.ask_guard(box, tool_name, support.tool_input(tool_name, target), role, ticket, project)


def _writes_refused(box, project, folder, what, ticket):
    """Write and Edit on a file in ``folder``, a Bash redirect into it, ``mkdir -p`` in it and ``rm -rf`` of it."""
    target = folder / "work" / "README.md"
    for tool_name in ("Write", "Edit"):
        _refused(_ask(box, project, tool_name, target, ticket), f"{tool_name} on {target} {what}", box, target)
    for command in (f"echo written > {q(target)}", f"mkdir -p {q(folder / 'clone')}", f"rm -rf {q(folder)}"):
        _refused(_ask(box, project, "Bash", command, ticket), f"Bash `{command}` {what}", box, folder)


def _writes_allowed(box, project, folder, what, ticket):
    """Write and Edit on a file in ``folder``, a Bash redirect, ``mkdir -p`` and ``rm -rf`` of a sub-folder."""
    target = folder / "work" / "README.md"
    for tool_name in ("Write", "Edit"):
        support.assert_allowed(_ask(box, project, tool_name, target, ticket), f"{tool_name} on {target} {what}")
    for command in (f"echo written > {q(target)}", f"mkdir -p {q(folder / 'clone')}", f"rm -rf {q(folder / 'old')}"):
        support.assert_allowed(_ask(box, project, "Bash", command, ticket), f"Bash `{command}` {what}")


def _state(folder):
    """What ``folder`` holds: each entry's kind, and a file's size and modification time. No file is read."""
    result = {}
    for directory, names, files in os.walk(folder):
        for name in names + files:
            path = os.path.join(directory, name)
            info = os.lstat(path)
            rel = os.path.relpath(path, folder)
            if stat.S_ISLNK(info.st_mode):
                result[rel] = ("link", os.readlink(path))
            elif stat.S_ISDIR(info.st_mode):
                result[rel] = ("folder",)
            else:
                result[rel] = ("file", info.st_size, info.st_mtime_ns)
    return result


def _launched(box, cli, ticket, role=ENGINEER):
    result = support.launch(box, cli, role, ticket)
    result.session()
    return result


def _real_entries(result, box):
    return [(entry, support.entry_path(entry, box)) for entry in result.allow_write()]


def _entries_at_or_under_the_root(result, box):
    root = os.path.realpath(box.root)
    return [entry for entry, real in _real_entries(result, box)
            if real is not None and (support.covers(real, root) or real.startswith(root + "/"))]


def _assert_temp_folder_kept(result, box):
    folder = result.variable("TMPDIR")
    assert folder and any(support.covers(real, os.path.join(folder, "f.txt")) for _, real in _real_entries(result, box)), (
        f"the sandbox may not write the session's temp folder {folder}: {result.allow_write()}")


def _work(folder, text):
    """A file of the test's own in ``folder`` (never the launcher's record), and an ``old`` sub-folder."""
    (folder / "old").mkdir(parents=True, exist_ok=True)
    return support.write(folder / "work" / "README.md", text)


# --------------------------------------------------------------------------
# 1. A folder belongs to the one repository whose launch made it
# --------------------------------------------------------------------------

@pytest.fixture()
def first(sandbox, project, cli):
    """The first project (the fixture worktree ``~/gov-os-worktrees/W2-90``), launched for MAIN and OTHER.

    Each launch makes the ticket's own folder; the test then puts a file of its own in each.
    """
    for ticket in (MAIN, OTHER):
        _launched(sandbox, cli, ticket)
        assert sandbox.own(ticket).is_dir(), f"the first project's launch of {ticket.tk} made no {sandbox.own(ticket)}"
        _work(sandbox.own(ticket), f"{ticket.folder}'s work, by the first project\n")
    return project


def test_the_launching_repositorys_session_keeps_its_folder(first, sandbox):
    """The control: the session of the repository whose launch made the folder writes there."""
    _writes_allowed(sandbox, first, sandbox.own(MAIN), f"by the engineer on {MAIN.tk} in the first project", MAIN.tk)


def test_a_later_launch_in_the_same_repository_keeps_the_folder_its_content_and_its_entry(first, sandbox, cli):
    own = sandbox.own(MAIN)
    support.set_plan(cli, listing=(own,))
    result = _launched(sandbox, cli, MAIN)
    assert "work" in (result.session()["listed"][str(own)] or []), "the later session did not find the folder's content"
    assert (own / "work" / "README.md").read_text(encoding="utf-8") == f"{MAIN.folder}'s work, by the first project\n"
    under = [real for _, real in _real_entries(result, sandbox)
             if real is not None and real.startswith(os.path.realpath(sandbox.root) + "/")]
    assert under == [os.path.realpath(own)], (
        f"after a later launch the sandbox's entries under the root are {under}, not [{own}]: {result.allow_write()}")
    support.assert_allowed(_ask(sandbox, first, "Write", own / "work" / "README.md", MAIN.tk),
                           "Write in the own folder after a later launch")


def _second_worktree(sandbox, project):
    location = sandbox.home / support.WORKTREES / f"{MAIN.folder}-second"
    support.git(project, "worktree", "add", "-q", "-b", "second", str(location))
    return _at(sandbox, location), location


def test_a_second_worktree_of_the_same_repository_gets_the_same_folder(first, sandbox, cli):
    """Every worktree of one repository is the same repository: its session and its launch get the folder."""
    box, second = _second_worktree(sandbox, first)
    own = sandbox.own(MAIN)
    _writes_allowed(box, second, own, f"by the engineer on {MAIN.tk} in a second worktree {second}", MAIN.tk)
    result = _launched(box, cli, MAIN)
    assert any(support.covers(real, own / "f.txt") for _, real in _real_entries(result, box)), (
        f"a launch in the second worktree {second} may not write the folder {own}: {result.allow_write()}")
    assert (own / "work" / "README.md").is_file(), "a launch in the second worktree lost the folder's content"


# Another Gov OS project on the same HOME (how it is made, and where), by the folder its ticket's name shares.
ANOTHER_REPOSITORY = {
    "a-project-built-apart-outside-the-root": "W2-91",
    "a-clone-inside-the-first-projects-own-folder": "W2-91",
    "a-clone-of-the-first-project-outside-the-root": "W2-90",
}


def _another_repository(sandbox, first, form):
    """``(box, project, ticket)``: another repository whose ``in_progress`` ticket names a folder the first made."""
    if form == "a-project-built-apart-outside-the-root":
        box = _at(sandbox, sandbox.home / "projects" / "second")
        return box, support.make_project(box), OTHER
    if form == "a-clone-inside-the-first-projects-own-folder":
        location = sandbox.own(MAIN) / "clone"
        support.git(sandbox.own(MAIN), "clone", "-q", "--no-hardlinks", str(first), str(location))
        return _at(sandbox, location), location, OTHER
    location = sandbox.home / "clones" / "third"
    location.parent.mkdir(parents=True)
    support.git(location.parent, "clone", "-q", "--no-hardlinks", str(first), str(location))
    return _at(sandbox, location), location, MAIN


@pytest.mark.parametrize("form", sorted(ANOTHER_REPOSITORY))
def test_another_repositorys_session_gets_nothing_in_a_folder_the_first_made(first, sandbox, form):
    box, other, ticket = _another_repository(sandbox, first, form)
    folder = sandbox.own(ticket)
    assert ticket.folder == ANOTHER_REPOSITORY[form] and folder.is_dir()
    assert (other / ".tickets" / f"{ticket.tk}.md").is_file(), f"premise: {other} has no ticket {ticket.tk}"
    _writes_refused(box, other, folder, f"by the engineer on {ticket.tk} of another repository {other} ({form})",
                    ticket.tk)
    # The success control: the first project's session on the same ticket keeps the folder.
    support.assert_allowed(_ask(sandbox, first, "Write", folder / "work" / "README.md", ticket.tk),
                           f"Write in {folder} by the first project's session on {ticket.tk}, after the other's calls")


@pytest.mark.parametrize("form", sorted(ANOTHER_REPOSITORY))
def test_a_launch_in_another_repository_neither_adds_nor_changes_the_folder(first, sandbox, cli, form):
    box, other, ticket = _another_repository(sandbox, first, form)
    folder = sandbox.own(ticket)
    before = _state(folder)
    result = _launched(box, cli, ticket)
    holding = _entries_at_or_under_the_root(result, box)
    assert holding == [], (
        f"the sandbox of a session on {ticket.tk} in another repository {other} ({form}) may write at or under the "
        f"root through {holding}: allowWrite is {result.allow_write()}")
    assert _state(folder) == before, (
        f"a launch in another repository {other} ({form}) changed what {folder} holds")
    _assert_temp_folder_kept(result, box)


NO_RECORD = ("before-any-launch", "beside-a-launched-folder")


def _no_record_layout(sandbox, cli, layout):
    """Before the case: nothing launched, or OTHER's folder launched beside (the root then exists)."""
    if layout == "beside-a-launched-folder":
        _launched(sandbox, cli, OTHER)
        assert sandbox.own(OTHER).is_dir()


@pytest.mark.parametrize("layout", NO_RECORD)
def test_a_folder_made_by_hand_gives_no_session_anything(project, sandbox, cli, layout):
    """A folder under the root that no launch made: the guard refuses MAIN's session there, with its reason."""
    _no_record_layout(sandbox, cli, layout)
    _work(sandbox.own(MAIN), "made by hand\n")
    _writes_refused(sandbox, project, sandbox.own(MAIN), f"(a folder made by hand, {layout})", MAIN.tk)


@pytest.mark.parametrize("layout", NO_RECORD)
def test_a_folder_that_does_not_exist_yet_gives_no_session_anything(project, sandbox, cli, layout):
    _no_record_layout(sandbox, cli, layout)
    own = sandbox.own(MAIN)
    assert not os.path.lexists(own)
    what = f"(the own folder does not exist yet, {layout})"
    for tool_name in ("Write", "Edit"):
        _refused(_ask(sandbox, project, tool_name, own / "notes.txt", MAIN.tk), f"{tool_name} on {own} {what}",
                 sandbox, own / "notes.txt")
    for command in (f"echo written > {q(own / 'notes.txt')}", f"mkdir -p {q(own / 'clone')}"):
        _refused(_ask(sandbox, project, "Bash", command, MAIN.tk), f"Bash `{command}` {what}", sandbox, own)


@pytest.mark.parametrize("content", ("empty", "holding-a-file"))
def test_a_launch_neither_adds_nor_records_a_folder_that_exists_without_a_record(project, sandbox, cli, content):
    """The folder was there before any launch: the launch leaves it as it is and gives the session nothing there."""
    own = sandbox.own(MAIN)
    own.mkdir(parents=True)
    if content == "holding-a-file":
        _work(own, "there before any launch\n")
    before = _state(own)
    result = _launched(sandbox, cli, MAIN)
    holding = _entries_at_or_under_the_root(result, sandbox)
    assert holding == [], (
        f"the launch added a folder that no launch made ({content}) through {holding}: allowWrite is "
        f"{result.allow_write()}")
    assert _state(own) == before, f"the launch changed what {own} holds ({content}): it wrote into a folder it did not make"
    _assert_temp_folder_kept(result, sandbox)
    _refused(_ask(sandbox, project, "Write", own / "notes.txt", MAIN.tk),
             f"Write in {own} after a launch that found it there ({content})", sandbox, own / "notes.txt")


# --------------------------------------------------------------------------
# 2. A project's own secrets check follows a link that stays inside the project, also under the root
# --------------------------------------------------------------------------

@pytest.fixture()
def indexed_project(sandbox):
    """The fixture project with the kernel's gitleaks rules, as the suite's index cases build it."""
    project = support.make_project(sandbox, extra={"governance/project/path-map.yaml": support.path_map_text()})
    shutil.copy2(support.GITLEAKS_TEMPLATE, project / ".gitleaks.toml")
    support.git(project, "add", "-A")
    support.git(project, "commit", "-q", "-m", "gitleaks rules")
    return project


LOCATIONS = ("outside-the-root", "a-clone-under-the-root")


def _located(sandbox, indexed_project, location):
    """The project the check runs in: the fixture worktree, or its clone at ``~/gov-os-runs/W2-90/clone``."""
    if location == "outside-the-root":
        return indexed_project
    clone = sandbox.own(MAIN) / "clone"
    sandbox.own(MAIN).mkdir(parents=True)
    support.git(sandbox.own(MAIN), "clone", "-q", "--no-hardlinks", str(indexed_project), str(clone))
    return clone


def _runtime(project):
    runtime = project / ".gov-runtime"
    support.write(runtime / "scratch" / "clean.txt", "nothing here\n")
    return runtime


def _plant(path):
    return support.write(path, f"chunk: {support.SECRET}\n")


# A link in the project's .gov-runtime/ to a place of the same project outside .gov-runtime/:
# (the link, relative to .gov-runtime/; its target, relative to the project; the planted file, relative to the target).
INSIDE_LINKS = {
    "a-store-folder-link": ("packets", "shared-store", "DAEO-0000/packet.md"),
    "a-folder-link-in-scratch": ("scratch/kept", "kept-store", "store.txt"),
    "a-file-link": ("store.txt", "kept/store.txt", None),
}


@needs_gitleaks
@pytest.mark.parametrize("link", sorted(INSIDE_LINKS))
@pytest.mark.parametrize("location", LOCATIONS)
def test_a_projects_own_check_follows_a_link_that_stays_inside_the_project(indexed_project, sandbox, location, link):
    project = _located(sandbox, indexed_project, location)
    runtime = _runtime(project)
    name, target_rel, planted_rel = INSIDE_LINKS[link]
    target = project / target_rel
    _plant(target / planted_rel if planted_rel else target)
    premise = support.run_check(sandbox, project)
    assert premise.returncode == 0, (
        f"premise: with no link, the check in {project} is red on a secret outside .gov-runtime/\n{premise.describe()}")
    (runtime / name).parent.mkdir(parents=True, exist_ok=True)
    (runtime / name).symlink_to(target, target_is_directory=planted_rel is not None)
    run = support.run_check(sandbox, project)
    assert run.returncode != 0, (
        f"the check of the project {project} ({location}) did not follow {link} .gov-runtime/{name} -> {target}, a "
        f"place of the same project that holds a secret: it is green\n{run.describe()}")


def _under_the_root_outside_the_project(sandbox, place):
    """A place under the root but outside the clone at ``~/gov-os-runs/W2-90/clone``, and where its secret lies."""
    if place == "a-sibling-in-the-same-own-folder":
        return sandbox.own(MAIN) / "sibling-store", sandbox.own(MAIN) / "sibling-store" / "store.txt"
    if place == "another-tickets-folder":
        return sandbox.own(OTHER) / "store", sandbox.own(OTHER) / "store" / "store.txt"
    return sandbox.root, sandbox.root / "W2-77" / "store" / "store.txt"


OUTSIDE_THE_PROJECT = ("a-sibling-in-the-same-own-folder", "another-tickets-folder", "the-root-itself")


@needs_gitleaks
@pytest.mark.parametrize("place", OUTSIDE_THE_PROJECT)
def test_a_link_under_the_root_but_outside_the_project_is_still_not_followed(indexed_project, sandbox, place):
    """DEC-743 3 holds for the clone's own check: a link out of the clone into the root is not followed."""
    clone = _located(sandbox, indexed_project, "a-clone-under-the-root")
    runtime = _runtime(clone)
    target, planted = _under_the_root_outside_the_project(sandbox, place)
    _plant(planted)
    (runtime / "packets").symlink_to(target, target_is_directory=True)
    run = support.run_check(sandbox, clone)
    assert run.returncode == 0, (
        f"the clone's check followed .gov-runtime/packets -> {target} ({place}), under the root but outside the "
        f"clone\n{run.describe()}")
    assert support.SECRET not in run.stdout + run.stderr, "the check printed the secret"


@needs_gitleaks
def test_this_repositorys_check_does_not_follow_a_link_into_a_clone_under_the_root(indexed_project, sandbox):
    """The repository outside the root: a link to a folder of the clone under the root is not followed (DEC-728 3)."""
    clone = _located(sandbox, indexed_project, "a-clone-under-the-root")
    _plant(clone / "shared-store" / "DAEO-0000" / "packet.md")
    runtime = _runtime(indexed_project)
    (runtime / "packets").symlink_to(clone / "shared-store", target_is_directory=True)
    run = support.run_check(sandbox, indexed_project)
    assert run.returncode == 0, (
        f"this repository's check scanned a clone under the root through .gov-runtime/packets\n{run.describe()}")
    assert support.SECRET not in run.stdout + run.stderr, "the check printed the secret"
