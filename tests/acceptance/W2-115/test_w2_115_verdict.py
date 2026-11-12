"""S11: READY is computed, not declared: from the reviewer's structured verdict per KPI line (the probe record's fenced
``verdict`` block, governance/project/briefs/JUDGEMENT.md).

A FULL ticket (KPI lines S1 "It works" and F1 "It does not work") with its probe record committed by the reviewer
(``Role: independent-auditor``). The close refuses only on a finding in scope, reachable in ordinary work, that fails
open or loses work (``FINDING_BLOCKS``); a malformed or incomplete verdict refuses (``VERDICT_MALFORMED``); a verdict
an orchestrator's commit wrote over the reviewer's is refused (``VERDICT_NOT_REVIEWER``).

Red on today's code: today's close reads no verdict block (it closes on all of them) and its record has no
``review``.
"""

import pytest

import w2_115_support as support

PROBE_REL = f"docs/probes/{support.TICKET}/PR-{support.TICKET}.md"
# The reviewer's commit carries its role and no Task trailer: today's probe gate refuses a reviewer's commit in the
# ticket's range (PROBE_INVALID), so the probe record stays outside it, as W1-30's reviewer commits it.
REVIEWER_TRAILERS = ("Role: independent-auditor",)
HARMLESS = [("F1", "out", "yes", "fails open"), ("F2", "in", "no", "loses work"), ("F3", "in", "yes", "other")]


def _full_project(make_project):
    files = {support.close_support.ticket_path(support.TICKET): support.close_support.ticket_text(
        support.TICKET, support.WBS, profile="FULL", allowed_paths=support.TICKET_PATHS, status="in_progress")}
    return make_project(files=files)


def _reviewed(make_project, sandbox, body, over=None):
    """The ticket's work, the reviewer's probe record with ``body``; ``over``, a body an orchestrator's commit
    writes over it; then the checkpoint and the close."""
    project = _full_project(make_project)
    probed = project.work({support.WIDGET: "# the widget, CHANGED\n"})
    project.write(PROBE_REL, support.probe_text(support.TICKET, body, probed))
    project._commit("the probe record", support.close_support.REVIEWER, REVIEWER_TRAILERS)
    if over is not None:
        project.write(PROBE_REL, support.probe_text(support.TICKET, over, probed))
        project._commit("the verdict, rewritten", support.close_support.ORCHESTRATOR,
                        support.close_support.ORCHESTRATOR["trailers"])
    project.ready(sandbox)
    return project, project.close(sandbox)


def test_a_complete_verdict_with_only_harmless_findings_is_ready(make_project, sandbox):
    """S11: a complete verdict per KPI line whose findings are out of scope, not ordinary work, or neither fail open
    nor lose work gives READY: the close passes and its record says READY and names the probe record."""
    body = support.verdict([("S1", "pass", HARMLESS), ("F1", "pass", [])])
    project, run = _reviewed(make_project, sandbox, body)
    support.passed(run)
    review = project.record().get("review")
    assert isinstance(review, dict) and review.get("verdict") == support.READY, f"review: {review!r}"
    assert review.get("record") == PROBE_REL, f"the review names another record: {review!r}"


@pytest.mark.parametrize("consequence", ["fails open", "loses work"])
def test_an_in_scope_ordinary_finding_that_fails_open_or_loses_work_refuses(make_project, sandbox, consequence):
    """S11: one finding in scope, reachable in ordinary work, that fails open (or loses work) refuses: FINDING_BLOCKS."""
    body = support.verdict([("S1", "fail", [("F1", "in", "yes", consequence)] + HARMLESS[1:]), ("F1", "pass", [])])
    project, run = _reviewed(make_project, sandbox, body)
    support.assert_refused(run, support.FINDING_BLOCKS)
    assert project.ticket_status() == "in_progress"


@pytest.mark.parametrize("body", [
    "{\"kpis\": [ not json",
    support.verdict([("S1", "pass", [])]),
    {"kpis": [{"kpi": "S1", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes"}]},
              {"kpi": "F1", "verdict": "pass", "findings": []}]},
    {"kpis": [{"kpi": "S1", "verdict": "maybe", "findings": []}, {"kpi": "F1", "verdict": "pass", "findings": []}]},
], ids=["not_json", "a_kpi_line_missing", "a_finding_without_consequence", "a_verdict_neither_pass_nor_fail"])
def test_a_malformed_or_incomplete_verdict_refuses(make_project, sandbox, body):
    """S11: a malformed or incomplete verdict refuses (fail closed): VERDICT_MALFORMED."""
    project, run = _reviewed(make_project, sandbox, body)
    support.assert_refused(run, support.VERDICT_MALFORMED)
    assert project.ticket_status() == "in_progress"


def test_a_verdict_the_lead_wrote_over_the_reviewer_s_is_refused(make_project, sandbox):
    """S11: the reviewer's verdict blocks; an orchestrator's later commit rewrites it to a harmless one: the close
    refuses with VERDICT_NOT_REVIEWER."""
    blocking = support.verdict([("S1", "fail", [("F1", "in", "yes", "fails open")]), ("F1", "pass", [])])
    harmless = support.verdict([("S1", "pass", HARMLESS), ("F1", "pass", [])])
    project, run = _reviewed(make_project, sandbox, blocking, over=harmless)
    support.assert_refused(run, support.VERDICT_NOT_REVIEWER)
    assert project.ticket_status() == "in_progress"
