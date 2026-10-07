"""The context of a close is ``gov.context``'s, or the close is refused with its reason (DEC-454, DEC-470)."""
from __future__ import annotations

import sqlite3
from pathlib import Path
from unittest.mock import patch

import pytest

from gov.cli.errors import GovError
from gov.close import command
from gov.close.command import _build_context, _Finding

ROOT = Path("/no-such-project")
PACKET = {"hash": "ab" * 32, "mandatory": [{"id": "DEC-1", "authority": "decision", "sha256": "cd" * 32}]}


def _refused(context=None, decisions=None):
    with patch("gov.context.context", side_effect=context, return_value=PACKET), \
            patch("gov.decisions.check", side_effect=decisions, return_value=[]):
        with pytest.raises(_Finding) as raised:
            _build_context(ROOT, "T-1")
    assert raised.value.code == "CONTEXT_FAILED"
    return raised.value


def test_the_packet_is_the_one_gov_context_built():
    with patch("gov.context.context", return_value=PACKET) as built, \
            patch("gov.decisions.check", return_value=[]):
        assert _build_context(ROOT, "T-1") is PACKET
    built.assert_called_once_with(ROOT, "T-1")


@pytest.mark.parametrize("code, message, details", [
    ("STORE_MISSING", "no store at /p; load it first", {"root": "/p"}),
    ("BLOCKED", "mandatory input 'DEC-gone' not found in the store", {"missing": "DEC-gone"}),
    ("BLOCKED", "mandatory input 'DEC-old' is superseded", {"superseded": "DEC-old"}),
    ("CONTRADICTION", "conflicting mandatory inputs: 'DEC-a' and 'DEC-b'", {"conflicting": ["DEC-a", "DEC-b"]}),
])
def test_every_error_of_gov_context_refuses_with_its_reason(code, message, details):
    finding = _refused(context=GovError(code, message, details))
    assert code in finding.message and message in finding.message
    assert finding.details["context_error"] == code
    assert details.items() <= finding.details.items()


def test_a_store_that_cannot_be_read_refuses():
    assert "locked" in _refused(context=sqlite3.OperationalError("database is locked")).message


def test_a_decision_checker_that_cannot_run_refuses():
    finding = _refused(decisions=GovError("DECISIONS_HISTORY_UNREADABLE", "a shallow clone"))
    assert "decisions could not be checked" in finding.message and "a shallow clone" in finding.message


@pytest.mark.parametrize("code", ["ACTIVE_SUPERSEDED", "DUPLICATE_ID", "OVERLAPPING_ID"])
def test_a_contradictory_register_refuses(code):
    with patch("gov.context.context", return_value=PACKET), \
            patch("gov.decisions.check", return_value=[{"code": code, "ids": ["DEC-1"]}]):
        with pytest.raises(_Finding) as raised:
            _build_context(ROOT, "T-1")
    assert code in raised.value.message


def test_another_finding_of_the_checker_does_not_refuse():
    with patch("gov.context.context", return_value=PACKET), \
            patch("gov.decisions.check", return_value=[{"code": "ACTIVE_UNAPPROVED", "ids": ["DEC-1"]}]):
        assert _build_context(ROOT, "T-1") is PACKET


def test_the_close_builds_no_store_and_has_no_hash_of_its_own():
    """DEC-470: building the store is ``gov rebuild``'s work; no fallback hash exists."""
    source = Path(command.__file__).read_text(encoding="utf-8")
    assert "gov.store" not in source and "import load" not in source
    assert not hasattr(command, "_hash_from_inputs") and not hasattr(command, "_try_context_hash")
