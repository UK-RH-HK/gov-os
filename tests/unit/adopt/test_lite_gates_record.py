"""Builder tests for the fix under W2-52 (DAEO-siiz): a verdict the A5, A7 or A10 gate accepts is a record the store reads.
Regression evidence only (MR-3). The helper is ``project.require_record``; the gates are held through W2-52's own builder
projects (``test_lite_gates``)."""
from __future__ import annotations

import pytest
import yaml

from gov.adopt import lite_gates, project
from gov.cli.errors import GovError

from .test_adopt import VERDICT, commit, planned, refused, root, stage, verdict, write
from .test_lite_gates import GATE_VERDICT, after_a6

__all__ = ["root"]


def test_a_head_with_id_type_and_status_is_a_record():
    project.require_record({"id": "AV-1", "type": "evidence", "status": "ACTIVE"}, "v.md")


def test_a_head_with_no_id_is_no_record_and_so_not_refused():
    project.require_record({"stage": "A5", "verdict": "pass"}, "v.md")


@pytest.mark.parametrize("head, keys", [
    ({"id": "AV-1", "type": "evidence"}, ["status"]),
    ({"id": "AV-1", "status": "ACTIVE"}, ["type"]),
    ({"id": "AV-1"}, ["type", "status"]),
    ({"id": "AV-1", "type": "", "status": "ACTIVE"}, ["type"]),
    ({"id": "AV-1", "type": "evidence", "status": 7}, ["status"]),
    ({"id": "AV-1", "type": ["evidence"], "status": ["x"]}, ["type", "status"]),
])
def test_an_id_without_a_string_type_or_status_is_refused_naming_the_file_and_keys(head, keys):
    with pytest.raises(GovError) as caught:
        project.require_record(head, "audit/v.md")
    assert caught.value.code == "ADOPT_VERDICT_NOT_A_RECORD"
    assert "audit/v.md" in caught.value.message and all(key in caught.value.message for key in keys)
    missing = ("type", "status")
    assert all((key in caught.value.message) == (key in keys) for key in missing)
    assert caught.value.details["keys"] == keys


def _a7_verdict(root, stage_given="A7", **drop):
    checked = [{"record": project.record_path(stage_),
                "sha256": project.sha256((root / project.record_path(stage_)).read_bytes())}
               for stage_ in lite_gates.CHECKED["A7"]]
    head = {"id": "AV-7", "type": "evidence", "status": "ACTIVE", "stage": stage_given, "verdict": "pass",
            "auditor_session": "auditor-7", "checked": checked}
    for key in drop:
        head.pop(key)
    write(root, GATE_VERDICT, "---\n" + yaml.safe_dump(head) + "---\n\n# AV-7\n")
    commit(root, "A7: the auditor's record", "Role: independent-auditor")


def test_the_a7_gate_refuses_a_verdict_with_an_id_and_no_status_and_writes_nothing(root):
    after_a6(root)
    _a7_verdict(root, status=None)
    before = project.tree(root)
    with pytest.raises(GovError) as caught:
        stage(root, "A7", verdict=GATE_VERDICT)
    assert caught.value.code == "ADOPT_VERDICT_NOT_A_RECORD" and GATE_VERDICT in caught.value.message
    assert project.tree(root) == before and project.dirty(root) == []


def test_the_a7_gate_keeps_its_own_refusal_first(root):
    after_a6(root)
    _a7_verdict(root, status=None, type=None, stage_given="A5")
    with pytest.raises(GovError) as caught:
        stage(root, "A7", verdict=GATE_VERDICT)
    assert caught.value.code == "ADOPT_VERDICT_OTHER_STAGE"


def test_the_a5_gate_refuses_a_verdict_with_an_id_and_no_type(root):
    planned(root)
    verdict(root)
    head = project.frontmatter((root / VERDICT).read_text(encoding="utf-8"))
    head.update({"id": "AV-5", "status": "ACTIVE"})
    head.pop("type", None)
    write(root, VERDICT, "---\n" + yaml.safe_dump(head) + "---\n\n# AV-5\n")
    commit(root, "A5: the auditor's record", "Role: independent-auditor")
    with pytest.raises(GovError) as caught:
        stage(root, "A5", verdict=VERDICT)
    assert caught.value.code == "ADOPT_VERDICT_NOT_A_RECORD" and "type" in caught.value.message
