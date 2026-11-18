"""S1 (and the schema's side of F1): a test map whose targets name any project-relative pytest folder, file or node id
validates against the test-map schema, and loads, as ``tests/`` targets do today (DEC-1199 (2), F-023).

The schema is the tree's own ``template/governance/kernel/schemas/test-map.schema.json``, judged with
``jsonschema.Draft202012Validator`` as ``gov.close.select.load_map`` judges. No loop is a parametrize (the tree's
opt-in list keeps one row of one); a failing form is named in the assertion.
"""
from gov.close import select

import w2_191_support as support

# Project-relative forms of every kind: a folder, with and without its slash, a top-level folder, a file, a node id,
# a class's method, a parameter set, a file at the top.
FORMS = ["governance/scripts/tests", "governance/scripts/tests/", "checks", "product/tests/test_a.py",
         "product/tests/test_a.py::test_case", "product/tests/test_a.py::TestK::test_m",
         "product/tests/test_a.py::test_case[a-b]", "test_top.py"]


def test_s1_the_schema_accepts_project_relative_targets_in_every_place():
    refused = []
    for position in support.POSITIONS:
        for form in FORMS:
            errors = support.schema_errors(support.with_target(position, form))
            if errors:
                refused.append(f"{position}: {form!r} -> {errors[0]}")
    assert not refused, "the schema refuses project-relative targets:\n" + "\n".join(refused)


def test_s1_the_schema_accepts_the_example_map_of_the_line():
    """The line's own example: governance/scripts/tests and product/tests/test_a.py named together."""
    test_map = support.map_data(
        record_reading=[support.SCRIPTS_SUITE], every_close=[support.PRODUCT_FILE],
        couplings=[support.coupling([support.SCRIPTS_SUITE, support.PRODUCT_NODE])])
    assert support.schema_errors(test_map) == []


def test_s1_the_loader_takes_a_map_naming_existing_suites_outside_tests(tmp_path):
    """The map the line describes, with its suites in the project: ``load_map`` gives the map, with no reason."""
    test_map = support.map_data(
        record_reading=[support.SCRIPTS_RECORDS_NODE, "checks"],
        every_close=[support.PRODUCT_FILE],
        couplings=[support.coupling([support.SCRIPTS_SUITE, support.PRODUCT_NODE,
                                     f"{support.PRODUCT_FILE}::TestK::test_m"])])
    project = support.plant(tmp_path, test_map)
    given, why = select.load_map(project.root)
    assert why is None and given == test_map, f"load_map gave {given!r} with reason {why!r}"


def test_s1_the_loader_takes_a_map_naming_one_suite_in_each_place(tmp_path):
    """Each place alone (record_reading, every_close, a coupling's suites) takes a target outside tests/."""
    taken, refused = 0, []
    for position in support.POSITIONS:
        project = support.plant(tmp_path / position, support.with_target(position, support.SCRIPTS_SUITE))
        given, why = select.load_map(project.root)
        if given is None:
            refused.append(f"{position}: {why}")
        else:
            taken += 1
    assert not refused and taken == len(support.POSITIONS), f"the loader refuses: {refused}"


def test_s1_tests_targets_validate_as_today_guard():
    """Guard case (green by design): ``tests/`` targets in every place and form validate before and after."""
    forms = ["tests/unit", "tests/acceptance/W1-x/", "tests/unit/test_a.py", "tests/unit/test_a.py::test_c",
             "tests/unit/test_a.py::TestK::test_m[p]"]
    refused = [f"{position}: {form!r}" for position in support.POSITIONS for form in forms
               if support.schema_errors(support.with_target(position, form))]
    assert not refused, f"the schema refuses tests/ targets it takes today: {refused}"


def test_s1_an_empty_or_non_text_target_is_still_refused_guard():
    """Guard case (green by design): widening the pattern keeps a target a non-empty string."""
    for bad in ("", None, 3, ["tests/unit"]):
        for position in support.POSITIONS:
            assert support.schema_errors(support.with_target(position, bad)), f"{position}: {bad!r} validates"
