"""Fixtures for the W2-57 acceptance tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_57_support as support  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def code_under_test():
    """This worktree's ``src/`` is the code every case runs (DEC-732)."""
    return support.code_under_test()


@pytest.fixture(scope="session")
def rulesync_bin():
    """The installed rulesync, as W1-38's suite finds it. Skips only when it is truly absent; a rulesync that
    is there and gives no answer in time fails the case, naming the timeout (DEC-892 item 2)."""
    if support.adapters.rulesync_version() is None:
        pytest.skip("rulesync is not installed")
    return support.REAL_RULESYNC


@pytest.fixture()
def generated_project(tmp_path, rulesync_bin):
    """An adopted project as W1-38's suite builds it, ``rulesync generate`` run in it and committed."""
    root = tmp_path / "project"
    root.mkdir()
    support.adapters.init_git(root)
    support.adapters.build_project_from_template(root)
    made = support.adapters.run_rulesync_generate(root)
    assert made.returncode == 0, f"rulesync generate failed: {made.stderr}"
    support.adapters.commit_all(root, "generated")
    return root


@pytest.fixture()
def sandbox(tmp_path):
    """The home, temporary and launcher folders ``gov`` runs with (W1-07)."""
    return support.cli.make_sandbox(tmp_path / "sandbox")


@pytest.fixture()
def stand_ins(tmp_path):
    """A folder for the case's stand-in tools; a stand-in still waiting at the end is stopped."""
    folder = support.StandIns(tmp_path / "stand-ins")
    yield folder
    folder.stop_leftovers()


@pytest.fixture(scope="session")
def interface():
    """The envelope fields and exit codes of this worktree's ``docs/interfaces/API-0002.yaml``."""
    return support.cli.load_interface(support.REPO_ROOT)
