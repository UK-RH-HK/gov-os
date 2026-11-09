"""W2-128 round 1: the ticket schema (TPL-5 S1, S2) and the lesson, failure and research schemas (sources,
decisions). The ready check (TPL-5 S3) and the dependency refusals are round 2 (README).

"Allows a field" is read as the schema declaring it in the ticket's form: the form is accepted and a value of
another shape (a bare string where a list is due) is refused. Today's schemas accept any extra key, so the refusal
half is what shows the declaration.
"""

from __future__ import annotations

import copy

import pytest

import w2_128_support as s

THIS_TICKET = s.REPO / ".tickets/DAEO-t8mp.md"


def _ticket() -> dict:
    front = s.record_front(THIS_TICKET)
    assert isinstance(front, dict), "premise: this ticket's front matter cannot be read"
    instance = s.as_instance(front)
    assert not s.schema_errors("ticket.schema.json", instance), "premise: this ticket is not valid today"
    return instance


def _with(base: dict, **fields) -> dict:
    instance = copy.deepcopy(base)
    instance.update(fields)
    return instance


def _accepts(schema: str, instance: dict) -> list[str]:
    return s.schema_errors(schema, instance)


# --- S10 (TPL-5 S1): the ticket schema -----------------------------------------------------------------------------

def test_s10_ticket_schema_declares_non_goals_as_a_list_of_strings():
    base = _ticket()
    assert not _accepts("ticket.schema.json", _with(base, non_goals=["no generator in this round"])), \
        "ticket.schema.json refuses non_goals: [str]"
    assert _accepts("ticket.schema.json", _with(base, non_goals="no generator")), \
        "ticket.schema.json does not declare non_goals: a bare string passes"


def test_s10_ticket_schema_accepts_a_kpi_line_as_line_and_verify_beside_the_string_form():
    base = _ticket()
    kpis = copy.deepcopy(base["kpis"])
    kpis["success"] = [kpis["success"][0], {"line": "S9 an observable outcome [DEC-1050]",
                                            "verify": "pytest tests/unit/x.py exits 0"}]
    kpis["failure"] = [{"line": "what must never happen", "verify": "the refusal case"}] + kpis["failure"]
    errors = _accepts("ticket.schema.json", _with(base, kpis=kpis))
    assert not errors, f"ticket.schema.json refuses the {{line, verify}} KPI form beside strings: {errors[:3]}"


@pytest.mark.parametrize("field", ["reads", "needs"])
def test_s10_ticket_schema_declares_reads_and_needs_as_lists_of_strings(field):
    base = _ticket()
    assert not _accepts("ticket.schema.json", _with(base, **{field: ["src/gov/links/**"]})), \
        f"ticket.schema.json refuses {field}: [str]"
    assert not _accepts("ticket.schema.json", _with(base, **{field: []})), \
        f"ticket.schema.json refuses an empty {field} (a declared none)"
    assert _accepts("ticket.schema.json", _with(base, **{field: "src/gov/links/**"})), \
        f"ticket.schema.json does not declare {field}: a bare string passes"


def test_s10_ticket_schema_declares_waits_on_as_a_string_or_ref_and_reason():
    # The CTO's P1 (b) and P2 (a), 2026-11-09: an item is a string or {ref, reason}; the key is ref, never on.
    base = _ticket()
    good = [{"ref": "DAEO-k7hz", "reason": "the store's statements first"},
            {"ref": "docs/research/W2-92-memory-measure.md", "reason": "the measure decides the hop"}]
    errors = _accepts("ticket.schema.json", _with(base, waits_on=good))
    assert not errors, f"ticket.schema.json refuses waits_on: [{{ref, reason}}]: {errors[:3]}"
    strings = ["DAEO-qskx — W2-142: the guard first"]
    errors = _accepts("ticket.schema.json", _with(base, waits_on=strings))
    assert not errors, f"ticket.schema.json refuses waits_on: [str] (DAEO-2bdu's form): {errors[:3]}"
    mixed = strings + good[:1]
    errors = _accepts("ticket.schema.json", _with(base, waits_on=mixed))
    assert not errors, f"ticket.schema.json refuses a string item beside a {{ref, reason}} item: {errors[:3]}"
    assert not _accepts("ticket.schema.json", _with(base, waits_on=[])), "ticket.schema.json refuses waits_on: []"
    assert _accepts("ticket.schema.json", _with(base, waits_on="DAEO-k7hz")), \
        "ticket.schema.json does not declare waits_on: a bare string passes"
    assert _accepts("ticket.schema.json", _with(base, waits_on=[{"reason": "the store's statements first"}])), \
        "ticket.schema.json accepts a waits_on object without ref"
    assert _accepts("ticket.schema.json", _with(base, waits_on=[{"on": "DAEO-k7hz", "reason": "the store first"}])), \
        "ticket.schema.json accepts a waits_on object keyed on instead of ref"


def test_s10_every_existing_ticket_stays_valid():
    tickets = s.records_of(("task",), folders=(".tickets",))
    assert len(tickets) >= 100, f"premise: only {len(tickets)} tickets found"
    invalid = {rel: errors[:2] for rel, front in tickets
               if (errors := s.schema_errors("ticket.schema.json", s.as_instance(front)))}
    assert not invalid, f"{len(invalid)} existing tickets no longer validate: {dict(list(invalid.items())[:5])}"


def test_s10_t1_is_the_ticket_template_with_its_skeleton_in_one_yaml_block():
    import yaml

    front, body = s.split(s.template("ticket"))
    assert isinstance(front, dict) and front.get("name") == "ticket", "ticket.md's front matter is not T-1's"
    blocks = [content for info, content in s.fenced_blocks(body) if info.split()[:1] == ["yaml"]]
    assert len(blocks) == 1, f"ticket.md's body holds {len(blocks)} fenced yaml blocks, not one"
    skeleton = yaml.safe_load(blocks[0])
    assert isinstance(skeleton, dict), "ticket.md's yaml block is not a mapping"
    for key in ("allowed_paths", "kpis", "non_goals", "sources"):
        assert key in skeleton, f"ticket.md's skeleton lacks {key}"
    success = (skeleton.get("kpis") or {}).get("success")
    assert isinstance(success, list) and success and all(isinstance(line, dict) and {"line", "verify"} <= set(line)
                                                         for line in success), \
        f"ticket.md's skeleton KPI lines are not {{line, verify}}: {success!r}"


# --- S16: sources and decisions on the lesson, failure and research schemas -----------------------------------------

MINIMAL = {
    "lesson.schema.json": {"id": "L-0999", "type": "lesson", "status": "PROVISIONAL", "state_class": "EVIDENCE",
                           "lifecycle": "candidate", "scope": "project", "severity": "low"},
    "failure.schema.json": {"id": "FAIL-0999", "type": "failure", "status": "ACTIVE", "state_class": "EVIDENCE"},
    "research.schema.json": {"id": "RES-0999", "type": "research", "status": "ACTIVE", "state_class": "EVIDENCE"},
}


@pytest.mark.parametrize("schema", sorted(MINIMAL))
def test_s16_schema_declares_optional_sources_as_a_list_of_ids(schema):
    base = MINIMAL[schema]
    assert not _accepts(schema, base), f"premise: the minimal record is not valid against {schema}"
    errors = _accepts(schema, _with(base, sources=["DEC-1073", "FAIL-0001"]))
    assert not errors, f"{schema} refuses sources: [ids]: {errors[:3]}"
    assert _accepts(schema, _with(base, sources="DEC-1073")), f"{schema} does not declare sources: a bare string passes"


def test_s16_research_schema_declares_optional_decisions_as_a_list_of_ids():
    base = MINIMAL["research.schema.json"]
    errors = _accepts("research.schema.json", _with(base, decisions=["DEC-1073"]))
    assert not errors, f"research.schema.json refuses decisions: [ids]: {errors[:3]}"
    assert _accepts("research.schema.json", _with(base, decisions="DEC-1073")), \
        "research.schema.json does not declare decisions: a bare string passes"


def test_s16_every_existing_lesson_failure_and_research_record_stays_valid():
    records = s.records_of(("lesson", "failure", "research"))
    assert records, "premise: no lesson, failure or research record found"
    schema = {"lesson": "lesson.schema.json", "failure": "failure.schema.json", "research": "research.schema.json"}
    invalid = {rel: errors[:2] for rel, front in records
               if (errors := s.schema_errors(schema[front["type"]], s.as_instance(front)))}
    assert not invalid, f"existing records no longer validate: {invalid}"
