"""govbridge.notes.validate against a real (synthetic) Git repo -- CONTROL-A-style real-view resolution, not a
mocked filesystem, matching REPAIR_DAG.yaml node R1-RN's acceptance line:

    Refused: a claim with no source, a source that does not resolve, a note placed in A, and a built_from_sha256
    mismatch. Accepted: a note rebuilt twice from the same sources, with an identical hash. unresolved[] is
    mandatory and may be empty.
"""
from __future__ import annotations

from govbridge.core.yamlutil import sha256_text
from govbridge.notes import build as buildmod
from govbridge.notes import validate as validatemod


def _good_source(repo, path, blob, lines, text) -> dict:
    return {
        "item_id": "U-1", "path": path, "commit": repo.commit, "blob": blob,
        "lines": lines, "content_sha256": sha256_text(text),
    }


def _good_note(repo) -> dict:
    source = _good_source(repo, repo.path_a, repo.blob_a, repo.lines_a_1_2, repo.text_a_1_2)
    claims = [{"claim_id": "C-1", "text": "make_gadget constructs a Gadget", "sources": [source]}]
    return buildmod.build_note("N-1", claims, unresolved=[])


def test_valid_note_passes(notes_repo):
    note = _good_note(notes_repo)
    result = validatemod.validate_note(note, repo=str(notes_repo.root))
    assert result == {"status": "PASS", "problems": []}


def test_valid_note_with_multiple_sources_and_claims_passes(notes_repo):
    source_a = _good_source(notes_repo, notes_repo.path_a, notes_repo.blob_a, notes_repo.lines_a_1_2,
                             notes_repo.text_a_1_2)
    source_b = _good_source(notes_repo, notes_repo.path_b, notes_repo.blob_b, notes_repo.lines_b_1_1,
                             notes_repo.text_b_1_1)
    claims = [
        {"claim_id": "C-1", "text": "gadget", "sources": [source_a]},
        {"claim_id": "C-2", "text": "sprocket", "sources": [source_b]},
    ]
    note = buildmod.build_note("N-1", claims, unresolved=["a third widget kind was not covered"])
    result = validatemod.validate_note(note, repo=str(notes_repo.root))
    assert result["status"] == "PASS"


# -- refused: a claim with no source -------------------------------------------------------------------------

def test_claim_with_no_source_is_refused(notes_repo):
    note = buildmod.build_note("N-1", [{"claim_id": "C-1", "text": "x", "sources": []}])
    result = validatemod.validate_note(note, repo=str(notes_repo.root))
    assert result["status"] == "FAIL"
    assert any("no source" in p for p in result["problems"])


# -- refused: a source that does not resolve ------------------------------------------------------------------

def test_source_with_wrong_content_sha256_does_not_resolve(notes_repo):
    source = _good_source(notes_repo, notes_repo.path_a, notes_repo.blob_a, notes_repo.lines_a_1_2, "wrong text")
    note = buildmod.build_note("N-1", [{"claim_id": "C-1", "text": "x", "sources": [source]}])
    result = validatemod.validate_note(note, repo=str(notes_repo.root))
    assert result["status"] == "FAIL"
    assert any("does not resolve" in p for p in result["problems"])


def test_source_with_wrong_blob_does_not_resolve(notes_repo):
    source = _good_source(notes_repo, notes_repo.path_a, "0" * 40, notes_repo.lines_a_1_2, notes_repo.text_a_1_2)
    note = buildmod.build_note("N-1", [{"claim_id": "C-1", "text": "x", "sources": [source]}])
    result = validatemod.validate_note(note, repo=str(notes_repo.root))
    assert result["status"] == "FAIL"
    assert any("blob mismatch" in p for p in result["problems"])


def test_source_with_unknown_path_does_not_resolve(notes_repo):
    source = _good_source(notes_repo, "widgets/does-not-exist.py", notes_repo.blob_a, notes_repo.lines_a_1_2,
                           notes_repo.text_a_1_2)
    note = buildmod.build_note("N-1", [{"claim_id": "C-1", "text": "x", "sources": [source]}])
    result = validatemod.validate_note(note, repo=str(notes_repo.root))
    assert result["status"] == "FAIL"
    assert any("does not exist at commit" in p for p in result["problems"])


def test_source_with_unresolvable_commit_does_not_resolve(notes_repo):
    source = _good_source(notes_repo, notes_repo.path_a, notes_repo.blob_a, notes_repo.lines_a_1_2,
                           notes_repo.text_a_1_2)
    source["commit"] = "f" * 40
    note = buildmod.build_note("N-1", [{"claim_id": "C-1", "text": "x", "sources": [source]}])
    result = validatemod.validate_note(note, repo=str(notes_repo.root))
    assert result["status"] == "FAIL"
    assert any("commit does not resolve" in p for p in result["problems"])


def test_source_with_lines_out_of_range_does_not_resolve(notes_repo):
    source = _good_source(notes_repo, notes_repo.path_a, notes_repo.blob_a, [1, 2], notes_repo.text_a_1_2)
    source["lines"] = [40, 41]
    note = buildmod.build_note("N-1", [{"claim_id": "C-1", "text": "x", "sources": [source]}])
    result = validatemod.validate_note(note, repo=str(notes_repo.root))
    assert result["status"] == "FAIL"
    assert any("out of range" in p for p in result["problems"])


# -- refused: a note placed in A -----------------------------------------------------------------------------

def test_note_placed_in_a_is_refused_even_if_otherwise_valid(notes_repo):
    note = _good_note(notes_repo)
    result = validatemod.validate_note(note, repo=str(notes_repo.root), target_section="A")
    assert result["status"] == "FAIL"
    assert any("section A" in p or "'A'" in p for p in result["problems"])


def test_note_not_targeted_at_a_is_unaffected_by_placement_check(notes_repo):
    note = _good_note(notes_repo)
    result_none = validatemod.validate_note(note, repo=str(notes_repo.root), target_section=None)
    result_h = validatemod.validate_note(note, repo=str(notes_repo.root), target_section="H")
    assert result_none["status"] == "PASS"
    assert result_h["status"] == "PASS"


def test_note_placement_check_is_case_insensitive(notes_repo):
    note = _good_note(notes_repo)
    result = validatemod.validate_note(note, repo=str(notes_repo.root), target_section="a")
    assert result["status"] == "FAIL"


# -- refused: a built_from_sha256 mismatch --------------------------------------------------------------------

def test_built_from_sha256_mismatch_is_refused(notes_repo):
    note = _good_note(notes_repo)
    tampered = dict(note, built_from_sha256="0" * 64)
    result = validatemod.validate_note(tampered, repo=str(notes_repo.root))
    assert result["status"] == "FAIL"
    assert any("built_from_sha256 mismatch" in p for p in result["problems"])


# -- unresolved[] is mandatory and may be empty ---------------------------------------------------------------

def test_missing_unresolved_key_is_refused(notes_repo):
    note = _good_note(notes_repo)
    del note["unresolved"]
    result = validatemod.validate_note(note, repo=str(notes_repo.root))
    assert result["status"] == "FAIL"
    assert any("unresolved" in p for p in result["problems"])


def test_empty_unresolved_list_is_accepted(notes_repo):
    note = _good_note(notes_repo)
    assert note["unresolved"] == []
    result = validatemod.validate_note(note, repo=str(notes_repo.root))
    assert result["status"] == "PASS"


def test_nonempty_unresolved_list_is_accepted(notes_repo):
    source = _good_source(notes_repo, notes_repo.path_a, notes_repo.blob_a, notes_repo.lines_a_1_2,
                           notes_repo.text_a_1_2)
    claims = [{"claim_id": "C-1", "text": "x", "sources": [source]}]
    note = buildmod.build_note("N-1", claims, unresolved=["could not resolve widgets/sprocket.py's constructor"])
    result = validatemod.validate_note(note, repo=str(notes_repo.root))
    assert result["status"] == "PASS"
