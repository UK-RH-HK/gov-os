"""W2-50, success 1 and 2 (the guard's half): a session writes under ``~/gov-os-runs/<its own ticket>/``.

"One durable root. ~/gov-os-runs/ is the one durable scratch root outside the
repository, known to the guard [...]" and "Its own folder only. A session of
any role writes only under ~/gov-os-runs/<its own ticket>/. That folder is
named by the ticket's W2 id (its external-ref, as for worktrees), or by its tk
id when it has none, and resolved from the session's GOV_TICKET: The guard
allows Write, Edit and judged Bash targets there; [...] The folder is created
on first use." [DEC-728 items 1 and 2]

The root is the temporary HOME's ``gov-os-runs``; HOME is not inside the temp
folder the guard sees, so no case is allowed because of the temp folder rule.
The refusals of the same KPI ("writes *only* under") are in
``test_w2_50_guard_refusals.py``.

Rewritten under DEC-751 (DEC-491): a folder belongs to the one repository
whose launch made it, so each case that expects a write allowed first makes
the folder by ``gov launch`` of the fixture project
(``support.open_own_folder``), never by hand.
"""

from __future__ import annotations

import pytest

import w2_50_support as support

q = support.q
MAIN = support.MAIN


def _bash_forms(sandbox, project):
    """Judged Bash writes whose every target lies in MAIN's own folder."""
    own = sandbox.own(MAIN)
    source = project / "src/app/main.py"
    return {
        "redirect": f"echo written > {q(own / 'out.txt')}",
        "append": f"echo more >> {q(own / 'log.txt')}",
        "tee": f"echo written | tee {q(own / 'tee.txt')}",
        "touch": f"touch {q(own / 'touched.txt')}",
        "mkdir-p": f"mkdir -p {q(own / 'a' / 'b' / 'c')}",
        "cp-into": f"cp {q(source)} {q(own / 'copy.py')}",
        "mv-within": f"mv {q(own / 'first.txt')} {q(own / 'second.txt')}",
        "rm-within": f"rm -rf {q(own / 'old')}",
    }


BASH_FORMS = ("redirect", "append", "tee", "touch", "mkdir-p", "cp-into", "mv-within", "rm-within")


def _prepare_own(sandbox):
    own = support.open_own_folder(sandbox, MAIN)     # DEC-751: made by a launch, not by hand
    (own / "old").mkdir(parents=True, exist_ok=True)
    support.write(own / "first.txt", "first\n")
    support.write(own / "existing.txt", "a\n")
    return own


# --------------------------------------------------------------------------
# Write, Edit and judged Bash targets in the own folder
# --------------------------------------------------------------------------

@pytest.mark.parametrize("role", support.ROLES)
@pytest.mark.parametrize("tool_name", ("Write", "Edit"))
def test_every_role_may_write_a_file_in_its_own_tickets_folder(guard, sandbox, role, tool_name):
    """"A session of any role": each role, on the ticket its session runs under, with the file tools."""
    ticket = support.TICKET_OF[role]
    own = support.open_own_folder(sandbox, ticket)     # DEC-751: made by a launch of the ticket
    target = own / "notes" / "existing.txt"
    support.write(target, "a\n")
    support.assert_allowed(guard(tool_name, target, role, ticket.tk),
                           f"{tool_name} on {target} by {role} on {ticket.tk} ({ticket.folder})")


@pytest.mark.parametrize("role", support.ROLES)
def test_every_role_may_write_through_bash_in_its_own_tickets_folder(guard, sandbox, role):
    ticket = support.TICKET_OF[role]
    target = support.open_own_folder(sandbox, ticket) / "bash.txt"     # DEC-751
    command = f"echo written > {q(target)}"
    support.assert_allowed(guard("Bash", command, role, ticket.tk), f"Bash `{command}` by {role} on {ticket.tk}")


@pytest.mark.parametrize("form", BASH_FORMS)
def test_judged_bash_forms_into_the_own_folder_are_allowed(guard, sandbox, project, form):
    _prepare_own(sandbox)
    command = _bash_forms(sandbox, project)[form]
    support.assert_allowed(guard("Bash", command), f"Bash `{command}` by the engineer on {MAIN.tk}")


def test_a_clone_into_the_own_folder_is_allowed(guard, sandbox, project):
    """The use the root is for: a working clone from an exact path (DEC-723 item 3)."""
    command = f"git clone --no-hardlinks {q(project)} {q(sandbox.own(MAIN) / 'clone')}"
    support.assert_allowed(guard("Bash", command), f"Bash `{command}`")


def test_a_write_deep_inside_a_clone_in_the_own_folder_is_allowed(guard, sandbox):
    own = support.open_own_folder(sandbox, MAIN)     # DEC-751
    target = own / "clone" / "src" / "pkg" / "module.py"
    support.write(target, "VALUE = 1\n")
    for tool_name in ("Write", "Edit"):
        support.assert_allowed(guard(tool_name, target), f"{tool_name} on {target}")
    command = f"echo more >> {q(target)}"
    support.assert_allowed(guard("Bash", command), f"Bash `{command}`")


# --------------------------------------------------------------------------
# The folder's name: W2 id, tk id when there is none, exact spelling
# --------------------------------------------------------------------------

def test_a_ticket_without_a_w2_id_writes_in_the_folder_named_by_its_tk_id(guard, sandbox):
    target = support.open_own_folder(sandbox, support.NO_W2_ID) / "notes.txt"     # DEC-751
    assert target.parent == sandbox.root / support.NO_W2_ID.tk
    support.assert_allowed(guard("Write", target, support.ENGINEER, support.NO_W2_ID.tk),
                           f"Write on {target} by the engineer on {support.NO_W2_ID.tk}, which has no external-ref")
    command = f"echo written > {q(target)}"
    support.assert_allowed(guard("Bash", command, support.ENGINEER, support.NO_W2_ID.tk), f"Bash `{command}`")


def test_a_w2_id_with_a_letter_suffix_names_the_folder_as_written(guard, sandbox):
    """``external-ref: W2-99a`` -> ``~/gov-os-runs/W2-99a/`` (as for worktrees, e.g. W2-15a)."""
    target = support.open_own_folder(sandbox, support.SUFFIXED) / "notes.txt"     # DEC-751
    assert target.parent == sandbox.root / support.SUFFIXED.wbs
    support.assert_allowed(guard("Write", target, support.ENGINEER, support.SUFFIXED.tk),
                           f"Write on {target} by the engineer on {support.SUFFIXED.tk} ({support.SUFFIXED.wbs})")


def test_the_folder_follows_gov_ticket_not_the_worktree(guard, sandbox):
    """Resolved from the session's GOV_TICKET: in the W2-90 worktree, a session on W2-91 has W2-91's folder."""
    target = support.open_own_folder(sandbox, support.OTHER) / "notes.txt"     # DEC-751: launched in this worktree
    support.assert_allowed(guard("Write", target, support.ENGINEER, support.OTHER.tk),
                           f"Write on {target} by the engineer on {support.OTHER.tk}")


# --------------------------------------------------------------------------
# Created on first use
# --------------------------------------------------------------------------

def test_the_first_write_is_allowed_when_neither_the_root_nor_the_folder_exists(guard, sandbox):
    """"The folder is created on first use": by the first launch, then the session's first write there is allowed.

    Rewritten under DEC-751: neither the root nor the folder exists before the
    first launch; the launch makes them (R2's step, DEC-743 1), and the first
    write in the made folder is allowed. A folder that does not exist yet gives
    no session anything (``test_w2_50_last_review.py``).
    """
    assert not sandbox.root.exists(), "the fixture's HOME already holds the root"
    support.open_own_folder(sandbox, MAIN)
    target = sandbox.own(MAIN) / "first.txt"
    support.assert_allowed(guard("Write", target), f"Write on {target}, the first use")
    command = f"mkdir -p {q(sandbox.own(MAIN) / 'clone')}"
    support.assert_allowed(guard("Bash", command), f"Bash `{command}`, the first use")
