"""Unit tests for context building in gov close (DEC-454)."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest


class TestBuildContext:
    @patch("gov.decisions.check")
    @patch("gov.store.loader.load")
    @patch("gov.context.context")
    def test_structural_findings_refuse_context(self, mock_ctx, mock_load, mock_dec):
        from gov.close.command import _build_context

        mock_dec.return_value = [
            {"code": "ACTIVE_SUPERSEDED", "ids": ["DEC-1"]},
        ]
        h, decs, err = _build_context(Path("/fake"), "T-1", {})
        assert err is not None
        assert "ACTIVE_SUPERSEDED" in err
        mock_ctx.assert_not_called()

    @patch("gov.decisions.check")
    @patch("gov.store.loader.load")
    @patch("gov.context.context")
    def test_duplicate_id_refuses_context(self, mock_ctx, mock_load, mock_dec):
        from gov.close.command import _build_context

        mock_dec.return_value = [
            {"code": "DUPLICATE_ID", "ids": ["DEC-X"]},
        ]
        h, decs, err = _build_context(Path("/fake"), "T-1", {})
        assert err is not None
        assert "DUPLICATE_ID" in err

    @patch("gov.decisions.check")
    @patch("gov.store.loader.load")
    @patch("gov.context.context")
    def test_overlapping_id_refuses_context(self, mock_ctx, mock_load, mock_dec):
        from gov.close.command import _build_context

        mock_dec.return_value = [
            {"code": "OVERLAPPING_ID", "ids": ["DEC-A"]},
        ]
        h, decs, err = _build_context(Path("/fake"), "T-1", {})
        assert err is not None
        assert "OVERLAPPING_ID" in err

    @patch("gov.decisions.check")
    @patch("gov.store.loader.load")
    @patch("gov.context.context")
    def test_unapproved_does_not_refuse(self, mock_ctx, mock_load, mock_dec):
        from gov.close.command import _build_context

        mock_dec.return_value = [
            {"code": "ACTIVE_UNAPPROVED", "ids": ["DEC-2"]},
        ]
        mock_ctx.return_value = {"hash": "abc123", "mandatory": []}
        h, decs, err = _build_context(Path("/fake"), "T-1", {})
        assert err is None
        assert h == "abc123"

    @patch("gov.decisions.check")
    @patch("gov.store.loader.load")
    @patch("gov.context.context")
    def test_context_success_returns_hash_and_decisions(
            self, mock_ctx, mock_load, mock_dec):
        from gov.close.command import _build_context

        mock_dec.return_value = []
        mock_ctx.return_value = {
            "hash": "deadbeef",
            "mandatory": [
                {"id": "DEC-100", "authority": "decision"},
                {"id": "REQ-1", "authority": "requirement"},
            ],
        }
        h, decs, err = _build_context(Path("/fake"), "T-1", {})
        assert err is None
        assert h == "deadbeef"
        assert decs == ["DEC-100"]

    @patch("gov.decisions.check")
    @patch("gov.store.loader.load")
    @patch("gov.context.context")
    def test_context_failure_falls_back_to_hash(
            self, mock_ctx, mock_load, mock_dec):
        from gov.close.command import _build_context, _hash_from_inputs

        mock_dec.return_value = []
        mock_ctx.side_effect = RuntimeError("no store")
        h, decs, err = _build_context(Path("/fake"), "T-1", {})
        assert err is None
        assert h != ""
        assert decs == []


class TestIsCloseInfra:
    def test_docs_close_path_is_infra(self):
        from gov.close.command import _is_close_infra
        assert _is_close_infra("docs/close/T-1/CL-T-1.md", "W1-test")

    def test_docs_checkpoint_path_is_infra(self):
        from gov.close.command import _is_close_infra
        assert _is_close_infra("docs/checkpoints/T-1/CP-T-1.md", "W1-test")

    def test_gov_runtime_is_infra(self):
        from gov.close.command import _is_close_infra
        assert _is_close_infra(".gov-runtime/store.db", "W1-test")

    def test_ticket_file_is_infra(self):
        from gov.close.command import _is_close_infra
        assert _is_close_infra(".tickets/T-1.md", "W1-test")

    def test_acceptance_test_is_infra(self):
        from gov.close.command import _is_close_infra
        assert _is_close_infra("tests/acceptance/W1-test/test_foo.py", "W1-test")

    def test_source_file_is_not_infra(self):
        from gov.close.command import _is_close_infra
        assert not _is_close_infra("src/app.py", "W1-test")

    def test_different_wbs_acceptance_not_infra(self):
        from gov.close.command import _is_close_infra
        assert not _is_close_infra("tests/acceptance/W1-other/test_x.py", "W1-test")
