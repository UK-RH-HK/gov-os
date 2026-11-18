"""W2-50, the review's findings, as described behaviour (DEC-136): tests added after implementation.

The review of the implemented ticket found three behaviours the suite did not
hold. Each is tested here through the interfaces the suite already drives: the
guard's PreToolUse hook with the call on stdin, and ``gov launch`` with the
stand-in CLI.

1. **A project that lies inside the session's own folder keeps every
   in-project rule.** A clone at ``~/gov-os-runs/W2-90/clone`` holding its own
   ``.tickets/`` with the session's ticket is a project like any other: its
   acceptance tests, its ``.gov-runtime/`` outside ``scratch/``, its
   ``.tickets/``, its ``.claude/settings.json``, its guard hook and every path
   outside the ticket's ``allowed_paths`` stay refused, and its allowed paths
   stay open. As a project in the temp folder does not get the temp folder's
   allowance (DEC-108's counterpart), the own folder outside such a project
   gives that session nothing. (Emergency 2, release 0.1.2: ``gov launch``
   writes no sandbox write list, so its case for such a project is retired.)
2. **Only a plain folder name names a folder.** The ticket's name (its
   ``external-ref``, or its tk id when it has none) names the own folder only
   when it starts with a letter or digit and holds only letters, digits,
   ``.``, ``_`` and ``-``. Any other name gives no own folder.
3. **One folder belongs to one ticket.** A name two or more tickets of the
   project share, whatever the other ticket's status, gives no session of
   those tickets that folder.

Every location is the suite's: a temporary HOME, a temp folder disjoint from
it, the fixture project built from scratch. Case 1 builds the same fixture
project at ``~/gov-os-runs/W2-90/clone`` of the temporary HOME, and runs each
in-project rule in both places: the worktree's run is the control that the
rule holds in another project. Tickets are written in the form the suite's
tickets have (``external-ref: <name>``, the value as written).
"""

from __future__ import annotations

import dataclasses
import os

import pytest

import w2_50_support as support

q = support.q
MAIN, OTHER, NO_W2_ID = support.MAIN, support.OTHER, support.NO_W2_ID
ENGINEER, TEST_DESIGNER, ORCHESTRATOR = support.ENGINEER, support.TEST_DESIGNER, support.ORCHESTRATOR


def _ticket_named(tk, name, status="in_progress"):
    """The suite's ticket text for an engineer ticket ``tk`` whose ``external-ref`` is ``name``, as written."""
    text = support.ticket_text(support.Ticket(tk, ENGINEER, None, ("src/app/**",)))
    assert f"assignee: {ENGINEER}\n" in text and "status: in_progress\n" in text
    text = text.replace(f"assignee: {ENGINEER}\n", f"assignee: {ENGINEER}\nexternal-ref: {name}\n", 1)
    return text.replace("status: in_progress\n", f"status: {status}\n", 1)


def _launched(box, cli, role, ticket):
    result = support.launch(box, cli, role, ticket)
    result.session()
    return result


def _assert_temp_folder_kept(result, box):
    """The session still gets a temp folder of its own (its TMPDIR), not the launcher's. Emergency 2 (release 0.1.2):
    there is no sandbox write list to hold it on."""
    folder = result.variable("TMPDIR")
    assert folder and os.path.realpath(folder) != os.path.realpath(box.tmpdir), (
        f"the session got no temp folder of its own: TMPDIR is {folder!r}")


def _folders_under_the_root(box):
    """The folders the launches made under the root (the run folders), by name."""
    root = box.root
    return sorted(name for name in os.listdir(root) if (root / name).is_dir()) if root.is_dir() else []


# --------------------------------------------------------------------------
# 1. A project that lies inside the session's own folder keeps every in-project rule
# --------------------------------------------------------------------------


LOCATIONS = ("a-worktree", "inside-the-own-folder")


# --------------------------------------------------------------------------
# 2. Only a plain folder name names a folder
# --------------------------------------------------------------------------

NAMED = support.Ticket("DAEO-zz80", ENGINEER, None, ("src/app/**",))   # its external-ref is the case's name

# Names that are not one plain folder name, with a folder a glob of that name would match (or None).
NOT_PLAIN = {
    "a-star": ("*", "W2-93"),
    "a-double-star": ("**", "W2-93/deep"),
    "a-question-mark": ("W2-9?", "W2-93"),
    "a-bracket": ("W2-[9]3", "W2-93"),
    "a-quote": ("W2'90", None),
    "a-space": ("W2 90", None),
    "a-hash": ("W2-90#a", None),
    "a-tilde": ("~W2-90", None),
    "a-leading-dash": ("-W2-90", None),
    "a-leading-dot": (".hidden", None),
    "dot-dot": ("..", None),
}
PLAIN = "W2-90_b.1"      # letters, digits, '.', '_' and '-', starting with a letter


def _named_project(box, name):
    return support.make_project(box, extra={f".tickets/{NAMED.tk}.md": _ticket_named(NAMED.tk, name)})


LAUNCHED_NOT_PLAIN = ("a-star", "a-double-star", "a-bracket", "a-quote", "a-space", "a-leading-dash", "dot-dot")


@pytest.mark.parametrize("case", LAUNCHED_NOT_PLAIN)
def test_the_launcher_neither_makes_nor_adds_a_folder_for_a_name_that_is_not_plain(sandbox, cli, case):
    """No folder made; the temp folder stays. (Emergency 2, release 0.1.2: no sandbox write list to read.)"""
    name, _ = NOT_PLAIN[case]
    _named_project(sandbox, name)
    result = _launched(sandbox, cli, ENGINEER, NAMED.tk)
    if name not in (".", ".."):
        assert not os.path.lexists(sandbox.root / name), f"the launcher made {sandbox.root / name}"
    _assert_temp_folder_kept(result, sandbox)


def test_the_launcher_adds_the_folder_of_a_plain_name_with_dot_and_underscore(sandbox, cli):
    """The control: the same ticket form with a plain name gets exactly that folder, made before the session starts."""
    _named_project(sandbox, PLAIN)
    support.set_plan(cli, check=(sandbox.root / PLAIN,))
    result = _launched(sandbox, cli, ENGINEER, NAMED.tk)
    assert result.session()["seen"][str(sandbox.root / PLAIN)] is True, "the session started without its folder"
    made = _folders_under_the_root(sandbox)
    assert made == [PLAIN], f"the folders made under the root are {made}, not [{PLAIN!r}]"


# --------------------------------------------------------------------------
# 3. One folder belongs to one ticket
# --------------------------------------------------------------------------

SHARER = support.Ticket("DAEO-zz81", ENGINEER, None, ("src/app/**",))   # external-ref W2-90, MAIN's name
CROSS = support.Ticket("DAEO-zz82", ENGINEER, None, ("src/app/**",))    # external-ref DAEO-zz98, NO_W2_ID's name


def _sharing_project(box, status="in_progress"):
    """The fixture project with SHARER, whose external-ref is MAIN's W2 id, in ``status``."""
    return support.make_project(box, extra={f".tickets/{SHARER.tk}.md": _ticket_named(SHARER.tk, MAIN.folder,
                                                                                         status)})


def _crossing_project(box):
    """The fixture project with CROSS, whose external-ref is the tk id NO_W2_ID's folder is named by."""
    return support.make_project(box, extra={f".tickets/{CROSS.tk}.md": _ticket_named(CROSS.tk, NO_W2_ID.tk)})


SHARED_LAUNCHES = {
    "the-same-external-ref-of-a-closed-ticket": (MAIN, MAIN.folder),
    "an-external-ref-equal-to-the-tk-id": (NO_W2_ID, NO_W2_ID.tk),
}


@pytest.mark.parametrize("case", sorted(SHARED_LAUNCHES))
def test_the_launcher_neither_makes_nor_adds_a_folder_two_tickets_name(sandbox, cli, case):
    ticket, folder = SHARED_LAUNCHES[case]
    if ticket is MAIN:
        _sharing_project(sandbox, "closed")
    else:
        _crossing_project(sandbox)
    result = _launched(sandbox, cli, ENGINEER, ticket)
    assert not os.path.lexists(sandbox.root / folder), f"the launcher made the shared folder {sandbox.root / folder}"
    _assert_temp_folder_kept(result, sandbox)


def test_the_launcher_keeps_the_folder_of_a_ticket_whose_name_no_other_shares(sandbox, cli):
    """The control, in the project where W2-90 is shared: OTHER gets exactly its own folder, made."""
    _sharing_project(sandbox, "closed")
    support.set_plan(cli, check=(sandbox.own(OTHER),))
    result = _launched(sandbox, cli, ENGINEER, OTHER)
    assert result.session()["seen"][str(sandbox.own(OTHER))] is True, "the session started without its folder"
    made = _folders_under_the_root(sandbox)
    assert made == [sandbox.own(OTHER).name], f"the folders made under the root are {made}, not [{sandbox.own(OTHER).name!r}]"
