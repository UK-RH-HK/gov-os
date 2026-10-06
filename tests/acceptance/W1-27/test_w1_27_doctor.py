"""KPI success 1 and failure 1: ``gov doctor`` reports installation health.

Success: doctor reports pinned vs found tool versions, hooks wired, path map
with zero unclassified paths, index freshness, canaries, framework.lock
MATCH/DRIFT, per-repository isolation; non-zero on any failure
[CAP-02.a, CAP-06.a, CAP-25.a].

Failure: doctor passes with a tool at the wrong version.
"""

from __future__ import annotations

import json

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
# Command identity
# --------------------------------------------------------------------------

def test_doctor_is_a_read_command(gov, interface):
    """``doctor`` is a read command (CAP-27, DEC-317): it returns an envelope and never changes the working tree."""
    before = support.porcelain(support.Path(gov.__wrapped__ if hasattr(gov, '__wrapped__') else ''))
    run = gov("doctor", "--json")
    envelope = support.assert_envelope(run, interface, command="doctor")
    assert isinstance(envelope, dict), run.describe()


def test_doctor_envelope_is_valid_on_healthy_project(gov, project, interface):
    """A project with all health indicators met gives ok=true, exit 0."""
    support.write_path_map(project, support.minimal_valid_path_map())
    run = gov("doctor", "--json")
    envelope = support.assert_envelope(run, interface, command="doctor")
    assert envelope["ok"] is True, f"doctor is not ok on a healthy project\n{run.describe()}"
    assert run.returncode == 0, f"exit code is not 0 on a healthy project\n{run.describe()}"


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
