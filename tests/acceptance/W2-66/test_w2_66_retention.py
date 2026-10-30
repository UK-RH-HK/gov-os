"""Part 3, the retention KPI (DEC-905, DEC-904 item 1): every pytest run of a close and of the nightly is given
``-o tmp_path_retention_policy=failed``.

So a passing test's ``tmp_path`` goes as the test ends and a failing test's stays, and the evidence block names
the option (README, "Interface", items 6, 8 and 9). How a case sees it: the fixture's own tests report, at every
run, what their run's configuration says (the option's value as the run reads it, and the ``-o`` overrides the run
was given), the parallel worker they ran in, and their own ``tmp_path``, in a file of their own outside the project.
The case then looks whether each folder is still there. No case reads the close's command line.

The fixture's runs: the ticket's own suite (W2-aa, the acceptance run), W1-bb's new file (the regression's parallel
run: it overlaps the widget change), and W1-bb's serial-only case (``support.BB_APART``, run alone afterwards) with
two parameter sets. In the refused close one test of the parallel run and one parameter set of the serial case
fail. README, "Part 3".
"""

import json
from pathlib import Path

import pytest

import w2_66_support as support

POLICY_KEY = "tmp_path_retention_policy"
POLICY = "failed"
OVERRIDE = f"{POLICY_KEY}={POLICY}"

OWN_FILE = "tests/acceptance/W2-aa/test_aa_retention.py"
PARALLEL_FILE = "tests/acceptance/W1-bb/test_bb_retention.py"
SERIAL_FILE = support.BB_APART.split("::")[0]
SERIAL_NAME = support.BB_APART.split("::")[1]

# The fixture's reporting tests, by the run that holds them: (passing, failing) case names.
FORMS = {
    "acceptance": (["test_aa_retention"], []),
    "parallel": (["test_bb_retention_passes"], ["test_bb_retention_fails"]),
    "serial-afterwards": ([f"{SERIAL_NAME}[passes]"], [f"{SERIAL_NAME}[fails]"]),
}


def _reporting(name, report, outcome="'passes'", decorator="", arguments=""):
    """One test function that reports how its run was configured, then passes when ``outcome`` is ``'passes'``."""
    return (
        f"{decorator}"
        f"def {name}(request, tmp_path{arguments}):\n"
        "    (tmp_path / 'written').write_text('a file in the test folder', encoding='utf-8')\n"
        "    case = os.environ['PYTEST_CURRENT_TEST'].split('::')[-1].split(' ')[0]\n"
        f"    with open(os.path.join({str(report)!r}, case), 'a', encoding='utf-8') as out:\n"
        f"        out.write(json.dumps({{'policy': request.config.getini({POLICY_KEY!r}),\n"
        "                              'overrides': list(request.config.option.override_ini or []),\n"
        "                              'worker': os.environ.get('PYTEST_XDIST_WORKER', 'none'),\n"
        "                              'tmp_path': str(tmp_path)}) + '\\n')\n"
        f"    assert {outcome} == 'passes', 'planted failure: ' + case\n\n\n"
    )


_HEAD = "import json\nimport os\n\nimport pytest\n\n\n"


def plant(fixture, report, fail):
    """The reporting tests, merged before the ticket's work; with ``fail``, one of each run fails."""
    report.mkdir(parents=True, exist_ok=True)
    parallel = _reporting("test_bb_retention_passes", report)
    if fail:
        parallel += _reporting("test_bb_retention_fails", report, outcome="'fails'")
    sets = ["passes", "fails"] if fail else ["passes"]
    serial = _reporting(SERIAL_NAME, report, outcome="outcome",
                        decorator=f"@pytest.mark.parametrize('outcome', {sets!r})\n", arguments=", outcome")
    fixture.merged({OWN_FILE: _HEAD + _reporting("test_aa_retention", report),
                    PARALLEL_FILE: _HEAD + parallel,
                    SERIAL_FILE: _HEAD + serial}, "a test designer's cases that report their runs")


def reports(report):
    """``{case: [report, ...]}``: one report for each time the case ran."""
    found = {}
    for path in sorted(Path(report).iterdir()):
        found[path.name] = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    return found


def assert_given_the_option(found, names, where):
    """Each case of ``names`` ran, and every run of it was given ``-o tmp_path_retention_policy=failed``."""
    for name in names:
        runs = found.get(name)
        assert runs, f"{name} did not run in {where}: what ran {sorted(found)}"
        wrong = [r for r in runs if r.get("policy") != POLICY or OVERRIDE not in (r.get("overrides") or [])]
        assert not wrong, (f"{where}: {name} ran without -o {OVERRIDE}; its run's configuration said "
                           f"{[(r.get('policy'), r.get('overrides')) for r in wrong]}")
    return [r for name in names for r in found[name]]


def _in_form(runs, form, name):
    if form == "parallel":
        assert all(r["worker"] != "none" for r in runs), f"{name} did not run in a worker of the parallel run: {runs}"
    elif form == "serial-afterwards":
        assert all(r["worker"] == "none" for r in runs), f"{name} did not run alone, in no worker: {runs}"


# --------------------------------------------------------------------------
# The close: one refused close (a failing test in each regression run) and one passed close
# --------------------------------------------------------------------------

@pytest.fixture(scope="module")
def refused_close(module_dir):
    base = module_dir / "refused"
    fixture = support.Fixture(base / "project", base / "told")
    sandbox = support.cli_support.make_sandbox(base / "sandbox")
    plant(fixture, base / "report", fail=True)
    support.widget_change(fixture, sandbox)
    run = fixture.close(sandbox)
    return fixture, run, reports(base / "report")


@pytest.fixture(scope="module")
def passed_close(module_dir):
    base = module_dir / "passed"
    fixture = support.Fixture(base / "project", base / "told")
    sandbox = support.cli_support.make_sandbox(base / "sandbox")
    plant(fixture, base / "report", fail=False)
    support.widget_change(fixture, sandbox)
    run = fixture.close(sandbox)
    return fixture, run, reports(base / "report")


@pytest.mark.parametrize("form", sorted(FORMS))
def test_every_test_run_of_the_close_is_given_the_retention_option(refused_close, form):
    _, run, found = refused_close
    passing, failing = FORMS[form]
    for name in passing + failing:
        runs = assert_given_the_option(found, [name], f"the close's {form} run\n{run.describe()}")
        _in_form(runs, form, name)


@pytest.mark.parametrize("form", ["parallel", "serial-afterwards"])
def test_a_passing_test_s_folder_goes_and_a_failing_test_s_stays(refused_close, form):
    _, run, found = refused_close
    passing, failing = FORMS[form]
    for name in passing + failing:
        assert found.get(name), f"{name} did not run in the close's {form} run: what ran {sorted(found)}"
    kept = [r["tmp_path"] for name in passing for r in found[name] if Path(r["tmp_path"]).exists()]
    assert not kept, f"a passing test's tmp_path is still there after the close ({form} run): {kept}"
    gone = [r["tmp_path"] for name in failing for r in found[name] if not (Path(r["tmp_path"]) / "written").is_file()]
    assert not gone, f"a failing test's tmp_path was not kept after the close ({form} run): {gone}"


def test_the_refused_close_s_evidence_names_the_option(refused_close):
    _, run, _ = refused_close
    support.refused(run)
    evidence = support.evidence_of(run)
    assert evidence.get(POLICY_KEY) == POLICY, \
        f"the refused close's evidence does not name {POLICY_KEY}: {POLICY!r}: {evidence}"


def test_a_passed_close_names_the_option_in_its_result_and_its_record(passed_close):
    fixture, run, found = passed_close
    support.passed(run)
    assert_given_the_option(found, [name for passing, _ in FORMS.values() for name in passing],
                            f"the passed close\n{run.describe()}")
    evidence = support.evidence_of(run)
    assert evidence.get(POLICY_KEY) == POLICY, f"the passed close's evidence does not name {POLICY_KEY}: {evidence}"
    assert support.record_evidence(fixture).get(POLICY_KEY) == POLICY, \
        f"the close record's evidence block does not name {POLICY_KEY}"
    kept = [r["tmp_path"] for runs in found.values() for r in runs if Path(r["tmp_path"]).exists()]
    assert not kept, f"a passing test's tmp_path is still there after the passed close: {kept}"


# --------------------------------------------------------------------------
# The nightly runs in the close's form (KPI 10; DEC-905 item 1)
# --------------------------------------------------------------------------

def test_the_nightly_run_s_test_runs_are_given_the_retention_option(make_fixture, sandbox, tmp_path):
    fixture = make_fixture(green=False)
    report = tmp_path / "report"
    plant(fixture, report, fail=False)
    run = support.run_nightly(fixture, sandbox, "main")
    assert run.envelope().get("ok") is True and run.returncode == 0, f"the nightly run is not green\n{run.describe()}"
    found = reports(report)
    for form in ("parallel", "serial-afterwards"):
        for name in FORMS[form][0]:
            _in_form(assert_given_the_option(found, [name], f"the nightly's {form} run\n{run.describe()}"), form, name)
    kept = [r["tmp_path"] for runs in found.values() for r in runs if Path(r["tmp_path"]).exists()]
    assert not kept, f"a passing test's tmp_path is still there after the nightly run: {kept}"
