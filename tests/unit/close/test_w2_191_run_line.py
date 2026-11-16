"""W2-191 S2: the regression run's line names the selected targets outside ``tests/``, so that pytest collects them."""
from __future__ import annotations

from pathlib import Path

from gov.close.command import _scope_form

from . import test_w2_191_support as support

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
                    "/p/governance/scripts/tests"]


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


# --- the run itself ---------------------------------------------------------------

def test_the_regression_run_collects_a_selected_outside_suite_and_nothing_it_leaves_out(tmp_path):
    """A real pytest run of the form: the selected outside folder runs whole, the selected node id of another
    outside file runs that case alone, and an outside file nothing selects stays out."""
    from functools import partial

    from gov.close import command

    files = {"tests/unit/test_u.py": "def test_u():\n    pass\n",
             "governance/scripts/tests/test_s.py": "def test_s1():\n    pass\n\n\ndef test_s2():\n    pass\n",
             "product/tests/test_a.py": "def test_a():\n    pass\n\n\ndef test_b():\n    assert False\n",
             "product/tests/test_left_out.py": "def test_left():\n    assert False\n"}
    for rel, text in files.items():
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / rel).write_text(text, encoding="utf-8")
    support.plant_runner(tmp_path)
    (tmp_path / "tests/acceptance/W1-own").mkdir(parents=True)
    (tmp_path / ".gov-runtime/j").mkdir(parents=True)
    scope = {"scope": "scoped", "selected": [{"target": "tests/unit", "why": []},
                                             {"target": "governance/scripts/tests", "why": []},
                                             {"target": "product/tests/test_a.py::test_a", "why": []}],
             "ignore": ["tests/acceptance/W1-own/"], "deselect": [], "check_result": None, "limit": [],
             "folder": ".gov-runtime/j", "junit_xml": [], "runs": [], "per_test_timeout": 60,
             "tmp_path_retention_policy": "failed", "distribution": "load"}
    stated: list = []
    findings, counts = partial(command._run_tests, workers=1)(
        tmp_path, tmp_path / "tests", 180, ignore=tmp_path / "tests/acceptance/W1-own", none_collected_ok=True,
        stated=stated, scope=scope)
    assert findings == [] and counts["passed"] == 4 and counts["failed"] == 0, (findings, counts)


# --- F1: a project with no tests/ folder ----------------------------------------------

def _project_without_tests(tmp_path, suite_text: str) -> Path:
    """No ``tests/`` folder: the suite lives in ``governance/scripts/tests``; a ticket's own suite is not there."""
    (tmp_path / "governance/scripts/tests").mkdir(parents=True)
    (tmp_path / "governance/scripts/tests/test_f.py").write_text(suite_text, encoding="utf-8")
    support.plant_runner(tmp_path)
    (tmp_path / ".gov-runtime/j").mkdir(parents=True)
    return tmp_path


def _scope_of(*selected: str, ignore=(OWN,)) -> dict:
    return {"scope": "scoped", "selected": [{"target": t, "why": [{"reason": "X"}]} for t in selected],
            "ignore": list(ignore), "deselect": [], "check_result": None, "limit": [], "folder": ".gov-runtime/j",
            "junit_xml": [], "runs": [], "per_test_timeout": 60, "tmp_path_retention_policy": "failed",
            "distribution": "load"}


def _regression(root: Path, scope: dict | None, stated: list):
    from gov.close import command

    return command._check_tests(root, root / "tests", 180, ignore=root / OWN, stated=stated, workers=1, scope=scope)


def test_f1_a_failing_outside_test_fails_the_close_where_the_project_has_no_tests_folder(tmp_path):
    import pytest

    from gov.close import command

    root = _project_without_tests(tmp_path, "def test_f():\n    assert False\n")
    stated: list = []
    with pytest.raises(command._Finding) as failed:
        _regression(root, _scope_of("governance/scripts/tests"), stated)
    assert failed.value.code == "CHECK_FAILED"
    assert failed.value.details["tests_run"]["failed"] >= 1
    assert stated and stated[0]["run"] == "regression" and stated[0]["failed"] >= 1


def test_f1_a_passing_outside_test_is_counted_where_the_project_has_no_tests_folder(tmp_path):
    root = _project_without_tests(tmp_path, "def test_f():\n    pass\n\n\ndef test_g():\n    pass\n")
    counts = _regression(root, _scope_of("governance/scripts/tests"), [])
    assert counts["passed"] == 2 and counts["failed"] == 0 and counts["errors"] == 0


def test_f1_one_outside_case_runs_alone_where_the_project_has_no_tests_folder(tmp_path):
    root = _project_without_tests(tmp_path, "def test_f():\n    pass\n\n\ndef test_g():\n    assert False\n")
    counts = _regression(root, _scope_of("governance/scripts/tests/test_f.py::test_f"), [])
    assert counts["passed"] == 1 and counts["failed"] == 0


def test_f1_without_an_outside_target_a_project_with_no_tests_folder_runs_nothing_as_before(tmp_path):
    root = _project_without_tests(tmp_path, "def test_f():\n    assert False\n")
    stated: list = []
    for scope in (None, _scope_of(), _scope_of("tests", "tests/unit"), _scope_of(OWN.rstrip("/"), ignore=[OWN])):
        assert _regression(root, scope, stated) == {"passed": 0, "failed": 0, "errors": 0, "skipped": 0}
    assert stated == []  # no pytest was started


def test_f1_the_run_line_of_a_project_with_no_tests_folder_names_only_the_outside_targets(tmp_path, monkeypatch):
    from gov.close import command

    root = _project_without_tests(tmp_path, "def test_f():\n    pass\n")
    (root / "product/tests").mkdir(parents=True)
    (root / "product/tests/test_a.py").write_text("def test_a():\n    pass\n", encoding="utf-8")
    lines: list = []

    def one(root_, cmd, env, timeout, what, rel):
        lines.append(cmd)
        return [], {"seconds": 0.0, "passed": 1, "failed": 0, "errors": 0, "skipped": 0}

    monkeypatch.setattr(command, "_one_test_run", one)
    scope = _scope_of("governance/scripts/tests", "product/tests/test_a.py::test_a", "tests/unit")
    scope["deselect"] = ["product/tests/test_a.py::test_other"]
    counts = _regression(root, scope, [])
    assert counts["passed"] >= 1 and len(lines) == 1
    line = lines[0]
    assert str(root / "tests") not in line  # no ``tests`` positional
    assert not any(arg.startswith("--ignore") and str(root / "tests/acceptance") in arg for arg in line)
    assert "--ignore" not in line  # nor the ``--ignore`` of the folder that is not there
    assert f"{root / 'governance/scripts/tests'}" in line and f"{root / 'product/tests/test_a.py'}::test_a" in line
    assert "--deselect=product/tests/test_a.py::test_other" in line  # the form's own options stay


def test_f1_with_a_tests_folder_the_run_line_is_as_before(tmp_path, monkeypatch):
    from gov.close import command

    root = _project_without_tests(tmp_path, "def test_f():\n    pass\n")
    (root / "tests/unit").mkdir(parents=True)
    (root / "tests/unit/test_u.py").write_text("def test_u():\n    pass\n", encoding="utf-8")
    lines: list = []
    monkeypatch.setattr(command, "_one_test_run", lambda r, cmd, env, t, w, rel: (lines.append(cmd) or [], {
        "seconds": 0.0, "passed": 1, "failed": 0, "errors": 0, "skipped": 0}))
    _regression(root, _scope_of("tests/unit", "governance/scripts/tests"), [])
    assert lines[0][lines[0].index("pytest") + 1] == str(root / "tests")
    assert ["--ignore", str(root / OWN)] == lines[0][lines[0].index("--ignore"):][:2]
