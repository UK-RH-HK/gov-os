"""Unit tests for the canary runner's handling of empty and malformed declarations (DEC-136).

The canary runner reads declarations from a fixed template path (_TEMPLATE) and queries
indexes through _SEARCHERS.  These tests patch both to isolate declaration handling from
the actual search backends.

Red tests (1-3): the current runner treats empty or degenerate canary lists as a pass,
reporting AVAILABLE instead of FACET_UNAVAILABLE.  This is the fail-open shape of W1-22.
Green tests (4-5): the runner already handles missing files and non-dict YAML correctly;
these are regression guards.

Placed in tests/acceptance/W1-22/ because the ITD guard restricts writes to
tests/acceptance/**; the engineer should move this to tests/unit/validate/test_canary.py
(the ticket's allowed_paths include tests/unit/validate/**).
"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import yaml

from gov.retrieval.canary import run_canaries, FACET_UNAVAILABLE, AVAILABLE

_INDEXES = ("lexical", "semantic")


def _write_decl(directory: Path, index: str, content) -> None:
    (directory / f"{index}.yaml").write_text(
        yaml.dump(content), encoding="utf-8",
    )


def _dummy_searcher(root, query, refresh=False):
    return {"available": True, "hits": [{"path": "dummy.md"}]}


_MOCK_SEARCHERS = {idx: _dummy_searcher for idx in _INDEXES}


def _patched(template_dir):
    return (
        patch("gov.retrieval.canary._TEMPLATE", template_dir),
        patch("gov.retrieval.canary._SEARCHERS", _MOCK_SEARCHERS),
    )


class TestEmptyCanaryDeclarations:
    """Empty or null canary lists must report FACET_UNAVAILABLE, not AVAILABLE (DEC-136)."""

    def test_empty_canaries_list_reports_facet_unavailable(self, tmp_path):
        """canaries: [] -> FACET_UNAVAILABLE.

        Red reason: the loop body never runs, misses stays empty,
        passed is True, and the runner returns AVAILABLE.
        """
        for idx in _INDEXES:
            _write_decl(tmp_path, idx, {"canaries": []})
        p1, p2 = _patched(tmp_path)
        with p1, p2:
            result = run_canaries(tmp_path)
        for idx in _INDEXES:
            assert result[idx]["status"] == FACET_UNAVAILABLE, (
                f"{idx}: empty canaries list reports "
                f"{result[idx]['status']!r}, expected FACET_UNAVAILABLE"
            )
            assert result[idx]["passed"] is False

    def test_null_canaries_reports_facet_unavailable(self, tmp_path):
        """canaries: null -> FACET_UNAVAILABLE.

        Red reason: decl.get('canaries', []) returns None (key exists),
        then 'for canary in None' raises TypeError — the runner crashes.
        """
        for idx in _INDEXES:
            _write_decl(tmp_path, idx, {"canaries": None})
        p1, p2 = _patched(tmp_path)
        with p1, p2:
            result = run_canaries(tmp_path)
        for idx in _INDEXES:
            assert result[idx]["status"] == FACET_UNAVAILABLE, (
                f"{idx}: null canaries reports "
                f"{result[idx]['status']!r}, expected FACET_UNAVAILABLE"
            )
            assert result[idx]["passed"] is False

    def test_entry_without_query_reports_facet_unavailable(self, tmp_path):
        """canaries: [{}] -> FACET_UNAVAILABLE.

        Red reason: canary['query'] raises KeyError in the try block;
        the except handler also accesses canary['query'], raising a
        second KeyError that propagates uncaught — the runner crashes.
        """
        for idx in _INDEXES:
            _write_decl(tmp_path, idx, {"canaries": [{}]})
        p1, p2 = _patched(tmp_path)
        with p1, p2:
            result = run_canaries(tmp_path)
        for idx in _INDEXES:
            assert result[idx]["status"] == FACET_UNAVAILABLE, (
                f"{idx}: entry without query reports "
                f"{result[idx]['status']!r}, expected FACET_UNAVAILABLE"
            )
            assert result[idx]["passed"] is False


class TestMalformedDeclarations:
    """Missing or malformed YAML must report FACET_UNAVAILABLE (regression guards)."""

    def test_missing_yaml_reports_facet_unavailable(self, tmp_path):
        """No YAML file at all -> FACET_UNAVAILABLE (already handled)."""
        p1, p2 = _patched(tmp_path)
        with p1, p2:
            result = run_canaries(tmp_path)
        for idx in _INDEXES:
            assert result[idx]["status"] == FACET_UNAVAILABLE
            assert result[idx]["passed"] is False

    def test_non_dict_yaml_reports_facet_unavailable(self, tmp_path):
        """YAML that parses as a non-dict -> FACET_UNAVAILABLE (already handled)."""
        for idx in _INDEXES:
            (tmp_path / f"{idx}.yaml").write_text(
                "- just a list\n", encoding="utf-8",
            )
        p1, p2 = _patched(tmp_path)
        with p1, p2:
            result = run_canaries(tmp_path)
        for idx in _INDEXES:
            assert result[idx]["status"] == FACET_UNAVAILABLE
            assert result[idx]["passed"] is False
