"""W2-191 S2 and F1: gov close's selection resolves a target outside ``tests/`` as it resolves one under it."""
from __future__ import annotations

import pytest

from gov.close import batch, select

from . import test_w2_191_support as support
from .test_w2_191_support import OUTSIDE_CASE, OUTSIDE_SUITE, targets

TASK = ("Task: P-W1-own", "Role: engineer")


def _work(repo, files: dict) -> None:
    repo.commit("work", *TASK, files=files)


# --- the scoped close's plan (select.plan) ---------------------------------------

def test_s2_a_change_a_coupling_maps_to_an_outside_suite_selects_that_folder(repo):
    support.project(repo)
    _work(repo, {"governance/scripts/tool.py": "T = 2\n"})
    plan = select.plan(repo.root, "W1-own", ticket="P-W1-own")
    assert plan["scope"] == "scoped" and plan["why_full"] == []
    found = targets(plan)
    assert found[OUTSIDE_SUITE] == ["COUPLING"]
    assert found[OUTSIDE_CASE] == ["RECORD_READING"]  # record_reading joins every selection
    assert found["tests/acceptance/W1-own/"] == ["OWN"] and found["tests/unit"] == ["UNIT"]
    assert "governance/scripts/tests/test_tool.py" not in found  # every_close: no record in this change
    coupling = next(e for e in plan["selected"] if e["target"] == OUTSIDE_SUITE)["why"][0]
    assert coupling["paths"] == ["governance/scripts/tool.py"]


def test_s2_a_record_only_change_runs_the_record_reading_and_every_close_targets_outside_tests(repo):
    support.project(repo)
    _work(repo, {"docs/notes.md": "# notes, more\n"})
    plan = select.plan(repo.root, "W1-own", ticket="P-W1-own")
    assert plan["scope"] == "scoped"
    found = targets(plan)
    assert found[OUTSIDE_CASE] == ["RECORD_READING"]
    assert found["governance/scripts/tests/test_tool.py"] == ["EVERY_CLOSE"]
    assert OUTSIDE_SUITE not in found  # no coupling path in the change


def test_s2_an_outside_target_is_left_out_of_tests_only_forms(repo):
    """The regression run is ``pytest tests``: an outside target is neither ignored nor deselected by the form (the
    run line collects it, ``command._scope_form``); the acceptance suites no target reaches are still left out."""
    support.project(repo)
    repo.commit("more", files={"tests/acceptance/W1-zz/test_zz.py": "def test_zz():\n    pass\n"})
    support.green(repo, "NR-2")
    _work(repo, {"governance/scripts/tool.py": "T = 2\n"})
    plan = select.plan(repo.root, "W1-own", ticket="P-W1-own")
    assert plan["ignore"] == ["tests/acceptance/W1-own/", "tests/acceptance/W1-zz/"]
    assert plan["deselect"] == []
    assert [e["target"] for e in plan["left_out"]] == ["tests/acceptance/W1-zz/"]


def test_f1_an_outside_target_that_names_nothing_widens_to_the_full_run_with_the_reason(repo):
    gone = {"paths": ["governance/scripts/**"], "suites": ["governance/scripts/gone"], "why": "never there"}
    support.project(repo, support.map_data(couplings=[gone]))
    _work(repo, {"governance/scripts/tool.py": "T = 2\n"})
    plan = select.plan(repo.root, "W1-own", ticket="P-W1-own")
    assert plan["scope"] == "full"
    assert plan["why_full"] == [{"reason": "UNRESOLVED_TARGET", "target": "governance/scripts/gone",
                                 "detail": "FILE_GONE"}]


def test_f1_an_outside_case_that_names_nothing_widens_with_case_gone(repo):
    support.project(repo, support.map_data(record_reading=["product/tests/test_a.py::test_gone"]))
    _work(repo, {"src/own/y.py": "y = 2\n"})
    plan = select.plan(repo.root, "W1-own", ticket="P-W1-own")
    assert plan["scope"] == "full"
    assert plan["why_full"] == [{"reason": "UNRESOLVED_TARGET", "target": "product/tests/test_a.py::test_gone",
                                 "detail": "CASE_GONE"}]


def test_f1_a_project_with_tests_targets_alone_selects_as_it_did(repo):
    """The selection of a ``tests/``-only map does not depend on this ticket: the schema planted is the new one."""
    data = {"version": 1, "shared_core": ["src/core/**"], "record_only": [".tickets/**.md", "docs/**.md"],
            "record_reading": ["tests/unit/test_u.py::test_u"], "every_close": [],
            "couplings": [{"paths": ["product/**"], "suites": ["tests/acceptance/W1-own/"], "why": "w"}]}
    support.project(repo, data)
    _work(repo, {"product/app.py": "A = 2\n"})
    plan = select.plan(repo.root, "W1-own", ticket="P-W1-own")
    assert plan["scope"] == "scoped"
    assert targets(plan) == {"tests/acceptance/W1-own/": ["OWN", "COUPLING"], "tests/unit": ["UNIT"],
                             "tests/unit/test_u.py::test_u": ["RECORD_READING"]}
    assert plan["ignore"] == ["tests/acceptance/W1-own/"] and plan["deselect"] == []


# --- the strict-by-ticket selection (select.scoped) ------------------------------

def test_s2_scoped_names_the_outside_suite_a_coupling_maps_the_change_to(repo):
    support.project(repo)
    _work(repo, {"governance/scripts/tool.py": "T = 2\n"})
    chosen = select.scoped(repo.root, "P-W1-own")
    assert OUTSIDE_SUITE in chosen["suites"] and OUTSIDE_CASE in chosen["suites"]
    assert chosen["why"][OUTSIDE_SUITE] == ["COUPLING governance/scripts/tool.py"]
    assert OUTSIDE_CASE not in chosen["suites"]  # record_reading needs a record in the change


def test_s2_scoped_with_records_alone_runs_the_outside_record_reading_target(repo):
    support.project(repo)
    _work(repo, {"docs/notes.md": "# notes, more\n"})
    chosen = select.scoped(repo.root, "P-W1-own")
    assert chosen["records_only"] is True
    assert chosen["suites"] == [OUTSIDE_CASE]  # nothing else: not even the own suite


def test_s2_scoped_with_records_and_code_adds_every_close_outside_tests(repo):
    support.project(repo)
    _work(repo, {"docs/notes.md": "# notes, more\n", "governance/scripts/tool.py": "T = 2\n"})
    chosen = select.scoped(repo.root, "P-W1-own")
    assert set(chosen["suites"]) == {OUTSIDE_SUITE, OUTSIDE_CASE, "tests/acceptance/W1-own/"}  # test_tool.py folded
    assert chosen["why"][OUTSIDE_CASE] == ["RECORD_READING"]


def test_s2_scoped_folds_an_outside_case_into_the_outside_folder_that_holds_it(repo):
    test_map = support.map_data(record_reading=["governance/scripts/tests/test_tool.py::test_t"])
    support.project(repo, test_map)
    _work(repo, {"docs/notes.md": "# more\n", "governance/scripts/tool.py": "T = 2\n"})
    chosen = select.scoped(repo.root, "P-W1-own")
    assert OUTSIDE_SUITE in chosen["suites"]
    assert not [s for s in chosen["suites"] if s.startswith("governance/scripts/tests/")], chosen["suites"]


def test_f1_scoped_refuses_an_outside_target_that_names_nothing(repo):
    gone = {"paths": ["governance/scripts/**"], "suites": ["governance/scripts/gone/"], "why": "never there"}
    support.project(repo, support.map_data(couplings=[gone]))
    _work(repo, {"governance/scripts/tool.py": "T = 2\n"})
    with pytest.raises(select.SelectionRefused) as refused:
        select.scoped(repo.root, "P-W1-own")
    assert "governance/scripts/gone/ (FILE_GONE)" in refused.value.reason


def test_f1_scoped_refuses_a_map_with_an_escaping_target_as_unreadable(repo):
    support.project(repo, support.map_data(record_reading=["../outside/test_o.py"]), schema=support.schema_file(None))
    _work(repo, {"docs/notes.md": "# more\n"})
    with pytest.raises(select.SelectionRefused) as refused:
        select.scoped(repo.root, "P-W1-own")
    assert "TEST_MAP_UNREADABLE" in refused.value.reason


def test_f1_plan_goes_full_on_a_map_with_an_escaping_target(repo):
    support.project(repo, support.map_data(couplings=[
        {"paths": ["governance/scripts/**"], "suites": ["/etc"], "why": "w"}]), schema=support.schema_file(None))
    _work(repo, {"governance/scripts/tool.py": "T = 2\n"})
    plan = select.plan(repo.root, "W1-own", ticket="P-W1-own")
    assert plan["scope"] == "full" and [w["reason"] for w in plan["why_full"]] == ["TEST_MAP_UNREADABLE"]


# --- the reusing close's form (batch.reused_form) --------------------------------

def test_s2_the_reused_form_names_the_outside_record_reading_targets(repo):
    support.project(repo)
    plan = {"scope": "scoped", "why_full": [], "head": "h"}
    form = batch.reused_form(repo.root, "tests/acceptance/W1-own/", plan)
    assert form["scope"] == "reused"
    assert [e["target"] for e in form["selected"]] == [OUTSIDE_CASE]
    assert form["selected"][0]["why"] == [{"reason": "RECORD_READING"}]
    assert "tests/unit/" in form["ignore"] and "tests/acceptance/W1-own/" in form["ignore"]
    assert not [i for i in form["ignore"] if i.startswith(("product", "governance"))]
    assert form["deselect"] == []


def test_f1_the_reused_form_of_a_tests_only_map_is_unchanged(repo):
    data = {"version": 1, "shared_core": ["src/core/**"], "record_reading": ["tests/unit/test_u.py::test_u"],
            "every_close": [], "couplings": []}
    support.project(repo, data)
    form = batch.reused_form(repo.root, "tests/acceptance/W1-own/", {"scope": "scoped", "why_full": [], "head": "h"})
    assert [e["target"] for e in form["selected"]] == ["tests/unit/test_u.py::test_u"]
    assert form["ignore"] == ["tests/acceptance/W1-own/"] and form["deselect"] == []
