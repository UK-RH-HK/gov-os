"""W2-191 S2 at the close's run line (path case P-W2-191-1 (b), DEC-1156 (7)): the strict and the reusing close run
their regression as ``pytest <root>/tests --ignore <own suite>`` with ``gov.close.command._scope_form``'s options, and
a selected target outside ``tests/`` is never collected by ``pytest tests``. What the run line collects is observed
by ``pytest --collect-only`` over the very arguments the close builds; the form of the extra arguments is not pinned.

The scope comes from a real ``select.plan`` (and ``batch.reused_form``) of a planted project that carries a
project-local, relaxed copy of the test-map schema, so the case is judged on the run line alone.
"""
from gov.close import batch, command, select

import w2_191_support as support

NINE = "tests/acceptance/W9/test_nine.py::test_nine"
W8_A_ONE = "tests/acceptance/W8/test_a.py::test_one"
W8_A_TWO = "tests/acceptance/W8/test_a.py::test_two"
W8_B = "tests/acceptance/W8/test_b.py::test_b"
EXTRA = {
    "tests/acceptance/W8/test_a.py": "def test_one():\n    assert True\n\n\ndef test_two():\n    assert True\n",
    "tests/acceptance/W8/test_b.py": "def test_b():\n    assert True\n",
    "tests/acceptance/W9/test_nine.py": "def test_nine():\n    assert True\n",
}
UNIT_RECORDS = "tests/unit/test_records.py::test_ok"
UNIT_DATA = "tests/unit/test_data_contract.py::test_ok"
SCRIPTS_CASES = [f"{support.SCRIPTS_RECORDS}::test_reads", f"{support.SCRIPTS_SUITE}/test_scripts.py::test_scripts"]
PRODUCT_CASE = support.PRODUCT_NODE
PRODUCT_OTHER = f"{support.PRODUCT_FILE}::TestK::test_m"
CHECKS_CASE = "checks/test_c.py::test_ok"


def _lines(tmp, test_map, changed):
    """``(project, own, strict plan, reused form)``: the ticket's change committed on a green base."""
    project = support.plant(tmp, test_map, {**EXTRA, **support.relaxed_schema_files()})
    project.green_night()
    project.work(changed)
    own = f"tests/acceptance/{support.WBS}/"
    plan = select.plan(project.root, support.WBS, ticket=support.TICKET)
    assert plan["scope"] == "scoped", plan["why_full"]
    return project, own, plan, batch.reused_form(project.root, own, plan)


def _run_line(project, own, scope):
    """The arguments of the close's regression run: its folder, the own suite's ``--ignore``, ``_scope_form``."""
    suite = project.root / own
    return [str(project.root / "tests"), "--ignore", str(suite)] + command._scope_form(project.root, scope, suite)


def test_s2_the_strict_and_reused_close_run_line_collects_the_targets_outside_tests(tmp_path):
    """A coupled folder and a record-reading node outside tests/, beside tests/ targets, some of them part of a
    suite: the run line collects every selected outside target (the named node alone of a node id) and, under
    tests/, exactly what it collected before (the selected targets, not the left-out ones). The reusing close's
    record-reading set holds the outside node alone. A project with tests/ targets only runs as before."""
    test_map = support.map_data(
        record_reading=[PRODUCT_CASE, W8_A_ONE],
        couplings=[support.coupling([support.SCRIPTS_SUITE])])
    project, own, plan, form = _lines(tmp_path / "both", test_map,
                                      {support.COUPLED_INPUT: "a rule, changed\n", "docs/notes.md": "# changed\n"})
    selected = {e["target"] for e in plan["selected"]}
    assert {support.SCRIPTS_SUITE, PRODUCT_CASE, W8_A_ONE} <= selected, selected  # the premise: the plan selects them

    strict = support.collected(project, _run_line(project, own, plan))
    outside = [n for n in strict if not n.startswith("tests/")]
    under = [n for n in strict if n.startswith("tests/")]
    # (2) under tests/ the run is what it was: the selected targets, not the left-out ones
    assert under == sorted([UNIT_RECORDS, UNIT_DATA, W8_A_ONE]), f"the strict run collects under tests/: {under}"
    # (1) every selected outside target, the named node alone of a node id, nothing unselected
    assert outside == sorted([*SCRIPTS_CASES, PRODUCT_CASE]), (
        f"the strict close's run line collects outside tests/: {outside}; the plan selected {sorted(selected)}")

    # (3) the reusing close: the record-reading set alone
    assert [e["target"] for e in form["selected"]] == [PRODUCT_CASE, W8_A_ONE], form["selected"]
    reused = support.collected(project, _run_line(project, own, form))
    assert [n for n in reused if n.startswith("tests/")] == [W8_A_ONE], reused
    assert [n for n in reused if not n.startswith("tests/")] == [PRODUCT_CASE], (
        f"the reusing close's run line collects outside tests/: {reused}")
    assert PRODUCT_OTHER not in strict + reused and CHECKS_CASE not in strict + reused

    # a project with tests/ targets only: the same as before
    only_map = support.map_data(record_reading=[W8_A_ONE], couplings=[support.coupling(["tests/unit/test_data_contract.py"],
                                                                                       paths=["data/*.txt"])])
    only, own, plan, form = _lines(tmp_path / "only", only_map, {"data/t.txt": "t, changed\n"})
    assert support.collected(only, _run_line(only, own, plan)) == sorted([UNIT_RECORDS, UNIT_DATA, W8_A_ONE])
    assert support.collected(only, _run_line(only, own, form)) == [W8_A_ONE]
