"""Fixtures for the W2-37 acceptance tests (``gov impact``)."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_37_support as support  # noqa: E402

INDEXED_ROOTS = set()


def pytest_configure(config):
    config.addinivalue_line("markers", "local_only: runs the codebase-memory and gitleaks binaries; not for CI, "
                                       "and not inside a worker's sandbox (P-W2-38)")


@pytest.fixture(scope="session")
def box(tmp_path_factory):
    """HOME, TMPDIR, a working directory and a PATH with ``git`` alone, outside any repository."""
    made = support.make_box(tmp_path_factory.mktemp("w2-37-box"))
    yield made
    support.remove_daemon_dirs(made, INDEXED_ROOTS)


@pytest.fixture(scope="session")
def built(box):
    """``gov impact``, once the ticket has built it; every case of the command fails here until then."""
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
    return support.build_fixture(tmp_path_factory.mktemp("w2-37-base") / "repo")


@pytest.fixture(scope="session")
def graph(built, base, box, tmp_path_factory):
    """A clone with its store loaded once. Cases only ask of it, with ``git`` alone on PATH."""
    root = support.clone(base, tmp_path_factory.mktemp("w2-37-graph") / "repo")
    support.load_store(root, box)
    return root


@pytest.fixture(scope="session")
def asked(graph, box):
    """``asked(change)``: the checked assessment of ``gov impact --json <change>`` in ``graph``, asked once."""
    kept = {}

    def get(change):
        key = change if isinstance(change, str) else tuple(change)
        if key not in kept:
            kept[key] = support.ask(graph, change, box)
        return kept[key]

    return get


@pytest.fixture()
def repo(built, base, box, tmp_path):
    """This case's own clone of the fixture repository, with its store loaded."""
    root = support.clone(base, tmp_path / "repo")
    support.load_store(root, box)
    return root


@pytest.fixture()
def project(repo):
    """This case's own clone, as a Project the case can write and commit in."""
    made = support.Project.__new__(support.Project)
    made.root, made.minute = repo, 100
    return made


# --------------------------------------------------------------------------
# The code side: the real tool, in temporary repositories only
# --------------------------------------------------------------------------

@pytest.fixture(scope="session")
def tools():
    """The codebase-memory and gitleaks binaries. Nothing is installed: without them the case is skipped."""
    for name in (support.TOOL, "gitleaks"):
        if shutil.which(name) is None:
            pytest.skip(f"{name} is not on PATH on this machine")


@pytest.fixture(scope="session")
def code_base(tmp_path_factory):
    """The fixture repository with the code, its test and the adoption files. Never loaded or indexed."""
    return support.build_fixture(tmp_path_factory.mktemp("w2-37-code-base") / "repo", code=True)


def _indexed_clone(code_base, box, destination):
    root = support.clone(code_base, destination)
    support.load_store(root, box)
    INDEXED_ROOTS.add(str(root))
    support.build_index(root, box)
    for name, callers in support.CALLERS.items():   # the premise: the index sees the calls the source makes
        found = support.call("gov.codeintel", "callers", root, box, name, path=box.full)
        names = sorted(str(entry.get("name", entry)) if isinstance(entry, dict) else str(entry)
                       for entry in (found or []))
        for caller in callers:
            assert any(support.names_symbol(n, caller) for n in names), \
                f"the fixture is wrong: the code index does not see {caller} call {name} ({names})"
    return root


@pytest.fixture(scope="session")
def indexed(built, tools, code_base, box, tmp_path_factory):
    """A clone with its store loaded and its code index built. Cases only ask of it, with the session's PATH."""
    return _indexed_clone(code_base, box, tmp_path_factory.mktemp("w2-37-indexed") / "repo")


@pytest.fixture(scope="session")
def asked_code(indexed, box):
    """``asked_code(change)``: the checked assessment in ``indexed`` with the code tool on PATH, asked once."""
    kept = {}

    def get(change):
        key = change if isinstance(change, str) else tuple(change)
        if key not in kept:
            kept[key] = support.ask(indexed, change, box, path=box.full)
        return kept[key]

    return get


@pytest.fixture()
def indexed_own(built, tools, code_base, box, tmp_path):
    """This case's own indexed clone."""
    return _indexed_clone(code_base, box, tmp_path / "repo")
