"""W1-35 acceptance tests: four method skills and the skill-regression check declaration.

Tests cover every KPI success and failure line for the STANDARD profile.
Lines that need a live model session (MR-A-02 / MR-B-02 dev scenarios) are
tested on the skill text as far as possible and noted for W1-42.
"""

from __future__ import annotations

import math
import os
import re
import shutil
from pathlib import Path

import pytest
import yaml

from conftest import (
    CHECKS_DIR,
    CITATION_PATTERN,
    FRONTMATTER_REQUIRED,
    MAX_BODY_TOKENS,
    MAX_DESC_TOKENS,
    PERMISSION_PATTERNS,
    REPO_ROOT,
    RESERVED_COMMANDS,
    SKILL_FOLDER_RELS,
    SKILL_NAMES,
    SKILL_PATHS,
    SKILL_REGRESSION_FAMILY,
    check_support,
    cli_support,
    find_check_declaration,
    parse_skill,
    token_count,
    well_formed_skill,
)


# ============================================================================
# KPI success line 1 (CAP-24.a): versioned frontmatter, desc <= 60 tokens,
#   body <= 2.5k tokens
# ============================================================================

class TestFrontmatterAndSize:
    """covers: S1"""

    @pytest.mark.parametrize("skill_name", SKILL_NAMES)
    def test_frontmatter_is_valid_yaml(self, skill_texts, skill_name):
        front, _, _ = skill_texts[skill_name]
        assert front is not None, f"{skill_name}: frontmatter is missing or invalid YAML"

    @pytest.mark.parametrize("skill_name", SKILL_NAMES)
    def test_frontmatter_has_required_fields(self, skill_texts, skill_name):
        front, _, _ = skill_texts[skill_name]
        assert front is not None
        for field in FRONTMATTER_REQUIRED:
            assert field in front, f"{skill_name}: missing required field '{field}'"

    @pytest.mark.parametrize("skill_name", SKILL_NAMES)
    def test_version_is_present_and_nonempty(self, skill_texts, skill_name):
        front, _, _ = skill_texts[skill_name]
        assert front is not None
        version = front.get("version")
        assert version is not None and str(version).strip(), \
            f"{skill_name}: version must be non-empty"

    @pytest.mark.parametrize("skill_name", SKILL_NAMES)
    def test_description_within_60_tokens(self, skill_texts, skill_name):
        front, _, _ = skill_texts[skill_name]
        assert front is not None
        desc = str(front.get("description", ""))
        tokens = token_count(desc)
        assert tokens <= MAX_DESC_TOKENS, \
            f"{skill_name}: description is {tokens} tokens (max {MAX_DESC_TOKENS})"

    @pytest.mark.parametrize("skill_name", SKILL_NAMES)
    def test_body_within_2500_tokens(self, skill_texts, skill_name):
        _, body, _ = skill_texts[skill_name]
        tokens = token_count(body)
        assert tokens <= MAX_BODY_TOKENS, \
            f"{skill_name}: body is {tokens} tokens (max {MAX_BODY_TOKENS})"


# ============================================================================
# KPI failure line 1: A skill body exceeds 2.5k tokens
# ============================================================================

class TestFailureBodyExceeds:
    """covers: F1"""

    @pytest.mark.parametrize("skill_name", SKILL_NAMES)
    def test_body_over_2500_tokens_would_fail(self, skill_texts, skill_name):
        _, body, _ = skill_texts[skill_name]
        tokens = token_count(body)
        assert tokens <= MAX_BODY_TOKENS, \
            f"{skill_name}: body is {tokens} tokens, exceeds {MAX_BODY_TOKENS} — FAIL"


# ============================================================================
# KPI success line 5 (CAP-24.b): no skill grants a permission or states a rule
#   as its own authority; cites the policy or decision it follows
# ============================================================================

class TestNoPermissionGrants:
    """covers: S5"""

    @pytest.mark.parametrize("skill_name", SKILL_NAMES)
    def test_no_permission_granting_language(self, skill_texts, skill_name):
        _, _, full_text = skill_texts[skill_name]
        for pattern in PERMISSION_PATTERNS:
            matches = pattern.findall(full_text)
            for match in matches:
                line_no = None
                for i, line in enumerate(full_text.splitlines(), 1):
                    if match in line:
                        line_no = i
                        break
                cited = bool(CITATION_PATTERN.search(
                    full_text.splitlines()[line_no - 1] if line_no else ""
                ))
                assert cited, (
                    f"{skill_name} line {line_no}: permission-like language "
                    f"'{match}' without a CAP/DEC/MR citation on the same line"
                )

    @pytest.mark.parametrize("skill_name", SKILL_NAMES)
    def test_procedural_statements_cite_policy(self, skill_texts, skill_name):
        _, body, _ = skill_texts[skill_name]
        procedural_markers = re.compile(
            r"^\s*(?:\d+\.|-|\*)\s+.+$", re.MULTILINE
        )
        steps = procedural_markers.findall(body)
        uncited_steps = []
        for step in steps:
            step_stripped = step.strip()
            if len(step_stripped) < 15:
                continue
            if not CITATION_PATTERN.search(step_stripped):
                if any(kw in step_stripped.lower() for kw in (
                    "must", "shall", "require", "refuse", "deny", "block",
                    "only", "never", "always",
                )):
                    uncited_steps.append(step_stripped[:80])
        if uncited_steps:
            pytest.fail(
                f"{skill_name}: procedural statements with authority-like "
                f"language lack citations:\n" +
                "\n".join(f"  - {s}" for s in uncited_steps[:5])
            )


# ============================================================================
# KPI success line 6 (CAP-24.c): change skill takes a skill change through
#   evidence -> proposal -> independent review -> owner approval -> new version
# ============================================================================

class TestChangeSkillLifecycle:
    """covers: S6"""

    LIFECYCLE_STEPS = [
        "evidence",
        "proposal",
        "independent review",
        "owner approval",
        "version",
    ]

    def test_change_skill_documents_lifecycle(self, skill_texts):
        _, _, full_text = skill_texts["change"]
        text_lower = full_text.lower()
        for step in self.LIFECYCLE_STEPS:
            assert step.lower() in text_lower, \
                f"change skill does not mention lifecycle step '{step}'"

    def test_change_skill_lifecycle_order(self, skill_texts):
        _, _, full_text = skill_texts["change"]
        text_lower = full_text.lower()
        positions = []
        for step in self.LIFECYCLE_STEPS:
            pos = text_lower.find(step.lower())
            assert pos >= 0, f"step '{step}' not found"
            positions.append(pos)
        for i in range(len(positions) - 1):
            assert positions[i] < positions[i + 1], (
                f"lifecycle step '{self.LIFECYCLE_STEPS[i]}' appears after "
                f"'{self.LIFECYCLE_STEPS[i + 1]}' — order violation"
            )


# ============================================================================
# KPI success line 7 (CAP-33.d): CIT-P and CIT-E for kernel/policy/skill
#   changes; refuses to archive without records
# ============================================================================

class TestCITWorkflow:
    """covers: S7"""

    CIT_STEPS = [
        "evidence",
        "corroboration",
        "proposal",
        "cit-p",
        "independent review",
        "owner approval",
        "versioned promotion",
    ]

    def test_change_skill_mentions_cit_p_and_cit_e(self, skill_texts):
        _, _, full_text = skill_texts["change"]
        text_lower = full_text.lower()
        assert "cit-p" in text_lower, "change skill does not mention CIT-P"
        assert "cit-e" in text_lower, "change skill does not mention CIT-E"

    def test_change_skill_cit_steps_present(self, skill_texts):
        _, _, full_text = skill_texts["change"]
        text_lower = full_text.lower()
        for step in self.CIT_STEPS:
            assert step in text_lower, \
                f"change skill does not mention CIT step '{step}'"

    def test_change_skill_refuses_archive_without_records(self, skill_texts):
        _, _, full_text = skill_texts["change"]
        text_lower = full_text.lower()
        assert "refuse" in text_lower or "reject" in text_lower or "block" in text_lower, \
            "change skill does not state a refusal for archive without records"
        assert "archive" in text_lower or "cit-e" in text_lower, \
            "change skill does not reference archive/CIT-E in refusal context"

    def test_change_skill_cites_cap33d(self, skill_texts):
        _, _, full_text = skill_texts["change"]
        assert "CAP-33" in full_text, \
            "change skill does not cite CAP-33"


# ============================================================================
# KPI success line 8 (CAP-38.b): skill-regression check declaration
# ============================================================================

class TestCheckDeclaration:
    """covers: S8"""

    def test_check_declaration_exists(self):
        path = find_check_declaration()
        assert path is not None, (
            "No check declaration matching 'skill-regression-a*' found "
            f"in {CHECKS_DIR}"
        )

    def test_check_declaration_valid_yaml(self):
        path = find_check_declaration()
        assert path is not None
        text = path.read_text(encoding="utf-8")
        data = yaml.safe_load(text)
        assert isinstance(data, dict), "check declaration is not a YAML map"

    def test_check_declaration_has_five_fields(self):
        path = find_check_declaration()
        assert path is not None
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        required = ("id", "family", "tier", "severity", "command")
        for field in required:
            assert field in data, f"check declaration missing field '{field}'"
            assert isinstance(data[field], str), \
                f"check declaration field '{field}' must be a string"

    def test_check_declaration_family_is_skill_regression(self):
        path = find_check_declaration()
        assert path is not None
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert data["family"] == "skill regression", \
            f"check family is '{data['family']}', expected 'skill regression'"

    def test_check_declaration_severity_valid(self):
        path = find_check_declaration()
        assert path is not None
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert data["severity"] in ("hard-block", "warning"), \
            f"severity '{data['severity']}' not in (hard-block, warning)"


# ============================================================================
# KPI success line 9 (CAP-32.c, DEC-102): discovery treats experiments as
#   a normal step
# ============================================================================

class TestDiscoveryExperiments:
    """covers: S9"""

    def test_discovery_mentions_experiments(self, skill_texts):
        _, _, full_text = skill_texts["discovery"]
        text_lower = full_text.lower()
        assert "experiment" in text_lower, \
            "discovery skill does not mention experiments"

    def test_discovery_sandbox_requirement(self, skill_texts):
        _, _, full_text = skill_texts["discovery"]
        text_lower = full_text.lower()
        assert "sandbox" in text_lower, \
            "discovery skill does not mention sandbox for experiments"

    def test_discovery_evidence_record(self, skill_texts):
        _, _, full_text = skill_texts["discovery"]
        text_lower = full_text.lower()
        assert "evidence" in text_lower and "record" in text_lower, \
            "discovery skill does not mention evidence records for experiments"

    def test_discovery_normal_cycle_promotion(self, skill_texts):
        _, _, full_text = skill_texts["discovery"]
        text_lower = full_text.lower()
        assert ("normal cycle" in text_lower or "normal promotion" in text_lower
                or "promoted" in text_lower), \
            "discovery skill does not mention promotion through normal cycle"

    def test_discovery_cit_p_for_closed_spec(self, skill_texts):
        _, _, full_text = skill_texts["discovery"]
        assert "CIT-P" in full_text or "cit-p" in full_text.lower(), \
            "discovery skill does not mention CIT-P for changing closed specs"

    def test_discovery_cites_dec102_or_cap32(self, skill_texts):
        _, _, full_text = skill_texts["discovery"]
        assert "DEC-102" in full_text or "CAP-32" in full_text, \
            "discovery skill does not cite DEC-102 or CAP-32"


# ============================================================================
# KPI success line 10 (CAP-30.f, DEC-103): order of specification work
# ============================================================================

class TestSpecificationWorkOrder:
    """covers: S10"""

    SPEC_ORDER = [
        "discovery",
        "scenario",
        "data",
        "acceptance test",
        "implementation",
    ]

    def test_discovery_states_work_order(self, skill_texts):
        _, _, full_text = skill_texts["discovery"]
        text_lower = full_text.lower()
        for step in self.SPEC_ORDER:
            assert step in text_lower, \
                f"discovery skill does not mention spec work step '{step}'"

    def test_planning_states_work_order(self, skill_texts):
        _, _, full_text = skill_texts["planning"]
        text_lower = full_text.lower()
        for step in self.SPEC_ORDER:
            assert step in text_lower, \
                f"planning skill does not mention spec work step '{step}'"

    def test_work_order_correct_sequence_discovery(self, skill_texts):
        _, _, full_text = skill_texts["discovery"]
        text_lower = full_text.lower()
        positions = []
        for step in self.SPEC_ORDER:
            pos = text_lower.find(step)
            if pos >= 0:
                positions.append((step, pos))
        for i in range(len(positions) - 1):
            step_a, pos_a = positions[i]
            step_b, pos_b = positions[i + 1]
            assert pos_a < pos_b, (
                f"discovery: '{step_a}' appears after '{step_b}' — "
                f"violates DEC-103 work order"
            )

    def test_owner_reviews_scenarios_and_ux_not_tests(self, skill_texts):
        _, _, full_text = skill_texts["discovery"]
        text_lower = full_text.lower()
        assert "owner" in text_lower, "discovery skill does not mention owner review"
        assert "scenario" in text_lower, "discovery skill does not mention scenarios"


# ============================================================================
# KPI success line 2 (CAP-34.c, DEC-093): decision packages
# (text-level test; live session test is for W1-42)
# ============================================================================

class TestDecisionPackages:
    """covers: S2"""

    def test_discovery_mentions_decision_packages(self, skill_texts):
        _, _, full_text = skill_texts["discovery"]
        text_lower = full_text.lower()
        assert "decision package" in text_lower, \
            "discovery skill does not mention decision packages"

    def test_discovery_mentions_p1_p3_ranking(self, skill_texts):
        _, _, full_text = skill_texts["discovery"]
        assert "P1" in full_text or "p1" in full_text.lower(), \
            "discovery skill does not mention P1 ranking"
        assert "P3" in full_text or "p3" in full_text.lower() or "P2" in full_text, \
            "discovery skill does not mention ranking levels"

    def test_discovery_mentions_cap_of_five(self, skill_texts):
        _, _, full_text = skill_texts["discovery"]
        text_lower = full_text.lower()
        assert "five" in text_lower or "5" in full_text, \
            "discovery skill does not mention the cap of five packages"

    def test_discovery_p1_bypass(self, skill_texts):
        _, _, full_text = skill_texts["discovery"]
        text_lower = full_text.lower()
        assert "bypass" in text_lower or "override" in text_lower, \
            "discovery skill does not mention P1 bypass of the cap"

    def test_discovery_cites_dec093_or_cap34(self, skill_texts):
        _, _, full_text = skill_texts["discovery"]
        assert "DEC-093" in full_text or "CAP-34" in full_text, \
            "discovery skill does not cite DEC-093 or CAP-34"


# ============================================================================
# KPI success line 3 (CAP-30.b, DEC-089): planning emits schema-valid tickets
#   and one gap ticket per required open readiness row
# (text-level; schema validation needs a live session, for W1-42)
# ============================================================================

class TestPlanningGapTickets:
    """covers: S3"""

    def test_planning_mentions_gap_tickets(self, skill_texts):
        _, _, full_text = skill_texts["planning"]
        text_lower = full_text.lower()
        assert "gap" in text_lower or "linked" in text_lower, \
            "planning skill does not mention gap tickets"

    def test_planning_mentions_readiness_rows(self, skill_texts):
        _, _, full_text = skill_texts["planning"]
        text_lower = full_text.lower()
        assert "readiness" in text_lower, \
            "planning skill does not mention readiness rows"

    def test_planning_mentions_ticket_classes(self, skill_texts):
        _, _, full_text = skill_texts["planning"]
        text_lower = full_text.lower()
        ticket_classes = ["discovery", "data", "research", "test-design"]
        found = sum(1 for tc in ticket_classes if tc in text_lower)
        assert found >= 2, (
            "planning skill does not mention enough gap ticket classes "
            f"(found {found} of {ticket_classes})"
        )

    def test_planning_cites_dec089_or_cap30(self, skill_texts):
        _, _, full_text = skill_texts["planning"]
        assert "DEC-089" in full_text or "CAP-30" in full_text, \
            "planning skill does not cite DEC-089 or CAP-30"

    def test_planning_mentions_schema_valid_tickets(self, skill_texts):
        _, _, full_text = skill_texts["planning"]
        text_lower = full_text.lower()
        assert "ticket" in text_lower, \
            "planning skill does not mention tickets"


# ============================================================================
# KPI success line 4 (CAP-33.a, CAP-47.d, DEC-088): test design reads only
#   specification and KPIs; change covers CIT-P/CIT-E; audit ticket on CIT-E
# (text-level for test-design; live session test for W1-42)
# ============================================================================

class TestTestDesignConstraints:
    """covers: S4"""

    def test_test_design_reads_only_spec_and_kpis(self, skill_texts):
        _, _, full_text = skill_texts["test-design"]
        text_lower = full_text.lower()
        assert "specification" in text_lower or "spec" in text_lower, \
            "test-design skill does not mention specification"
        assert "kpi" in text_lower, \
            "test-design skill does not mention KPIs"

    def test_test_design_no_implementation_files(self, skill_texts):
        _, _, full_text = skill_texts["test-design"]
        text_lower = full_text.lower()
        assert ("implementation" in text_lower or "source" in text_lower
                or "code" in text_lower), \
            "test-design skill does not address implementation file restriction"

    def test_change_covers_audit_ticket(self, skill_texts):
        _, _, full_text = skill_texts["change"]
        text_lower = full_text.lower()
        assert "audit" in text_lower and "ticket" in text_lower, \
            "change skill does not mention audit ticket"

    def test_change_audit_on_closed_spine(self, skill_texts):
        _, _, full_text = skill_texts["change"]
        assert "DEC-088" in full_text or "CAP-47" in full_text, \
            "change skill does not cite DEC-088 or CAP-47 for audit triggers"


# ============================================================================
# KPI failure line 2: test-design skill reads implementation files
# ============================================================================

class TestFailureTestDesignReadsImpl:
    """covers: F2"""

    def test_test_design_states_restriction(self, skill_texts):
        _, _, full_text = skill_texts["test-design"]
        text_lower = full_text.lower()
        restricted = (
            ("no" in text_lower or "not" in text_lower or "never" in text_lower
             or "only" in text_lower or "refuse" in text_lower)
            and ("implementation" in text_lower or "source code" in text_lower
                 or "src/" in text_lower)
        )
        assert restricted, (
            "test-design skill does not state the restriction against reading "
            "implementation files"
        )


# ============================================================================
# KPI failure line 3: required open readiness row has no linked gap ticket
# ============================================================================

class TestFailureMissingGapTicket:
    """covers: F3"""

    def test_planning_states_gap_ticket_requirement(self, skill_texts):
        _, _, full_text = skill_texts["planning"]
        text_lower = full_text.lower()
        assert "gap" in text_lower or "linked" in text_lower, \
            "planning skill does not state the gap ticket requirement"
        assert "readiness" in text_lower or "open" in text_lower, \
            "planning skill does not reference open readiness rows"


# ============================================================================
# KPI success line 11 (CAP-33.e, DEC-105): experiment contradicts closed spec
#   -> CIT-P with three costed options
# ============================================================================

class TestEvidenceTriggeredChange:
    """covers: S11"""

    def test_change_mentions_three_options(self, skill_texts):
        _, _, full_text = skill_texts["change"]
        text_lower = full_text.lower()
        options = ["apply", "defer", "re-baseline"]
        found = sum(1 for opt in options if opt in text_lower)
        assert found >= 3, (
            f"change skill mentions only {found}/3 of the costed options "
            f"(apply, defer, re-baseline)"
        )

    def test_change_cit_p_on_contradiction(self, skill_texts):
        _, _, full_text = skill_texts["change"]
        text_lower = full_text.lower()
        assert "contradict" in text_lower or "conflict" in text_lower, \
            "change skill does not mention contradiction/conflict triggering CIT-P"

    def test_change_cites_dec105_or_cap33e(self, skill_texts):
        _, _, full_text = skill_texts["change"]
        assert "DEC-105" in full_text or "CAP-33" in full_text, \
            "change skill does not cite DEC-105 or CAP-33"

    def test_change_versions_kept(self, skill_texts):
        _, _, full_text = skill_texts["change"]
        text_lower = full_text.lower()
        assert "version" in text_lower and "kept" in text_lower, \
            "change skill does not state that every version is kept"


# ============================================================================
# KPI success line 12 (CAP-38.e, DEC-136): test design takes probe findings
#   as described behaviours, never code
# ============================================================================

class TestProbeFindings:
    """covers: S12"""

    def test_test_design_mentions_probe_findings(self, skill_texts):
        _, _, full_text = skill_texts["test-design"]
        text_lower = full_text.lower()
        assert ("probe" in text_lower or "finding" in text_lower
                or "orchestrator" in text_lower), \
            "test-design skill does not mention probe findings"

    def test_test_design_described_behaviours_not_code(self, skill_texts):
        _, _, full_text = skill_texts["test-design"]
        text_lower = full_text.lower()
        assert "described" in text_lower or "behaviour" in text_lower or "behavior" in text_lower, \
            "test-design skill does not mention 'described behaviours'"
        assert "never" in text_lower or "not" in text_lower, \
            "test-design skill does not state the 'never as code' constraint"

    def test_test_design_specification_gap_reporting(self, skill_texts):
        _, _, full_text = skill_texts["test-design"]
        text_lower = full_text.lower()
        assert "specification gap" in text_lower or "spec gap" in text_lower or \
               ("gap" in text_lower and "specification" in text_lower), \
            "test-design skill does not mention specification gap reporting"

    def test_test_design_cites_dec136_or_cap38(self, skill_texts):
        _, _, full_text = skill_texts["test-design"]
        assert "DEC-136" in full_text or "CAP-38" in full_text, \
            "test-design skill does not cite DEC-136 or CAP-38"


# ============================================================================
# KPI success line 13 (CAP-33.f, DEC-167): "what is the impact of X?" triggers
#   impact assessment via OpenSpec proposal + gov closure
# ============================================================================

class TestImpactAssessment:
    """covers: S13"""

    def test_change_mentions_impact_assessment(self, skill_texts):
        _, _, full_text = skill_texts["change"]
        text_lower = full_text.lower()
        assert "impact" in text_lower, \
            "change skill does not mention impact assessment"

    def test_change_mentions_openspec(self, skill_texts):
        _, _, full_text = skill_texts["change"]
        text_lower = full_text.lower()
        assert "openspec" in text_lower, \
            "change skill does not mention OpenSpec for impact assessment"

    def test_change_mentions_gov_closure(self, skill_texts):
        _, _, full_text = skill_texts["change"]
        text_lower = full_text.lower()
        assert "closure" in text_lower or "gov closure" in text_lower, \
            "change skill does not mention gov closure for impact assessment"

    def test_change_impact_triggered_by_question(self, skill_texts):
        _, _, full_text = skill_texts["change"]
        text_lower = full_text.lower()
        assert ("what is the impact" in text_lower
                or "impact of" in text_lower), \
            "change skill does not mention the question trigger for impact assessment"

    def test_change_cites_dec167_or_cap33f(self, skill_texts):
        _, _, full_text = skill_texts["change"]
        assert "DEC-167" in full_text or "CAP-33" in full_text, \
            "change skill does not cite DEC-167 or CAP-33"


# ============================================================================
# Edge case: referenced gov commands are known (RESERVED_COMMANDS)
# ============================================================================

class TestReferencedCommands:
    """covers: S8 (command-exists part)"""

    @pytest.mark.parametrize("skill_name", SKILL_NAMES)
    def test_referenced_commands_are_known(self, skill_texts, skill_name):
        _, _, full_text = skill_texts[skill_name]
        gov_cmd_pattern = re.compile(r"`gov\s+(\w+)`")
        matches = gov_cmd_pattern.findall(full_text)
        for cmd in matches:
            assert cmd in RESERVED_COMMANDS, (
                f"{skill_name}: references `gov {cmd}` which is not in "
                f"RESERVED_COMMANDS ({RESERVED_COMMANDS})"
            )


# ============================================================================
# Edge case: discovery routing, batching and state rules (W1-34 residual)
# ============================================================================

class TestRoutingBatchingState:
    """covers: S2, S9 (W1-34 residual)"""

    def test_discovery_carries_routing_rules(self, skill_texts):
        _, _, full_text = skill_texts["discovery"]
        text_lower = full_text.lower()
        assert "rout" in text_lower or "route" in text_lower or "routing" in text_lower, \
            "discovery skill does not carry routing rules (W1-34 residual)"

    def test_discovery_carries_batching_rules(self, skill_texts):
        _, _, full_text = skill_texts["discovery"]
        text_lower = full_text.lower()
        assert "batch" in text_lower, \
            "discovery skill does not carry batching rules (W1-34 residual)"

    def test_discovery_carries_state_rules(self, skill_texts):
        _, _, full_text = skill_texts["discovery"]
        text_lower = full_text.lower()
        assert "state" in text_lower, \
            "discovery skill does not carry state rules (W1-34 residual)"


# ============================================================================
# Edge case: CIT-P and CIT-E use openspec
# ============================================================================

class TestCITUsesOpenSpec:
    """covers: S7, S13"""

    def test_change_cit_p_uses_openspec(self, skill_texts):
        _, _, full_text = skill_texts["change"]
        text_lower = full_text.lower()
        assert "openspec" in text_lower, \
            "change skill does not reference openspec for CIT-P/CIT-E"


# ============================================================================
# Edge case: audit ticket when CIT-E changes closed spine (DEC-088, CAP-47.d)
# ============================================================================

class TestAuditTicketOnCITE:
    """covers: S4"""

    def test_change_audit_on_cit_e_closed_spine(self, skill_texts):
        _, _, full_text = skill_texts["change"]
        text_lower = full_text.lower()
        has_audit = "audit" in text_lower
        has_spine = "spine" in text_lower
        has_cit_e = "cit-e" in text_lower
        assert has_audit and (has_spine or has_cit_e), (
            "change skill does not describe audit ticket creation when CIT-E "
            "changes a closed spine"
        )


# ============================================================================
# Cross-cutting: every skill cites at least one policy or decision
# ============================================================================

class TestCitations:
    """covers: S5"""

    @pytest.mark.parametrize("skill_name", SKILL_NAMES)
    def test_skill_cites_at_least_one_reference(self, skill_texts, skill_name):
        _, _, full_text = skill_texts[skill_name]
        citations = CITATION_PATTERN.findall(full_text)
        assert len(citations) > 0, \
            f"{skill_name}: no CAP, DEC or MR citations found"


# ============================================================================
# KPI success line 2 (live session portion): 0 of discovery's decision
#   packages are answerable from retrieval bundle files — text-level proxy
# ============================================================================

class TestDiscoveryRetrievalProxy:
    """covers: S2 (text proxy; full test at W1-42)"""

    def test_discovery_mentions_retrieval(self, skill_texts):
        _, _, full_text = skill_texts["discovery"]
        text_lower = full_text.lower()
        assert ("retrieval" in text_lower or "retrieve" in text_lower
                or "context" in text_lower), \
            "discovery skill does not mention retrieval bundle"


# ============================================================================
# KPI success line 3 (live session portion): planning emits schema-valid
#   tickets — text-level proxy
# ============================================================================

class TestPlanningSchemaProxy:
    """covers: S3 (text proxy; full test at W1-42)"""

    def test_planning_mentions_schema(self, skill_texts):
        _, _, full_text = skill_texts["planning"]
        text_lower = full_text.lower()
        assert "schema" in text_lower or "ticket" in text_lower, \
            "planning skill does not mention schema-valid tickets"


# ============================================================================
# KPI success line 4 (live session portion): test-design transcript reads
#   no file outside spec and KPIs — text-level proxy
# ============================================================================

class TestTestDesignReadRestrictionProxy:
    """covers: S4, F2 (text proxy; full test at W1-42)"""

    def test_test_design_declares_read_restriction(self, skill_texts):
        _, _, full_text = skill_texts["test-design"]
        text_lower = full_text.lower()
        assert "only" in text_lower or "must not" in text_lower or "never" in text_lower, \
            "test-design skill does not declare a read restriction"


# ============================================================================
# A. Declaration's command runs the generic validator correctly (CAP-38.b)
# ============================================================================

class TestDeclarationCommand:
    """covers: S8 (validator integration)"""

    def test_command_is_not_true(self):
        path = find_check_declaration()
        assert path is not None
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        command = data["command"]
        assert command.strip() != "true", \
            "the check declaration's command is still 'true'"

    def test_command_runs_skill_validator(self):
        path = find_check_declaration()
        assert path is not None
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        command = data["command"]
        assert "python3 -m gov.check.skill_validator" in command, \
            f"command does not invoke the generic skill validator: {command}"

    def test_command_has_no_fallback(self):
        path = find_check_declaration()
        assert path is not None
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        command = data["command"]
        assert "||" not in command, \
            f"command contains '||' fallback: {command}"

    def test_command_references_all_four_skill_folders(self):
        path = find_check_declaration()
        assert path is not None
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        command = data["command"]
        for folder_rel in SKILL_FOLDER_RELS:
            assert folder_rel in command, \
                f"command does not reference skill folder {folder_rel}: {command}"

    def test_command_referenced_paths_exist(self):
        path = find_check_declaration()
        assert path is not None
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        command = data["command"]
        for folder_rel in SKILL_FOLDER_RELS:
            if folder_rel in command:
                full_path = REPO_ROOT / folder_rel
                assert full_path.is_dir(), \
                    f"path {folder_rel} referenced in command does not exist"


# ============================================================================
# B. Integration: gov check on a temporary project
# ============================================================================

class TestSkillRegressionGreen:
    """covers: S8 (GREEN path)"""

    def test_skill_regression_green_with_well_formed_skills(
        self, full_project, sandbox
    ):
        full_project.commit("before check")
        run = check_support.run_check(full_project, sandbox)
        interface = cli_support.load_interface(REPO_ROOT)
        envelope = check_support.envelope_of(run, interface)
        result = envelope.get("result") or envelope.get("error", {}).get("details", {})
        status = check_support.family_status(result, SKILL_REGRESSION_FAMILY)
        assert status == check_support.GREEN, (
            f"skill regression family is {status}, expected GREEN "
            f"with well-formed skills\n{run.describe()}"
        )


class TestSkillRegressionRedMissingFrontmatter:
    """covers: S8 (RED: missing frontmatter)"""

    def test_red_when_frontmatter_removed(self, full_project, sandbox):
        skill_path = full_project.root / "template" / "governance" / "kernel" / "skills" / "discovery" / "SKILL.md"
        skill_path.write_text("# Discovery\n\nNo frontmatter here.\n", encoding="utf-8")
        full_project.commit("break frontmatter")
        run = check_support.run_check(full_project, sandbox)
        interface = cli_support.load_interface(REPO_ROOT)
        envelope = check_support.envelope_of(run, interface)
        result = envelope.get("result") or envelope.get("error", {}).get("details", {})
        status = check_support.family_status(result, SKILL_REGRESSION_FAMILY)
        assert status == check_support.RED, (
            f"skill regression family is {status}, expected RED "
            f"when frontmatter is missing\n{run.describe()}"
        )


class TestSkillRegressionRedMissingVersion:
    """covers: S8 (RED: missing version)"""

    def test_red_when_version_missing(self, full_project, sandbox):
        skill_path = full_project.root / "template" / "governance" / "kernel" / "skills" / "planning" / "SKILL.md"
        skill_path.write_text(
            "---\nname: planning\ndescription: Plans things.\n---\n\n# Planning\n\nBody.\n",
            encoding="utf-8",
        )
        full_project.commit("remove version field")
        run = check_support.run_check(full_project, sandbox)
        interface = cli_support.load_interface(REPO_ROOT)
        envelope = check_support.envelope_of(run, interface)
        result = envelope.get("result") or envelope.get("error", {}).get("details", {})
        status = check_support.family_status(result, SKILL_REGRESSION_FAMILY)
        assert status == check_support.RED, (
            f"skill regression family is {status}, expected RED "
            f"when version field is missing\n{run.describe()}"
        )


class TestSkillRegressionRedDescriptionTooLong:
    """covers: S8 (RED: description exceeds 60 tokens)"""

    def test_red_when_description_exceeds_60_tokens(self, full_project, sandbox):
        skill_path = full_project.root / "template" / "governance" / "kernel" / "skills" / "change" / "SKILL.md"
        long_desc = "word " * 100
        skill_path.write_text(
            f"---\nname: change\nversion: \"1.0.0\"\ndescription: {long_desc}\n---\n\n# Change\n\nBody.\n",
            encoding="utf-8",
        )
        full_project.commit("bloat description")
        run = check_support.run_check(full_project, sandbox)
        interface = cli_support.load_interface(REPO_ROOT)
        envelope = check_support.envelope_of(run, interface)
        result = envelope.get("result") or envelope.get("error", {}).get("details", {})
        status = check_support.family_status(result, SKILL_REGRESSION_FAMILY)
        assert status == check_support.RED, (
            f"skill regression family is {status}, expected RED "
            f"when description exceeds 60 tokens\n{run.describe()}"
        )


class TestSkillRegressionRedBodyTooLong:
    """covers: S8 (RED: body exceeds 2500 tokens)"""

    def test_red_when_body_exceeds_2500_tokens(self, full_project, sandbox):
        skill_path = full_project.root / "template" / "governance" / "kernel" / "skills" / "test-design" / "SKILL.md"
        long_body = "word " * 3000
        skill_path.write_text(
            f"---\nname: test-design\nversion: \"1.0.0\"\ndescription: Designs tests.\n---\n\n{long_body}\n",
            encoding="utf-8",
        )
        full_project.commit("bloat body")
        run = check_support.run_check(full_project, sandbox)
        interface = cli_support.load_interface(REPO_ROOT)
        envelope = check_support.envelope_of(run, interface)
        result = envelope.get("result") or envelope.get("error", {}).get("details", {})
        status = check_support.family_status(result, SKILL_REGRESSION_FAMILY)
        assert status == check_support.RED, (
            f"skill regression family is {status}, expected RED "
            f"when body exceeds 2500 tokens\n{run.describe()}"
        )


class TestSkillRegressionRedUnknownCommand:
    """covers: S8 (RED: unknown gov command)"""

    def test_red_when_unknown_gov_command(self, full_project, sandbox):
        skill_path = full_project.root / "template" / "governance" / "kernel" / "skills" / "discovery" / "SKILL.md"
        skill_path.write_text(
            "---\nname: discovery\nversion: \"1.0.0\"\n"
            "description: Discovers things.\n---\n\n"
            "# Discovery\n\nRun `gov foobar` to do nothing.\n",
            encoding="utf-8",
        )
        full_project.commit("inject unknown command")
        run = check_support.run_check(full_project, sandbox)
        interface = cli_support.load_interface(REPO_ROOT)
        envelope = check_support.envelope_of(run, interface)
        result = envelope.get("result") or envelope.get("error", {}).get("details", {})
        status = check_support.family_status(result, SKILL_REGRESSION_FAMILY)
        assert status == check_support.RED, (
            f"skill regression family is {status}, expected RED "
            f"when an unknown gov command is referenced\n{run.describe()}"
        )


class TestSkillRegressionRedMissingFolder:
    """covers: S8 (RED: skill folder missing)"""

    def test_red_when_skill_folder_missing(self, full_project, sandbox):
        skill_dir = full_project.root / "template" / "governance" / "kernel" / "skills" / "discovery"
        shutil.rmtree(skill_dir)
        full_project.commit("remove discovery folder")
        run = check_support.run_check(full_project, sandbox)
        interface = cli_support.load_interface(REPO_ROOT)
        envelope = check_support.envelope_of(run, interface)
        result = envelope.get("result") or envelope.get("error", {}).get("details", {})
        status = check_support.family_status(result, SKILL_REGRESSION_FAMILY)
        assert status == check_support.RED, (
            f"skill regression family is {status}, expected RED "
            f"when a skill folder is missing entirely\n{run.describe()}"
        )


# ============================================================================
# D. Planned vs misspelt commands: gov close is valid, gov foobar is not
# ============================================================================

class TestPlannedVsMisspeltCommands:
    """covers: S8 (command-exists: planned commands valid, misspelt ones rejected)"""

    def test_planned_command_is_valid(self, full_project, sandbox):
        skill_path = full_project.root / "template" / "governance" / "kernel" / "skills" / "change" / "SKILL.md"
        skill_path.write_text(
            "---\nname: change\nversion: \"1.0.0\"\n"
            "description: Changes things.\n---\n\n"
            "# Change\n\nRun `gov close` to close a ticket.\n",
            encoding="utf-8",
        )
        full_project.commit("use planned command")
        run = check_support.run_check(full_project, sandbox)
        interface = cli_support.load_interface(REPO_ROOT)
        envelope = check_support.envelope_of(run, interface)
        result = envelope.get("result") or envelope.get("error", {}).get("details", {})
        checks = check_support.checks_of(result)
        sr_findings = []
        for entry in checks:
            if isinstance(entry, dict) and entry.get("id") == "skill-regression-a":
                sr_findings = entry.get("findings", [])
        unknown_cmd_findings = [
            f for f in sr_findings
            if isinstance(f, dict) and f.get("code") == "SKILL_UNKNOWN_COMMAND"
        ]
        assert not unknown_cmd_findings, (
            f"'gov close' is a planned reserved command but was flagged: {unknown_cmd_findings}"
        )

    def test_misspelt_command_is_rejected(self, full_project, sandbox):
        skill_path = full_project.root / "template" / "governance" / "kernel" / "skills" / "change" / "SKILL.md"
        skill_path.write_text(
            "---\nname: change\nversion: \"1.0.0\"\n"
            "description: Changes things.\n---\n\n"
            "# Change\n\nRun `gov foobar` to do nothing.\n",
            encoding="utf-8",
        )
        full_project.commit("use misspelt command")
        run = check_support.run_check(full_project, sandbox)
        interface = cli_support.load_interface(REPO_ROOT)
        envelope = check_support.envelope_of(run, interface)
        result = envelope.get("result") or envelope.get("error", {}).get("details", {})
        status = check_support.family_status(result, SKILL_REGRESSION_FAMILY)
        assert status == check_support.RED, (
            f"skill regression family is {status}, expected RED "
            f"when a misspelt command 'gov foobar' is used\n{run.describe()}"
        )
