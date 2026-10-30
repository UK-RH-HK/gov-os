"""KPI success line 2 [F-M13, W2-M301, W2-M309, W2-M310, W2-L243]: core-schema reads
``docs/audit/wave-1/W1-43-wave-1-exit-audit.md`` and the exit report as valid, and is green on this repository.

The W1-43 report is read as it was committed (it lies outside the ticket's paths). The cases that run in this
worktree's root only read; the one in a temporary project copies the report as its one named file.
"""

from __future__ import annotations

import pytest

import w2_02_support as support

W1_43_REPORT = "docs/audit/wave-1/W1-43-wave-1-exit-audit.md"
EXIT_REPORT = "docs/plan/wave-1-exit/EXIT-REPORT.md"
A5_VERDICT = "docs/adoption/adoption-path-map-verdict.md"


@pytest.fixture(scope="module")
def here(tmp_path_factory):
    """``(exit code, findings)`` of core-schema in this worktree's root."""
    home = tmp_path_factory.mktemp("w2-02-home")
    return support.run_core_schema(support.REPO_ROOT, home)


def _naming(findings, rel):
    return [finding for finding in findings if finding.get("path") == rel or rel in str(finding.get("message", ""))]


def test_core_schema_reads_the_w1_43_exit_audit_report_as_valid_here(here):
    """No finding names the report. Red today: ``SCHEMA_INVALID_TYPE`` ('type' field is missing)."""
    _, findings = here
    found = _naming(findings, W1_43_REPORT)
    assert not found, f"core-schema names the W1-43 exit audit report: {found}"


def test_core_schema_reads_the_w1_43_report_as_valid_in_a_project_of_its_own(tmp_path):
    """The same report, copied by name to its path in a temporary project with the kernel's schemas: no finding.
    Red today: ``SCHEMA_INVALID_TYPE``."""
    project = support.Project(tmp_path)
    project.kernel_schemas()
    project.write(W1_43_REPORT, (support.REPO_ROOT / W1_43_REPORT).read_text(encoding="utf-8"))
    code, findings = project.core_schema()
    assert not support.about(findings, W1_43_REPORT), f"the W1-43 report is a finding: {findings}"
    assert code == 0


def test_core_schema_reads_the_wave_1_exit_report_as_valid_here(here):
    """No finding names the exit report. Passes today (the report has no frontmatter); held so it stays."""
    _, findings = here
    found = _naming(findings, EXIT_REPORT)
    assert not found, f"core-schema names the exit report: {found}"


def test_the_a5_adoption_verdict_still_validates_here(here):
    """W2-M317: the A5 verdict, moved unchanged to ``docs/adoption/`` (DEC-626), stays valid. Passes today."""
    _, findings = here
    found = _naming(findings, A5_VERDICT)
    assert not found, f"core-schema names the A5 adoption verdict: {found}"


def test_core_schema_is_green_on_this_repository(here):
    """Exit code 0 and no finding at all. Red today: exit 1 with one finding (the W1-43 report)."""
    code, findings = here
    assert findings == [], f"core-schema has {len(findings)} findings on this repository: {findings}"
    assert code == 0, f"core-schema exits {code} on this repository"
