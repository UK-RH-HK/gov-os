"""Acceptance tests for the evidence validator (W1-22, S1, F1, CAP-57.a).

The validator checks an evidence bundle returned by ``retrieve()`` against the project on disk:

- the ``stopping_reason`` must be one of the six fixed reasons (ADR-0002 §4, DEC-034, DEC-396);
- every evidence item must cite a file that exists under ``root``;
- the ``sha256`` must match the cited span (``start_line`` to ``end_line``), **not** the whole file (stricter
  than W1-21's ``check_citation``, which accepts either; DEC-036);
- the quoted ``text`` must appear in the cited lines.

Interface fixed by this test suite (DP-1):

    ``gov.retrieval.validate.validate(root: Path, bundle: dict) -> dict``

    Returns ``{"valid": bool, "errors": [{"code": str, "message": str, ...}, ...]}``.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from w1_22_support import (
    build_fixture, sha256, span_bytes, valid_bundle,
    K_REASON, K_EVIDENCE, E_SHA, E_PATH, E_START, E_END, E_TEXT,
    V_VALID, V_ERRORS, REASONS, CANARY_FILE,
)


# ---------------------------------------------------------------------------
# S1 positive: the validator accepts a correct bundle
# ---------------------------------------------------------------------------

class TestValidatorAccepts:

    def test_validator_accepts_a_valid_bundle(self, validator_api, base, tmp_path):
        """A bundle with a valid reason, an existing file, a correct span hash and matching text passes."""
        root = _project(base, tmp_path)
        bundle = valid_bundle(root)
        result = validator_api.validate(root, bundle)
        assert result[V_VALID] is True, f"a correct bundle was rejected: {result}"
        assert result[V_ERRORS] == [], f"a correct bundle has errors: {result[V_ERRORS]}"

    def test_validator_accepts_each_fixed_stopping_reason(self, validator_api, base, tmp_path):
        """Every value in the fixed list is accepted (CAP-55.a)."""
        root = _project(base, tmp_path)
        for reason in REASONS:
            bundle = valid_bundle(root)
            bundle[K_REASON] = reason
            result = validator_api.validate(root, bundle)
            assert result[V_VALID] is True, f"the fixed reason {reason!r} was rejected: {result}"

    def test_validator_accepts_empty_evidence_with_valid_reason(self, validator_api, base, tmp_path):
        """An empty evidence list is valid when the stopping reason says why (e.g. FACET_UNAVAILABLE)."""
        root = _project(base, tmp_path)
        bundle = valid_bundle(root)
        bundle[K_EVIDENCE] = []
        bundle[K_REASON] = "FACET_UNAVAILABLE"
        result = validator_api.validate(root, bundle)
        assert result[V_VALID] is True, f"an empty bundle with a valid reason was rejected: {result}"


# ---------------------------------------------------------------------------
# S1 negative: the validator rejects defective bundles [CAP-57.a]
# ---------------------------------------------------------------------------

class TestValidatorRejects:

    def test_validator_rejects_bundle_without_stopping_reason(self, validator_api, base, tmp_path):
        root = _project(base, tmp_path)
        bundle = valid_bundle(root)
        del bundle[K_REASON]
        result = validator_api.validate(root, bundle)
        assert result[V_VALID] is False, "a bundle without a stopping reason was accepted"

    def test_validator_rejects_bundle_with_invalid_stopping_reason(self, validator_api, base, tmp_path):
        """NOT_FOUND is not a fixed stopping reason — it must be rejected (CAP-55.a)."""
        root = _project(base, tmp_path)
        bundle = valid_bundle(root)
        bundle[K_REASON] = "NOT_FOUND"
        result = validator_api.validate(root, bundle)
        assert result[V_VALID] is False, "a bundle with NOT_FOUND as stopping reason was accepted"

    def test_validator_rejects_unresolvable_citation(self, validator_api, base, tmp_path):
        """An evidence item that cites a path not under root must be rejected (DEC-036)."""
        root = _project(base, tmp_path)
        bundle = valid_bundle(root)
        bundle[K_EVIDENCE][0][E_PATH] = "no/such/file.md"
        result = validator_api.validate(root, bundle)
        assert result[V_VALID] is False, "a bundle citing a nonexistent file was accepted"

    def test_validator_rejects_stale_hash(self, validator_api, base, tmp_path):
        """The sha256 does not match the cited span (DEC-036)."""
        root = _project(base, tmp_path)
        bundle = valid_bundle(root)
        bundle[K_EVIDENCE][0][E_SHA] = sha256(b"wrong content entirely")
        result = validator_api.validate(root, bundle)
        assert result[V_VALID] is False, "a bundle with a stale hash was accepted"

    def test_validator_rejects_absent_span(self, validator_api, base, tmp_path):
        """The quoted text does not appear in the cited lines (DEC-036)."""
        root = _project(base, tmp_path)
        bundle = valid_bundle(root)
        bundle[K_EVIDENCE][0][E_TEXT] = "this text does not appear in any file of the fixture"
        result = validator_api.validate(root, bundle)
        assert result[V_VALID] is False, "a bundle with absent span text was accepted"

    def test_validator_checks_hash_against_span_not_whole_file(self, validator_api, base, tmp_path):
        """The hash must match the cited span only (start_line to end_line), not the whole file.

        This is stricter than W1-21's ``check_citation`` which accepts either (DP-4)."""
        root = _project(base, tmp_path)
        bundle = valid_bundle(root, start=1, end=1)
        item = bundle[K_EVIDENCE][0]
        rel = item[E_PATH]
        whole_bytes = (root / rel).read_bytes()
        first_line = span_bytes(root, rel, 1, 1)
        if sha256(whole_bytes) == sha256(first_line):
            pytest.skip("the first line is the entire file; cannot distinguish span from whole-file hash")
        item[E_SHA] = sha256(whole_bytes)
        result = validator_api.validate(root, bundle)
        assert result[V_VALID] is False, \
            "the validator accepted a whole-file hash when only the span hash should be valid"

    def test_validator_rejects_citation_with_out_of_range_lines(self, validator_api, base, tmp_path):
        root = _project(base, tmp_path)
        bundle = valid_bundle(root)
        bundle[K_EVIDENCE][0][E_START] = 1
        bundle[K_EVIDENCE][0][E_END] = 9999
        bundle[K_EVIDENCE][0][E_SHA] = sha256(b"placeholder")
        result = validator_api.validate(root, bundle)
        assert result[V_VALID] is False, "a bundle with out-of-range line numbers was accepted"

    def test_validator_reports_multiple_errors(self, validator_api, base, tmp_path):
        """When a bundle has several defects, all are reported."""
        root = _project(base, tmp_path)
        bundle = valid_bundle(root)
        bundle[K_REASON] = "BOGUS"
        bundle[K_EVIDENCE][0][E_PATH] = "no/such/file.md"
        result = validator_api.validate(root, bundle)
        assert result[V_VALID] is False
        assert len(result[V_ERRORS]) >= 2, \
            f"expected at least two errors but got {len(result[V_ERRORS])}: {result[V_ERRORS]}"


# ---------------------------------------------------------------------------
# F1: a bundle with an unresolvable citation must NOT pass
# ---------------------------------------------------------------------------

class TestF1:

    def test_an_unresolvable_citation_does_not_pass(self, validator_api, base, tmp_path):
        """F1: an evidence item citing a path that does not exist under root must be rejected.

        This is the ticket's failure KPI — the validator must never silently accept a broken citation."""
        root = _project(base, tmp_path)
        bundle = valid_bundle(root)
        bundle[K_EVIDENCE][0][E_PATH] = "deleted/vanished.md"
        result = validator_api.validate(root, bundle)
        assert result[V_VALID] is False, \
            "F1 violated: a bundle with an unresolvable citation passed the validator"
        codes = [error.get("code", "") for error in result.get(V_ERRORS, [])]
        assert any(codes), f"F1: the error list is empty or has no codes: {result}"


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _project(base, tmp_path):
    """A copy of the base fixture in this test's temporary directory."""
    dest = tmp_path / "project"
    import shutil
    shutil.copytree(base, dest)
    return dest
