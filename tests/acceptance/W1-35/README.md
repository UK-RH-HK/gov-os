# W1-35 acceptance tests

Ticket: DAEO-0i6h (W1-35) — "Skills: discovery, planning, independent test design, change"
Profile: STANDARD

## KPI coverage

### Success lines

| # | KPI line | Tests | Expected red reason |
|---|----------|-------|---------------------|
| S1 | Each skill has versioned frontmatter, desc <= 60 tokens, body <= 2.5k tokens (CAP-24.a) | `TestFrontmatterAndSize::test_frontmatter_is_valid_yaml`, `test_frontmatter_has_required_fields`, `test_version_is_present_and_nonempty`, `test_description_within_60_tokens`, `test_body_within_2500_tokens` | Missing or invalid frontmatter; missing name/version/description; desc > 60 tokens; body > 2500 tokens |
| S2 | Decision packages: 0 answerable from retrieval bundle, at most 5, P1 may bypass (DEC-093, CAP-34.c) | `TestDecisionPackages::test_discovery_mentions_decision_packages`, `test_discovery_mentions_p1_p3_ranking`, `test_discovery_mentions_cap_of_five`, `test_discovery_p1_bypass`, `test_discovery_cites_dec093_or_cap34`; `TestDiscoveryRetrievalProxy::test_discovery_mentions_retrieval`; `TestRoutingBatchingState` (3 tests) | Skill text omits decision-package mechanics, ranking, cap, bypass, retrieval, routing/batching/state rules |
| S3 | Planning emits schema-valid tickets and one linked gap ticket per required open readiness row (DEC-089, CAP-30.b) | `TestPlanningGapTickets::test_planning_mentions_gap_tickets`, `test_planning_mentions_readiness_rows`, `test_planning_mentions_ticket_classes`, `test_planning_cites_dec089_or_cap30`, `test_planning_mentions_schema_valid_tickets`; `TestPlanningSchemaProxy` | Skill text omits gap tickets, readiness, ticket classes, citations |
| S4 | Test design reads only spec and KPIs; change covers CIT-P/CIT-E; audit ticket on CIT-E (DEC-088, CAP-33.a, CAP-47.d) | `TestTestDesignConstraints` (4 tests); `TestAuditTicketOnCITE`; `TestTestDesignReadRestrictionProxy` | Skill text omits spec/KPI read restriction, audit ticket, CIT-E/spine references |
| S5 | No skill grants a permission or states a rule as its own authority (CAP-24.b) | `TestNoPermissionGrants::test_no_permission_granting_language`, `test_procedural_statements_cite_policy`; `TestCitations::test_skill_cites_at_least_one_reference` | Permission-granting language without citation; procedural authority without CAP/DEC/MR reference |
| S6 | Change skill lifecycle: evidence → proposal → independent review → owner approval → versioned promotion (CAP-24.c) | `TestChangeSkillLifecycle::test_change_skill_documents_lifecycle`, `test_change_skill_lifecycle_order` | Missing lifecycle step; steps in wrong order |
| S7 | CIT-P and CIT-E for kernel/policy/skill changes; refuses archive without records (CAP-33.d) | `TestCITWorkflow` (4 tests); `TestCITUsesOpenSpec` | Missing CIT-P or CIT-E mention; missing refusal; missing CAP-33 citation; missing openspec reference |
| S8 | Registers skill-regression family check (CAP-38.b) | `TestCheckDeclaration` (5 tests); `TestReferencedCommands::test_referenced_commands_are_known` | Missing check declaration; invalid YAML; missing fields; wrong family; unknown gov command reference |
| S9 | Discovery treats experiments as normal step (DEC-102, CAP-32.c) | `TestDiscoveryExperiments` (6 tests) | Missing experiment, sandbox, evidence-record, normal-cycle, CIT-P mentions; missing DEC-102/CAP-32 citation |
| S10 | Discovery and planning follow spec work order (DEC-103, CAP-30.f) | `TestSpecificationWorkOrder` (4 tests) | Missing work-order steps; wrong sequence; missing owner review mention |
| S11 | Experiment contradicts closed spec → CIT-P with three options (DEC-105, CAP-33.e) | `TestEvidenceTriggeredChange` (4 tests) | Missing options (apply/defer/re-baseline); missing contradiction trigger; missing DEC-105/CAP-33 citation; missing version-kept statement |
| S12 | Probe findings as described behaviours, never code (DEC-136, CAP-38.e) | `TestProbeFindings` (4 tests) | Missing probe/finding mention; missing "described behaviours"; missing gap reporting; missing DEC-136/CAP-38 citation |
| S13 | Impact assessment triggered by "what is the impact of X?" (DEC-167, CAP-33.f) | `TestImpactAssessment` (5 tests) | Missing impact/openspec/closure mention; missing question trigger; missing DEC-167/CAP-33 citation |

### Failure lines

| # | KPI line | Tests | Expected red reason |
|---|----------|-------|---------------------|
| F1 | A skill body exceeds 2.5k tokens | `TestFailureBodyExceeds::test_body_over_2500_tokens_would_fail` (parameterised x4) | Body token count > 2500 |
| F2 | The test-design skill reads implementation files | `TestFailureTestDesignReadsImpl::test_test_design_states_restriction`; `TestTestDesignReadRestrictionProxy` | Skill text does not state restriction against reading implementation files |
| F3 | A required open readiness row has no linked gap ticket after planning | `TestFailureMissingGapTicket::test_planning_states_gap_ticket_requirement` | Planning skill does not state gap ticket requirement for open readiness rows |

## What is tested here vs. at W1-42

**Tested here (on the skill file text):**
- Frontmatter validity and field presence (name, version, description)
- Token counts (description <= 60, body <= 2500)
- Citations of CAP, DEC, MR references
- No permission-granting language
- Named steps, their order, and key assertions per skill
- Check declaration YAML validity and field correctness
- Referenced `gov` commands exist in RESERVED_COMMANDS

**Measured at W1-42 (dev-tier live sessions):**
- "0 of the decision packages discovery asks are answerable from files its retrieval bundle cites"
- "Its transcript reads no file outside them" (test design reads only spec and KPIs)
- "Planning emits schema-valid tickets" (actual ticket schema validation)
- Live CIT-P/CIT-E workflow execution

## Token counting

Uses `ceil(len(text) / 4)` where `text` is the decoded UTF-8 string, per W1-24.

## Running

```bash
cd /home/usain/gov-os-worktrees/W1-35
python3 -m pytest tests/acceptance/W1-35/ -v
```
