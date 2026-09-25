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
def _no_env_leak(monkeypatch):
    monkeypatch.delenv("GOVBRIDGE_STORE", raising=False)
