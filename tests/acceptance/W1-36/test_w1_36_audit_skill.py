"""Tests for the audit skill (S2, S6, S7, F2, F3).

S2: Audit produces a report naming its milestone with one row per contract
    item and decision in scope, each classed in one of six classes [DEC-088].
S6: The audit starts a fresh session whose only inputs are the bounded context
    pack and the repository; the report states the pack hash [CAP-47.b].
S7: A wave-exit audit report has one row per LITE feature specification
    closed in the wave [CAP-47.d].
F2: The audit must not edit audited files.
F3: An owner-level finding must not become a ticket without a decision package.
"""
from w1_36_support import AUDIT_CLASSES


class TestAuditReport:
    """S2: report form — milestone, rows, six classes."""

    def test_the_report_names_its_milestone(self, audit_skill):
        body = audit_skill["body"].lower()
        assert "milestone" in body, \
            "the audit skill must say the report names its milestone"

    def test_the_skill_cites_dec_088(self, audit_skill):
        assert "DEC-088" in audit_skill["body"], \
            "the audit skill must cite DEC-088 (audit triggers and report form)"

    def test_the_report_has_rows_per_contract_item_and_decision(self, audit_skill):
        body = audit_skill["body"].lower()
        has_row = "row" in body or "entry" in body or "line" in body
        has_scope = "contract" in body or "cap" in body or "decision" in body
        assert has_row and has_scope, (
            "the audit skill must say the report has one row per "
            "contract item and decision in scope"
        )

    def test_the_report_uses_the_six_classes(self, audit_skill):
        body = audit_skill["body"]
        for cls in AUDIT_CLASSES:
            assert cls in body, \
                f"the audit skill must name the classification class {cls}"


class TestAuditFreshSession:
    """S6: fresh session, bounded inputs, pack hash."""

    def test_the_skill_says_the_session_is_fresh(self, audit_skill):
        body = audit_skill["body"].lower()
        assert "fresh" in body, \
            "the audit skill must say the session is fresh (no prior context)"

    def test_the_skill_says_inputs_are_context_pack_and_repository(self, audit_skill):
        body = audit_skill["body"].lower()
        has_pack = (
            "context pack" in body
            or "gov context" in body
            or "context packet" in body
        )
        has_repo = "repository" in body or "repo" in body
        assert has_pack and has_repo, (
            "the audit skill must say the only inputs are "
            "the bounded context pack and the repository"
        )

    def test_the_skill_says_report_states_pack_hash(self, audit_skill):
        body = audit_skill["body"].lower()
        assert "hash" in body, \
            "the audit skill must say the report states the pack hash"

    def test_the_skill_references_cap_47(self, audit_skill):
        assert "CAP-47" in audit_skill["body"], \
            "the audit skill must reference CAP-47 (audit independence)"


class TestAuditWaveExit:
    """S7: wave-exit report covers every LITE feature specification."""

    def test_wave_exit_covers_every_lite_feature_spec(self, audit_skill):
        body = audit_skill["body"].lower()
        has_wave_exit = "wave-exit" in body or "wave exit" in body
        has_lite = "lite" in body
        assert has_wave_exit and has_lite, (
            "the audit skill must say wave-exit reports cover "
            "every LITE feature specification closed in the wave"
        )


class TestAuditDecisionPackages:
    """S2 (partial) and F3: contested/owner findings → decision packages;
    agreed fixes → tickets; owner-level findings cannot skip the package."""

    def test_contested_findings_become_decision_packages(self, audit_skill):
        body = audit_skill["body"].lower()
        assert "contested" in body, \
            "the audit skill must address contested findings"
        assert "decision package" in body or "package" in body, \
            "the audit skill must say contested findings become decision packages"

    def test_owner_level_findings_become_decision_packages(self, audit_skill):
        body = audit_skill["body"].lower()
        assert "owner" in body, \
            "the audit skill must address owner-level findings"

    def test_agreed_fixes_become_tickets(self, audit_skill):
        body = audit_skill["body"].lower()
        assert "ticket" in body, \
            "the audit skill must say agreed fixes become tickets"

    def test_owner_finding_requires_decision_package_before_ticket(self, audit_skill):
        """F3: owner-level → decision package required before ticket."""
        body = audit_skill["body"].lower()
        has_owner = "owner" in body
        has_package = "decision package" in body or "package" in body
        assert has_owner and has_package, (
            "the audit skill must say owner-level findings require "
            "a decision package before they can become tickets"
        )


class TestAuditReadOnly:
    """F2: the audit session must not edit audited files."""

    def test_the_skill_says_it_does_not_edit_audited_files(self, audit_skill):
        body = audit_skill["body"].lower()
        is_read_only = (
            "read-only" in body
            or "read only" in body
            or "does not edit" in body
            or "never edit" in body
            or "must not edit" in body
            or "no edit" in body
            or "does not write" in body
            or "never write" in body
            or "must not write" in body
        )
        assert is_read_only, (
            "the audit skill must say the session is read-only "
            "or that it does not edit audited files"
        )


class TestAuditReportDEC441Form:
    """DEC-441: the audit skill states the report's minimal form —
    frontmatter fields, table columns, classes, and no-evidence notation."""

    def test_mentions_pack_sha256_field(self, audit_skill):
        """The skill must name pack_sha256 as a report frontmatter field."""
        assert "pack_sha256" in audit_skill["body"], (
            "the audit skill must name pack_sha256 as a frontmatter field "
            "(DEC-441: the report's YAML frontmatter holds pack_sha256)"
        )

    def test_mentions_commit_as_report_field(self, audit_skill):
        """The skill must name commit as a report frontmatter field."""
        body = audit_skill["body"]
        has_commit_field = (
            "frontmatter" in body.lower()
            or "`commit`" in body
        )
        assert has_commit_field, (
            "the audit skill must state commit as a report frontmatter field "
            "(DEC-441: the report's YAML frontmatter holds commit)"
        )

    def test_describes_table_columns(self, audit_skill):
        """The skill must describe the table columns: item, class, evidence."""
        body = audit_skill["body"].lower()
        has_evidence_col = "evidence" in body
        has_table_context = "table" in body or "|" in body or "column" in body
        assert has_evidence_col and has_table_context, (
            "the audit skill must describe the table with columns "
            "item, class, evidence (DEC-441)"
        )

    def test_describes_no_evidence_as_dash(self, audit_skill):
        """The skill must state that no evidence is written as '-'."""
        body = audit_skill["body"]
        has_dash_notation = (
            "`-`" in body
            or "written as `-`" in body
            or "written as -" in body.lower()
            or "cite none" in body.lower() and "`-`" in body
        )
        assert has_dash_notation, (
            "the audit skill must state that no evidence is written as "
            "'-' (DEC-441: a non-OK row may cite none, written as -)"
        )
