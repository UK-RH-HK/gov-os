"""Fixtures for the W2-92 acceptance tests."""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_92_support as support  # noqa: E402


@pytest.fixture(scope="session")
def api(tmp_path_factory):
    if shutil.which("gitleaks") is None:
        pytest.skip("gitleaks is not on PATH on this machine: the lexical index's secret filter cannot run (DEC-287)")
    if support.real_tool() is None:
        pytest.skip(f"{support.TOOL} is not on PATH on this machine: the planted code index cannot be built")
    made = support.Api(tmp_path_factory.mktemp("w2-92-api"))
    yield made
    support.remove_daemon_dirs(made)


@pytest.fixture(scope="session")
def planted(api, tmp_path_factory):
    """``planted(kind)``: one project per kind, built once. ``full`` has the lexical index, the record graph and the
    code index; ``nocode`` has no code index; ``nostore`` has the lexical index and the code index but no record
    graph. A retrieval only reads, so the tests share them."""
    built = {}

    def make(kind):
        if kind not in built:
            root = support.build_project(tmp_path_factory.mktemp(f"w2-92-{kind}") / "repo")
            api.build(root, store=kind != "nostore", code=kind != "nocode")
            built[kind] = root
        return built[kind]

    return make


@pytest.fixture(scope="session")
def asked(api, planted):
    """``asked(kind, query, tool=RECORDING, **kwargs)``: ``(bundle, requests)``, asked once per session."""
    answers = {}

    def ask(kind, query, tool=support.RECORDING, **kwargs):
        key = (kind, query, tool, json.dumps(kwargs, sort_keys=True))
        if key not in answers:
            answers[key] = api.retrieve(planted(kind), query, tool=tool, **kwargs)
        return answers[key]

    return ask


# --------------------------------------------------------------------------
# S7 to S10 (DEC-1074 (5)): the marina, built by this worktree's code and by the integrated code
# --------------------------------------------------------------------------
# No code index and no code-graph tool: these cases run inside a worker's sandbox (gitleaks is needed for the
# lexical index's secret filter).

@pytest.fixture(scope="session")
def marina_api(tmp_path_factory):
    """This worktree's code."""
    if shutil.which("gitleaks") is None:
        pytest.skip("gitleaks is not on PATH on this machine: the lexical index's secret filter cannot run (DEC-287)")
    return support.AtSrc(tmp_path_factory.mktemp("w2-92-marina-api"))


@pytest.fixture(scope="session")
def marina_base_api(marina_api, tmp_path_factory):
    """The integrated code ``support.LINKS_BASE``, its ``src/`` taken from git into the session's folder."""
    place = tmp_path_factory.mktemp("w2-92-marina-base")
    return support.AtSrc(place / "api", src=support.base_src(place))


def _marina(api, place):
    root = support.build_links_project(place / "repo")
    api.build(root, store=True, code=False)
    return root


@pytest.fixture(scope="session")
def marina(marina_api, tmp_path_factory):
    """The marina, its lexical index and record store built by this worktree's code."""
    return _marina(marina_api, tmp_path_factory.mktemp("w2-92-marina"))


@pytest.fixture(scope="session")
def marina_at_base(marina_base_api, tmp_path_factory):
    """The same marina (the same commit), its lexical index and record store built by the integrated code."""
    return _marina(marina_base_api, tmp_path_factory.mktemp("w2-92-marina-at-base"))


@pytest.fixture(scope="session")
def marina_ask(marina_api, marina):
    """``marina_ask(query, **kwargs)``: this worktree's bundle, asked once per session."""
    answers = {}

    def ask(query, **kwargs):
        key = (query, json.dumps(kwargs, sort_keys=True))
        if key not in answers:
            answers[key] = marina_api.bundle(marina, query, **kwargs)
        return answers[key]

    return ask


@pytest.fixture(scope="session")
def marina_base_ask(marina_base_api, marina_at_base):
    """``marina_base_ask(query, **kwargs)``: the integrated code's bundle (today's), asked once per session."""
    answers = {}

    def ask(query, **kwargs):
        key = (query, json.dumps(kwargs, sort_keys=True))
        if key not in answers:
            answers[key] = marina_base_api.bundle(marina_at_base, query, **kwargs)
        return answers[key]

    return ask
