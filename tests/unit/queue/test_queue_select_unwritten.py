"""``select.scoped`` with ``change`` counts ``change`` alone (SEL-1, plan item 1-0, DEC-1244 X-1; ``.tickets/
DAEO-j9z6.md`` "Fix: a trustworthy impact selection"): a path the base added since the green record, or the ticket's
own earlier commit wrote, is neither counted nor refused nor listed (``unplaced_base`` stays, empty); a path ``change``
names that nothing places is refused naming only itself; without ``change`` nothing changes (W2-115b's fix, L2-4,
"Fix: the queue's selection refuses only the landing's own unplaced paths", rewritten by SEL-1).

The planted project is ``queue_support``'s, its test map placing the green record's folder (``docs/close/**``) as a
record so that ``unplaced_base`` can be compared whole. "Base-side" is a commit after the green record with no
``Task:`` trailer of the ticket's (none, or another ticket's), as the integration branch's direct commits are.
"""
from __future__ import annotations

import json
import os
import site

import pytest
import yaml

from gov.close import select

from queue_support import OTHER, TICKET, WBS, map_text, plant

DOC = "proposals/plan.md"            # a document outside record_only (which holds docs/**.md and .tickets/**.md)
SCRIPT = "repin.sh"                  # a shell script nothing places
OWN = {"src/pkg/feature.py": "def twice(x):\n    return 2 * x\n"}   # mapped code: the ticket's own suite holds it
OWN_SUITE = f"tests/acceptance/{WBS}/"


def _map(couplings=()):
    data = yaml.safe_load(map_text())
    data["record_only"] = list(data["record_only"]) + ["docs/close/**"]
    data["couplings"] = list(couplings)
    return yaml.safe_dump(data, sort_keys=False)


@pytest.fixture
def make(tmp_path, monkeypatch):
    """``make(couplings=())``: a planted project (as the folder's ``project`` fixture) whose map holds ``couplings``."""
    monkeypatch.setenv("PYTHONUSERBASE", site.getuserbase())
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", os.devnull)
    monkeypatch.delenv("GOV_ROLE", raising=False)
    return lambda couplings=(): plant(tmp_path, extra={"governance/project/test-map.yaml": _map(couplings)})


def _night(project) -> str:
    """A green nightly record naming the head as it is now, committed by no ticket: the green base."""
    head = project.sha()
    project.commit("a green night", "Role: orchestrator",
                   files={f"docs/close/nightly/NR-20261101T010000Z-{head[:12]}.json":
                          json.dumps({"verdict": "green", "head": head}) + "\n"})
    return head


def _base_side(project, files: dict, *trailers: str) -> None:
    """A direct commit on the base after the green record: no ``Task:`` of the ticket's."""
    project.commit("a direct commit", *(trailers or ("Role: orchestrator",)), files=files)


def _own(project, files: dict | None = None) -> None:
    project.commit("the ticket's work", f"Task: {TICKET}", "Role: engineer", files=files or OWN)


def _refused(project, **keys) -> str:
    with pytest.raises(select.SelectionRefused) as raised:
        select.scoped(project.root, TICKET, **keys)
    return raised.value.reason


# -- with change: the base's paths are not counted --------------------------------------------------------------------

def test_with_change_the_base_s_unplaced_paths_are_not_counted_and_unplaced_base_is_empty(make):
    project = make()
    _night(project)
    _base_side(project, {DOC: "# a plan\n"})
    _base_side(project, {SCRIPT: "#!/bin/sh\necho repin\n"})
    _own(project)
    chosen = select.scoped(project.root, TICKET, change=sorted(OWN))
    assert chosen.get("unplaced_base") == [], chosen.get("unplaced_base")
    assert DOC not in chosen["changed"] and SCRIPT not in chosen["changed"], chosen["changed"]
    assert OWN_SUITE in chosen["suites"], chosen["suites"]


def test_with_change_given_as_an_empty_list_the_base_s_paths_are_not_counted_either(make):
    project = make()
    _night(project)
    _base_side(project, {DOC: "# a plan\n"})
    _base_side(project, {SCRIPT: "#!/bin/sh\necho repin\n"})
    _own(project)
    chosen = select.scoped(project.root, TICKET, change=[])
    assert chosen.get("unplaced_base") == [], chosen.get("unplaced_base")
    assert chosen["changed"] == [], chosen["changed"]


def test_unplaced_base_is_an_empty_list_when_the_base_holds_none(make):
    project = make()
    _night(project)
    _own(project)
    chosen = select.scoped(project.root, TICKET, change=sorted(OWN))
    assert "unplaced_base" in chosen, sorted(chosen)
    assert chosen["unplaced_base"] == []


def test_another_ticket_s_commit_on_the_base_is_not_counted_either(make):
    project = make()
    _night(project)
    _base_side(project, {DOC: "# a plan\n"}, f"Task: {OTHER}", "Role: engineer")
    _own(project)
    chosen = select.scoped(project.root, TICKET, change=sorted(OWN))
    assert chosen.get("unplaced_base") == [], chosen.get("unplaced_base")
    assert DOC not in chosen["changed"], chosen["changed"]


def test_a_base_side_path_a_test_imports_is_not_counted_so_that_test_is_not_selected(make):
    project = make()
    _night(project)
    _base_side(project, {"src/pkg/lonely.py": "VALUE = 1  # moved on the base\n", DOC: "# a plan\n"})
    _own(project)
    chosen = select.scoped(project.root, TICKET, change=sorted(OWN))
    assert "tests/unit/test_lonely.py" not in chosen["suites"], chosen["suites"]
    assert chosen.get("unplaced_base") == [], chosen.get("unplaced_base")


def test_a_base_side_path_a_coupling_holds_is_not_counted_so_its_suite_is_not_selected(make):
    project = make([{"paths": ["scripts/**"], "suites": ["tests/unit/test_other.py"], "why": "the deploy script"}])
    _night(project)
    _base_side(project, {"scripts/deploy.sh": "#!/bin/sh\n", DOC: "# a plan\n"})
    _own(project)
    chosen = select.scoped(project.root, TICKET, change=sorted(OWN))
    assert "tests/unit/test_other.py" not in chosen["suites"], chosen["suites"]
    assert chosen.get("unplaced_base") == [], chosen.get("unplaced_base")


# -- the change's own unplaced paths are refused, naming only them ---------------------------------------------------

def test_a_ticket_s_own_earlier_commit_s_unplaced_path_is_not_counted_so_not_refused(make):
    project = make()
    _night(project)
    _base_side(project, {DOC: "# a plan\n"})
    _own(project, {**OWN, "tools/own.sh": "#!/bin/sh\n"})
    chosen = select.scoped(project.root, TICKET, change=sorted(OWN))   # change does not name it: not this landing's
    assert "tools/own.sh" not in chosen["changed"], chosen["changed"]
    assert DOC not in chosen["changed"], chosen["changed"]


def test_a_path_change_names_that_nothing_places_is_refused_naming_it_and_not_the_base_s(make):
    project = make()
    _night(project)
    _base_side(project, {DOC: "# a plan\n", SCRIPT: "#!/bin/sh\n"})
    project.commit("a slip on the branch", "Role: engineer", files={"tools/slip.sh": "#!/bin/sh\n"})
    _own(project)
    reason = _refused(project, change=sorted([*OWN, "tools/slip.sh"]))
    assert "tools/slip.sh" in reason
    assert DOC not in reason and SCRIPT not in reason, f"the refusal names the base's paths: {reason}"


# -- without change: nothing changes (gov close) ---------------------------------------------------------------------

def test_without_change_the_base_s_unplaced_path_is_still_refused(make):
    project = make()
    _night(project)
    _base_side(project, {DOC: "# a plan\n"})
    _base_side(project, {SCRIPT: "#!/bin/sh\necho repin\n"})
    _own(project)
    reason = _refused(project)
    assert DOC in reason and SCRIPT in reason
