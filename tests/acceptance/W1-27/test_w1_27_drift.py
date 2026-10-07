"""KPI success 6: doctor reports Claude Code drift (DEC-210, DEC-214).

The CLI at ``~/.local/bin/claude`` and the active VS Code extension differing
from each other, either being newer than the registry's record, or the
extension's bundled binary at the recorded version with another sha256, is
reported as drift; the CLI or the active extension below the minimum, 2.1.285,
or the CLI at the recorded version with another sha256, is a failure.

Claude Code drift is tested with fake binaries in temporary directories and
never by touching the installed CLI or extension.
"""

from __future__ import annotations

import hashlib
import json
import os
import stat
from pathlib import Path

import pytest

import w1_27_support as support


def _fake_cli(sandbox, version):
    """Create a fake ``claude`` CLI in the sandbox bin directory, returning ``(path, sha256)``."""
    cli_path = sandbox.bin / "claude"
    body = f"#!/bin/sh\necho '{version}'\n"
    cli_path.write_text(body, encoding="utf-8")
    cli_path.chmod(cli_path.stat().st_mode | stat.S_IEXEC)
    sha = hashlib.sha256(cli_path.read_bytes()).hexdigest()
    return cli_path, sha


def _fake_extension(tmp_path, version, binary_body=None):
    """Create a fake VS Code extension directory, returning ``(ext_dir, bundled_binary_sha256)``."""
    ext_dir = tmp_path / "extensions" / f"anthropic.claude-code-{version}"
    ext_dir.mkdir(parents=True, exist_ok=True)

    import json as _json
    exts_file = tmp_path / "extensions" / "extensions.json"
    exts_file.write_text(_json.dumps([{
        "identifier": {"id": "anthropic.claude-code"},
        "version": version,
        "location": {"path": str(ext_dir)},
    }]), encoding="utf-8")

    (ext_dir / "package.json").write_text(_json.dumps({
        "name": "claude-code", "version": version,
    }), encoding="utf-8")

    binary_dir = ext_dir / "resources" / "native-binary"
    binary_dir.mkdir(parents=True, exist_ok=True)
    binary_path = binary_dir / "claude"
    body = binary_body or f"#!/bin/sh\necho 'ext {version}'\n"
    binary_path.write_text(body, encoding="utf-8")
    binary_path.chmod(binary_path.stat().st_mode | stat.S_IEXEC)
    sha = hashlib.sha256(binary_path.read_bytes()).hexdigest()
    return ext_dir.parent, sha


def _registry_for_claude_code(version, sha256):
    return support.tool_entry_yaml("claude code", version, sha256,
                                   install="echo test", uninstall="echo test",
                                   date="2026-01-01", approved_by="test")


# --------------------------------------------------------------------------
# Drift (reported, not a hard failure)
# --------------------------------------------------------------------------

def test_cli_newer_than_registry_is_drift(gov, project, sandbox, interface, tmp_path):
    """The CLI being newer than the registry record is reported as drift."""
    _, cli_sha = _fake_cli(sandbox, "2.1.300")
    registry = _registry_for_claude_code("2.1.288", cli_sha)
    support.write_tool_registry(project, registry)
    run = gov("doctor", "--json")
    text = json.dumps(run.envelope()).lower()
    assert "drift" in text, f"doctor does not report drift for CLI newer than registry\n{run.describe()}"


def test_cli_and_extension_different_versions_is_drift(gov, project, sandbox, interface, tmp_path):
    """The CLI and the extension at different versions is reported as drift."""
    _, cli_sha = _fake_cli(sandbox, "2.1.288")
    _, ext_sha = _fake_extension(tmp_path, "2.1.290")
    registry = _registry_for_claude_code("2.1.288", cli_sha)
    support.write_tool_registry(project, registry)
    run = gov("doctor", "--json")
    text = json.dumps(run.envelope()).lower()
    assert "drift" in text, f"doctor does not report drift for CLI/extension version mismatch\n{run.describe()}"


def test_extension_bundled_binary_different_sha256_is_drift(gov, project, sandbox, interface, tmp_path):
    """The extension's bundled binary at the recorded version with a different sha256 is drift (DEC-214)."""
    _, cli_sha = _fake_cli(sandbox, "2.1.288")
    _, ext_sha = _fake_extension(tmp_path, "2.1.288", binary_body="#!/bin/sh\n# different body\necho '2.1.288'\n")
    registry = _registry_for_claude_code("2.1.288", cli_sha)
    support.write_tool_registry(project, registry)
    run = gov("doctor", "--json")
    text = json.dumps(run.envelope()).lower()
    assert "drift" in text, \
        f"doctor does not report drift for extension binary sha256 mismatch\n{run.describe()}"


# --------------------------------------------------------------------------
# Hard failure
# --------------------------------------------------------------------------

def test_cli_below_minimum_is_failure(gov, project, sandbox, interface, tmp_path):
    """The CLI below the minimum version 2.1.285 is a hard failure, not just drift."""
    _, cli_sha = _fake_cli(sandbox, "2.1.280")
    registry = _registry_for_claude_code("2.1.288", cli_sha)
    support.write_tool_registry(project, registry)
    run = gov("doctor", "--json")
    envelope = support.assert_envelope(run, interface, command="doctor")
    assert envelope["ok"] is not True, \
        f"doctor passes with CLI below minimum version\n{run.describe()}"


def test_extension_below_minimum_is_failure(gov, project, sandbox, interface, tmp_path):
    """The active extension below the minimum version 2.1.285 is a hard failure."""
    _, cli_sha = _fake_cli(sandbox, "2.1.288")
    _, ext_sha = _fake_extension(tmp_path, "2.1.280")
    registry = _registry_for_claude_code("2.1.288", cli_sha)
    support.write_tool_registry(project, registry)
    run = gov("doctor", "--json")
    envelope = support.assert_envelope(run, interface, command="doctor")
    assert envelope["ok"] is not True, \
        f"doctor passes with extension below minimum version\n{run.describe()}"


def test_cli_at_recorded_version_different_sha256_is_failure(gov, project, sandbox, interface, tmp_path):
    """The CLI at the recorded version with a different sha256 is a hard failure (DEC-214)."""
    _, cli_sha = _fake_cli(sandbox, "2.1.288")
    registry = _registry_for_claude_code("2.1.288", "0" * 64)
    support.write_tool_registry(project, registry)
    run = gov("doctor", "--json")
    envelope = support.assert_envelope(run, interface, command="doctor")
    assert envelope["ok"] is not True, \
        f"doctor passes with CLI sha256 mismatch at recorded version\n{run.describe()}"
