"""Unit tests for gov.doctor internal functions (DEC-135: regression evidence)."""

from __future__ import annotations

import hashlib
import json
import os
import stat
import subprocess
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
    assert result["status"] == "unmeasured"
    assert "method" in result


def test_check_adoption_level_minimal(tmp_path):
    from gov.doctor.command import _check_adoption_level
    result = _check_adoption_level(tmp_path, {})
    assert result["level"] == "MINIMAL"


def test_check_framework_lock_missing(tmp_path):
    from gov.doctor.command import _check_framework_lock
    result = _check_framework_lock(tmp_path)
    assert result["match"] == "MISSING"
    assert result["status"] == "unmeasured"


def test_home_uses_env():
    from gov.doctor.command import _home
    with mock.patch.dict(os.environ, {"HOME": "/tmp/test-fake-home"}):
        assert _home() == Path("/tmp/test-fake-home")


def test_vendored_folder_digest(tmp_path):
    from gov.doctor.command import _vendored_folder_digest
    vendor = tmp_path / "vendor" / "tool"
    vendor.mkdir(parents=True)
    (vendor / "A.txt").write_bytes(b"aaa\n")
    sub = vendor / "sub"
    sub.mkdir()
    (sub / "B.txt").write_bytes(b"bbb\n")
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=str(tmp_path), check=True)
    subprocess.run(["git", "add", "-A"], cwd=str(tmp_path), check=True)
    subprocess.run(["git", "commit", "-q", "-m", "init"], cwd=str(tmp_path), check=True,
                    env={**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
                         "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"})
    digest = _vendored_folder_digest(vendor, tmp_path)
    assert digest is not None
    files = {"A.txt": b"aaa\n", "sub/B.txt": b"bbb\n"}
    lines = sorted(f"{hashlib.sha256(c).hexdigest()}  {r}\n".encode() for r, c in files.items())
    expected = hashlib.sha256(b"".join(lines)).hexdigest()
    assert digest == expected


def test_pyyaml_version_compared():
    from gov.doctor.command import _check_no_binary_tool
    result = _check_no_binary_tool("pyyaml", "99.99.99", "0" * 64, Path("/nonexistent"))
    assert result["ok"] is not True
    assert result["sha256_match"] is not True
    assert "reason" in result


def test_pyyaml_sha256_match_always_false():
    from gov.doctor.command import _check_no_binary_tool
    import yaml
    result = _check_no_binary_tool("pyyaml", yaml.__version__, "0" * 64, Path("/nonexistent"))
    assert result["ok"] is True
    assert result["sha256_match"] is False


def test_parse_version_list():
    from gov.doctor.command import _parse_version_list
    parsed = _parse_version_list("sentence-transformers 6.1.0, torch 2.14.1+cu130, transformers 5.18.0")
    assert parsed == {"sentence-transformers": "6.1.0", "torch": "2.14.1+cu130", "transformers": "5.18.0"}


def test_read_dist_version(tmp_path):
    from gov.doctor.command import _read_dist_version
    dist = tmp_path / "my_package-1.2.3.dist-info"
    dist.mkdir()
    (dist / "METADATA").write_text("Metadata-Version: 2.1\nName: my-package\nVersion: 1.2.3\n\nDescription.\n")
    assert _read_dist_version(tmp_path, "my-package") == "1.2.3"
    assert _read_dist_version(tmp_path, "my_package") == "1.2.3"
    assert _read_dist_version(tmp_path, "other") is None


class TestHasStandaloneOldPath:
    """Unit tests for the occurrence-level sub-path logic (DEC-456 point 3)."""

    def _fn(self, content, old_path, new_path):
        from gov.doctor.command import _has_standalone_old_path
        return _has_standalone_old_path(content, old_path, new_path)

    def test_old_path_only_inside_new_path(self):
        assert self._fn(
            'FRAMEWORK_PATH = "docs/source/originals/target.py"\n',
            "target.py",
            "docs/source/originals/target.py",
        ) is False

    def test_old_path_standalone(self):
        assert self._fn(
            'OLD = "target.py"\n',
            "target.py",
            "docs/source/originals/target.py",
        ) is True

    def test_old_path_standalone_alongside_new_path(self):
        assert self._fn(
            'NEW = "docs/source/originals/target.py"\nOLD = "target.py"\n',
            "target.py",
            "docs/source/originals/target.py",
        ) is True

    def test_no_old_path_at_all(self):
        assert self._fn(
            "no reference here\n",
            "target.py",
            "docs/source/originals/target.py",
        ) is False

    def test_old_path_not_suffix_of_new(self):
        assert self._fn(
            'import old_mod\n',
            "old_mod",
            "new_mod",
        ) is True

    def test_multiple_new_path_occurrences_hide_old(self):
        assert self._fn(
            'a = "lib/foo.py"\nb = "lib/foo.py"\n',
            "foo.py",
            "lib/foo.py",
        ) is False

    def test_old_path_between_new_paths(self):
        assert self._fn(
            'a = "lib/foo.py"\nb = "foo.py"\nc = "lib/foo.py"\n',
            "foo.py",
            "lib/foo.py",
        ) is True


class TestIsHistorical:
    """Unit tests for the historical-path classification (DEC-448, DEC-456)."""

    def _fn(self, path):
        from gov.doctor.command import _is_historical
        return _is_historical(path)

    def test_decision_register(self):
        assert self._fn("docs/DECISION_REGISTER.md") is True

    def test_cit_records(self):
        assert self._fn("docs/changes/W1-01.md") is True

    def test_bootstrap(self):
        assert self._fn("governance/project/bootstrap.md") is True

    def test_archived_sources(self):
        assert self._fn("docs/source/original.py") is True

    def test_sources_md(self):
        assert self._fn("docs/SOURCES.md") is True

    def test_old_cli_tree(self):
        assert self._fn("cli/commands.py") is True

    def test_old_cli_root(self):
        assert self._fn("cli/main.py") is True

    def test_src_gov_cli_is_not_historical(self):
        assert self._fn("src/gov/cli/commands.py") is False

    def test_live_file(self):
        assert self._fn("src/gov/doctor/command.py") is False

    def test_nested_cli_is_not_historical(self):
        assert self._fn("src/gov/cli/sub/module.py") is False
