"""W2-50, the review's finding D (DEC-774), as described behaviour (DEC-136): tests added after implementation.

The review of the last round found that ``cp -b`` (``--backup``), ``install``,
``mv`` and ``cp --remove-destination`` onto a symbolic link replace the link
with a new file at the link's own path, while the guard judges the link's
target: where such a link sits at a protected name, a session puts a file
there. The owner decided it (DEC-774, 2026-10-18). Each case is tested through
the interface the suite already drives: the guard's PreToolUse hook with the
call on stdin.

D. **A write that replaces a symbolic link rather than following it is
   refused, as a form the guard cannot read ("doubt").** What each form does
   to a link was found by running it in a temporary folder (GNU coreutils 9.4;
   see the README): a backup (``-b``, ``--backup``, ``-S``, ``--suffix``),
   ``--remove-destination`` (and the abbreviations ``cp`` accepts), ``cp -f``
   onto a link whose target it cannot open for writing, every ``install`` and
   every ``mv`` replace the link; so does ``-T`` onto a link to a folder
   (``mv``, ``install``, ``cp -b``), and ``cp -P`` / ``-a`` / ``-R`` /
   ``--no-dereference`` of a source that is itself a link. ``cp -f`` onto a
   link is a form that may replace (the guard cannot know ahead whether the
   target opens): refused too. A link moved away (``mv <link> <elsewhere>``)
   is written at its own path. Each form is asked with the link at a
   protected name (the fixture project's acceptance folder, or another
   ticket's folder pointing into the session's own folder) and, for a few,
   in an allowed folder pointing to an allowed file: the rule is for the
   form, not the place.

   **As doubt.** Each case first asks the guard for ``ln -t <an allowed
   folder> X``, refused today as a form it cannot read, and takes the target
   its refusal names (the first quoted path of the reason). A case in an
   allowed place must be refused naming that same target: nothing else there
   is refused. A case at a protected name must be refused naming that target,
   or the link's own path, or the link's folder (as given or normalised; the
   guard may also name the place it refuses).
Controls. A plain ``cp`` (no backup, no ``-f``, no ``--remove-destination``)
   writes through a link to an allowed, writable file: allowed, in an allowed
   folder and at a protected name; ``cp -t``, too. A link to a folder used as
   the destination folder, or at a middle level, is followed by ``cp``,
   ``install`` and ``mv``: allowed. The replacing forms onto ordinary files
   that are not links: allowed. A link moved between allowed folders:
   allowed.

No allowed command is run: every case asks the guard only. The sources are
files of the test's own in ``src/app/staging/`` (in the session's paths), so a
move's source lies where the session may write. Every link is made by the
fixture in the test's own temporary tree. Every location is the suite's: a
temporary HOME, a temp folder disjoint from it, the fixture project built from
scratch, and own folders made by a launch.
"""

from __future__ import annotations

import os
import re

import pytest

import w2_50_support as support

q = support.q
MAIN, OTHER = support.MAIN, support.OTHER
ENGINEER = support.ENGINEER

ACCEPTANCE_FOLDER = "tests/acceptance/W2-90"           # the fixture project's acceptance tests (MAIN's)


# --------------------------------------------------------------------------
# The layout
# --------------------------------------------------------------------------

@pytest.fixture()
def links(sandbox, project):
    """MAIN's and OTHER's folders made by a launch; the links; the sources. The paths by name.

    Links at a protected name:
    - ``AL``: ``tests/acceptance/W2-90/test_link.py`` -> ``src/app/allowed.py`` (allowed, writable);
    - ``AR``: ``tests/acceptance/W2-90/test_ro.py`` -> ``src/app/readonly.py`` (allowed, mode 0444);
    - ``AX``: ``tests/acceptance/W2-90/test_dangling.py`` -> ``src/app/missing.py`` (not there);
    - ``OL``: ``~/gov-os-runs/W2-91/mylink`` -> ``~/gov-os-runs/W2-90/mine.txt`` (the session's own folder);
    - ``OD``: ``~/gov-os-runs/W2-91/dirlink`` -> ``~/gov-os-runs/W2-90/sub/`` (a link to a folder).
    Links in an allowed folder, to an allowed place:
    - ``PL``: ``src/app/links/ok_link.py`` -> ``src/app/allowed.py``;
    - ``PR``: ``src/app/links/ro_link.py`` -> ``src/app/readonly.py``;
    - ``PD``: ``src/app/dirlink`` -> ``src/app/d/`` (a link to a folder);
    - ``WL``: ``~/gov-os-runs/W2-90/links/ok_link.txt`` -> ``~/gov-os-runs/W2-90/mine.txt``;
    - ``WD``: ``~/gov-os-runs/W2-90/dirlink`` -> ``~/gov-os-runs/W2-90/sub/``.
    Folders: ``AF`` the acceptance folder, ``OF`` OTHER's folder, ``PF`` ``src/app/links``, ``WF``
    ``~/gov-os-runs/W2-90/links``, ``O`` MAIN's folder, ``P`` the project. Sources in ``S``
    (``src/app/staging/``): ``X``, and one file at each link's name (``test_link.py``, ``mylink``,
    ``ok_link.py``, ``ok_link.txt``) for the ``-t`` forms; ``SL``, a link to ``X``. Ordinary files:
    ``src/app/existing.py``, ``~/gov-os-runs/W2-90/d2/f.txt``.
    """
    own, other = support.open_own_folder(sandbox, MAIN), support.open_own_folder(sandbox, OTHER)
    app = project / "src/app"
    accept = project / ACCEPTANCE_FOLDER
    support.write(accept / "test_a.py", "def test_a():\n    assert True\n")
    allowed = support.write(app / "allowed.py", "VALUE = 2\n")
    readonly = support.write(app / "readonly.py", "VALUE = 3\n")
    readonly.chmod(0o444)
    (accept / "test_link.py").symlink_to(allowed)
    (accept / "test_ro.py").symlink_to(readonly)
    (accept / "test_dangling.py").symlink_to(app / "missing.py")
    mine = support.write(own / "mine.txt", "mine\n")
    (own / "sub").mkdir()
    (other / "mylink").symlink_to(mine)
    (other / "dirlink").symlink_to(own / "sub", target_is_directory=True)
    (app / "links").mkdir()
    (app / "links" / "ok_link.py").symlink_to(allowed)
    (app / "links" / "ro_link.py").symlink_to(readonly)
    (app / "d").mkdir()
    (app / "dirlink").symlink_to(app / "d", target_is_directory=True)
    (own / "links").mkdir()
    (own / "links" / "ok_link.txt").symlink_to(mine)
    (own / "dirlink").symlink_to(own / "sub", target_is_directory=True)
    staging = app / "staging"
    for name in ("X", "test_link.py", "mylink", "ok_link.py", "ok_link.txt"):
        support.write(staging / name, f"{name}\n")
    (staging / "SL").symlink_to(staging / "X")
    support.write(app / "existing.py", "VALUE = 1\n")
    support.write(own / "d2" / "f.txt", "f\n")
    paths = {
        "AL": accept / "test_link.py", "AR": accept / "test_ro.py", "AX": accept / "test_dangling.py",
        "OL": other / "mylink", "OD": other / "dirlink",
        "PL": app / "links" / "ok_link.py", "PR": app / "links" / "ro_link.py", "PD": app / "dirlink",
        "WL": own / "links" / "ok_link.txt", "WD": own / "dirlink",
        "AF": accept, "OF": other, "PF": app / "links", "WF": own / "links",
        "O": own, "P": project, "S": staging,
    }
    for key in ("AL", "AR", "AX", "OL", "OD", "PL", "PR", "PD", "WL", "WD"):
        assert paths[key].is_symlink(), f"premise: {paths[key]} is not a symbolic link"
    return paths


PROTECTED = ("AL", "AR", "AX", "OL", "OD")      # links at a protected name
ALLOWED = ("PL", "PR", "PD", "WL", "WD")        # links in an allowed folder, to an allowed place


def _ask(sandbox, project, command):
    return support.ask_guard(sandbox, "Bash", support.tool_input("Bash", command), ENGINEER, MAIN.tk, project)


def _fill(template, paths):
    """A command from its template: ``{NAME}`` is the quoted path, ``{NAME}/rest`` keeps the rest as written."""
    return template.format(**{name: q(path) for name, path in paths.items()})


def _forms(path):
    path = str(path)
    return {path, os.path.normpath(path)}


def _doubt_target(sandbox, project, paths):
    """Ask the guard for ``ln -t <an allowed folder> X`` (refused today as a form it cannot read); the target it names."""
    command = f"ln -t {q(paths['P'] / 'src/app/d')} {q(paths['S'] / 'X')}"
    result = _ask(sandbox, project, command)
    support.assert_refused(result, f"premise: Bash `{command}` (ln -t, the form the guard cannot read)")
    quoted = re.findall(r"'([^']*)'", result.reason)
    return quoted[0] if quoted else None


# --------------------------------------------------------------------------
# D. A write that replaces a link is refused as doubt (DEC-774)
# --------------------------------------------------------------------------

# id: (command, the link the call replaces or moves). Ids end in the link's place.
REPLACING = {
    # cp with a backup: the link is renamed to <link><suffix>, a new file made at its path.
    "cp-b--acceptance": ("cp -b {S}/X {AL}", "AL"),
    "cp-b--other-ticket": ("cp -b {S}/X {OL}", "OL"),
    "cp-b--allowed": ("cp -b {S}/X {PL}", "PL"),
    "cp-backup--acceptance": ("cp --backup {S}/X {AL}", "AL"),
    "cp-backup-simple--other-ticket": ("cp --backup=simple {S}/X {OL}", "OL"),
    "cp-backup-numbered--acceptance": ("cp --backup=numbered {S}/X {AL}", "AL"),
    "cp-S-joined--acceptance": ("cp -S.t {S}/X {AL}", "AL"),
    "cp-S-joined--own-folder": ("cp -S.t {S}/X {WL}", "WL"),
    "cp-suffix--other-ticket": ("cp --suffix=.bak {S}/X {OL}", "OL"),
    "cp-bS-joined-value-separate--acceptance": ("cp -bS .t {S}/X {AL}", "AL"),
    "cp-b-S-separate--other-ticket": ("cp -b -S .t {S}/X {OL}", "OL"),
    "cp-b-f--acceptance": ("cp -b -f {S}/X {AL}", "AL"),
    "cp-b-t--acceptance": ("cp -b -t {AF} {S}/test_link.py", "AL"),
    "cp-b-t--other-ticket": ("cp -b -t {OF} {S}/mylink", "OL"),
    "cp-backup-t--allowed": ("cp --backup -t {PF} {S}/ok_link.py", "PL"),
    "cp-b-T--acceptance": ("cp -b -T {S}/X {AL}", "AL"),
    "cp-b-dashdash--other-ticket": ("cp -b -- {S}/X {OL}", "OL"),
    # cp --remove-destination: the link is removed, a new file made at its path.
    "cp-remove-destination--acceptance": ("cp --remove-destination {S}/X {AL}", "AL"),
    "cp-remove-destination--other-ticket": ("cp --remove-destination {S}/X {OL}", "OL"),
    "cp-remove-destination--allowed": ("cp --remove-destination {S}/X {PL}", "PL"),
    "cp-rem-abbreviated--acceptance": ("cp --rem {S}/X {AL}", "AL"),
    "cp-remove-destination-t--other-ticket": ("cp --remove-destination -t {OF} {S}/mylink", "OL"),
    "cp-remove-abbreviated-t--acceptance": ("cp --remove -t {AF} {S}/test_link.py", "AL"),
    # cp -f: replaces a link whose target it cannot open for writing; a form that may replace.
    "cp-f-target-unwritable--acceptance": ("cp -f {S}/X {AR}", "AR"),
    "cp-force-target-unwritable--acceptance": ("cp --force {S}/X {AR}", "AR"),
    "cp-f-target-unwritable--allowed": ("cp -f {S}/X {PR}", "PR"),
    "cp-f-target-writable--acceptance": ("cp -f {S}/X {AL}", "AL"),
    "cp-force-target-writable--other-ticket": ("cp --force {S}/X {OL}", "OL"),
    "cp-f-target-writable--allowed": ("cp -f {S}/X {PL}", "PL"),
    "cp-f-dangling--acceptance": ("cp -f {S}/X {AX}", "AX"),
    # install: always replaces the link.
    "install--acceptance": ("install {S}/X {AL}", "AL"),
    "install--other-ticket": ("install {S}/X {OL}", "OL"),
    "install--allowed": ("install {S}/X {PL}", "PL"),
    "install-m--acceptance": ("install -m 644 {S}/X {AL}", "AL"),
    "install-b--other-ticket": ("install -b {S}/X {OL}", "OL"),
    "install-t--acceptance": ("install -t {AF} {S}/test_link.py", "AL"),
    "install-t--other-ticket": ("install -t {OF} {S}/mylink", "OL"),
    "install-T--acceptance": ("install -T {S}/X {AL}", "AL"),
    "install-D--other-ticket": ("install -D {S}/X {OL}", "OL"),
    # mv: always replaces the link (a rename over it).
    "mv--acceptance": ("mv {S}/X {AL}", "AL"),
    "mv--other-ticket": ("mv {S}/X {OL}", "OL"),
    "mv--allowed": ("mv {S}/X {PL}", "PL"),
    "mv-f--acceptance": ("mv -f {S}/X {AL}", "AL"),
    "mv-b--other-ticket": ("mv -b {S}/X {OL}", "OL"),
    "mv-T--acceptance": ("mv -T {S}/X {AL}", "AL"),
    "mv-t--acceptance": ("mv -t {AF} {S}/test_link.py", "AL"),
    "mv-t--other-ticket": ("mv -t {OF} {S}/mylink", "OL"),
    "mv-dashdash--other-ticket": ("mv -- {S}/X {OL}", "OL"),
    # -T onto a link to a folder: the folder link itself is replaced by a file.
    "mv-T-onto-a-folder-link--other-ticket": ("mv -T {S}/X {OD}", "OD"),
    "install-T-onto-a-folder-link--other-ticket": ("install -T {S}/X {OD}", "OD"),
    "cp-b-T-onto-a-folder-link--other-ticket": ("cp -b -T {S}/X {OD}", "OD"),
    "mv-T-onto-a-folder-link--allowed": ("mv -T {S}/X {PD}", "PD"),
    # A source that is itself a link, copied as a link: the destination link is replaced by a new link.
    "cp-P-of-a-link--acceptance": ("cp -P {S}/SL {AL}", "AL"),
    "cp-a-of-a-link--other-ticket": ("cp -a {S}/SL {OL}", "OL"),
    "cp-R-of-a-link--acceptance": ("cp -R {S}/SL {AL}", "AL"),
    "cp-no-dereference-of-a-link--allowed": ("cp --no-dereference {S}/SL {PL}", "PL"),
    # A link moved away: the call writes at the link's own path (it is no longer there).
    "mv-a-link-away--acceptance": ("mv {AL} {O}/x", "AL"),
    "mv-a-link-away--other-ticket": ("mv {OL} {O}/x", "OL"),
    "mv-a-folder-link-away--other-ticket": ("mv {OD} {O}/moved", "OD"),
    "mv-t-a-link-away--acceptance": ("mv -t {O}/sub {AL}", "AL"),
}


@pytest.mark.parametrize("case", sorted(REPLACING))
def test_a_write_that_replaces_a_link_is_refused_as_a_form_the_guard_cannot_read(links, sandbox, project, case):
    template, key = REPLACING[case]
    link = links[key]
    doubt = _doubt_target(sandbox, project, links)
    command = _fill(template, links)
    where = "at a protected name" if key in PROTECTED else "in an allowed folder, to an allowed place"
    what = f"Bash `{command}` ({case}; it replaces the link {link} -> {os.readlink(link)}, {where})"
    result = _ask(sandbox, project, command)
    support.assert_refused(result, what)
    names = {doubt} if doubt else set()
    if key in PROTECTED:
        names |= _forms(link) | _forms(link.parent)
    if names:
        assert any(name in result.reason for name in names), (
            f"{what}: refused, but not as the form the guard cannot read: an `ln -t` is refused naming {doubt!r}; "
            f"this refusal names none of {sorted(names)}: {result.reason[:400]!r}")


# --------------------------------------------------------------------------
# Controls: a write that follows a link stays allowed
# --------------------------------------------------------------------------

# A plain cp writes through a link to an allowed, writable file: the link stays, its target changes.
THROUGH = {
    "cp--allowed": "cp {S}/X {PL}",
    "cp--own-folder": "cp {S}/X {WL}",
    "cp-t--allowed": "cp -t {PF} {S}/ok_link.py",
    "cp-t--own-folder": "cp -t {WF} {S}/ok_link.txt",
    "cp--acceptance-link-to-an-allowed-file": "cp {S}/X {AL}",
    "cp--other-tickets-link-into-the-own-folder": "cp {S}/X {OL}",
}


@pytest.mark.parametrize("form", sorted(THROUGH))
def test_a_plain_copy_through_a_link_to_an_allowed_file_is_allowed(links, sandbox, project, form):
    command = _fill(THROUGH[form], links)
    support.assert_allowed(_ask(sandbox, project, command), f"Bash `{command}` ({form}; cp writes through the link)")


# A link to a folder as the destination folder, or at a middle level: the tools write into the folder it points to.
FOLDER_LINK = {
    "cp-into-a-folder-link": "cp {S}/X {PD}/",
    "cp-b-into-a-folder-link": "cp -b {S}/X {PD}/",
    "install-into-a-folder-link": "install {S}/X {PD}/",
    "install-m-into-a-folder-link": "install -m 644 {S}/X {PD}/",
    "mv-into-a-folder-link": "mv {S}/X {PD}/",
    "cp-through-a-folder-link-at-a-middle-level": "cp {S}/X {PD}/new.py",
    "install-through-a-folder-link-at-a-middle-level": "install {S}/X {PD}/new.py",
    "mv-through-a-folder-link-at-a-middle-level": "mv {S}/X {PD}/new.py",
    "cp-into-a-folder-link-of-the-own-folder": "cp {S}/X {WD}/",
    "mv-into-a-folder-link-of-the-own-folder": "mv {S}/X {WD}/",
}


@pytest.mark.parametrize("form", sorted(FOLDER_LINK))
def test_a_copy_install_or_move_through_a_link_to_an_allowed_folder_is_allowed(links, sandbox, project, form):
    command = _fill(FOLDER_LINK[form], links)
    support.assert_allowed(_ask(sandbox, project, command),
                           f"Bash `{command}` ({form}; the tool writes into the folder the link points to)")


# The replacing forms onto an ordinary file that is not a link.
ONTO_ORDINARY = {
    "cp-b": "cp -b {src} {dst}",
    "cp-remove-destination": "cp --remove-destination {src} {dst}",
    "cp-f": "cp -f {src} {dst}",
    "install": "install {src} {dst}",
    "mv-b": "mv -b {src} {dst}",
}
ORDINARY_FILES = {"repository": ("P", "src/app/existing.py"), "own-folder": ("O", "d2/f.txt")}


@pytest.mark.parametrize("where", sorted(ORDINARY_FILES))
@pytest.mark.parametrize("form", sorted(ONTO_ORDINARY))
def test_a_replacing_form_onto_an_ordinary_allowed_file_is_allowed(links, sandbox, project, form, where):
    head, rest = ORDINARY_FILES[where]
    destination = links[head] / rest
    assert destination.is_file() and not destination.is_symlink(), f"premise: {destination} is not an ordinary file"
    command = ONTO_ORDINARY[form].format(src=q(links["S"] / "X"), dst=q(destination))
    support.assert_allowed(_ask(sandbox, project, command), f"Bash `{command}` ({form}, onto an ordinary file)")


MOVED_LINKS = {
    "a-link-of-the-repository": "mv {PL} {P}/src/app/d/",
    "a-link-of-the-own-folder": "mv {WL} {O}/sub/",
}


@pytest.mark.parametrize("form", sorted(MOVED_LINKS))
def test_a_link_moved_between_allowed_folders_is_allowed(links, sandbox, project, form):
    command = _fill(MOVED_LINKS[form], links)
    support.assert_allowed(_ask(sandbox, project, command), f"Bash `{command}` ({form}, from and to allowed folders)")
