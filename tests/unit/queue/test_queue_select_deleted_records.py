"""``select.scoped`` with ``change`` (W2-115b's fixes I-1 and I-2, DEC-1239): a path the change deleted is listed
under ``deleted`` and is no selected target; a Markdown document nothing places is a record with a notice
``RECORD_PLACED <path>``; code nothing places still refuses; without ``change`` nothing changes."""
from __future__ import annotations

import os
import site

import pytest

from gov.close import select

from queue_support import TICKET, WBS, plant

OWN = {"src/pkg/feature.py": "def twice(x):\n    return 2 * x\n"}


@pytest.fixture
def project(tmp_path, monkeypatch):
    monkeypatch.setenv("PYTHONUSERBASE", site.getuserbase())
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", os.devnull)
    monkeypatch.delenv("GOV_ROLE", raising=False)
    return plant(tmp_path)


def _own(project, files):
    project.commit("the ticket's work", f"Task: {TICKET}", "Role: engineer", files=files)


def test_a_deleted_path_is_listed_and_not_selected_as_a_changed_test(project):
    gone = "tests/unit/pkg/test_old.py"
    project.commit("a test", f"Task: {TICKET}", "Role: engineer",
                   files={gone: "def test_a():\n    pass\n", "tests/unit/pkg/test_keep.py": "def test_b():\n    pass\n"})
    os.remove(project.root / gone)
    project.commit("delete it", f"Task: {TICKET}", "Role: engineer", files=OWN)
    chosen = select.scoped(project.root, TICKET, change=[gone, *OWN])
    assert chosen["deleted"] == [gone]
    assert gone not in chosen["why"] and gone not in chosen["suites"]
    assert "tests/unit/pkg/" in chosen["suites"], chosen["suites"]


def test_deleted_is_empty_with_change_and_absent_without(project):
    _own(project, OWN)
    assert select.scoped(project.root, TICKET, change=sorted(OWN))["deleted"] == []
    assert "deleted" not in select.scoped(project.root, TICKET)


def test_a_document_nothing_places_is_a_record_with_a_notice(project):
    _own(project, {**OWN, "notes/x.md": "# x\n"})
    chosen = select.scoped(project.root, TICKET, change=[*OWN, "notes/x.md"])
    assert "notes/x.md" in chosen["records"]
    assert chosen["notices"] == ["RECORD_PLACED notes/x.md"]


@pytest.mark.parametrize("doc", ["src/pkg/NOTES.md", "template/guide.md"])
def test_a_markdown_file_in_a_code_place_still_refuses(project, doc):
    _own(project, {**OWN, doc: "# x\n"})
    with pytest.raises(select.SelectionRefused) as raised:
        select.scoped(project.root, TICKET, change=[*OWN, doc])
    assert doc in raised.value.reason


def test_without_change_a_document_nothing_places_is_refused_as_before(project):
    _own(project, {**OWN, "notes/x.md": "# x\n"})
    with pytest.raises(select.SelectionRefused) as raised:
        select.scoped(project.root, TICKET)
    assert "notes/x.md" in raised.value.reason
