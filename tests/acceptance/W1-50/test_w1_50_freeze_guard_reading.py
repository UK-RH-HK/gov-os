"""W1-50, KPI line 1 (DEC-402), the guard's half: what freezes, what does not, and what is recorded.

"A freeze flag set by gov pause carries a marker line; the guard treats an
empty file, or one without the marker, at the flag's path as no freeze and
records its presence."

The guard is asked as W1-02's suite asks it: the kernel's PreToolUse hook as a
process, in a temporary project. The question is always the same one, a Write
by the engineer inside its ticket's paths, which nothing but a freeze denies.

The readings, with their sources, are in ``w1_50_freeze_README.md``. In short:

- nothing at the path, an empty file, a file without the marker, a link to
  either, and the character device a session sees inside the sandbox: **no
  freeze** (DEC-402; the live observation of 2026-10-05);
- a marker line, whatever follows or precedes it, and its near spellings:
  **frozen**;
- whatever the guard cannot read as a file (a directory, a dangling link, a
  file it may not open): **frozen**, the stricter reading (DEC-179);
- an unmarked presence is one line in ``.gov-runtime/records.jsonl`` per call
  (DEC-177's form), never a finding, and a records file that cannot be written
  changes no answer;
- the hook's second reading, for an install (W1-04), reads the flag the same
  way.
"""

from __future__ import annotations

import os
import re

import pytest

import w1_50_freeze_support as support
from w1_50_freeze_support import freeze_project, freeze_sandbox  # noqa: F401  fixtures

MARKER = support.A_MARKER_LINE
BOM = b"\xef\xbb\xbf"


def _elsewhere_file(sandbox, name, text):
    path = sandbox.elsewhere / name
    path.write_text(text, encoding="utf-8")
    return path


# name: what is put at the flag's path. Each returns nothing; ``project`` and ``sandbox`` are this test's own.
NOT_FROZEN = {
    "nothing-at-the-path": lambda project, sandbox: None,
    "an-empty-file-0444": lambda project, sandbox: support.put_placeholder(project),
    "text-without-the-marker": lambda project, sandbox: support.put_text(project, "off\n"),
    "a-link-to-a-file-without-the-marker":
        lambda project, sandbox: support.put_link(project, _elsewhere_file(sandbox, "unmarked", "off\n")),
    "a-character-device": lambda project, sandbox: support.put_link(project, "/dev/null"),
}
RECORDED = sorted(set(NOT_FROZEN) - {"nothing-at-the-path"})

FROZEN = {
    "the-marker-line": lambda project, sandbox: support.put_text(project, MARKER),
    "the-marker-line-then-more": lambda project, sandbox: support.put_text(project, MARKER + "false\noff\n"),
    "the-marker-line-after-other-lines": lambda project, sandbox: support.put_text(project, "a note\n" + MARKER),
    "a-link-to-a-file-with-the-marker":
        lambda project, sandbox: support.put_link(project, _elsewhere_file(sandbox, "marked", MARKER)),
    "a-directory": lambda project, sandbox: support.put_directory(project),
    "a-dangling-link": lambda project, sandbox: support.put_link(project, sandbox.elsewhere / "no-such-file"),
    "a-file-the-guard-cannot-read": lambda project, sandbox: support.put_text(project, "off\n", mode=0o000),
    # Near spellings of the marker line: the stricter reading freezes.
    "a-byte-order-mark-before-the-marker": lambda project, sandbox: support.put_text(project, BOM + MARKER.encode()),
    "crlf-line-ends": lambda project, sandbox: support.put_text(project, MARKER.replace("\n", "\r\n") + "more\r\n"),
    "another-letter-case": lambda project, sandbox: support.put_text(project, MARKER.replace("FROZEN", "frozen")),
    "blank-lines-before-the-marker": lambda project, sandbox: support.put_text(project, "\n\n" + MARKER),
    "trailing-spaces": lambda project, sandbox: support.put_text(project, MARKER.replace("\n", "   \n")),
    "a-very-large-file-marker-first":
        lambda project, sandbox: support.put_text(project, MARKER + "x" * 79 + "\n" + ("filler line\n" * 400_000)),
}


@pytest.fixture()
def project(freeze_project):  # noqa: F811
    return freeze_project


@pytest.fixture()
def sandbox(freeze_sandbox):  # noqa: F811
    return freeze_sandbox


# --------------------------------------------------------------------------
# No freeze
# --------------------------------------------------------------------------

@pytest.mark.parametrize("shape", sorted(NOT_FROZEN))
def test_what_is_not_a_marked_flag_does_not_freeze(project, sandbox, shape):
    NOT_FROZEN[shape](project, sandbox)
    for tool_name in ("Write", "Edit"):
        result = support.guard_write(project, sandbox, tool_name)
        support.assert_not_frozen(result, f"with {shape} at {support.FLAG_REL}, {tool_name}")
    command = f"echo changed > {support.OWN_REL}"
    result = support.guard_bash(project, sandbox, command)
    support.assert_not_frozen(result, f"with {shape} at {support.FLAG_REL}, Bash `{command}`")


# --------------------------------------------------------------------------
# Frozen
# --------------------------------------------------------------------------

@pytest.mark.parametrize("shape", sorted(FROZEN))
def test_a_marked_flag_and_what_the_guard_cannot_read_freeze(project, sandbox, shape):
    if shape == "a-file-the-guard-cannot-read" and os.geteuid() == 0:
        pytest.skip("root reads a file of mode 000")
    support.assert_not_frozen(support.guard_write(project, sandbox), "before anything is at the flag's path, Write")
    FROZEN[shape](project, sandbox)
    for tool_name in ("Write", "Edit"):
        result = support.guard_write(project, sandbox, tool_name)
        support.assert_frozen(result, f"with {shape} at {support.FLAG_REL}, {tool_name}")
    command = f"echo changed > {support.OWN_REL}"
    support.assert_frozen(support.guard_bash(project, sandbox, command),
                          f"with {shape} at {support.FLAG_REL}, Bash `{command}`")


def test_a_freeze_ends_when_the_marker_goes(project, sandbox):
    """The same path, three states in a row: marked, emptied, marked again."""
    support.put_text(project, MARKER)
    support.assert_frozen(support.guard_write(project, sandbox), "with the marker line")
    support.put_text(project, "")
    support.assert_not_frozen(support.guard_write(project, sandbox), "after the flag was emptied")
    support.put_text(project, MARKER)
    support.assert_frozen(support.guard_write(project, sandbox), "with the marker line again")


# --------------------------------------------------------------------------
# The record of an unmarked presence
# --------------------------------------------------------------------------

@pytest.mark.parametrize("shape", RECORDED)
def test_an_unmarked_presence_is_recorded(project, sandbox, shape):
    """One line in ``records.jsonl``, in DEC-177's form (DEC-122's fields, ``action: "recorded"``)."""
    NOT_FROZEN[shape](project, sandbox)
    support.assert_not_frozen(support.guard_write(project, sandbox), f"with {shape} at {support.FLAG_REL}, Write")

    records = support.flag_records(project)
    assert len(records) == 1, (
        f"with {shape} at {support.FLAG_REL}, one allowed Write left {len(records)} lines naming the path in "
        f"{support.RECORDS_REL}, not one: {support.json_lines(project, support.RECORDS_REL)}"
    )
    record = records[0]
    missing = [name for name in support.RECORD_FIELDS if name not in record]
    assert not missing, f"the record lacks {missing} (DEC-122's fields, DEC-177): {record}"
    assert record["action"] == support.RECORDED, f"the record's action is {record['action']!r}: {record}"
    assert record["paths"] == [support.FLAG_REL], f"the record's paths are {record['paths']!r}: {record}"
    assert record["session_id"] == support.guard_support.SESSION_ID, record
    assert (record["role"], record["ticket"], record["tool"]) == (support.ENGINEER, support.TICKET, "Write"), record
    assert isinstance(record["reason"], str) and record["reason"].strip(), f"the record gives no reason: {record}"
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", str(record["time"])), record


def test_an_unmarked_presence_is_a_record_and_not_a_finding(project, sandbox):
    """DEC-177: ``findings.jsonl`` and its action list are unchanged."""
    support.put_placeholder(project)
    support.assert_not_frozen(support.guard_write(project, sandbox), "with a placeholder, Write")
    assert support.flag_findings(project) == [], (
        f"the placeholder is in {support.FINDINGS_REL}: {support.flag_findings(project)}"
    )


def test_the_presence_is_recorded_once_for_each_call(project, sandbox):
    """DEC-177: one JSON line per call. Nothing is remembered from one call to the next."""
    support.put_placeholder(project)
    for count in (1, 2, 3):
        support.assert_not_frozen(support.guard_write(project, sandbox), f"call {count} with a placeholder")
        assert len(support.flag_records(project)) == count, (
            f"after {count} calls, {support.RECORDS_REL} holds {len(support.flag_records(project))} lines "
            f"naming {support.FLAG_REL}"
        )


def test_nothing_is_recorded_when_nothing_is_at_the_path(project, sandbox):
    support.assert_not_frozen(support.guard_write(project, sandbox), "with nothing at the path, Write")
    assert support.flag_records(project) == [], support.flag_records(project)
    assert support.flag_findings(project) == [], support.flag_findings(project)


def test_a_records_file_that_cannot_be_written_does_not_stop_an_unfrozen_call(project, sandbox):
    """The record is an observation: it never blocks a call and never fails one."""
    support.put_placeholder(project)
    (project / support.RECORDS_REL).mkdir(parents=True)   # nothing can be appended to a directory
    for tool_name in ("Write", "Edit"):
        result = support.guard_write(project, sandbox, tool_name)
        support.assert_not_frozen(result, f"with a placeholder and no writable records file, {tool_name}")


def test_a_records_file_that_cannot_be_written_does_not_lift_a_freeze(project, sandbox):
    support.put_text(project, MARKER)
    (project / support.RECORDS_REL).mkdir(parents=True)
    support.assert_frozen(support.guard_write(project, sandbox), "with the marker and no writable records file")


# --------------------------------------------------------------------------
# The hook's second reading: an install (W1-04, DEC-120)
# --------------------------------------------------------------------------

INSTALL = "pip install requests"
# shape: (what is put at the path, the orchestrator's answer). Before anything is there the answer is "ask".
INSTALL_READINGS = {
    "an-empty-file-0444": (NOT_FROZEN["an-empty-file-0444"], "ask"),
    "text-without-the-marker": (NOT_FROZEN["text-without-the-marker"], "ask"),
    "the-marker-line": (FROZEN["the-marker-line"], "deny"),
    "another-letter-case": (FROZEN["another-letter-case"], "deny"),
    "a-directory": (FROZEN["a-directory"], "deny"),
}


@pytest.mark.parametrize("shape", sorted(INSTALL_READINGS))
def test_the_install_rule_reads_the_flag_as_the_guard_does(project, sandbox, shape):
    """An install writes nothing in the repository, so only the hook's own reading of the flag decides it."""
    put, expected = INSTALL_READINGS[shape]
    ask = support.guard_bash(project, sandbox, INSTALL, role=support.ORCHESTRATOR, ticket=support.ORCHESTRATOR_TICKET)
    assert ask.decision == "ask", f"`{INSTALL}` by the orchestrator, nothing at the path: {ask.describe()}"
    put(project, sandbox)
    result = support.guard_bash(project, sandbox, INSTALL, role=support.ORCHESTRATOR,
                                ticket=support.ORCHESTRATOR_TICKET)
    assert result.decision == expected and result.returncode == 0, (
        f"with {shape} at {support.FLAG_REL}, `{INSTALL}` by the orchestrator is not answered {expected!r}: "
        f"{result.describe()}"
    )
    if expected == "deny":
        assert "frozen" in result.stdout.lower(), f"the denial does not name the freeze: {result.describe()}"
