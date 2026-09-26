"""govbridge.notes.build: built_from_sha256 is computed over the SORTED source hashes (order-independent), and a
note rebuilt twice from the same sources is accepted with an identical hash (REPAIR_DAG.yaml node R1-RN acceptance:
"Accepted: a note rebuilt twice from the same sources, with an identical hash")."""
from __future__ import annotations

from govbridge.notes import build as buildmod


def _source(content_sha256: str, item_id="U-1") -> dict:
    return {"item_id": item_id, "path": "a.py", "commit": "a" * 40, "blob": "b" * 40,
            "lines": [1, 2], "content_sha256": content_sha256}


def test_built_from_sha256_is_order_independent():
    claims_forward = [
        {"claim_id": "C-1", "text": "first", "sources": [_source("1" * 64)]},
        {"claim_id": "C-2", "text": "second", "sources": [_source("2" * 64)]},
    ]
    claims_reversed = [
        {"claim_id": "C-2", "text": "second", "sources": [_source("2" * 64)]},
        {"claim_id": "C-1", "text": "first", "sources": [_source("1" * 64)]},
    ]
    assert buildmod.compute_built_from_sha256(claims_forward) == buildmod.compute_built_from_sha256(claims_reversed)


def test_built_from_sha256_changes_with_sources():
    claims_a = [{"claim_id": "C-1", "text": "x", "sources": [_source("1" * 64)]}]
    claims_b = [{"claim_id": "C-1", "text": "x", "sources": [_source("2" * 64)]}]
    assert buildmod.compute_built_from_sha256(claims_a) != buildmod.compute_built_from_sha256(claims_b)


def test_build_note_sets_fixed_class_and_mandatory_unresolved():
    note = buildmod.build_note("N-1", [{"claim_id": "C-1", "text": "x", "sources": [_source("1" * 64)]}])
    assert note["class"] == "DERIVED_NOTE"
    assert note["unresolved"] == []  # mandatory key, defaults to empty, never omitted
    assert "built_from_sha256" in note


def test_build_note_preserves_explicit_unresolved():
    note = buildmod.build_note(
        "N-1", [{"claim_id": "C-1", "text": "x", "sources": [_source("1" * 64)]}],
        unresolved=["evidence at widgets/unknown.py could not be located"],
    )
    assert note["unresolved"] == ["evidence at widgets/unknown.py could not be located"]


def test_rebuild_twice_from_same_sources_is_identical():
    claims = [
        {"claim_id": "C-1", "text": "first", "sources": [_source("1" * 64)]},
        {"claim_id": "C-2", "text": "second", "sources": [_source("2" * 64), _source("3" * 64, item_id="U-2")]},
    ]
    note = buildmod.build_note("N-1", claims, unresolved=["one gap"])

    rebuilt_once = buildmod.rebuild(note)
    rebuilt_twice = buildmod.rebuild(rebuilt_once)

    assert rebuilt_once["built_from_sha256"] == note["built_from_sha256"]
    assert rebuilt_twice["built_from_sha256"] == note["built_from_sha256"]
    assert rebuilt_once == rebuilt_twice


def test_rebuild_detects_tampered_hash():
    claims = [{"claim_id": "C-1", "text": "x", "sources": [_source("1" * 64)]}]
    note = buildmod.build_note("N-1", claims)
    tampered = dict(note, built_from_sha256="0" * 64)

    rebuilt = buildmod.rebuild(tampered)
    assert rebuilt["built_from_sha256"] != tampered["built_from_sha256"]
    assert rebuilt["built_from_sha256"] == note["built_from_sha256"]
