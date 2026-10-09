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

## The follow-up: the way a wave is run (DEC-537, DEC-539, DEC-541)

Written before implementation by a fresh Independent Test Designer, for the ticket's two last success lines.
Files: `test_w1_35_orchestration.py` (54 cases) and `w1_35_orchestration_support.py` (paths, the reader, the table
of rows). No existing case was changed. The four skills' cases and `conftest.py` are untouched.

Run: `env -u PYTHONPATH python3 -m pytest tests/acceptance/W1-35 -q -p no:cacheprovider -rs`

**Red before implementation: 53 of the 54 new cases fail, each because a deliverable does not exist**
(`template/governance/kernel/skills/orchestration/SKILL.md does not exist`, `... has no section whose heading
names the ticket lead`, `.../templates/brief-<kind>.md does not exist`, `no check declaration matching
skill-regression-orchestration*.yaml`). One new case is green already and is a guard:
`TestRulesyncSources::test_the_orchestrator_roles_rulesync_source_carries_the_role_files_body` (source and role
file agree today; it turns red if only one of the two gains the lead section). The 112 earlier cases stay green.

The new cases were also run against a throwaway deliverable kept outside the tree: all pass on a skill of about
1,500 tokens that states the rows in the specification's own words; with one statement taken out, the case of
that row (or of the status route) fails and names the statement.

### The public interface

| Deliverable | Path |
|---|---|
| The skill | `template/governance/kernel/skills/orchestration/SKILL.md`, frontmatter `name: orchestration` |
| Its rulesync source | `template/.rulesync/skills/orchestration/SKILL.md` |
| The ticket lead | a section of `template/governance/kernel/roles/orchestrator.md`: a heading that names the lead, and the text under it |
| The role's rulesync source | `template/.rulesync/subagents/orchestrator.md`, its body the role file's text |
| The five briefs | `template/governance/kernel/templates/brief-test-designer.md`, `brief-engineer.md`, `brief-reviewer.md`, `brief-product-spec.md`, `brief-lead.md` |
| The check | one file `template/governance/kernel/checks/skill-regression-orchestration*.yaml` |

The five file names are fixed by this suite. Nothing else is: no heading text, no sentence, no order.

### How the text is read

- **A statement** is one paragraph, one top-level list item with its wrapped and indented lines, one table row, or
  one fenced block. A paragraph that ends with a colon is also read together with the list directly under it.
- **A clause is found** when one statement carries every idea of the clause. An idea is a word pattern with its
  common variants, matched without regard to case; the profile names, the four return forms, `P1` to `P3` and
  `AUTH_REQUIRED` are matched as written. No clause is an exact sentence.
- **The corpus of a row** is the skill and every file of the kernel's templates folder that the skill names by its
  file name. A row may be divided between them (DEC-539); a clause found nowhere fails the row's case, which lists
  every missing clause. Reading: "the brief templates it names" is taken to include another kernel template the
  skill names, so the package's fields may be those of `decision-package.md` and need not be repeated.
- **A decision id** the specification gives for a row is cited somewhere in that corpus.
- **Standing sentences** are compared word for word, backticks and brackets included; only line breaks are free.
- **A placeholder** is `<...>`, `{{...}}`, `{...}` or `[UPPER CASE]`, and its text names what it stands for.

### Success line 14 [CAP-24.a, CAP-24.b]

| What is held | Cases | Red reason today |
|---|---|---|
| The skill has the form and the bounds of the others | `TestOrchestrationSkillForm` (5): versioned frontmatter and name; description <= 60 tokens; body <= 2.5k tokens; every `gov <word>` in code is a reserved command; the skill names the five briefs | the skill does not exist |
| It cites what it follows and grants nothing | `TestOrchestrationSkillAuthority` (3): a CAP, DEC or MR id is cited; permission-like wording has an id on its line; a list item with a word of authority (must, only, never, ...) has an id | the skill does not exist |
| Each row is stated (success), and a row or clause that is absent is found (failure) | `TestRows::test_every_clause_of_the_row_is_stated[<row>]` × 11 | the skill does not exist |
| The Wave 2 items are rules followed by hand, not a mechanism yet (DEC-537) | `TestWave2Items` (2): one section says both "by hand" and "not enforced yet" and cites DEC-537; it names the resource gate, the launch without a model, `AUTH_REQUIRED`, and leads started through the launcher | the skill does not exist |
| The ticket lead is a section of the role file | `TestTicketLeadSection` (7): what a lead is; what it does; what it never does (merge, edit ticket files or the decision register, push); the four return forms; an id cited; no labelled field added; the roles and the rulesync subagents stay at six | no section whose heading names the ticket lead |
| The five briefs | `TestBriefTemplates` (12): placeholders for ticket, profile, paths, sources, decisions × 5; the three standing sentences × 5; the test designer's states behaviour and sources only and cites DEC-462; no brief is named or framed as a record template | the brief does not exist |
| The wording | `TestWording` (2): no `pytest`, `python`, `.py`, `conftest` or `tests/acceptance` in the skill's body, the lead section or a brief, and the skill names tests in a project's terms (DEC-534); no ticket id, branch, folder, workbench, model name or `x.y.z` version of this repository's wave (DEC-539) | a deliverable does not exist |
| The check is registered as `skill-regression-a` is | `TestOrchestrationCheck` (5): five string fields, family, tier and severity those of `skill-regression-a`, an id of its own; the command runs the generic validator over the skill's folder with no fallback; the delivered skill passes the validator; the same file with a body over the bound gives the one finding `SKILL_BODY_TOO_LONG` (failure line 1); in a temporary project `gov check` shows the check `GREEN` under `skill regression`, and `RED` with the skill taken out | no declaration; the skill does not exist |
| The template's rulesync sources stay in step | `TestRulesyncSources` (2) | the skill does not exist; the role case is the green guard |

The rows and their cases (each case lists the clauses a reader cannot find):

| Row | Case id | Decision ids that must be cited |
|---|---|---|
| Parallel tickets | `[parallel tickets]` | |
| Integration order | `[integration order]` | DEC-536, DEC-498 |
| The ticket loop | `[the ticket loop]` | DEC-413, DEC-096 |
| Decisions | `[decisions]` | DEC-220, DEC-416, DEC-463 |
| Stops | `[stops]` | |
| Sessions | `[sessions]` | DEC-460, DEC-420 |
| Briefs | `[briefs]` (and `TestBriefTemplates`) | DEC-462, DEC-221 |
| Commits | `[commits]` | DEC-476, DEC-491 |
| Checkpoints and context | `[checkpoints and context]` | DEC-511 |
| Temp hygiene and protected files | `[temp hygiene and protected files]` | DEC-508, DEC-525 |
| Learning metrics | `[learning metrics]` | DEC-106 |

The clauses of each row are the table `ROWS` in `w1_35_orchestration_support.py`: one entry per clause of the
specification's row, named in plain words.

### Success line 15 [CAP-28.a]

| What is held | Case | Red reason today |
|---|---|---|
| A status question in plain words is routed to `gov status --json`; DEC-541 or CAP-28 is cited | `TestStatusRoute::test_a_status_question_is_routed_to_the_command` | the skill does not exist |
| The parts: tickets, open packages, gates, readiness, governance share, pause state, health | `test_the_route_names_the_parts_the_answer_is_given_from` | the same |
| A part marked not read is said not to be read | `test_a_part_marked_not_read_is_said_not_to_be_read` | the same |
| Never from recall | `test_the_answer_is_never_given_from_recall` | the same |
| Failure: a skill that only names the command states no route | `test_a_skill_without_the_route_is_found` | the same |

The parts and "not read" are looked for in the section where the route is stated.

### What no case here holds

- **A live session that answers a status question.** The cases hold that the skill states the route. Whether a
  session with the skill loaded runs the command and answers from its output needs a model session, the Claude
  Code CLI and a generated `.claude/skills/`; none of that is inside this worktree, so no case here can run it
  and none is left for the lead. It is measured at W1-42, which is a provider of CAP-28 and runs from the
  kernel's skill and briefs (DEC-537).
- **That the roster and the guard are unchanged.** The cases hold the six role files and the six rulesync
  subagents. The roster file and the guard's code are outside the ticket's paths; W1-33's suite holds them.
- **That a filled brief is followed**, and that the orchestrator runs a wave this way: W1-42.
- **Whether a rule's cited decision is the right one.** The cases hold that the ids the specification gives are
  cited; the review reads the pairing.

### What the implementer must respect (other suites)

1. **Rulesync sources (W1-38).** The adapter-portability check compares every kernel role and every kernel skill
   with its source under `.rulesync/`, both ways. In the project W1-38's suite builds from the template, a kernel
   skill without `template/.rulesync/skills/orchestration/SKILL.md`, or a role file whose text differs from the
   body of `template/.rulesync/subagents/orchestrator.md`, makes the check red and
   `TestRegisteredFamilyCheck::test_gov_check_is_green_on_a_clean_generated_project` fail. Deliver both sources
   in the same change: the skill's with the kernel's frontmatter and body, the role's with the kernel's text as
   its body and its `claudecode.tools` unchanged. `TestRulesyncSources` holds both here.
2. **This repository's own `.rulesync/**` and `.claude/**` are not written by the follow-up.** Once the
   deliverables exist, `python3 -m gov.adapters.portability` run at this repository's root reports two new
   findings until the owner applies the output at the exit: `SOURCE_MISSING` for
   `.rulesync/skills/orchestration/SKILL.md` and `SOURCE_DIFFERS` for `.rulesync/subagents/orchestrator.md`. No
   case of W1-38's suite reads this repository's root, so no case turns red; the check at the root does. See the
   package in the designer's return.
3. **The role file's labelled fields stay as they are (W1-33).**
   `test_the_definition_agrees_with_its_kernel_role_file[orchestrator]` compares the labelled fields of this
   repository's `.claude/agents/orchestrator.md` with the role file's: the same labels, the same text. Text
   outside the labelled items is free. So the lead section stands under its own heading, after the fields, holds
   no list item that starts with a bold label, and no existing field changes by a word. Otherwise that W1-33
   case is red until the owner applies the generated definition.
4. **A brief is not a record template (W1-08, W1-34).** W1-34's suite reads only `decision-package*` and
   `decision-record*`. W1-08's suite validates every templates file whose name holds `decision`, `madr`, `adr`,
   `ticket`, `lesson`, `failure`, `research`, `gate`, `package` or `checkpoint` against that record's schema. The
   five names above hold none of these words; keep them, add no record frontmatter, and add no `.jinja` suffix
   (Copier renders only suffixed files, so a `{{...}}` placeholder in a `.md` file is copied as it is).
5. **The path map (W1-39).** Nothing to do: the template's path map classes `governance/kernel/**` and
   `.rulesync/**` by pattern, this repository's classes `template/**`, and the lock is written at copy time.
6. **Code spans and the validator.** The generic validator reads every code span and fenced block for
   `gov <word>` and reports a word that is not a reserved command. `gov launch` is not one: name the launcher in
   prose. `gov status`, `gov close`, `gov check` and `gov checkpoint` are reserved.
7. **"can read".** The permission rule of the four skills (an id on the line of `may|can|shall` + `read`,
   `write`, ...) also matches "an owner can read on a phone". Write "readable on a phone", or put an id on the
   line.

## Token counting

Uses `ceil(len(text) / 4)` where `text` is the decoded UTF-8 string, per W1-24.

## Running

```bash
cd /home/usain/gov-os-worktrees/W1-35
python3 -m pytest tests/acceptance/W1-35/ -v
```
