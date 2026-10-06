"""Unit tests for governance check modules (W1-26)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.check import runner  # noqa: E402


def _write(root, rel, text):
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _git_init(root):
    subprocess.run(["git", "init", "-q", "-b", "main", str(root)],
                   capture_output=True, check=True)
    env = {"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null",
           "GIT_AUTHOR_NAME": "Test", "GIT_AUTHOR_EMAIL": "t@t",
           "GIT_COMMITTER_NAME": "Test", "GIT_COMMITTER_EMAIL": "t@t",
           "PATH": subprocess.check_output(["bash", "-c", "echo $PATH"]).decode().strip(),
           "HOME": str(root.parent), "LC_ALL": "C"}
    return env


def _commit(root, env, message="fixture"):
    subprocess.run(["git", "-C", str(root), "add", "-A"],
                   capture_output=True, check=True, env=env)
    subprocess.run(["git", "-C", str(root), "commit", "-q", "--allow-empty", "-m", message],
                   capture_output=True, check=True, env=env)


# --------------------------------------------------------------------------
# runner: FAMILIES tuple
# --------------------------------------------------------------------------

def test_families_count():
    assert len(runner.FAMILIES) == 17


def test_families_unique():
    assert len(set(runner.FAMILIES)) == 17


# --------------------------------------------------------------------------
# runner: _provenance
# --------------------------------------------------------------------------

def test_provenance_fields():
    prov = runner._provenance("test-check", "abc123", "1.0.0")
    assert prov["commit"] == "abc123"
    assert prov["check_version"] == "1.0.0"
    assert len(prov["inputs_hash"]) == 16


def test_provenance_deterministic():
    p1 = runner._provenance("x", "abc", "1.0")
    p2 = runner._provenance("x", "abc", "1.0")
    assert p1["inputs_hash"] == p2["inputs_hash"]


def test_provenance_different_inputs():
    p1 = runner._provenance("x", "abc", "1.0")
    p2 = runner._provenance("y", "abc", "1.0")
    assert p1["inputs_hash"] != p2["inputs_hash"]


# --------------------------------------------------------------------------
# runner: _inputs_hash
# --------------------------------------------------------------------------

def test_inputs_hash_length():
    assert len(runner._inputs_hash("check", "commit")) == 16


# --------------------------------------------------------------------------
# schema check
# --------------------------------------------------------------------------

def test_schema_clean_record(tmp_path):
    from gov.check.schema import check
    root = tmp_path / "project"
    _write(root, ".tickets/T-001.md",
           "---\nid: T-001\ntype: task\nstatus: open\nstate_class: AUTHORITATIVE\n---\n# T-001\n")
    assert check(root) == []


def test_schema_missing_fields(tmp_path):
    from gov.check.schema import check
    root = tmp_path / "project"
    _write(root, ".tickets/T-BAD.md",
           "---\nid: T-BAD\ntype: task\n---\n# T-BAD\n")
    findings = check(root)
    assert len(findings) > 0
    codes = {f["code"] for f in findings}
    assert "SCHEMA_MISSING_FIELD" in codes


# --------------------------------------------------------------------------
# graph check
# --------------------------------------------------------------------------

def test_graph_clean(tmp_path):
    from gov.check.graph import check
    root = tmp_path / "project"
    _write(root, "docs/adr/DEC-001.md",
           "---\nid: DEC-001\ntype: decision\nstatus: ACTIVE\nstate_class: AUTHORITATIVE\n---\n")
    assert check(root) == []


def test_graph_duplicate_id(tmp_path):
    from gov.check.graph import check
    root = tmp_path / "project"
    _write(root, "docs/adr/DEC-001.md",
           "---\nid: DEC-001\ntype: decision\nstatus: ACTIVE\nstate_class: AUTHORITATIVE\n---\n")
    _write(root, "docs/adr/DEC-001-copy.md",
           "---\nid: DEC-001\ntype: decision\nstatus: ACTIVE\nstate_class: AUTHORITATIVE\n---\n")
    findings = check(root)
    codes = {f["code"] for f in findings}
    assert "DUPLICATE_ID" in codes


def test_graph_dangling_reference(tmp_path):
    from gov.check.graph import check
    root = tmp_path / "project"
    _write(root, "docs/adr/DEC-001.md",
           "---\nid: DEC-001\ntype: decision\nstatus: ACTIVE\nstate_class: AUTHORITATIVE\n"
           "depends_on: DEC-999\n---\n")
    findings = check(root)
    codes = {f["code"] for f in findings}
    assert "DANGLING_REFERENCE" in codes


# --------------------------------------------------------------------------
# authority check
# --------------------------------------------------------------------------

def test_authority_clean(tmp_path):
    from gov.check.authority import check
    root = tmp_path / "project"
    _write(root, "docs/adr/DEC-001.md",
           "---\nid: DEC-001\ntype: decision\nstatus: ACTIVE\nstate_class: AUTHORITATIVE\n---\n")
    assert check(root) == []


# --------------------------------------------------------------------------
# mutation check
# --------------------------------------------------------------------------

def test_mutation_clean(tmp_path):
    from gov.check.mutation import check
    root = tmp_path / "project"
    _write(root, ".tickets/W1-01.md",
           "---\nid: W1-01\ntype: task\nstatus: open\nstate_class: AUTHORITATIVE\n"
           "role: engineer\nallowed_paths:\n- src/**\nkpis:\n  success: [works]\n  failure: []\n---\n")
    assert check(root) == []


def test_mutation_acceptance_in_allowed(tmp_path):
    from gov.check.mutation import check
    root = tmp_path / "project"
    _write(root, ".tickets/W1-BAD.md",
           "---\nid: W1-BAD\ntype: task\nstatus: open\nstate_class: AUTHORITATIVE\n"
           "role: engineer\nallowed_paths:\n- tests/acceptance/**\n"
           "kpis:\n  success: [works]\n  failure: []\n---\n")
    findings = check(root)
    codes = {f["code"] for f in findings}
    assert "IMPLEMENTER_COVERS_ACCEPTANCE" in codes


# --------------------------------------------------------------------------
# commands check
# --------------------------------------------------------------------------

def test_commands_check(tmp_path):
    from gov.check.commands import check
    root = tmp_path / "project"
    for cmd in ("status", "check", "readiness"):
        _write(root, f"src/gov/cli/commands/{cmd}.py", f"# {cmd}\n")
    findings = check(root)
    assert len(findings) > 0


# --------------------------------------------------------------------------
# claims check: ticket DAG
# --------------------------------------------------------------------------

def test_claims_clean(tmp_path):
    from gov.check.claims import check
    root = tmp_path / "project"
    _write(root, ".tickets/T-001.md",
           "---\nid: T-001\ntype: task\nstatus: open\nstate_class: AUTHORITATIVE\n"
           "role: engineer\nallowed_paths:\n- src/**\nkpis:\n  success: [works]\n  failure: []\n---\n")
    assert check(root) == []


def test_claims_missing_ticket_field(tmp_path):
    from gov.check.claims import check
    root = tmp_path / "project"
    _write(root, ".tickets/T-BAD.md",
           "---\nid: T-BAD\ntype: task\nstatus: open\n---\n# T-BAD\n")
    findings = check(root)
    codes = {f["code"] for f in findings}
    assert "TICKET_MISSING_FIELD" in codes


# --------------------------------------------------------------------------
# pathmap check
# --------------------------------------------------------------------------

def test_pathmap_no_pathmap(tmp_path):
    from gov.check.pathmap import check
    root = tmp_path / "project"
    assert check(root) == []


# --------------------------------------------------------------------------
# run_checks integration
# --------------------------------------------------------------------------

def test_run_checks_returns_families_and_checks(tmp_path):
    import shutil
    root = tmp_path / "project"
    env = _git_init(root)
    _write(root, "README.md", "# Test\n")
    shutil.copytree(REPO / "src", root / "src")
    checks_src = REPO / "template" / "governance" / "kernel" / "checks"
    if checks_src.is_dir():
        shutil.copytree(checks_src, root / "template" / "governance" / "kernel" / "checks")
    _commit(root, env, "initial")
    result, has_hard_block = runner.run_checks(root)
    assert "families" in result
    assert "checks" in result
    families = result["families"]
    assert len(families) == 17
    for fam_name in runner.FAMILIES:
        assert fam_name in families
        assert families[fam_name]["status"] in ("RED", "YELLOW", "GREEN")
