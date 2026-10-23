"""Part 2, KPI 6 and failure line 2: the close record's evidence block.

Scope (scoped or full, never full for a scoped run), base, head, tree, every suite and case run, every suite left
out and why, every skip with its reason and the skip count, the failing tests with their failure text kept, and
the run's JUnit XML. A passed close states it in its result and its close record; a refused close in its
refusal's details, as it states its ``test_runs`` (W1-30 round 13). README, "Part 2".
"""

import pytest

import w2_66_support as support

FAIL_TEXT = "planted failure in W1-bb"
SKIP_TEXT = "planted skip in W1-bb"
FAILING = "tests/acceptance/W1-bb/test_bb_fails.py::test_bb_fails"
SKIPPED = "tests/acceptance/W1-bb/test_bb_skips.py::test_bb_skips"


def _plant(fixture, fail=True):
    files = {SKIPPED.split("::")[0]: f"import pytest\n\n\ndef test_bb_skips():\n    pytest.skip({SKIP_TEXT!r})\n"}
    if fail:
        files[FAILING.split("::")[0]] = f"def test_bb_fails():\n    assert False, {FAIL_TEXT!r}\n"
    fixture.merged(files, "a test designer's new cases in W1-bb")


@pytest.fixture(scope="module")
def refused_close(module_dir):
    fixture = support.Fixture(module_dir / "project", module_dir / "told")
    sandbox = support.cli_support.make_sandbox(module_dir / "sandbox")
    _plant(fixture)
    support.widget_change(fixture, sandbox)
    return fixture, fixture.close(sandbox)


def test_a_refused_close_states_its_evidence_and_says_scoped(refused_close):
    fixture, run = refused_close
    support.refused(run)
    evidence = support.evidence_of(run)
    assert evidence.get("scope") == support.SCOPED, f"a scoped run is stated {evidence.get('scope')!r}"
    assert evidence.get("head") == fixture.head() and evidence.get("tree") == support.tree_of(fixture.root), \
        f"the refused close's evidence does not state its head and tree: {evidence}"
    assert evidence.get("base") == fixture.initial, f"the refused close's evidence states no base: {evidence}"


def test_every_failing_test_is_named_with_its_failure_text_kept(refused_close):
    _, run = refused_close
    evidence = support.evidence_of(run)
    failures = [f for f in evidence.get("failures") or [] if f.get("test") == FAILING]
    assert failures, f"the failing test is not named: {evidence.get('failures')}"
    assert FAIL_TEXT in str(failures[0].get("text")), f"the failure text is not kept: {failures[0]}"


def test_every_skip_is_named_with_its_reason_and_counted(refused_close):
    _, run = refused_close
    evidence = support.evidence_of(run)
    skips = evidence.get("skips")
    assert isinstance(skips, list), f"the evidence names no skips: {evidence}"
    named = [s for s in skips if s.get("test") == SKIPPED]
    assert named and SKIP_TEXT in str(named[0].get("reason")), f"the skip is not named with its reason: {skips}"
    assert evidence.get("skip_count") == len(skips) == 1, \
        f"the skip count is not the number of skips: {evidence.get('skip_count')} for {skips}"


def test_the_junit_xml_of_a_refused_close_holds_the_failure_text_and_the_skip(refused_close):
    fixture, run = refused_close
    cases = support.junit_cases(fixture.root, support.evidence_of(run))
    assert cases.get("test_bb_fails", ("", ""))[0] in ("failure", "error") and \
        FAIL_TEXT in cases["test_bb_fails"][1], f"the JUnit XML does not hold the failure with its text: {cases}"
    assert cases.get("test_bb_skips", ("",))[0] == "skipped", f"the JUnit XML does not hold the skip: {cases}"


def test_a_refused_close_names_every_suite_it_left_out(refused_close):
    fixture, run = refused_close
    evidence = support.evidence_of(run)
    missing = [wbs for wbs in support.NOT_REACHED_BY_A_WIDGET_CHANGE
               if not support.suite_named_left_out(fixture, evidence, wbs)]
    assert not missing, f"left-out suites the refused close does not name: {missing}"


def test_a_refused_close_leaves_nothing_untracked_but_its_repair_ticket(refused_close):
    """Its JUnit XML is kept where git ignores it (DEC-490: a refusal leaves only its repair ticket)."""
    fixture, run = refused_close
    left = [rel for rel in support.close_support.untracked_paths(fixture)
            if not (rel.startswith(".tickets/") and rel.endswith(".md"))]
    assert not left, f"the refused close left untracked files in the tree: {left}"


def test_a_passed_close_names_its_skips_in_the_result_and_the_record(fixture, sandbox):
    _plant(fixture, fail=False)
    support.widget_change(fixture, sandbox)
    run = fixture.close(sandbox)
    support.passed(run)
    evidence = support.evidence_of(run)
    assert [s.get("test") for s in evidence.get("skips") or []] == [SKIPPED], f"the skip is not named: {evidence}"
    assert evidence.get("skip_count") == 1 and evidence.get("failures") == [], f"counts are wrong: {evidence}"
    assert support.record_evidence(fixture) == evidence, "the close record's evidence block is not the result's"


def test_a_full_close_names_every_suite_it_ran_and_its_junit_xml_holds_every_case(fixture, sandbox):
    support.widget_change(fixture, sandbox)
    run = fixture.close(sandbox, support.FULL_OPTION)
    support.passed(run)
    evidence = support.evidence_of(run)
    unnamed = [wbs for wbs in support.SUITES if not support.selected_for(evidence, support.suite_of(wbs))]
    assert not unnamed and support.selected_for(evidence, "tests/unit"), \
        f"the full run does not name these suites as run: {unnamed}"
    cases = support.junit_cases(fixture.root, evidence)
    missing = sorted(set(fixture.told_runs()) - set(cases))
    assert not missing, f"cases that ran are missing from the full run's JUnit XML: {missing}"
