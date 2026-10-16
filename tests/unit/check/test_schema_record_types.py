"""Builder tests for W2-02's record types in core-schema: the audit-report folder, unmeasured types (regression
evidence only; the acceptance tests are tests/acceptance/W2-02/)."""
from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.check.schema import check  # noqa: E402

SCHEMAS_REL = "template/governance/kernel/schemas"
SHARED = "id: X-0001\nstatus: ACTIVE\nstate_class: AUTHORITATIVE\n"
REPORT = "milestone: wave-9-exit\ncommit: 0123456789abcdef0123456789abcdef01234567\npack_sha256: " + "a" * 64 + "\n"


def _write(root, rel, front):
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{front}---\n# A record\n", encoding="utf-8")
    return rel


def _project(tmp_path, *leave_out):
    for path in (REPO / SCHEMAS_REL).glob("*.schema.json"):
        if path.name not in leave_out:
            (tmp_path / SCHEMAS_REL).mkdir(parents=True, exist_ok=True)
            shutil.copy(path, tmp_path / SCHEMAS_REL / path.name)
    return tmp_path


def test_a_report_in_the_audit_folder_without_type_is_an_audit_report(tmp_path):
    root = _project(tmp_path)
    _write(root, "docs/audit/w9/report.md", REPORT)
    assert check(root) == []


def test_a_type_that_is_no_text_in_the_audit_folder_stays_invalid(tmp_path):
    rel = _write(_project(tmp_path), "docs/audit/w9/report.md", REPORT + "type: [audit-report]\n")
    assert [(f["code"], f["path"]) for f in check(tmp_path)] == [("SCHEMA_INVALID_TYPE", rel)]


def test_a_record_without_type_beside_the_audit_folder_stays_invalid(tmp_path):
    rel = _write(_project(tmp_path), "docs/auditing/report.md", REPORT)
    assert [(f["code"], f["path"]) for f in check(tmp_path)] == [("SCHEMA_INVALID_TYPE", rel)]


def test_an_audit_report_with_a_commit_that_is_no_commit_id_is_refused(tmp_path):
    _write(_project(tmp_path), "docs/audit/w9/report.md", REPORT.replace("0123456789abcdef", "HEAD~1", 1))
    assert [(f["code"], f["field"]) for f in check(tmp_path)] == [("SCHEMA_INVALID_FIELD", "commit")]


def test_a_shared_type_with_its_schema_absent_is_unmeasured_once(tmp_path):
    rel = _write(_project(tmp_path, "close.schema.json"), "docs/close/P-aaaa/CL-P-aaaa.md",
                 SHARED + "type: close\ntask: P-aaaa\n")
    assert [(f["code"], f["path"], f["type"]) for f in check(tmp_path)] == [("SCHEMA_UNREADABLE", rel, "close")]


def test_the_adoption_verdict_owes_the_shared_frontmatter(tmp_path):
    _write(_project(tmp_path), "docs/adoption/AV-0001.md", "id: AV-0001\ntype: adoption-verdict\n"
           "verdict: ADOPTED_HEALTHY\n")
    assert sorted(f["field"] for f in check(tmp_path)) == ["state_class", "status"]


def test_a_decision_entry_is_no_record_file_type(tmp_path):
    _write(_project(tmp_path), "docs/decisions/DEC-730.md", SHARED.replace("X-0001", "DEC-730")
           + "type: register-entry\nowner: owner\ndate: 2026-10-16\n")
    assert [f["code"] for f in check(tmp_path)] == ["SCHEMA_UNKNOWN_TYPE"]


def test_the_wbs_id_grammar_is_dec_730s():
    common = json.loads((REPO / SCHEMAS_REL / "common.schema.json").read_text(encoding="utf-8"))
    pattern = common["$defs"]["wbs_id"]["pattern"]
    assert pattern == "^W[0-9]+-[0-9]{2,}[a-z]?$"
    assert [bool(re.search(pattern, each)) for each in ("W2-15", "W2-15a", "W2-15ab")] == [True, True, False]
