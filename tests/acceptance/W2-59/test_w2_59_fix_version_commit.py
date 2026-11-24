"""W2-59 fix F3 (fixes-015a, release 0.1.5): ``gov --version`` in a pinned install prints the commit its wheel was built
from, not ``commit unknown``.

The wheel is built through the one route the release, ``gov install`` and ``gov update`` share
(``gov.release._wheel(repo, commit)``) from a small git repository holding a copy of this tree's ``src/`` and
``pyproject.toml``, unpacked into a folder that has no git repository and no ``pyproject.toml`` around it (an installed
layout), and run from a working folder that is no repository or is another one. A source checkout prints its own git
head as before (guard).
"""

from __future__ import annotations

import json
import shutil
import zipfile

import pytest

import w2_59_support as support


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    base = tmp_path_factory.mktemp("w259-fix-version")
    repo = base / "built-from"
    repo.mkdir()
    shutil.copytree(support.SRC, repo / "src", ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    shutil.copyfile(support.PYPROJECT, repo / "pyproject.toml")
    support.git(repo, "init", "-q")
    support.git(repo, "add", "-A")
    support.git(repo, "commit", "-q", "-m", "w259 fix: the tree the wheel is built from")
    commit = support.git(repo, "rev-parse", "HEAD")
    keep = base / "kept"
    keep.mkdir()
    code = ("import json, sys; from pathlib import Path; from gov.release import _wheel; "
            "print(json.dumps(_wheel(Path(sys.argv[1]), sys.argv[2], keep=Path(sys.argv[3]))))")
    env = support.worktree_code_env(base / "home")
    (base / "home").mkdir()
    done = support.run([support.REAL_PYTHON, "-c", code, repo, commit, keep], cwd=base, env=env)
    assert done.returncode == 0, f"the wheel could not be built\n{done.describe()}"
    wheel = json.loads(done.stdout.strip().splitlines()[-1])["path"]
    site = base / "site"
    with zipfile.ZipFile(wheel) as archive:
        archive.extractall(site)
    return {"repo": repo, "commit": commit, "site": site, "base": base}


def _version(built, cwd):
    env = support.base_env(built["base"] / "home", support.SYSTEM_PATH)
    env["PYTHONPATH"] = str(built["site"])
    return support.run([support.REAL_PYTHON, "-m", "gov.cli.main", "--version"], cwd=cwd, env=env)


def _named(done):
    named = support.named_commits(done.stdout)
    assert named, f"gov --version names no commit\n{done.describe()}"
    return named


def test_the_installed_wheel_prints_the_commit_it_was_built_from(built):
    outside = built["base"] / "outside"
    outside.mkdir(exist_ok=True)
    done = _version(built, outside)
    assert done.returncode == 0, done.describe()
    assert "unknown" not in done.stdout, f"gov --version says unknown\n{done.describe()}"
    assert any(built["commit"].startswith(c) and len(c) >= 12 for c in _named(done)), (
        f"gov --version does not print the build commit {built['commit']}\n{done.describe()}")


def test_the_installed_wheel_inside_another_repository_still_prints_its_own_commit(built):
    other = support.make_repository(built["base"] / "other")
    other_head = support.git(other, "rev-parse", "HEAD")
    done = _version(built, other)
    assert done.returncode == 0, done.describe()
    named = _named(done)
    assert any(built["commit"].startswith(c) and len(c) >= 12 for c in named), done.describe()
    assert not any(other_head.startswith(c) for c in named), f"it named the working folder's commit\n{done.describe()}"


def test_a_source_checkout_still_prints_its_git_head(built):
    """Guard (green on the base): the copy's ``src`` on the path, in a git repository, names that repository's HEAD."""
    outside = built["base"] / "outside2"
    outside.mkdir(exist_ok=True)
    env = support.base_env(built["base"] / "home", support.SYSTEM_PATH)
    env["PYTHONPATH"] = str(built["repo"] / "src")
    done = support.run([support.REAL_PYTHON, "-m", "gov.cli.main", "--version"], cwd=outside, env=env)
    assert done.returncode == 0, done.describe()
    assert any(built["commit"].startswith(c) and len(c) >= 12 for c in _named(done)), done.describe()
