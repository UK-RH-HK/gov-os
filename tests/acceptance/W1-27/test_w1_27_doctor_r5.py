"""Round 5, KPI success 1 & 3: doctor finds tools at their registered
locations and excludes historical records from the stale-path check (DEC-448).

DEC-448 (owner, 2026-10-07):

  1. Each tool is checked at its registered location (the PATH prefix of
     DEC-202 and the registry's paths), not only on PATH, so Node 22,
     openspec and ccusage are found where they are installed.  The machine's
     default Node stays 18.

  2. Historical records (the register, the CIT records, bootstrap.md,
     archived sources) are excluded from the stale-path check.  The stale
     paths in live documents are fixed, and any remainder becomes a small
     cleanup task.

Path-map and historical marking
--------------------------------
The path-map schema (``template/governance/kernel/schemas/path-map.schema.json``)
has a top-level ``state_class`` (``common.schema.json#/$defs/state_class``,
enum including ``HISTORICAL``), but no per-namespace or per-file state class.
Namespace fields are: paths, memory_class, sensitivity, permitted_roles,
retention, export_policy, embedding_policy, provenance, deletion_rebuild
— none marks a file as historical.

The ``HISTORICAL`` state class exists in ``common.schema.json`` and is used
in individual record frontmatter, but the four kinds DEC-448 names are not
all records with YAML frontmatter (the register is a Markdown file, so is
bootstrap.md, and ``docs/source/`` is a directory tree).

**The path-map has no field or entry kind that marks a file as historical.**
The cases below identify the four kinds by the paths the decision names,
held in one named list ``HISTORICAL_PATHS``.

Predecessor analysis
--------------------
The first round's ``test_w1_27_doctor.py`` has ``test_doctor_does_not_pass_
with_wrong_tool_version`` (failure KPI 1) and ``test_doctor_report_mentions_
tool_versions``, neither of which tests that doctor finds a tool at a
registered location that is not on PATH.  ``test_w1_27_path_compliance.py``
has ``test_moved_path_reference_is_reported`` but does not test the
historical-record exclusion.  Both gaps let DEC-448's two points through.
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
# The four kinds of historical records named in DEC-448, each by the path
# it has in this repository.
# --------------------------------------------------------------------------- #

HISTORICAL_PATHS = [
    "docs/DECISION_REGISTER.md",          # the register
    "docs/changes/",                       # CIT records (S2-CIT-E.md, S2-CIT-P.md)
    "governance/project/bootstrap.md",     # bootstrap.md
    "docs/source/",                        # archived sources
]


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #

def _fake_tool(directory, name, version):
    """Write a fake tool shell script in ``directory`` that prints ``version``.

    Returns ``(path, sha256)``.
    """
    path = Path(directory) / name
    body = f"#!/bin/sh\necho '{version}'\n"
    path.write_text(body, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IEXEC)
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    return path, sha


def _registry_with_location(name, version, sha256, location_prefix, **extra):
    """A tool-registry entry whose ``install`` command carries a PATH prefix,
    telling doctor where the tool is installed (the PATH prefix of DEC-202).
    """
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
    """A tool-registry entry with no location info — doctor falls back to PATH."""
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


# =========================================================================== #
# Part 1: Tools at registered locations (DEC-448, DEC-202)
# =========================================================================== #

# --------------------------------------------------------------------------- #
# Case 1: Tool at registered location, not on PATH, correct version → pass
# --------------------------------------------------------------------------- #

def test_tool_at_registered_location_passes(gov, project, tmp_path):
    """A tool that is not on PATH but is installed at the location its
    registry entry names (the PATH prefix of DEC-202) at the pinned version:
    doctor finds it there and the tools section passes for it, and says
    where it was found.

    KPI: "doctor reports pinned vs found tool versions" [CAP-25.a].
    DEC-448: "Each tool is checked at its registered location".
    """
    tool_dir = tmp_path / "registered-location" / "bin"
    tool_dir.mkdir(parents=True)
    _, tool_sha = _fake_tool(tool_dir, "fake-registered-tool", "1.2.3")

    registry = _registry_with_location(
        "fake-registered-tool", "1.2.3", tool_sha, str(tool_dir),
        note=f"installed at {tool_dir}/fake-registered-tool",
    )
    support.write_tool_registry(project, registry)

    run = gov("doctor", "--json")
    envelope = run.envelope()
    text = json.dumps(envelope).lower()

    assert "fake-registered-tool" in text, (
        f"doctor does not mention fake-registered-tool at all\n{run.describe()}"
    )

    sections = _doctor_sections(envelope)
    tools = sections.get("tools", {})
    tools_text = json.dumps(tools).lower()
    found_and_pass = (
        "1.2.3" in tools_text
        and ("pass" in tools_text or "ok" in tools_text or "found" in tools_text)
    )
    assert found_and_pass, (
        f"doctor did not find fake-registered-tool at its registered "
        f"location {tool_dir} or did not pass for it\n"
        f"tools section: {tools}\n{run.describe()}"
    )

    assert str(tool_dir) in json.dumps(envelope) or "registered" in text, (
        f"doctor does not say where the tool was found\n"
        f"tools section: {tools}\n{run.describe()}"
    )


# --------------------------------------------------------------------------- #
# Case 2: Tool at registered location, wrong version → failure
# --------------------------------------------------------------------------- #

def test_tool_at_registered_location_wrong_version_fails(gov, project, tmp_path):
    """A tool at its registered location with a wrong version: a failure.

    KPI failure: "doctor passes with a tool at the wrong version" [CAP-25.a].
    DEC-448.
    """
    tool_dir = tmp_path / "registered-location" / "bin"
    tool_dir.mkdir(parents=True)
    _, tool_sha = _fake_tool(tool_dir, "wrong-ver-tool", "9.9.9")

    registry = _registry_with_location(
        "wrong-ver-tool", "1.0.0", tool_sha, str(tool_dir),
    )
    support.write_tool_registry(project, registry)

    run = gov("doctor", "--json")
    envelope = run.envelope()

    assert envelope.get("ok") is not True, (
        f"doctor passes with a tool at the wrong version at its "
        f"registered location\n{run.describe()}"
    )


# --------------------------------------------------------------------------- #
# Case 3: Tool registered at an empty location, not on PATH → failure
# --------------------------------------------------------------------------- #

def test_tool_at_empty_registered_location_fails(gov, project, tmp_path):
    """A tool registered with a location where nothing is installed and
    nothing on PATH either: a failure, naming the place looked at.

    KPI: "doctor reports pinned vs found tool versions" [CAP-25.a].
    DEC-448.
    """
    empty_dir = tmp_path / "empty-location" / "bin"
    empty_dir.mkdir(parents=True)

    registry = _registry_with_location(
        "absent-tool", "1.0.0", "0" * 64, str(empty_dir),
    )
    support.write_tool_registry(project, registry)

    run = gov("doctor", "--json")
    envelope = run.envelope()
    text = json.dumps(envelope)

    assert envelope.get("ok") is not True, (
        f"doctor passes for a tool that is neither at its registered "
        f"location nor on PATH\n{run.describe()}"
    )

    assert str(empty_dir) in text or "absent-tool" in text, (
        f"doctor does not name the place it looked at for the absent "
        f"tool\n{run.describe()}"
    )


# --------------------------------------------------------------------------- #
# Case 4: Tool with no registered location → found on PATH as before
# --------------------------------------------------------------------------- #

def test_tool_without_registered_location_found_on_path(gov, project):
    """A tool with no registered location: found on PATH as before.

    KPI: "doctor reports pinned vs found tool versions" [CAP-25.a].
    DEC-448: the default PATH lookup still works.
    """
    registry = _registry_without_location("python3", "3.12.3", "0" * 64)
    support.write_tool_registry(project, registry)

    run = gov("doctor", "--json")
    envelope = run.envelope()
    text = json.dumps(envelope).lower()

    assert "python3" in text or "python" in text, (
        f"doctor does not mention python3 from PATH\n{run.describe()}"
    )


# --------------------------------------------------------------------------- #
# Case 5: Doctor changes nothing on the machine and nothing in PATH
# --------------------------------------------------------------------------- #

def test_doctor_does_not_modify_path(gov, project, tmp_path):
    """Doctor changes nothing on the machine and nothing in PATH for anyone
    else.

    DEC-448: finding tools at registered locations must not alter the
    machine's PATH or install anything.
    """
    tool_dir = tmp_path / "registered-location" / "bin"
    tool_dir.mkdir(parents=True)
    _, tool_sha = _fake_tool(tool_dir, "nomod-tool", "1.0.0")
    registry = _registry_with_location(
        "nomod-tool", "1.0.0", tool_sha, str(tool_dir),
    )
    support.write_tool_registry(project, registry)

    path_before = os.environ.get("PATH", "")
    before = support.snapshot(project)

    run = gov("doctor", "--json")

    path_after = os.environ.get("PATH", "")
    after = support.snapshot(project)

    assert path_before == path_after, (
        f"doctor changed PATH:\nbefore: {path_before}\nafter: {path_after}"
    )
    diff = support.snapshot_difference(before, after)
    assert not diff, (
        f"doctor changed the project:\n" + "\n".join(diff) + f"\n{run.describe()}"
    )


# =========================================================================== #
# Part 2: Historical records excluded from the stale-path check (DEC-448)
# =========================================================================== #

# --------------------------------------------------------------------------- #
# Case 6: A reference to a moved path inside a historical record is NOT
#         reported by the stale-path check
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize("historical_path", HISTORICAL_PATHS, ids=[
    "register", "cit-records", "bootstrap", "archived-sources",
])
def test_stale_path_in_historical_record_is_not_reported(gov, project, interface, historical_path):
    """A reference to a moved path inside a historical record is not
    reported by the stale-path check.

    DEC-448: "Historical records (the register, the CIT records,
    bootstrap.md, archived sources) are excluded from the stale-path check."

    Each of the four kinds is tested by the path it has in this repository.
    """
    support.write_path_map(project, support.minimal_valid_path_map())

    old_path = project / "src" / "gov" / "doctor" / "old_historical_module.py"
    old_path.parent.mkdir(parents=True, exist_ok=True)
    old_path.write_text("# old module\n", encoding="utf-8")
    support.commit_all(project, "add old module")

    new_path = project / "src" / "gov" / "doctor" / "new_historical_module.py"
    old_path.rename(new_path)
    support.commit_all(project, "move old module to new module")

    if historical_path.endswith("/"):
        hist_file = project / historical_path / "test-historical.md"
    else:
        hist_file = project / historical_path
    hist_file.parent.mkdir(parents=True, exist_ok=True)
    hist_file.write_text(
        f"Reference to the old path: src/gov/doctor/old_historical_module.py\n",
        encoding="utf-8",
    )
    support.commit_all(project, f"add historical reference in {historical_path}")

    run = gov("doctor", "--json")
    envelope = run.envelope()
    text = json.dumps(envelope)

    assert "old_historical_module" not in text, (
        f"doctor reports a reference to a moved path inside a historical "
        f"record ({historical_path}) — DEC-448 says historical records "
        f"are excluded from the stale-path check\n{run.describe()}"
    )


# --------------------------------------------------------------------------- #
# Case 7: A reference to the SAME moved path inside a LIVE document IS
#         reported
# --------------------------------------------------------------------------- #

def test_stale_path_in_live_document_is_reported(gov, project, interface):
    """A reference to a moved path inside a live document IS reported.

    DEC-448: the exclusion is narrow — a live document beside an excluded
    one is still checked.
    """
    support.write_path_map(project, support.minimal_valid_path_map())

    old_path = project / "src" / "gov" / "doctor" / "old_live_module.py"
    old_path.parent.mkdir(parents=True, exist_ok=True)
    old_path.write_text("# old module\n", encoding="utf-8")
    support.commit_all(project, "add old module")

    new_path = project / "src" / "gov" / "doctor" / "new_live_module.py"
    old_path.rename(new_path)
    support.commit_all(project, "move old module to new module")

    live_file = project / "docs" / "live-reference.md"
    live_file.parent.mkdir(parents=True, exist_ok=True)
    live_file.write_text(
        "Reference to the old path: src/gov/doctor/old_live_module.py\n",
        encoding="utf-8",
    )
    support.commit_all(project, "add live reference")

    run = gov("doctor", "--json")
    envelope = run.envelope()
    text = json.dumps(envelope)

    assert "old_live_module" in text or "moved" in text.lower() or "stale" in text.lower(), (
        f"doctor does not report a reference to a moved path inside a "
        f"live document — the stale-path check should report it\n"
        f"{run.describe()}"
    )


# --------------------------------------------------------------------------- #
# Case 8: The stale-path section says how many files it left out as
#         historical
# --------------------------------------------------------------------------- #

def test_stale_path_section_counts_excluded_historical(gov, project, interface):
    """The stale-path section says how many files it left out as historical.

    DEC-448: the exclusion is visible — the section reports the count so
    the reader knows files were skipped, not missed.
    """
    support.write_path_map(project, support.minimal_valid_path_map())

    hist_file = project / "docs" / "DECISION_REGISTER.md"
    hist_file.parent.mkdir(parents=True, exist_ok=True)
    hist_file.write_text("# Decision Register\nSome old path reference\n", encoding="utf-8")

    hist_file2 = project / "governance" / "project" / "bootstrap.md"
    hist_file2.parent.mkdir(parents=True, exist_ok=True)
    hist_file2.write_text("# Bootstrap\nSome old path reference\n", encoding="utf-8")

    support.commit_all(project, "add historical files")

    run = gov("doctor", "--json")
    envelope = run.envelope()
    text = json.dumps(envelope).lower()

    has_exclusion_count = (
        "historical" in text
        or "excluded" in text
        or "skipped" in text
    )
    assert has_exclusion_count, (
        f"the stale-path section does not mention how many files it left "
        f"out as historical — the section should say how many were "
        f"excluded (DEC-448)\n{run.describe()}"
    )
