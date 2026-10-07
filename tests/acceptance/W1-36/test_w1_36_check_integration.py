"""Integration tests: skill-regression and audit-reproducibility families
through ``run_checks`` on temporary projects (b, c).

(b) Skill-regression through ``gov check``:
    - GREEN when the four valid skills are present.
    - RED when one skill is broken (frontmatter removed).
    - RED when skills are missing (unmeasured, DEC-425).

(c) Audit-reproducibility through ``gov check``:
    - GREEN on a valid audit report under ``docs/audit/``.
    - RED on a report with a commit that does not resolve.
    - RED on a report with an unknown class.
    - RED on an OK row with no evidence (all ``-``).
    - RED on an evidence path absent at the cited commit.
    - YELLOW on a project with no audit report (DEC-447): "not applicable
      until the first audit", a warning, not red; does not make gov check
      fail; folder missing and folder-present-but-empty both YELLOW.
    - RED when one valid and one invalid report are present (DEC-447): the
      hard block holds once any report exists.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

from w1_36_support import (
    ALL_SKILL_RELS,
    CHECKS_DIR_REL,
    REPO_ROOT,
    _tmp_git,
    add_and_commit,
    build_check_project,
    head_sha,
)

sys.path.insert(0, str(REPO_ROOT / "src"))

from gov.check.runner import run_checks  # noqa: E402

_PACK_HEX = "a" * 64


def _family_status(result, family_name):
    families = result.get("families", {})
    entry = families.get(family_name)
    if isinstance(entry, dict):
        return entry.get("status")
    return entry


def _ensure_pythonpath(monkeypatch):
    """Ensure PYTHONPATH includes REPO_ROOT/src so subprocesses find gov."""
    src = str(REPO_ROOT / "src")
    old = os.environ.get("PYTHONPATH", "")
    if src not in old:
        monkeypatch.setenv("PYTHONPATH", src + (":" + old if old else ""))


# ── (b) Skill-regression through gov check ─────────────────────────────

class TestSkillRegressionGovCheck:
    """Skill-regression family through run_checks on a temporary project."""

    def test_green_with_valid_skills(self, tmp_path, monkeypatch):
        """GREEN when the four valid skills are present."""
        _ensure_pythonpath(monkeypatch)
        root = build_check_project(
            tmp_path / "project",
            check_decls=["skill-regression-b1.yaml"],
        )
        result, _ = run_checks(root)
        status = _family_status(result, "skill regression")
        assert status == "GREEN", (
            f"skill-regression family is {status}, expected GREEN "
            f"when the four valid skills are present"
        )

    def test_red_when_skill_broken(self, tmp_path, monkeypatch):
        """RED when one skill has its frontmatter removed."""
        _ensure_pythonpath(monkeypatch)
        root = build_check_project(
            tmp_path / "project",
            check_decls=["skill-regression-b1.yaml"],
        )
        broken = root / ALL_SKILL_RELS[0]
        broken.write_text("# Retrieval\n\nNo frontmatter here.\n",
                          encoding="utf-8")
        add_and_commit(root, "break a skill")

        result, _ = run_checks(root)
        status = _family_status(result, "skill regression")
        assert status == "RED", (
            f"skill-regression family is {status}, expected RED "
            f"when one skill is broken (frontmatter removed)"
        )

    def test_red_when_skills_missing(self, tmp_path, monkeypatch):
        """RED when the skills folder is missing (unmeasured, DEC-425)."""
        _ensure_pythonpath(monkeypatch)
        root = build_check_project(
            tmp_path / "project",
            check_decls=["skill-regression-b1.yaml"],
            skill_files=False,
        )
        result, _ = run_checks(root)
        status = _family_status(result, "skill regression")
        assert status == "RED", (
            f"skill-regression family is {status}, expected RED "
            f"when skills are missing (unmeasured is never green, DEC-425)"
        )


# ── (c) Audit-reproducibility through gov check ────────────────────────

def _valid_report(commit):
    return (
        f"---\nmilestone: test-milestone\ncommit: {commit}\n"
        f"pack_sha256: sha256:{_PACK_HEX}\n---\n"
        "# Audit Report\n\n"
        "| item | class | evidence |\n|---|---|---|\n"
        "| CAP-01 | OK | README.md |\n"
        "| DEC-001 | MISSING | - |\n"
    )


def _build_audit_project(tmp_path, monkeypatch, *, report_text=None,
                          skip_report=False):
    """Build a temp project for audit-reproducibility tests.

    Returns (root, initial_commit).  If *report_text* is given it is written
    under ``docs/audit/test/`` and committed.
    """
    _ensure_pythonpath(monkeypatch)
    root = build_check_project(
        tmp_path / "project",
        check_decls=["audit-reproducibility.yaml"],
        skill_files=False,
    )
    initial_commit = head_sha(root)

    if not skip_report and report_text is not None:
        report_dir = root / "docs" / "audit" / "test"
        report_dir.mkdir(parents=True, exist_ok=True)
        (report_dir / "report.md").write_text(report_text, encoding="utf-8")
        add_and_commit(root, "add audit report")

    return root, initial_commit


class TestAuditReproGovCheck:
    """Audit-reproducibility family through run_checks on a temporary project."""

    def test_green_with_valid_report(self, tmp_path, monkeypatch):
        """GREEN on a project holding a valid audit report."""
        _ensure_pythonpath(monkeypatch)
        root = build_check_project(
            tmp_path / "project",
            check_decls=["audit-reproducibility.yaml"],
            skill_files=False,
        )
        commit = head_sha(root)
        report = _valid_report(commit)
        report_dir = root / "docs" / "audit" / "test"
        report_dir.mkdir(parents=True, exist_ok=True)
        (report_dir / "report.md").write_text(report, encoding="utf-8")
        add_and_commit(root, "add valid audit report")

        result, _ = run_checks(root)
        status = _family_status(result, "audit reproducibility")
        assert status == "GREEN", (
            f"audit-reproducibility family is {status}, expected GREEN "
            f"on a valid audit report"
        )

    def test_red_when_commit_does_not_resolve(self, tmp_path, monkeypatch):
        """RED when the report cites a commit that does not resolve."""
        bad_commit = "deadbeef" * 5  # 40 hex chars, not in this repo
        root, _ = _build_audit_project(
            tmp_path, monkeypatch,
            report_text=(
                f"---\nmilestone: m1\ncommit: {bad_commit}\n"
                f"pack_sha256: sha256:{_PACK_HEX}\n---\n"
                "# Report\n\n| item | class | evidence |\n|---|---|---|\n"
                "| CAP-01 | OK | README.md |\n"
            ),
        )
        result, _ = run_checks(root)
        status = _family_status(result, "audit reproducibility")
        assert status == "RED", (
            f"audit-reproducibility family is {status}, expected RED "
            f"when the report cites a commit that does not resolve"
        )

    def test_red_when_class_unknown(self, tmp_path, monkeypatch):
        """RED when a row uses an unknown class."""
        root, commit = _build_audit_project(tmp_path, monkeypatch,
                                            skip_report=True)
        report = (
            f"---\nmilestone: m1\ncommit: {commit}\n"
            f"pack_sha256: sha256:{_PACK_HEX}\n---\n"
            "# Report\n\n| item | class | evidence |\n|---|---|---|\n"
            "| CAP-01 | INVALID_CLASS | README.md |\n"
        )
        report_dir = root / "docs" / "audit" / "test"
        report_dir.mkdir(parents=True, exist_ok=True)
        (report_dir / "report.md").write_text(report, encoding="utf-8")
        add_and_commit(root, "add report with unknown class")

        result, _ = run_checks(root)
        status = _family_status(result, "audit reproducibility")
        assert status == "RED", (
            f"audit-reproducibility family is {status}, expected RED "
            f"when a row uses an unknown class"
        )

    def test_red_when_ok_row_has_no_evidence(self, tmp_path, monkeypatch):
        """RED when an OK row has all-dash evidence."""
        root, commit = _build_audit_project(tmp_path, monkeypatch,
                                            skip_report=True)
        report = (
            f"---\nmilestone: m1\ncommit: {commit}\n"
            f"pack_sha256: sha256:{_PACK_HEX}\n---\n"
            "# Report\n\n| item | class | evidence |\n|---|---|---|\n"
            "| CAP-01 | OK | - |\n"
        )
        report_dir = root / "docs" / "audit" / "test"
        report_dir.mkdir(parents=True, exist_ok=True)
        (report_dir / "report.md").write_text(report, encoding="utf-8")
        add_and_commit(root, "add report with OK but no evidence")

        result, _ = run_checks(root)
        status = _family_status(result, "audit reproducibility")
        assert status == "RED", (
            f"audit-reproducibility family is {status}, expected RED "
            f"when an OK row cites no evidence (all dash)"
        )

    def test_red_when_evidence_path_absent(self, tmp_path, monkeypatch):
        """RED when an evidence path does not exist at the cited commit."""
        root, commit = _build_audit_project(tmp_path, monkeypatch,
                                            skip_report=True)
        report = (
            f"---\nmilestone: m1\ncommit: {commit}\n"
            f"pack_sha256: sha256:{_PACK_HEX}\n---\n"
            "# Report\n\n| item | class | evidence |\n|---|---|---|\n"
            "| CAP-01 | OK | nonexistent/file.txt |\n"
        )
        report_dir = root / "docs" / "audit" / "test"
        report_dir.mkdir(parents=True, exist_ok=True)
        (report_dir / "report.md").write_text(report, encoding="utf-8")
        add_and_commit(root, "add report with absent evidence path")

        result, _ = run_checks(root)
        status = _family_status(result, "audit reproducibility")
        assert status == "RED", (
            f"audit-reproducibility family is {status}, expected RED "
            f"when an evidence path does not exist at the cited commit"
        )

    def test_yellow_when_no_audit_report_folder_missing(self, tmp_path,
                                                        monkeypatch):
        """YELLOW when the reports folder does not exist (DEC-447).

        Revised after implementation: owner decision DEC-447 — before the
        first audit, the family is a warning (YELLOW), not red.
        """
        _ensure_pythonpath(monkeypatch)
        root = build_check_project(
            tmp_path / "project",
            check_decls=["audit-reproducibility.yaml"],
            skill_files=False,
        )
        result, has_hard_block_red = run_checks(root)
        status = _family_status(result, "audit reproducibility")
        assert status == "YELLOW", (
            f"audit-reproducibility family is {status}, expected YELLOW "
            f"when the project has no audit report (DEC-447)"
        )
        assert status != "GREEN", (
            f"audit-reproducibility family must never be GREEN when "
            f"there is no report"
        )
        assert status != "RED", (
            f"audit-reproducibility family is RED but DEC-447 says it "
            f"should be a warning before the first audit"
        )

    def test_yellow_when_no_audit_report_folder_empty(self, tmp_path,
                                                      monkeypatch):
        """YELLOW when the reports folder exists but is empty (DEC-447)."""
        _ensure_pythonpath(monkeypatch)
        root = build_check_project(
            tmp_path / "project",
            check_decls=["audit-reproducibility.yaml"],
            skill_files=False,
        )
        (root / "docs" / "audit").mkdir(parents=True, exist_ok=True)

        result, has_hard_block_red = run_checks(root)
        status = _family_status(result, "audit reproducibility")
        assert status == "YELLOW", (
            f"audit-reproducibility family is {status}, expected YELLOW "
            f"when the reports folder exists but has no report (DEC-447)"
        )

    def test_yellow_reason_says_not_applicable(self, tmp_path, monkeypatch):
        """The YELLOW reason says "not applicable until the first audit"."""
        _ensure_pythonpath(monkeypatch)
        root = build_check_project(
            tmp_path / "project",
            check_decls=["audit-reproducibility.yaml"],
            skill_files=False,
        )
        result, _ = run_checks(root)
        families = result.get("families", {})
        entry = families.get("audit reproducibility", {})
        reason = ""
        if isinstance(entry, dict):
            reason = entry.get("reason", "")
        assert "not applicable" in reason.lower(), (
            f"expected reason to contain 'not applicable', got: {reason!r}"
        )

    def test_yellow_alone_does_not_make_gov_check_fail(self, tmp_path,
                                                       monkeypatch):
        """A project with only the audit-reproducibility family YELLOW
        does not make ``gov check`` exit as failed (DEC-447)."""
        _ensure_pythonpath(monkeypatch)
        root = build_check_project(
            tmp_path / "project",
            check_decls=["audit-reproducibility.yaml"],
            skill_files=False,
        )
        _, has_hard_block_red = run_checks(root)
        assert not has_hard_block_red, (
            "YELLOW audit-reproducibility alone must not cause "
            "gov check to report a hard-block failure (DEC-447)"
        )

    def test_red_when_one_valid_and_one_invalid_report(self, tmp_path,
                                                       monkeypatch):
        """RED when the folder holds one valid and one invalid report (DEC-447).

        Once any report exists, the hard block holds: a valid report does
        not excuse a broken one.
        """
        _ensure_pythonpath(monkeypatch)
        root = build_check_project(
            tmp_path / "project",
            check_decls=["audit-reproducibility.yaml"],
            skill_files=False,
        )
        commit = head_sha(root)
        report_dir = root / "docs" / "audit" / "test"
        report_dir.mkdir(parents=True, exist_ok=True)
        (report_dir / "good.md").write_text(
            _valid_report(commit), encoding="utf-8")
        bad_commit = "deadbeef" * 5
        (report_dir / "bad.md").write_text(
            f"---\nmilestone: m1\ncommit: {bad_commit}\n"
            f"pack_sha256: sha256:{_PACK_HEX}\n---\n"
            "# Bad Report\n\n| item | class | evidence |\n|---|---|---|\n"
            "| CAP-01 | OK | README.md |\n",
            encoding="utf-8",
        )
        add_and_commit(root, "add one valid and one invalid report")

        result, has_hard_block_red = run_checks(root)
        status = _family_status(result, "audit reproducibility")
        assert status == "RED", (
            f"audit-reproducibility family is {status}, expected RED "
            f"when one valid and one invalid report are present (DEC-447)"
        )
        assert has_hard_block_red, (
            "gov check must exit as failed when the audit family is RED"
        )
