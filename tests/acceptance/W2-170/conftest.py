"""W2-170's fixtures: a template world per variant, built once per session under pytest's temp folder (under
``TMPDIR``), and copied whole for each test, so that no test sees another's writes.

Variants (the repository's ``retrieval.yaml`` and path map at the audit commit): ``standard`` (the pool on),
``pool_off``, ``no_retrieval``, ``retrieval_list`` (not a mapping) and ``bad_repo_map`` (a malformed path map).
"""

from __future__ import annotations

import shutil
import subprocess
import sys

import pytest

import w2_170_world as W


@pytest.fixture(scope="session")
def templates(tmp_path_factory):
    built = {}

    def get(variant: str):
        if variant not in built:
            base = tmp_path_factory.mktemp(f"w2-170-template-{variant}")
            W.build(base / "w", variant)
            built[variant] = base / "w"
        return built[variant]

    return get


@pytest.fixture
def make_world(templates, tmp_path):
    count = [0]

    def make(variant: str = "standard") -> W.World:
        count[0] += 1
        dest = tmp_path / f"world{count[0]}"
        shutil.copytree(templates(variant), dest, symlinks=True)
        return W.World(dest)

    return make


@pytest.fixture
def world(make_world) -> W.World:
    return make_world()


@pytest.fixture(scope="session", autouse=True)
def _children_import_this_tree_s_gov(tmp_path_factory):
    """DEC-732: every child process imports ``gov`` from this tree's ``src/``; a run that would test other code
    fails here, before any case."""
    home = tmp_path_factory.mktemp("w2-170-home")
    done = subprocess.run([sys.executable, "-c", "import gov; print(gov.__file__)"], env=W.child_env(home),
                          capture_output=True, text=True, timeout=60)
    assert done.returncode == 0, done.stderr
    assert done.stdout.strip().startswith(str(W.SRC) + "/"), (done.stdout, str(W.SRC))
