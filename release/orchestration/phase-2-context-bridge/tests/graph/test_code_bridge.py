"""``govbridge.graph.code_bridge`` (routed issue B5/BR-AR-0007: "Code-derived edges (CALLS/READS_KEY/TESTS) are
on-demand, tested only on a B3-schema fixture. Wire them against the real B3 tables, so why/impact reach code."):
builds a shaped in-memory connection from the REAL, persisted code-route tables
(govbridge.code.store: code_symbol/code_call_site/code_literal) and proves govbridge.graph.derive's
callers_of/callees_of/reads_key_of/tests_of -- whose own schema/queries and existing frozen fixture test
(tests/graph/test_derive.py) are UNCHANGED -- see real hits through it. New test file."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))
import _repobuilder as rb  # noqa: E402

from govbridge.graph import code_bridge
from govbridge.graph import derive as D


@pytest.fixture(autouse=True)
def _isolated_store(tmp_path, monkeypatch):
    monkeypatch.setenv("GOVBRIDGE_STORE", str(tmp_path / "store"))
    monkeypatch.setenv("GOV_BRIDGE_HOME", str(tmp_path / "home"))


@pytest.fixture
def repo(tmp_path):
    root = tmp_path / "repo"
    rb.init(root)
    return root


def _write_fixture_crate(root) -> str:
    rb.write(root, "runtime/src/mod_a.rs", "pub fn exact_target() {}\n")
    rb.write(root, "runtime/src/mod_b.rs",
             "fn caller_exact() {\n    crate::mod_a::exact_target();\n}\n"
             "#[test]\nfn test_caller_exact() {\n    crate::mod_a::exact_target();\n}\n")
    rb.write(root, "runtime/src/tools.rs",
             "fn installation_authority(d: &D) {\n    if d.str(\"mutation\").as_str() == \"allowed\" {}\n}\n")
    return rb.commit(root, "fixture crate")


def test_shaped_connection_is_none_for_a_commit_with_no_rust(repo):
    rb.write(repo, "README.md", "no rust here\n")
    c1 = rb.commit(repo, "no rust")
    conn = code_bridge.build_shaped_code_connection(c1, repo=str(repo))
    assert conn is None


def test_callers_and_tests_reach_real_code_through_the_shaped_connection(repo):
    c1 = _write_fixture_crate(repo)
    conn = code_bridge.build_shaped_code_connection(c1, repo=str(repo))
    assert conn is not None

    callers = D.callers_of(conn, "exact_target")
    assert len(callers) == 2  # caller_exact and test_caller_exact
    caller_srcs = {e.src for e in callers}
    assert any("caller_exact" in s for s in caller_srcs)
    assert any("test_caller_exact" in s for s in caller_srcs)

    callees = D.callees_of(conn, "caller_exact")
    assert len(callees) == 1
    assert "exact_target" in callees[0].dst

    tests = D.tests_of(conn, "exact_target")
    assert len(tests) == 1
    assert "test_caller_exact" in tests[0].src


def test_reads_key_reaches_the_macro_token_literal(repo):
    c1 = _write_fixture_crate(repo)
    conn = code_bridge.build_shaped_code_connection(c1, repo=str(repo))
    assert conn is not None
    reads = D.reads_key_of(conn, "mutation")
    assert len(reads) == 1
    assert "installation_authority" in reads[0].src
