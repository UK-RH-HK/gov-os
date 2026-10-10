"""Round 15, piece 3 (DEC-612, DEC-614, DEC-620): the schema check knows the record types in use.

Measured before the round: the schema check reports ``SCHEMA_UNKNOWN_TYPE`` for the records of type
``change-execution-record`` and ``change-impact-proposal`` this repository holds. After the round the
orchestrator also creates records of type ``capability`` (ids such as ``CAP-38`` and ``CAP-38.b``) and gives the
Charter and the Contract the type ``specification`` and the Wave 1 work breakdown the type ``plan``. DEC-620:
"Each owes the shared frontmatter and nothing more."

Every case builds its own temporary project: the kernel template's schema files (each copied as the file it is)
and records the case writes, with ids of the form this repository's records have. No case reads a record of this
repository under ``docs/``: those gain their frontmatter only after the round's merge. The checks are run as the
kernel template declares them (``core-schema``, ``core-graph``), by ``sh -c`` in the project root.
"""

from __future__ import annotations

import json
import re

import pytest

import w1_30_r15_support as r15

SCHEMA_CHECK, GRAPH_CHECK = "core-schema", "core-graph"
UNKNOWN_TYPE = "SCHEMA_UNKNOWN_TYPE"
MISSING_FIELD = "SCHEMA_MISSING_FIELD"
OUTSIDE_GRAMMAR = "ID_OUTSIDE_GRAMMAR"
SHARED = ("id", "type", "status", "state_class")

# type -> (where a record of it stands, its id): the places and the forms of id this repository uses.
RECORDS = {
    "change-execution-record": ("docs/changes/S2-CIT-E.md", "S2-CIT-E"),
    "change-impact-proposal": ("docs/changes/S2-CIT-P.md", "S2-CIT-P"),
    "capability": ("docs/contract/capabilities/CAP-38.md", "CAP-38"),
    "specification": ("docs/charter/CHARTER_v5.md", "CHARTER-v5"),
    "plan": ("docs/plan/WAVE_1_WBS.md", "WAVE-1-WBS"),
}
TYPES = sorted(RECORDS)
# Ids that exist or are decided: the two change records this repository holds, and the capability ids of DEC-620.
# The ids the Charter, the Contract and the work breakdown will get are the orchestrator's and are held by no case.
REAL_IDS = {
    "change-execution-record": ("S2-CIT-E",),
    "change-impact-proposal": ("S2-CIT-P",),
    "capability": ("CAP-38", "CAP-38.b"),
}
NOBODY_KNOWS = "minutes-of-a-meeting"


def _findings(check_id, project, sandbox):
    """The findings the check prints (a JSON list; nothing printed is no finding) and its exit code."""
    done = r15.run_declared_command(check_id, project, sandbox)
    assert "Traceback" not in done.stderr, f"{check_id} ended with a traceback\n{done.stderr}"
    findings = json.loads(done.stdout) if done.stdout.strip() else []
    findings = findings.get("findings", []) if isinstance(findings, dict) else findings
    assert bool(findings) == (done.returncode != 0), \
        f"{check_id}: exit code {done.returncode} with {len(findings)} findings\n{done.stdout}\n{done.stderr}"
    return findings


def _about(findings, rel):
    return [finding for finding in findings if finding.get("path") == rel]


def _project(scratch):
    project = scratch()
    project.kernel_schemas()
    return project


@pytest.mark.parametrize("record_type", TYPES)
def test_a_record_of_the_type_that_holds_the_shared_frontmatter_passes(record_type, scratch, sandbox):
    """The four shared fields and no other: nothing beyond them is owed.
    Red before the round: ``SCHEMA_UNKNOWN_TYPE`` for each of the five types."""
    rel, record_id = RECORDS[record_type]
    project = _project(scratch)
    project.write(rel, r15.record_text(record_id, record_type))
    found = _about(_findings(SCHEMA_CHECK, project, sandbox), rel)
    assert not found, f"a {record_type} record that holds the shared frontmatter is a finding: {found}"


@pytest.mark.parametrize("record_type", TYPES)
def test_a_record_of_the_type_without_state_class_is_a_finding(record_type, scratch, sandbox):
    """Its one finding is the field it lacks. Red before the round: the missing field is reported, and beside it
    ``SCHEMA_UNKNOWN_TYPE``."""
    rel, record_id = RECORDS[record_type]
    project = _project(scratch)
    project.write(rel, r15.record_text(record_id, record_type, state_class=None))
    found = _about(_findings(SCHEMA_CHECK, project, sandbox), rel)
    assert [(finding.get("code"), finding.get("field")) for finding in found] == [(MISSING_FIELD, "state_class")], \
        f"a {record_type} record without state_class: its one finding is not the missing field: {found}"


def test_a_type_nobody_knows_is_still_an_unknown_type(scratch, sandbox):
    """Pins what holds today (passes before the round), in a project that also holds the five types: the five
    are known by name, not by the check giving up on types."""
    project = _project(scratch)
    for record_type, (rel, record_id) in RECORDS.items():
        project.write(rel, r15.record_text(record_id, record_type))
    rel = project.write("docs/notes/MIN-0001.md", r15.record_text("MIN-0001", NOBODY_KNOWS))
    found = _about(_findings(SCHEMA_CHECK, project, sandbox), rel)
    assert [(finding.get("code"), finding.get("type")) for finding in found] == [(UNKNOWN_TYPE, NOBODY_KNOWS)], \
        f"a record of a type nobody knows is not reported as of an unknown type: {found}"


@pytest.mark.parametrize("record_id", ("CAP-38", "CAP-38.b"))
def test_a_capability_id_passes_the_id_grammar_of_the_schema_check_and_of_the_graph_check(record_id, scratch,
                                                                                         sandbox):
    """A capability and one of its covers items (``CAP-38.b``: a dot and a letter after the number).
    Red before the round on the schema check (``SCHEMA_UNKNOWN_TYPE``); the graph check passes it today."""
    project = _project(scratch)
    rel = project.write(f"docs/contract/capabilities/{record_id}.md", r15.record_text(record_id, "capability",
                                                                                      state_class="DERIVED"))
    found = _about(_findings(SCHEMA_CHECK, project, sandbox), rel)
    assert not found, f"the schema check refuses the capability record {record_id}: {found}"
    graph = [finding for finding in _findings(GRAPH_CHECK, project, sandbox)
             if finding.get("code") == OUTSIDE_GRAMMAR or record_id in json.dumps(finding)]
    assert not graph, f"the graph check refuses the capability record {record_id}: {graph}"


def _schema_of(record_type):
    """``(file name, schema)`` of the kernel template's schema files whose ``type`` property is the constant
    ``record_type``: how a record schema of the kernel says which type it is of (``lesson``, ``research``)."""
    found = []
    for path in sorted((r15.REPO_ROOT / r15.SCHEMAS_REL).glob("*.schema.json")):
        schema = json.loads(path.read_text(encoding="utf-8"))
        if (schema.get("properties") or {}).get("type", {}).get("const") == record_type:
            found.append((path.name, schema))
    return found


@pytest.mark.parametrize("record_type", TYPES)
def test_the_type_has_a_schema_file_in_the_kernel_template_beside_the_others(record_type):
    """One schema file of the type; it refers to the shared frontmatter of ``common.schema.json`` and requires
    nothing beyond it; an id grammar it gives accepts the ids of the type that exist or are decided.
    Red before the round: no schema file of the type."""
    found = _schema_of(record_type)
    assert len(found) == 1, (f"{r15.SCHEMAS_REL} holds {len(found)} schema files whose `type` is the constant "
                             f"{record_type!r}; one is expected: {[name for name, _ in found]}")
    name, schema = found[0]
    refs = [entry.get("$ref") for entry in schema.get("allOf", []) if isinstance(entry, dict)]
    assert "common.schema.json#/$defs/frontmatter" in refs, f"{name} does not refer to the shared frontmatter"
    beyond = sorted(set(schema.get("required", [])) - set(SHARED))
    assert not beyond, f"{name} requires fields beyond the shared frontmatter: {beyond}"
    common = json.loads((r15.REPO_ROOT / r15.SCHEMAS_REL / "common.schema.json").read_text(encoding="utf-8"))
    shape = (schema.get("properties") or {}).get("id") or {}
    if "$ref" in shape:
        source, _, definition = shape["$ref"].partition("#/$defs/")
        owner = common if source == "common.schema.json" else schema
        shape = owner.get("$defs", {}).get(definition)
        assert isinstance(shape, dict), f"{name}: the id grammar it refers to does not exist"
    if "pattern" in shape:
        refused = [record_id for record_id in REAL_IDS.get(record_type, ())
                   if not re.search(shape["pattern"], record_id)]
        assert not refused, f"{name}: its id grammar {shape['pattern']} refuses {refused}"
