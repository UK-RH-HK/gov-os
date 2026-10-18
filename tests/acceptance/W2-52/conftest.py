"""Fixtures for the W2-52 acceptance tests: two temporary projects, built once and copied by each case."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
for _folder in (_HERE.parent / "W1-07", _HERE.parent / "W1-41", _HERE):
    if str(_folder) not in sys.path:
        sys.path.insert(0, str(_folder))

import w2_52_support as gates  # noqa: E402


@pytest.fixture(scope="session")
def interface():
    """The envelope and the exit codes of API-0002, read from this worktree's interface file."""
    return gates.base.load_interface(gates.REPO_ROOT)


@pytest.fixture(scope="session")
def stand_in():
    """The stand-in embedding endpoint on a loopback port (no model)."""
    endpoint = gates.EmbeddingStandIn()
    try:
        yield endpoint
    finally:
        endpoint.close()


@pytest.fixture(scope="session")
def vector_site(tmp_path_factory):
    """A folder linking the installed ``sqlite_vec``; None where it is not installed."""
    return gates.vector_site(tmp_path_factory.mktemp("vector-site"))


@pytest.fixture(scope="session")
def after_a6(tmp_path_factory, interface, stand_in, vector_site):
    """The harbour project through A6: three move batches done, the legacy material still there (W1-41's stages,
    as built; the A5 verdict is the Independent Auditor's)."""
    folder = tmp_path_factory.mktemp("after-a6")
    project = gates.build_harbour(folder / "harbour")
    adoption = gates.GateAdoption(project, gates.support.make_sandbox(folder / "sandbox"), interface,
                                  endpoint=stand_in.host, site=vector_site)
    adoption.through("A6", gates.proposal())
    return gates.snapshot(adoption)


@pytest.fixture(scope="session")
def after_a8(tmp_path_factory, after_a6, interface, stand_in, vector_site):
    """The same project, A8 run straight after A6 (no A7 record: W2-24's fixture adoption, unchanged)."""
    adoption = gates.copy_adoption(after_a6, tmp_path_factory.mktemp("after-a8"), interface,
                                   endpoint=stand_in.host, site=vector_site)
    adoption.ok("A8")
    return gates.snapshot(adoption)


@pytest.fixture()
def a6_copy(after_a6, tmp_path, interface, stand_in, vector_site):
    """A copy of the project after A6, for one case."""
    return gates.copy_adoption(after_a6, tmp_path, interface, endpoint=stand_in.host, site=vector_site)


@pytest.fixture()
def a8_copy(after_a8, tmp_path, interface, stand_in, vector_site):
    """A copy of the project after A8, for one case."""
    return gates.copy_adoption(after_a8, tmp_path, interface, endpoint=stand_in.host, site=vector_site)


@pytest.fixture()
def needs_vectors(vector_site):
    """A case whose pass needs the semantic index built (and so ``sqlite_vec``)."""
    if vector_site is None:
        pytest.skip("sqlite_vec is not installed: the semantic index cannot be built, so its canary cannot hit")
