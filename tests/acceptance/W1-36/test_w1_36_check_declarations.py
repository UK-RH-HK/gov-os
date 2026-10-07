"""Tests for the check declarations (S5).

S5: Registers the skill-regression family check over its four skills and the
    audit-reproducibility family check (an audit report's cited commit, rows
    and evidence paths resolve), using the generic validators from W1-26
    [CAP-38.b].

Command validation (DEC-425, DEC-439): no fallback that can succeed without
the generic validator.
"""
from w1_36_support import NORMALISED_FAMILIES, normalise_family

_BYPASS_PATTERNS = ("if ", "test ", "importlib", "find_spec", "which ")


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


class TestSkillRegressionCommandValidation:
    """Command validation (DEC-425, DEC-439): the skill-regression command
    calls the W1-26 generic validator with no fallback."""

    def test_no_or_fallback_in_command(self, skill_regression_checks):
        for check in skill_regression_checks:
            assert "||" not in check["command"], (
                f"{check['_path'].name}: command has '||' fallback — "
                f"a check that can succeed without measuring is not merged (DEC-425)"
            )

    def test_no_conditional_bypass_in_command(self, skill_regression_checks):
        for check in skill_regression_checks:
            cmd = check["command"]
            for pat in _BYPASS_PATTERNS:
                assert pat not in cmd, (
                    f"{check['_path'].name}: command contains '{pat.strip()}' "
                    f"which can bypass the validator (DEC-439)"
                )

    def test_command_calls_skill_validator(self, skill_regression_checks):
        for check in skill_regression_checks:
            assert "gov.check.skill_validator" in check["command"], (
                f"{check['_path'].name}: command must call "
                f"gov.check.skill_validator (the W1-26 generic validator)"
            )


class TestAuditReproNotApplicableField:
    """DEC-447: the audit-reproducibility declaration carries
    ``allows-not-applicable: "true"``."""

    def test_allows_not_applicable_is_present(self, audit_repro_checks):
        for check in audit_repro_checks:
            assert "allows-not-applicable" in check, (
                f"{check['_path'].name} must carry "
                f"allows-not-applicable: \"true\" (DEC-447)"
            )

    def test_allows_not_applicable_value_is_true(self, audit_repro_checks):
        for check in audit_repro_checks:
            val = check.get("allows-not-applicable")
            assert val == "true", (
                f"{check['_path'].name}: allows-not-applicable is "
                f"{val!r}, expected \"true\" (DEC-447)"
            )

    def test_severity_stays_hard_block(self, audit_repro_checks):
        """The field does not change the severity: still hard-block."""
        for check in audit_repro_checks:
            assert check.get("severity") == "hard-block", (
                f"{check['_path'].name}: severity is "
                f"{check.get('severity')!r}, expected 'hard-block' "
                f"(DEC-447: a hard block once a report exists)"
            )


class TestSkillRegressionNotApplicableAbsent:
    """DEC-447: no other declaration (skill-regression) carries the field."""

    def test_skill_regression_has_no_allows_not_applicable(
            self, skill_regression_checks):
        for check in skill_regression_checks:
            assert "allows-not-applicable" not in check, (
                f"{check['_path'].name} must NOT carry "
                f"allows-not-applicable — a skill check never "
                f"becomes 'not applicable' (DEC-447)"
            )


class TestAuditReproCommandValidation:
    """Command validation (DEC-425, DEC-439): the audit-reproducibility command
    calls the W1-26 generic validator with no fallback."""

    def test_no_or_fallback_in_command(self, audit_repro_checks):
        for check in audit_repro_checks:
            assert "||" not in check["command"], (
                f"{check['_path'].name}: command has '||' fallback — "
                f"a check that can succeed without measuring is not merged (DEC-425)"
            )

    def test_no_conditional_bypass_in_command(self, audit_repro_checks):
        for check in audit_repro_checks:
            cmd = check["command"]
            for pat in _BYPASS_PATTERNS:
                assert pat not in cmd, (
                    f"{check['_path'].name}: command contains '{pat.strip()}' "
                    f"which can bypass the validator (DEC-439)"
                )

    def test_command_calls_audit_validator(self, audit_repro_checks):
        for check in audit_repro_checks:
            assert "gov.check.audit_validator" in check["command"], (
                f"{check['_path'].name}: command must call "
                f"gov.check.audit_validator (the W1-26 generic validator)"
            )
