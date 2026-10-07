"""Unit tests for input hash computation in gov close."""
from __future__ import annotations

import hashlib
from pathlib import Path

import pytest


@pytest.fixture
def root(tmp_path):
    r = tmp_path / "project"
    r.mkdir()
    tickets = r / ".tickets"
    tickets.mkdir()
    return r


class TestBuildInputs:
    def test_ticket_hash_is_file_content(self, root):
        from gov.close.command import _build_inputs

        ticket_path = root / ".tickets" / "T-0001.md"
        content = b"---\nid: T-0001\nstatus: open\n---\n"
        ticket_path.write_bytes(content)
        expected = "sha256:" + hashlib.sha256(content).hexdigest()

        inputs = _build_inputs(root, "T-0001", {})
        ticket_input = next(i for i in inputs if i["id"] == "T-0001")
        assert ticket_input["hash"] == expected

    def test_ticket_hash_not_id_string(self, root):
        from gov.close.command import _build_inputs

        ticket_path = root / ".tickets" / "T-0001.md"
        content = b"---\nid: T-0001\nstatus: open\n---\n"
        ticket_path.write_bytes(content)
        bad_hash = "sha256:" + hashlib.sha256(b"T-0001").hexdigest()

        inputs = _build_inputs(root, "T-0001", {})
        ticket_input = next(i for i in inputs if i["id"] == "T-0001")
        assert ticket_input["hash"] != bad_hash

    def test_source_hash_is_file_content(self, root):
        from gov.close.command import _build_inputs

        ticket_path = root / ".tickets" / "T-0001.md"
        ticket_path.write_bytes(b"ticket\n")

        source_path = root / ".tickets" / "SRC-01.md"
        source_content = b"---\nid: SRC-01\n---\nsource content\n"
        source_path.write_bytes(source_content)
        expected = "sha256:" + hashlib.sha256(source_content).hexdigest()

        inputs = _build_inputs(root, "T-0001", {"sources": ["SRC-01"]})
        source_input = next(i for i in inputs if i["id"] == "SRC-01")
        assert source_input["hash"] == expected
