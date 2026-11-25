"""``select.scoped`` with ``change`` counts the change alone; a path nothing places is named with the line to add
(plan item 1-0, DEC-1244 X-1; ``.tickets/DAEO-j9z6.md`` "Fix: a trustworthy impact selection, SEL-1 to SEL-3").

The planted project is ``queue_support``'s, its test map placing the green record's folder (``docs/close/**``) as a
record. "The base's commit" is a commit after the green record with no ``Task:`` trailer of the ticket's.
"""
from __future__ import annotations

import json
import os
import site

import pytest
import yaml

from gov.close import select

from queue_support import TICKET, WBS, map_text, plant

MAP = "governance/project/test-map.yaml"
OWN = {"src/pkg/other.py": "def other():\n    return 2\n"}          # the branch's change: test_other imports it
OWN_SUITE = f"tests/acceptance/{WBS}/"
LONELY = "src/pkg/lonely.py"                                          # test_lonely imports it; no change of the branch's
DOC = "proposals/plan.md"
SCRIPT = "repin.sh"


def _map():
    data = yaml.safe_load(map_text())
    data["record_only"] = list(data["record_only"]) + ["docs/close/**"]
    return yaml.safe_dump(data, sort_keys=False)


@pytest.fixture
def project(tmp_path, monkeypatch):
    monkeypatch.setenv("PYTHONUSERBASE", site.getuserbase())
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", os.devnull)
    monkeypatch.delenv("GOV_ROLE", raising=False)
    repo = plant(tmp_path, extra={MAP: _map()})
    head = repo.sha()
    repo.commit("a green night", "Role: orchestrator",
                files={f"docs/close/nightly/NR-20261101T010000Z-{head[:12]}.json":
                       json.dumps({"verdict": "green", "head": head}) + "\n"})
    return repo


def _base(project, files, *trailers):
    project.commit("a direct commit", *(trailers or ("Role: orchestrator",)), files=files)


def _branch(project, files=None):
    project.commit("the branch's work", f"Task: {TICKET}", "Role: engineer", files=files or OWN)


# -- SEL-1: with change, the change alone ----------------------------------------------------------------------------

def test_sel1_a_path_the_base_added_after_the_green_record_is_not_counted_nor_selected(project):
    _base(project, {LONELY: "VALUE = 2  # moved on the base\n"})
    _branch(project)
    chosen = select.scoped(project.root, TICKET, change=sorted(OWN))
    assert chosen["changed"] == sorted(OWN), chosen["changed"]
    assert "tests/unit/test_lonely.py" not in chosen["suites"], chosen["suites"]
    assert "tests/unit/test_other.py" in chosen["suites"] and OWN_SUITE in chosen["suites"], chosen["suites"]


def test_sel1_the_ticket_s_earlier_commit_is_not_counted_either(project):
    project.commit("an earlier landing of the ticket", f"Task: {TICKET}", "Role: engineer",
                   files={LONELY: "VALUE = 2  # an earlier landing\n"})
    _branch(project)
    chosen = select.scoped(project.root, TICKET, change=sorted(OWN))
    assert chosen["changed"] == sorted(OWN), chosen["changed"]
    assert "tests/unit/test_lonely.py" not in chosen["suites"], chosen["suites"]


def test_sel1_the_base_s_unplaced_paths_are_neither_refused_nor_listed(project):
    _base(project, {DOC: "# a plan\n"})
    _base(project, {SCRIPT: "#!/bin/sh\necho repin\n"})
    _branch(project)
    chosen = select.scoped(project.root, TICKET, change=sorted(OWN))
    assert chosen["unplaced_base"] == [], chosen["unplaced_base"]
    assert DOC not in chosen["changed"] and SCRIPT not in chosen["changed"], chosen["changed"]


def test_sel1_an_unplaced_path_of_the_ticket_s_earlier_commit_does_not_refuse(project):
    project.commit("an earlier landing of the ticket", f"Task: {TICKET}", "Role: engineer",
                   files={"tools/own.sh": "#!/bin/sh\n"})
    _branch(project)
    chosen = select.scoped(project.root, TICKET, change=sorted(OWN))
    assert "tools/own.sh" not in chosen["changed"], chosen["changed"]


def test_sel1_an_empty_change_counts_nothing_of_the_base(project):
    _base(project, {LONELY: "VALUE = 2  # moved on the base\n"})
    chosen = select.scoped(project.root, TICKET, change=[])
    assert chosen["changed"] == [], chosen["changed"]
    assert "tests/unit/test_lonely.py" not in chosen["suites"], chosen["suites"]


def test_sel1_without_change_the_green_range_is_still_counted(project):
    # a guard: gov close passes no change; its model (everything since the green record) stays
    _base(project, {LONELY: "VALUE = 2  # moved on the base\n"})
    chosen = select.scoped(project.root, TICKET)
    assert LONELY in chosen["changed"] and "tests/unit/test_lonely.py" in chosen["suites"], chosen


# -- SEL-3: unplaced named, with the line to add ----------------------------------------------------------------------

def test_sel3_unplaced_is_an_empty_list_when_every_path_is_placed(project):
    _branch(project)
    chosen = select.scoped(project.root, TICKET, change=sorted(OWN))
    assert "unplaced" in chosen, sorted(chosen)
    assert chosen["unplaced"] == [], chosen["unplaced"]


def test_sel3_a_path_nothing_places_is_named_with_the_line_to_add(project):
    _branch(project, {**OWN, "tools/new_script.sh": "#!/bin/sh\n"})
    change = sorted([*OWN, "tools/new_script.sh"])
    try:
        chosen = select.scoped(project.root, TICKET, change=change)
    except select.SelectionRefused as refusal:     # the refusal is the landing's; the object may also carry it
        said = refusal.reason
        assert "tools/new_script.sh" in said, said
        assert MAP in said and "coupling" in said.lower(), f"no line to add: {said}"
    else:
        assert chosen["unplaced"] == ["tools/new_script.sh"], chosen["unplaced"]


def test_sel3_a_record_document_is_placed_with_its_notice_and_unplaced_stays_empty(project):
    _branch(project, {**OWN, "proposals/note.md": "# a note\n"})   # outside the map's record_only (docs/**.md)
    chosen = select.scoped(project.root, TICKET, change=sorted([*OWN, "proposals/note.md"]))
    assert chosen["unplaced"] == [], chosen["unplaced"]
    assert "RECORD_PLACED proposals/note.md" in chosen["notices"], chosen["notices"]


def test_sel3_without_change_the_base_s_unplaced_path_is_still_refused(project):
    # a guard: gov close's refusal stays
    _base(project, {SCRIPT: "#!/bin/sh\n"})
    with pytest.raises(select.SelectionRefused) as raised:
        select.scoped(project.root, TICKET)
    assert SCRIPT in raised.value.reason
