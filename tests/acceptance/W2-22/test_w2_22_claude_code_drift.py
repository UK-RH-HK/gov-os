"""W2-22 fix, DEC-1227 D6 (a): ``gov doctor``'s ``claude_code`` section and a patch-only CLI/extension gap.

The VS Code extension updates itself, so a gap of the PATCH number alone (same major and same minor) between the
Claude Code CLI and the extension is the normal state of a machine that has the editor. It is reported as drift
(``drift: true`` and an issue of type ``drift`` naming both versions, in the JSON and in the plain output) and
``gov doctor`` still exits 0. A larger gap (the minor or the major differs), a version below the minimum
(2.1.285) and a CLI whose sha256 differs from the one recorded for its version still end ``gov doctor`` with exit
3, error code ``DOCTOR_UNHEALTHY``, naming ``claude_code``; a patch-only gap beside one of them masks nothing.

Every case builds a small committed repository of its own, a stand-in ``claude`` first on the ``PATH`` and a
stand-in extension under the case's ``HOME``; the machine's own CLI, extension and home are never read or touched.
Sources: ``docs/emergency-2/W2-81-PROVING-RUN-0.1.4-ANALYSIS.md`` rows P1 and A1.
"""

from __future__ import annotations

import pytest

import w2_22_support as support

DOCTOR_UNHEALTHY = "DOCTOR_UNHEALTHY"


def _unhealthy(run, section_name="claude_code"):
    """``gov doctor`` ended with exit 3, ``DOCTOR_UNHEALTHY``, and named the part; the part's section."""
    envelope = support.envelope(run)
    error = envelope.get("error") or {}
    assert run.returncode == 3 and envelope.get("ok") is False and error.get("code") == DOCTOR_UNHEALTHY, (
        f"expected exit 3 with {DOCTOR_UNHEALTHY}\n{run.describe()}")
    assert section_name in str(error.get("message")) or section_name in (error.get("details") or {}), (
        f"the error does not name {section_name}\n{run.describe()}")
    return support.section(run)


def _issue_texts(section, kind=None):
    return [str(issue.get("detail")) for issue in section.get("issues") or []
            if isinstance(issue, dict) and (kind is None or issue.get("type") == kind)]


# --------------------------------------------------------------------------------------------------------------
# A1: a patch-only gap is drift, named, and exit 0
# --------------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("cli,extension", [
    ("2.1.329", "2.1.328"),   # the CLI ahead by one
    ("2.1.328", "2.1.329"),   # the extension ahead by one
    ("2.1.329", "2.1.300"),   # a wide patch gap, still the same minor
])
def test_a_patch_only_gap_is_named_drift_and_doctor_exits_0(sandbox, tmp_path, monkeypatch, cli, extension):
    support.write_cli(sandbox, cli)
    support.write_extension(sandbox, extension)
    run = support.doctor(tmp_path, sandbox, monkeypatch, "--json")
    envelope = support.envelope(run)
    assert run.returncode == 0 and envelope.get("ok") is True, f"a patch-only gap must not fail doctor\n{run.describe()}"
    assert envelope["result"].get("healthy") is True, f"healthy must be true for a patch-only gap\n{run.describe()}"
    part = support.section(run)
    assert (part.get("cli_version"), part.get("extension_version")) == (cli, extension), (
        f"doctor did not read the stand-in CLI and extension: {part}")
    assert part.get("drift") is True and part.get("status") == "drift", f"the gap is still reported as drift: {part}"
    named = [text for text in _issue_texts(part, "drift") if cli in text and extension in text]
    assert named, f"no drift issue names both versions {cli} and {extension}: {part}"


def test_a_patch_only_gap_is_named_in_the_plain_output_too(sandbox, tmp_path, monkeypatch):
    support.write_cli(sandbox, "2.1.329")
    support.write_extension(sandbox, "2.1.328")
    run = support.doctor(tmp_path, sandbox, monkeypatch)          # no --json
    assert run.returncode == 0, f"a patch-only gap must not fail doctor (plain output)\n{run.describe()}"
    lines = (run.stdout + "\n" + run.stderr).splitlines()
    assert any("2.1.329" in line and "2.1.328" in line for line in lines), (
        f"the plain output does not name the drift between 2.1.329 and 2.1.328 on one line\n{run.describe()}")
    assert "drift" in (run.stdout + run.stderr).lower(), f"the plain output does not say drift\n{run.describe()}"


def test_equal_versions_are_no_drift_and_doctor_exits_0(sandbox, tmp_path, monkeypatch):
    """Control: no gap, no drift."""
    support.write_cli(sandbox, "2.1.329")
    support.write_extension(sandbox, "2.1.329")
    run = support.doctor(tmp_path, sandbox, monkeypatch, "--json")
    envelope = support.envelope(run)
    assert run.returncode == 0 and envelope.get("ok") is True and envelope["result"].get("healthy") is True, (
        run.describe())
    part = support.section(run)
    assert part.get("drift") is not True and not _issue_texts(part, "drift"), f"equal versions are no drift: {part}"


# --------------------------------------------------------------------------------------------------------------
# A2: larger gaps and real failures still end doctor with exit 3
# --------------------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("cli,extension", [
    ("2.2.0", "2.1.329"),     # the CLI one minor ahead
    ("2.1.329", "2.2.0"),     # the extension one minor ahead
    ("2.1.329", "2.2.5"),     # the extension a minor ahead with a patch number besides
    ("3.0.0", "2.1.329"),     # a major ahead
    ("2.1.329", "3.0.0"),     # the extension a major ahead
])
def test_a_gap_beyond_the_patch_number_fails_doctor(sandbox, tmp_path, monkeypatch, cli, extension):
    support.write_cli(sandbox, cli)
    support.write_extension(sandbox, extension)
    run = support.doctor(tmp_path, sandbox, monkeypatch, "--json")
    part = _unhealthy(run)
    assert (part.get("cli_version"), part.get("extension_version")) == (cli, extension), part
    assert [text for text in _issue_texts(part) if cli in text and extension in text], (
        f"no issue names both versions {cli} and {extension}: {part}")


@pytest.mark.parametrize("extension", ["2.1.280", "2.1.290"], ids=["extension-also-below", "extension-above"])
def test_a_cli_below_the_minimum_fails_doctor(sandbox, tmp_path, monkeypatch, extension):
    support.write_cli(sandbox, "2.1.280")
    support.write_extension(sandbox, extension)
    run = support.doctor(tmp_path, sandbox, monkeypatch, "--json")
    part = _unhealthy(run)
    assert part.get("cli_version") == "2.1.280" and part.get("status") == "fail", part
    assert [text for text in _issue_texts(part, "failure") if "2.1.280" in text], f"no failure names 2.1.280: {part}"


def test_a_cli_with_another_sha256_than_the_record_fails_doctor(sandbox, tmp_path, monkeypatch):
    sha = support.write_cli(sandbox, "2.1.329")
    support.write_extension(sandbox, "2.1.329")
    registry = support.claude_code_registry("2.1.329", "0" * 64)
    assert sha != "0" * 64
    run = support.doctor(tmp_path, sandbox, monkeypatch, "--json", registry=registry)
    part = _unhealthy(run)
    assert part.get("cli_sha256") == sha and part.get("status") == "fail" and _issue_texts(part, "failure"), part


def test_a_patch_only_gap_does_not_mask_a_cli_sha256_failure(sandbox, tmp_path, monkeypatch):
    support.write_cli(sandbox, "2.1.329")
    support.write_extension(sandbox, "2.1.328")
    registry = support.claude_code_registry("2.1.329", "0" * 64)    # the CLI is at the recorded version, other hash
    run = support.doctor(tmp_path, sandbox, monkeypatch, "--json", registry=registry)
    part = _unhealthy(run)
    assert part.get("status") == "fail" and _issue_texts(part, "failure"), part


def test_a_patch_only_gap_does_not_mask_an_extension_below_the_minimum(sandbox, tmp_path, monkeypatch):
    support.write_cli(sandbox, "2.1.290")
    support.write_extension(sandbox, "2.1.280")                      # same minor as the CLI, below 2.1.285
    run = support.doctor(tmp_path, sandbox, monkeypatch, "--json")
    part = _unhealthy(run)
    assert part.get("status") == "fail" and [t for t in _issue_texts(part, "failure") if "2.1.280" in t], part


def test_a_patch_only_gap_does_not_mask_drift_from_the_record(sandbox, tmp_path, monkeypatch):
    """Both binaries are newer than the registry's record (2.1.288): that drift is not the CLI/extension gap, so
    the exemption does not cover it (the existing rule of W1-27: a CLI newer than the record is drift, exit 3)."""
    sha = support.write_cli(sandbox, "2.1.329")
    support.write_extension(sandbox, "2.1.328")
    run = support.doctor(tmp_path, sandbox, monkeypatch, "--json", registry=support.claude_code_registry("2.1.288", sha))
    part = _unhealthy(run)
    assert [t for t in _issue_texts(part, "drift") if "2.1.329" in t and "2.1.288" in t], part
