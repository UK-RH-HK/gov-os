"""Fixtures for the W2-13 acceptance tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_13_support as support  # noqa: E402


def pytest_configure(config):
    config.addinivalue_line("markers", "local_only: clones a dev tier (GOV_DEV_TIERS) and indexes it; not for CI")
    config.addinivalue_line("markers", "latency: a timed case; run it alone, never beside another suite (DEC-372)")
    config.addinivalue_line(
        "markers", "needs(*names): what the case needs installed on this machine (git, gitleaks, sqlite_vec, ollama, "
                   "reranker); it skips, with the reason, when one is absent. Nothing is installed by a test.")


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    """A case that needs what this machine lacks skips, whatever the state of the ticket."""
    names = [name for marker in item.iter_markers("needs") for name in marker.args]
    reasons = support.lacking(*names)
    if reasons:
        pytest.skip("; ".join(reasons))


@pytest.fixture(scope="session")
def box(tmp_path_factory):
    """The places and environments of the child processes."""
    return support.Box(tmp_path_factory.mktemp("w2-13-box"))


@pytest.fixture(scope="session")
def ollama():
    """The stand-in Ollama endpoint, healthy for the whole session, on its own loopback port."""
    stand_in = support.OllamaStandIn()
    try:
        yield stand_in
    finally:
        stand_in.close()


@pytest.fixture(scope="session")
def base(tmp_path_factory):
    """The fixture repository. Never indexed: it is the source of every clone."""
    return support.build_fixture(tmp_path_factory.mktemp("w2-13-base") / "repo")


@pytest.fixture(scope="session")
def built(box, base, ollama, tmp_path_factory):
    """A clone of the fixture rebuilt by ``gov rebuild --json`` through the stand-in endpoint: the record store, the
    lexical index and the vectors (no code graph: the code tool is not on the scratch PATH). Every case that only
    reads shares it; a case that changes a project takes ``repo``."""
    if support.lacking("git", "gitleaks", "sqlite_vec"):
        pytest.skip("; ".join(support.lacking("git", "gitleaks", "sqlite_vec")))
    root = support.clone(base, tmp_path_factory.mktemp("w2-13-built") / "repo")
    result = box.rebuild(root, host=ollama.host)
    assert result["stores"].get("semantic", {}).get("status") == "recreated", \
        f"premise: the fixture's vectors were not built through the stand-in endpoint: {result['stores']!r}"
    return root


@pytest.fixture(scope="session")
def real_tiers(box, tmp_path_factory):
    """``programme -> root`` of the two dev tiers, each cloned and rebuilt by ``gov rebuild --json`` with this
    machine's Ollama (the real embedder), once for the session: the real-model cases share them and only read."""
    env, roots = box.real_env(), {}
    for programme, tier in support.TIERS.items():
        root = support.clone_tier(tier, tmp_path_factory.mktemp(f"w2-13-real-{tier}") / tier)
        if root is None:
            pytest.skip(f"no dev tier at {support.DEV_TIERS / tier} (GOV_DEV_TIERS)")
        result = box.rebuild(root, env=env)
        assert result["stores"].get("semantic", {}).get("status") == "recreated", \
            f"premise: the vectors of {tier} were not built with the real embedder: {result['stores']!r}"
        roots[programme] = root
    return roots


@pytest.fixture()
def repo(base, tmp_path):
    """This case's own clone of the fixture repository, not indexed."""
    return support.clone(base, tmp_path / "repo")
