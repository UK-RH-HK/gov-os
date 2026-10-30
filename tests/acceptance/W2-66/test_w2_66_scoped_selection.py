"""Part 1, KPI 1, 3, 4 and 5: a one-module change outside the shared core runs a scoped regression.

One close of the fixture project, shared by the module's cases: the ticket changes ``src/gov/widget/thing.py``
(its own paths, and W1-bb's, a Wave 1 ticket's, and W2-bz's, a Wave 2 ticket's), on a project whose base is the initial commit (a green nightly
record names it, committed after it: a record-only commit inside the change). README, "Part 1".
"""

import pytest

import w2_66_support as support


@pytest.fixture(scope="module")
def scoped(module_dir):
    fixture = support.Fixture(module_dir / "project", module_dir / "told")
    sandbox = support.cli_support.make_sandbox(module_dir / "sandbox")
    support.widget_change(fixture, sandbox)
    head = fixture.head()
    run = fixture.close(sandbox)
    return fixture, run, head


def _evidence(scoped):
    return support.evidence_of(scoped[1])


def test_the_scoped_close_passes(scoped):
    support.passed(scoped[1])


def test_a_one_module_change_is_stated_scoped_never_full(scoped):
    evidence = _evidence(scoped)
    assert evidence.get("scope") == support.SCOPED, f"a one-module change is not a scoped run: {evidence}"
    assert evidence.get("left_out"), "a scoped run names nothing it left out"


def test_the_base_is_the_last_fully_green_commit(scoped):
    evidence = _evidence(scoped)
    fixture, _, _ = scoped
    assert evidence.get("base") == fixture.initial, \
        f"the base is not the commit the green record names ({fixture.initial}): {evidence.get('base')!r}"


def test_the_record_only_commits_since_the_base_are_inside_the_change(scoped):
    evidence = _evidence(scoped)
    fixture, _, _ = scoped
    changed = evidence.get("changed")
    assert isinstance(changed, list), f"the evidence does not state the change: {evidence}"
    assert fixture.nightly_record in changed, \
        f"the record-only commit after the base is not in the change: {changed}"
    assert support.WIDGET in changed, f"the ticket's change is not in the change: {changed}"


def test_the_head_and_the_tree_are_stated(scoped):
    evidence = _evidence(scoped)
    fixture, _, head = scoped
    assert evidence.get("head") == head, f"the head is not stated: {evidence.get('head')!r}, expected {head}"
    assert evidence.get("tree") == support.tree_of(fixture.root, head), f"the tree is not stated: {evidence}"


def test_the_own_suite_runs_and_is_named(scoped):
    evidence = _evidence(scoped)
    fixture, _, _ = scoped
    assert fixture.ran(support.case_of(support.WBS)), "the ticket's own suite did not run"
    why = {w["reason"] for w in support.selected_for(evidence, support.suite_of(support.WBS))}
    assert support.OWN in why, f"the own suite is not named with {support.OWN}: {evidence.get('selected')}"


def test_the_unit_tests_run_and_are_named(scoped):
    evidence = _evidence(scoped)
    fixture, _, _ = scoped
    assert fixture.ran("test_in_unit"), "tests/unit did not run"
    why = {w["reason"] for w in support.selected_for(evidence, "tests/unit")}
    assert support.UNIT in why, f"tests/unit is not named with {support.UNIT}: {evidence.get('selected')}"


@pytest.mark.parametrize("wbs", ["W1-bb", "W2-bz"])
def test_a_suite_whose_ticket_paths_overlap_the_change_runs_and_is_named_with_why(scoped, wbs):
    evidence = _evidence(scoped)
    fixture, _, _ = scoped
    ticket = support.SUITES[wbs][0]
    assert fixture.ran(support.case_of(wbs)), f"{wbs}, whose ticket's paths overlap the change, did not run"
    why = [w for w in support.selected_for(evidence, support.suite_of(wbs)) if w["reason"] == support.OVERLAP]
    assert why, f"{wbs} is not named with {support.OVERLAP}: {evidence.get('selected')}"
    assert any(w.get("ticket") == ticket and support.WIDGET in (w.get("paths") or []) for w in why), \
        f"the reason for {wbs} names neither its ticket {ticket} nor the changed path: {why}"


@pytest.mark.parametrize("wbs", support.NOT_REACHED_BY_A_WIDGET_CHANGE)
def test_a_suite_the_change_cannot_reach_is_left_out_and_named_with_why(scoped, wbs):
    evidence = _evidence(scoped)
    fixture, _, _ = scoped
    assert not fixture.ran(support.case_of(wbs)), f"{wbs} ran, though nothing of the change reaches it"
    assert support.suite_named_left_out(fixture, evidence, wbs), \
        f"{wbs} is not named as left out: {evidence.get('left_out')}"
    why = {w["reason"] for w in support.left_out_for(evidence, support.suite_of(wbs))} or \
        {w["reason"] for entry in evidence["left_out"] if support.within(str(entry.get("target")),
                                                                          support.suite_of(wbs))
         for w in support.reasons(entry)}
    assert support.NOT_REACHED in why, f"{wbs} is left out without the reason {support.NOT_REACHED}: {why}"


def test_the_selection_keeps_the_full_runs_form_so_a_bare_conftest_import_still_collects(scoped):
    """W1-35's collection (lens H finding 17): W1-bb imports a name from a bare ``conftest``; with W2-bz selected
    too, a run given the two folders as a list fails to collect it. The full run's form collects it."""
    fixture, run, _ = scoped
    assert fixture.ran(support.case_of("W1-bb")) and fixture.ran(support.case_of("W2-bz")), \
        f"W1-bb or W2-bz did not run: the selection does not keep the full run's form\n{run.describe()}"


def test_the_record_reading_set_runs_on_a_scoped_close_and_is_named(scoped):
    evidence = _evidence(scoped)
    fixture, _, _ = scoped
    assert fixture.ran("test_rr_reads_the_register"), "the record-reading set did not run on a scoped close"
    why = {w["reason"] for w in support.selected_for(evidence, support.RR_RECORDS)}
    assert support.RECORD_READING in why, f"the set is not named with {support.RECORD_READING}: {why}"
    assert not fixture.ran("test_rr_other"), "W1-rr's other file ran: the set ran its whole suite"


def test_the_every_close_files_run_and_are_named(scoped):
    evidence = _evidence(scoped)
    fixture, _, _ = scoped
    assert fixture.ran("test_ec_contract"), "the every-close file (W1-07's contract files' kind) did not run"
    why = {w["reason"] for w in support.selected_for(evidence, support.EC_CONTRACT)}
    assert support.EVERY_CLOSE in why, f"the every-close file is not named with {support.EVERY_CLOSE}: {why}"
    assert not fixture.ran("test_ec_other"), "W1-ec's other file ran: the every-close list ran its whole suite"


def test_the_serial_cases_of_the_selected_suites_run_alone_and_only_those(scoped):
    fixture, run, _ = scoped
    runs = fixture.told_runs()
    assert support.close_support.ran_alone(runs.get("test_apart_W1_bb", [])), \
        f"the serial-only case of a selected suite did not run once, alone: {runs.get('test_apart_W1_bb')}"
    assert "test_apart_W1_dd" not in runs, "the serial-only case of a left-out suite ran"


def test_the_record_says_which_serial_cases_ran(scoped):
    _, run, _ = scoped
    runs = support.passed(run).get("test_runs") or []
    afterwards = [r for r in runs if r.get("form") == "serial-afterwards"]
    assert len(afterwards) == 1 and afterwards[0].get("cases") == [support.BB_APART], \
        f"the serial run afterwards does not name exactly the selected suites' case: {afterwards}"


def test_the_close_record_holds_the_same_evidence_block(scoped):
    evidence = _evidence(scoped)
    fixture, _, _ = scoped
    assert support.record_evidence(fixture) == evidence, "the close record's evidence block is not the result's"


def test_the_junit_xml_holds_every_case_run_and_no_case_left_out(scoped):
    evidence = _evidence(scoped)
    fixture, _, _ = scoped
    cases = support.junit_cases(fixture.root, evidence)
    ran = {name for name in fixture.told_runs()}
    assert ran <= set(cases), f"cases that ran are missing from the JUnit XML: {sorted(ran - set(cases))}"
    left = {support.case_of(wbs) for wbs in support.NOT_REACHED_BY_A_WIDGET_CHANGE} | {"test_apart_W1_dd"}
    assert not left & set(cases), f"the JUnit XML holds cases that did not run: {sorted(left & set(cases))}"


def test_a_scoped_close_states_its_settings_defaults(scoped):
    evidence = _evidence(scoped)
    assert evidence.get("per_test_timeout") == support.DEFAULT_PER_TEST_TIMEOUT, \
        f"the per-test limit is not stated, or not the default {support.DEFAULT_PER_TEST_TIMEOUT}: {evidence}"
    assert evidence.get("distribution") == support.DEFAULT_DISTRIBUTION, \
        f"the distribution mode is not stated, or not the default {support.DEFAULT_DISTRIBUTION!r}: {evidence}"
