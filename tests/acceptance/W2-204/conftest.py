"""W2-204's fixtures: the planted second repository per test (``world``), the planted runs built once per session
(``stage``), and the two guards every case runs under.

``MEMAUDIT_CONFIG`` (set for every test by ``tests/conftest.py``, W2-204 I6) is removed here for every case of this
folder: a repository is judged by its own file. A case of the trial form sets the variable itself, in the child's
environment.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_204_stages as ST  # noqa: E402
import w2_204_support as K  # noqa: E402


@pytest.fixture(autouse=True)
def _a_repository_s_own_file(monkeypatch):
    monkeypatch.delenv("MEMAUDIT_CONFIG", raising=False)


@pytest.fixture(scope="session", autouse=True)
def _children_import_this_tree_s_gov(tmp_path_factory):
    """Every child imports ``gov`` from this tree's ``src/``; a run that would test other code fails here."""
    home = tmp_path_factory.mktemp("w2-204-home")
    done = subprocess.run([sys.executable, "-c", "import gov; print(gov.__file__)"], env=K.W171.child_env(home),
                          capture_output=True, text=True, timeout=60)
    assert done.returncode == 0, done.stderr
    assert done.stdout.strip().startswith(str(K.SRC) + "/"), (done.stdout, str(K.SRC))


@pytest.fixture
def world(tmp_path) -> K.World:
    return K.build(tmp_path / "w")


@pytest.fixture(scope="session")
def stage(tmp_path_factory):
    return lambda name: ST.shared(tmp_path_factory, name)
