"""W2-64 keeps W2-02's KPIs (the lead's design note, item 6), and leaves nothing out silently (item 4): a record with
no string ``type``, an unknown type, a type whose schema file is in neither layout, a schema file that cannot be
parsed, and a file that opens with ``---`` whose frontmatter cannot be read are each a finding, never green.

Each case runs core-schema as declared, with the installed check-jsonschema on the validator folder of ``PATH``.
"""

from __future__ import annotations

import pytest

import w2_64_support as S

REL = "docs/records/REC-ONE.md"


def _project(tmp_path, records, leave_out=(), broken=None):
    project = S.Project(S.Place(tmp_path).real_tool()).kernel_schemas(leave_out=leave_out).registry()
    for name, text in (broken or {}).items():
        project.write(f"{S.KERNEL_SCHEMAS_REL}/{name}", text)
    for rel, text in records.items():
        project.write(rel, text)
    return project


@pytest.mark.parametrize("front", ({"id": "REC-ONE", "status": "ACTIVE", "state_class": "AUTHORITATIVE"},
                                   S.shared("REC-ONE", 5)), ids=("absent", "not-a-string"))
def test_a_type_absent_or_not_a_string_is_schema_invalid_type(tmp_path, front):
    """A record whose ``type`` is absent or not a string: ``SCHEMA_INVALID_TYPE`` on its path, exit non-zero. Passes
    today."""
    run = _project(tmp_path, {REL: S.markdown(front)}).core_schema()
    assert S.INVALID_TYPE in [f.get("code") for f in S.about(run.findings, REL)], run.describe()
    assert run.code != 0, run.describe()


def test_an_unknown_type_is_schema_unknown_type(tmp_path):
    """A record of a type the check does not know: ``SCHEMA_UNKNOWN_TYPE``, exit non-zero. Passes today."""
    run = _project(tmp_path, {REL: S.markdown(S.shared("REC-ONE", "minutes-of-a-meeting"))}).core_schema()
    assert S.UNKNOWN_TYPE in [f.get("code") for f in S.about(run.findings, REL)], run.describe()
    assert run.code != 0, run.describe()


def _lesson():
    return S.markdown(S.shared("L-0001", "lesson", lifecycle="ACTIVE", scope="project", severity="low"))


def test_a_type_whose_schema_is_in_neither_layout_is_unmeasured(tmp_path):
    """A lesson record with no ``lesson.schema.json`` in either layout: ``SCHEMA_UNREADABLE`` on its path (reported
    unmeasured), exit non-zero, never green. Passes today."""
    run = _project(tmp_path, {REL: _lesson()}, leave_out=("lesson.schema.json",)).core_schema()
    assert S.UNREADABLE in [f.get("code") for f in S.about(run.findings, REL)], run.describe()
    assert run.code != 0, run.describe()


def test_a_record_schema_that_cannot_be_parsed_is_red(tmp_path):
    """``lesson.schema.json`` that is not JSON, and a lesson record: RED, a finding on the record or naming the
    schema file. Passes today (``SCHEMA_UNREADABLE``)."""
    run = _project(tmp_path, {REL: _lesson()}, broken={"lesson.schema.json": "{ this is not json"}).core_schema()
    assert run.code != 0, f"an unparsable schema file is green\n{run.describe()}"
    assert S.about(run.findings, REL) or any("lesson.schema.json" in S.text_of(f) for f in run.findings), \
        run.describe()


def test_a_common_schema_that_cannot_be_parsed_is_red(tmp_path):
    """*Red.* ``common.schema.json``, which every record schema refers to, is not JSON; a valid ticket: RED, a finding
    on the record or naming ``common.schema.json``. Today: green (the subset reads the ticket schema's own
    ``required`` list without the shared file)."""
    run = _project(tmp_path, {".tickets/PROJ-aaaa.md": S.ticket()},
                   broken={"common.schema.json": "{ this is not json"}).core_schema()
    assert run.code != 0, f"an unparsable common.schema.json is green\n{run.describe()}"
    assert S.about(run.findings, ".tickets/PROJ-aaaa.md") or \
        any("common.schema.json" in S.text_of(f) for f in run.findings), run.describe()


UNREADABLE_FRONTMATTER = {
    "no closing line": "---\nid: REC-ONE\ntype: plan\nstatus: ACTIVE\n\n# A record with no end to its frontmatter\n",
    "a YAML error": "---\nid: REC-ONE\ntype: [plan\nstatus: : ACTIVE\n---\n\n# Body\n",
    "not a mapping": "---\n- id\n- type\n---\n\n# Body\n",
}


@pytest.mark.parametrize("case", sorted(UNREADABLE_FRONTMATTER))
def test_a_file_that_opens_with_dashes_and_whose_frontmatter_cannot_be_read_is_a_finding(tmp_path, case):
    """*Red.* A file under ``docs/`` that opens with ``---`` and whose frontmatter cannot be read (``case``) is a
    finding on its path and core-schema exits non-zero: no silent skip. Today: skipped, exit 0."""
    run = _project(tmp_path, {REL: UNREADABLE_FRONTMATTER[case]}).core_schema()
    assert S.about(run.findings, REL), f"a file whose frontmatter cannot be read ({case}) is skipped\n{run.describe()}"
    assert run.code != 0, run.describe()


def test_a_file_whose_first_line_is_not_dashes_is_no_record(tmp_path):
    """A Markdown file whose first line is not ``---`` is not a record, as today: no finding, exit 0. Passes
    today."""
    run = _project(tmp_path, {"docs/notes.md": "# Notes\n\n---\n\nid: not frontmatter\n"}).core_schema()
    assert run.code == 0 and run.findings == [], run.describe()
