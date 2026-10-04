"""W1-48 — the CLI for headless runs and the active VS Code extension are at or above the minimum.

KPI success 2: "The CLI used for headless runs and the active VS Code
extension's bundled version are both at or above the minimum, 2.1.285, and the
registry record states both; a difference between them, or from the registry's
record, is drift that gov doctor reports, not a failure, except that the CLI
at the recorded version with another sha256 is a failure (DEC-210, DEC-214)
[CAP-61.e]".

KPI failure 1: "A headless run uses a CLI below 2.1.285".

CAP-61.e: "Sessions run on Claude Code 2.1.285 or later, and the CLI used for
headless runs is aligned with the VS Code extension's bundled version".

DEC-210 (the owner's answer on DP-1) says how this is tested:

- the extension is the one VS Code has active, read from its ``extensions.json``;
- its bundled version is read from both its ``package.json`` and its bundled
  binary's ``--version``, and the binary's sha256 is compared with the registry;
- it is a hard failure only if the CLI or the active extension is below the
  minimum, 2.1.285;
- if the CLI and the extension differ, or either is newer than the registry's
  record, that is drift, which ``gov doctor`` (W1-27) reports. It is not a test
  failure. The tests are "at or above the minimum", not "equal to the pin".

DEC-214 (the owner's answer on DP-3) refines it: the CLI at
``~/.local/bin/claude`` with the recorded version and another sha256 than the
registry's is a hard failure; for the active extension's bundled binary the
same difference is drift.

DEC-205: "Every headless worker is started with the absolute path
``~/.local/bin/claude``, never a bare ``claude``". So "the CLI used for
headless runs" is that file. No test here looks ``claude`` up through ``PATH``:
a second ``claude`` (a Windows-side copy) is on it.

The tests of what is on this machine are ``local_only``. They read files that
are there and run ``--version``; no session is started. They fail, not skip,
when the file is absent: on this machine it must be there. The rule that
decides between failure and drift is tested on fixed sample values in
``test_w1_48_drift.py``.
"""

from __future__ import annotations

import os
import re

import pytest

import w1_48_support as support

NAMES = support.CLAUDE_CODE

HOME_CLI = re.compile(r"(?<![\w.~/-])(?:~|\$HOME|\$\{HOME\}|/home/[^/\s]+)/\.local/bin/claude(?![\w.-])")
EXTENSION_WORD = re.compile(r"extension", re.IGNORECASE)
CLAUDE_CODE_VERSION = re.compile(r"(?<![0-9.])\d+\.\d+\.\d+(?![0-9]|\.[0-9])")

NO_CLI = f"~/{support.CLI_REL} does not exist: the CLI that headless workers start (DEC-205) is not installed"


def _entry(registry):
    return support.one(registry, NAMES)


def _pin(registry):
    return support.norm_version(_entry(registry).get("version", ""))


def _extension_versions(entry):
    """Every three-part version named in a clause of the record that holds "extension".

    ``version`` and the two commands are left out: ``version`` is the CLI's.
    """
    return [token for statement in support.statements(entry, skip=("version", "install", "uninstall"))
            for clause in support.clauses(statement) if EXTENSION_WORD.search(clause)
            for token in CLAUDE_CODE_VERSION.findall(clause)]


def _active_extensions():
    """``[(folder, bundled binary)]`` of the Claude Code extension VS Code has active; fails when there is none."""
    try:
        index = support.load_extensions_index()
    except support.Missing as exc:
        pytest.fail(str(exc), pytrace=False)
    rows = support.active_extension_rows(index)
    assert rows, (
        f"{support.EXTENSIONS / support.EXTENSIONS_INDEX} has no row for {support.EXTENSION_ID}: VS Code has no "
        "Claude Code extension active, so its bundled version cannot be shown to be at or above the minimum"
    )
    found = []
    for row in rows:
        folder = support.extension_folder(row)
        assert folder is not None and folder.is_dir(), (
            f"the {support.EXTENSION_ID} row of extensions.json points at {folder}, which is not a folder"
        )
        found.append((folder, folder / support.BUNDLED_REL))
    return found


# --------------------------------------------------------------------------
# "the registry record states both" (success 2) and DEC-205 for the record
# --------------------------------------------------------------------------

def test_the_record_is_about_the_cli_at_local_bin_claude(registry):
    """DEC-205: the record names the file ``~/.local/bin/claude``, in any fact of the entry."""
    entry = _entry(registry)
    text = "\n".join(support.statements(entry))
    assert HOME_CLI.search(text), (
        "the Claude Code entry does not name ~/.local/bin/claude (as ~, $HOME or an absolute home path): "
        "the record must say which `claude` is pinned, because a second one is on PATH (DEC-205)"
    )


def test_the_record_states_the_vs_code_extensions_bundled_version(registry):
    """One clause of the record, outside ``version`` and the two commands, holds "extension" and a version.

    ``version`` is the CLI's version. The extension's is stated beside it: in
    the note, or in a fact of its own whose key holds "extension". DEC-210: it
    need not equal the pin.
    """
    entry = _entry(registry)
    assert _extension_versions(entry), (
        f"the Claude Code entry states the CLI's version ({_pin(registry)!r}) but no clause of it names the VS Code "
        "extension together with a version: the record must state both (CAP-61.e)"
    )


def test_the_record_states_no_extension_version_below_the_minimum(registry):
    """DEC-210: a version the record names for the extension is 2.1.285 or later; it may differ from the pin."""
    entry = _entry(registry)
    floor = support.version_key(support.FLOOR)
    below = sorted({token for token in _extension_versions(entry) if support.version_key(token) < floor})
    assert below == [], (
        f"the Claude Code entry names the extension with {below}, below the minimum {support.FLOOR} (DEC-153)"
    )


# --------------------------------------------------------------------------
# The CLI on this machine (success 2, failure 1, DEC-205)
# --------------------------------------------------------------------------

@pytest.mark.local_only
def test_the_cli_at_local_bin_claude_is_installed():
    assert support.CLI.is_file(), NO_CLI
    assert os.access(support.CLI, os.X_OK), f"~/{support.CLI_REL} is not executable"


@pytest.mark.local_only
def test_the_cli_for_headless_runs_is_2_1_285_or_later():
    """Failure 1. This case reads no registry: it holds or fails on the machine alone."""
    assert support.CLI.is_file(), NO_CLI
    text, version = support.cli_version()
    assert version is not None, f"~/{support.CLI_REL} --version prints no version: {text!r}"
    assert support.version_key(version) >= support.version_key(support.FLOOR), (
        f"~/{support.CLI_REL} is Claude Code {version}: a headless run would use a CLI below {support.FLOOR}"
    )


# --------------------------------------------------------------------------
# The active VS Code extension on this machine (success 2, CAP-61.e, DEC-210)
# --------------------------------------------------------------------------

@pytest.mark.local_only
def test_vs_code_has_a_claude_code_extension_active_that_bundles_a_cli():
    """DEC-210: the extension is the row of ``extensions.json``; its folder holds a ``package.json`` and a binary."""
    for folder, bundled in _active_extensions():
        assert support.package_version(folder), f"{folder.name} has no package.json that gives a version"
        assert bundled.is_file(), f"{folder.name} bundles no CLI at {support.BUNDLED_REL}"


@pytest.mark.local_only
def test_the_active_vs_code_extension_is_2_1_285_or_later_by_its_package_json():
    floor = support.version_key(support.FLOOR)
    for folder, _ in _active_extensions():
        version = support.package_version(folder)
        assert version is not None and support.version_key(version) is not None, (
            f"the package.json of {folder.name} gives no version that can be compared with {support.FLOOR}: "
            f"{version!r}"
        )
        assert support.version_key(version) >= floor, (
            f"the active VS Code extension {folder.name} is {version} by its package.json, below {support.FLOOR}"
        )


@pytest.mark.local_only
def test_the_active_vs_code_extension_bundles_a_cli_at_2_1_285_or_later():
    """The bundled binary is asked with ``--version``; no session is started."""
    floor = support.version_key(support.FLOOR)
    for folder, bundled in _active_extensions():
        assert bundled.is_file(), f"{folder.name} bundles no CLI at {support.BUNDLED_REL}"
        text, version = support.printed_version([bundled, "--version"])
        assert version is not None, f"the CLI bundled in {folder.name} prints no version with --version: {text!r}"
        assert support.version_key(version) >= floor, (
            f"the active VS Code extension {folder.name} bundles Claude Code {version}, below {support.FLOOR}"
        )


# --------------------------------------------------------------------------
# This machine against the registry's record (DEC-210, DEC-214): below the minimum fails, and so does the CLI at
# the recorded version with another sha256; drift does not
# --------------------------------------------------------------------------

@pytest.mark.local_only
def test_this_machine_compared_with_the_record_shows_no_hard_failure(registry):
    """The CLI and the active extension are read as DEC-210 says and compared with the registry's record.

    Both versions of the extension are read, and both digests are taken and
    compared with the registry's. Two things fail: a version below the minimum
    (DEC-210), and the CLI at the recorded version with another sha256 than the
    registry's (DEC-214). A CLI or an extension that differs from the other,
    or from the record, is drift for ``gov doctor``, and so is the extension's
    bundled binary at the recorded version with another sha256 (DEC-214).
    """
    entry = _entry(registry)
    assert support.CLI.is_file(), NO_CLI
    _, cli_version = support.cli_version()
    cli_sha256 = support.file_sha256(support.CLI)
    for folder, bundled in _active_extensions():
        assert bundled.is_file(), f"{folder.name} bundles no CLI at {support.BUNDLED_REL}"
        _, binary_version = support.printed_version([bundled, "--version"])
        seen = support.Seen(cli_version=cli_version, cli_sha256=cli_sha256,
                            extension_package_version=support.package_version(folder),
                            extension_binary_version=binary_version,
                            extension_sha256=support.file_sha256(bundled))
        verdict = support.compare_with_record(support.field(entry, "version"), support.field(entry, "sha256"), seen)
        assert verdict.failures == (), (
            f"this machine is below the minimum {support.FLOOR} (DEC-210), or its CLI is the recorded version "
            f"with another sha256 than the registry's (DEC-214): {list(verdict.failures)}"
        )
