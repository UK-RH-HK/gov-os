"""W2-191 S2: the regression run's line names the selected targets outside ``tests/``, so that pytest collects them."""
from __future__ import annotations

from pathlib import Path

from gov.close.command import _scope_form

ROOT = Path("/p")
OWN = "tests/acceptance/W1-own/"


def _scope(*selected: str, scope: str = "scoped", ignore=(OWN,), deselect=()) -> dict:
    return {"scope": scope, "selected": [{"target": t, "why": [{"reason": "X"}]} for t in selected],
            "ignore": list(ignore), "deselect": list(deselect)}


def test_a_tests_only_scope_gives_the_list_it_gave_before():
    scope = _scope("tests/unit", "tests/acceptance/W1-cc/", "tests/unit/test_u.py::test_u",
                   ignore=[OWN, "tests/acceptance/W1-zz/"],
                   deselect=["tests/acceptance/W1-rr/test_rr.py::test_other"])
    assert _scope_form(ROOT, scope, ROOT / OWN) == [
        "--ignore=/p/tests/acceptance/W1-zz",
        "--deselect=tests/acceptance/W1-rr/test_rr.py::test_other",
        "--deselect=acceptance/W1-rr/test_rr.py::test_other"]


def test_without_an_ignore_the_acceptance_run_gets_no_form():
    assert _scope_form(ROOT, _scope("governance/scripts/tests"), None) == []


def test_an_outside_folder_file_and_node_id_are_collected_where_they_lie():
    scope = _scope("tests/unit", "governance/scripts/tests", "product/tests/test_a.py",
                   "product/tests/test_x.py::TestC::test_m[a-b]")
    form = _scope_form(ROOT, scope, ROOT / OWN)
    assert form == ["/p/governance/scripts/tests", "/p/product/tests/test_a.py",
                    "/p/product/tests/test_x.py::TestC::test_m[a-b]"]


def test_the_options_come_first_then_the_outside_targets_in_the_order_selected():
    scope = _scope("product/tests/test_a.py", "governance/scripts/tests/", ignore=[OWN, "tests/unit/"],
                   deselect=["tests/acceptance/W1-rr/test_rr.py::test_other"])
    form = _scope_form(ROOT, scope, ROOT / OWN)
    assert form == ["--ignore=/p/tests/unit", "--deselect=tests/acceptance/W1-rr/test_rr.py::test_other",
                    "--deselect=acceptance/W1-rr/test_rr.py::test_other", "/p/product/tests/test_a.py",
                    "/p/governance/scripts/tests/"]


def test_the_reused_form_collects_its_outside_record_reading_targets():
    scope = _scope("product/tests/test_a.py::test_a", scope="reused", ignore=[OWN, "tests/unit/"])
    assert _scope_form(ROOT, scope, ROOT / OWN) == ["--ignore=/p/tests/unit", "/p/product/tests/test_a.py::test_a"]


def test_a_target_the_run_ignores_is_not_collected_twice():
    """The ticket's own suite, ignored by the regression run (the acceptance run holds it), stays out of it even
    where its folder lies outside ``tests/``."""
    scope = _scope("checks/", "governance/scripts/tests", ignore=["checks/"])
    assert _scope_form(ROOT, scope, ROOT / "checks") == ["/p/governance/scripts/tests"]


def test_the_full_scope_names_nothing_beyond_tests():
    scope = _scope("tests", ignore=[OWN], scope="full")
    assert _scope_form(ROOT, scope, ROOT / OWN) == []


def test_a_folder_named_like_tests_but_elsewhere_is_outside():
    scope = _scope("tests_extra/test_a.py", "testsuite", "tests")
    assert _scope_form(ROOT, scope, ROOT / OWN) == ["/p/tests_extra/test_a.py", "/p/testsuite"]
