"""W2-50, success 4: nothing under ``~/gov-os-runs`` is indexed by this repository's stores.

"Never indexed. Nothing under ~/gov-os-runs is indexed by this repository's
stores, and this repository's secrets-indexing check never scans it: A product
clone that is adopted there has its own store, inside the clone; that store is
the clone's, not this repository's; A planted secret in a clone there reaches
no index of this repository." [DEC-728 item 3]

"This repository" is the fixture project (a ticket worktree under the
temporary HOME), built from scratch with a path map whose ``docs`` namespace is
indexed. Its stores are what ``gov rebuild`` builds, run in it with the
worktree's code; a full rebuild needs the embedding endpoint, so the rebuild
here is ``--no-embeddings`` (a temporary repository, never this worktree or the
main tree). The way in that a repository offers to a folder outside it is a
symbolic link: the cases put links from the project into the own folder.

The secrets-indexing check is run as its family runner runs it: its declared
``command``, by ``sh -c``, in the project's root, with gitleaks on PATH.

The planted strings are built at run time; none stands whole in this file.
"""

from __future__ import annotations

import shutil

import pytest

import w2_50_support as support

MAIN = support.MAIN

needs_gitleaks = pytest.mark.skipif(shutil.which("gitleaks") is None,
                                    reason="gitleaks is not on PATH: the secret filter and the check cannot run")


@pytest.fixture()
def indexed_project(sandbox):
    """The fixture project with an indexed ``docs`` namespace, the kernel's gitleaks rules and a word of its own."""
    project = support.make_project(sandbox, extra={
        "governance/project/path-map.yaml": support.path_map_text(),
        "docs/inside.md": f"# Inside\n\nThe word {support.REPO_MARKER} is in the repository.\n",
    })
    shutil.copy2(support.GITLEAKS_TEMPLATE, project / ".gitleaks.toml")
    support.git(project, "add", "-A")
    support.git(project, "commit", "-q", "-m", "gitleaks rules")
    return project


def _plant_runs_clone(sandbox):
    """A clone-like folder in the own folder: a word and a secret in its docs, and a store of its own."""
    clone = sandbox.own(MAIN) / "clone"
    support.write(clone / "docs" / "notes.md", f"# Notes\n\nThe word {support.RUNS_MARKER} is here.\n")
    support.write(clone / "docs" / "config.md", f"# Config\n\nThe value is {support.SECRET} today.\n")
    support.write(clone / ".gov-runtime" / "store.txt", f"chunk: {support.SECRET}\n")
    return clone


def _rebuild(sandbox, root):
    run = support.run_gov(sandbox, root, "rebuild", "--json", "--no-embeddings", timeout=support.REBUILD_TIMEOUT_S)
    assert run.returncode == 0, f"gov rebuild did not succeed in {root}\n{run.describe()}"
    return run


def _store_files_holding(project, sandbox, needle):
    """Files of the project's stores (``.gov-runtime/``) and of HOME outside the root that hold ``needle``."""
    found = support.holders(project / ".gov-runtime", needle)
    found += support.holders(sandbox.home, needle, skip=(sandbox.root, project))
    return found


# --------------------------------------------------------------------------
# The repository's stores
# --------------------------------------------------------------------------

@needs_gitleaks
def test_a_link_into_the_own_folder_brings_nothing_of_it_into_the_repositorys_stores(indexed_project, sandbox):
    project = indexed_project
    clone = _plant_runs_clone(sandbox)
    (project / "docs" / "runs").symlink_to(sandbox.own(MAIN), target_is_directory=True)
    (project / "docs" / "linked-notes.md").symlink_to(clone / "docs" / "notes.md")
    support.git(project, "add", "-A")
    support.git(project, "commit", "-q", "-m", "links into the own folder")
    _rebuild(sandbox, project)
    assert _store_files_holding(project, sandbox, support.REPO_MARKER), (
        "the control failed: the repository's own word reached no store, so the rebuild indexed nothing")
    assert _store_files_holding(project, sandbox, support.RUNS_MARKER) == [], (
        "a word that lives only under ~/gov-os-runs reached this repository's stores: "
        f"{_store_files_holding(project, sandbox, support.RUNS_MARKER)}")
    assert _store_files_holding(project, sandbox, support.SECRET) == [], (
        "a secret planted in a clone under ~/gov-os-runs reached this repository's stores")


@needs_gitleaks
def test_an_adopted_clone_in_the_own_folder_has_its_own_store_inside_it(indexed_project, sandbox):
    """The clone's rebuild makes the clone's store, inside the clone; the repository's stores do not change.

    The repository's stores are compared without their ``logs`` folders: the
    code index's daemon may still write its own log after the repository's
    rebuild has returned, and a log is not an index.
    """
    project = indexed_project
    _rebuild(sandbox, project)
    before = support.snapshot(project / ".gov-runtime", skip_names=("logs",))
    clone = sandbox.own(MAIN) / "clone"
    sandbox.own(MAIN).mkdir(parents=True)
    support.git(sandbox.own(MAIN), "clone", "-q", "--no-hardlinks", str(project), str(clone))
    support.write(clone / "docs" / "clone-only.md", f"# Clone\n\nThe word {support.CLONE_MARKER} is in the clone.\n")
    support.write(clone / "docs" / "config.md", f"# Config\n\nThe value is {support.SECRET} today.\n")
    support.git(clone, "add", "-A")
    support.git(clone, "commit", "-q", "-m", "the clone's own work")
    _rebuild(sandbox, clone)

    clone_store = clone / ".gov-runtime"
    assert support.holders(clone_store, support.CLONE_MARKER), (
        f"the clone's rebuild left no store of its own inside the clone ({clone_store})")
    assert support.snapshot(project / ".gov-runtime", skip_names=("logs",)) == before, (
        "the clone's rebuild changed this repository's stores")
    assert _store_files_holding(project, sandbox, support.CLONE_MARKER) == [], (
        "the clone's word reached this repository's stores or HOME outside the root")
    assert support.holders(clone_store, support.SECRET) == [], "the planted secret reached the clone's own store"
    assert _store_files_holding(project, sandbox, support.SECRET) == [], (
        "a secret planted in the clone reached this repository's stores")


# --------------------------------------------------------------------------
# The secrets-indexing check
# --------------------------------------------------------------------------

@needs_gitleaks
def test_the_check_finds_a_secret_in_the_repositorys_own_store(indexed_project, sandbox):
    """The control: the check, run here, does look at this repository's derived stores."""
    support.write(indexed_project / ".gov-runtime" / "chunk.txt", f"chunk: {support.SECRET}\n")
    run = support.run_check(sandbox, indexed_project)
    assert run.returncode != 0, f"the check did not find a secret in .gov-runtime/\n{run.describe()}"


@needs_gitleaks
def test_the_check_is_green_with_a_secret_in_a_clone_under_the_root(indexed_project, sandbox):
    _plant_runs_clone(sandbox)
    support.write(indexed_project / ".gov-runtime" / "clean.txt", "nothing here\n")
    run = support.run_check(sandbox, indexed_project)
    assert run.returncode == 0, f"the repository's check failed on a secret that lies under ~/gov-os-runs\n{run.describe()}"


@needs_gitleaks
@pytest.mark.parametrize("link", ("a-folder-link", "a-file-link"))
def test_the_check_does_not_scan_the_root_through_a_link_in_the_runtime_folder(indexed_project, sandbox, link):
    """A link from ``.gov-runtime/scratch/`` into the own folder: the check never scans ``~/gov-os-runs``."""
    clone = _plant_runs_clone(sandbox)
    scratch = indexed_project / ".gov-runtime" / "scratch"
    scratch.mkdir(parents=True, exist_ok=True)
    if link == "a-folder-link":
        (scratch / "runs").symlink_to(sandbox.own(MAIN), target_is_directory=True)
    else:
        (scratch / "store-link.txt").symlink_to(clone / ".gov-runtime" / "store.txt")
    run = support.run_check(sandbox, indexed_project)
    assert run.returncode == 0, (
        f"the repository's check scanned ~/gov-os-runs through {link} in .gov-runtime/scratch/\n{run.describe()}")
    assert support.SECRET not in run.stdout + run.stderr, "the check printed the secret"
