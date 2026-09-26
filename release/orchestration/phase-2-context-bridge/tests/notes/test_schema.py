"""config/notes-schema.yaml loads, declares the fixed shape R1-RN's acceptance check names, and never drifts from
the NOTE_CLASS constant govbridge.notes.schema/build/validate actually use (the same discipline
govbridge.authority.classes uses against ORCHESTRATOR_STATE.yaml)."""
from __future__ import annotations

from govbridge.notes import schema as schemamod


def test_schema_loads_and_declares_derived_note():
    doc = schemamod.load_schema()
    assert doc["schema"] == "govbridge-schema/1"
    assert doc["class"] == "DERIVED_NOTE"
    assert doc["admissible_in_a"] is False
    assert doc["admissible_in_d1"] is False


def test_note_class_constant_matches_schema_file():
    doc = schemamod.load_schema()
    assert schemamod.NOTE_CLASS == doc["class"]
    assert doc["fields"]["class"]["const"] == schemamod.NOTE_CLASS


def test_schema_field_tables_present():
    doc = schemamod.load_schema()
    for top in ("note_id", "class", "claims", "unresolved", "built_from_sha256"):
        assert top in doc["fields"], top
    for cf in ("claim_id", "text", "sources"):
        assert cf in doc["claim_fields"], cf
    for sf in ("item_id", "path", "commit", "blob", "lines", "content_sha256"):
        assert sf in doc["source_fields"], sf
    assert doc["claim_fields"]["sources"]["min_items"] == 1


def test_structural_problems_empty_for_well_shaped_note():
    note = {
        "note_id": "N-1",
        "class": "DERIVED_NOTE",
        "claims": [
            {"claim_id": "C-1", "text": "a claim", "sources": [
                {"item_id": "U-1", "path": "a.py", "commit": "a" * 40, "blob": "b" * 40,
                 "lines": [1, 2], "content_sha256": "c" * 64},
            ]},
        ],
        "unresolved": [],
        "built_from_sha256": "d" * 64,
    }
    assert schemamod.structural_problems(note) == []


def test_structural_problems_flags_missing_unresolved_key():
    note = {
        "note_id": "N-1",
        "class": "DERIVED_NOTE",
        "claims": [],
        "built_from_sha256": "d" * 64,
    }
    problems = schemamod.structural_problems(note)
    assert any("unresolved" in p for p in problems)


def test_structural_problems_flags_wrong_class_const():
    note = {
        "note_id": "N-1",
        "class": "OWNER_DECISION",
        "claims": [],
        "unresolved": [],
        "built_from_sha256": "d" * 64,
    }
    problems = schemamod.structural_problems(note)
    assert any("expected constant" in p for p in problems)


def test_structural_problems_flags_claim_with_no_source():
    note = {
        "note_id": "N-1",
        "class": "DERIVED_NOTE",
        "claims": [{"claim_id": "C-1", "text": "a claim", "sources": []}],
        "unresolved": [],
        "built_from_sha256": "d" * 64,
    }
    problems = schemamod.structural_problems(note)
    assert any("no source is refused" in p for p in problems)


def test_structural_problems_flags_bad_line_range():
    note = {
        "note_id": "N-1",
        "class": "DERIVED_NOTE",
        "claims": [
            {"claim_id": "C-1", "text": "a claim", "sources": [
                {"item_id": "U-1", "path": "a.py", "commit": "a" * 40, "blob": "b" * 40,
                 "lines": [5, 2], "content_sha256": "c" * 64},
            ]},
        ],
        "unresolved": [],
        "built_from_sha256": "d" * 64,
    }
    problems = schemamod.structural_problems(note)
    assert any("lines" in p for p in problems)
