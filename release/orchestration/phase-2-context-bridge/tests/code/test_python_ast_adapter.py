"""Tests for govbridge.code.adapters.python_ast: the reused code_intel plugin, run unmodified from its own Git
blob. These run against the real repository (not a synthetic fixture) because the plugin being wrapped --
capabilities/python/govos_capabilities/code_intel_python_ast.py -- only exists there; the point of this adapter is
precisely that it never copies that file, so there is no fixture copy of it to test against instead.
"""
from __future__ import annotations

import subprocess

from govbridge.code.adapters import python_ast


def _git(args):
    r = subprocess.run(["git", *args], capture_output=True, text=True, check=True)
    return r.stdout.strip()


def test_records_commit_resolves_to_a_real_commit():
    commit = python_ast.records_commit()
    assert len(commit) == 40
    assert _git(["cat-file", "-t", commit]) == "commit"


def test_plugin_blob_id_matches_git_directly():
    commit = python_ast.records_commit()
    expected = _git(["rev-parse", f"{commit}:capabilities/python/govos_capabilities/code_intel_python_ast.py"])
    assert python_ast.plugin_blob_id(commit=commit) == expected


def test_run_executes_the_unmodified_plugin_and_returns_its_shape():
    src = "def foo(x):\n    return bar(x)\n\nclass C:\n    def method(self):\n        return 1\n"
    result = python_ast.run(src, "demo.py")
    assert result["ok"] is True
    assert result["protocol"] == "gov-capability/1"
    outputs = result["outputs"]
    names = {s["name"] for s in outputs["symbols"]}
    assert {"foo", "C", "method"} <= names
    calls = {c["name"] for c in outputs["calls"]}
    assert "bar" in calls
    # blob id is recorded, and it is exactly the blob the plugin ran from
    commit = python_ast.records_commit()
    expected_blob = _git(["rev-parse", f"{commit}:capabilities/python/govos_capabilities/code_intel_python_ast.py"])
    assert result["blob"] == expected_blob
    assert result["commit"] == commit


def test_run_reports_syntax_error_without_crashing():
    result = python_ast.run("def broken(:\n", "broken.py")
    assert result["ok"] is True  # the plugin itself never crashes -- it reports ok_parse: False in outputs
    assert result["outputs"]["ok_parse"] is False
    assert result["outputs"]["error"]


def test_second_run_reuses_materialised_plugin_directory(tmp_path):
    # two calls with the same commit should not error and should agree byte-for-byte on the blob id used
    r1 = python_ast.run("x = 1\n", "a.py")
    r2 = python_ast.run("y = 2\n", "b.py")
    assert r1["blob"] == r2["blob"]
