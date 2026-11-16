"""S2: gov close's selection resolves a target outside ``tests/`` (DEC-1199 (2), DEC-968); and F1's second half: a
project with ``tests/`` targets selects as before.

Asserted at the selection's own interfaces: ``select.scoped`` (and ``gov close --select``), ``select.plan`` and
``batch.reused_form``. How the close's pytest line is formed from a plan is not asserted (see the README, "Open").
"""
import json

from gov.close import batch, select

import w2_191_support as support

_targets = support.targets_of


def _coupled(tmp_path, suites, **more):
    return support.plant(tmp_path, support.map_data(couplings=[support.coupling(suites)], **more))


# --- S2: a coupling to a suite outside tests/ --------------------------------------------------------------------

def test_s2_a_change_a_coupling_maps_to_an_outside_suite_selects_that_folder(tmp_path):
    project = _coupled(tmp_path, [support.SCRIPTS_SUITE])
    project.work({support.COUPLED_INPUT: "a rule, changed\n"})
    chosen = select.scoped(project.root, support.TICKET)
    assert chosen["suites"] == [support.SCRIPTS_SUITE], chosen["suites"]
    assert chosen["why"][support.SCRIPTS_SUITE] == [f"COUPLING {support.COUPLED_INPUT}"]


def test_s2_gov_close_select_prints_the_outside_suite(tmp_path):
    project = _coupled(tmp_path, [support.SCRIPTS_SUITE, support.PRODUCT_NODE])
    project.work({support.COUPLED_INPUT: "a rule, changed\n"})
    done = support.gov_select(project)
    assert done.returncode == 0, done.stderr
    printed = json.loads(done.stdout)
    assert printed["ticket"] == support.TICKET
    assert printed["suites"] == sorted([support.SCRIPTS_SUITE, support.PRODUCT_NODE]), printed["suites"]
    assert "-p" in printed["pytest_options"]


def test_s2_the_strict_close_plan_selects_the_outside_suite_for_a_coupled_change(tmp_path):
    project = _coupled(tmp_path, [support.SCRIPTS_SUITE])
    project.green_night()
    project.work({support.COUPLED_INPUT: "a rule, changed\n"})
    plan = select.plan(project.root, support.WBS, ticket=support.TICKET)
    assert plan["scope"] == "scoped" and plan["why_full"] == [], plan["why_full"]
    assert _targets(plan)[support.SCRIPTS_SUITE] == ["COUPLING"], _targets(plan)


def test_s2_a_coupling_to_a_node_id_in_a_file_outside_tests_selects_that_node(tmp_path):
    project = _coupled(tmp_path, [f"{support.PRODUCT_FILE}::TestK::test_m"])
    project.work({support.COUPLED_INPUT: "a rule, changed\n"})
    assert select.scoped(project.root, support.TICKET)["suites"] == [f"{support.PRODUCT_FILE}::TestK::test_m"]


def test_s2_a_coupling_the_change_does_not_reach_selects_nothing_of_it(tmp_path):
    """Key edge: an outside suite is selected by its coupling's paths, not by being named in the map."""
    test_map = support.map_data(couplings=[support.coupling([support.SCRIPTS_SUITE]),
                                           support.coupling([support.PRODUCT_FILE], paths=["data/*.txt"])])
    project = support.plant(tmp_path, test_map)
    project.work({"data/t.txt": "t, changed\n"})
    assert select.scoped(project.root, support.TICKET)["suites"] == [support.PRODUCT_FILE]


# --- S2: record_reading and every_close outside tests/ -----------------------------------------------------------

def test_s2_a_record_only_change_runs_the_record_reading_target_outside_tests(tmp_path):
    project = support.plant(tmp_path, support.map_data(record_reading=[support.SCRIPTS_RECORDS_NODE]))
    project.work({"docs/notes.md": "# notes, changed\n"})
    chosen = select.scoped(project.root, support.TICKET)
    assert chosen["suites"] == [support.SCRIPTS_RECORDS_NODE], chosen["suites"]
    assert chosen["records_only"] is True


def test_s2_the_plan_selects_the_record_reading_target_outside_tests(tmp_path):
    project = support.plant(tmp_path, support.map_data(record_reading=[support.SCRIPTS_RECORDS_NODE, "checks"]))
    project.green_night()
    project.work({"docs/notes.md": "# notes, changed\n"})
    plan = select.plan(project.root, support.WBS, ticket=support.TICKET)
    assert plan["scope"] == "scoped" and plan["why_full"] == [], plan["why_full"]
    targets = _targets(plan)
    assert targets[support.SCRIPTS_RECORDS_NODE] == ["RECORD_READING"] and targets["checks"] == ["RECORD_READING"]


def test_s2_the_record_reading_set_of_a_reusing_close_holds_the_target_outside_tests(tmp_path):
    """``reused_form``: the record-reading set alone, its entry named and not ignored or deselected."""
    project = support.plant(tmp_path, support.map_data(record_reading=[support.SCRIPTS_RECORDS_NODE]))
    project.green_night()
    project.work({"docs/notes.md": "# notes, changed\n"})
    plan = select.plan(project.root, support.WBS, ticket=support.TICKET)
    form = batch.reused_form(project.root, f"tests/acceptance/{support.WBS}/", plan)
    assert form["scope"] == "reused" and form["why_full"] == []
    assert [e["target"] for e in form["selected"]] == [support.SCRIPTS_RECORDS_NODE], form["selected"]
    assert select.runs(support.SCRIPTS_RECORDS_NODE, form["ignore"], form["deselect"]), form


def test_s2_every_close_outside_tests_joins_a_change_holding_a_record_and_code(tmp_path):
    project = _coupled(tmp_path, [support.SCRIPTS_SUITE], every_close=[support.PRODUCT_FILE])
    project.green_night()
    project.work({"docs/notes.md": "# notes, changed\n", support.COUPLED_INPUT: "a rule, changed\n"})
    plan = select.plan(project.root, support.WBS, ticket=support.TICKET)
    assert plan["scope"] == "scoped", plan["why_full"]
    targets = _targets(plan)
    assert targets[support.PRODUCT_FILE] == ["EVERY_CLOSE"] and targets[support.SCRIPTS_SUITE] == ["COUPLING"], targets
    chosen = select.scoped(project.root, support.TICKET)
    assert support.PRODUCT_FILE in chosen["suites"] and support.SCRIPTS_SUITE in chosen["suites"], chosen["suites"]


def test_s2_targets_outside_tests_and_under_it_select_together(tmp_path):
    """Key edge (S2 with F1): a map naming both kinds selects each as it does alone."""
    test_map = support.map_data(
        record_reading=[support.SCRIPTS_RECORDS_NODE, "tests/unit/test_records.py"],
        couplings=[support.coupling([support.SCRIPTS_SUITE]),
                   support.coupling(["tests/unit/test_data_contract.py"], paths=["data/*.txt"])])
    project = support.plant(tmp_path, test_map)
    project.work({support.COUPLED_INPUT: "a rule, changed\n", "data/t.txt": "t, changed\n",
                  "docs/notes.md": "# notes, changed\n"})
    chosen = select.scoped(project.root, support.TICKET)
    # the record-reading node lies inside the coupled folder: the folder alone is listed (the selection's own rule)
    assert chosen["suites"] == sorted([support.SCRIPTS_SUITE, "tests/unit/test_data_contract.py",
                                       "tests/unit/test_records.py"]), chosen["suites"]


# --- F1: a project whose targets are all under tests/ selects as before (guard cases, green by design) --------------

TESTS_MAP = {"record_reading": ["tests/unit/test_records.py"],
             "couplings": [{"paths": ["data/*.txt"], "suites": ["tests/unit/test_data_contract.py"],
                            "why": "a text read"}]}


def test_f1_a_tests_only_project_selects_its_coupling_as_before_guard(tmp_path):
    project = support.plant(tmp_path, support.map_data(**TESTS_MAP))
    project.work({"data/t.txt": "t, changed\n"})
    chosen = select.scoped(project.root, support.TICKET)
    assert chosen["suites"] == ["tests/unit/test_data_contract.py"], chosen["suites"]
    assert chosen["why"] == {"tests/unit/test_data_contract.py": ["COUPLING data/t.txt"]}


def test_f1_a_tests_only_project_selects_its_record_reading_as_before_guard(tmp_path):
    project = support.plant(tmp_path, support.map_data(**TESTS_MAP))
    project.work({"docs/notes.md": "# notes, changed\n"})
    chosen = select.scoped(project.root, support.TICKET)
    assert chosen["suites"] == ["tests/unit/test_records.py"] and chosen["records_only"] is True, chosen["suites"]


def test_f1_a_tests_only_project_plans_as_before_guard(tmp_path):
    project = support.plant(tmp_path, support.map_data(**TESTS_MAP))
    project.green_night()
    project.work({"data/t.txt": "t, changed\n"})
    plan = select.plan(project.root, support.WBS, ticket=support.TICKET)
    assert plan["scope"] == "scoped" and plan["why_full"] == []
    assert _targets(plan) == {"tests/unit": ["UNIT"], "tests/unit/test_data_contract.py": ["COUPLING"],
                              "tests/unit/test_records.py": ["RECORD_READING"]}, _targets(plan)
    form = batch.reused_form(project.root, f"tests/acceptance/{support.WBS}/", plan)
    assert [e["target"] for e in form["selected"]] == ["tests/unit/test_records.py"]
