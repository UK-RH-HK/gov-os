import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _repobuilder  # noqa: E402


@pytest.fixture(autouse=True)
def _isolated_store(tmp_path, monkeypatch):
    """Every test gets its own store -- never the real BR-AR-0005 store, and never another test's (tmp_path is
    unique per test). Mirrors tests/core/conftest.py's _no_env_leak intent for this node's own tests."""
    monkeypatch.setenv("GOVBRIDGE_STORE", str(tmp_path / "store"))


@pytest.fixture
def repo(tmp_path):
    root = tmp_path / "repo"
    _repobuilder.init(root)
    return root
