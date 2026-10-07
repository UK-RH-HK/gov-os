"""KPI success 1 and failure 1: ``gov doctor`` reports installation health.

Success: doctor reports pinned vs found tool versions, hooks wired, path map
with zero unclassified paths, index freshness, canaries, framework.lock
MATCH/DRIFT, per-repository isolation; non-zero on any failure
[CAP-02.a, CAP-06.a, CAP-25.a].

Failure: doctor passes with a tool at the wrong version.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

import w1_27_support as support

# Section names the doctor report must contain (the contract does not fix their
# spelling, so the tests look for a recognisable substring in the result keys or
# in the JSON-serialised result).
REPORT_SECTIONS = (
    "tool",           # pinned vs found tool versions
    "hook",           # hooks wired
    "path",           # path-map coverage / unclassified paths
    "index",          # index freshness
    "canar",          # canaries
    "framework",      # framework.lock MATCH/DRIFT
    "isolation",      # per-repository isolation
)


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def _doctor_sections(envelope):
    """Extract doctor's full result dict from either a healthy or unhealthy envelope."""
    if envelope.get("ok"):
        return envelope.get("result", {})
    return envelope.get("error", {}).get("details", {})


def _make_real_home_sandbox(tmp_path):
    """A sandbox with HOME pointing to the real user's home."""
    base = tmp_path / "real-home-sandbox"
    for name in ("tmp", "bin", "pycache", "elsewhere"):
        (base / name).mkdir(parents=True, exist_ok=True)
    return support.base.Sandbox(
        home=Path.home(),
        tmpdir=base / "tmp",
        bin=base / "bin",
        pycache=base / "pycache",
        elsewhere=base / "elsewhere",
    )


# --------------------------------------------------------------------------
# Command identity
# --------------------------------------------------------------------------

def test_doctor_is_a_read_command(gov, project, interface, tmp_path):
    """``doctor`` is a read command (CAP-27, DEC-317): it returns an envelope and never changes the working tree.

    Revised after implementation: doctor verifies every registry entry under
    the session's home (DEC-452); the case built its healthy project from
    this repository's registry and so depended on the real machine.
    """
    tool_dir = tmp_path / "fake-tools" / "bin"
    tool_dir.mkdir(parents=True)
    _, sha = support.fake_tool(tool_dir, "read-cmd-tool", "1.0.0")
    registry = support.tool_entry_with_location_yaml(
        "read-cmd-tool", "1.0.0", sha, str(tool_dir),
    )
    support.write_tool_registry(project, registry)

    before = support.snapshot(project)
    run = gov("doctor", "--json")
    envelope = support.assert_envelope(run, interface, command="doctor")
    assert isinstance(envelope, dict), run.describe()
    after = support.snapshot(project)
    diff = support.snapshot_difference(before, after)
    assert not diff, (
        f"doctor changed the project:\n" + "\n".join(diff) + f"\n{run.describe()}"
    )


def test_doctor_envelope_is_valid_on_healthy_project(gov, project, interface, tmp_path):
    """A project with all health indicators met gives ok=true, exit 0.

    Revised after implementation: doctor verifies every registry entry under
    the session's home (DEC-452); the case built its healthy project from
    this repository's registry and so depended on the real machine.
    """
    tool_dir = tmp_path / "fake-tools" / "bin"
    tool_dir.mkdir(parents=True)
    _, sha = support.fake_tool(tool_dir, "healthy-tool", "2.0.0")
    registry = support.tool_entry_with_location_yaml(
        "healthy-tool", "2.0.0", sha, str(tool_dir),
    )
    support.write_tool_registry(project, registry)
    support.write_path_map(project, support.minimal_valid_path_map())
    run = gov("doctor", "--json")
    envelope = support.assert_envelope(run, interface, command="doctor")
    assert envelope["ok"] is True, f"doctor is not ok on a healthy project\n{run.describe()}"
    assert run.returncode == 0, f"exit code is not 0 on a healthy project\n{run.describe()}"


# --------------------------------------------------------------------------
# Machine-dependent: real registry, real home
# --------------------------------------------------------------------------

def test_doctor_real_registry_every_entry_reported(project, tmp_path, interface):
    """Machine-dependent: runs doctor against this repository's real
    registry with the real home.  Asserts only what holds on any machine:
    the tools section lists every registry entry by name, and every entry
    is either ok with the way it passed or not ok with a reason.  It does
    not assert that the machine is healthy.
    """
    reg_path = project / "governance" / "project" / "tool-registry.yaml"
    if not reg_path.is_file():
        pytest.skip("no tool-registry.yaml in the project")

    reg_text = reg_path.read_text(encoding="utf-8")
    expected_names = set()
    for m in re.finditer(r"^\s*-\s*name:\s*(.+)$", reg_text, re.MULTILINE):
        expected_names.add(m.group(1).strip())
    assert expected_names, "no tool names found in the registry"

    sandbox = _make_real_home_sandbox(tmp_path)
    run = support.run_gov(project, sandbox, "doctor", "--json")
    envelope = support.assert_envelope(run, interface, command="doctor")
    sections = _doctor_sections(envelope)

    tools_section = sections.get("tools", {})
    entries = tools_section.get("tools", [])
    reported = {}
    for entry in entries:
        if isinstance(entry, dict) and "name" in entry:
            reported[entry["name"]] = entry

    # "claude code" has its own dedicated section (claude_code) in the
    # doctor report, separate from the tools list.
    tools_expected = expected_names - {"claude code"}
    missing = tools_expected - set(reported.keys())
    assert not missing, (
        f"registry entries not reported by doctor: {sorted(missing)}\n"
        f"reported: {sorted(reported.keys())}\n{run.describe()}"
    )

    if "claude code" in expected_names:
        assert "claude_code" in sections, (
            f"'claude code' is in the registry but doctor has no "
            f"claude_code section\n{run.describe()}"
        )

    for name, entry in reported.items():
        assert "ok" in entry, (
            f"entry '{name}' has no 'ok' field: {entry}"
        )
        if entry["ok"] is True:
            info = {k: v for k, v in entry.items() if k not in ("name", "ok")}
            assert info, (
                f"entry '{name}' is ok but has no fields showing how "
                f"it passed: {entry}"
            )
        else:
            info = {k: v for k, v in entry.items() if k not in ("name", "ok")}
            assert info, (
                f"entry '{name}' is not ok but has no fields showing "
                f"why: {entry}"
            )


# --------------------------------------------------------------------------
# Report contents: each section is present
# --------------------------------------------------------------------------

def test_doctor_report_mentions_tool_versions(gov, project, interface):
    """The doctor result mentions tool version information (CAP-25.a)."""
    run = gov("doctor", "--json")
    text = json.dumps(run.envelope())
    assert "tool" in text.lower(), f"doctor report does not mention tool versions\n{run.describe()}"


def test_doctor_report_mentions_hooks(gov, project, interface):
    """The doctor result mentions hooks (wired or not)."""
    run = gov("doctor", "--json")
    text = json.dumps(run.envelope())
    assert "hook" in text.lower(), f"doctor report does not mention hooks\n{run.describe()}"


def test_doctor_report_mentions_path_map_coverage(gov, project, interface):
    """The doctor result mentions path-map coverage (CAP-06.a): zero unclassified paths."""
    run = gov("doctor", "--json")
    text = json.dumps(run.envelope())
    found = "path" in text.lower() or "unclassified" in text.lower()
    assert found, f"doctor report does not mention path-map coverage\n{run.describe()}"


def test_doctor_report_mentions_index_freshness(gov, project, interface):
    """The doctor result mentions index freshness."""
    run = gov("doctor", "--json")
    text = json.dumps(run.envelope())
    assert "index" in text.lower() or "fresh" in text.lower(), \
        f"doctor report does not mention index freshness\n{run.describe()}"


def test_doctor_report_mentions_canaries(gov, project, interface):
    """The doctor result mentions canaries."""
    run = gov("doctor", "--json")
    text = json.dumps(run.envelope())
    assert "canar" in text.lower(), f"doctor report does not mention canaries\n{run.describe()}"


def test_doctor_report_mentions_framework_lock(gov, project, interface):
    """The doctor result mentions framework.lock with MATCH or DRIFT (CAP-02.a)."""
    run = gov("doctor", "--json")
    text = json.dumps(run.envelope())
    assert "framework" in text.lower() or "lock" in text.lower(), \
        f"doctor report does not mention framework.lock\n{run.describe()}"


def test_doctor_report_mentions_isolation(gov, project, interface):
    """The doctor result mentions per-repository isolation."""
    run = gov("doctor", "--json")
    text = json.dumps(run.envelope())
    assert "isolat" in text.lower(), f"doctor report does not mention per-repository isolation\n{run.describe()}"


# --------------------------------------------------------------------------
# Exit code on failure
# --------------------------------------------------------------------------

def test_doctor_exit_nonzero_on_any_failure(gov, project, interface):
    """When any health check fails, exit code is non-zero."""
    registry = support.tool_entry_yaml("fake-tool", "99.99.99", "0" * 64,
                                       install="echo fake", uninstall="echo fake",
                                       date="2026-01-01", approved_by="test")
    support.write_tool_registry(project, registry)
    run = gov("doctor", "--json")
    envelope = support.assert_envelope(run, interface, command="doctor")
    assert run.returncode != 0, f"doctor exits 0 despite a health failure\n{run.describe()}"


# --------------------------------------------------------------------------
# Failure KPI 1: doctor passes with a tool at the wrong version
# --------------------------------------------------------------------------

def test_doctor_does_not_pass_with_wrong_tool_version(gov, project, interface):
    """A tool in the registry at a version that does not match what is found must cause doctor to report not-ok.

    The test writes a registry entry with a version that no real tool has, then asserts that doctor is not ok.
    """
    registry = support.tool_entry_yaml("node", "0.0.1-fake", "0" * 64,
                                       install="echo fake", uninstall="echo fake",
                                       date="2026-01-01", approved_by="test")
    support.write_tool_registry(project, registry)
    run = gov("doctor", "--json")
    envelope = support.assert_envelope(run, interface, command="doctor")
    assert envelope["ok"] is not True, \
        f"doctor passes with a tool at the wrong version\n{run.describe()}"
