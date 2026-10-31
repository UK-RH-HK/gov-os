"""Builder tests for the close schema's skips (DEC-954 ride-along): a skip's reason is a string that may be empty,
since pytest can report a skip with no reason; it stays required and a string (regression evidence only; the
acceptance tests are tests/acceptance/W2-64/)."""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.check.schema import check  # noqa: E402

SCHEMAS_REL = "template/governance/kernel/schemas"
RECORD = "docs/close/P-aaaa/CL-P-aaaa.md"
COMMIT = "0123456789abcdef0123456789abcdef01234567"


def _project(tmp_path):
    (tmp_path / SCHEMAS_REL).mkdir(parents=True)
    for path in (REPO / SCHEMAS_REL).glob("*.schema.json"):
        shutil.copy(path, tmp_path / SCHEMAS_REL / path.name)
    return tmp_path


def _close(root, skip):
    evidence = {"scope": "scoped", "why_full": [], "base": COMMIT, "head": COMMIT, "tree": COMMIT,
                "changed": ["src/a.py"], "selected": [], "left_out": [], "skips": [skip], "skip_count": 1,
                "failures": [], "junit_xml": [".gov-runtime/close/junit.xml"]}
    front = ("id: CL-P-aaaa\ntype: close\nstatus: ACTIVE\nstate_class: AUTHORITATIVE\ntask: P-aaaa\n"
             f"evidence: {json.dumps(evidence)}\n")
    path = root / RECORD
    path.parent.mkdir(parents=True)
    path.write_text(f"---\n{front}---\n# A close\n", encoding="utf-8")


def test_a_skip_with_an_empty_reason_validates(tmp_path):
    _close(_project(tmp_path), {"test": "tests/unit/test_a.py::test_one", "reason": ""})
    assert check(tmp_path) == []


def test_a_skip_with_a_reason_validates(tmp_path):
    _close(_project(tmp_path), {"test": "tests/unit/test_a.py::test_one", "reason": "needs a network"})
    assert check(tmp_path) == []


@pytest.mark.parametrize("skip", [{"test": "tests/unit/test_a.py::test_one"},
                                  {"test": "tests/unit/test_a.py::test_one", "reason": None},
                                  {"test": "tests/unit/test_a.py::test_one", "reason": 3}],
                         ids=["no-reason", "null-reason", "number-reason"])
def test_a_skip_without_a_string_reason_is_refused(tmp_path, skip):
    _close(_project(tmp_path), skip)
    findings = check(tmp_path)
    assert [(f["code"], f["path"], f["field"], f["schema"]) for f in findings] == [
        ("SCHEMA_INVALID_FIELD", RECORD, "evidence", "close.schema.json")]
    assert findings[0]["at"].startswith("$.evidence.skips[0]")


def test_a_skip_with_an_empty_test_stays_refused(tmp_path):
    _close(_project(tmp_path), {"test": "", "reason": ""})
    assert [(f["code"], f["field"]) for f in check(tmp_path)] == [("SCHEMA_INVALID_FIELD", "evidence")]


def test_only_the_skip_reason_is_relaxed():
    defs = json.loads((REPO / SCHEMAS_REL / "close.schema.json").read_text(encoding="utf-8"))["$defs"]
    skip = defs["evidence"]["properties"]["skips"]["items"]
    assert skip["required"] == ["test", "reason"]
    assert skip["properties"] == {"test": {"$ref": "#/$defs/text"}, "reason": {"type": "string"}}
    assert defs["reason"]["properties"]["reason"] == {"$ref": "#/$defs/text"}
    assert defs["evidence"]["properties"]["failures"]["items"]["properties"]["text"] == {"$ref": "#/$defs/text"}
