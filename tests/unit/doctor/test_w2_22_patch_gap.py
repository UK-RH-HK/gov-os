"""Unit tests for the patch-only CLI/extension gap of gov doctor's claude_code section (W2-22 fix, DEC-1227 D6 (a)).

A difference of the patch number only (same major and minor) is drift, reported and not blocking; a minor or major
difference, or a version that cannot be read, blocks as before.
"""

from __future__ import annotations

import pytest

from gov.doctor.command import _blocks_health, _failed_parts, _is_patch_only_gap


@pytest.mark.parametrize("cli, ext", (
    ("2.1.329", "2.1.328"),
    ("2.1.328", "2.1.329"),  # either direction
    ("2.1.329", "2.1.300"),  # a wide patch gap is still a patch gap
    ("v2.1.329", "2.1.328"),  # a v prefix is read
    ("2.1.329", "v2.1.328"),
))
def test_a_difference_of_the_patch_number_only_is_a_patch_only_gap(cli, ext):
    assert _is_patch_only_gap(cli, ext) is True


@pytest.mark.parametrize("cli, ext", (
    ("2.2.0", "2.1.329"),  # minor
    ("2.1.329", "2.2.0"),
    ("2.1.329", "2.2.5"),
    ("3.0.0", "2.1.329"),  # major
    ("2.1.329", "3.0.0"),
    ("3.1.329", "2.1.329"),  # major differs, minor and patch equal
))
def test_a_minor_or_major_difference_is_not_a_patch_only_gap(cli, ext):
    assert _is_patch_only_gap(cli, ext) is False


@pytest.mark.parametrize("cli, ext", (
    ("garbage", "2.1.328"),
    ("2.1.329", "garbage"),
    ("", "2.1.328"),
    ("2.1", "2.1"),  # no patch number to compare: not a patch-only gap
    ("2.1", "2.1.328"),
    ("2.1.329", "2.1"),
))
def test_a_version_that_cannot_be_parsed_stays_blocking(cli, ext):
    assert _is_patch_only_gap(cli, ext) is False


def test_the_same_version_is_no_gap():
    assert _is_patch_only_gap("2.1.329", "2.1.329") is False


def test_a_drift_with_a_blocking_issue_blocks_health():
    assert _blocks_health({"status": "drift", "drift_blocking": True}) is True


def test_a_patch_only_drift_alone_does_not_block_health():
    assert _blocks_health({"status": "drift", "drift_blocking": False}) is False


def test_a_drift_section_that_does_not_say_stays_blocking():
    # every other section's drift, and a claude_code section from before this fix
    assert _blocks_health({"status": "drift"}) is True


@pytest.mark.parametrize("section", (
    {"status": "fail"},
    {"status": "fail", "drift_blocking": False},  # a failure beside a patch-only gap
))
def test_a_failure_always_blocks_health(section):
    assert _blocks_health(section) is True


@pytest.mark.parametrize("status", ("pass", "unmeasured", "report"))
def test_the_other_statuses_do_not_block_health(status):
    assert _blocks_health({"status": status}) is False


def test_failed_parts_does_not_name_a_non_blocking_drift():
    sections = {"claude_code": {"status": "drift", "drift_blocking": False},
                "tools": {"status": "fail", "reason": "a tool is missing"}}
    assert _failed_parts(sections) == "tools (a tool is missing)"


def test_failed_parts_names_a_blocking_claude_code_drift():
    sections = {"claude_code": {"status": "drift", "drift_blocking": True}}
    assert _failed_parts(sections) == "claude_code"
