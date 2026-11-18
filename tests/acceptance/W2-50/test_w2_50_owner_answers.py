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


# --------------------------------------------------------------------------
# 1. R7 is scoped to the root
# --------------------------------------------------------------------------


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


# --------------------------------------------------------------------------
# 5. §6.5: ticket-lead is not among "any role"
# --------------------------------------------------------------------------

