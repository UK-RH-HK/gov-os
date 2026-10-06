"""Unit tests for gov.doctor internal functions (DEC-135: regression evidence)."""

from __future__ import annotations

import hashlib
import json
import os
import stat
import tempfile
from pathlib import Path
from unittest import mock

import pytest


def test_version_tuple():
    from gov.doctor.command import _version_tuple
    assert _version_tuple("2.1.285") == (2, 1, 285)
    assert _version_tuple("v22.23.3") == (22, 23, 3)
    assert _version_tuple("0.12.21") == (0, 12, 21)


def test_version_comparison():
    from gov.doctor.command import _version_tuple
    assert _version_tuple("2.1.285") < _version_tuple("2.1.288")
    assert _version_tuple("2.1.300") > _version_tuple("2.1.288")
    assert _version_tuple("2.1.280") < _version_tuple("2.1.285")


def test_sha256_file(tmp_path):
    from gov.doctor.command import _sha256_file
    f = tmp_path / "test.txt"
    f.write_text("hello", encoding="utf-8")
    expected = hashlib.sha256(b"hello").hexdigest()
    assert _sha256_file(f) == expected


def test_sha256_file_missing(tmp_path):
    from gov.doctor.command import _sha256_file
    assert _sha256_file(tmp_path / "no-such-file") is None


def test_match_pattern():
    from gov.doctor.command import _match_pattern
    assert _match_pattern("src/gov/doctor/command.py", "src/**")
    assert _match_pattern("README.md", "*")
    assert not _match_pattern("src/gov/doctor/command.py", "docs/**")
    assert _match_pattern("lefthook.yml", "*")
    assert _match_pattern(".claude/settings.json", ".claude/**")


def test_check_held_out_missing(tmp_path):
    from gov.doctor.command import _check_held_out
    result = _check_held_out(tmp_path)
    assert result["missing"] is True
    assert result["status"] == "report"


def test_check_held_out_present(tmp_path):
    from gov.doctor.command import _check_held_out
    held = tmp_path / "governance" / "project" / "held-out.yaml"
    held.parent.mkdir(parents=True)
    held.write_text("", encoding="utf-8")
    result = _check_held_out(tmp_path)
    assert result["missing"] is False
    assert result["status"] == "pass"


def test_check_hooks_no_config(tmp_path):
    from gov.doctor.command import _check_hooks
    result = _check_hooks(tmp_path)
    assert result["config_present"] is False


def test_check_isolation(tmp_path):
    from gov.doctor.command import _check_isolation
    result = _check_isolation(tmp_path)
    assert result["isolated"] is True


def test_check_adoption_level_minimal(tmp_path):
    from gov.doctor.command import _check_adoption_level
    result = _check_adoption_level(tmp_path, {})
    assert result["level"] == "MINIMAL"


def test_check_framework_lock_missing(tmp_path):
    from gov.doctor.command import _check_framework_lock
    result = _check_framework_lock(tmp_path)
    assert result["match"] == "MISSING"
    assert result["status"] == "unmeasured"
