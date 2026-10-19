"""KPI 5 and failure KPI 3, through the ratchet's core: its one public function (DEC-757 item 2: "the core as one
public function", which W2-19 reuses for its own runs).

The function (README, "The ratchet's core"): ``gov.close.ratchet.apply_accepted_reds(root, results)`` (an optional
``commit`` defaults to ``HEAD``). ``results`` maps a test id to ``passed``, ``failed``, ``error`` or ``skipped``;
a red is ``failed`` or ``error``. It reads the path map's ``accepted_reds``, the decision register and the history
at ``root``, and returns ``{"ok": bool, "accepted_reds": [...], "findings": [...]}``: each report as the close's
(``test``, ``decision``, ``reason``, ``fixed_by``, ``result``), each finding ``{"code", "test", "message"}``.

The project: W2-53's temporary project with the owner's decision and entry for the listed red (as in
``test_w2_53_accepted_reds.py``); no ticket is needed, the function judges results it is given.
"""

import pytest

import w2_53_support as support

DECISION = "DEC-902"
LISTED = support.RETR_RED
OTHER = support.SHARE_RED
PASSING = support.RETR_GREEN


def _listed(project, role="owner"):
    project.record_decision(DECISION, support.OWNER_ACCEPTED, support.owner_text_naming(LISTED))
    return support.add_entries(project, support.ACCEPTED_REDS,
                               [support.red_entry(LISTED, DECISION, fixed_by="W2-13")], role=role)


def _reports(verdict, test_id, result):
    return [report for report in verdict.get(support.ACCEPTED_REDS) or []
            if report.get("test") == test_id and report.get("result") == result
            and report.get("decision") == DECISION and report.get("fixed_by") == "W2-13"]


def _coded(verdict, code, test_id):
    return [finding for finding in verdict.get("findings") or []
            if finding.get("code") == code and finding.get("test") == test_id]


@pytest.mark.parametrize("red", ("failed", "error"))
def test_the_ratchet_passes_a_listed_red_and_reports_it(red, project, sandbox):
    _listed(project)

    verdict = support.run_ratchet(project, sandbox, {LISTED: red, PASSING: "passed", OTHER: "skipped"})

    assert verdict.get("ok") is True, f"the ratchet refuses a listed red ({red}): {verdict}"
    assert _reports(verdict, LISTED, support.RESULT_FAILED), f"the listed red is not reported as failed: {verdict}"
    assert not verdict.get("findings"), f"the ratchet has findings for a covered run: {verdict}"


@pytest.mark.parametrize("red", ("failed", "error"))
def test_the_ratchet_refuses_a_red_the_list_does_not_cover(red, project, sandbox):
    _listed(project)

    verdict = support.run_ratchet(project, sandbox, {LISTED: "failed", OTHER: red})

    assert verdict.get("ok") is False, f"the ratchet passes a red the list does not cover: {verdict}"
    assert _coded(verdict, support.RED_NOT_ACCEPTED, OTHER), f"no {support.RED_NOT_ACCEPTED} for {OTHER}: {verdict}"
    assert not _coded(verdict, support.RED_NOT_ACCEPTED, LISTED), f"the listed red is refused: {verdict}"


def test_the_ratchet_refuses_a_listed_red_that_passes_naming_the_entry_to_remove(project, sandbox):
    _listed(project)

    verdict = support.run_ratchet(project, sandbox, {LISTED: "passed"})

    assert verdict.get("ok") is False, f"the ratchet passes a listed red that passes: {verdict}"
    found = [finding for finding in _coded(verdict, support.ACCEPTED_RED_PASSES, LISTED)
             if "remov" in support.text_of(finding).lower()]
    assert found, f"no {support.ACCEPTED_RED_PASSES} finding names the entry to remove: {verdict}"


def test_the_ratchet_refuses_an_entry_the_owner_did_not_add_naming_its_commit(project, sandbox):
    added = _listed(project, role="orchestrator")

    verdict = support.run_ratchet(project, sandbox, {LISTED: "failed"})

    assert verdict.get("ok") is False, f"the ratchet counts an entry the orchestrator added: {verdict}"
    found = [finding for finding in _coded(verdict, support.ACCEPTED_RED_REFUSED, LISTED)
             if added[:7] in support.text_of(finding)]
    assert found, f"no {support.ACCEPTED_RED_REFUSED} finding names the entry and its commit {added[:7]}: {verdict}"
    assert not _reports(verdict, LISTED, support.RESULT_FAILED), f"the refused entry covers its red: {verdict}"


def test_the_ratchet_reports_an_entry_whose_test_was_not_run_and_passes(project, sandbox):
    _listed(project)

    verdict = support.run_ratchet(project, sandbox, {PASSING: "passed"})

    assert verdict.get("ok") is True, f"the ratchet refuses for a listed test that was not run: {verdict}"
    assert _reports(verdict, LISTED, support.RESULT_NOT_RUN), f"the entry is not reported as not run: {verdict}"
