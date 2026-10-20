"""Unit tests for core-schema's audit-report type (W2-54, DEC-768 item 1; DEC-441, DEC-565, DEC-626)."""
from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from gov.check import schema

REPO = Path(__file__).resolve().parents[3]
REPORT = "---\nmilestone: wave-1-exit\ncommit: 60ea6924\npack_sha256: 2355ce5f\n---\n\n# An audit\n"


@pytest.fixture
def project(tmp_path):
    schemas = tmp_path / schema.SCHEMA_DIR
    schemas.mkdir(parents=True)
    for name in ("common.schema.json", "audit-report.schema.json"):
        shutil.copyfile(REPO / schema.SCHEMA_DIR / name, schemas / name)
    return tmp_path


def _write(root, rel, text):
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_a_typeless_record_in_the_audit_folder_is_an_audit_report(project):
    _write(project, "docs/audit/wave-1/report.md", REPORT)
    assert schema.check(project) == []


def test_a_record_stating_type_audit_report_is_held_to_the_schema(project):
    _write(project, "docs/notes/report.md", REPORT.replace("---\n", "---\ntype: audit-report\n", 1))
    assert schema.check(project) == []


@pytest.mark.parametrize("field", ("milestone", "commit", "pack_sha256"))
def test_an_audit_report_lacking_a_field_fails_naming_it(project, field):
    text = "\n".join(line for line in REPORT.split("\n") if not line.startswith(f"{field}:"))
    _write(project, "docs/audit/report.md", text)
    findings = schema.check(project)
    assert [(f["code"], f.get("field")) for f in findings] == [("SCHEMA_MISSING_FIELD", field)]


def test_a_commit_of_the_wrong_shape_fails(project):
    _write(project, "docs/audit/report.md", REPORT.replace("60ea6924", "not-a-commit"))
    assert [(f["code"], f.get("field")) for f in schema.check(project)] == [("SCHEMA_INVALID_FIELD", "commit")]


@pytest.mark.parametrize("folder", ("docs/notes", "docs/audit-archive", "docs/reports/audit"))
def test_a_typeless_record_outside_the_audit_folder_still_fails(project, folder):
    _write(project, f"{folder}/report.md", REPORT)
    assert [f["code"] for f in schema.check(project)] == ["SCHEMA_INVALID_TYPE"]


def test_the_other_types_of_w2_02_stay_unknown():
    assert "close" not in schema.SCHEMA_MAP and "adoption-verdict" not in schema.SCHEMA_MAP
    assert schema.STANDALONE_TYPES == ("probe", "audit-report")
