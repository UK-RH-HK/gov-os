"""Unit tests for gov.adapters.portability internal functions."""

from __future__ import annotations

import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src"))

from gov.adapters import portability


class TestFindRulesync:
    def test_returns_explicit_bin_when_file_exists(self, tmp_path):
        mock = tmp_path / "rulesync"
        mock.write_text("#!/bin/sh\n")
        env = {"RULESYNC_BIN": str(mock)}
        orig = os.environ.get("RULESYNC_BIN")
        os.environ["RULESYNC_BIN"] = str(mock)
        try:
            assert portability._find_rulesync() == str(mock)
        finally:
            if orig is None:
                os.environ.pop("RULESYNC_BIN", None)
            else:
                os.environ["RULESYNC_BIN"] = orig

    def test_returns_none_when_explicit_bin_missing(self):
        orig = os.environ.get("RULESYNC_BIN")
        os.environ["RULESYNC_BIN"] = "/nonexistent/rulesync"
        try:
            assert portability._find_rulesync() is None
        finally:
            if orig is None:
                os.environ.pop("RULESYNC_BIN", None)
            else:
                os.environ["RULESYNC_BIN"] = orig


class TestReadProjectConfig:
    def test_returns_empty_when_no_config(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        assert portability._read_project_config() == {}

    def test_reads_version_from_config(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "rulesync.jsonc").write_text(json.dumps({"version": "24.0.0"}))
        config = portability._read_project_config()
        assert config["version"] == "24.0.0"


class TestSourceEmpty:
    def test_empty_when_no_dir(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        assert portability._source_empty() is True

    def test_empty_when_dir_empty(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".rulesync").mkdir()
        assert portability._source_empty() is True

    def test_not_empty_when_has_files(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        rs = tmp_path / ".rulesync"
        rs.mkdir()
        (rs / "hooks.jsonc").write_text("{}")
        assert portability._source_empty() is False


class TestCheckVersion:
    def test_mismatch_detected(self, tmp_path):
        mock = tmp_path / "rulesync"
        mock.write_text('#!/bin/bash\necho "99.0.0"\n')
        mock.chmod(0o755)
        err = portability._check_version(str(mock), "24.0.0")
        assert err is not None
        assert "version" in err.lower()

    def test_match_passes(self, tmp_path):
        mock = tmp_path / "rulesync"
        mock.write_text('#!/bin/bash\necho "24.0.0"\n')
        mock.chmod(0o755)
        err = portability._check_version(str(mock), "24.0.0")
        assert err is None
