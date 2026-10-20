"""W2-50, the review of the last round (DEC-764, DEC-765), as described behaviour (DEC-136): tests added after implementation.

The review of the last round found two behaviours the suite did not hold; the
owner decided them (DEC-764 and DEC-765, 2026-10-18). Each is tested through
the interface the suite already drives: the guard's PreToolUse hook with the
call on stdin.

A. **A copy whose landed path is not ``<folder>/<name>`` is refused, as a form
   the guard cannot read** (DEC-764). ``cp --parents <source> <folder>``
   writes ``<folder>/<source as written>``: with ``..`` in the source, or
   through a link at a middle level of that path, it lands outside the
   allowed place. Every such call is refused whatever its source, the way the
   guard refuses ``ln -t`` today: each case asks the guard for an ``ln -t`` of
   the same folder first, takes the target its refusal names (the quoted path
   of the guard's reason), and asks that the ``--parents`` refusal name the
   same. The abbreviations ``cp`` accepts (``--parent``, ``--par``) are the
   same option. ``install --help`` and ``mv --help`` list no option that
   makes the landed path other than ``<folder>/<name>`` or the named
   destination: no case for them.
B. **An option's value is read as a value, and nothing after ``--`` is read as
   an option** (DEC-765). ``cp -S.t``, ``install -oroot``, ``install -m+t``
   and the rest name a suffix, an owner, a mode or a group, never ``-t``;
   ``cp -- -t F`` copies the file named ``-t``. Each call is judged as the
   files it writes (found by running each form in a temporary folder: the
   destination, and with ``-S`` or ``--suffix`` the backup
   ``<destination><suffix>`` of the file it replaces), and refused with the
   guard's reason, naming one of them, when one is refused as a direct write.
   ``-Z`` takes no value on this machine: ``cp -Zt <folder> X`` is a copy into
   ``<folder>`` and stays judged (a fail-closed control).
Controls. Ordinary copies, installs and moves into an allowed folder, the
   ``-t`` and ``-m`` forms, and a value with no ``t`` or a ``--`` onto an
   allowed file stay as before: allowed into an allowed place, refused into a
   protected one.

No allowed command is run: every case asks the guard only. The sources are
files of the test's own, in ``elsewhere/`` or in an allowed folder of the
session (``src/app/staging/``, ``~/gov-os-runs/W2-90/staging/``), so a move's
source lies where the session may write. Every location is the suite's: a
temporary HOME, a temp folder disjoint from it, the fixture project built from
scratch, and own folders made by a launch.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

import w2_50_support as support

q = support.q
MAIN, OTHER = support.MAIN, support.OTHER
ENGINEER = support.ENGINEER

ACCEPTANCE_FOLDER = "tests/acceptance/W2-90"           # the fixture project's acceptance tests (MAIN's)
ACCEPTANCE_TEST = f"{ACCEPTANCE_FOLDER}/test_a.py"


# --------------------------------------------------------------------------
# The layout and the guard, asked from a working folder
# --------------------------------------------------------------------------

@pytest.fixture()
def places(sandbox, project):
    """MAIN's and OTHER's folders made by a launch, the acceptance test, the sources; the paths by name.

    - ``E``: ``elsewhere/``, holding ``X``, ``s/inner.py``, ``W2-91/work.txt``, ``lnk/work.txt``,
      ``sub/test_a.py`` and the folder ``cwd/``;
    - ``O``: MAIN's own folder, holding ``d/`` (empty), ``d2/`` with ``f.txt``, ``staging/X`` and ``lnk``, a
      link to OTHER's folder (which holds ``work.txt``);
    - ``P``: the project, holding ``src/app/d/`` (empty), ``src/app/existing.py``, ``src/app/staging/`` with
      ``X``, ``F`` and ``-t``, ``src/app/m/sub``, a link to the acceptance folder, and the acceptance test;
    - ``H``: HOME, holding ``tests/acceptance/W2-90/test_a.py`` (a source whose ``../..`` spelling from the
      project mirrors the acceptance test's path).
    """
    own, other = support.open_own_folder(sandbox, MAIN), support.open_own_folder(sandbox, OTHER)
    elsewhere = sandbox.elsewhere
    accept = support.write(project / ACCEPTANCE_TEST, "def test_a():\n    assert True\n")
    support.write(other / "work.txt", "theirs\n")
    for rel, text in (("X", "x\n"), ("s/inner.py", "VALUE = 4\n"), ("W2-91/work.txt", "mine\n"),
                      ("lnk/work.txt", "mine\n"), ("sub/test_a.py", "def test_a():\n    assert False\n")):
        support.write(elsewhere / rel, text)
    (elsewhere / "cwd").mkdir()
    (own / "d").mkdir()
    support.write(own / "d2" / "f.txt", "f\n")
    support.write(own / "staging" / "X", "x\n")
    (own / "lnk").symlink_to(other, target_is_directory=True)
    (project / "src/app/d").mkdir(parents=True)
    support.write(project / "src/app/existing.py", "VALUE = 1\n")
    for name in ("X", "F", "-t"):
        support.write(project / "src/app/staging" / name, f"{name}\n")
    (project / "src/app/m").mkdir()
    (project / "src/app/m/sub").symlink_to(accept.parent, target_is_directory=True)
    support.write(sandbox.home / ACCEPTANCE_TEST, "def test_a():\n    assert False\n")
    return {"E": elsewhere, "O": own, "P": project, "H": sandbox.home, "AT": accept, "PROT": accept.parent,
            "S": project / "src/app/staging", "OTHER": other}


def _ask(sandbox, project, command, cwd=None, role=ENGINEER, ticket=MAIN.tk):
    """The guard's decision on a Bash call made from ``cwd`` (the project when None), as the harness runs it."""
    cwd = Path(cwd or project)
    if cwd == Path(project):
        return support.ask_guard(sandbox, "Bash", support.tool_input("Bash", command), role, ticket, project)
    data = {
        "session_id": "w2-50-acceptance-session",
        "transcript_path": str(sandbox.elsewhere / "transcript.jsonl"),
        "cwd": str(cwd),
        "permission_mode": "default",
        "hook_event_name": "PreToolUse",
        "tool_name": "Bash",
        "tool_input": support.tool_input("Bash", command),
        "tool_use_id": "toolu_w2_50_short_round",
    }
    try:
        proc = subprocess.run([sys.executable, str(Path(project) / support.GUARD_REL)], input=json.dumps(data),
                              capture_output=True, text=True, cwd=str(cwd),
                              env=support.base_environment(sandbox, role, ticket, project),
                              timeout=support.COMMAND_TIMEOUT_S)
        returncode, stdout, stderr = proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired:
        returncode, stdout, stderr = None, "", "timed out"
    decision, reason = support._decision(returncode, stdout, stderr)
    return support.Decision(decision, reason, returncode, stdout, stderr)


def _fill(template, paths):
    """A command from its template: ``{NAME}`` is the quoted path, ``{NAME}/rest`` keeps the rest as written."""
    return template.format(**{name: q(path) for name, path in paths.items()})


def _forms(path):
    path = str(path)
    return {path, os.path.normpath(path), os.path.realpath(path)}


# --------------------------------------------------------------------------
# A. cp --parents is refused as a form the guard cannot read (DEC-764)
# --------------------------------------------------------------------------

# id: (working folder, the folder the copy writes into, command). Working folders: None (the project), or a name.
PARENTS = {
    # Into the own folder.
    "own-folder-dotdot-into-another-tickets-folder": ("E/cwd", "O", "cp --parents ../W2-91/work.txt {O}/"),
    "own-folder-through-a-link-at-a-middle-level": ("E", "O", "cp --parents lnk/work.txt {O}/"),
    "own-folder-harmless-without-a-slash": ("E", "O/d", "cp --parents X {O}/d"),
    "own-folder-harmless-with-a-slash": ("E", "O/d", "cp --parents X {O}/d/"),
    "own-folder-harmless-t": ("E", "O/d", "cp --parents -t {O}/d X"),
    "own-folder-harmless-target-directory": ("E", "O/d", "cp --parents --target-directory={O}/d X"),
    "own-folder-harmless-r": ("E", "O/d", "cp -r --parents s {O}/d/"),
    "own-folder-abbreviated-parent": ("E", "O/d", "cp --parent X {O}/d"),
    # Into a folder of the repository the session may write.
    "repository-dotdot-onto-the-acceptance-test": (None, "P/src/app",
                                                   "cp --parents ../../tests/acceptance/W2-90/test_a.py -t {P}/src/app"),
    "repository-through-a-link-at-a-middle-level": ("E", "P/src/app/m", "cp --parents sub/test_a.py {P}/src/app/m/"),
    "repository-harmless-without-a-slash": ("E", "P/src/app/d", "cp --parents X {P}/src/app/d"),
    "repository-harmless-a": ("E", "P/src/app/d", "cp -a --parents s {P}/src/app/d/"),
    "repository-abbreviated-par": ("E", "P/src/app/d", "cp --par X {P}/src/app/d"),
}


def _resolve(name, paths):
    """``E``, ``E/cwd``, ``O/d``, ``P/src/app``: a path of the layout by its name and a rest."""
    if name is None:
        return None
    head, _, rest = name.partition("/")
    return paths[head] / rest if rest else paths[head]


def _doubt_target(sandbox, project, folder, cwd, paths):
    """Ask the guard for ``ln -t <folder> X`` (refused today as a form it cannot read); the target its reason names."""
    command = f"ln -t {q(folder)} {q(paths['E'] / 'X')}"
    result = _ask(sandbox, project, command, cwd)
    support.assert_refused(result, f"premise: Bash `{command}` (ln -t, the form the guard cannot read)")
    quoted = re.findall(r"'([^']*)'", result.reason)
    return quoted[0] if quoted else None


@pytest.mark.parametrize("case", sorted(PARENTS))
def test_a_copy_with_parents_is_refused_as_a_form_the_guard_cannot_read(places, sandbox, project, case):
    cwd_name, folder_name, template = PARENTS[case]
    cwd, folder = _resolve(cwd_name, places), _resolve(folder_name, places)
    doubt = _doubt_target(sandbox, project, folder, cwd, places)
    command = _fill(template, places)
    what = f"Bash `{command}` from {cwd or project} ({case}; cp --parents writes <folder>/<source as written>)"
    result = _ask(sandbox, project, command, cwd)
    support.assert_refused(result, what)
    if doubt is not None:
        assert doubt in result.reason, (
            f"{what}: refused, but not as the form the guard cannot read: an `ln -t` of the same folder is refused "
            f"naming {doubt!r}, this refusal does not: {result.reason[:400]!r}")


# --------------------------------------------------------------------------
# B. An option's value is a value, and nothing after -- is an option (DEC-765)
# --------------------------------------------------------------------------

def test_the_acceptance_test_named_directly_is_refused(places, sandbox, project):
    """The premise of the B cases: a Write, a redirect and a plain ``cp`` onto the acceptance test are refused."""
    accept = places["AT"]
    support.assert_refused(support.ask_guard(sandbox, "Write", support.tool_input("Write", accept), ENGINEER,
                                             MAIN.tk, project), f"Write on {accept}", *_forms(accept))
    for command in (f"echo x > {q(accept)}", f"cp {q(places['S'] / 'X')} {q(accept)}"):
        support.assert_refused(_ask(sandbox, project, command), f"Bash `{command}`", *_forms(accept))


# id: (working folder, command, the files it writes). Each written file is named as the tool writes it (run in a
# temporary folder): the destination, the backup ``<destination><suffix>``, or ``<folder>/<name>``.
VALUES = {
    "cp-S-joined": (None, "cp -S.t {S}/X {AT}", ("AT", "AT.t")),
    "cp-bS-joined": (None, "cp -bS.t {S}/X {AT}", ("AT", "AT.t")),
    "cp-S-separate": (None, "cp -S .t {S}/X {AT}", ("AT", "AT.t")),
    "cp-suffix-equals": (None, "cp --suffix=.t {S}/X {AT}", ("AT", "AT.t")),
    "cp-suffix-separate": (None, "cp --suffix .t {S}/X {AT}", ("AT", "AT.t")),
    "cp-S-separate-value-dash-t": (None, "cp -S -t {S}/F {AT}", ("AT", "AT-t")),
    "cp-suffix-separate-value-dash-t": (None, "cp --suffix -t {S}/F {AT}", ("AT", "AT-t")),
    "install-S-joined": (None, "install -S.t {S}/X {AT}", ("AT", "AT.t")),
    "install-o-joined": (None, "install -oroot {S}/X {AT}", ("AT",)),
    "install-o-separate": (None, "install -o root {S}/X {AT}", ("AT",)),
    "install-m-joined": (None, "install -m+t {S}/X {AT}", ("AT",)),
    "install-mode-equals": (None, "install --mode=+t {S}/X {AT}", ("AT",)),
    "install-g-joined": (None, "install -gstaff {S}/X {AT}", ("AT",)),
    "mv-S-joined": (None, "mv -S.t {S}/X {AT}", ("AT", "AT.t")),
    "cp-dashdash-a-file-named-dash-t": ("S", "cp -- -t {AT}", ("AT",)),
    "cp-t-then-dashdash": (None, "cp -t {PROT} -- {S}/X", ("PROT/X", "PROT")),
    "cp-dashdash-then-the-folder": (None, "cp -- {S}/X {PROT}/", ("PROT/X", "PROT")),
    "cp-dashdash-after-an-operand": (None, "cp {S}/X -- {AT}", ("AT",)),
    "mv-dashdash-a-file-named-dash-t": ("S", "mv -- -t {AT}", ("AT",)),
    "cp-Z-then-t-fail-closed": (None, "cp -Zt {PROT} {S}/X", ("PROT/X", "PROT")),
}


def _written(names, paths):
    found = set()
    for name in names:
        head = re.match(r"[A-Z]+", name).group(0)
        found |= _forms(str(paths[head]) + name[len(head):])
    return sorted(found)


@pytest.mark.parametrize("case", sorted(VALUES))
def test_an_option_value_or_a_double_dash_is_judged_as_the_files_the_call_writes(places, sandbox, project, case):
    cwd_name, template, names = VALUES[case]
    cwd = _resolve(cwd_name, places)
    command = _fill(template, places)
    written = _written(names, places)
    support.assert_refused(_ask(sandbox, project, command, cwd),
                           f"Bash `{command}` from {cwd or project} ({case}; it writes {names})", *written)


# --------------------------------------------------------------------------
# Controls: nothing earlier now refuses that should pass
# --------------------------------------------------------------------------

# A value with no t, a --, and the B forms onto an allowed file of the repository and of the own folder.
ONTO_ALLOWED = {
    "cp-S-bak": "cp -S.bak {src} {dst}",
    "install-m-and-o-separate": "install -m 0644 -o root {src} {dst}",
    "cp-dashdash": "cp -- {src} {dst}",
    "cp-S-joined-t": "cp -S.t {src} {dst}",
    "install-o-joined": "install -oroot {src} {dst}",
}
ALLOWED_FILES = {"repository": "P/src/app/existing.py", "own-folder": "O/d2/f.txt"}


@pytest.mark.parametrize("where", sorted(ALLOWED_FILES))
@pytest.mark.parametrize("form", sorted(ONTO_ALLOWED))
def test_an_option_value_or_a_double_dash_onto_an_allowed_file_is_allowed(places, sandbox, project, form, where):
    destination = _resolve(ALLOWED_FILES[where], places)
    command = ONTO_ALLOWED[form].format(src=q(places["S"] / "X"), dst=q(destination))
    support.assert_allowed(_ask(sandbox, project, command), f"Bash `{command}` ({form}, onto an allowed file)")


# The ordinary forms the earlier files do not hold (see the README): a move into a folder of each, a copy into a
# repository folder written without a slash.
ORDINARY = {
    "mv-into-a-folder-of-the-own-folder": "mv {O}/staging/X {O}/d/",
    "mv-into-a-folder-of-the-repository": "mv {S}/X {P}/src/app/d/",
    "cp-into-a-folder-of-the-repository-without-a-slash": "cp {E}/X {P}/src/app/d",
}


@pytest.mark.parametrize("form", sorted(ORDINARY))
def test_an_ordinary_copy_or_move_into_an_allowed_folder_is_allowed(places, sandbox, project, form):
    command = _fill(ORDINARY[form], places)
    support.assert_allowed(_ask(sandbox, project, command), f"Bash `{command}` (a folder holding no link)")


TARGET_FORMS = {"cp-t": "cp -t {d} {src}", "install-m-separate": "install -m 644 {src} {d}/"}
TARGET_FOLDERS = {"own-folder": "O/d", "repository": "P/src/app/d", "acceptance-folder": "PROT"}


@pytest.mark.parametrize("where", sorted(TARGET_FOLDERS))
@pytest.mark.parametrize("form", sorted(TARGET_FORMS))
def test_the_t_and_m_forms_stay_judged_as_before(places, sandbox, project, form, where):
    folder = _resolve(TARGET_FOLDERS[where], places)
    command = TARGET_FORMS[form].format(d=q(folder), src=q(places["E"] / "X"))
    result = _ask(sandbox, project, command)
    if where == "acceptance-folder":
        support.assert_refused(result, f"Bash `{command}` (into the acceptance folder)",
                               *(_forms(folder) | _forms(folder / "X")))
    else:
        support.assert_allowed(result, f"Bash `{command}` (into an allowed folder)")
