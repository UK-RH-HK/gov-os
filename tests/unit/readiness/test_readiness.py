"""Builder tests for ``gov readiness`` (W1-13). Regression evidence only (DEC-136).

They cover what the acceptance tests leave to the builder: the rows, the mandatory rows and the capability-type
table held in the code are the contract's, the checker does not fail open on what it cannot read or what is not
declared, and a specification closed by hand still gets its one audit ticket. Every project is a temporary directory (DEC-322).
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov import readiness  # noqa: E402
from gov.cli.errors import GovError  # noqa: E402
from gov.readiness import checker  # noqa: E402

SPEC = "SPEC-zq13"
TEMPLATE = REPO / "template" / "openspec"


def _project(root, profile="FULL", capability_types=(), status="DRAFT", satisfied=True):
    shutil.copytree(TEMPLATE, root / "openspec")
    change = root / "openspec" / "changes" / "zq13-sample"
    change.mkdir(parents=True)
    rows = yaml.safe_load((TEMPLATE / "schemas/feature-readiness/templates/readiness.yaml").read_text())["rows"]
    if satisfied:
        rows = [{**row, "state": "PRESENT", "evidence": ["DEC-085"]} for row in rows]
    (change / "readiness.yaml").write_text(yaml.safe_dump({"rows": rows}), encoding="utf-8")
    (change / "proposal.md").write_text(
        f"---\nid: {SPEC}\ntype: specification\nstatus: {status}\nstate_class: AUTHORITATIVE\nprofile: {profile}\n"
        f"spine: false\ncapability_types: [{', '.join(capability_types)}]\n---\n# Proposal\n", encoding="utf-8")
    return root


def test_the_mandatory_rows_and_the_shipped_schema_are_the_contracts():
    contract = yaml.safe_load((REPO / "docs/contract/readiness-dimensions.yaml").read_text(encoding="utf-8"))
    schema = yaml.safe_load((TEMPLATE / "schemas/feature-readiness/schema.yaml").read_text(encoding="utf-8"))
    assert list(checker.MANDATORY) == contract["mandatory_rows"]
    assert checker.KEYS == {row["n"]: row["key"] for row in contract["dimensions"]}
    assert checker.EXTRA == {name: set(rows)
                             for name, rows in contract["capability_types"]["extra_rows_for_standard"].items()}
    assert set(checker.STATES) == {state["state"] for state in contract["cell_states"]}
    assert set(checker.SATISFIED) == {state["state"] for state in contract["cell_states"] if state["satisfies"]}
    assert {row["n"]: row["key"] for row in schema["dimensions"]} \
        == {row["n"]: row["key"] for row in contract["dimensions"]}


def test_a_project_without_the_schema_does_not_pass(tmp_path):
    root = _project(tmp_path)
    assert readiness.check(root, SPEC)["closed"] is True
    shutil.rmtree(root / "openspec" / "schemas")
    with pytest.raises(GovError) as caught:
        readiness.check(root, SPEC)
    assert caught.value.code == checker.INVALID


def test_a_schema_that_adds_a_row_or_a_type_does_not_pass(tmp_path):
    root = _project(tmp_path)
    path = root / "openspec" / "schemas" / "feature-readiness" / "schema.yaml"
    shipped = yaml.safe_load(path.read_text(encoding="utf-8"))
    table = shipped["capability_types"]["extra_rows_for_standard"]
    for edited in ({**shipped, "dimensions": [*shipped["dimensions"], {"n": 27, "key": "more"}]},
                   {**shipped, "capability_types": {"extra_rows_for_standard": {**table, "blockchain": []}}}):
        path.write_text(yaml.safe_dump(edited), encoding="utf-8")
        with pytest.raises(GovError) as caught:
            readiness.check(root, SPEC)
        assert caught.value.code == checker.INVALID


def test_a_change_with_no_specification_record_is_invalid_and_the_archive_is_not_a_change(tmp_path):
    root = _project(tmp_path)
    (root / "openspec" / "changes" / "archive" / "zq11-old").mkdir(parents=True)
    assert readiness.check_all(root)["closed"] is True
    (root / "openspec" / "changes" / "zq12-bare").mkdir()
    with pytest.raises(GovError) as caught:
        readiness.check_all(root)
    assert (caught.value.code, caught.value.exit_code) == (checker.INVALID, 1)
    assert "zq12-bare" in caught.value.message
    assert [report.get("specification", report.get("change")) for report in caught.value.details["specifications"]] \
        == [SPEC, "zq12-bare"]


def test_a_standard_specification_with_no_capability_type_does_not_pass(tmp_path):
    with pytest.raises(GovError) as caught:
        readiness.check(_project(tmp_path, profile="STANDARD"), SPEC)
    assert caught.value.code == checker.INVALID


def test_the_bare_command_does_not_pass_while_one_specification_is_open(tmp_path):
    with pytest.raises(GovError) as caught:
        readiness.check_all(_project(tmp_path, satisfied=False))
    assert (caught.value.code, caught.value.exit_code) == (checker.NOT_CLOSED, checker.EXIT_OPEN)
    assert [report["specification"] for report in caught.value.details["specifications"]] == [SPEC]


def test_a_specification_closed_by_hand_still_gets_its_one_audit_ticket(tmp_path):
    root = _project(tmp_path, status="CLOSED")
    script = root / "governance" / "kernel" / "bin" / "tk"
    script.parent.mkdir(parents=True)
    shutil.copyfile(REPO / "template" / "governance" / "kernel" / "bin" / "tk", script)
    script.chmod(0o755)
    first, second = readiness.close(root, SPEC), readiness.close(root, SPEC)
    assert first["audit_ticket"] and second["audit_ticket"] == first["audit_ticket"]
    assert [path.stem for path in (root / ".tickets").glob("*.md")] == [first["audit_ticket"]]
