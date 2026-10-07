"""The repair ticket is opened through the ticket tool, or not at all (B3)."""
from __future__ import annotations

import subprocess

import pytest

from gov.cli.errors import GovError
from gov.close.command import _open_repair_ticket, _tk
from gov.tasks.tickets import frontmatter

TICKET = "T-0001"
TOOL = "governance/kernel/bin/tk"


def _tickets(root):
    return sorted(path.stem for path in (root / ".tickets").glob("*.md"))


def test_the_repair_ticket_has_the_parent_the_dependency_the_findings_and_the_class(root):
    repair = _open_repair_ticket(root, TICKET, ["test_x failed", "test_y failed"], "narrow", "ab" * 32)
    path = root / ".tickets" / f"{repair}.md"
    front = frontmatter(path)
    assert front["parent"] == TICKET and front["deps"] == [TICKET]
    assert front["disposition"] == "narrow" and front["context_hash"] == "ab" * 32
    text = path.read_text(encoding="utf-8")
    assert "test_x failed" in text and "test_y failed" in text


def test_the_ticket_tool_reads_the_dependency_back(root):
    repair = _open_repair_ticket(root, TICKET, ["a finding"])
    tree = subprocess.run([str(root / TOOL), "dep", "tree", repair], cwd=root, capture_output=True, text=True,
                          check=True).stdout.splitlines()
    assert repair in tree[0] and any(TICKET in line for line in tree[1:])
    assert frontmatter(root / ".tickets" / f"{TICKET}.md")["deps"] == []


def test_without_a_class_the_ticket_records_unclassed_and_no_hash(root):
    front = frontmatter(root / ".tickets" / f"{_open_repair_ticket(root, TICKET, ['a finding'])}.md")
    assert front["disposition"] == "unclassed" and "context_hash" not in front


def test_a_context_that_failed_is_named_and_no_hash_is_recorded(root):
    repair = _open_repair_ticket(root, TICKET, ["a finding"], "repair", None, "the context cannot be built: X")
    path = root / ".tickets" / f"{repair}.md"
    assert "context_hash" not in frontmatter(path)
    assert "the context cannot be built: X" in path.read_text(encoding="utf-8")


def test_an_absent_tool_opens_nothing_and_is_named(root):
    (root / TOOL).unlink()
    said = _open_repair_ticket(root, TICKET, ["a finding"])
    assert said.startswith("not opened") and "tk" in said
    assert _tickets(root) == [TICKET]


def test_a_failing_tool_opens_nothing_and_its_reason_is_given(root):
    (root / TOOL).write_text("#!/bin/sh\necho 'planted failure' >&2\nexit 7\n", encoding="utf-8")
    said = _open_repair_ticket(root, TICKET, ["a finding"])
    assert said.startswith("not opened") and "exit code 7" in said and "planted failure" in said
    assert _tickets(root) == [TICKET]


def test_a_dependency_the_tool_refuses_is_said(root):
    """``tk create`` works and ``tk dep`` fails: the answer names the ticket and the dependency not recorded."""
    tool = root / TOOL
    real = tool.with_name("tk-real")
    tool.rename(real)
    tool.write_text(f'#!/bin/sh\n[ "$1" = dep ] && {{ echo "planted dep failure" >&2; exit 5; }}\n'
                    f'exec "{real}" "$@"\n', encoding="utf-8")
    tool.chmod(0o755)
    said = _open_repair_ticket(root, TICKET, ["a finding"])
    assert "dependency" in said and "planted dep failure" in said
    assert len(_tickets(root)) == 2


def test_closing_through_the_tool(root):
    _tk(root, "close", TICKET)
    assert frontmatter(root / ".tickets" / f"{TICKET}.md")["status"] == "closed"


def test_closing_without_the_tool_is_an_error(root):
    (root / TOOL).unlink()
    with pytest.raises(GovError) as raised:
        _tk(root, "close", TICKET)
    assert raised.value.code == "TICKET_TOOL_ABSENT"
    assert frontmatter(root / ".tickets" / f"{TICKET}.md")["status"] == "in_progress"


def test_closing_with_a_failing_tool_is_an_error(root):
    (root / TOOL).write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
    with pytest.raises(GovError) as raised:
        _tk(root, "close", TICKET)
    assert raised.value.code == "TICKET_TOOL_FAILED"
