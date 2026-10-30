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
import os
import stat

import w1_27_support as support
import w2_67_doctor


def _fake_cli(sandbox, version):
    """Create a fake ``claude`` CLI in the sandbox bin directory, returning ``(path, sha256)``.

    The directory is put first on the PATH doctor sees by ``_doctor`` (doctor finds the CLI on its PATH).
    """
    cli_path = sandbox.bin / "claude"
    body = f"#!/bin/sh\necho '{version}'\n"
    cli_path.write_text(body, encoding="utf-8")
    cli_path.chmod(cli_path.stat().st_mode | stat.S_IEXEC)
    sha = hashlib.sha256(cli_path.read_bytes()).hexdigest()
    return cli_path, sha


def _fake_extension(sandbox, version, binary_body=None):
    """Create a fake VS Code extension directory under the sandbox home's ``.vscode-server/extensions``, where
    doctor looks for the active extension, returning ``(extensions_dir, bundled_binary_sha256)``."""
    extensions = sandbox.home / ".vscode-server" / "extensions"
    ext_dir = extensions / f"anthropic.claude-code-{version}"
    ext_dir.mkdir(parents=True, exist_ok=True)

    import json as _json
    exts_file = extensions / "extensions.json"
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


# Revised (W2-67, I4 F1; Rewrite-Reason: the fake CLI is never read, and the planted extension is not where doctor
# reads it): the fake CLI lay in sandbox.bin, which was not on the doctor process's PATH, so doctor read this
# machine's real CLI, and the fake extension lay under tmp_path, not under the home where doctor looks; the drift
# cases found the key ``drift``, always there, and the failure cases passed on the real CLI's own drift. Each case
# now puts the fake CLI first on the PATH doctor sees and the fake extension under HOME/.vscode-server/extensions,
# runs doctor on a small committed project of its own with this worktree's code, and reads the claude_code
# section: the versions read are the fakes', and the issue the rule raises is there with its type.

def _doctor(tmp_path, sandbox, monkeypatch, registry):
    """``gov doctor --json`` on a small project with ``registry``, the sandbox's bin first on PATH; the
    claude_code section and the run."""
    project = w2_67_doctor.small_project(tmp_path / "repo")
    support.write_tool_registry(project, registry)
    monkeypatch.setenv("PATH", f"{sandbox.bin}{os.pathsep}{os.environ.get('PATH', '/usr/bin:/bin')}")
    run = w2_67_doctor.doctor(project, sandbox)
    return w2_67_doctor.section(run, "claude_code"), run


def _issues(section, kind):
    """The issue details of one type (``drift`` or ``failure``)."""
    return [str(issue.get("detail")) for issue in section.get("issues") or []
            if isinstance(issue, dict) and issue.get("type") == kind]


# --------------------------------------------------------------------------
# Drift (reported, not a hard failure)
# --------------------------------------------------------------------------

def test_cli_newer_than_registry_is_drift(sandbox, tmp_path, monkeypatch):
    """The CLI being newer than the registry record is reported as drift."""
    _, cli_sha = _fake_cli(sandbox, "2.1.300")
    section, run = _doctor(tmp_path, sandbox, monkeypatch, _registry_for_claude_code("2.1.288", cli_sha))
    assert section.get("cli_version") == "2.1.300", f"doctor did not read the fake CLI: {section}\n{run.describe()}"
    drift = [detail for detail in _issues(section, "drift") if "2.1.300" in detail and "2.1.288" in detail]
    assert drift and section.get("drift") is True and section.get("status") == "drift", (
        f"doctor does not report drift for CLI newer than registry: {section}\n{run.describe()}"
    )
    assert not _issues(section, "failure"), f"a newer CLI is a failure, not drift: {section}\n{run.describe()}"


def test_cli_and_extension_different_versions_is_drift(sandbox, tmp_path, monkeypatch):
    """The CLI and the extension at different versions is reported as drift.

    The registry records the extension's version and binary, so the only rule that applies is the CLI and the
    extension differing (the CLI is below the record but above the minimum).
    """
    _fake_cli(sandbox, "2.1.288")
    _, ext_sha = _fake_extension(sandbox, "2.1.290")
    section, run = _doctor(tmp_path, sandbox, monkeypatch, _registry_for_claude_code("2.1.290", ext_sha))
    assert (section.get("cli_version"), section.get("extension_version")) == ("2.1.288", "2.1.290"), (
        f"doctor did not read the fake CLI and extension: {section}\n{run.describe()}"
    )
    drift = [detail for detail in _issues(section, "drift") if "2.1.288" in detail and "2.1.290" in detail]
    assert drift and section.get("drift") is True and section.get("status") == "drift", (
        f"doctor does not report drift for CLI/extension version mismatch: {section}\n{run.describe()}"
    )


def test_extension_bundled_binary_different_sha256_is_drift(sandbox, tmp_path, monkeypatch):
    """The extension's bundled binary at the recorded version with a different sha256 is drift (DEC-214)."""
    _, cli_sha = _fake_cli(sandbox, "2.1.288")
    _, ext_sha = _fake_extension(sandbox, "2.1.288", binary_body="#!/bin/sh\n# different body\necho '2.1.288'\n")
    section, run = _doctor(tmp_path, sandbox, monkeypatch, _registry_for_claude_code("2.1.288", cli_sha))
    assert section.get("extension_version") == "2.1.288" and section.get("extension_binary_sha256") == ext_sha, (
        f"doctor did not read the fake extension's bundled binary: {section}\n{run.describe()}"
    )
    assert section.get("extension_binary_sha256") != section.get("pinned_sha256"), section
    assert _issues(section, "drift") and section.get("drift") is True and section.get("status") == "drift", (
        f"doctor does not report drift for extension binary sha256 mismatch: {section}\n{run.describe()}"
    )
    assert not _issues(section, "failure"), f"the bundled binary's hash is a failure, not drift: {section}"


# --------------------------------------------------------------------------
# Hard failure
# --------------------------------------------------------------------------

def test_cli_below_minimum_is_failure(sandbox, tmp_path, monkeypatch):
    """The CLI below the minimum version 2.1.285 is a hard failure, not just drift."""
    _, cli_sha = _fake_cli(sandbox, "2.1.280")
    section, run = _doctor(tmp_path, sandbox, monkeypatch, _registry_for_claude_code("2.1.288", cli_sha))
    assert section.get("cli_version") == "2.1.280", f"doctor did not read the fake CLI: {section}\n{run.describe()}"
    assert [detail for detail in _issues(section, "failure") if "2.1.280" in detail], (
        f"doctor raises no failure naming the CLI's 2.1.280: {section}\n{run.describe()}"
    )
    assert section.get("status") == "fail" and run.envelope()["ok"] is not True, \
        f"doctor passes with CLI below minimum version\n{run.describe()}"


def test_extension_below_minimum_is_failure(sandbox, tmp_path, monkeypatch):
    """The active extension below the minimum version 2.1.285 is a hard failure."""
    _, cli_sha = _fake_cli(sandbox, "2.1.288")
    _fake_extension(sandbox, "2.1.280")
    section, run = _doctor(tmp_path, sandbox, monkeypatch, _registry_for_claude_code("2.1.288", cli_sha))
    assert section.get("extension_version") == "2.1.280", (
        f"doctor did not read the fake extension: {section}\n{run.describe()}"
    )
    assert [detail for detail in _issues(section, "failure") if "2.1.280" in detail], (
        f"doctor raises no failure naming the extension's 2.1.280: {section}\n{run.describe()}"
    )
    assert section.get("status") == "fail" and run.envelope()["ok"] is not True, \
        f"doctor passes with extension below minimum version\n{run.describe()}"


def test_cli_at_recorded_version_different_sha256_is_failure(sandbox, tmp_path, monkeypatch):
    """The CLI at the recorded version with a different sha256 is a hard failure (DEC-214)."""
    _, cli_sha = _fake_cli(sandbox, "2.1.288")
    section, run = _doctor(tmp_path, sandbox, monkeypatch, _registry_for_claude_code("2.1.288", "0" * 64))
    assert (section.get("cli_version"), section.get("cli_sha256")) == ("2.1.288", cli_sha), (
        f"doctor did not read the fake CLI: {section}\n{run.describe()}"
    )
    assert _issues(section, "failure") and not _issues(section, "drift"), (
        f"the CLI at its recorded version with another sha256 raises no failure (or only drift): {section}\n"
        f"{run.describe()}"
    )
    assert section.get("status") == "fail" and run.envelope()["ok"] is not True, \
        f"doctor passes with CLI sha256 mismatch at recorded version\n{run.describe()}"
