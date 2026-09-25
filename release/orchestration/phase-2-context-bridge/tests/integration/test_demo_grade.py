"""``govbridge.demo.grade`` (I1/BR-AR-0009, DAG node I1 acceptance check 7): "a passing fixture grades
DEMONSTRATION_PASS; fixtures for UPSTREAM_ONLY, each G3 hard fail and G7 undeclared reads each grade
DEMONSTRATION_FAIL with the right gate named."

Builds everything programmatically from the REAL compiler (``govbridge.compile.packet.compile_packet``) against
the existing ``tests/fixtures/compile/compile_repobuilder`` fixture (CX-* ids, never Review-8/Phase-2 content --
OC-BR-02), rather than hand-authoring static YAML that would have to guess at hashes/read-tokens: the oracle,
answers and receipt are constructed FROM the compiled packet's own manifest, so a "passing" fixture is provably
self-consistent, and each broken variant changes exactly one thing.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

FIXTURES_COMPILE = Path(__file__).resolve().parents[1] / "fixtures" / "compile"
sys.path.insert(0, str(FIXTURES_COMPILE))
import compile_repobuilder as repobuilder  # noqa: E402

from govbridge.compile import packet as packetmod
from govbridge.core.yamlutil import load_yaml_file
from govbridge.demo import grade as grademod
from govbridge.route.router import FAKE_ROUTES

FIXTURES_INTEGRATION = Path(__file__).resolve().parents[1] / "fixtures" / "integration"
QUERIES_PATH = str(FIXTURES_INTEGRATION / "demo-queries-synthetic.yaml")
ORACLE_PATH = str(FIXTURES_INTEGRATION / "oracle-synthetic.yaml")
ANSWERS_PASSING_PATH = str(FIXTURES_INTEGRATION / "answers-passing.yaml")
ANSWERS_UPSTREAM_ONLY_PATH = str(FIXTURES_INTEGRATION / "answers-upstream-only.yaml")
ANSWERS_G3_FAIL_PATH = str(FIXTURES_INTEGRATION / "answers-g3-fail.yaml")
READS_UNDECLARED_PATH = str(FIXTURES_INTEGRATION / "reads-undeclared.json")


@pytest.fixture(autouse=True)
def _no_env_leak(monkeypatch):
    monkeypatch.delenv("GOVBRIDGE_STORE", raising=False)


def _compile_fixture_packet(tmp_path):
    fixture_repo = repobuilder.build(tmp_path / "repo")
    view_path = tmp_path / "canonical-view.yaml"
    repobuilder.write_canonical_view(view_path, fixture_repo)
    registry_path = tmp_path / "authority-registry.yaml"
    repobuilder.write_registry(registry_path)
    task_spec = {
        "schema": "govbridge-task-spec/1", "task_id": "T-DEMO-GRADE", "role": "test",
        "objective": "demo grade fixture",
        "view": str(view_path),
        "required_inputs": [{"state_ref": "state:bridge#mandatory_bridge_inputs.items[*]", "reason": "test"}],
        "seeds": [], "queries": [],
        "mutation_scope": [], "prohibitions": [], "required_checks": [],
        "completion_vocabulary": ["ANSWERED"], "budget_profile": "bounded-builder",
    }
    result = packetmod.compile_packet(task_spec, routes=FAKE_ROUTES, repo=str(fixture_repo.root),
                                       registry_path=str(registry_path))
    assert result["status"] == packetmod.STATUS_OK
    return result, task_spec, str(fixture_repo.root)


def _write_packet_dir(tmp_path, name, result, task_spec):
    import yaml
    d = tmp_path / name
    d.mkdir()
    (d / "packet.md").write_text(result["rendered"], encoding="utf-8")
    (d / "manifest.json").write_text(json.dumps(result["manifest"], indent=1, sort_keys=True), encoding="utf-8")
    (d / "task_spec.yaml").write_text(yaml.safe_dump(task_spec, sort_keys=False), encoding="utf-8")
    meta = {"status": result["status"], "packet_id": result.get("packet_id"),
             "packet_sha256": result.get("packet_sha256"), "manifest_sha256": result.get("manifest_sha256"),
             "registry_path": result.get("registry_path")}
    (d / "meta.json").write_text(json.dumps(meta, indent=1, sort_keys=True), encoding="utf-8")
    return str(d)


def _valid_receipt(manifest: dict, packet_sha256: str) -> dict:
    m_sha = manifest["manifest_sha256"]
    read_tokens = {letter: hashlib.sha256((m_sha + letter).encode()).hexdigest()[:12]
                   for letter in "ABCDEFGHIJ"}
    a_rows = manifest["sections"]["A"]["items"]
    inputs_consumed = [f"{r['unit']['id']}@{r['content_sha256']}" for r in a_rows]
    items_relied_on = [r["item_id"] for r in a_rows[:1]]
    return {
        "context_packet_hash": [packet_sha256],
        "manifest_sha256": [m_sha],
        "read_tokens": read_tokens,
        "inputs_consumed": inputs_consumed,
        "items_relied_on": items_relied_on,
        "external_reads": [],
        "outputs_produced": [], "decisions_applied": [], "acceptance_evidence": [], "deviations": [],
        "unresolved": [],
    }


def _write_yaml(path: Path, doc: dict) -> str:
    import yaml
    path.write_text(yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")
    return str(path)


def test_passing_fixture_grades_demonstration_pass(tmp_path):
    result, task_spec, repo_root = _compile_fixture_packet(tmp_path)
    packet_dir = _write_packet_dir(tmp_path, "main", result, task_spec)
    receipt = _valid_receipt(result["manifest"], result["packet_sha256"])
    receipt_path = _write_yaml(tmp_path / "receipt.yaml", receipt)

    report = grademod.grade(oracle_path=ORACLE_PATH, answers_path=ANSWERS_PASSING_PATH, receipt_path=receipt_path,
                             packet_dirs=[packet_dir], queries_path=QUERIES_PATH, corpus_bytes=10_000_000,
                             repo=repo_root)
    assert report["verdict"] == "DEMONSTRATION_PASS", json.dumps(report, indent=1, default=str)
    for gate_name, gate in report["gates"].items():
        assert gate["result"] == "PASS", (gate_name, gate)


def test_upstream_only_enforcement_fails_the_chain(tmp_path):
    # answers-upstream-only.yaml cites ONLY the trap anchor (CX-DIRECTION) at the T-CHAIN-1 enforcement stage -- an
    # upstream representation, never the real enforcement point (CX-0010A) -- so the stage grades UPSTREAM_ONLY and
    # the WHOLE chain fails, "regardless of every other stage" (DEMONSTRATION_DESIGN.md section 4 G4, the
    # launcher's own rule).
    result, task_spec, repo_root = _compile_fixture_packet(tmp_path)
    packet_dir = _write_packet_dir(tmp_path, "main", result, task_spec)
    receipt = _valid_receipt(result["manifest"], result["packet_sha256"])
    receipt_path = _write_yaml(tmp_path / "receipt.yaml", receipt)

    report = grademod.grade(oracle_path=ORACLE_PATH, answers_path=ANSWERS_UPSTREAM_ONLY_PATH,
                             receipt_path=receipt_path, packet_dirs=[packet_dir], queries_path=QUERIES_PATH,
                             corpus_bytes=10_000_000, repo=repo_root)
    assert report["verdict"] == "DEMONSTRATION_FAIL"
    assert report["gates"]["G4_chains"]["result"] == "FAIL"
    stage = report["gates"]["G4_chains"]["chains"][0]["stages"][0]
    assert stage["grade"] == "UPSTREAM_ONLY"


def test_g3_hard_fail_when_a_decision_is_asserted_for_a_direction(tmp_path):
    # answers-g3-fail.yaml's T-CHAIN-1 answer_text asserts a decision has been made for a direction ("has been
    # authorised ... must be deleted") -- G3's mechanical phrase scan fails on this (DEMONSTRATION_DESIGN.md
    # section 4 G3: "the F1 direction is presented as a decision").
    result, task_spec, repo_root = _compile_fixture_packet(tmp_path)
    packet_dir = _write_packet_dir(tmp_path, "main", result, task_spec)
    receipt = _valid_receipt(result["manifest"], result["packet_sha256"])
    receipt_path = _write_yaml(tmp_path / "receipt.yaml", receipt)

    report = grademod.grade(oracle_path=ORACLE_PATH, answers_path=ANSWERS_G3_FAIL_PATH, receipt_path=receipt_path,
                             packet_dirs=[packet_dir], queries_path=QUERIES_PATH, corpus_bytes=10_000_000,
                             repo=repo_root)
    assert report["verdict"] == "DEMONSTRATION_FAIL"
    assert report["gates"]["G3_authority_classes"]["result"] == "FAIL"


def test_g7_fails_on_an_undeclared_read(tmp_path):
    result, task_spec, repo_root = _compile_fixture_packet(tmp_path)
    packet_dir = _write_packet_dir(tmp_path, "main", result, task_spec)
    receipt = _valid_receipt(result["manifest"], result["packet_sha256"])  # external_reads: []
    receipt_path = _write_yaml(tmp_path / "receipt.yaml", receipt)

    report = grademod.grade(oracle_path=ORACLE_PATH, answers_path=ANSWERS_PASSING_PATH, receipt_path=receipt_path,
                             packet_dirs=[packet_dir], queries_path=QUERIES_PATH, corpus_bytes=10_000_000,
                             reads_path=READS_UNDECLARED_PATH, repo=repo_root)
    assert report["verdict"] == "DEMONSTRATION_FAIL"
    assert report["gates"]["G7_no_dumping"]["result"] == "FAIL"
    assert report["gates"]["G7_no_dumping"]["undeclared_reads"]


def test_oracle_and_answers_fixtures_match_the_schemas():
    """A structural sanity check independent of grade(): the committed oracle/answers fixtures parse and carry the
    fields govbridge.demo.grade actually reads (belt-and-braces alongside the DAG's own `demo validate-oracle`,
    which this run's own scope tests only against a deliberately-invalid oracle -- see test_validate_oracle.py)."""
    oracle = load_yaml_file(ORACLE_PATH)
    assert oracle["schema"] == "govbridge-oracle/1"
    assert len(oracle["chains"]) == 1
    answers = load_yaml_file(ANSWERS_PASSING_PATH)
    assert {a["query_id"] for a in answers["answers"]} >= {"T-CHAIN-1", "T-SIDE-BY-SIDE", "T-BOTH-WAYS"}
