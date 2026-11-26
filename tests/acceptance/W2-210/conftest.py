"""Fixtures for the W2-210 acceptance tests: two adopted projects, built once per run and copied by each case."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
for _folder in (_HERE.parent / "W1-07", _HERE.parent / "W1-41", _HERE.parent / "W2-52", _HERE.parent / "W2-81", _HERE):
    if str(_folder) not in sys.path:
        sys.path.insert(0, str(_folder))

import w2_210_support as d1  # noqa: E402

gates = d1.gates


@pytest.fixture(scope="session", autouse=True)
def _code_graph_tool_on_path():
    """The build's A3 and A6 need the code-graph tool; the repository's ``tests/conftest.py`` keeps it off ``PATH`` for
    every suite not in its ``_CBM_SUITES`` (this folder is not, yet). The children the cases start get it back, at the
    end of their ``PATH``; nothing else changes."""
    patch = pytest.MonkeyPatch()
    original = d1.support.environment

    def environment(sandbox, without=()):
        env = original(sandbox, without)
        env["PATH"] = d1.with_code_graph(env["PATH"])
        return env
    patch.setattr(d1.support, "environment", environment)
    yield
    patch.undo()


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
    """A folder linking the installed ``sqlite_vec``; the build needs it (the lite A10 gate's canary)."""
    site = gates.vector_site(tmp_path_factory.mktemp("vector-site"))
    if site is None:
        pytest.skip("sqlite_vec is not installed: the lite A10 gate's semantic canary cannot hit, so no adoption "
                    "can be built to give a verdict on")
    return site


@pytest.fixture(scope="session")
def adopted_snapshot(tmp_path_factory, interface, stand_in, vector_site):
    """The harbour adopted through A0 to A8 and both gates (with the Independent Auditor's records) and one closed
    ticket: every condition the stage reads from records is met."""
    return d1.shared_build(
        tmp_path_factory, "adopted",
        lambda folder: d1.build_adopted(folder, interface, stand_in.host, vector_site))


@pytest.fixture(scope="session")
def native_snapshot(tmp_path_factory, interface, stand_in, vector_site):
    """The same adoption whose A3 record holds a move out of the native layout without both grounds."""
    return d1.shared_build(
        tmp_path_factory, "native",
        lambda folder: d1.build_adopted(folder, interface, stand_in.host, vector_site, native_without_grounds=True))


@pytest.fixture()
def adopted(adopted_snapshot, tmp_path, interface, stand_in, vector_site):
    """A copy of the adopted project for one case."""
    return gates.copy_adoption(adopted_snapshot, tmp_path, interface, endpoint=stand_in.host, site=vector_site)


@pytest.fixture()
def native_copy(native_snapshot, tmp_path, interface, stand_in, vector_site):
    return gates.copy_adoption(native_snapshot, tmp_path, interface, endpoint=stand_in.host, site=vector_site)


# --------------------------------------------------------------------------
# The real command line, on the adopted project (the live tools: not green on the harbour)
# --------------------------------------------------------------------------

def _copy_of(outcome_or_ad, destination, interface, stand_in, vector_site):
    ad = outcome_or_ad.ad if hasattr(outcome_or_ad, "ad") else outcome_or_ad
    return gates.copy_adoption(gates.Snapshot(ad.project, dict(ad.stages)), destination, interface,
                               endpoint=stand_in.host, site=vector_site)


@pytest.fixture(scope="session")
def cli_plain(adopted_snapshot, tmp_path_factory, interface, stand_in, vector_site):
    """``gov adopt --lite --stage VERDICT`` run once for real (no exceptions file) on a copy of the adopted project:
    the live ``gov doctor`` and ``gov check`` are not green there. Read-only for the cases; a case that changes
    something copies ``outcome.project`` with ``copy_of``."""
    ad = gates.copy_adoption(adopted_snapshot, tmp_path_factory.mktemp("cli-plain"), interface,
                             endpoint=stand_in.host, site=vector_site)
    return d1.run_stage(ad)


@pytest.fixture(scope="session")
def cli_owner(cli_plain, tmp_path_factory, interface, stand_in, vector_site):
    """The stage run again, after the owner committed an exceptions file naming each condition the first run found
    not met (the tool conditions where the first run left no record): the record is replaced."""
    ad = _copy_of(cli_plain, tmp_path_factory.mktemp("cli-owner"), interface, stand_in, vector_site)
    try:
        front, _ = d1.record_at_head(ad.project)
        names = [name for name, state in d1.record_states(front).items() if state == "not met"]
    except (AssertionError, KeyError, TypeError):
        names = list(d1.TOOL_CONDITIONS)
    before = d1.last_commit(ad.project, d1.VERDICT_REL) or None
    d1.write_exceptions(ad.project, d1.accept(*names), "owner")
    outcome = d1.run_stage(ad)
    outcome.names, outcome.earlier_commit = names, before
    return outcome


@pytest.fixture()
def copy_of(interface, stand_in, vector_site):
    """A copy of a project the session fixtures left (``outcome.project`` or an adoption), for one case."""
    def make(source, destination):
        return _copy_of(source, destination, interface, stand_in, vector_site)
    return make


@pytest.fixture(scope="session")
def ground(tmp_path_factory):
    """W2-81's proving ground at the self-tests' seed, built once (the judge's cases render stand-in adoptions)."""
    import shutil

    import w2_81_build as build
    from w2_81_words import DEFAULT_SEED

    run = tmp_path_factory.mktemp("w2-81-ground")
    built = build.build_all(run, DEFAULT_SEED, build.SELF_TEST_LARGE)
    yield built
    shutil.rmtree(run, ignore_errors=True)
