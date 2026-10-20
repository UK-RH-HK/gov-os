"""W2-50, the failure lines: each refused, with the guard's reason.

- another ticket's folder under ``~/gov-os-runs``;
- the root itself (a file directly in it, or removing it);
- a path outside it reached by ``..``, a symbolic link or a hard link;
- a session with no ticket;
- any path outside the repository other than the temp folder and the session's own folder;
- ``~/gov-os-workbench`` and ``~/gov-os-worktrees`` (other than the session's own worktree) stay refused as before.

DEC-728 item 2: the refusals hold for Write, Edit and judged Bash targets
alike, and the rule is the same for each role that may write. Every case runs
the engineer on MAIN (``DAEO-zz90``, folder ``W2-90``) unless it names another
role or ticket; the two first lines also run for every role.

"With the guard's reason": a refusal is a ``deny`` whose reason is not empty
and names the target (as given, normalised or resolved) or why (the root's
name, ``ticket``, ``outside``, the workbench or the worktrees). The wording is
the guard's own.

Many of these refusals already hold today, because the guard refuses every
write outside the repository but the temp folder. They are here so that the
change that opens the own folder opens nothing else; the README lists which
pass before the change.
"""

from __future__ import annotations

import os

import pytest

import w2_50_support as support

q = support.q
MAIN, OTHER = support.MAIN, support.OTHER
ENGINEER = support.ENGINEER


def _refused(result, what, sandbox, *paths):
    names = []
    for path in paths:
        names += support.why_words(path, sandbox)
    support.assert_refused(result, what, *names)


def _file_tools_and_bash(guard, sandbox, target, what, role=ENGINEER, ticket=MAIN.tk):
    for tool_name in ("Write", "Edit"):
        _refused(guard(tool_name, target, role, ticket), f"{tool_name} on {target} {what}", sandbox, target)
    command = f"echo written > {q(target)}"
    _refused(guard("Bash", command, role, ticket), f"Bash `{command}` {what}", sandbox, target)


def _populate(sandbox):
    """The root with MAIN's and OTHER's folders, a file in each, and a file elsewhere.

    Rewritten under DEC-751: both folders are made by ``gov launch`` of the
    fixture project, so they are this repository's and MAIN's is open; each
    refusal below is then the rule's, not that of a folder no launch made.
    """
    own, other = support.open_own_folder(sandbox, MAIN), support.open_own_folder(sandbox, OTHER)
    support.write(own / "mine.txt", "mine\n")
    (own / "dir").mkdir(parents=True, exist_ok=True)
    support.write(other / "theirs.txt", "theirs\n")
    support.write(sandbox.elsewhere / "target.txt", "outside\n")
    return own, other


# --------------------------------------------------------------------------
# 1. Another ticket's folder
# --------------------------------------------------------------------------

def test_another_tickets_folder_is_refused_to_the_file_tools_and_bash(guard, sandbox):
    _populate(sandbox)
    _file_tools_and_bash(guard, sandbox, sandbox.own(OTHER) / "theirs.txt", "(another ticket's folder)")


@pytest.mark.parametrize("form", ("touch", "mkdir-p", "cp-into", "mv-into", "rm-in", "tee"))
def test_judged_bash_forms_into_another_tickets_folder_are_refused(guard, sandbox, project, form):
    own, other = _populate(sandbox)
    command = {
        "touch": f"touch {q(other / 'new.txt')}",
        "mkdir-p": f"mkdir -p {q(other / 'a' / 'b')}",
        "cp-into": f"cp {q(project / 'src/app/main.py')} {q(other / 'main.py')}",
        "mv-into": f"mv {q(own / 'mine.txt')} {q(other / 'mine.txt')}",
        "rm-in": f"rm -rf {q(other / 'theirs.txt')}",
        "tee": f"echo written | tee {q(other / 'tee.txt')}",
    }[form]
    _refused(guard("Bash", command), f"Bash `{command}`", sandbox, other)


@pytest.mark.parametrize("role", support.ROLES)
def test_another_tickets_folder_is_refused_to_every_role(guard, sandbox, role):
    ticket = support.TICKET_OF[role]
    target = sandbox.own(OTHER) / "theirs.txt"
    assert ticket != OTHER
    _refused(guard("Write", target, role, ticket.tk), f"Write on {target} by {role} on {ticket.tk}", sandbox, target)
    command = f"echo written > {q(target)}"
    _refused(guard("Bash", command, role, ticket.tk), f"Bash `{command}` by {role} on {ticket.tk}", sandbox, target)


# Folders that are not MAIN's, though their names are near W2-90 or name MAIN another way.
NOT_OWN = {
    "a-ticket-that-does-not-exist": "W2-77",
    "a-case-change-of-the-own-name": "w2-90",
    "a-longer-id-that-starts-with-the-own": "W2-900",
    "the-own-id-with-a-suffix": "W2-90a",
    "the-own-id-with-an-extension": "W2-90.old",
    "the-tk-id-of-a-ticket-that-has-a-w2-id": MAIN.tk,
}


@pytest.mark.parametrize("name", sorted(NOT_OWN))
def test_a_folder_whose_name_is_near_the_own_is_another_folder(guard, sandbox, name):
    target = sandbox.root / NOT_OWN[name] / "notes.txt"
    _refused(guard("Write", target), f"Write on {target} ({name})", sandbox, target)
    command = f"echo written > {q(target)}"
    _refused(guard("Bash", command), f"Bash `{command}` ({name})", sandbox, target)


# --------------------------------------------------------------------------
# 2. The root itself
# --------------------------------------------------------------------------

def test_a_file_directly_in_the_root_is_refused(guard, sandbox):
    _populate(sandbox)
    _file_tools_and_bash(guard, sandbox, sandbox.root / "loose.txt", "(a file directly in the root)")
    command = f"touch {q(sandbox.root / 'loose.txt')}"
    _refused(guard("Bash", command), f"Bash `{command}`", sandbox, sandbox.root)


@pytest.mark.parametrize("role", support.ROLES)
def test_a_file_directly_in_the_root_is_refused_to_every_role(guard, sandbox, role):
    ticket = support.TICKET_OF[role]
    target = sandbox.root / "loose.txt"
    _refused(guard("Write", target, role, ticket.tk), f"Write on {target} by {role}", sandbox, target)


@pytest.mark.parametrize("spelling", ("dot", "trailing-slash-dot"))
def test_a_file_in_the_root_spelled_through_dot_is_refused(guard, sandbox, spelling):
    """The root reached through ``.``: ``~/gov-os-runs/./loose.txt`` and ``~/gov-os-runs/W2-90/./../loose.txt``."""
    target = {"dot": f"{sandbox.root}/./loose.txt",
              "trailing-slash-dot": f"{sandbox.root}/{MAIN.folder}/./../loose.txt"}[spelling]
    _refused(guard("Write", target), f"Write on {target}", sandbox, target)
    command = f"echo written > {q(target)}"
    _refused(guard("Bash", command), f"Bash `{command}`", sandbox, target)


def test_the_root_path_itself_as_a_file_is_refused(guard, sandbox):
    """No root yet: a Write on ``~/gov-os-runs`` itself would make the root a file."""
    target = sandbox.root
    _refused(guard("Write", target), f"Write on {target}", sandbox, target)
    command = f"echo written > {q(target)}"
    _refused(guard("Bash", command), f"Bash `{command}`", sandbox, target)


ROOT_REMOVALS = {
    "rm-rf": "rm -rf {root}",
    "rm-rf-trailing-slash": "rm -rf {root}/",
    "rm-rf-dot": "rm -rf {root}/.",
    "rm-r-from-the-own-folder": "rm -r {root}/W2-90/..",
    "rmdir": "rmdir {root}",
    "mv-away": "mv {root} {elsewhere}/moved-root",
}


@pytest.mark.parametrize("name", sorted(ROOT_REMOVALS))
def test_removing_or_moving_the_root_is_refused(guard, sandbox, name):
    _populate(sandbox)
    command = ROOT_REMOVALS[name].format(root=q(sandbox.root), elsewhere=q(sandbox.elsewhere))
    _refused(guard("Bash", command), f"Bash `{command}`", sandbox, sandbox.root)


# --------------------------------------------------------------------------
# 3. Out of the own folder by .., a symbolic link or a hard link
# --------------------------------------------------------------------------

def _dotdot(sandbox):
    own = f"{sandbox.own(MAIN)}"
    return {
        "into-another-tickets-folder": f"{own}/../{OTHER.folder}/theirs.txt",
        "into-the-root": f"{own}/../loose.txt",
        "into-home": f"{own}/../../loose.txt",
        "out-to-elsewhere": f"{own}/../../../elsewhere/target.txt",
        "twice-down-and-out": f"{own}/a/b/../../../{OTHER.folder}/theirs.txt",
    }


@pytest.mark.parametrize("name", ("into-another-tickets-folder", "into-the-root", "into-home", "out-to-elsewhere",
                                  "twice-down-and-out"))
def test_a_path_that_leaves_the_own_folder_by_dotdot_is_refused(guard, sandbox, name):
    _populate(sandbox)
    target = _dotdot(sandbox)[name]
    _file_tools_and_bash(guard, sandbox, target, f"({name})")


def test_a_symbolic_link_in_the_own_folder_to_another_tickets_folder_is_refused(guard, sandbox):
    own, other = _populate(sandbox)
    (own / "to-other").symlink_to(other, target_is_directory=True)
    _file_tools_and_bash(guard, sandbox, own / "to-other" / "theirs.txt", "(through a link to W2-91)")
    _refused(guard("Bash", f"mkdir -p {q(own / 'to-other' / 'new')}"), "mkdir through a link to W2-91", sandbox,
             own / "to-other", other)


def test_a_symbolic_link_in_the_own_folder_to_the_root_is_refused(guard, sandbox):
    own, _ = _populate(sandbox)
    (own / "to-root").symlink_to(sandbox.root, target_is_directory=True)
    _file_tools_and_bash(guard, sandbox, own / "to-root" / "loose.txt", "(through a link to the root)")


def test_a_symbolic_link_in_the_own_folder_to_a_folder_elsewhere_is_refused(guard, sandbox):
    own, _ = _populate(sandbox)
    (own / "to-elsewhere").symlink_to(sandbox.elsewhere, target_is_directory=True)
    _file_tools_and_bash(guard, sandbox, own / "to-elsewhere" / "target.txt", "(through a link to elsewhere)")


def test_a_symbolic_link_in_the_own_folder_to_a_file_elsewhere_is_refused(guard, sandbox):
    own, _ = _populate(sandbox)
    (own / "file-link.txt").symlink_to(sandbox.elsewhere / "target.txt")
    _file_tools_and_bash(guard, sandbox, own / "file-link.txt", "(a link to a file elsewhere)")


def test_an_own_folder_that_is_itself_a_link_elsewhere_is_refused(guard, sandbox):
    """``~/gov-os-runs/W2-90`` is a link to a folder outside the root: what is written lands outside."""
    sandbox.root.mkdir(parents=True)
    (sandbox.elsewhere / "fake-own").mkdir()
    sandbox.own(MAIN).symlink_to(sandbox.elsewhere / "fake-own", target_is_directory=True)
    _file_tools_and_bash(guard, sandbox, sandbox.own(MAIN) / "notes.txt", "(the own folder is a link elsewhere)")


def test_a_link_in_the_repository_to_another_tickets_folder_is_refused(guard, sandbox, project):
    """A link inside the engineer's own paths of the worktree, pointing into W2-91's folder."""
    _, other = _populate(sandbox)
    link = project / "src/app/runs-link"
    link.symlink_to(other, target_is_directory=True)
    _file_tools_and_bash(guard, sandbox, link / "theirs.txt", "(a repository link into W2-91's folder)")


def test_a_hard_link_in_the_own_folder_to_a_file_elsewhere_is_refused(guard, sandbox):
    own, _ = _populate(sandbox)
    os.link(sandbox.elsewhere / "target.txt", own / "hard.txt")
    _file_tools_and_bash(guard, sandbox, own / "hard.txt", "(a hard link to a file elsewhere)")


def test_a_hard_link_in_the_own_folder_to_a_file_of_another_ticket_is_refused(guard, sandbox):
    own, other = _populate(sandbox)
    os.link(other / "theirs.txt", own / "hard-theirs.txt")
    _file_tools_and_bash(guard, sandbox, own / "hard-theirs.txt", "(a hard link to W2-91's file)")


@pytest.mark.parametrize("spelling", ("ln", "cp -l", "link"))
@pytest.mark.parametrize("source", ("elsewhere", "another-ticket"))
def test_making_a_hard_link_in_the_own_folder_to_a_file_outside_it_is_refused(guard, sandbox, spelling, source):
    _, other = _populate(sandbox)
    origin = {"elsewhere": sandbox.elsewhere / "target.txt", "another-ticket": other / "theirs.txt"}[source]
    command = f"{spelling} {q(origin)} {q(sandbox.own(MAIN) / 'new-hard.txt')}"
    _refused(guard("Bash", command), f"Bash `{command}`", sandbox, origin, sandbox.own(MAIN) / "new-hard.txt")


MOVES = {
    "mv-own-file-to-another-ticket": "mv {own}/mine.txt {other}/mine.txt",
    "mv-another-tickets-file-in": "mv {other}/theirs.txt {own}/theirs.txt",
    "mv-own-file-elsewhere": "mv {own}/mine.txt {elsewhere}/mine.txt",
    "mv-file-in-from-elsewhere": "mv {elsewhere}/target.txt {own}/target.txt",
    "cp-own-file-to-another-ticket": "cp {own}/mine.txt {other}/",
    "cp-r-own-folder-elsewhere": "cp -r {own}/dir {elsewhere}/dir-copy",
    "mv-the-own-folder-onto-another": "mv {own} {other}/nested",
}


@pytest.mark.parametrize("name", sorted(MOVES))
def test_a_move_or_copy_across_the_own_folders_edge_is_refused(guard, sandbox, name):
    own, other = _populate(sandbox)
    command = MOVES[name].format(own=q(own), other=q(other), elsewhere=q(sandbox.elsewhere))
    _refused(guard("Bash", command), f"Bash `{command}`", sandbox, own, other, sandbox.elsewhere)


# --------------------------------------------------------------------------
# 4. A session with no ticket
# --------------------------------------------------------------------------

@pytest.mark.parametrize("role", support.ROLES)
def test_a_session_with_no_ticket_may_not_write_under_the_root(guard, sandbox, role):
    for folder in (MAIN.folder, "no-ticket", ""):
        target = sandbox.root / folder / "notes.txt" if folder else sandbox.root / "notes.txt"
        _refused(guard("Write", target, role, None), f"Write on {target} by {role} with no GOV_TICKET",
                 sandbox, target)
        command = f"echo written > {q(target)}"
        _refused(guard("Bash", command, role, None), f"Bash `{command}` by {role} with no GOV_TICKET",
                 sandbox, target)


def test_an_empty_gov_ticket_is_no_ticket(guard, sandbox):
    target = sandbox.own(MAIN) / "notes.txt"
    _file_tools_and_bash(guard, sandbox, target, "with GOV_TICKET empty", ticket="")


@pytest.mark.parametrize("folder", (support.UNKNOWN_TICKET, MAIN.folder))
def test_a_gov_ticket_that_names_no_ticket_is_no_ticket(guard, sandbox, folder):
    """A forged or unknown id: no ticket file has it, so no folder is the session's."""
    target = sandbox.root / folder / "notes.txt"
    _file_tools_and_bash(guard, sandbox, target, f"with GOV_TICKET={support.UNKNOWN_TICKET}",
                         ticket=support.UNKNOWN_TICKET)


def test_a_session_with_no_role_may_not_write_in_the_folder(guard, sandbox):
    target = sandbox.own(MAIN) / "notes.txt"
    _file_tools_and_bash(guard, sandbox, target, "with no GOV_ROLE", role=None)


# --------------------------------------------------------------------------
# 5. Any other path outside the repository
# --------------------------------------------------------------------------

OUTSIDE = {
    "elsewhere": lambda box: box.elsewhere / "outside.txt",
    "home": lambda box: box.home / "loose.txt",
    "a-dotfile-in-home": lambda box: box.home / ".bashrc",
    "a-sibling-of-the-root-with-a-longer-name": lambda box: box.home / f"{support.RUNS}2" / MAIN.folder / "n.txt",
    "a-sibling-of-the-root-with-an-extension": lambda box: box.home / f"{support.RUNS}.old" / MAIN.folder / "n.txt",
    "a-folder-of-the-roots-name-outside-home": lambda box: box.elsewhere / support.RUNS / MAIN.folder / "n.txt",
}


@pytest.mark.parametrize("name", sorted(OUTSIDE))
def test_a_path_outside_the_repository_the_temp_folder_and_the_own_folder_is_refused(guard, sandbox, name):
    target = OUTSIDE[name](sandbox)
    _file_tools_and_bash(guard, sandbox, target, f"({name})")


def test_the_temp_folder_stays_open(guard, sandbox):
    """The control of the line above: the temp folder is the other place outside the repository (DEC-159)."""
    target = sandbox.tmpdir / "scratch.txt"
    support.assert_allowed(guard("Write", target), f"Write on {target}")
    command = f"echo written > {q(target)}"
    support.assert_allowed(guard("Bash", command), f"Bash `{command}`")


# --------------------------------------------------------------------------
# 6. The workbench and the worktrees stay refused
# --------------------------------------------------------------------------

def test_the_workbench_stays_refused(guard, sandbox):
    """DEC-723: no agent writes in ``~/gov-os-workbench``. The folder here is the temporary HOME's, made by the test."""
    target = sandbox.home / support.WORKBENCH / "examin" / "README.md"
    support.write(target, "owner's copy\n")
    _file_tools_and_bash(guard, sandbox, target, "(the workbench)")
    command = f"mkdir -p {q(sandbox.home / support.WORKBENCH / 'new')}"
    _refused(guard("Bash", command), f"Bash `{command}`", sandbox, sandbox.home / support.WORKBENCH)
    # Not asked: ``git clone <src> ~/gov-os-workbench/...``. The guard has never judged a clone's destination
    # (README, discoveries), so "as before" does not hold it; the sandbox's write list is what stops it.


def test_another_worktree_stays_refused(guard, sandbox):
    target = sandbox.home / support.WORKTREES / OTHER.folder / "src" / "other" / "main.py"
    support.write(target, "VALUE = 1\n")
    _file_tools_and_bash(guard, sandbox, target, "(another ticket's worktree)")


def test_the_worktrees_folder_itself_stays_refused(guard, sandbox):
    _file_tools_and_bash(guard, sandbox, sandbox.home / support.WORKTREES / "loose.txt", "(the worktrees folder)")


def test_the_sessions_own_worktree_stays_open_within_its_paths(guard, sandbox, project):
    """The control: the session's own worktree is the repository, and its ticket's paths are written as before."""
    target = project / "src/app/main.py"
    support.assert_allowed(guard("Write", target), f"Write on {target}")
    command = f"echo written > {q(target)}"
    support.assert_allowed(guard("Bash", command), f"Bash `{command}`")
