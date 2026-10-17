"""W2-50, the extra review's findings (DEC-758 item 1), as described behaviour (DEC-136): tests added after implementation.

An extra independent review of the repaired ticket found two behaviours the
suite did not hold; the owner decided them (DEC-758, 2026-10-17). Each is
tested through the interfaces the suite already drives: the guard's PreToolUse
hook with the call on stdin, and ``gov launch`` with the stand-in CLI.

F1. **A copy or install into a folder is judged as each file it writes.**
    ``cp X d/``, ``cp X d``, ``install X d/``, ``cp -r s/. d/``, ``cp a b d/``
    and the ``-t`` / ``--target-directory`` forms write ``d/<name of each
    source>``. The call is refused, with the guard's reason, whenever any of
    those files is refused as a direct write: an entry already in ``d`` at a
    source's name that is a symbolic link out of the allowed place, a hard
    link to a file outside it, or a symbolic link to a folder outside it. This
    holds in the own folder and inside the repository, for every ticket (row
    W2-H056), and for the own folder's marker (row W2-L349): a file named like
    the marker copied, installed or moved into the own folder is refused, as
    the direct write onto the marker is. Each refusal case first shows, as its
    premise, that the same file named directly is refused today.
F2. **A project whose real root lies inside ``~/gov-os-runs`` gets no own
    folder.** Its session gets nothing in any folder under the root outside
    the project itself, whatever ticket it names, marked or not; its
    ``gov launch`` adds no folder under the root to the sandbox's write list,
    makes none and writes nothing there (its temp folder stays).

The marker's name is never taken from code: it is the one entry a launch
leaves in the own folder it makes, read from a listing of that folder right
after the launch (DEC-462: the marker's content is never read or written by
a test). No allowed command is run for real: every case asks the guard only.
Every location is the suite's: a temporary HOME, a temp folder disjoint from
it, fixture projects built from scratch, cloned or added as worktrees inside
the test's own folder.
"""

from __future__ import annotations

import dataclasses
import json
import os
import shutil
import stat
from pathlib import Path

import pytest

import w2_50_support as support

q = support.q
MAIN, OTHER, SPEC = support.MAIN, support.OTHER, support.SPEC
ENGINEER, PRODUCT_SPEC = support.ENGINEER, support.PRODUCT_SPEC

PAYLOAD = "payload.py"      # the source's name, and the name of the entry already in the destination folder
FIRST = "first.py"          # the first of several sources, landing on nothing
ACCEPTANCE_TEST = "tests/acceptance/W2-90/test_kpi.py"     # the fixture project's acceptance test (MAIN's)


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


def _ask(box, project, tool_name, target, ticket=MAIN.tk, role=ENGINEER):
    return support.ask_guard(box, tool_name, support.tool_input(tool_name, target), role, ticket, project)


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


def _state(folder, skip=None):
    """What ``folder`` holds: each entry's kind, and a file's size and modification time. No file is read.

    ``skip`` (a real path) is left out with everything under it.
    """
    result = {}
    skip = os.path.realpath(skip) if skip else None
    for directory, names, files in os.walk(folder):
        names[:] = [name for name in names if not skip or os.path.realpath(os.path.join(directory, name)) != skip]
        for name in names + files:
            path = os.path.join(directory, name)
            if skip and os.path.realpath(path) == skip:
                continue
            info = os.lstat(path)
            rel = os.path.relpath(path, folder)
            if stat.S_ISLNK(info.st_mode):
                result[rel] = ("link", os.readlink(path))
            elif stat.S_ISDIR(info.st_mode):
                result[rel] = ("folder",)
            else:
                result[rel] = ("file", info.st_size, info.st_mtime_ns)
    return result


def _sources(sandbox):
    """The files the copies read, outside the project and the root: ``payload.py``, ``first.py``, ``s/payload.py``."""
    support.write(sandbox.elsewhere / PAYLOAD, "VALUE = 2\n")
    support.write(sandbox.elsewhere / FIRST, "VALUE = 3\n")
    support.write(sandbox.elsewhere / "s" / PAYLOAD, "VALUE = 4\n")
    return sandbox.elsewhere


# The copy and install forms into a folder ``d``; each writes ``d/payload.py`` (and, for several sources, ``d/first.py``).
COPY_FORMS = {
    "cp-into-the-folder-with-a-slash": "cp {src}/payload.py {d}/",
    "cp-into-the-folder-without-a-slash": "cp {src}/payload.py {d}",
    "install-into-the-folder": "install {src}/payload.py {d}/",
    "cp-r-of-a-folders-contents": "cp -r {src}/s/. {d}/",
    "cp-of-several-sources": "cp {src}/first.py {src}/payload.py {d}/",
    "cp-t": "cp -t {d} {src}/payload.py",
    "cp-target-directory": "cp --target-directory={d} {src}/payload.py",
}
# The forms that are ordinary copies of today (the -t forms are the guard's own today: refused already).
PLAIN_FORMS = ("cp-into-the-folder-with-a-slash", "cp-into-the-folder-without-a-slash", "install-into-the-folder",
               "cp-r-of-a-folders-contents", "cp-of-several-sources")


def _command(form, src, d):
    return COPY_FORMS[form].format(src=q(src), d=q(d))


# --------------------------------------------------------------------------
# F1. In the own folder: an entry at the source's name that leads out
# --------------------------------------------------------------------------

@pytest.fixture()
def opened(sandbox, project):
    """MAIN's and OTHER's folders made by a launch, a file in OTHER's, the project's acceptance test, the sources."""
    own, other = support.open_own_folder(sandbox, MAIN), support.open_own_folder(sandbox, OTHER)
    support.write(other / "theirs.py", "theirs\n")
    support.write(project / ACCEPTANCE_TEST, "def test_kpi():\n    assert True\n")
    _sources(sandbox)
    return own, other


def _plant(kind, entry, project, other):
    """Put at ``entry`` (``d/payload.py``) an entry of ``kind``; return what a write through it would reach."""
    entry.parent.mkdir(parents=True, exist_ok=True)
    if kind == "a-link-to-the-projects-acceptance-test":
        target = project / ACCEPTANCE_TEST
        entry.symlink_to(target)
    elif kind == "a-link-to-a-file-in-another-tickets-folder":
        target = other / "theirs.py"
        entry.symlink_to(target)
    elif kind == "a-hard-link-to-a-file-in-the-project":
        target = project / "docs" / "notes.md"
        os.link(target, entry)
    else:
        raise ValueError(kind)
    return target


LEADING_OUT = {
    "a-link-to-the-projects-acceptance-test": tuple(COPY_FORMS),
    "a-link-to-a-file-in-another-tickets-folder": ("cp-into-the-folder-with-a-slash", "install-into-the-folder",
                                                   "cp-of-several-sources"),
    "a-hard-link-to-a-file-in-the-project": ("cp-into-the-folder-without-a-slash", "install-into-the-folder",
                                             "cp-r-of-a-folders-contents"),
}
LEADING_OUT_CASES = [(kind, form) for kind, forms in sorted(LEADING_OUT.items()) for form in forms]


@pytest.mark.parametrize("kind,form", LEADING_OUT_CASES, ids=[f"{k}--{f}" for k, f in LEADING_OUT_CASES])
def test_a_copy_into_an_own_folder_folder_that_lands_on_an_entry_leading_out_is_refused(opened, sandbox, project,
                                                                                         kind, form):
    own, other = opened
    d = own / "d"
    entry = d / PAYLOAD
    target = _plant(kind, entry, project, other)
    _refused(_ask(sandbox, project, "Write", entry), f"premise: Write on {entry} ({kind})", sandbox, entry, target)
    command = _command(form, sandbox.elsewhere, d)
    _refused(_ask(sandbox, project, "Bash", command),
             f"Bash `{command}` ({form}; {d} holds {PAYLOAD}, {kind})", sandbox, entry, d, target)


LINKED_FOLDERS = ("another-tickets-folder", "the-projects-acceptance-test-folder")
FOLDER_FORMS = {"with-a-slash": "cp -r {src}/s {d}/", "without-a-slash": "cp -r {src}/s {d}"}


@pytest.mark.parametrize("form", sorted(FOLDER_FORMS))
@pytest.mark.parametrize("linked", LINKED_FOLDERS)
def test_a_folder_copy_onto_a_link_to_a_folder_outside_is_refused(opened, sandbox, project, linked, form):
    """``cp -r s d/`` where ``d/s`` is a link to a folder outside the own folder: the files land in that folder."""
    own, other = opened
    d = own / "d"
    d.mkdir()
    target = other if linked == "another-tickets-folder" else (project / ACCEPTANCE_TEST).parent
    (d / "s").symlink_to(target, target_is_directory=True)
    _refused(_ask(sandbox, project, "Write", d / "s" / PAYLOAD), f"premise: Write on {d / 's' / PAYLOAD} ({linked})",
             sandbox, d / "s" / PAYLOAD, target)
    command = FOLDER_FORMS[form].format(src=q(sandbox.elsewhere), d=q(d))
    _refused(_ask(sandbox, project, "Bash", command), f"Bash `{command}` ({d}/s links to {target})", sandbox,
             d / "s", d, target)


CONTROL_FORMS = PLAIN_FORMS + ("cp-r-of-a-folder",)


@pytest.mark.parametrize("form", CONTROL_FORMS)
def test_an_ordinary_copy_into_an_own_folder_folder_is_allowed(opened, sandbox, project, form):
    """The control: the same forms into a folder of the own folder that holds no such entry."""
    own, _ = opened
    d = own / "clean"
    d.mkdir()
    if form == "cp-r-of-a-folder":
        command = f"cp -r {q(sandbox.elsewhere / 's')} {q(d)}/"
    else:
        command = _command(form, sandbox.elsewhere, d)
    support.assert_allowed(_ask(sandbox, project, "Bash", command), f"Bash `{command}` (a folder holding no such entry)")


@pytest.mark.parametrize("form", ("cp-into-the-folder-with-a-slash", "install-into-the-folder"))
def test_a_copy_over_an_ordinary_file_of_the_same_name_in_the_own_folder_is_allowed(opened, sandbox, project, form):
    own, _ = opened
    d = own / "d"
    support.write(d / PAYLOAD, "VALUE = 1\n")
    command = _command(form, sandbox.elsewhere, d)
    support.assert_allowed(_ask(sandbox, project, "Bash", command), f"Bash `{command}` ({d / PAYLOAD} an ordinary file)")


# --------------------------------------------------------------------------
# F1. Inside the repository, for every ticket (W2-H056)
# --------------------------------------------------------------------------

# A role, its ticket, and a folder inside its allowed paths.
IN_REPOSITORY = {
    "the-engineer-in-src-app": (ENGINEER, MAIN, "src/app/drop"),
    "product-spec-in-docs-spec": (PRODUCT_SPEC, SPEC, "docs/spec/drop"),
}
REPOSITORY_FORMS = ("cp-into-the-folder-with-a-slash", "install-into-the-folder")


@pytest.mark.parametrize("form", REPOSITORY_FORMS)
@pytest.mark.parametrize("who", sorted(IN_REPOSITORY))
def test_a_copy_into_a_repository_folder_that_lands_on_a_link_to_the_acceptance_test_is_refused(sandbox, project,
                                                                                                who, form):
    role, ticket, rel = IN_REPOSITORY[who]
    _sources(sandbox)
    target = support.write(project / ACCEPTANCE_TEST, "def test_kpi():\n    assert True\n")
    d = project / rel
    d.mkdir(parents=True)
    (d / PAYLOAD).symlink_to(target)
    _refused(_ask(sandbox, project, "Write", d / PAYLOAD, ticket.tk, role), f"premise: Write on {d / PAYLOAD} by {role}",
             sandbox, d / PAYLOAD, target, "acceptance")
    command = _command(form, sandbox.elsewhere, d)
    _refused(_ask(sandbox, project, "Bash", command, ticket.tk, role),
             f"Bash `{command}` by {role} on {ticket.tk} ({d / PAYLOAD} links to {target})", sandbox, d / PAYLOAD, d,
             target, "acceptance")


@pytest.mark.parametrize("form", REPOSITORY_FORMS + ("cp-r-of-a-folders-contents",))
@pytest.mark.parametrize("who", sorted(IN_REPOSITORY))
def test_an_ordinary_copy_into_an_allowed_repository_folder_is_allowed(sandbox, project, who, form):
    """The control: the same forms into a folder of the role's paths that holds no such entry."""
    role, ticket, rel = IN_REPOSITORY[who]
    _sources(sandbox)
    d = project / rel
    d.mkdir(parents=True)
    command = _command(form, sandbox.elsewhere, d)
    support.assert_allowed(_ask(sandbox, project, "Bash", command, ticket.tk, role),
                           f"Bash `{command}` by {role} on {ticket.tk} (a folder of its paths, no such entry)")


# --------------------------------------------------------------------------
# F1. The own folder's marker (W2-L349)
# --------------------------------------------------------------------------

@pytest.fixture()
def marked(sandbox, project):
    """MAIN's folder made by a launch; the marker's name, from a listing of that folder right after the launch.

    A file of the test's own, named like the marker, waits in ``staging/`` of the own folder with an ordinary file.
    """
    own = support.open_own_folder(sandbox, MAIN)
    names = sorted(os.listdir(own))
    assert len(names) == 1, f"premise: the launch left {names} in {own}, not exactly one entry (the marker)"
    name = names[0]
    assert (own / name).is_file() and not (own / name).is_symlink(), f"premise: {own / name} is not a regular file"
    support.write(own / "staging" / name, "a file of the test's own, named like the marker\n")
    support.write(own / "staging" / "ordinary.txt", "ordinary\n")
    return own, name


MARKER_FORMS = {
    "cp-into-the-folder-with-a-slash": "cp {staging}/{name} {own}/",
    "cp-into-the-folder-without-a-slash": "cp {staging}/{name} {own}",
    "install-into-the-folder": "install {staging}/{name} {own}/",
    "cp-r-of-a-folders-contents": "cp -r {staging}/. {own}/",
    "mv-into-the-folder": "mv {staging}/{name} {own}/",
}


def test_the_marker_named_directly_is_refused(marked, sandbox, project):
    """The premise of the marker forms (CIT-E difference 15): Write, and ``cp`` / ``mv`` onto the marker by its name."""
    own, name = marked
    marker = own / name
    _refused(_ask(sandbox, project, "Write", marker), f"Write on the marker {marker}", sandbox, marker)
    for verb in ("cp", "mv"):
        command = f"{verb} {q(own / 'staging' / name)} {q(marker)}"
        _refused(_ask(sandbox, project, "Bash", command), f"Bash `{command}`", sandbox, marker)


@pytest.mark.parametrize("form", sorted(MARKER_FORMS))
def test_a_copy_install_or_move_of_a_file_named_like_the_marker_into_the_own_folder_is_refused(marked, sandbox,
                                                                                                project, form):
    own, name = marked
    command = MARKER_FORMS[form].format(staging=q(own / "staging"), own=q(own), name=q(name))
    if form == "cp-r-of-a-folders-contents":
        os.remove(own / "staging" / "ordinary.txt")
    _refused(_ask(sandbox, project, "Bash", command), f"Bash `{command}` (lands on the marker {own / name})", sandbox,
             own / name, own)


@pytest.mark.parametrize("form", ("cp-into-the-folder-with-a-slash", "install-into-the-folder", "mv-into-the-folder"))
def test_an_ordinary_file_copied_or_moved_into_the_own_folder_is_allowed(marked, sandbox, project, form):
    """The control of the marker forms: the same forms with an ordinary file."""
    own, _ = marked
    command = MARKER_FORMS[form].format(staging=q(own / "staging"), own=q(own), name="ordinary.txt")
    support.assert_allowed(_ask(sandbox, project, "Bash", command), f"Bash `{command}` (an ordinary file)")


# --------------------------------------------------------------------------
# F2. A project whose real root lies inside ~/gov-os-runs gets no own folder
# --------------------------------------------------------------------------

FORGED = support.Ticket("DAEO-zz77", ENGINEER, "W2-77", ("src/app/**",))    # in_progress; names W2-77, no folder yet


@pytest.fixture()
def first(sandbox, project, cli):
    """The first project (the worktree ``~/gov-os-worktrees/W2-90``, outside the root), launched for MAIN and OTHER."""
    for ticket in (MAIN, OTHER):
        _launched(sandbox, cli, ticket)
        assert sandbox.own(ticket).is_dir(), f"premise: the first project's launch made no {sandbox.own(ticket)}"
        support.write(sandbox.own(ticket) / "work" / "README.md", f"{ticket.folder}'s work, by the first project\n")
    return project


def _forged_project(location, gitdir):
    """A project written from the suite's files at ``location``, whose ``.git`` is a file naming ``gitdir``."""
    files = dict(support.PROJECT_FILES)
    for ticket in support.TICKETS:
        files[f".tickets/{ticket.tk}.md"] = support.ticket_text(ticket)
    files[".claude/settings.json"] = json.dumps({"hooks": {
        "PreToolUse": [{"matcher": "*", "hooks": [{"type": "command", "command": support.GUARD_COMMAND}]}],
    }}, indent=2) + "\n"
    for rel, text in files.items():
        support.write(location / rel, text)
    for rel, source in support.COPIED_FILES.items():
        (location / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, location / rel)
    support.write(location / ".git", f"gitdir: {gitdir}\n")
    return location


# The forms of a project under the root, by how it is made.
UNDER_THE_ROOT = (
    "a-git-file-naming-the-first-projects-common-directory",
    "a-worktree-of-the-first-project",
    "a-clone-of-the-first-project",
    "a-worktree-reached-through-a-link-outside-the-root",
)


def _under_the_root(sandbox, first, form):
    """``(box, project, real)``: a project whose real root lies in MAIN's own folder, holding FORGED's ticket."""
    own = sandbox.own(MAIN)
    if form == "a-git-file-naming-the-first-projects-common-directory":
        project = _forged_project(own / "forged", first / ".git")
    elif form == "a-worktree-of-the-first-project":
        project = own / "wt"
        support.git(first, "worktree", "add", "-q", "-b", "under-the-root", str(project))
    elif form == "a-clone-of-the-first-project":
        project = own / "clone"
        support.git(own, "clone", "-q", "--no-hardlinks", str(first), str(project))
    else:
        real = own / "wt-linked"
        support.git(first, "worktree", "add", "-q", "-b", "through-a-link", str(real))
        project = sandbox.home / "projects" / "via-link"
        project.parent.mkdir(parents=True)
        project.symlink_to(real, target_is_directory=True)
    support.write(project / ".tickets" / f"{FORGED.tk}.md", support.ticket_text(FORGED))
    real = Path(os.path.realpath(project))
    assert support.covers(os.path.realpath(own), real), f"premise: {project} does not lie in {own}"
    assert (project / support.GUARD_REL).is_file(), f"premise: {project} has no guard hook"
    return _at(sandbox, project), project, real


# The folders under the root a session of that project is refused, by the ticket it names.
FOLDERS = (
    "another-tickets-folder-the-first-project-made",
    "the-own-tickets-folder-that-holds-the-project",
    "a-folder-made-by-hand",
    "a-folder-the-projects-own-launch-would-make",
)


def _folder_case(sandbox, box, cli, folder):
    """``(ticket, path)``: the session's ticket and the folder under the root its calls name."""
    if folder == "another-tickets-folder-the-first-project-made":
        return OTHER, sandbox.own(OTHER)
    if folder == "the-own-tickets-folder-that-holds-the-project":
        return MAIN, sandbox.own(MAIN)
    if folder == "a-folder-made-by-hand":
        support.write(sandbox.own(FORGED) / "work" / "README.md", "made by hand\n")
        return FORGED, sandbox.own(FORGED)
    support.launch(box, cli, ENGINEER, FORGED)        # the public way a folder would be made; F2: it makes none
    return FORGED, sandbox.own(FORGED)


@pytest.mark.parametrize("folder", FOLDERS)
@pytest.mark.parametrize("form", UNDER_THE_ROOT)
def test_a_project_under_the_root_gets_nothing_in_a_folder_under_the_root(first, sandbox, cli, form, folder):
    box, project, real = _under_the_root(sandbox, first, form)
    ticket, path = _folder_case(sandbox, box, cli, folder)
    what = f"by the engineer on {ticket.tk} of the project {project} under the root ({form}; {folder})"
    target = path / "work" / "README.md"
    assert not support.covers(str(real), target), f"premise: {target} lies inside the project {real}"
    for tool_name in ("Write", "Edit"):
        _refused(_ask(box, project, tool_name, target, ticket.tk), f"{tool_name} on {target} {what}", box, target)
    for command in (f"echo written > {q(target)}", f"rm -rf {q(path / 'work')}"):
        _refused(_ask(box, project, "Bash", command, ticket.tk), f"Bash `{command}` {what}", box, path, target)
    # The success control: the first project, outside the root, keeps its own folder.
    if folder == "another-tickets-folder-the-first-project-made":
        support.assert_allowed(_ask(sandbox, first, "Write", target, OTHER.tk),
                               f"Write on {target} by the first project's session on {OTHER.tk}, after the other's calls")


@pytest.mark.parametrize("form", UNDER_THE_ROOT)
def test_a_project_under_the_root_keeps_its_in_project_writes(first, sandbox, form):
    """The control of the refusals above: a path of the ticket's own inside that project is judged as before."""
    box, project, _ = _under_the_root(sandbox, first, form)
    target = project / "src" / "app" / "main.py"
    for tool_name in ("Write", "Edit"):
        support.assert_allowed(_ask(box, project, tool_name, target, MAIN.tk), f"{tool_name} on {target} ({form})")


@pytest.mark.parametrize("ticket", (OTHER, FORGED), ids=("a-folder-the-first-project-made", "a-folder-not-there-yet"))
@pytest.mark.parametrize("form", UNDER_THE_ROOT)
def test_a_launch_from_a_project_under_the_root_adds_makes_and_writes_nothing_there(first, sandbox, cli, form, ticket):
    box, project, real = _under_the_root(sandbox, first, form)
    before = _state(sandbox.root, skip=real)
    result = _launched(box, cli, ticket)
    holding = _entries_at_or_under_the_root(result, box)
    assert holding == [], (
        f"the sandbox of a session on {ticket.tk} in the project {project} under the root ({form}) may write at or "
        f"under the root through {holding}: allowWrite is {result.allow_write()}")
    assert _state(sandbox.root, skip=real) == before, (
        f"a launch from the project {project} under the root ({form}) made or changed something under the root "
        f"outside the project: {sorted(set(_state(sandbox.root, skip=real).items()) ^ set(before.items()))}")
    _assert_temp_folder_kept(result, box)
    # The success control: the first project's launch of the same ticket's folder keeps it.
    if ticket is OTHER:
        again = _launched(sandbox, cli, OTHER)
        assert any(support.covers(r, sandbox.own(OTHER) / "f.txt") for _, r in _real_entries(again, sandbox)), (
            f"the first project's launch of {OTHER.tk} lost its folder: {again.allow_write()}")
