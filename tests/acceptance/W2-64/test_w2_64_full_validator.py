"""W2-64 KPI success 1 and failure 1: core-schema validates every record against its schema through
check-jsonschema, not a subset; a record its schema refuses is refused, and the refusal names the record and the
rule [lens G R2 (a), F2, DEC-872 item 2].

Every case runs core-schema as declared in a temporary repository built from scratch, the kernel's schema files
copied in by name, a tool registry pinning check-jsonschema as this repository's does, and the installed
check-jsonschema alone on the validator folder of ``PATH``.
"""

from __future__ import annotations

import pytest

import w2_64_support as S

TICKET_REL = ".tickets/PROJ-aaaa.md"
TICKET_SCHEMA = "ticket.schema.json"


def _project(tmp_path, records, layouts=(S.KERNEL_SCHEMAS_REL,)):
    project = S.Project(S.Place(tmp_path).real_tool())
    for layout in layouts:
        project.kernel_schemas(layout=layout)
    project.registry()
    for rel, text in records.items():
        project.write(rel, text)
    return project


def test_a_valid_ticket_passes(tmp_path):
    """The control: a ticket every rule of its schema takes (an unquoted timestamp among its fields) passes: exit 0,
    no finding. Passes today."""
    run = _project(tmp_path, {TICKET_REL: S.ticket()}).core_schema()
    assert run.code == 0 and run.findings == [], f"a valid ticket is refused\n{run.describe()}"


def test_lens_g_planted_ticket_is_refused_naming_record_and_rule(tmp_path):
    """*Red.* Run G-4's planted ticket (status ``banana``, state_class ``NOT-A-CLASS``, profile ``HUGE``, est_loc
    -5, deps ``["not an id"]``, empty ``allowed_paths`` and ``kpis``) is refused: core-schema exits non-zero, and
    for each fault the schemas refuse there is a finding on the record's path that names the schema file, the
    place and the validator's message. ``status: banana`` breaks no rule (the shared ``status`` is any non-empty
    text) and gives no finding. Today: exit 0, no finding (the subset checks required fields only)."""
    run = _project(tmp_path, {TICKET_REL: S.ticket(**S.PLANTED)}).core_schema()
    assert run.code != 0, f"lens G's planted ticket passes core-schema\n{run.describe()}"
    mine = S.about(run.findings, TICKET_REL)
    assert mine, f"no finding names {TICKET_REL}\n{run.describe()}"
    for field, place, words in (("state_class", "state_class", ("NOT-A-CLASS",)),
                                ("profile", "profile", ("HUGE",)),
                                ("est_loc", "est_loc", ("-5",)),
                                ("deps", "deps[0]", ("not an id",)),
                                ("allowed_paths", "allowed_paths", ()),
                                ("kpis", "kpis", ("success",)),
                                ("kpis", "kpis", ("failure",))):
        named = [finding for finding in mine if finding.get("field") == field
                 and S.names_rule(finding, TICKET_SCHEMA, place, words)]
        assert named, (f"no finding on {TICKET_REL} names field '{field}' with the rule ({TICKET_SCHEMA}, the place "
                       f"'{place}', the message's {list(words)}): {mine}")
        assert all(finding.get("code") in S.REFUSALS for finding in named), named
    assert not [finding for finding in mine if finding.get("field") == "status"], \
        f"status 'banana' breaks no rule of the schemas, yet is refused: {mine}"


@pytest.mark.parametrize("field, value, words", (
    ("state_class", "NOT-A-CLASS", ("NOT-A-CLASS",)),
    ("profile", "HUGE", ("HUGE",)),
    ("deps", ["not an id"], ("not an id",)),
    ("wbs_id", "W9-1", ("W9-1",)),
))
def test_one_fault_the_subset_passed_is_refused(tmp_path, field, value, words):
    """*Red.* The subset's gap closed: a valid ticket but for one value its schema (or ``common.schema.json``, through
    a ``$ref``) refuses is refused, ``SCHEMA_INVALID_FIELD`` on its path naming the field, the schema file and the
    validator's message. Today: exit 0, no finding."""
    run = _project(tmp_path, {TICKET_REL: S.ticket(**{field: value})}).core_schema()
    assert run.code != 0, f"a ticket with {field}={value!r} passes core-schema\n{run.describe()}"
    mine = [finding for finding in S.about(run.findings, TICKET_REL) if finding.get("field") == field]
    assert mine, f"no finding on {TICKET_REL} names '{field}'\n{run.describe()}"
    assert all(finding.get("code") == S.INVALID_FIELD for finding in mine), mine
    assert any(S.names_rule(finding, TICKET_SCHEMA, field, words) for finding in mine), \
        f"no finding names the rule ({TICKET_SCHEMA}, '{field}', {list(words)}): {mine}"


def test_a_missing_required_field_is_schema_missing_field(tmp_path):
    """A ticket without ``kpis``, a field its schema requires: ``SCHEMA_MISSING_FIELD`` naming ``kpis``, on the record's
    path. Passes today."""
    run = _project(tmp_path, {TICKET_REL: S.ticket(kpis=None)}).core_schema()
    assert run.code != 0, run.describe()
    mine = S.about(run.findings, TICKET_REL)
    assert any(finding.get("code") == S.MISSING_FIELD and finding.get("field") == "kpis" for finding in mine), \
        f"no {S.MISSING_FIELD} naming 'kpis': {mine}"


def test_every_finding_is_on_a_record_s_repository_path(tmp_path):
    """*Red.* Findings carry today's shape (``code``, ``path``, ``field``, ``message``), and the path is the record's
    path in the repository, never a temporary instance file's; each record's own errors are its own. Today: no
    finding at all."""
    records = {TICKET_REL: S.ticket(state_class="NOT-A-CLASS"),
               ".tickets/PROJ-cccc.md": S.ticket(id="PROJ-cccc", profile="HUGE"),
               "docs/plan/PLAN-ONE.md": S.markdown(S.shared("PLAN-ONE", "plan", state_class="NOT-A-CLASS"))}
    run = _project(tmp_path, records).core_schema()
    assert run.code != 0, run.describe()
    assert run.findings, run.describe()
    for finding in run.findings:
        assert {"code", "path", "field", "message"} <= set(finding), f"a finding lacks today's keys: {finding}"
        assert finding["path"] in records, f"a finding names a path that is no record of the project: {finding}"
    assert [f.get("field") for f in S.about(run.findings, TICKET_REL)] == ["state_class"], run.describe()
    assert [f.get("field") for f in S.about(run.findings, ".tickets/PROJ-cccc.md")] == ["profile"], run.describe()
    assert [f.get("field") for f in S.about(run.findings, "docs/plan/PLAN-ONE.md")] == ["state_class"], \
        run.describe()


def test_several_errors_of_one_record_are_several_findings(tmp_path):
    """*Red.* A record with three faults has a finding for each, not a count. Today: none."""
    run = _project(tmp_path, {TICKET_REL: S.ticket(state_class="NOT-A-CLASS", profile="HUGE",
                                                   est_loc=-5)}).core_schema()
    fields = sorted(finding.get("field") for finding in S.about(run.findings, TICKET_REL))
    assert fields == ["est_loc", "profile", "state_class"], f"not one finding per fault: {fields}\n{run.describe()}"


def test_a_finding_under_both_layouts_is_given_once(tmp_path):
    """*Red.* With the schema files in both kernel layouts (``template/governance/kernel/schemas/`` and
    ``governance/kernel/schemas/``), a fault gives as many findings as under one layout: one. Today: none."""
    run = _project(tmp_path, {TICKET_REL: S.ticket(state_class="NOT-A-CLASS")},
                   layouts=(S.KERNEL_SCHEMAS_REL, S.INSTALLED_SCHEMAS_REL)).core_schema()
    mine = [finding for finding in S.about(run.findings, TICKET_REL) if finding.get("field") == "state_class"]
    assert len(mine) == 1, f"{len(mine)} findings on state_class under two layouts; one expected\n{run.describe()}"
    assert run.code != 0, run.describe()


def test_the_installed_layout_alone_is_measured(tmp_path):
    """*Red.* A project holding only the installed layout (``governance/kernel/schemas/``) is held to it: the fault
    is refused. Today: no finding."""
    run = _project(tmp_path, {TICKET_REL: S.ticket(state_class="NOT-A-CLASS")},
                   layouts=(S.INSTALLED_SCHEMAS_REL,)).core_schema()
    assert run.code != 0, f"the installed layout's schema is not applied\n{run.describe()}"
    assert [f for f in S.about(run.findings, TICKET_REL) if f.get("field") == "state_class"], run.describe()


def test_a_standalone_record_owes_no_shared_frontmatter(tmp_path):
    """``STANDALONE_TYPES`` keeps its meaning: an audit report in its folder (no ``type``, DEC-441's three fields)
    owes no shared frontmatter and passes. Passes today."""
    front = {"milestone": "wave-9-exit", "commit": "a" * 40, "pack_sha256": "b" * 64}
    rel = "docs/audit/wave-9/report.md"
    run = _project(tmp_path, {rel: S.markdown(front)}).core_schema()
    assert S.about(run.findings, rel) == [] and run.code == 0, run.describe()


def test_a_shared_field_is_owed_by_every_other_record(tmp_path):
    """A plan record without ``state_class``: ``SCHEMA_MISSING_FIELD`` naming it, given once. Passes today."""
    front = S.shared("PLAN-ONE", "plan")
    del front["state_class"]
    rel = "docs/plan/PLAN-ONE.md"
    run = _project(tmp_path, {rel: S.markdown(front)}).core_schema()
    mine = [finding for finding in S.about(run.findings, rel) if finding.get("field") == "state_class"]
    assert len(mine) == 1 and mine[0].get("code") == S.MISSING_FIELD, run.describe()
    assert run.code != 0, run.describe()
