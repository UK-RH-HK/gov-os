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
    assert found["governance/scripts/tests/test_tool.py"] == ["EVERY_CLOSE"]  # the green night's record is in it
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
    data = {"version": 1, "shared_core": ["src/core/**"], "record_only": [".tickets/**.md", "docs/**.md",
                                                                  "docs/close/nightly/*.json"],
            "record_reading": ["tests/unit/test_u.py::test_u"], "every_close": [],
            "couplings": [{"paths": ["product/**"], "suites": ["tests/acceptance/W1-own/"], "why": "w"}]}
    support.project(repo, data)
    _work(repo, {"product/app.py": "A = 2\n"})
    plan = select.plan(repo.root, "W1-own", ticket="P-W1-own")
    assert plan["scope"] == "scoped"
    assert targets(plan) == {"tests/acceptance/W1-own/": ["OWN", "COUPLING"], "tests/unit": ["UNIT"],
                             "tests/unit/test_u.py::test_u": ["RECORD_READING"]}
    assert plan["ignore"] == ["tests/acceptance/W1-own/"] and plan["deselect"] == []


# --- F2: the full plan names the map's outside targets --------------------------------

COUPLING_WHY = "the scripts' suite lives beside them"
FULL_OUTSIDE = {"tests/acceptance/W1-own/": ["OWN"], "tests": ["FULL"],
                OUTSIDE_CASE: ["RECORD_READING"], "governance/scripts/tests/test_tool.py": ["EVERY_CLOSE"],
                OUTSIDE_SUITE: ["COUPLING"]}


def _full_why(plan: dict, target: str) -> list[dict]:
    return next(e for e in plan["selected"] if e["target"] == target)["why"]


def test_f2_a_first_close_without_a_base_names_every_outside_target_beside_tests(repo):
    repo.commit("base", files=support.files())  # no green record: BASE_UNKNOWN
    plan = select.plan(repo.root, "W1-own", ticket="P-W1-own")
    assert plan["scope"] == "full" and [w["reason"] for w in plan["why_full"]] == ["BASE_UNKNOWN"]
    assert targets(plan) == FULL_OUTSIDE
    assert _full_why(plan, OUTSIDE_CASE) == [{"reason": "RECORD_READING"}]
    assert _full_why(plan, "governance/scripts/tests/test_tool.py") == [{"reason": "EVERY_CLOSE"}]
    assert _full_why(plan, OUTSIDE_SUITE) == [{"reason": "COUPLING", "coupling": COUPLING_WHY}]
    assert plan["left_out"] == [] and plan["ignore"] == ["tests/acceptance/W1-own/"] and plan["deselect"] == []


def test_f2_the_own_suite_and_tests_come_first_as_before(repo):
    repo.commit("base", files=support.files())
    plan = select.plan(repo.root, "W1-own", ticket="P-W1-own")
    assert [e["target"] for e in plan["selected"]][:2] == ["tests/acceptance/W1-own/", "tests"]


def test_f2_every_coupling_is_named_whatever_the_change(repo):
    """The change here touches no coupling's path: the full plan still holds each coupling's suites."""
    second = {"paths": ["product/**"], "suites": ["product/tests/test_c.py", OUTSIDE_SUITE], "why": "the product"}
    support.project(repo, support.map_data(couplings=support.map_data()["couplings"] + [second]))
    _work(repo, {"src/core/z.py": "z = 2\n"})  # a shared-core change: full
    plan = select.plan(repo.root, "W1-own", ticket="P-W1-own")
    assert plan["scope"] == "full" and [w["reason"] for w in plan["why_full"]] == ["SHARED_CORE"]
    found = targets(plan)
    assert found["product/tests/test_c.py"] == ["COUPLING"]
    assert found[OUTSIDE_SUITE] == ["COUPLING", "COUPLING"]  # named by two couplings: one entry, both reasons
    assert _full_why(plan, OUTSIDE_SUITE) == [{"reason": "COUPLING", "coupling": COUPLING_WHY},
                                              {"reason": "COUPLING", "coupling": "the product"}]


@pytest.mark.parametrize("change,reason", [({"src/core/z.py": "z = 2\n"}, "SHARED_CORE"),
                                           ({"product/app.py": "A = 2\n"}, "UNPLACED")])
def test_f2_a_shared_core_or_unplaced_change_names_them_too(repo, change, reason):
    support.project(repo, support.map_data(couplings=[
        {"paths": ["governance/scripts/**"], "suites": [OUTSIDE_SUITE], "why": "w"}]))
    _work(repo, change)
    plan = select.plan(repo.root, "W1-own", ticket="P-W1-own")
    assert plan["scope"] == "full" and reason in [w["reason"] for w in plan["why_full"]]
    assert targets(plan)[OUTSIDE_SUITE] == ["COUPLING"] and targets(plan)[OUTSIDE_CASE] == ["RECORD_READING"]


def test_f2_a_full_asked_plan_names_them(repo):
    support.project(repo)
    _work(repo, {"governance/scripts/tool.py": "T = 2\n"})
    plan = select.plan(repo.root, "W1-own", full_asked=True, ticket="P-W1-own")
    assert plan["scope"] == "full" and [w["reason"] for w in plan["why_full"]] == ["FULL_ASKED"]
    assert targets(plan) == FULL_OUTSIDE


def test_f2_an_outside_target_the_head_does_not_hold_is_left_out_with_its_reason(repo):
    gone = {"paths": ["nothing/**"], "suites": ["governance/scripts/gone", "product/tests/test_a.py::test_gone"],
            "why": "never there"}
    support.project(repo, support.map_data(couplings=support.map_data()["couplings"] + [gone]))
    _work(repo, {"src/core/z.py": "z = 2\n"})
    plan = select.plan(repo.root, "W1-own", ticket="P-W1-own")
    assert plan["scope"] == "full"
    assert "governance/scripts/gone" not in targets(plan) and "product/tests/test_a.py::test_gone" not in targets(plan)
    assert plan["left_out"] == [
        {"target": "governance/scripts/gone", "why": [{"reason": "UNRESOLVED_TARGET", "detail": "FILE_GONE"}]},
        {"target": "product/tests/test_a.py::test_gone",
         "why": [{"reason": "UNRESOLVED_TARGET", "detail": "CASE_GONE"}]}]
    # why_full names only the changed couplings', every-close and record-reading targets: here none of them
    assert [w["reason"] for w in plan["why_full"]] == ["SHARED_CORE"]
    assert targets(plan)[OUTSIDE_SUITE] == ["COUPLING"]  # the ones the head holds are still named


def test_f2_an_unresolved_target_keeps_its_why_full_entry_and_is_also_left_out(repo):
    support.project(repo, support.map_data(record_reading=["product/tests/test_a.py::test_gone"]))
    _work(repo, {"src/own/y.py": "y = 2\n"})
    plan = select.plan(repo.root, "W1-own", ticket="P-W1-own")
    assert plan["why_full"] == [{"reason": "UNRESOLVED_TARGET", "target": "product/tests/test_a.py::test_gone",
                                 "detail": "CASE_GONE"}]
    assert plan["left_out"] == [{"target": "product/tests/test_a.py::test_gone",
                                 "why": [{"reason": "UNRESOLVED_TARGET", "detail": "CASE_GONE"}]}]
    assert "product/tests/test_a.py::test_gone" not in targets(plan)


@pytest.mark.parametrize("breaking", ["missing", "unreadable"])
def test_f2_an_unreadable_or_missing_map_gives_today_s_full_plan(repo, breaking):
    files = support.files()
    if breaking == "missing":
        del files[select.MAP_REL]
    else:
        files[select.MAP_REL] = "version: 1\ncouplings: not-a-list\n"
    repo.commit("base", files=files)
    plan = select.plan(repo.root, "W1-own", ticket="P-W1-own")
    assert plan["scope"] == "full"
    assert targets(plan) == {"tests/acceptance/W1-own/": ["OWN"], "tests": ["FULL"]}
    assert plan["left_out"] == []


def test_f2_a_map_whose_targets_are_all_under_tests_gives_today_s_full_plan(repo):
    data = {"version": 1, "shared_core": ["src/core/**"], "record_reading": ["tests/unit/test_u.py::test_u"],
            "every_close": ["tests/unit"],
            "couplings": [{"paths": ["product/**"], "suites": ["tests/acceptance/W1-own/", "tests/unit"], "why": "w"}]}
    repo.commit("base", files=support.files(data))
    plan = select.plan(repo.root, "W1-own", ticket="P-W1-own")
    assert plan["scope"] == "full"
    assert targets(plan) == {"tests/acceptance/W1-own/": ["OWN"], "tests": ["FULL"]}
    assert plan["left_out"] == []


def test_f2_the_full_plan_s_outside_targets_reach_the_regression_run_line(repo):
    from gov.close.command import _scope_form

    repo.commit("base", files=support.files())
    plan = select.plan(repo.root, "W1-own", ticket="P-W1-own")
    root = repo.root
    form = _scope_form(root, plan, root / "tests/acceptance/W1-own")
    # record_reading, every_close, then the couplings' suites, each as a positional target of its own
    assert form == [str(root / OUTSIDE_CASE.partition("::")[0]) + "::test_a",
                    str(root / "governance/scripts/tests/test_tool.py"), str(root / OUTSIDE_SUITE)]


# --- the strict-by-ticket selection (select.scoped) ------------------------------

def test_s2_scoped_names_the_outside_suite_a_coupling_maps_the_change_to(repo):
    support.project(repo)
    _work(repo, {"governance/scripts/tool.py": "T = 2\n"})
    chosen = select.scoped(repo.root, "P-W1-own")
    assert OUTSIDE_SUITE in chosen["suites"] and OUTSIDE_CASE in chosen["suites"]
    assert chosen["why"][OUTSIDE_SUITE] == ["COUPLING governance/scripts/tool.py"]
    # the green night's record is in the change: record_reading joins, and every_close (a code path is too), whose
    # file the outside folder holds
    assert chosen["why"][OUTSIDE_CASE] == ["RECORD_READING"]
    assert "governance/scripts/tests/test_tool.py" not in chosen["suites"]


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
