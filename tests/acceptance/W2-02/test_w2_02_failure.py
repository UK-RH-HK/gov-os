"""KPI failure line [W2-M138]: an audit report missing its milestone or pack hash is invalid; a record with an
unknown type is still ``SCHEMA_INVALID_TYPE``.

Measured before the ticket: core-schema answers ``SCHEMA_INVALID_TYPE`` for a record whose ``type`` is missing or
no text, and ``SCHEMA_UNKNOWN_TYPE`` for a record whose type it does not know (both held by W1-26's and W1-30's
suites). Which code "an unknown type" keeps is package P-4; the case here holds what both readings share.
"""

from __future__ import annotations

import pytest

import w2_02_support as support


@pytest.fixture
def project(tmp_path):
    made = support.Project(tmp_path)
    made.kernel_schemas()
    return made


@pytest.mark.parametrize("field", support.AUDIT_FIELDS)
def test_an_audit_report_missing_a_field_of_dec_441_is_refused_on_that_field(project, field):
    """W2-M138: without ``milestone`` or ``pack_sha256`` (and, DEC-441's third field, ``commit``): a finding on
    the report names the field it lacks, and the check is not green.
    Red today: the one finding is ``SCHEMA_INVALID_TYPE`` ('type' field is missing), which names no such field."""
    head = project.commit("initial")
    rel = project.write(support.AUDIT_REPORT_REL, support.audit_report(head, leave_out=(field,)))
    code, findings = project.core_schema()
    found = [finding for finding in support.about(findings, rel) if support.names_field(finding, field)]
    assert found, f"an audit report without {field!r} is not refused on it: {support.about(findings, rel)}"
    assert code != 0, f"core-schema is green on an audit report without {field!r}"


def test_an_audit_report_missing_both_milestone_and_pack_hash_names_both(project):
    """Both missing: each named. Red today, as above."""
    head = project.commit("initial")
    rel = project.write(support.AUDIT_REPORT_REL, support.audit_report(head, leave_out=("milestone", "pack_sha256")))
    _, findings = project.core_schema()
    found = support.about(findings, rel)
    for field in ("milestone", "pack_sha256"):
        assert any(support.names_field(finding, field) for finding in found), \
            f"an audit report without milestone and pack_sha256 is not refused on {field!r}: {found}"


def test_a_record_with_an_unknown_type_is_still_refused(project):
    """``type: frobnicate``, the shared frontmatter otherwise whole: a finding on the file whose code is the
    check's code for a type it cannot use (``SCHEMA_UNKNOWN_TYPE`` today, ``SCHEMA_INVALID_TYPE`` as the KPI line
    words it; P-4), never "unmeasured", and the check is not green. Passes today ("still")."""
    rel = project.write("docs/notes/ZZ-0001.md", support.markdown(support.shared("ZZ-0001", "frobnicate")))
    code, findings = project.core_schema()
    found = support.about(findings, rel)
    assert [finding.get("code") for finding in found if finding.get("code") in
            (support.UNKNOWN_TYPE, support.INVALID_TYPE)], f"a record of type frobnicate is not refused: {found}"
    assert not any(support.says_unmeasured(finding) for finding in found), \
        f"a record of a type nobody knows is reported unmeasured: {found}"
    assert code != 0


@pytest.mark.parametrize("type_value", (None, ["decision"]), ids=("missing", "a-list"))
def test_a_record_whose_type_is_missing_or_no_text_is_still_schema_invalid_type(project, type_value):
    """A record (``id``, ``status``, ``state_class``) outside the audit folder whose ``type`` is missing or a
    list: ``SCHEMA_INVALID_TYPE`` on the file. Passes today ("still"): the audit report's form, which has no
    ``type``, does not open a way round it elsewhere."""
    front = support.shared("ZZ-0002", "placeholder")
    if type_value is None:
        del front["type"]
    else:
        front["type"] = type_value
    rel = project.write("docs/notes/ZZ-0002.md", support.markdown(front))
    code, findings = project.core_schema()
    found = support.about(findings, rel)
    assert support.INVALID_TYPE in [finding.get("code") for finding in found], \
        f"a record whose type is {type_value!r} is not SCHEMA_INVALID_TYPE: {found}"
    assert code != 0
