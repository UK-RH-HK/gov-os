"""Unit tests for gov.util.digest (DEC-135: regression evidence; moved from tests/unit/doctor with the helper, DEC-1039 (2))."""

from __future__ import annotations

import hashlib

from gov.util.digest import sha256, sha256_file


def test_sha256_file(tmp_path):
    f = tmp_path / "test.txt"
    f.write_text("hello", encoding="utf-8")
    expected = hashlib.sha256(b"hello").hexdigest()
    assert sha256_file(f) == expected


def test_sha256_file_missing(tmp_path):
    assert sha256_file(tmp_path / "no-such-file") is None


def test_sha256_of_bytes():
    assert sha256(b"hello") == hashlib.sha256(b"hello").hexdigest()
