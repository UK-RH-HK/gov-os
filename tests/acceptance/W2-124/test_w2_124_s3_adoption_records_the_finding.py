"""S3 and F2: adoption never fails for a missing embedder; stage A6 finishes and records a named finding.

Ticket KPI S3: a planted adoption run with the embedder stub unavailable: stage A6's record shows it finished, and both that
record and the adoption report hold one finding that names the semantic store, the reason and the rebuild command; the run
does not exit with an error. F2: an adoption that fails, or reports success without the finding, is the failure.

Interface: the A6 record (as committed) and the stage's ``gov adopt --lite --stage A6 --json`` result each hold
``findings: [{code: SEMANTIC_NOT_RECREATED, store: semantic, reason, command: "gov rebuild"}]``.
"""

from __future__ import annotations

import w2_124_support as support

CODE = "SEMANTIC_NOT_RECREATED"


def _report_findings(last):
    findings = last.result.get("findings")
    assert isinstance(findings, list), f"the adoption report holds no findings list\n{last.describe()}"
    return findings


def _record(project):
    text = support.head_file(project, support.A6_RECORD)
    assert text is not None, f"{support.A6_RECORD} is not committed"
    return support.frontmatter(text)


def _assert_one_named_finding(findings, where):
    named = [f for f in findings if isinstance(f, dict) and f.get("code") == CODE]
    assert len(named) == 1, f"{where}: expected one {CODE} finding, found {len(named)} in {findings}"
    finding = named[0]
    assert finding.get("store") == "semantic", f"{where}: the finding's store is {finding.get('store')!r}"
    assert isinstance(finding.get("reason"), str) and finding["reason"].strip(), f"{where}: the finding has no reason"
    assert finding.get("command") == "gov rebuild", f"{where}: the finding's command is {finding.get('command')!r}"
    return finding


def test_s3_stage_a6_finishes_without_an_error_with_the_embedder_unavailable(runs):
    adoption, last, project = runs.adoption("s3-dead", embedder="dead")
    assert last.returncode == 0 and last.envelope().get("ok") is True, \
        f"the adoption did not run through A6 without an error\n{last.describe()}"
    assert "INDEX_REFRESH_FAILED" not in last.stdout + last.stderr, f"A6 failed its index refresh\n{last.describe()}"
    assert adoption.runs["A6"].result.get("stage") == "A6"
    assert _record(project).get("status") == "done", f"the A6 record does not show it finished: {_record(project)}"


def test_s3_the_adoption_report_holds_the_named_finding(runs):
    _, last, _ = runs.adoption("s3-dead", embedder="dead")
    _assert_one_named_finding(_report_findings(last), "the adoption report")


def test_s3_the_committed_a6_record_holds_the_named_finding(runs):
    _, _, project = runs.adoption("s3-dead", embedder="dead")
    findings = _record(project).get("findings")
    assert isinstance(findings, list), f"the committed A6 record holds no findings list: {_record(project)}"
    _assert_one_named_finding(findings, "the committed A6 record")
    assert support.git(project, "status", "--porcelain").strip() == "", "A6 left the tree dirty after its commits"


def test_s3_record_and_report_give_the_same_finding(runs):
    _, last, project = runs.adoption("s3-dead", embedder="dead")
    in_report = _assert_one_named_finding(_report_findings(last), "the adoption report")
    in_record = _assert_one_named_finding(_record(project).get("findings") or [], "the committed A6 record")
    assert in_report == in_record, f"the report's finding {in_report} differs from the record's {in_record}"


def test_s3_a_healthy_embedder_adoption_holds_no_such_finding(runs):
    adoption, last, project = runs.adoption("s3-healthy", embedder="healthy")
    assert last.returncode == 0 and last.envelope().get("ok") is True, f"the control adoption failed\n{last.describe()}"
    in_report = [f for f in (last.result.get("findings") or []) if isinstance(f, dict) and f.get("code") == CODE]
    in_record = [f for f in (_record(project).get("findings") or []) if isinstance(f, dict) and f.get("code") == CODE]
    assert not in_report and not in_record, f"a healthy adoption reports {CODE}: {in_report} {in_record}"


# ---- F2 ---------------------------------------------------------------------------------------------------------------

def test_f2_an_unavailable_embedder_never_fails_the_adoption_nor_hides_the_finding(runs):
    """The failure line: an error exit, or a record or report without the finding."""
    adoption, last, project = runs.adoption("s3-dead", embedder="dead")
    failed = {stage: run.returncode for stage, run in adoption.runs.items() if run.returncode != 0}
    assert not failed, f"stages exited with an error: {failed}\n{last.describe()}"
    assert [stage for stage in support.STAGES if stage in adoption.runs] == list(support.STAGES), \
        f"the adoption did not run every stage to A6: {sorted(adoption.runs)}"
    report = [f for f in (last.result.get("findings") or []) if isinstance(f, dict) and f.get("code") == CODE]
    record = [f for f in (_record(project).get("findings") or []) if isinstance(f, dict) and f.get("code") == CODE]
    assert report, f"the adoption reports success without the {CODE} finding\n{last.describe()}"
    assert record, f"the A6 record has no {CODE} finding: {_record(project)}"
