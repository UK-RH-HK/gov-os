"""W2-50, the owner's answers to the change proposal (DEC-743, 2026-10-17), as described behaviour (DEC-136).

The owner approved the CIT-P (``docs/changes/W2-50-CIT-P.md``) with answers
that fix behaviour the first suite left open. Each case here holds one answer
the first suite did not hold yet; what it already held is named in the README.

1. **R7 is scoped to the root.** ``rmdir`` of ``~/gov-os-runs`` is refused in
   each spelling the suite uses for the root; ``rmdir`` elsewhere stays as
   today's guard decides it.
2. **R2's step.** The launcher makes the root and the session's own folder
   before the session starts, leaves what is there alone, and makes no other
   folder under the root.
3. **The link rule (§6.1 (i)).** The secrets-indexing check does not follow a
   link from ``.gov-runtime/`` into ``~/gov-os-runs``; it still follows a linked
   folder elsewhere (W1-15's B4), and a folder whose name only starts with the
   root's is elsewhere.
4. **§6.4.** The own folder is open only while the ticket is ``in_progress``.
5. **§6.5.** ``ticket-lead`` (DEC-434) is not among "any role": it may not
   write in its ticket's folder; its own list is unchanged.

The fixtures are the suite's (``conftest.py``, ``w2_50_support.py``): a
temporary HOME, a temp folder disjoint from it, a fixture project built from
scratch. The tickets of answer 4 are written into the fixture project by the
case, from the suite's own ticket text with only the status changed.
"""

from __future__ import annotations

import os
import shutil

import pytest

import w2_50_support as support

q = support.q
MAIN, OTHER = support.MAIN, support.OTHER
ENGINEER = support.ENGINEER
TICKET_LEAD = "ticket-lead"      # DEC-434: the ticket lead's own role, known to the guard (W1-50)

needs_gitleaks = pytest.mark.skipif(shutil.which("gitleaks") is None,
                                    reason="gitleaks is not on PATH: the secret filter and the check cannot run")


def _refused(result, what, sandbox, *paths):
    names = []
    for path in paths:
        names += support.why_words(path, sandbox)
    support.assert_refused(result, what, *names)


def _populate(sandbox):
    """The root with MAIN's and OTHER's folders and a file in each, as the refusal cases build it."""
    own, other = sandbox.own(MAIN), sandbox.own(OTHER)
    support.write(own / "mine.txt", "mine\n")
    support.write(other / "theirs.txt", "theirs\n")
    return own, other


def _writes_refused(guard, sandbox, folder, what, role, ticket_id):
    """Write, Edit and two judged Bash forms (a redirect, and ``mkdir -p`` of a new folder) in ``folder``."""
    target = folder / "notes.txt"
    support.write(target, "a\n")
    for tool_name in ("Write", "Edit"):
        _refused(guard(tool_name, target, role, ticket_id), f"{tool_name} on {target} {what}", sandbox, target)
    for command in (f"echo written > {q(target)}", f"mkdir -p {q(folder / 'clone')}"):
        _refused(guard("Bash", command, role, ticket_id), f"Bash `{command}` {what}", sandbox, folder)


# --------------------------------------------------------------------------
# 1. R7 is scoped to the root
# --------------------------------------------------------------------------

# The spellings of the root the suite's removal cases use, but the plain one (held by
# test_w2_50_guard_refusals.py::test_removing_or_moving_the_root_is_refused[rmdir]).
ROOT_RMDIRS = {
    "trailing-slash": "rmdir {root}/",
    "dot": "rmdir {root}/.",
    "through-the-own-folder": "rmdir {root}/W2-90/..",
}


@pytest.mark.parametrize("spelling", sorted(ROOT_RMDIRS))
def test_rmdir_of_the_root_is_refused_in_each_spelling(guard, sandbox, spelling):
    """DEC-743 1: ``rmdir`` is judged for ``~/gov-os-runs`` itself, however the root is spelled."""
    _populate(sandbox)
    command = ROOT_RMDIRS[spelling].format(root=q(sandbox.root))
    _refused(guard("Bash", command), f"Bash `{command}`", sandbox, sandbox.root)


def test_rmdir_of_an_empty_folder_in_the_repository_outside_the_paths_stays_as_today(guard, sandbox, project):
    """DEC-743 1: ``rmdir`` is not judged everywhere. Inside the repository it stays as today's guard decides it.

    Measured on ``w2/W2-50`` at ``a5ef3c69``, before the change: the guard allows
    ``rmdir`` of an empty folder under ``docs/``, outside the engineer's
    ``src/app/**``, because it does not judge ``rmdir``. The case holds that
    decision; judging ``rmdir`` as a write target everywhere would refuse it.
    """
    empty = project / "docs" / "empty"
    empty.mkdir()
    command = f"rmdir {q(empty)}"
    support.assert_allowed(guard("Bash", command), f"Bash `{command}` (an empty folder outside the ticket's paths)")


def test_rmdir_of_an_empty_folder_inside_the_own_folder_stays_allowed(guard, sandbox):
    """DEC-743 1: once the own folder is open, ``rmdir`` of its empty sub-folder is allowed."""
    own, _ = _populate(sandbox)
    (own / "empty").mkdir()
    command = f"rmdir {q(own / 'empty')}"
    support.assert_allowed(guard("Bash", command), f"Bash `{command}` (an empty folder in the own folder)")


# --------------------------------------------------------------------------
# 2. R2's step: the launcher makes the root and the own folder, and nothing else
# --------------------------------------------------------------------------

def _launched(sandbox, cli, role, ticket):
    result = support.launch(sandbox, cli, role, ticket)
    result.session()
    return result


def test_the_first_launch_makes_the_root_with_the_own_folder_and_nothing_else(project, sandbox, cli):
    """Neither the root nor any folder exists: the session finds the root holding its own folder only."""
    assert not sandbox.root.exists(), "the fixture's HOME already holds the root"
    support.set_plan(cli, listing=(sandbox.root,))
    session = _launched(sandbox, cli, ENGINEER, MAIN).session()
    assert session["listed"][str(sandbox.root)] == [MAIN.folder], (
        f"when the session started, the root {sandbox.root} held {session['listed'][str(sandbox.root)]}, "
        f"not exactly the own folder [{MAIN.folder!r}] (None: the launcher made no root)")
    assert sandbox.own(MAIN).is_dir() and not sandbox.own(MAIN).is_symlink(), (
        f"{sandbox.own(MAIN)} is not a directory after the launch")


def test_a_launch_into_an_existing_root_makes_only_the_own_folder_and_leaves_the_rest_alone(project, sandbox, cli):
    """The root exists with other folders but not the own one: the launch adds the own folder and touches nothing else."""
    support.write(sandbox.own(OTHER) / "clone" / "README.md", "W2-91's clone\n")
    support.write(sandbox.root / "W2-77" / "notes.txt", "a folder of no ticket\n")
    before = support.snapshot(sandbox.root)
    support.set_plan(cli, listing=(sandbox.root,))
    session = _launched(sandbox, cli, ENGINEER, MAIN).session()
    expected = sorted(["W2-77", MAIN.folder, OTHER.folder])
    assert session["listed"][str(sandbox.root)] == expected, (
        f"when the session started, the root held {session['listed'][str(sandbox.root)]}, not {expected}")
    after = {rel: digest for rel, digest in support.snapshot(sandbox.root).items()
             if rel != MAIN.folder and not rel.startswith(MAIN.folder + os.sep)}
    assert after == before, "the launch changed what the root held outside the own folder"


# --------------------------------------------------------------------------
# 3. The link rule (§6.1 (i)): not into the root; elsewhere still followed
# --------------------------------------------------------------------------

@pytest.fixture()
def indexed_project(sandbox):
    """The fixture project with the kernel's gitleaks rules, as ``test_w2_50_never_indexed.py`` builds it."""
    project = support.make_project(sandbox, extra={"governance/project/path-map.yaml": support.path_map_text()})
    shutil.copy2(support.GITLEAKS_TEMPLATE, project / ".gitleaks.toml")
    support.git(project, "add", "-A")
    support.git(project, "commit", "-q", "-m", "gitleaks rules")
    return project


def _scratch(project):
    scratch = project / ".gov-runtime" / "scratch"
    scratch.mkdir(parents=True, exist_ok=True)
    return scratch


def _plant_secret(folder):
    """A store-like file holding the planted secret, in ``folder``."""
    return support.write(folder / ".gov-runtime" / "store.txt", f"chunk: {support.SECRET}\n")


@needs_gitleaks
def test_the_check_does_not_scan_the_root_through_a_link_to_the_root_itself(indexed_project, sandbox):
    """A folder link from ``.gov-runtime/scratch/`` to ``~/gov-os-runs`` itself, not to a folder under it."""
    _plant_secret(sandbox.own(MAIN) / "clone")
    (_scratch(indexed_project) / "runs-root").symlink_to(sandbox.root, target_is_directory=True)
    run = support.run_check(sandbox, indexed_project)
    assert run.returncode == 0, (
        f"the repository's check scanned ~/gov-os-runs through a link to the root itself\n{run.describe()}")
    assert support.SECRET not in run.stdout + run.stderr, "the check printed the secret"


@needs_gitleaks
def test_the_check_still_follows_a_linked_folder_elsewhere(indexed_project, sandbox):
    """W1-15's B4 here: a link to a folder outside the project and outside ``~/gov-os-runs`` is still followed."""
    shared = sandbox.elsewhere / "shared-store"
    _plant_secret(shared)
    _plant_secret(sandbox.own(MAIN) / "clone")     # the root exists too, with a secret the check must not need
    (_scratch(indexed_project) / "shared").symlink_to(shared, target_is_directory=True)
    run = support.run_check(sandbox, indexed_project)
    assert run.returncode != 0, (
        f"a link in .gov-runtime/ to a folder elsewhere ({shared}) that holds a secret, and the check is green\n"
        f"{run.describe()}")


@needs_gitleaks
def test_the_check_follows_a_link_to_a_folder_whose_name_only_starts_with_the_roots(indexed_project, sandbox):
    """``~/gov-os-runs-old`` is not the root: a link to it is followed like any other folder elsewhere."""
    near = sandbox.home / f"{support.RUNS}-old"
    _plant_secret(near / MAIN.folder)
    sandbox.own(MAIN).mkdir(parents=True)          # the root exists beside it
    (_scratch(indexed_project) / "runs-old").symlink_to(near, target_is_directory=True)
    run = support.run_check(sandbox, indexed_project)
    assert run.returncode != 0, (
        f"a link in .gov-runtime/ to {near}, whose name only starts with the root's, was not followed: the check "
        f"is green with a secret there\n{run.describe()}")


# --------------------------------------------------------------------------
# 4. §6.4: the own folder is open only while the ticket is in_progress
# --------------------------------------------------------------------------

STATUS_TICKET = support.Ticket("DAEO-zz95", ENGINEER, "W2-95", ("src/app/**",))


def _add_ticket(project, ticket, status):
    """Write ``ticket`` into the fixture project with ``status``, from the suite's own ticket text, and commit it."""
    original = support.ticket_text(ticket)
    text = original.replace("status: in_progress", f"status: {status}", 1)
    assert status == "in_progress" or text != original, "the fixture ticket's text has no status line to change"
    support.write(project / ".tickets" / f"{ticket.tk}.md", text)
    support.git(project, "add", "-A")
    support.git(project, "commit", "-q", "-m", f"fixture ticket {ticket.tk} ({status})")


def test_the_same_ticket_in_progress_opens_its_folder(guard, sandbox, project):
    """The control of the two refusals below: the ticket written the same way, ``in_progress``, opens its folder."""
    _add_ticket(project, STATUS_TICKET, "in_progress")
    target = sandbox.own(STATUS_TICKET) / "notes.txt"
    support.write(target, "a\n")
    for tool_name in ("Write", "Edit"):
        support.assert_allowed(guard(tool_name, target, ENGINEER, STATUS_TICKET.tk),
                               f"{tool_name} on {target} by the engineer on {STATUS_TICKET.tk} (in_progress)")
    command = f"echo written > {q(target)}"
    support.assert_allowed(guard("Bash", command, ENGINEER, STATUS_TICKET.tk), f"Bash `{command}` (in_progress)")


@pytest.mark.parametrize("status", ("open", "closed"))
def test_the_folder_of_a_ticket_that_is_not_in_progress_is_closed(guard, sandbox, project, status):
    """DEC-743 6: a session whose GOV_TICKET names a ticket in another status may not write in its folder."""
    _add_ticket(project, STATUS_TICKET, status)
    _writes_refused(guard, sandbox, sandbox.own(STATUS_TICKET), f"by the engineer on {STATUS_TICKET.tk} ({status})",
                    ENGINEER, STATUS_TICKET.tk)


# --------------------------------------------------------------------------
# 5. §6.5: ticket-lead is not among "any role"
# --------------------------------------------------------------------------

def test_a_ticket_lead_may_not_write_in_its_tickets_folder(guard, sandbox):
    """DEC-743 7: a ``ticket-lead`` session on MAIN (``in_progress``) may not write in ``~/gov-os-runs/W2-90``."""
    _writes_refused(guard, sandbox, sandbox.own(MAIN), f"by {TICKET_LEAD} on {MAIN.tk}", TICKET_LEAD, MAIN.tk)


def test_a_ticket_lead_keeps_its_scratch_in_the_repository(guard, sandbox, project):
    """The control: DEC-434's own list is unchanged, so the refusal above is not one of an unknown role."""
    target = project / ".gov-runtime" / "scratch" / "lead" / "CHECKPOINT.md"
    support.assert_allowed(guard("Write", target, TICKET_LEAD, MAIN.tk), f"Write on {target} by {TICKET_LEAD}")
    command = f"echo written > {q(project / '.gov-runtime' / 'scratch' / 'lead' / 'notes.md')}"
    support.assert_allowed(guard("Bash", command, TICKET_LEAD, MAIN.tk), f"Bash `{command}` by {TICKET_LEAD}")
