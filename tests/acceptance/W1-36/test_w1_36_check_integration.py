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
    - RED (not green) on a project with no audit report.
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

    def test_red_when_no_audit_report(self, tmp_path, monkeypatch):
        """RED (not green) when the project has no audit report yet.

        The validator says 'unmeasured' and exits 1 (DEC-425); the runner
        treats that as RED for a hard-block check.
        """
        _ensure_pythonpath(monkeypatch)
        root = build_check_project(
            tmp_path / "project",
            check_decls=["audit-reproducibility.yaml"],
            skill_files=False,
        )
        result, _ = run_checks(root)
        status = _family_status(result, "audit reproducibility")
        assert status != "GREEN", (
            f"audit-reproducibility family is {status}, expected not GREEN "
            f"when the project has no audit report (unmeasured is never "
            f"green, DEC-425)"
        )
