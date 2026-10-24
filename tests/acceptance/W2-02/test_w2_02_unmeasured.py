"""KPI success line 3 [W2-M260, W2-L177]: a type with no schema file is reported unmeasured, not green.

Measured before the ticket: in a project without a type's schema file, a well-formed record of that type gives no
finding and the check exits 0, as if it had been measured.
"""

from __future__ import annotations

import re

import pytest

import w2_02_support as support

# type -> (its schema file, where a record of it lies, the record's frontmatter)
RECORDS = {
    "research": ("research.schema.json", "docs/research/RES-0001.md",
                 support.shared("RES-0001", "research", status="ACCEPTED", state_class="EVIDENCE",
                                question="Does it hold?")),
    "close": (None, "docs/close/PROJ-aaaa/CL-PROJ-aaaa.md",
              support.shared("CL-PROJ-aaaa", "close", task="PROJ-aaaa")),
}


def _names_the_type(finding, record_type, rel):
    """The finding names the type itself: its ``type`` field, or its message once the record's own path is taken
    out (the path holds the type's folder name: ``docs/research/``, ``docs/close/``)."""
    if finding.get("type") == record_type:
        return True
    message = str(finding.get("message", "")).replace(rel, "")
    return re.search(rf"\b{re.escape(record_type)}\b", message) is not None


def _schema_file(record_type):
    name = RECORDS[record_type][0]
    if name is None:
        found = support.schemas_of_type(record_type)
        assert len(found) == 1, f"the kernel has {len(found)} schema files of type {record_type}; one is expected"
        name = next(iter(found))
    return name


@pytest.mark.parametrize("record_type", sorted(RECORDS))
def test_a_type_whose_schema_file_is_absent_is_reported_unmeasured_and_not_green(tmp_path, record_type):
    """Every kernel schema file but the type's own, and one record of the type: a finding says the type is
    unmeasured (code or message), names the type, and the check exits non-zero.
    Red today: ``research``: no finding, exit 0; ``close``: no kernel schema of type close (the case fails at
    finding it).

    Revised (W2-67, I4 §2.2 and F7): "names the type" was met by the record's own path in the message
    (``docs/research/…``, ``docs/close/…``), so a finding that named no type passed. The type is now looked for in
    the finding's ``type`` field, or in its message with the record's path taken out."""
    name = _schema_file(record_type)
    project = support.Project(tmp_path)
    project.kernel_schemas(leave_out=(name,))
    _, rel, front = RECORDS[record_type]
    assert record_type in rel, f"the premise: the record's path {rel} holds the type's name"
    project.write(rel, support.markdown(front))
    code, findings = project.core_schema()
    found = [finding for finding in findings if support.says_unmeasured(finding)
             and _names_the_type(finding, record_type, rel)]
    assert found, f"no finding says the type {record_type} is unmeasured: {findings}"
    assert code != 0, f"core-schema exits 0 although the type {record_type} is unmeasured"


def test_a_project_with_no_schema_file_at_all_is_not_green(tmp_path):
    """No schema file in the project, one research record: unmeasured, not green. Red today: no finding, exit 0."""
    project = support.Project(tmp_path)
    _, rel, front = RECORDS["research"]
    project.write(rel, support.markdown(front))
    code, findings = project.core_schema()
    assert any(support.says_unmeasured(finding) for finding in findings), \
        f"no finding says anything is unmeasured: {findings}"
    assert code != 0, "core-schema exits 0 in a project that holds no schema file"


def test_a_type_whose_schema_file_is_present_is_not_reported_unmeasured(tmp_path):
    """The converse: every kernel schema file and a well-formed research record: no finding says unmeasured.
    Passes today; held so the report is not given where the type is measured."""
    project = support.Project(tmp_path)
    project.kernel_schemas()
    _, rel, front = RECORDS["research"]
    project.write(rel, support.markdown(front))
    code, findings = project.core_schema()
    assert not [finding for finding in findings if support.says_unmeasured(finding)], findings
    assert code == 0, f"core-schema exits {code}: {findings}"
