"""W1-48 — DEC-210: below the minimum is a hard failure; a difference is drift. Tested on fixed sample values.

DEC-210: "The check is dynamic, not exact. It is a hard failure only if the CLI
or the active extension is below the minimum, 2.1.285 (DEC-153). If the CLI
and the extension differ, or either is newer than the registry's record, that
is drift that ``gov doctor`` reports, not a test failure."

DEC-214 (refines DEC-210): "For the CLI at ``~/.local/bin/claude``, the
recorded version with a different sha256 is a hard failure. For the active
extension's bundled binary it is drift, reported by ``gov doctor``."

KPI failure 1: "A headless run uses a CLI below 2.1.285". CAP-61.e: "Sessions
run on Claude Code 2.1.285 or later".

The ``local_only`` case of ``test_w1_48_cli.py`` gives the rule what this
machine holds. Here the same rule (``support.compare_with_record``) is given
fixed values, so that both sides are exercised without changing the machine,
and the reading of VS Code's ``extensions.json`` is given fixed rows. No case
of this file reads the machine or the registry.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import w1_48_support as support

RECORDED = "2.1.288"
SHA_RECORDED = "a" * 64
SHA_OTHER = "b" * 64


def _seen(cli=RECORDED, package=RECORDED, binary=RECORDED, cli_sha=SHA_RECORDED, extension_sha=SHA_RECORDED):
    return support.Seen(cli_version=cli, cli_sha256=cli_sha, extension_package_version=package,
                        extension_binary_version=binary, extension_sha256=extension_sha)


def _verdict(seen, recorded=RECORDED):
    return support.compare_with_record(recorded, SHA_RECORDED, seen)


# --------------------------------------------------------------------------
# The hard failure: below the minimum
# --------------------------------------------------------------------------

BELOW = {
    "the CLI one patch below": _seen(cli="2.1.284"),
    "the CLI far below": _seen(cli="2.0.999"),
    "the CLI a major version below": _seen(cli="1.9.999"),
    "the extension's package.json below": _seen(package="2.1.284"),
    "the extension's bundled binary below": _seen(binary="2.1.284"),
    "the extension below by both readings": _seen(package="2.1.283", binary="2.1.283"),
    "the CLI and the extension below": _seen(cli="2.1.284", package="2.1.284", binary="2.1.284"),
    "the CLI prints no version": _seen(cli=None),
    "the extension's package.json gives no version": _seen(package=None),
    "the bundled binary prints no version": _seen(binary=None),
    "the CLI's version is not digits and dots": _seen(cli="latest"),
}


@pytest.mark.parametrize("case", sorted(BELOW))
def test_a_cli_or_an_active_extension_below_the_minimum_is_a_hard_failure(case):
    verdict = _verdict(BELOW[case])
    assert verdict.failures, f"{case}: not a hard failure, and DEC-210 makes it one ({BELOW[case]})"


def test_a_version_below_the_minimum_fails_even_when_the_registry_records_it():
    """The minimum is 2.1.285 (DEC-153), not the registry's record: equal to a record of 2.1.284 still fails."""
    verdict = _verdict(_seen(cli="2.1.284", package="2.1.284", binary="2.1.284"), recorded="2.1.284")
    assert len(verdict.failures) == 3, f"three versions below the minimum, {len(verdict.failures)} reported"
    assert verdict.drift == (), f"nothing differs from the record here: {verdict.drift}"


def test_the_failure_names_what_is_below_the_minimum():
    verdict = _verdict(_seen(binary="2.1.284"))
    assert len(verdict.failures) == 1 and "bundled binary" in verdict.failures[0] and "2.1.284" in verdict.failures[0]


# --------------------------------------------------------------------------
# Not a failure: at or above the minimum, whatever the record says
# --------------------------------------------------------------------------

AT_OR_ABOVE = {
    # case: (what is seen, whether it is drift)
    "all three equal to the record": (_seen(), False),
    "the CLI newer than the record": (_seen(cli="2.1.289", cli_sha=SHA_OTHER), True),
    "the extension newer than the record": (
        _seen(package="2.1.290", binary="2.1.290", extension_sha=SHA_OTHER), True),
    "both newer than the record, and equal": (
        _seen(cli="2.1.290", package="2.1.290", binary="2.1.290", cli_sha=SHA_OTHER, extension_sha=SHA_OTHER), True),
    "the CLI and the extension differ, both newer": (
        _seen(cli="2.1.289", package="2.1.291", binary="2.1.291", cli_sha=SHA_OTHER, extension_sha=SHA_OTHER), True),
    "the CLI older than the record, at the minimum": (_seen(cli="2.1.285", cli_sha=SHA_OTHER), True),
    "the extension older than the record, above the minimum": (
        _seen(package="2.1.286", binary="2.1.286", extension_sha=SHA_OTHER), True),
    "all three exactly at the minimum": (
        _seen(cli="2.1.285", package="2.1.285", binary="2.1.285", cli_sha=SHA_OTHER, extension_sha=SHA_OTHER), True),
    "the package.json and the bundled binary differ": (_seen(package="2.1.289"), True),
    "a later minor version": (
        _seen(cli="2.2.0", package="2.2.0", binary="2.2.0", cli_sha=SHA_OTHER, extension_sha=SHA_OTHER), True),
    "a later major version": (
        _seen(cli="3.0.0", package="3.0.0", binary="3.0.0", cli_sha=SHA_OTHER, extension_sha=SHA_OTHER), True),
    "a patch number with four digits": (_seen(cli="2.1.1000", cli_sha=SHA_OTHER), True),
    "a minor number of two digits": (_seen(cli="2.10.0", cli_sha=SHA_OTHER), True),
}


@pytest.mark.parametrize("case", sorted(AT_OR_ABOVE))
def test_a_cli_and_an_active_extension_at_or_above_the_minimum_are_no_hard_failure(case):
    seen, _ = AT_OR_ABOVE[case]
    verdict = _verdict(seen)
    assert verdict.failures == (), f"{case}: DEC-210 makes this no failure, and the check fails it: {verdict.failures}"


@pytest.mark.parametrize("case", sorted(AT_OR_ABOVE))
def test_a_difference_at_or_above_the_minimum_is_reported_as_drift(case):
    """Drift is what ``gov doctor`` will report: every difference is named, and equal versions name none."""
    seen, drifts = AT_OR_ABOVE[case]
    verdict = _verdict(seen)
    assert bool(verdict.drift) is drifts, f"{case}: drift expected {drifts}, reported {verdict.drift}"


def test_a_record_written_with_a_leading_v_is_the_same_version():
    verdict = _verdict(_seen(), recorded="v2.1.288")
    assert verdict == support.Verdict((), (), ()), f"v2.1.288 and 2.1.288 are the same pin: {verdict}"


def test_a_failure_and_drift_are_told_apart_in_one_look():
    """The CLI below the minimum and the extension newer than the record: one failure, and drift beside it."""
    verdict = _verdict(_seen(cli="2.1.284", package="2.1.290", binary="2.1.290"))
    assert len(verdict.failures) == 1 and "CLI" in verdict.failures[0]
    assert verdict.drift, "the extension is newer than the record and the CLI differs from it: that is drift too"


# --------------------------------------------------------------------------
# "the binary's sha256 is compared with the registry" (DEC-210); at the recorded version another digest fails
# for the CLI and is drift for the extension's bundled binary (DEC-214)
# --------------------------------------------------------------------------

def test_a_newer_binary_with_another_digest_is_drift_by_its_version_alone():
    """A different version has a different digest by itself: the digest is not reported a second time."""
    verdict = _verdict(_seen(cli="2.1.289", cli_sha=SHA_OTHER))
    assert verdict.failures == () and verdict.drift and verdict.digests == ()


def test_the_recorded_digest_is_compared_without_case():
    verdict = _verdict(_seen(cli_sha=SHA_RECORDED.upper(), extension_sha=SHA_RECORDED.upper()))
    assert verdict == support.Verdict((), (), ())


def test_the_cli_at_the_recorded_version_with_another_digest_is_a_hard_failure():
    """DEC-214: "For the CLI at ``~/.local/bin/claude``, the recorded version with a different sha256 is a hard
    failure." The failure names the CLI and the digest it has; nothing else differs, so there is no drift."""
    verdict = _verdict(_seen(cli_sha=SHA_OTHER))
    assert len(verdict.failures) == 1, (
        f"the CLI prints the recorded version and has another sha256: DEC-214 makes it one hard failure: {verdict}"
    )
    assert "CLI" in verdict.failures[0] and SHA_OTHER in verdict.failures[0] and SHA_RECORDED in verdict.failures[0]
    assert verdict.drift == (), f"the CLI's digest is a failure, not drift, and no version differs: {verdict.drift}"


def test_the_extensions_binary_at_the_recorded_version_with_another_digest_is_drift():
    """DEC-214: "For the active extension's bundled binary it is drift, reported by ``gov doctor``." No failure;
    the drift names the bundled binary and the digest it has."""
    verdict = _verdict(_seen(extension_sha=SHA_OTHER))
    assert verdict.failures == (), (
        f"the extension's bundled binary at the recorded version with another sha256 is drift (DEC-214), "
        f"and the check fails it: {verdict.failures}"
    )
    assert len(verdict.drift) == 1, f"one difference for `gov doctor` to report, {len(verdict.drift)} named"
    assert "bundled binary" in verdict.drift[0] and SHA_OTHER in verdict.drift[0] and SHA_RECORDED in verdict.drift[0]


def test_both_binaries_at_the_recorded_version_with_another_digest_are_one_failure_and_one_drift():
    """The same difference on both sides in one look: the CLI's fails, the extension's is reported (DEC-214)."""
    verdict = _verdict(_seen(cli_sha=SHA_OTHER, extension_sha=SHA_OTHER))
    assert len(verdict.failures) == 1 and "CLI" in verdict.failures[0], f"the CLI's digest alone fails: {verdict}"
    assert len(verdict.drift) == 1 and "bundled binary" in verdict.drift[0], f"the extension's is drift: {verdict}"


def test_the_clis_digest_fails_whatever_the_extension_is():
    """A newer extension is drift (DEC-210); it does not turn the CLI's digest difference into drift (DEC-214)."""
    verdict = _verdict(_seen(cli_sha=SHA_OTHER, package="2.1.290", binary="2.1.290", extension_sha="c" * 64))
    assert len(verdict.failures) == 1 and SHA_OTHER in verdict.failures[0], f"the CLI's digest must fail: {verdict}"
    assert verdict.drift, "the extension is newer than the record and than the CLI: that is drift beside the failure"


# --------------------------------------------------------------------------
# "the one VS Code has active, read from its extensions.json"
# --------------------------------------------------------------------------

def _row(extension_id, folder, version="2.1.288"):
    return {"identifier": {"id": extension_id}, "version": version, "relativeLocation": folder,
            "location": {"$mid": 1, "path": f"/home/someone/.vscode-server/extensions/{folder}", "scheme": "file"}}


INDEX = [
    _row("ms-python.python", "ms-python.python-2026.4.0", "2026.4.0"),
    _row("anthropic.claude-code", "anthropic.claude-code-2.1.288-linux-x64"),
    _row("openai.chatgpt", "openai.chatgpt-26.930.21537-linux-x64", "26.930.21537"),
]


def test_the_active_extension_is_the_row_of_extensions_json():
    rows = support.active_extension_rows(INDEX)
    assert [row["relativeLocation"] for row in rows] == ["anthropic.claude-code-2.1.288-linux-x64"]


def test_the_extension_id_is_compared_without_case():
    rows = support.active_extension_rows([_row("Anthropic.Claude-Code", "anthropic.claude-code-2.1.288-linux-x64")])
    assert len(rows) == 1


@pytest.mark.parametrize("index", [
    [],
    [_row("ms-python.python", "ms-python.python-2026.4.0")],
    [_row("anthropic.claude-code-helper", "anthropic.claude-code-helper-1.0.0")],
    [{"version": "2.1.288"}, "anthropic.claude-code", None],
    {"anthropic.claude-code-2.1.288-linux-x64": True},
    None,
], ids=["empty", "other extensions only", "another extension of a longer id", "rows without an identifier",
        "a mapping of folder names, as .obsolete is", "nothing"])
def test_an_index_without_a_claude_code_row_gives_no_active_extension(index):
    """A folder that is only on disk, or only listed in ``.obsolete``, is not the active extension."""
    assert support.active_extension_rows(index) == []


def test_the_folder_of_a_row_is_its_location():
    row = _row("anthropic.claude-code", "anthropic.claude-code-2.1.288-linux-x64")
    assert support.extension_folder(row) == Path(
        "/home/someone/.vscode-server/extensions/anthropic.claude-code-2.1.288-linux-x64")


def test_the_folder_of_a_row_without_a_location_is_its_relative_location_under_the_extensions_folder():
    row = {"identifier": {"id": "anthropic.claude-code"}, "relativeLocation": "anthropic.claude-code-2.1.290"}
    assert support.extension_folder(row, base=Path("/x/extensions")) == Path(
        "/x/extensions/anthropic.claude-code-2.1.290")
    assert support.extension_folder({"identifier": {"id": "anthropic.claude-code"}}) is None
