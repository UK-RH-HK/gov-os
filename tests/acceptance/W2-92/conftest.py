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
