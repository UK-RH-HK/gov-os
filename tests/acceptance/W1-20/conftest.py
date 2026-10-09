"""Fixtures for the W1-20 acceptance tests."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w1_20_support as support  # noqa: E402


def pytest_configure(config):
    config.addinivalue_line("markers", "local_only: runs the codebase-memory and gitleaks binaries; not for CI")


@pytest.fixture(scope="session")
def box(tmp_path_factory):
    """HOME, TMPDIR, a working directory and a PATH with ``git`` alone, outside any repository."""
    made = support.make_box(tmp_path_factory.mktemp("w1-20-box"))
    yield made
    support.remove_daemon_dirs(made)


@pytest.fixture(scope="session")
def built(box):
    """``gov closure``, once the ticket has built it; every test fails here until then."""
    reason = None
    try:
        support.require_built(box)
    except support.Missing as exc:
        reason = str(exc)
    if reason:
        pytest.fail(reason, pytrace=False)


@pytest.fixture(scope="session")
def base(tmp_path_factory):
    """The fixture repository of records. Never loaded: it is the source of every clone."""
    return support.build_fixture(tmp_path_factory.mktemp("w1-20-base") / "repo")


@pytest.fixture(scope="session")
def graph(built, base, box, tmp_path_factory):
    """A clone of the fixture repository with its store loaded once. Tests only ask closures of it."""
    root = support.clone(base, tmp_path_factory.mktemp("w1-20-graph") / "repo")
    support.load_store(root, box)
    return root


@pytest.fixture()
def repo(built, base, box, tmp_path):
    """This test's own clone of the fixture repository, with its store loaded."""
    root = support.clone(base, tmp_path / "repo")
    support.load_store(root, box)
    return root


# --------------------------------------------------------------------------
# The code side: the real tool, in temporary repositories only
# --------------------------------------------------------------------------

@pytest.fixture(scope="session")
def tools():
    """The codebase-memory and gitleaks binaries. Nothing is installed by a test: without them the test is skipped."""
    for name in (support.TOOL, "gitleaks"):
        if shutil.which(name) is None:
            pytest.skip(f"{name} is not on PATH on this machine")


@pytest.fixture(scope="session")
def code_base(tmp_path_factory):
    """The fixture repository with the four functions and the adoption files. Never loaded or indexed."""
    return support.build_fixture(tmp_path_factory.mktemp("w1-20-code-base") / "repo", code=True)


@pytest.fixture(scope="session")
def indexed_wrapper(tools, code_base, box, tmp_path_factory):
    """A clone with its store loaded and its code index built. It does not need ``gov closure``."""
    root = support.clone(code_base, tmp_path_factory.mktemp("w1-20-premise") / "repo")
    support.load_store(root, box)
    support.build_index(root, box)
    return root


@pytest.fixture(scope="session")
def indexed(built, indexed_wrapper):
    """The indexed clone, for the tests of ``gov closure``. Tests only ask closures of it."""
    return indexed_wrapper


@pytest.fixture(scope="session")
def asked(box):
    """``asked(root, ids, depth)``: the checked result of ``gov closure --json --depth <depth> <ids>`` in ``root``
    with the session's own PATH, asked once per session and kept (DEC-561: a closure over code pays the code
    tool's start, about twelve seconds). For cases that ask the identical closure of a clone no case changes
    (``indexed``, ``draft``). A case that runs a closure on purpose, as the determinism case does, does not use
    it."""
    kept = {}

    def get(root, ids, depth):
        key = (str(root), tuple(ids), depth)
        if key not in kept:
            kept[key] = support.ask(root, list(ids), box, depth=depth, path=box.full)
        return kept[key]

    return get


@pytest.fixture(scope="session")
def draft(built, tools, code_base, box, tmp_path_factory):
    """A clone whose working tree holds an uncommitted function, indexed as it stands (DEC-344)."""
    root = support.clone(code_base, tmp_path_factory.mktemp("w1-20-draft") / "repo")
    support.load_store(root, box)
    path = root / support.CODE_REL
    path.write_text(path.read_text(encoding="utf-8") + support.DRAFT_CODE, encoding="utf-8")
    support.build_index(root, box)
    return root
