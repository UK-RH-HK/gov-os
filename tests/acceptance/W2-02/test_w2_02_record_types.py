"""KPI success line 1 [AR-1, AR-3, W2-M316, W2-M317, AR-9]: the kernel schemas define a decision entry, an audit
report in DEC-441's form, an adoption verdict (the three CAP-44.h verdicts) and the ``close`` record type that
``gov close`` writes. A defined type is one core-schema measures: a well-formed record of it passes, and a record
missing what the type requires is refused.

What package P-2 (the conditions of the adoption verdict) and P-3 (how a decision entry reaches the check) leave
open is not held here; see the README.
"""

from __future__ import annotations

import re

import pytest
import yaml

import w2_02_support as support


@pytest.fixture
def project(tmp_path):
    made = support.Project(tmp_path)
    made.kernel_schemas()
    return made


# --------------------------------------------------------------------------
# The audit report, DEC-441's form [AR-3, W2-M316]
# --------------------------------------------------------------------------

def test_an_audit_report_in_dec_441_form_passes_core_schema(project):
    """A report with ``milestone``, ``commit``, ``pack_sha256`` and its table, where audit reports lie, and no
    ``type`` key (DEC-441's form has none). Red today: ``SCHEMA_INVALID_TYPE`` ('type' field is missing)."""
    head = project.commit("initial")
    rel = project.write(support.AUDIT_REPORT_REL, support.audit_report(head))
    code, findings = project.core_schema()
    found = support.about(findings, rel)
    assert not found, f"an audit report in DEC-441's form is a finding: {found}"
    assert code == 0, f"core-schema exits {code} on a project whose one record is a well-formed audit report"


# --------------------------------------------------------------------------
# The adoption verdict, CAP-44.h [AR-9, W2-M317]
# --------------------------------------------------------------------------

def test_one_kernel_schema_states_the_three_verdicts_of_cap_44_h():
    """Exactly one kernel schema file has a property whose values are ADOPTED_HEALTHY,
    ADOPTED_WITH_ACCEPTED_EXCEPTIONS and NOT_ADOPTED_HEALTHY, and it says its record type.
    Red today: no schema file states them."""
    support.the_verdict_type()


def _verdict_record(record_type, field, value):
    front = support.shared("AV-0001", record_type, status="ACCEPTED", state_class="EVIDENCE")
    if value is not None:
        front[field] = value
    return support.markdown(front, "# The adoption verdict\n\nThe conditions behind it.\n")


@pytest.mark.parametrize("verdict", support.VERDICTS)
def test_each_of_the_three_verdicts_is_a_well_formed_verdict(project, verdict):
    """A verdict record with that verdict: no finding names the verdict field.
    Red today: no kernel schema states the verdicts (the case fails at finding the type)."""
    record_type, field = support.the_verdict_type()
    rel = project.write("docs/adoption/AV-0001.md", _verdict_record(record_type, field, verdict))
    _, findings = project.core_schema()
    found = [finding for finding in support.about(findings, rel) if support.names_field(finding, field)
             or finding.get("code") == support.UNKNOWN_TYPE]
    assert not found, f"the verdict {verdict} is refused: {found}"


@pytest.mark.parametrize("verdict", ("ADOPTED", "pass", "adopted_healthy", None),
                         ids=("not-one-of-the-three", "the-A5-word", "lower-case", "missing"))
def test_a_verdict_record_without_one_of_the_three_verdicts_is_refused(project, verdict):
    """A word outside the three, or no verdict at all: a finding on the file names the verdict field, and the
    check is not green. Red today: no kernel schema states the verdicts."""
    record_type, field = support.the_verdict_type()
    rel = project.write("docs/adoption/AV-0001.md", _verdict_record(record_type, field, verdict))
    code, findings = project.core_schema()
    found = [finding for finding in support.about(findings, rel) if support.names_field(finding, field)]
    assert found, f"a verdict record with verdict {verdict!r} is not refused on {field!r}: {findings}"
    assert code != 0, "core-schema is green on a verdict record without one of the three verdicts"


# --------------------------------------------------------------------------
# The decision entry [AR-1]
# --------------------------------------------------------------------------

DECISION_ENTRY_FIELDS = {"id", "status", "owner", "date"}


def _decision_entry_schemas():
    found = {}
    for name, schema in support.kernel_schema_files().items():
        required = support.required_of(schema)
        if DECISION_ENTRY_FIELDS <= required and any("span" in field.lower() for field in required):
            found[name] = schema
    return found


def test_one_kernel_schema_is_a_decision_entry_with_id_status_owner_date_and_its_own_span():
    """Exactly one kernel schema file requires ``id``, ``status``, ``owner``, ``date`` and a span field (a required
    field whose name holds "span"), says its record type, and gives ``id`` a grammar that takes a register id
    (``DEC-730``) and refuses what is no decision id. Red today: no such schema file."""
    found = _decision_entry_schemas()
    assert len(found) == 1, (f"{support.KERNEL_SCHEMAS_REL} holds {len(found)} schema files that require "
                             f"{sorted(DECISION_ENTRY_FIELDS)} and a span; one is expected: {sorted(found)}")
    name, schema = next(iter(found.items()))
    assert support.type_of(schema), f"{name} says no record type (no constant `type` property)"
    shape = support._resolved(support.properties_of(schema).get("id") or {})
    pattern = shape.get("pattern")
    assert isinstance(pattern, str), f"{name} gives `id` no grammar"
    assert re.search(pattern, "DEC-730"), f"{name}: its id grammar {pattern} refuses the register id DEC-730"
    assert not re.search(pattern, "not a decision"), f"{name}: its id grammar {pattern} takes any text"


# --------------------------------------------------------------------------
# The close record, as this worktree's ``gov close`` writes it [AR-9]
# --------------------------------------------------------------------------

@pytest.fixture(scope="module")
def close_record(tmp_path_factory):
    """``(path, text)`` of the close record a real ``gov close`` wrote."""
    _, rel, text = support.closed_ticket(tmp_path_factory.mktemp("w2-02-close"))
    return rel, text


def test_the_kernel_has_one_schema_of_the_close_type():
    """One kernel schema file whose ``type`` is the constant ``close``. Red today: none."""
    found = support.schemas_of_type("close")
    assert len(found) == 1, f"{len(found)} kernel schema files are of type close; one is expected: {sorted(found)}"


def test_the_close_record_gov_close_writes_passes_core_schema(project, close_record):
    """The record ``gov close`` wrote, byte for byte at its path, in a project with the kernel's schemas: no finding
    on it. Red today: ``SCHEMA_UNKNOWN_TYPE`` (unknown record type 'close')."""
    rel, text = close_record
    project.write(rel, text)
    code, findings = project.core_schema()
    found = support.about(findings, rel)
    assert not found, f"the close record gov close wrote is a finding: {found}"
    assert code == 0, f"core-schema exits {code} on a project whose one record is the close record"


def test_a_close_record_that_names_no_ticket_is_refused(project, close_record):
    """The same record without ``task`` (the ticket it closes): a finding on the file names ``task``, and the check
    is not green. Red today: the one finding is ``SCHEMA_UNKNOWN_TYPE``, which names no field."""
    rel, text = close_record
    front, body = support.frontmatter_of(text)
    assert "task" in front, f"the close record gov close wrote has no `task`: {sorted(front)}"
    del front["task"]
    project.write(rel, "---\n" + yaml.safe_dump(front, sort_keys=False) + "---\n\n" + body)
    code, findings = project.core_schema()
    found = [finding for finding in support.about(findings, rel) if support.names_field(finding, "task")]
    assert found, f"a close record without `task` is not refused on `task`: {support.about(findings, rel)}"
    assert code != 0
