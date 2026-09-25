import sys
from pathlib import Path

import pytest

# Reuse B1's synthetic repo builder (tests/fixtures/core/repobuilder.py) exactly the way tests/core/conftest.py
# does -- read-only reuse of an existing generic fixture, never a mutation of tests/fixtures/core/** (outside
# this node's mutation_scope).
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
def _isolated_store(monkeypatch, tmp_path):
    # Every test builds its own store under tmp_path -- never the developer's real cache, never another run's
    # GOVBRIDGE_STORE (BR-DAG-AMEND-1).
    monkeypatch.delenv("GOVBRIDGE_STORE", raising=False)
    monkeypatch.setenv("GOVBRIDGE_STORE", str(tmp_path / "store"))
    monkeypatch.setenv("GOV_BRIDGE_HOME", str(tmp_path / "home"))


@pytest.fixture
def built_store(fixture_repo, view_path, rules_path):
    """Import govbridge.lexical (registers the layer) and run one full build (core + lexical together) against
    the fixture repo, returning (fixture_repo, view_path, rules_path) for the calling test to query against."""
    import govbridge.lexical  # noqa: F401  (registration side effect)
    from govbridge.core import freshness

    result = freshness.run(view_path=view_path, rules_path=rules_path, repo=str(fixture_repo.root), from_clean=True)
    assert result["trigger"] == "FULL"
    return fixture_repo, view_path, rules_path
