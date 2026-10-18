"""Fixtures for the W2-54 acceptance tests (the dropped list's order, the context check's limit, audit-report)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_54_support as support  # noqa: E402


@pytest.fixture(scope="session")
def code_under_test():
    """Every process the suite starts imports ``gov`` from this worktree's ``src/`` (DEC-732)."""
    where = support.gov_file(support.worktree_env())
    assert where == str(support.SRC / "gov" / "__init__.py"), \
        f"gov is imported from {where}, not from this worktree's src/ ({support.SRC})"
    return where


@pytest.fixture(scope="session")
def box(tmp_path_factory, code_under_test):
    """The scratch HOME, PATH and retrieval stand-in of every child process."""
    box = support.Box(tmp_path_factory.mktemp("w2-54-box"))
    where = support.gov_file(box.env("identity"))
    assert where == str(support.SRC / "gov" / "__init__.py"), \
        f"under the retrieval stand-in gov is imported from {where}, not from {support.SRC}"
    return box


@pytest.fixture(scope="session")
def indexed(box):
    """A project with its store and its lexical index: two tickets, one past the default ceiling."""
    if not box.has_gitleaks():
        pytest.fail("gitleaks is not on PATH: the lexical index of the fixture cannot be built", pytrace=False)
    return support.context_project(box, box.workdir / "indexed")


@pytest.fixture(scope="session")
def big_only(box):
    """A project whose one ticket has a mandatory input past the default ceiling (this repository's shape)."""
    if not box.has_gitleaks():
        pytest.fail("gitleaks is not on PATH: the lexical index of the fixture cannot be built", pytrace=False)
    return support.context_project(box, box.workdir / "big-only", tickets=(support.TK_BIG,))


@pytest.fixture(scope="session")
def unindexed(box):
    """A project with its record store and no lexical index."""
    return support.context_project(box, box.workdir / "unindexed", index=False)


@pytest.fixture(autouse=True)
def _fresh_log(request):
    """Each test sees only its own retrieval calls."""
    if "box" in request.fixturenames:
        request.getfixturevalue("box").reset_log()
    yield


@pytest.fixture()
def embedder():
    """Round 2: the stand-in embedder, healthy, on its own loopback port (README, "The stand-in embedder")."""
    stand_in = support.EmbedderStandIn()
    try:
        yield stand_in
    finally:
        stand_in.close()


@pytest.fixture(scope="session")
def gov_check_here(code_under_test):
    """One ``gov check --json`` in this worktree, against the store the lead built (about six minutes)."""
    done = support.run([sys.executable, "-c", support._GOV, "check", "--json"], cwd=support.REPO_ROOT,
                       env=support.worktree_env(), timeout=support.GOV_CHECK_TIMEOUT_S)
    return done, support.checks_of(done.envelope())
