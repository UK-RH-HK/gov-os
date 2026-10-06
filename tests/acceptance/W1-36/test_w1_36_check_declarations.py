"""Tests for the check declarations (S5).

S5: Registers the skill-regression family check over its four skills and the
    audit-reproducibility family check (an audit report's cited commit, rows
    and evidence paths resolve), using the generic validators from W1-26
    [CAP-38.b].
"""
from w1_36_support import NORMALISED_FAMILIES, normalise_family


class TestSkillRegressionCheck:
    """S5: skill-regression family check declaration."""

    def test_at_least_one_declaration_exists(self, skill_regression_checks):
        assert len(skill_regression_checks) >= 1

    def test_each_has_required_fields(self, skill_regression_checks):
        for check in skill_regression_checks:
            for field in ("id", "family", "tier", "severity", "command"):
                assert field in check, \
                    f"{check['_path'].name} missing required field '{field}'"

    def test_family_normalises_to_skill_regression(self, skill_regression_checks):
        for check in skill_regression_checks:
            norm = normalise_family(check["family"])
            assert norm == "skill-regression", (
                f"{check['_path'].name}: family '{check['family']}' "
                f"normalises to '{norm}', expected 'skill-regression'"
            )

    def test_family_is_a_known_family(self, skill_regression_checks):
        for check in skill_regression_checks:
            norm = normalise_family(check["family"])
            assert norm in NORMALISED_FAMILIES, \
                f"'{norm}' is not one of the 17 known families (DEC-436)"

    def test_tier_is_g1(self, skill_regression_checks):
        for check in skill_regression_checks:
            assert check["tier"] == "G1", \
                f"{check['_path'].name}: tier must be G1"

    def test_command_is_non_empty(self, skill_regression_checks):
        for check in skill_regression_checks:
            assert isinstance(check["command"], str) and check["command"].strip(), \
                f"{check['_path'].name}: command must be a non-empty string"


class TestAuditReproducibilityCheck:
    """S5: audit-reproducibility family check declaration."""

    def test_at_least_one_declaration_exists(self, audit_repro_checks):
        assert len(audit_repro_checks) >= 1

    def test_each_has_required_fields(self, audit_repro_checks):
        for check in audit_repro_checks:
            for field in ("id", "family", "tier", "severity", "command"):
                assert field in check, \
                    f"{check['_path'].name} missing required field '{field}'"

    def test_family_normalises_to_audit_reproducibility(self, audit_repro_checks):
        for check in audit_repro_checks:
            norm = normalise_family(check["family"])
            assert norm == "audit-reproducibility", (
                f"{check['_path'].name}: family '{check['family']}' "
                f"normalises to '{norm}', expected 'audit-reproducibility'"
            )

    def test_family_is_a_known_family(self, audit_repro_checks):
        for check in audit_repro_checks:
            norm = normalise_family(check["family"])
            assert norm in NORMALISED_FAMILIES, \
                f"'{norm}' is not one of the 17 known families (DEC-436)"

    def test_tier_is_g1(self, audit_repro_checks):
        for check in audit_repro_checks:
            assert check["tier"] == "G1", \
                f"{check['_path'].name}: tier must be G1"

    def test_command_is_non_empty(self, audit_repro_checks):
        for check in audit_repro_checks:
            assert isinstance(check["command"], str) and check["command"].strip(), \
                f"{check['_path'].name}: command must be a non-empty string"
