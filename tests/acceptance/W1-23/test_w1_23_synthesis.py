"""W1-23 acceptance tests: hierarchical synthesis notes (DAEO-9i8e, CAP-15.f).

KPIs under test:
  S1  When evidence exceeds the packet budget, notes are derived under .gov-runtime/,
      cite source ids and hashes, and disclose unresolved evidence.
  S2  A note is invalidated when any cited source hash changes; notes are rebuildable.
  F1  A note survives a change to a cited source (forbidden).
  F2  A note cites a span not in its source (forbidden).
"""
from __future__ import annotations

import shutil
from pathlib import Path

import w1_23_support as support

SMALL_BUDGET = 50


def _evidence_set(root):
    """Evidence from three files in two directories, exceeding SMALL_BUDGET in total tokens."""
    return [
        support.make_evidence_item(root, "docs/alpha.md", 1, 10, item_id="alpha-1"),
        support.make_evidence_item(root, "docs/beta.md", 1, 9, item_id="beta-1"),
        support.make_evidence_item(root, "specs/gamma.md", 1, 10, item_id="gamma-1"),
    ]


def _total_tokens(evidence):
    return sum(support.tokens(item["text"]) for item in evidence)


# ---------------------------------------------------------------------------
# S1: derivation, citation and unresolved disclosure
# ---------------------------------------------------------------------------


class TestDerive:
    """S1: When evidence exceeds the packet budget, notes are derived under .gov-runtime/,
    cite source ids and hashes, and disclose unresolved evidence [CAP-15.f]."""

    def test_notes_written_under_gov_runtime(self, synthesis_api, project):
        evidence = _evidence_set(project)
        assert _total_tokens(evidence) > SMALL_BUDGET, "precondition: evidence must exceed budget"
        synthesis_api.synthesize(project, evidence, SMALL_BUDGET)
        gov_runtime = Path(project) / ".gov-runtime"
        assert gov_runtime.is_dir(), ".gov-runtime/ was not created"
        note_files = [f for f in gov_runtime.rglob("*") if f.is_file()]
        assert note_files, "no note files written under .gov-runtime/"

    def test_notes_cite_source_ids(self, synthesis_api, project):
        evidence = _evidence_set(project)
        result = synthesis_api.synthesize(project, evidence, SMALL_BUDGET)
        notes = result["notes"]
        all_cited_ids = {c["source_id"] for group in notes for c in group["citations"]}
        evidence_ids = {item["id"] for item in evidence}
        assert all_cited_ids, "notes contain no citation ids"
        assert all_cited_ids <= evidence_ids, \
            f"citations reference unknown ids: {all_cited_ids - evidence_ids}"

    def test_notes_cite_source_sha256(self, synthesis_api, project):
        evidence = _evidence_set(project)
        result = synthesis_api.synthesize(project, evidence, SMALL_BUDGET)
        evidence_hashes = {item["id"]: item["sha256"] for item in evidence}
        for group in result["notes"]:
            for citation in group["citations"]:
                assert "source_sha256" in citation, "citation missing source_sha256"
                expected = evidence_hashes.get(citation["source_id"])
                assert citation["source_sha256"] == expected, \
                    f"sha256 mismatch for {citation['source_id']}"

    def test_notes_disclose_unresolved_evidence(self, synthesis_api, project):
        evidence = _evidence_set(project)
        gaps = [
            {"id": "unresolved-1", "path": "missing/file.md", "reason": "NOT_GATHERED"},
            {"id": "unresolved-2", "path": "missing/other.md", "reason": "NOT_GATHERED"},
        ]
        result = synthesis_api.synthesize(project, evidence, SMALL_BUDGET, gaps=gaps)
        unresolved = result["unresolved"]
        unresolved_ids = {item["id"] for item in unresolved}
        assert "unresolved-1" in unresolved_ids, "gap unresolved-1 not disclosed"
        assert "unresolved-2" in unresolved_ids, "gap unresolved-2 not disclosed"

    def test_notes_are_hierarchical(self, synthesis_api, project):
        evidence = _evidence_set(project)
        result = synthesis_api.synthesize(project, evidence, SMALL_BUDGET)
        notes = result["notes"]
        assert isinstance(notes, list), "notes must be a list of groups"
        assert len(notes) > 1, "hierarchical notes must have more than one group"
        for group in notes:
            assert "group" in group, "each group must have a 'group' key"
            assert "citations" in group, "each group must have a 'citations' key"
            assert isinstance(group["citations"], list), "citations must be a list"

    def test_no_unresolved_when_no_gaps(self, synthesis_api, project):
        evidence = _evidence_set(project)
        result = synthesis_api.synthesize(project, evidence, SMALL_BUDGET)
        unresolved = result.get("unresolved", [])
        assert unresolved == [], f"expected no unresolved without gaps, got {unresolved}"


# ---------------------------------------------------------------------------
# S2: invalidation on hash change and rebuildability
# ---------------------------------------------------------------------------


class TestInvalidation:
    """S2: A note is invalidated when any cited source hash changes;
    notes are rebuildable [CAP-15.f]."""

    def test_note_invalidated_when_source_hash_changes(self, synthesis_api, validate_api, project):
        evidence = _evidence_set(project)
        synthesis_api.synthesize(project, evidence, SMALL_BUDGET)
        alpha = Path(project) / "docs" / "alpha.md"
        alpha.write_text(alpha.read_text() + "\nNew line changes the hash.\n")
        result = validate_api.validate_notes(project)
        assert not result["valid"], "note must be invalid after source hash change"
        assert result["errors"], "expected error(s) for the changed source"

    def test_notes_rebuildable_same_bytes(self, synthesis_api, project):
        evidence = _evidence_set(project)
        gaps = [{"id": "gap-rb", "path": "missing.md", "reason": "NOT_GATHERED"}]
        synthesis_api.synthesize(project, evidence, SMALL_BUDGET, gaps=gaps)
        gov_runtime = Path(project) / ".gov-runtime"
        first = {str(f.relative_to(gov_runtime)): f.read_bytes()
                 for f in sorted(gov_runtime.rglob("*")) if f.is_file()}
        assert first, "no notes written on first derivation"
        shutil.rmtree(gov_runtime)
        synthesis_api.synthesize(project, evidence, SMALL_BUDGET, gaps=gaps)
        second = {str(f.relative_to(gov_runtime)): f.read_bytes()
                  for f in sorted(gov_runtime.rglob("*")) if f.is_file()}
        assert first == second, "re-derived notes differ from original (not deterministic/rebuildable)"


# ---------------------------------------------------------------------------
# F1: a note must not survive a change to a cited source
# ---------------------------------------------------------------------------


class TestF1:
    """F1 (failure KPI): a note survives a change to a cited source — forbidden."""

    def test_changed_source_invalidates_note(self, synthesis_api, validate_api, project):
        evidence = _evidence_set(project)
        synthesis_api.synthesize(project, evidence, SMALL_BUDGET)
        for item in evidence:
            fpath = Path(project) / item["path"]
            fpath.write_text(fpath.read_text() + "\nChanged to break the hash.\n")
        result = validate_api.validate_notes(project)
        assert not result["valid"], "notes must not survive when every cited source changes"


# ---------------------------------------------------------------------------
# F2: a note must not cite a span not in its source
# ---------------------------------------------------------------------------


class TestF2:
    """F2 (failure KPI): a note cites a span not in its source — forbidden."""

    def test_all_citations_reference_valid_spans(self, synthesis_api, project):
        evidence = _evidence_set(project)
        result = synthesis_api.synthesize(project, evidence, SMALL_BUDGET)
        for group in result["notes"]:
            for citation in group["citations"]:
                fpath = Path(project) / citation["path"]
                assert fpath.is_file(), f"cited path {citation['path']} does not exist"
                lines = fpath.read_bytes().splitlines(keepends=True)
                s, e = citation["start_line"], citation["end_line"]
                assert 1 <= s <= e <= len(lines), \
                    f"line range {s}-{e} out of bounds (file has {len(lines)} lines)"
                actual = support.sha256(b"".join(lines[s - 1:e]))
                assert actual == citation["source_sha256"], \
                    f"citation sha256 for {citation['source_id']} does not match actual span"
