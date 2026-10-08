"""Where a close finds the ticket tool (DEC-492): the installed kernel's place, and where that holds nothing, on
``PATH``; the kernel's wins where both exist; with neither the error says so. One lookup serves closing and
repair tickets."""
from __future__ import annotations

import os
import shutil

import pytest

from gov.cli.errors import GovError
from gov.close import tool
from gov.close.command import _record_and_close
from gov.tasks.tickets import frontmatter

from .conftest import TK

TICKET = "T-0001"
TOOL = "governance/kernel/bin/tk"
FAILS = "#!/bin/sh\necho 'planted failure' >&2\nexit 7\n"


def _on_path(monkeypatch, folder, script=None):
    """``folder/tk`` as the only ticket tool on ``PATH``: the real one, or ``script``."""
    folder.mkdir(parents=True, exist_ok=True)
    placed = folder / "tk"
    if script is None:
        shutil.copy2(TK, placed)
    else:
        placed.write_text(script, encoding="utf-8")
    placed.chmod(0o755)
    others = [entry for entry in os.environ["PATH"].split(os.pathsep)
              if entry and not os.path.exists(os.path.join(entry, "tk"))]
    monkeypatch.setenv("PATH", os.pathsep.join([str(folder), *others]))
    return placed


def _status(root):
    return frontmatter(root / ".tickets" / f"{TICKET}.md")["status"]


def test_the_kernels_tool_is_found_at_its_place(root):
    assert tool.find(root) == root / TOOL


def test_without_the_kernels_the_tool_on_path_is_found(root, monkeypatch, tmp_path):
    (root / TOOL).unlink()
    placed = _on_path(monkeypatch, tmp_path / "bin")
    assert tool.find(root) == placed


def test_a_tool_found_through_a_relative_entry_of_path_is_named_whole(root, monkeypatch, tmp_path):
    """The tool is started in the project's folder, where the caller's relative entry names another place."""
    (root / TOOL).unlink()
    placed = _on_path(monkeypatch, tmp_path / "bin")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("PATH", "bin" + os.pathsep + os.environ["PATH"].split(os.pathsep, 1)[1])
    assert tool.find(root) == placed and tool.find(root).is_absolute()


def test_the_tool_on_path_closes_and_opens_the_repair_ticket(root, monkeypatch, tmp_path):
    (root / TOOL).unlink()
    _on_path(monkeypatch, tmp_path / "bin")
    repair = tool.open_repair_ticket(root, TICKET, ["a finding"])
    front = frontmatter(root / ".tickets" / f"{repair}.md")
    assert front["parent"] == TICKET and front["deps"] == [TICKET]
    tool.close(root, TICKET)
    assert _status(root) == "closed"


def test_the_kernels_tool_wins_where_both_exist(root, monkeypatch, tmp_path):
    marker = tmp_path / "started"
    _on_path(monkeypatch, tmp_path / "bin", f'#!/bin/sh\necho "$@" >> "{marker}"\nexit 7\n')
    assert tool.find(root) == root / TOOL
    tool.close(root, TICKET)
    assert _status(root) == "closed" and not marker.exists()


@pytest.mark.parametrize("kernels", ["fails", "not-executable", "a-folder"])
def test_whatever_lies_at_the_kernels_place_is_not_replaced_by_the_tool_on_path(root, monkeypatch, tmp_path, kernels):
    marker = tmp_path / "started"
    _on_path(monkeypatch, tmp_path / "bin", f'#!/bin/sh\necho "$@" >> "{marker}"\nexec "{TK}" "$@"\n')
    place = root / TOOL
    place.unlink()
    if kernels == "a-folder":
        place.mkdir()
    else:
        place.write_text(FAILS, encoding="utf-8")
        place.chmod(0o755 if kernels == "fails" else 0o644)
    with pytest.raises(GovError) as raised:
        tool.close(root, TICKET)
    assert raised.value.code == "TICKET_TOOL_FAILED" and raised.value.details["tool"] == str(place)
    assert tool.open_repair_ticket(root, TICKET, ["a finding"]).startswith("not opened")
    assert not marker.exists() and _status(root) == "in_progress"


def test_with_neither_the_error_names_both_places(root, monkeypatch, tmp_path):
    (root / TOOL).unlink()
    monkeypatch.setenv("PATH", str(tmp_path / "no-such-folder"))
    with pytest.raises(GovError) as raised:
        tool.tk(root, "close", TICKET)
    assert raised.value.code == "TICKET_TOOL_ABSENT" and raised.value.details["command"] == "close"
    assert TOOL in raised.value.message and "PATH" in raised.value.message
    said = tool.open_repair_ticket(root, TICKET, ["a finding"])
    assert said.startswith("not opened") and "PATH" in said


def test_a_tool_that_answers_without_closing_has_not_closed_the_ticket(root, monkeypatch, tmp_path):
    """The tool on ``PATH`` is whatever carries its name: its exit code alone closes nothing."""
    (root / TOOL).unlink()
    _on_path(monkeypatch, tmp_path / "bin", "#!/bin/sh\nexit 0\n")
    with pytest.raises(GovError) as raised:
        _record_and_close(root, TICKET, {}, [])
    assert raised.value.code == "TICKET_TOOL_FAILED" and "in_progress" in raised.value.message
    assert _status(root) == "in_progress"
    assert not [path for folder in ("docs/close", "docs/checkpoints") for path in (root / folder).rglob("*.md")]
