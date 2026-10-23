"""Part 1, KPI 1 (test-side imports), KPI 3 (declared couplings) and KPI 5 with failure line 3 (the record-reading
set on a head with record-only commits; the pre-close gate's own ``gov check`` result). README, "Part 1"."""

import json

import w2_66_support as support


def test_a_changed_helper_selects_every_suite_that_imports_it_directly_or_through_another_helper(fixture, sandbox):
    """``gg_support`` lives in W1-gg's folder; W1-hh's ``hh_support`` imports it, and W2-ii imports ``hh_support``
    (the pattern of W2-01 → ``w1_30_support`` → ``w1_07_support``). A change to it reaches all three."""
    fixture.merged({support.GG_HELPER: "VALUE = 2\n"}, "a test designer's revision of a shared helper")
    support.widget_change(fixture, sandbox)
    run = fixture.close(sandbox)
    support.passed(run)
    evidence = support.evidence_of(run)
    assert evidence.get("scope") == support.SCOPED, f"a helper change is not a scoped run: {evidence}"
    for wbs in ("W1-gg", "W1-hh", "W2-ii"):
        assert fixture.ran(support.case_of(wbs)), f"{wbs} did not run, though it imports the changed helper"
    gg = {w["reason"] for w in support.selected_for(evidence, support.suite_of("W1-gg"))}
    assert support.TEST_CHANGED in gg, f"the helper's own suite is not named with {support.TEST_CHANGED}: {gg}"
    for wbs in ("W1-hh", "W2-ii"):
        why = [w for w in support.selected_for(evidence, support.suite_of(wbs)) if w["reason"] == support.HELPER]
        assert why and any(support.GG_HELPER in json.dumps(w) for w in why), \
            f"{wbs} is not named with {support.HELPER} and the helper it imports: {evidence.get('selected')}"
    for wbs in ("W2-cc", "W1-dd", "W1-cp"):
        assert not fixture.ran(support.case_of(wbs)), f"{wbs} ran, though it imports no changed helper"


def test_a_declared_coupling_selects_its_suites_and_names_why(fixture, sandbox):
    """``src/gov/textread/data.txt`` is read as text by W1-cp; no import shows it, the test map declares it."""
    fixture.merged({support.COUPLED_INPUT: "data, changed\n"})
    support.widget_change(fixture, sandbox)
    run = fixture.close(sandbox)
    support.passed(run)
    evidence = support.evidence_of(run)
    assert evidence.get("scope") == support.SCOPED, f"a declared coupling's file is not placed: {evidence}"
    assert fixture.ran(support.case_of("W1-cp")), "the coupled suite did not run"
    why = [w for w in support.selected_for(evidence, support.suite_of("W1-cp")) if w["reason"] == support.COUPLING]
    assert why and any(support.COUPLED_INPUT in json.dumps(w) for w in why), \
        f"W1-cp is not named with {support.COUPLING} and the changed path: {evidence.get('selected')}"


def test_a_record_only_commit_widens_nothing(fixture, sandbox):
    """The register, a ticket file, a probe record and the orchestration record are record-only (DEC-891)."""
    fixture.record_commit({
        support.REGISTER_REL: "# The decision register\n\nDEC-001 decided.\n",
        support.close_support.ticket_path("PROJ-dddd"):
            (fixture.root / support.close_support.ticket_path("PROJ-dddd")).read_text(encoding="utf-8") + "\n",
        "docs/probes/PROJ-cccc/PR-PROJ-cccc.md": support.close_support.probe_record("PROJ-cccc"),
        "governance/project/orchestration/log/a-note.md": "# a note\n",
    })
    support.widget_change(fixture, sandbox)
    run = fixture.close(sandbox)
    support.passed(run)
    evidence = support.evidence_of(run)
    assert evidence.get("scope") == support.SCOPED, f"a record-only commit widened the run: {evidence}"
    assert support.REGISTER_REL in (evidence.get("changed") or []), "the record-only commit is not in the change"
    assert not fixture.ran(support.case_of("W1-dd")), "a ticket-file edit selected that ticket's suite"
    assert fixture.ran("test_rr_reads_the_register"), "the record-reading set did not run"


def test_a_record_reading_test_turned_red_by_a_record_only_commit_refuses_the_scoped_close(fixture, sandbox):
    """Failure line 3: the record-only commit breaks the register; the set runs on this head and blocks."""
    fixture.record_commit({support.REGISTER_REL: f"# The decision register\n\n{support.BROKEN}\n"})
    support.widget_change(fixture, sandbox)
    run = fixture.close(sandbox)
    error = support.refused(run)
    evidence = support.evidence_of(run)
    assert evidence.get("scope") == support.SCOPED, f"the refused close is not stated scoped: {evidence}"
    failing = [f for f in evidence.get("failures") or [] if support.covers(support.RR_RECORDS, str(f.get("test")))]
    assert failing, f"the record-reading test is not among the failures: {evidence.get('failures')}\n{error}"
    assert support.BROKEN in str(failing[0].get("text")), f"the failure text is not kept: {failing[0]}"


def test_the_record_reading_set_reads_the_pre_close_gate_s_own_check_result(fixture, sandbox, tmp_path):
    """KPI 5: the gate's ``gov check --json`` output, given with ``--check-result``, reaches the set's tests in
    ``GOV_CLOSE_CHECK_RESULT``, so that a context-reproducibility or core-schema case reads it instead of running
    ``gov check`` again."""
    support.widget_change(fixture, sandbox)
    gate = support.close_support.run_gov(fixture.root, sandbox, "check", "--json")
    result = tmp_path / "gate-check.json"
    result.write_text(gate.stdout, encoding="utf-8")
    run = fixture.close(sandbox, support.CHECK_RESULT_OPTION, str(result))
    support.passed(run)
    seen = fixture.check_result_seen()
    assert seen is not None, "the record-reading test did not run"
    assert seen == gate.stdout, \
        f"the record-reading set was not handed the gate's own check result in {support.CHECK_RESULT_VARIABLE}"
