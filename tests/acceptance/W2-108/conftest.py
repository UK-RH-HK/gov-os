"""Fixtures of the W2-108 acceptance tests (README): a planted repository, its store, the stand-in embedder."""

from __future__ import annotations

import pytest

import w2_108_support as S


@pytest.fixture(scope="session")
def embedder():
    stand_in = S.OllamaStandIn()
    yield stand_in
    stand_in.close()


@pytest.fixture
def driver(tmp_path):
    return S.Driver(tmp_path / "driver")


@pytest.fixture
def planted(tmp_path, driver, embedder):
    """A committed planted repository whose store (record graph, lexical index, vectors) is built and fresh."""
    reason = S.lacking_gitleaks() or S.lacking_sqlite_vec()
    if reason:
        pytest.skip(reason)
    project = S.plant(tmp_path / "project")
    S.build(driver, project, embedder.host)
    return project


@pytest.fixture
def no_commit(tmp_path, driver, embedder):
    """A planted repository with no commit yet (its files only staged): ``HEAD`` cannot be read. Its lexical index
    and vectors are built; it has no record graph (a load needs ``HEAD``)."""
    reason = S.lacking_gitleaks() or S.lacking_sqlite_vec()
    if reason:
        pytest.skip(reason)
    project = S.plant(tmp_path / "project", with_commit=False)
    S.build(driver, project, embedder.host, records=False)
    return project


@pytest.fixture
def repo_store():
    """The store of the worktree the tests run in (or of ``W2108_STORE_ROOT``); skipped where there is none."""
    root = S.store_root()
    if not (root / S.STORE_REL).is_file():
        pytest.skip(f"no store at {root / S.STORE_REL}: the lead rebuilds the worktree's store before running "
                    f"these cases (README, 'This repository's store')")
    return root
