"""Regression tests for the evidence-bundle validator (DEC-136)."""
from __future__ import annotations

import hashlib
from pathlib import Path

from gov.retrieval.validate import validate, REASONS


def _file(tmp_path, rel="docs/sample.md", text="line one\nline two\nline three\n"):
    path = tmp_path / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return rel, text


def _bundle(root, rel, start=1, end=None):
    lines = (root / rel).read_bytes().splitlines(keepends=True)
    if end is None:
        end = len(lines)
    span = b"".join(lines[start - 1:end])
    return {"stopping_reason": "SATURATED",
            "evidence": [{"path": rel, "start_line": start, "end_line": end,
                          "sha256": hashlib.sha256(span).hexdigest(),
                          "text": span.decode("utf-8", "replace")}]}


def test_accepts_valid_bundle(tmp_path):
    rel, _ = _file(tmp_path)
    result = validate(tmp_path, _bundle(tmp_path, rel))
    assert result["valid"] is True
    assert result["errors"] == []


def test_accepts_every_fixed_reason(tmp_path):
    rel, _ = _file(tmp_path)
    for reason in REASONS:
        b = _bundle(tmp_path, rel)
        b["stopping_reason"] = reason
        assert validate(tmp_path, b)["valid"] is True


def test_rejects_missing_reason(tmp_path):
    rel, _ = _file(tmp_path)
    b = _bundle(tmp_path, rel)
    del b["stopping_reason"]
    result = validate(tmp_path, b)
    assert result["valid"] is False
    assert any(e["code"] == "MISSING_STOPPING_REASON" for e in result["errors"])


def test_rejects_invalid_reason(tmp_path):
    rel, _ = _file(tmp_path)
    b = _bundle(tmp_path, rel)
    b["stopping_reason"] = "NOT_FOUND"
    result = validate(tmp_path, b)
    assert result["valid"] is False
    assert any(e["code"] == "INVALID_STOPPING_REASON" for e in result["errors"])


def test_rejects_missing_file(tmp_path):
    rel, _ = _file(tmp_path)
    b = _bundle(tmp_path, rel)
    b["evidence"][0]["path"] = "no/such.md"
    result = validate(tmp_path, b)
    assert result["valid"] is False
    assert any(e["code"] == "FILE_NOT_FOUND" for e in result["errors"])


def test_rejects_stale_hash(tmp_path):
    rel, _ = _file(tmp_path)
    b = _bundle(tmp_path, rel)
    b["evidence"][0]["sha256"] = hashlib.sha256(b"wrong").hexdigest()
    result = validate(tmp_path, b)
    assert result["valid"] is False
    assert any(e["code"] == "HASH_MISMATCH" for e in result["errors"])


def test_rejects_absent_text(tmp_path):
    rel, _ = _file(tmp_path)
    b = _bundle(tmp_path, rel)
    b["evidence"][0]["text"] = "not in the file at all"
    result = validate(tmp_path, b)
    assert result["valid"] is False
    assert any(e["code"] == "TEXT_NOT_FOUND" for e in result["errors"])


def test_reports_multiple_errors(tmp_path):
    rel, _ = _file(tmp_path)
    b = _bundle(tmp_path, rel)
    b["stopping_reason"] = "BOGUS"
    b["evidence"][0]["path"] = "gone.md"
    result = validate(tmp_path, b)
    assert result["valid"] is False
    assert len(result["errors"]) >= 2


def test_span_hash_not_whole_file(tmp_path):
    rel, _ = _file(tmp_path)
    b = _bundle(tmp_path, rel, start=1, end=1)
    whole = (tmp_path / rel).read_bytes()
    b["evidence"][0]["sha256"] = hashlib.sha256(whole).hexdigest()
    result = validate(tmp_path, b)
    assert result["valid"] is False


def test_empty_evidence_is_valid(tmp_path):
    result = validate(tmp_path, {"stopping_reason": "FACET_UNAVAILABLE", "evidence": []})
    assert result["valid"] is True
