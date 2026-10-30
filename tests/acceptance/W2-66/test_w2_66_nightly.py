"""Part 3, KPI 10: the nightly full uncached regression, on a fixture repository (never on this repository).

One command, ``python3 -m gov.close.nightly <branch> --root <project> [--coverage] --json``, runs the full
regression on the branch's head in the close's form, with JUnit XML, and writes its record under
``docs/close/nightly/`` (README, "Interface"). Every failing test is re-run alone: one that fails alone is a P1
package with ``git bisect run`` over the commits since the last green night; one that passes alone is a flaky
candidate; one that a scoped close since the last green night left out or passed is a P1 package with the test
map's correction in it. With ``--coverage`` (the weekly run), coverage.py with lens H's shim across child
processes writes the measured map. README, "Part 3".
"""

import json

import pytest

import w2_66_support as support

READS_GADGET = (
    "import os\n\n\ndef test_reads_the_gadget():\n"
    "    text = open('src/gov/gadget/other.py', encoding='utf-8').read()\n"
    f"    assert {support.BROKEN!r} not in text, 'the gadget is broken: ' + text\n")
READS_WIDGET = (
    "def test_reads_the_widget():\n"
    f"    text = open({support.WIDGET!r}, encoding='utf-8').read()\n"
    f"    assert {support.BROKEN!r} not in text, 'the widget is broken: ' + text\n")
FLAKY = ("import os\n\n\ndef test_fails_beside_others():\n"
         "    assert os.environ.get('PYTEST_XDIST_WORKER') is None, 'fails in a parallel worker only'\n")
GADGET_TEST = "tests/acceptance/W2-cc/test_cc_reads.py::test_reads_the_gadget"
WIDGET_TEST = "tests/acceptance/W2-cc/test_cc_widget.py::test_reads_the_widget"
FLAKY_TEST = "tests/acceptance/W1-dd/test_dd_flaky.py::test_fails_beside_others"


def _record(fixture, sandbox, *args, expect_green):
    run = support.run_nightly(fixture, sandbox, *args)
    record, rel = support.nightly_record(fixture, run)
    envelope = run.envelope()
    if expect_green:
        assert envelope.get("ok") is True and run.returncode == 0, f"the nightly run is not green\n{run.describe()}"
    else:
        assert envelope.get("ok") is False and run.returncode == support.EXIT_CHECK_FAILED, \
            f"a red nightly run is not stated red (exit 3)\n{run.describe()}"
    return record, rel, run


def test_one_command_runs_the_full_regression_on_the_branch_s_head_with_junit_xml(make_fixture, sandbox):
    fixture = make_fixture(green=False)
    fixture.merged({"src/gov/fine/f.py": "# fine\n"})
    support.close_support.git(fixture.root, "branch", "integrate")
    integrate = fixture.head()
    # The working branch moves on and breaks a test: the nightly runs the given branch's head, not the tree.
    fixture.merged({"tests/acceptance/W1-dd/test_dd_broken.py": "def test_dd_broken():\n    assert False\n"})
    record, rel, _ = _record(fixture, sandbox, "integrate", expect_green=True)
    assert record.get("branch") == "integrate" and record.get("head") == integrate, \
        f"the record does not name the branch and its head {integrate}: {record}"
    assert record.get("tree") == support.tree_of(fixture.root, integrate), f"the record names no tree: {record}"
    assert record.get("scope") == support.FULL and record.get("verdict") == support.GREEN, f"not full and green: {record}"
    ran = fixture.told_runs()
    missing = [support.case_of(wbs) for wbs in support.SUITES if support.case_of(wbs) not in ran]
    assert not missing, f"the nightly run did not run every suite: {missing}"
    cases = support.junit_cases(fixture.root, record)
    assert set(ran) <= set(cases), f"cases missing from the nightly run's JUnit XML: {sorted(set(ran) - set(cases))}"
    assert fixture.head() != integrate and "test_dd_broken" not in cases, "the nightly ran the working tree"


def test_a_red_that_fails_alone_is_a_p1_package_with_git_bisect_over_the_commits_since_the_last_green_night(
        make_fixture, sandbox):
    fixture = make_fixture(green=False)
    green = fixture.merged({GADGET_TEST.split("::")[0]: READS_GADGET}, "W2-cc reads the gadget")
    fixture.plant_green_night(green)
    fixture.merged({"src/gov/fine/f.py": "# harmless\n"}, "harmless one")
    culprit = fixture.merged({"src/gov/gadget/other.py": f"# {support.BROKEN}\n"}, "the culprit")
    fixture.merged({"src/gov/fine/g.py": "# harmless\n"}, "harmless two")
    record, _, _ = _record(fixture, sandbox, "main", expect_green=False)
    assert record.get("verdict") == support.RED and record.get("base") == green, \
        f"the record is not red, or its base is not the last green night ({green}): {record}"
    failure = [f for f in record.get("failures") or [] if f.get("test") == GADGET_TEST]
    assert failure and failure[0].get("alone") == "failed" and support.BROKEN in str(failure[0].get("text")), \
        f"the red is not named, re-run alone, with its text: {record.get('failures')}"
    packages = [p for p in record.get("packages") or [] if p.get("test") == GADGET_TEST and p.get("kind") == support.BISECT]
    assert packages and packages[0].get("priority") == support.P1, f"no P1 bisect package: {record.get('packages')}"
    assert packages[0].get("first_bad") == culprit, \
        f"git bisect over the commits since the last green night did not find {culprit}: {packages[0]}"
    assert green in str(packages[0].get("range")), f"the bisect's range does not start at the green night: {packages[0]}"


def test_a_red_that_passes_alone_is_a_flaky_candidate_and_is_not_bisected(make_fixture, sandbox):
    fixture = make_fixture(green=False)
    fixture.merged({FLAKY_TEST.split("::")[0]: FLAKY}, "a test that fails beside others")
    record, _, _ = _record(fixture, sandbox, "main", expect_green=False)
    failure = [f for f in record.get("failures") or [] if f.get("test") == FLAKY_TEST]
    assert failure and failure[0].get("alone") == "passed" and failure[0].get("class") == support.FLAKY_CANDIDATE, \
        f"the red that passes alone is not a flaky candidate: {record.get('failures')}"
    assert not [p for p in record.get("packages") or [] if p.get("test") == FLAKY_TEST and p.get("kind") == support.BISECT], \
        f"a flaky candidate was bisected: {record.get('packages')}"


def test_a_red_a_scoped_close_since_the_last_green_night_left_out_is_a_p1_package_with_the_map_corrected(
        make_fixture, sandbox):
    """W2-cc reads the widget as text, a coupling the test map does not declare: the scoped close of a widget
    change leaves W2-cc out and passes; the nightly finds W2-cc red."""
    fixture = make_fixture(green=False)
    green = fixture.merged({WIDGET_TEST.split("::")[0]: READS_WIDGET}, "W2-cc reads the widget as text")
    fixture.plant_green_night(green)
    support.widget_change(fixture, sandbox, text=f"# {support.BROKEN}\n")
    close = fixture.close(sandbox)
    support.passed(close)
    assert support.evidence_of(close).get("scope") == support.SCOPED, "the fixture's close is not scoped"
    fixture.commit_what_the_close_left()
    record, _, _ = _record(fixture, sandbox, "main", expect_green=False)
    misses = [p for p in record.get("packages") or [] if p.get("test") == WIDGET_TEST and p.get("kind") == support.SELECTION_MISS]
    assert misses and misses[0].get("priority") == support.P1, f"no P1 selection-miss package: {record.get('packages')}"
    correction = misses[0].get("test_map_correction") or {}
    couplings = correction.get("couplings") or []
    assert any(any(support.matches(p, support.WIDGET) for p in c.get("paths") or [])
               and any(support.covers(s, WIDGET_TEST) for s in c.get("suites") or []) for c in couplings), \
        f"the package's test-map correction does not take the widget to W2-cc: {correction}"
    assert support.TICKET in json.dumps(misses[0]), f"the package does not name the scoped close: {misses[0]}"


def test_the_weekly_coverage_run_writes_the_measured_map_across_child_processes(make_fixture, sandbox):
    pytest.importorskip("coverage")
    fixture = make_fixture(green=False)
    fixture.merged({
        "tests/acceptance/W2-cc/test_cc_imports.py":
            "def test_imports_the_gadget():\n    import gov.gadget.other  # noqa: F401\n",
        "tests/acceptance/W1-dd/test_dd_child.py":
            "import subprocess\nimport sys\n\n\ndef test_a_child_imports_the_gizmo():\n"
            "    subprocess.run([sys.executable, '-c', 'import gov.gizmo.third'], check=True)\n",
        "src/gov/gadget/other.py": "VALUE = 1\n",
        "src/gov/gizmo/third.py": "VALUE = 3\n",
    })
    record, _, _ = _record(fixture, sandbox, "main", "--coverage", expect_green=True)
    rel = record.get("measured_map")
    assert isinstance(rel, str) and (fixture.root / rel).is_file(), f"the record names no measured map: {record}"
    measured = json.loads((fixture.root / rel).read_text(encoding="utf-8"))

    def tests_of(source):
        return [t for path, tests in measured.items() if path.endswith(source) for t in tests]

    assert any("test_imports_the_gadget" in t for t in tests_of("src/gov/gadget/other.py")), \
        f"the measured map does not take the gadget to the test that imports it: {measured}"
    assert any("test_a_child_imports_the_gizmo" in t for t in tests_of("src/gov/gizmo/third.py")), \
        f"the measured map does not see the child process (lens H's shim): {measured}"
