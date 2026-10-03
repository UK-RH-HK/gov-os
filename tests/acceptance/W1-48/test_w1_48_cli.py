"""W1-48 — the CLI for headless runs and the VS Code extension's bundled version are the pin.

KPI success 2: "The CLI used for headless runs and the VS Code extension's
bundled version are the same version, at or above the pin, and the registry
record states both [CAP-61.e]".

KPI failure 1: "A headless run uses a CLI below 2.1.285".

CAP-61.e: "Sessions run on Claude Code 2.1.285 or later, and the CLI used for
headless runs is aligned with the VS Code extension's bundled version".

DEC-205: "Every headless worker is started with the absolute path
``~/.local/bin/claude``, never a bare ``claude``", and "W1-48's test designer
adds a check that the pinned CLI is the one at ``~/.local/bin/claude``". So
"the CLI used for headless runs" is that file. No test here looks ``claude`` up
through ``PATH``: a second ``claude`` (a Windows-side copy) is on it.

DEC-196, DEC-203: Claude Code's CLI is a single-file binary, so the registry's
sha256 is that binary's.

The tests of what is on this machine are ``local_only``. They read files that
are there and run ``--version``; no session is started. They fail, not skip,
when the file is absent: on this machine it must be there.

Which of several extension folders on disk is "the" extension is an open
decision package (README, DP-1). The one extension test here holds under every
option of that package.
"""

from __future__ import annotations

import os
import re

import pytest

import w1_48_support as support

NAMES = support.CLAUDE_CODE

HOME_CLI = re.compile(r"(?<![\w.~/-])(?:~|\$HOME|\$\{HOME\}|/home/[^/\s]+)/\.local/bin/claude(?![\w.-])")
EXTENSION_WORD = re.compile(r"extension", re.IGNORECASE)

NO_CLI = f"~/{support.CLI_REL} does not exist: the CLI that headless workers start (DEC-205) is not installed"


def _entry(registry):
    return support.one(registry, NAMES)


def _pin(registry):
    return support.norm_version(_entry(registry).get("version", ""))


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
    """One clause of the record, outside ``version`` and the two commands, holds "extension" and the pinned version.

    ``version`` is the CLI's version. The extension's is stated beside it: in
    the note, or in a fact of its own whose key holds "extension".
    """
    entry = _entry(registry)
    pin = _pin(registry)
    stated = [clause for statement in support.statements(entry, skip=("version", "install", "uninstall"))
              for clause in support.clauses(statement)
              if EXTENSION_WORD.search(clause) and support.names_version(clause, pin)]
    assert pin and stated, (
        f"the Claude Code entry states the CLI's version ({pin!r}) but no clause of it names the VS Code extension "
        f"together with that version: the record must state both (CAP-61.e)"
    )


def test_the_record_states_no_other_version_for_the_extension(registry):
    """ "The same version": a clause that names the extension names no Claude Code version but the pin."""
    entry = _entry(registry)
    pin = _pin(registry)
    other = sorted({token for statement in support.statements(entry, skip=("version", "install", "uninstall"))
                    for clause in support.clauses(statement) if EXTENSION_WORD.search(clause)
                    for token in re.findall(r"(?<![0-9.])2\.\d+\.\d+(?![0-9]|\.[0-9])", clause) if token != pin})
    assert other == [], (
        f"the Claude Code entry pins {pin} and names the extension with {other}: the two must be the same version"
    )


# --------------------------------------------------------------------------
# The CLI on this machine (success 2, failure 1, DEC-205, DEC-196)
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


@pytest.mark.local_only
def test_the_cli_for_headless_runs_is_the_pinned_version(registry):
    """Success 2, "at or above the pin", with DEC-205: the pin is the version of the file at ``~/.local/bin/claude``.

    The CLI is not allowed to be newer than the record either: the registry
    pins one exact version, and a newer CLI is a raise of the pin that nobody
    recorded (failure 3).
    """
    pin = _pin(registry)
    assert support.CLI.is_file(), NO_CLI
    text, version = support.cli_version()
    assert version == pin, f"~/{support.CLI_REL} is Claude Code {text!r}; the registry pins {pin!r}"


@pytest.mark.local_only
def test_the_pinned_binary_is_the_one_at_local_bin_claude(registry):
    """DEC-205 and DEC-196: the registry's sha256 is the digest of the file ``~/.local/bin/claude`` resolves to."""
    recorded = support.field(_entry(registry), "sha256").lower()
    assert support.CLI.is_file(), NO_CLI
    found = support.file_sha256(support.CLI)
    assert recorded == found, (
        f"the registry records sha256 {recorded} for Claude Code; {os.path.realpath(support.CLI)} has {found}"
    )


# --------------------------------------------------------------------------
# The VS Code extension on this machine (success 2), as far as DP-1 leaves it clear
# --------------------------------------------------------------------------

@pytest.mark.local_only
def test_a_vs_code_extension_at_the_pinned_version_bundles_the_pinned_cli(registry):
    """Whichever folder is "the" extension (DP-1), one at the pin must be on disk and bundle a CLI at the pin.

    The folder's version is read from its ``package.json``; its bundled binary
    (``resources/native-binary/claude``) is asked with ``--version``.
    """
    pin = _pin(registry)
    folders = support.extension_folders()
    assert pin in folders, (
        f"no Claude Code extension at {pin} under {support.EXTENSIONS} (on disk: {sorted(folders) or 'none'}): "
        "the extension's bundled version cannot be the pin"
    )
    bundled = folders[pin] / support.BUNDLED_REL
    assert bundled.is_file(), f"{folders[pin].name} bundles no CLI at {support.BUNDLED_REL}"
    text, version = support.printed_version([bundled, "--version"])
    assert version == pin, f"{folders[pin].name} bundles Claude Code {text!r}; the registry pins {pin!r}"
