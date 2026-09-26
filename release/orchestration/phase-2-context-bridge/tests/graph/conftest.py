import sys
from pathlib import Path

import pytest

FIXTURES_AUTHORITY = Path(__file__).resolve().parents[1] / "fixtures" / "authority"
sys.path.insert(0, str(FIXTURES_AUTHORITY))
import authority_repobuilder as repobuilder  # noqa: E402


@pytest.fixture
def fixture_repo(tmp_path):
    return repobuilder.build(tmp_path / "repo")


@pytest.fixture
def view_path(tmp_path, fixture_repo):
    p = tmp_path / "canonical-view.yaml"
    repobuilder.write_canonical_view(p, fixture_repo)
    return str(p)


@pytest.fixture
def registry_path():
    return str(FIXTURES_AUTHORITY / "fixture-authority-registry.yaml")


@pytest.fixture(autouse=True)
def _no_env_leak(tmp_path, monkeypatch):
    """Every ``tests/graph/**`` test gets its own private, per-test ``GOVBRIDGE_STORE``.

    BR-DAG-AMEND-R1-17 reopening (pass 3, coordinator finding; same class of bug as
    ``tests/compile/conftest.py``'s own fix -- see its docstring for the full root-cause account): this used to
    only ``delenv``, which does nothing to stop a test that never sets ``GOVBRIDGE_STORE`` itself (for example
    ``test_code_bridge.py``/``test_symbol_history.py``'s own bare ``corestore.open_db()`` seeding calls) from
    falling through to ``govbridge.core.store``'s machine-wide default store, shared with, and mutated
    concurrently by, every other agent's own test-suite run in this session. Pointing it at a fresh
    ``tmp_path``-derived directory instead keeps every test in this package hermetic (R1-T1)."""
    monkeypatch.setenv("GOVBRIDGE_STORE", str(tmp_path / "isolated-govbridge-store"))
