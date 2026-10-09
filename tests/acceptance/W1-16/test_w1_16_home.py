"""KPI success 1 and failure 2: a per-repository home under ``.gov-runtime/`` [CAP-12.b].

Two repositories in temporary directories are indexed through the wrapper. Each
has its own home under its own ``.gov-runtime/``; ``list_projects`` asked in
one shows that repository's project and nothing else, by the wrapper and by the
tool itself; and no index file exists anywhere else after the run, the tool's
default home included. No test indexes this repository (DEC-322).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

import w1_16_support as support

ALPHA = {
    "app/alpha.py": "def alpha_only_helper(value):\n    return value + 1\n\n\n"
                    "def alpha_entry(value):\n    return alpha_only_helper(value)\n",
    "README.md": "# Alpha\n\nA small repository.\n",
}
BETA = {
    "lib/beta.py": "def beta_only_helper(value):\n    return value * 2\n\n\n"
                   "def beta_entry(value):\n    return beta_only_helper(value)\n",
    "README.md": "# Beta\n\nAnother small repository.\n",
}


def _repository(base, files):
    repo = support.Repo(base)
    for rel, text in files.items():
        repo.write(rel, text)
    return repo.commit("first")


@pytest.fixture(scope="module")
def sandbox(module_sandbox):
    """The tests of this file share one sandbox and the two indexed repositories."""
    return module_sandbox


@pytest.fixture(scope="module")
def two(module, cbm, sandbox, tmp_path_factory):
    """Two repositories, both indexed, and what stood in the tool's default home and in this repository's index
    stores before."""
    tmp_path = tmp_path_factory.mktemp("w1-16-home")
    before = {
        "default-home": support.snapshot(Path.home() / support.TOOL_DEFAULT_HOME_REL),
        "this-repository": support.index_stores(support.REPO_ROOT / support.RUNTIME_REL),
    }
    alpha = _repository(tmp_path / "alpha", ALPHA)
    beta = _repository(tmp_path / "beta", BETA)
    for repo in (alpha, beta):   # one indexing job at a time
        support.codeintel(repo.root, [("index", [])], sandbox)
    return alpha, beta, before


def _home(repo, sandbox):
    return Path(support.one(repo.root, "home", [], sandbox))


def test_the_wrapper_offers_its_public_interface(module, sandbox):
    """The interface the README states: a Python interface in ``gov.codeintel``, as W1-09's ``gov.tasks`` is."""
    child = ("import json, gov.codeintel as api\n"
             f"print(json.dumps([name for name in {list(support.INTERFACE)!r} "
             "if not callable(getattr(api, name, None))]))\n")
    done = subprocess.run([sys.executable, "-c", child], cwd=str(sandbox.elsewhere), env=support.child_env(sandbox),
                          capture_output=True, text=True, timeout=support.TIMEOUT_S, stdin=subprocess.DEVNULL)
    assert done.returncode == 0, f"gov.codeintel cannot be imported:\n{done.stderr}"
    missing = json.loads(done.stdout.splitlines()[-1])
    assert not missing, f"gov.codeintel lacks: {missing}"


@pytest.mark.local_only
def test_the_home_is_under_the_repositorys_gov_runtime(two, sandbox):
    for repo in two[:2]:
        home = _home(repo, sandbox)
        runtime = (repo.root / support.RUNTIME_REL).resolve()
        assert home.is_absolute() and home.resolve().is_relative_to(runtime) and home.resolve() != runtime.parent, \
            f"the home {home} is not under {runtime}"
        assert home.is_dir(), f"the home {home} does not exist after indexing"
        assert support.index_files(home), f"the home {home} holds no index file after indexing"


@pytest.mark.local_only
def test_two_repositories_have_two_homes(two, sandbox):
    alpha, beta, _ = two
    assert _home(alpha, sandbox).resolve() != _home(beta, sandbox).resolve()


@pytest.mark.local_only
def test_list_projects_in_one_repository_shows_only_its_own_project(two, sandbox):
    """By the wrapper, and by the tool's own ``list_projects`` asked with that repository's home (DEC-076)."""
    alpha, beta, _ = two
    for repo, other in ((alpha, beta), (beta, alpha)):
        listed = support.one(repo.root, "projects", [], sandbox)
        assert isinstance(listed, list) and len(listed) == 1 and isinstance(listed[0], str), \
            f"{repo.root.name}: expected one project name, got {listed!r}"
        seen = support.tool_projects(_home(repo, sandbox), sandbox)
        assert [name for name, _ in seen] == listed, \
            f"{repo.root.name}: the tool lists {seen} in this home, the wrapper {listed}"
        assert not [row for row in seen if str(other.root) in row[1]], \
            f"{repo.root.name}: the other repository's project is listed: {seen}"


@pytest.mark.local_only
def test_a_repository_answers_only_from_its_own_code(two, sandbox):
    alpha, beta, _ = two
    for repo, own, rel, foreign in ((alpha, "alpha_only_helper", "app/alpha.py", "beta_only_helper"),
                                    (beta, "beta_only_helper", "lib/beta.py", "alpha_only_helper")):
        run = support.codeintel(repo.root, [("definitions", [own]), ("definitions", [foreign])], sandbox)
        mine = support.entries(run.results[0], f"definitions({own})", repo.root)
        assert (rel, own) in mine, f"{repo.root.name} does not answer for its own code\n{run.describe()}"
        assert run.results[1] == [], f"{repo.root.name} answers for the other repository's code\n{run.describe()}"


@pytest.mark.local_only
def test_indexing_again_keeps_one_project(two, sandbox):
    alpha = two[0]
    run = support.codeintel(alpha.root, [("index", []), ("projects", [])], sandbox)
    assert len(run.results[1]) == 1, f"indexing twice left {run.results[1]!r}\n{run.describe()}"
    assert len(support.tool_projects(_home(alpha, sandbox), sandbox)) == 1


@pytest.mark.local_only
def test_no_index_file_exists_outside_gov_runtime_after_a_run(two, sandbox):
    """Failure 2. Index files are SQLite files, their side files and graph dumps, wherever a child could write."""
    alpha, beta, _ = two
    for repo in (alpha, beta):
        support.codeintel(repo.root, [("callers", [f"{repo.root.name}_only_helper"]), ("dead_code", [])], sandbox)
        outside = support.index_files(repo.root, skip=(".git", support.RUNTIME_REL))
        assert not outside, f"{repo.root.name}: index files in the repository, outside .gov-runtime/: {outside}"
        assert not (repo.root / ".codebase-memory").exists(), "the tool's persistence folder was written"
        assert repo.status() == [], \
            f"{repo.root.name}: the run changed the repository outside .gov-runtime/: {repo.status()}"
    for place in sandbox.places:
        left = support.index_files(place)
        assert not left, f"index files left in {place}: {left}"


@pytest.mark.local_only
def test_the_tools_default_home_is_not_used(two, sandbox):
    """Neither the default home of the child's HOME, nor the user's own, gains or loses a file."""
    before = two[2]
    default = sandbox.home / support.TOOL_DEFAULT_HOME_REL
    assert not default.exists() or not support.listing(default), \
        f"the tool's default home was used: {sorted(support.listing(default))}"
    assert support.snapshot(Path.home() / support.TOOL_DEFAULT_HOME_REL) == before["default-home"], \
        "the user's own codebase-memory home changed during the run"


@pytest.mark.local_only
def test_this_repository_is_not_indexed_by_the_run(two):
    """DEC-322: the tests build their indexes in temporary repositories; this repository's stores are not theirs.

    Only the index stores are watched (DEC-563): the rest of this repository's runtime folder is written by other
    sessions while the suite runs."""
    before = two[2]
    runtime = support.REPO_ROOT / support.RUNTIME_REL
    changed = sorted(support.index_stores(runtime) ^ before["this-repository"])
    assert not changed, f"files of an index store appeared or went under {runtime}: {changed}"
