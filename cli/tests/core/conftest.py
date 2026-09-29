import sys
from pathlib import Path

import pytest

FIXTURES_CORE = Path(__file__).resolve().parents[1] / "fixtures" / "core"
sys.path.insert(0, str(FIXTURES_CORE))
import repobuilder  # noqa: E402

write_canonical_view = repobuilder.write_canonical_view


@pytest.fixture
def fixture_repo(tmp_path):
    return repobuilder.build(tmp_path / "repo")


@pytest.fixture
def rules_path():
    return str(FIXTURES_CORE / "fixture-corpus-rules.yaml")


@pytest.fixture
def view_path(tmp_path, fixture_repo):
    p = tmp_path / "canonical-view.yaml"
    write_canonical_view(p, fixture_repo)
    return str(p)


@pytest.fixture(autouse=True)
def _no_env_leak(monkeypatch):
    # every test controls GOVBRIDGE_STORE / GOV_BRIDGE_HOME explicitly; never inherit the developer's real cache
    monkeypatch.delenv("GOVBRIDGE_STORE", raising=False)
