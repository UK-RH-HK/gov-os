"""KPI success 4 [CAP-27.a] and failure 1: ``gov status`` only reads.

"Read-only: git status --porcelain unchanged." / "status mutates the repository."

CAP-27's measure is ``git status --porcelain``. Derived state is ignored by
git, so that measure alone would not see a write under ``.gov-runtime/``: the
cases also compare every file of the project (the store, the claims and the
freeze flag included), HEAD and the refs, and what lies outside the project
(HOME, where the freeze mirror and the session logs live; the temp directory;
an unrelated directory). No source allows the command a cache (README,
"Read-only"): it writes nothing.

W1-07's suite runs the same measure on a copy of this repository's working
tree for every read command, ``status`` among them.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

import w1_32_support as support

cli_support = support.cli_support
tasks_support = support.tasks_support
pause_support = support.pause_support

DEV_TIERS = Path(os.environ.get("GOV_DEV_TIERS", "~/gov-os-workbench/synthetic")).expanduser()
DEV_TIER = "a-dev"
FORMS = {"json": ("--json",), "plain": ()}


@pytest.mark.parametrize("form", sorted(FORMS))
def test_git_status_porcelain_is_unchanged(project, sandbox, form):
    """CAP-27's acceptance line, on a clean project."""
    assert cli_support.porcelain(project.root) == "", "the fixture project is not clean"
    run = support.gov(project, sandbox, support.COMMAND, *FORMS[form])
    assert run.returncode == 0, run.describe()
    assert cli_support.porcelain(project.root) == "", \
        f"gov status left changes:\n{cli_support.porcelain(project.root)}\n{run.describe()}"


@pytest.mark.parametrize("form", sorted(FORMS))
def test_status_writes_nothing_anywhere(project, sandbox, interface, form):
    """Not in the project, not under ``.gov-runtime/``, not in HOME, not in the temp directory."""
    before = support.state(project, sandbox)
    run = support.gov(project, sandbox, support.COMMAND, *FORMS[form])
    if form == "json":
        support.answered(run, interface)
    support.assert_unchanged(before, support.state(project, sandbox), run)


def test_status_leaves_uncommitted_work_as_it_was(project, sandbox, interface):
    tasks_support.write(project.root, "README.md", "changed, not committed\n")
    tasks_support.write(project.root, "untracked-note.txt", "untracked\n")
    before = support.state(project, sandbox)
    assert before["porcelain"] != ""
    run = support.status(project, sandbox)
    support.parts(run, interface)
    support.assert_unchanged(before, support.state(project, sandbox), run)


def test_status_writes_no_store_where_none_is(project, sandbox, interface):
    """It reports the store as not read; it does not load one, and it creates no ``.gov-runtime/``."""
    runtime = project.root / ".gov-runtime"
    (project.root / support.STORE_REL).unlink()
    runtime.rmdir()
    before = support.state(project, sandbox)
    run = support.status(project, sandbox)
    support.parts(run, interface)
    assert not os.path.lexists(runtime), f"gov status created {runtime.name}/\n{run.describe()}"
    support.assert_unchanged(before, support.state(project, sandbox), run)


def test_status_of_a_paused_project_changes_neither_the_flag_nor_its_mirror(project, sandbox, interface):
    pause_support.succeeded(pause_support.pause(project.root, sandbox), interface)
    before = support.state(project, sandbox)
    run = support.status(project, sandbox)
    assert support.paused(support.parts(run, interface)) is True
    support.assert_unchanged(before, support.state(project, sandbox), run)


def test_status_takes_no_claim_and_releases_none(project, sandbox, interface):
    before = pause_support.locks(project.root)
    assert before == [support.T_CLAIMED]
    support.parts(support.status(project, sandbox), interface)
    assert pause_support.locks(project.root) == before
    assert project.driver.call("gov.tasks", "holder", project.root, support.T_CLAIMED) == support.HOLDER


def test_status_with_root_writes_neither_in_the_project_nor_where_it_runs(project, sandbox, interface):
    before = support.state(project, sandbox)
    run = cli_support.run_gov_with_code(support.REPO_ROOT, project.root, sandbox, support.COMMAND, "--json",
                                        "--root", str(project.root), cwd=sandbox.elsewhere)
    support.parts(run, interface)
    support.assert_unchanged(before, support.state(project, sandbox), run)


def test_repeated_status_gives_the_same_answer_and_writes_nothing(project, sandbox, interface):
    """Nothing is cached between two runs: the second answer is the first, and the files are as before both."""
    before = support.state(project, sandbox)
    first = support.status(project, sandbox)
    second = support.status(project, sandbox)
    assert support.answered(first, interface) == support.answered(second, interface)
    support.assert_unchanged(before, support.state(project, sandbox), second)


@pytest.mark.local_only
def test_status_leaves_a_dev_tier_clone_clean(sandbox, tmp_path, interface):
    """A project that is not the Gov OS: a clone of a dev tier, never the tier itself."""
    tier = DEV_TIERS / DEV_TIER
    if not (tier / ".git").exists():
        pytest.skip(f"no dev tier at {tier} (GOV_DEV_TIERS)")
    clone = tmp_path / "tier"
    subprocess.run(["git", "clone", "-q", "--no-hardlinks", str(tier), str(clone)], check=True, capture_output=True)
    before = (cli_support.porcelain(clone), cli_support.git_state(clone), cli_support.snapshot(clone, skip=(".git",)))
    run = cli_support.run_gov_with_code(support.REPO_ROOT, clone, sandbox, support.COMMAND, "--json")
    support.parts(run, interface)
    after = (cli_support.porcelain(clone), cli_support.git_state(clone), cli_support.snapshot(clone, skip=(".git",)))
    assert after[0] == before[0] == "", f"git status --porcelain is not empty:\n{after[0]}\n{run.describe()}"
    assert after[1:] == before[1:], f"gov status changed the clone\n{run.describe()}"
