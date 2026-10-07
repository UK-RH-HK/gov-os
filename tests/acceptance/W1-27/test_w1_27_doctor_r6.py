"""Round 6, KPI success 1 & failure 1: tools are found under the registered
prefixes and never pass unverified (DEC-440, DEC-448, DEC-452).

DEC-448 (owner, 2026-10-07):

  Each tool is checked at its registered location (the PATH prefix of
  DEC-202 and the registry's paths).

DEC-452 (orchestrator, 2026-10-07, delegated from DEC-448):

  Doctor looks for every tool first under its own entry's prefix, then
  under each PATH prefix that any entry of the registry carries (in the
  registry's order), and only then on PATH.

DEC-440 (owner, 2026-10-07):

  An error in a measurement is a failure, never a pass.  A tool is ``ok``
  only when the version read equals the pin, or, where no version can be
  read, when the file's hash equals the pinned hash.  A tool for which
  neither can be established is not ``ok``, the entry says why, and the
  tools section does not pass.

Predecessor analysis
--------------------
Round 5's ``test_w1_27_doctor_r5.py`` tests that doctor finds a tool at
its own entry's registered prefix.  There is no case for a tool found
under another entry's prefix (the Node problem: Node's entry has no
prefix but it is installed under the prefix that openspec and ccusage
carry).

Round 5 also has no case for the unverified-pass bug (the socat problem:
``found_version: "present"``, ``sha256_match: false``, ``ok: true``).
The code sets ``ok`` false only when a version was read and differs; when
no version could be read and the hash does not match, the tool still
passes.
"""

from __future__ import annotations

import hashlib
import json
import os
import stat
from pathlib import Path

import pytest

import w1_27_support as support


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def _fake_tool(directory, name, version):
    """Write a fake tool shell script that prints ``version``."""
    path = Path(directory) / name
    body = f"#!/bin/sh\necho '{version}'\n"
    path.write_text(body, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IEXEC)
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    return path, sha


def _fake_tool_no_version(directory, name):
    """Write a fake tool that exits with error on any invocation."""
    path = Path(directory) / name
    body = "#!/bin/sh\nexit 1\n"
    path.write_text(body, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IEXEC)
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    return path, sha


def _fake_tool_crashes(directory, name):
    """Write a fake tool that terminates on signal on any invocation."""
    path = Path(directory) / name
    body = "#!/bin/sh\nkill -TERM $$\n"
    path.write_text(body, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IEXEC)
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    return path, sha


def _registry_with_location(name, version, sha256, location_prefix, **extra):
    """A tool-registry entry with a PATH prefix in its install command."""
    install = f'PATH={location_prefix}:$PATH {location_prefix}/{name} --version'
    lines = [
        f"  - name: {name}",
        f'    version: "{version}"',
        f'    sha256: "{sha256}"',
        f'    install: "{install}"',
        f'    uninstall: "rm -f {location_prefix}/{name}"',
        f'    date: "2026-01-01"',
        f'    approved_by: "test"',
    ]
    for key, value in extra.items():
        lines.append(f'    {key}: "{value}"')
    return "\n".join(lines)


def _registry_without_location(name, version, sha256, **extra):
    """A tool-registry entry with no location info."""
    return support.tool_entry_yaml(
        name, version, sha256,
        install="echo install", uninstall="echo uninstall",
        date="2026-01-01", approved_by="test", **extra,
    )


def _doctor_sections(envelope):
    """Extract doctor's full result dict."""
    if envelope.get("ok"):
        return envelope.get("result", {})
    return envelope.get("error", {}).get("details", {})


def _find_tool_entry(sections, tool_name):
    """Find a tool entry by name in the parsed doctor sections."""
    tools_section = sections.get("tools", {})
    entries = tools_section.get("tools", [])
    for entry in entries:
        if isinstance(entry, dict) and entry.get("name") == tool_name:
            return entry
    return None


# =========================================================================== #
# Part 1: Tools found under registered prefixes (DEC-448, DEC-452)
# =========================================================================== #

# --------------------------------------------------------------------------- #
# Case 1: Tool with no prefix, found under another entry's prefix
# --------------------------------------------------------------------------- #

def test_tool_found_under_another_entrys_prefix(gov, project, tmp_path):
    """A tool whose own entry has no prefix, present at the pinned version
    under a prefix that another entry carries, and present at another
    version on PATH: found under the prefix, ``ok`` true, ``location``
    says where.

    DEC-448, DEC-452: doctor looks for every tool under each PATH prefix
    that any entry of the registry carries, not only the tool's own.

    RED: the current code only looks under the tool's own entry's prefix;
    for an entry with no prefix it falls back to PATH immediately, finding
    the system python3 at the wrong version.
    """
    prefix_dir = tmp_path / "other-prefix" / "bin"
    prefix_dir.mkdir(parents=True)

    _, sha_a = _fake_tool(prefix_dir, "tool-a", "1.0.0")

    fake_py, sha_py = _fake_tool(prefix_dir, "python3", "42.42.42")

    registry = "\n".join([
        _registry_with_location("tool-a", "1.0.0", sha_a, str(prefix_dir)),
        _registry_without_location("python3", "42.42.42", sha_py),
    ])
    support.write_tool_registry(project, registry)

    run = gov("doctor", "--json")
    envelope = run.envelope()
    sections = _doctor_sections(envelope)
    entry = _find_tool_entry(sections, "python3")

    assert entry is not None, (
        f"doctor has no entry for python3\n"
        f"tools section: {sections.get('tools', {})}\n{run.describe()}"
    )
    assert entry.get("ok") is True, (
        f"python3 is at the pinned version 42.42.42 under tool-a's prefix "
        f"{prefix_dir} but doctor does not pass for it — DEC-452 says "
        f"doctor checks every registered prefix, not only the tool's own\n"
        f"entry: {entry}\n{run.describe()}"
    )

    found_ver = str(entry.get("found_version", "")).lstrip("v")
    assert found_ver == "42.42.42", (
        f"found version should be '42.42.42' (from the fake python3 under "
        f"tool-a's prefix) but got '{entry.get('found_version')}'\n"
        f"entry: {entry}\n{run.describe()}"
    )

    assert str(prefix_dir) in str(entry.get("location", "")), (
        f"location should point to {prefix_dir}\n"
        f"entry: {entry}\n{run.describe()}"
    )


# --------------------------------------------------------------------------- #
# Case 2: Tool absent from all prefixes, found on PATH (wrong version fails)
# --------------------------------------------------------------------------- #

def test_tool_absent_from_all_prefixes_found_on_path(gov, project, tmp_path):
    """A tool absent under every registered prefix is found on PATH as
    before.  With a wrong version on PATH it fails.

    DEC-448, DEC-452: after checking all registered prefixes, doctor falls
    back to PATH.
    """
    prefix_dir = tmp_path / "other-prefix" / "bin"
    prefix_dir.mkdir(parents=True)

    _, sha_a = _fake_tool(prefix_dir, "tool-a", "1.0.0")

    registry = "\n".join([
        _registry_with_location("tool-a", "1.0.0", sha_a, str(prefix_dir)),
        _registry_without_location("python3", "999.999.999", "0" * 64),
    ])
    support.write_tool_registry(project, registry)

    run = gov("doctor", "--json")
    envelope = run.envelope()
    sections = _doctor_sections(envelope)
    entry = _find_tool_entry(sections, "python3")

    assert entry is not None, (
        f"doctor has no entry for python3\n"
        f"tools section: {sections.get('tools', {})}\n{run.describe()}"
    )
    assert entry.get("found_version") is not None, (
        f"python3 should be found on PATH but found_version is None — "
        f"the PATH fallback must still work when the tool is not in any "
        f"registered prefix\n"
        f"entry: {entry}\n{run.describe()}"
    )
    assert entry.get("ok") is not True, (
        f"python3 is at the wrong version on PATH but doctor passes — "
        f"a wrong version on PATH must fail\n"
        f"entry: {entry}\n{run.describe()}"
    )


# --------------------------------------------------------------------------- #
# Case 3: Entry's own prefix wins over another entry's prefix
# --------------------------------------------------------------------------- #

def test_own_prefix_wins_over_other_entrys_prefix(gov, project, tmp_path):
    """An entry's own prefix wins over another entry's prefix.

    DEC-452: "first under its own entry's prefix, then under each PATH
    prefix that any entry of the registry carries."  Own first.
    """
    prefix_a = tmp_path / "prefix-a" / "bin"
    prefix_a.mkdir(parents=True)
    prefix_own = tmp_path / "prefix-own" / "bin"
    prefix_own.mkdir(parents=True)

    _, sha_a = _fake_tool(prefix_a, "tool-a", "1.0.0")

    _fake_tool(prefix_a, "tool-c", "9.9.9")

    _, sha_c = _fake_tool(prefix_own, "tool-c", "3.0.0")

    registry = "\n".join([
        _registry_with_location("tool-a", "1.0.0", sha_a, str(prefix_a)),
        _registry_with_location("tool-c", "3.0.0", sha_c, str(prefix_own)),
    ])
    support.write_tool_registry(project, registry)

    run = gov("doctor", "--json")
    envelope = run.envelope()
    sections = _doctor_sections(envelope)
    entry = _find_tool_entry(sections, "tool-c")

    assert entry is not None, (
        f"doctor has no entry for tool-c\n"
        f"tools section: {sections.get('tools', {})}\n{run.describe()}"
    )
    assert entry.get("ok") is True, (
        f"tool-c is at the pinned version 3.0.0 under its own prefix "
        f"{prefix_own} but doctor does not pass for it\n"
        f"entry: {entry}\n{run.describe()}"
    )

    found_ver = str(entry.get("found_version", "")).lstrip("v")
    assert found_ver == "3.0.0", (
        f"found version should be '3.0.0' (from tool-c's own prefix) but "
        f"got '{entry.get('found_version')}' — own prefix must win over "
        f"another entry's prefix\n"
        f"entry: {entry}\n{run.describe()}"
    )

    assert str(prefix_own) in str(entry.get("location", "")), (
        f"location should point to {prefix_own} (tool-c's own prefix), "
        f"not {prefix_a} (tool-a's prefix)\n"
        f"entry: {entry}\n{run.describe()}"
    )


# =========================================================================== #
# Part 2: Tools must not pass unverified (DEC-440)
# =========================================================================== #

# --------------------------------------------------------------------------- #
# Case 4: No version read, hash mismatch → not ok, entry says why,
#          section fails
# --------------------------------------------------------------------------- #

def test_tool_no_version_no_hash_not_ok(gov, project, tmp_path):
    """A tool for which neither version nor hash can be established is not
    ``ok``.  The entry says why and the tools section does not pass.

    KPI failure: "doctor passes with a tool at the wrong version" [CAP-25.a].
    DEC-440: an error in a measurement is a failure, never a pass.

    RED: the current code sets ``ok=True`` when the version command fails
    (``found_version`` becomes ``"present"``) and never consults the hash
    for the ``ok`` decision.  There is no ``reason`` field.
    """
    tool_dir = tmp_path / "tools" / "bin"
    tool_dir.mkdir(parents=True)

    _, actual_sha = _fake_tool_no_version(tool_dir, "unverified-tool")
    wrong_sha = "0" * 64

    registry = _registry_with_location(
        "unverified-tool", "1.0.0", wrong_sha, str(tool_dir),
    )
    support.write_tool_registry(project, registry)

    run = gov("doctor", "--json")
    envelope = run.envelope()
    sections = _doctor_sections(envelope)
    entry = _find_tool_entry(sections, "unverified-tool")

    assert entry is not None, (
        f"doctor has no entry for unverified-tool\n"
        f"tools section: {sections.get('tools', {})}\n{run.describe()}"
    )
    assert entry.get("ok") is not True, (
        f"doctor passes for a tool with no readable version and a hash "
        f"mismatch — an unverifiable tool must not be ok (DEC-440)\n"
        f"entry: {entry}\n{run.describe()}"
    )

    reason = entry.get("reason", "")
    assert reason, (
        f"an unverified tool's entry must say why it is not ok "
        f"(e.g. 'unverified: no version read and the hash does not "
        f"match'), but no reason was given\n"
        f"entry: {entry}\n{run.describe()}"
    )

    tools_section = sections.get("tools", {})
    assert tools_section.get("status") != "pass", (
        f"the tools section passes despite an unverified tool\n"
        f"tools: {tools_section}\n{run.describe()}"
    )


# --------------------------------------------------------------------------- #
# Case 5: No version read, hash matches → ok (verified by hash)
# --------------------------------------------------------------------------- #

def test_tool_no_version_hash_match_ok(gov, project, tmp_path):
    """A tool whose version cannot be read but whose file hash equals the
    pinned hash is ``ok`` — the hash verifies it.

    DEC-440: "a tool is ok … where no version can be read, when the
    file's hash equals the pinned hash."
    """
    tool_dir = tmp_path / "tools" / "bin"
    tool_dir.mkdir(parents=True)

    _, actual_sha = _fake_tool_no_version(tool_dir, "hash-verified-tool")

    registry = _registry_with_location(
        "hash-verified-tool", "1.0.0", actual_sha, str(tool_dir),
    )
    support.write_tool_registry(project, registry)

    run = gov("doctor", "--json")
    envelope = run.envelope()
    sections = _doctor_sections(envelope)
    entry = _find_tool_entry(sections, "hash-verified-tool")

    assert entry is not None, (
        f"doctor has no entry for hash-verified-tool\n"
        f"tools section: {sections.get('tools', {})}\n{run.describe()}"
    )
    assert entry.get("ok") is True, (
        f"a tool with no readable version but a matching hash must be ok "
        f"(verified by hash, DEC-440)\n"
        f"entry: {entry}\n{run.describe()}"
    )
    assert entry.get("sha256_match") is True, (
        f"sha256_match should be True for a tool whose hash matches the "
        f"pinned hash\n"
        f"entry: {entry}\n{run.describe()}"
    )


# --------------------------------------------------------------------------- #
# Case 6: Version command raises → not ok when hash does not match
# --------------------------------------------------------------------------- #

def test_tool_version_raises_no_hash_not_ok(gov, project, tmp_path):
    """A tool whose version command raises or terminates on signal is not
    ``ok`` when the hash does not match the pin either.

    DEC-440: "a version command that raises or times out gives the same
    answer, never a pass."

    RED: the current code catches the failure, returns ``"present"``, and
    sets ``ok=True`` regardless of the hash.
    """
    tool_dir = tmp_path / "tools" / "bin"
    tool_dir.mkdir(parents=True)

    _, actual_sha = _fake_tool_crashes(tool_dir, "crashing-tool")
    wrong_sha = "0" * 64

    registry = _registry_with_location(
        "crashing-tool", "1.0.0", wrong_sha, str(tool_dir),
    )
    support.write_tool_registry(project, registry)

    run = gov("doctor", "--json")
    envelope = run.envelope()
    sections = _doctor_sections(envelope)
    entry = _find_tool_entry(sections, "crashing-tool")

    assert entry is not None, (
        f"doctor has no entry for crashing-tool\n"
        f"tools section: {sections.get('tools', {})}\n{run.describe()}"
    )
    assert entry.get("ok") is not True, (
        f"doctor passes for a tool whose version command raises and whose "
        f"hash does not match — an unverifiable tool must not pass "
        f"(DEC-440)\n"
        f"entry: {entry}\n{run.describe()}"
    )


# --------------------------------------------------------------------------- #
# Case 7: Version differs from pin, hash matches → fails
# --------------------------------------------------------------------------- #

def test_tool_version_mismatch_fails_despite_hash_match(gov, project, tmp_path):
    """A version that is read and differs from the pin fails even when the
    file's hash equals the pinned hash.

    DEC-440: version mismatch is authoritative.
    """
    tool_dir = tmp_path / "tools" / "bin"
    tool_dir.mkdir(parents=True)

    path, actual_sha = _fake_tool(tool_dir, "version-mismatch-tool", "9.9.9")

    registry = _registry_with_location(
        "version-mismatch-tool", "1.0.0", actual_sha, str(tool_dir),
    )
    support.write_tool_registry(project, registry)

    run = gov("doctor", "--json")
    envelope = run.envelope()
    sections = _doctor_sections(envelope)
    entry = _find_tool_entry(sections, "version-mismatch-tool")

    assert entry is not None, (
        f"doctor has no entry for version-mismatch-tool\n"
        f"tools section: {sections.get('tools', {})}\n{run.describe()}"
    )
    assert entry.get("ok") is not True, (
        f"doctor passes for a tool at version 9.9.9 when 1.0.0 is pinned "
        f"— version mismatch must fail even when the hash matches\n"
        f"entry: {entry}\n{run.describe()}"
    )
    assert entry.get("sha256_match") is True, (
        f"the hash does match (same binary, different version): this "
        f"confirms the version mismatch was the cause of the failure, "
        f"not a missing or different binary\n"
        f"entry: {entry}\n{run.describe()}"
    )
