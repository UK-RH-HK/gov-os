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
   gives that session nothing, and ``gov launch`` there puts no entry in the
   sandbox write list that holds the project's root.
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

GLOB_CHARACTERS = "*?["


def _refused(result, what, sandbox, *paths):
    names = []
    for path in paths:
        names += support.why_words(path, sandbox)
    support.assert_refused(result, what, *names)


def _ask(box, project, tool_name, target, role=ENGINEER, ticket=MAIN.tk):
    return support.ask_guard(box, tool_name, support.tool_input(tool_name, target), role, ticket, project)


def _all_refused(box, project, target, what, role=ENGINEER, ticket=MAIN.tk, *why):
    """Write, Edit and a judged Bash redirect on ``target``, each refused with the guard's reason."""
    for tool_name in ("Write", "Edit"):
        _refused(_ask(box, project, tool_name, target, role, ticket), f"{tool_name} on {target} {what}", box, target,
                 *why)
    command = f"echo written > {q(target)}"
    _refused(_ask(box, project, "Bash", command, role, ticket), f"Bash `{command}` {what}", box, target, *why)


def _all_allowed(box, project, target, what, role=ENGINEER, ticket=MAIN.tk):
    for tool_name in ("Write", "Edit"):
        support.assert_allowed(_ask(box, project, tool_name, target, role, ticket), f"{tool_name} on {target} {what}")
    command = f"echo written > {q(target)}"
    support.assert_allowed(_ask(box, project, "Bash", command, role, ticket), f"Bash `{command}` {what}")


def _folder_refused(box, project, folder, what, ticket):
    """Write, Edit, a Bash redirect and ``mkdir -p`` in ``folder``, each refused, for the engineer on ``ticket``."""
    _all_refused(box, project, folder / "notes.txt", what, ENGINEER, ticket)
    command = f"mkdir -p {q(folder / 'clone')}"
    _refused(_ask(box, project, "Bash", command, ENGINEER, ticket), f"Bash `{command}` {what}", box, folder)


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


def _real_entries(result, box):
    return [(entry, support.entry_path(entry, box)) for entry in result.allow_write()]


def _assert_temp_folder_kept(result, box):
    folder = result.variable("TMPDIR")
    assert folder and any(support.covers(real, os.path.join(folder, "f.txt")) for _, real in _real_entries(result, box)), (
        f"the sandbox may not write the session's temp folder {folder}: {result.allow_write()}")


def _entries_at_or_under_the_root(result, box):
    """The write list's entries that are the root, lie under it, or hold it."""
    root = os.path.realpath(box.root)
    return [entry for entry, real in _real_entries(result, box)
            if real is not None and (support.covers(real, root) or real.startswith(root + "/"))]


def _patterns(result):
    """The write list's entries that hold a glob character, once a trailing ``/**`` is set aside."""
    found = []
    for entry in result.allow_write():
        text = str(entry)
        text = text[: -len("/**")] if text.endswith("/**") else text
        if any(character in text for character in GLOB_CHARACTERS):
            found.append(entry)
    return found


# --------------------------------------------------------------------------
# 1. A project that lies inside the session's own folder keeps every in-project rule
# --------------------------------------------------------------------------

@dataclasses.dataclass(frozen=True)
class _InsideTheOwnFolder(support.Sandbox):
    """The suite's sandbox, with the fixture project at ``~/gov-os-runs/W2-90/clone`` instead of the worktree."""

    @property
    def project(self):
        return self.root / MAIN.folder / "clone"


def _inside_the_own_folder(box):
    return _InsideTheOwnFolder(**{field.name: getattr(box, field.name) for field in dataclasses.fields(box)})


LOCATIONS = ("a-worktree", "inside-the-own-folder")


@pytest.fixture(params=LOCATIONS)
def located(request, sandbox):
    """``(box, project)``: the fixture project in a worktree (the control) or inside MAIN's own folder."""
    box = sandbox if request.param == "a-worktree" else _inside_the_own_folder(sandbox)
    project = support.make_project(box)
    if request.param == "inside-the-own-folder":
        assert support.covers(os.path.realpath(box.own(MAIN)), project), f"{project} is not in {box.own(MAIN)}"
    return box, project


# The places a project's rules refuse, by the role that is refused, with words its reason may hold.
IN_PROJECT_REFUSALS = {
    "an-acceptance-test-by-the-engineer": (ENGINEER, "tests/acceptance/W2-90/test_new.py", "acceptance"),
    "an-acceptance-test-by-the-orchestrator": (ORCHESTRATOR, "tests/acceptance/W2-90/test_new.py", "acceptance"),
    "the-freeze-flag": (ENGINEER, ".gov-runtime/freeze", "freeze"),
    "a-runtime-record": (ENGINEER, ".gov-runtime/findings.jsonl", ".gov-runtime"),
    "a-ticket-file": (ENGINEER, ".tickets/DAEO-zz90.md", ".tickets"),
    "the-settings-file": (ENGINEER, ".claude/settings.json", "settings"),
    "the-guard-hook": (ENGINEER, support.GUARD_REL, "hook"),
    "a-path-outside-the-tickets-paths": (ENGINEER, "docs/notes.md", "allowed_paths"),
}

# What the same rules leave open, by the role that may write it.
IN_PROJECT_OPEN = {
    "a-path-inside-the-tickets-paths": (ENGINEER, "src/app/main.py"),
    "the-projects-scratch": (ENGINEER, ".gov-runtime/scratch/notes.md"),
    "an-acceptance-test-by-the-test-designer": (TEST_DESIGNER, "tests/acceptance/W2-90/test_new.py"),
}


@pytest.mark.parametrize("place", sorted(IN_PROJECT_REFUSALS))
def test_a_project_inside_the_own_folder_keeps_its_refusals(located, place):
    """Each refusal the project's rules make in a worktree, made the same way when the project is a clone in the own folder."""
    box, project = located
    role, rel, word = IN_PROJECT_REFUSALS[place]
    _all_refused(box, project, project / rel, f"by {role} on {MAIN.tk} ({place}, project at {project})", role,
                 MAIN.tk, word)


@pytest.mark.parametrize("place", sorted(IN_PROJECT_OPEN))
def test_a_project_inside_the_own_folder_keeps_what_its_rules_allow(located, place):
    """The control of the refusals: the same project, the same session, its allowed paths written as anywhere else."""
    box, project = located
    role, rel = IN_PROJECT_OPEN[place]
    _all_allowed(box, project, project / rel, f"by {role} on {MAIN.tk} ({place}, project at {project})", role,
                 MAIN.tk)


def test_the_own_folder_outside_a_project_inside_it_gives_that_session_nothing(sandbox):
    """DEC-108's counterpart: a project in the own folder does not get the own folder's allowance outside itself."""
    box = _inside_the_own_folder(sandbox)
    project = support.make_project(box)
    own = box.own(MAIN)
    support.write(own / "notes.txt", "beside the clone\n")
    for target in (own / "notes.txt", own / "another-clone" / "README.md"):
        _all_refused(box, project, target, f"(beside the project {project}, in the own folder)")
    command = f"mkdir -p {q(own / 'another-clone')}"
    _refused(_ask(box, project, "Bash", command), f"Bash `{command}` (beside the project)", box, own)


def test_a_launch_in_a_project_inside_the_own_folder_does_not_add_the_project(sandbox, cli):
    """``gov launch`` there: no entry of the sandbox write list holds the project's root; the temp folder stays."""
    box = _inside_the_own_folder(sandbox)
    project = support.make_project(box)
    result = _launched(box, cli, ENGINEER, MAIN)
    holding = [entry for entry, real in _real_entries(result, box) if support.covers(real, project)]
    assert holding == [], (
        f"the sandbox of a session in the project {project} may write the project itself through {holding}: "
        f"allowWrite is {result.allow_write()}")
    _assert_temp_folder_kept(result, box)


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


@pytest.mark.parametrize("case", sorted(NOT_PLAIN))
def test_a_name_that_is_not_a_plain_folder_name_gives_no_own_folder(sandbox, case):
    """The guard refuses a write in the folder such a name would give, and in any folder a glob of it would match."""
    name, matched = NOT_PLAIN[case]
    project = _named_project(sandbox, name)
    what = f"by the engineer on {NAMED.tk} (external-ref {name!r}, {case})"
    _folder_refused(sandbox, project, sandbox.root / name, what, NAMED.tk)
    if matched:
        _all_refused(sandbox, project, sandbox.root / matched / "notes.txt", f"{what}, a folder the glob matches",
                     ENGINEER, NAMED.tk)


def test_a_plain_folder_name_with_dot_and_underscore_names_the_folder(sandbox):
    """The control: a ticket written the same way, with a plain name, has its folder.

    Rewritten under DEC-751: the folder is made by ``gov launch`` of the ticket first.
    """
    project = _named_project(sandbox, PLAIN)
    support.open_own_folder(sandbox, NAMED.tk, ENGINEER, PLAIN)
    _all_allowed(sandbox, project, sandbox.root / PLAIN / "notes.txt",
                 f"by the engineer on {NAMED.tk} (external-ref {PLAIN!r})", ENGINEER, NAMED.tk)


LAUNCHED_NOT_PLAIN = ("a-star", "a-double-star", "a-bracket", "a-quote", "a-space", "a-leading-dash", "dot-dot")


@pytest.mark.parametrize("case", LAUNCHED_NOT_PLAIN)
def test_the_launcher_neither_makes_nor_adds_a_folder_for_a_name_that_is_not_plain(sandbox, cli, case):
    """No entry at, under or above the root, no pattern in the write list, no folder made; the temp folder stays."""
    name, _ = NOT_PLAIN[case]
    _named_project(sandbox, name)
    result = _launched(sandbox, cli, ENGINEER, NAMED.tk)
    under = _entries_at_or_under_the_root(result, sandbox)
    assert under == [], (
        f"the sandbox of a session on {NAMED.tk} (external-ref {name!r}) may write at or under the root through "
        f"{under}: allowWrite is {result.allow_write()}")
    patterns = _patterns(result)
    assert patterns == [], f"the sandbox's write list holds a pattern: {patterns}"
    if name not in (".", ".."):
        assert not os.path.lexists(sandbox.root / name), f"the launcher made {sandbox.root / name}"
    _assert_temp_folder_kept(result, sandbox)


def test_the_launcher_adds_the_folder_of_a_plain_name_with_dot_and_underscore(sandbox, cli):
    """The control: the same ticket form with a plain name gets exactly that folder, made before the session starts."""
    _named_project(sandbox, PLAIN)
    support.set_plan(cli, check=(sandbox.root / PLAIN,))
    result = _launched(sandbox, cli, ENGINEER, NAMED.tk)
    own = os.path.realpath(sandbox.root / PLAIN)
    under = [real for _, real in _real_entries(result, sandbox)
             if real is not None and real.startswith(os.path.realpath(sandbox.root) + "/")]
    assert under == [own], f"the sandbox's entries under the root are {under}, not [{own}]: {result.allow_write()}"
    assert result.session()["seen"][str(sandbox.root / PLAIN)] is True, "the session started without its folder"


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


@pytest.mark.parametrize("status", ("in_progress", "open", "closed"))
def test_a_folder_two_tickets_name_is_refused_to_the_session_of_either(sandbox, status):
    """Two tickets with the external-ref W2-90: MAIN's session may not write there, whatever SHARER's status."""
    project = _sharing_project(sandbox, status)
    _folder_refused(sandbox, project, sandbox.own(MAIN), f"by the engineer on {MAIN.tk} ({SHARER.tk} names it too, "
                    f"{status})", MAIN.tk)


def test_the_other_ticket_naming_the_folder_gets_it_neither(sandbox):
    project = _sharing_project(sandbox)
    _folder_refused(sandbox, project, sandbox.own(MAIN), f"by the engineer on {SHARER.tk} (external-ref "
                    f"{MAIN.folder}, as {MAIN.tk}'s)", SHARER.tk)


@pytest.mark.parametrize("ticket", (NO_W2_ID, CROSS), ids=("the-ticket-named-by-its-tk-id", "the-ticket-whose-ref-is-it"))
def test_an_external_ref_equal_to_another_tickets_tk_id_folder_is_refused_to_both(sandbox, ticket):
    """CROSS's external-ref is DAEO-zz98, the name of NO_W2_ID's folder (it has no external-ref): neither gets it."""
    project = _crossing_project(sandbox)
    _folder_refused(sandbox, project, sandbox.root / NO_W2_ID.tk, f"by the engineer on {ticket.tk} "
                    f"({CROSS.tk}'s external-ref is {NO_W2_ID.tk})", ticket.tk)


def test_a_ticket_whose_name_no_other_shares_keeps_its_folder(sandbox):
    """The control, in the same project: OTHER's W2-91 is named by no other ticket, so its folder stays open.

    Rewritten under DEC-751: the folder is made by ``gov launch`` of OTHER first.
    """
    project = _sharing_project(sandbox)
    support.open_own_folder(sandbox, OTHER)
    _all_allowed(sandbox, project, sandbox.own(OTHER) / "notes.txt", f"by the engineer on {OTHER.tk}", ENGINEER,
                 OTHER.tk)


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
    holding = [entry for entry, real in _real_entries(result, sandbox)
               if support.covers(real, sandbox.root / folder / "f.txt")]
    assert holding == [], (
        f"the sandbox of a session on {ticket.tk} may write the shared folder {sandbox.root / folder} through "
        f"{holding} ({case})")
    assert not os.path.lexists(sandbox.root / folder), f"the launcher made the shared folder {sandbox.root / folder}"
    _assert_temp_folder_kept(result, sandbox)


def test_the_launcher_keeps_the_folder_of_a_ticket_whose_name_no_other_shares(sandbox, cli):
    """The control, in the project where W2-90 is shared: OTHER gets exactly its own folder, made."""
    _sharing_project(sandbox, "closed")
    support.set_plan(cli, check=(sandbox.own(OTHER),))
    result = _launched(sandbox, cli, ENGINEER, OTHER)
    own = os.path.realpath(sandbox.own(OTHER))
    under = [real for _, real in _real_entries(result, sandbox)
             if real is not None and real.startswith(os.path.realpath(sandbox.root) + "/")]
    assert under == [own], f"the sandbox's entries under the root are {under}, not [{own}]: {result.allow_write()}"
    assert result.session()["seen"][str(sandbox.own(OTHER))] is True, "the session started without its folder"
