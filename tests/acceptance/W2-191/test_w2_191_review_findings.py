"""W2-191 S2 after the round-1 review (PR-DAEO-v6pf-r1): two blocking findings, each as described behaviour (DEC-136).

F1: a project with no ``tests/`` folder whose plan selects a target outside ``tests/`` holding a failing test: the strict
close's regression run (``command._check_tests(root, root / "tests", ..., ignore=<own suite>, scope=<the scope>)``) must
run that target, so the failure is counted and reported, never zero counts and no finding.

F2: a full-scope plan (``BASE_UNKNOWN``, ``SHARED_CORE``) with a readable map selects every map target outside
``tests/`` the head holds (each with its ``why``), lists the ones it does not hold in ``left_out``, and the close's run
line built from the plan collects them. A map whose targets are all under ``tests/``, and an unreadable or missing map,
give today's full plan.

The projects carry a project-local, relaxed copy of the test-map schema (``support.relaxed_schema_files``), so the cases
are judged on the run and the plan alone; how the fix starts pytest (folder, arguments) is not pinned.
"""
from gov.close import command, select

import w2_191_support as support

OWN = f"tests/acceptance/{support.WBS}/"
FAIL_FILE = "product/tests/test_fail.py"
FAIL_NODE = f"{FAIL_FILE}::test_bad"
FAIL = "def test_bad():\n    assert False\n"
ZERO = {"passed": 0, "failed": 0, "errors": 0, "skipped": 0}

CORE = "governance/scripts/core.cfg"
CHECKS = "checks/test_c.py"
GONE_CASE = f"{support.PRODUCT_FILE}::test_gone"
GONE_FILE = "checks/test_gone.py"
GONE_SUITE = "governance/gone/tests"
UNIT_RECORDS = "tests/unit/test_records.py::test_ok"
UNIT_DATA = "tests/unit/test_data_contract.py::test_ok"
SCRIPTS_CASES = [support.SCRIPTS_RECORDS_NODE, f"{support.SCRIPTS_SUITE}/test_scripts.py::test_scripts"]
CHECKS_CASE = "checks/test_c.py::test_ok"

def _gone(detail):
    return [{"reason": "UNRESOLVED_TARGET", "detail": detail}]


def _strict_run(project, plan):
    """The strict close's regression run, as the close calls it: ``(counts, finding)``, the finding None where the run
    raised none."""
    root = project.root
    scope = support.strict_scope(project, plan)
    try:
        return command._check_tests(root, root / "tests", 300, ignore=root / OWN, workers=1, scope=scope), None
    except command._Finding as found:
        return None, found


def test_f1_a_project_without_tests_runs_its_selected_outside_targets(tmp_path):
    """No ``tests/`` folder; the plan selects an outside target holding a failing test: the regression run runs it,
    counts the failure and raises ``CHECK_FAILED``. With no outside target selected the run stays as today: empty
    counts, no finding."""
    extra = {FAIL_FILE: FAIL, **support.relaxed_schema_files(), **support.child_pytest_files()}

    failing = support.plant_without_tests(tmp_path / "failing", support.map_data(record_reading=[FAIL_NODE]), extra)
    assert not (failing.root / "tests").exists()  # the premise: no tests/ at all
    failing.green_night()
    failing.work({"docs/notes.md": "# changed\n"})
    plan = select.plan(failing.root, support.WBS, ticket=support.TICKET)
    assert plan["scope"] == "scoped", plan["why_full"]
    assert "RECORD_READING" in support.targets_of(plan).get(FAIL_NODE, []), plan["selected"]  # the plan selects it

    counts, found = _strict_run(failing, plan)
    assert found is not None, (
        f"the strict close's regression run of a project without tests/ ran nothing of its selected outside target "
        f"{FAIL_NODE}, which holds a failing test: it returned counts {counts} and no finding")
    assert found.code == "CHECK_FAILED", (found.code, found.findings)
    assert found.findings, "the finding names nothing"
    assert found.details["tests_run"]["failed"] >= 1, found.details

    # no outside target selected and no tests/: as today, empty counts and no finding
    quiet = support.plant_without_tests(tmp_path / "quiet", support.map_data(), extra)
    quiet.green_night()
    quiet.work({"docs/notes.md": "# changed\n"})
    quiet_plan = select.plan(quiet.root, support.WBS, ticket=support.TICKET)
    assert quiet_plan["scope"] == "scoped", quiet_plan["why_full"]
    assert not [t for t in support.targets_of(quiet_plan) if not t.startswith("tests/")], quiet_plan["selected"]
    counts, found = _strict_run(quiet, quiet_plan)
    assert found is None, (found.code, found.findings)
    assert counts == ZERO, counts


def _full_project(tmp, test_map, how):
    """A planted project (its own suite is a real folder, so the plan's ``OWN`` entry is there) whose plan is full:
    ``BASE_UNKNOWN`` (no green record) or ``SHARED_CORE`` (a change to the map's shared core on a green base)."""
    project = support.plant(tmp, test_map, {f"{OWN}test_own.py": support.PASS, CORE: "core\n",
                                            **support.relaxed_schema_files()})
    if how == "SHARED_CORE":
        project.green_night()
        project.work({CORE: "core, changed\n"})
    plan = select.plan(project.root, support.WBS, ticket=support.TICKET)
    assert plan["scope"] == "full", plan
    assert how in [why["reason"] for why in plan["why_full"]], plan["why_full"]
    return project, plan


def _reasons(plan):
    return {target: sorted(set(reasons)) for target, reasons in support.targets_of(plan).items()}


def test_f2_a_full_plan_selects_the_maps_targets_outside_tests_and_the_close_runs_them(tmp_path):
    """A readable map naming record-reading, every-close and coupling targets outside ``tests/`` (some of them gone
    from the head): each full plan (``BASE_UNKNOWN``, ``SHARED_CORE``) selects those the head holds beside ``tests``
    and the own suite, lists the others in ``left_out``, and the run line collects the held ones. A map with
    ``tests/`` targets only, and an unreadable or missing map, give today's full plan."""
    test_map = support.map_data(
        shared_core=[CORE],
        record_reading=[support.PRODUCT_NODE, GONE_CASE],
        every_close=[CHECKS, GONE_FILE],
        couplings=[support.coupling([support.SCRIPTS_SUITE, GONE_SUITE])])
    expected = {OWN: ["OWN"], "tests": ["FULL"], support.PRODUCT_NODE: ["RECORD_READING"], CHECKS: ["EVERY_CLOSE"],
                support.SCRIPTS_SUITE: ["COUPLING"]}
    left_out = {GONE_CASE: _gone("CASE_GONE"), GONE_FILE: _gone("FILE_GONE"), GONE_SUITE: _gone("FILE_GONE")}

    for how in ("BASE_UNKNOWN", "SHARED_CORE"):
        project, plan = _full_project(tmp_path / how, test_map, how)
        assert _reasons(plan) == expected, (
            f"the {how} full plan selects {_reasons(plan)}, not the map's outside targets the head holds")
        assert {e["target"]: e["why"] for e in plan["left_out"]} == left_out, (how, plan["left_out"])
        # a target the head does not hold keeps its entry in why_full, as today
        gone = {(w["target"], w["detail"]) for w in plan["why_full"] if w["reason"] == "UNRESOLVED_TARGET"}
        assert {(GONE_CASE, "CASE_GONE"), (GONE_FILE, "FILE_GONE")} <= gone, plan["why_full"]

    # the run line the close builds from the plan collects them (the named node alone of a node id)
    suite = project.root / OWN
    line = [str(project.root / "tests"), "--ignore", str(suite)] + command._scope_form(project.root, plan, suite)
    assert support.collected(project, line) == sorted(
        [UNIT_RECORDS, UNIT_DATA, support.PRODUCT_NODE, CHECKS_CASE, *SCRIPTS_CASES]), "the run line"

    # as today: targets under tests/ only, and a map nothing can be read from
    today = {OWN: ["OWN"], "tests": ["FULL"]}
    under = support.map_data(record_reading=[UNIT_RECORDS], every_close=["tests/unit/test_data_contract.py"],
                             couplings=[support.coupling(["tests/unit"])])
    project, plan = _full_project(tmp_path / "under", under, "BASE_UNKNOWN")
    assert _reasons(plan) == today and plan["left_out"] == [], (plan["selected"], plan["left_out"])

    for why, text in (("TEST_MAP_UNREADABLE", "- not\n- a map\n"), ("TEST_MAP_MISSING", None)):
        project = support.plant(tmp_path / why, test_map, {f"{OWN}test_own.py": support.PASS,
                                                          **support.relaxed_schema_files()})
        if text is None:
            (project.root / select.MAP_REL).unlink()
            project.commit("no map")
        else:
            project.commit("bad map", files={select.MAP_REL: text})
        plan = select.plan(project.root, support.WBS, ticket=support.TICKET)
        assert plan["scope"] == "full" and why in [w["reason"] for w in plan["why_full"]], plan["why_full"]
        assert _reasons(plan) == today and plan["left_out"] == [], (why, plan["selected"], plan["left_out"])
