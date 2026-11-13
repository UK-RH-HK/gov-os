"""S2 and S3: the scoped close runs only the selection; one selection command for every level.

S2: a shared-core change selects its mapped suites (couplings and import graph), never the full suite; the ticket's
own change selects its suite and the reachable suites; records alone select the record-reading suites and nothing
else; governance files alone select nothing; a change nothing maps is refused (``SELECTION_REFUSED``, exit 2), never
widened; the close record shows no full-suite run.
S3: ``gov close --select <ticket>`` prints the scoped set and its pytest options, the same set the close runs
(compared in the close record's ``selection``).

Red on today's code: ``gov close --select`` does not exist (argparse refuses the option, exit 2 with a usage line);
the close record holds no ``selection``.
"""

import pytest

import w2_115_support as support

OTHERS = ("W2-bb", "W2-cc", "W2-dd", "W2-ee", "W2-ff")


def _selected(project, sandbox):
    project.ready(sandbox)
    return support.selection(project.select(sandbox))


def test_the_ticket_s_own_change_selects_its_suite_and_the_reachable_suites(make_project, sandbox):
    """S2: a change to the ticket's own module selects its own suite and the suites it reaches, nothing else."""
    project = make_project()
    project.work({support.WIDGET: "# the widget, CHANGED\n"})
    data = _selected(project, sandbox)
    suites = data["suites"]
    assert data["ticket"] == support.TICKET, f"the selection names another ticket: {data}"
    assert support.names(suites, support.suite_of("W2-aa")), f"the ticket's own suite is not selected: {suites}"
    assert support.names(suites, support.suite_of("W2-bb")), f"the reachable suite W2-bb is not selected: {suites}"
    for wbs in ("W2-cc", "W2-dd", "W2-ee"):
        assert not support.names(suites, support.suite_of(wbs)), f"{wbs}, which the change cannot reach, is selected"


def test_a_shared_core_change_selects_its_mapped_suites_never_the_full_suite(make_project, sandbox):
    """S2: a shared-core change selects the suites its couplings and the import graph name, never the full suite."""
    project = make_project()
    project.work({support.CORE: "# the shared core, CHANGED\n"})
    suites = _selected(project, sandbox)["suites"]
    assert support.names(suites, support.suite_of("W2-cc")), f"the coupled suite W2-cc is not selected: {suites}"
    assert support.names(suites, support.suite_of("W2-ee")), f"W2-ee, which imports the core, is not selected: {suites}"
    assert not support.names(suites, support.suite_of("W2-dd")), f"the selection widened to the full suite: {suites}"
    assert not any(s.rstrip("/") in ("tests", "tests/acceptance", ".") for s in suites), f"a whole tree: {suites}"


def test_records_alone_select_the_record_reading_suites_and_nothing_else(make_project, sandbox):
    """S2: a change to record places alone selects the record-reading suites the test map names, nothing else."""
    project = make_project()
    project.record_commit({support.REGISTER_REL: "# The decision register\n\nOne decision.\n"})
    suites = _selected(project, sandbox)["suites"]
    assert support.names(suites, support.RR_RECORDS), f"the record-reading suite is not selected: {suites}"
    for wbs in OTHERS:
        assert not support.names(suites, support.suite_of(wbs)), f"records alone selected {wbs}: {suites}"


def test_governance_files_alone_select_nothing_by_themselves(make_project, sandbox):
    """S2: a change to a governance file alone selects nothing by itself (no other suite, not the record readers)."""
    project = make_project()
    project.work({support.GOVERNANCE_FILE: "notes: changed\n"})
    suites = _selected(project, sandbox)["suites"]
    for wbs in OTHERS:
        assert not support.names(suites, support.suite_of(wbs)), f"a governance file selected {wbs}: {suites}"
    assert not support.names(suites, support.RR_RECORDS), f"a governance file selected the record readers: {suites}"


def test_a_change_nothing_maps_is_refused_with_its_reason_never_widened(make_project, sandbox):
    """S2: a planted change with no mapping exits with SELECTION_REFUSED and its reason, and prints no set."""
    project = make_project()
    project.merged({support.UNPLACED: "# odd\n"})
    project.work({support.WIDGET: "# the widget, CHANGED\n"})
    project.ready(sandbox)
    run = project.select(sandbox)
    assert run.returncode == 2, f"a refused selection does not exit 2\n{run.describe()}"
    assert support.SELECTION_REFUSED in run.stderr, f"stderr does not name SELECTION_REFUSED\n{run.describe()}"
    reason = run.stderr.split(support.SELECTION_REFUSED, 1)[1].strip(" :\n")
    assert reason, f"the refusal gives no reason\n{run.describe()}"
    assert '"suites"' not in run.stdout, f"a refused selection printed a set\n{run.describe()}"


def test_a_scoped_close_of_a_change_nothing_maps_is_refused(make_project, sandbox):
    """S2: the scoped close itself refuses an unmapped change with SELECTION_REFUSED rather than widening."""
    project = make_project()
    project.merged({support.UNPLACED: "# odd\n"})
    project.work({support.WIDGET: "# the widget, CHANGED\n"})
    project.ready(sandbox)
    run = project.close(sandbox)
    support.assert_refused(run, support.SELECTION_REFUSED)
    assert project.ticket_status() == "in_progress", "the ticket closed on a refused selection"
    assert not project.ran(support.case_of("W2-dd")), "the close widened to the full suite"


@pytest.fixture(scope="module")
def core_close(tmp_path_factory):
    """A scoped close of a shared-core change: the selection printed before it, then the close."""
    base = tmp_path_factory.mktemp("w2_115_core_close")
    sandbox = support.cli_support.make_sandbox(base / "sandbox")
    project = support.Smart(base / "project", base / "told")
    project.work({support.CORE: "# the shared core, CHANGED\n"})
    project.ready(sandbox)
    printed = project.select(sandbox)
    closed_head = project.head()
    run = project.close(sandbox)
    return project, printed, run, closed_head


def test_the_scoped_close_runs_only_the_selection_and_no_full_suite(core_close):
    """S2, S1: the scoped close of a shared-core change passes, ran the mapped suites, and the record shows no
    full-suite run (the suite nothing reaches did not run)."""
    project, _, run, _ = core_close
    support.passed(run)
    front = project.record()
    assert front.get("close") == support.SCOPED, f"the record does not say close: scoped: {front.get('close')!r}"
    assert project.ran(support.case_of("W2-cc")) and project.ran(support.case_of("W2-ee")), \
        "the mapped suites did not run"
    assert not project.ran(support.case_of("W2-dd")), "the scoped close ran a suite nothing reaches (the full suite)"
    runs = front.get("runs")
    assert isinstance(runs, list) and runs, f"the record names no runs: {runs!r}"
    assert not any("full" in str(r.get("name", "")).lower() for r in runs), f"a full-suite run is recorded: {runs}"


def test_select_prints_the_set_the_close_runs(core_close):
    """S3: ``gov close --select`` printed the scoped set and its pytest options, equal to the close record's
    ``selection`` for the same ticket."""
    project, printed, run, _ = core_close
    data = support.selection(printed)
    support.passed(run)
    recorded = project.record().get("selection")
    assert isinstance(recorded, dict), f"the close record holds no selection: {recorded!r}"
    assert recorded.get("suites") == data["suites"], \
        f"the close ran another set than --select printed: {recorded.get('suites')} != {data['suites']}"
    assert recorded.get("pytest_options") == data["pytest_options"], \
        f"the close used other pytest options: {recorded.get('pytest_options')} != {data['pytest_options']}"
