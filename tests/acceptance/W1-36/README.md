# W1-36 acceptance tests: Skills — retrieval, audit, checkpoint/resume, adopt

Written before the implementation by the independent test designer (MR-3) from
the ticket's KPI lines, its `covers` ids and its sources.  **74 cases** in
**five test files** plus support and fixtures.  The four skill/declaration files
read and parse the skill files (markdown with YAML frontmatter) and check
declarations (YAML); no case runs code or needs a network.  The integration
test file builds temporary git projects and calls ``run_checks``.

Run: `python3 -m pytest tests/acceptance/W1-36 -q -p no:cacheprovider`

## The interface the tests fix

### Skill files

Four markdown files under `template/governance/kernel/skills/<name>/SKILL.md`:

| Skill | Path |
|---|---|
| retrieval | `template/governance/kernel/skills/retrieval/SKILL.md` |
| audit | `template/governance/kernel/skills/audit/SKILL.md` |
| checkpoint | `template/governance/kernel/skills/checkpoint/SKILL.md` |
| adopt | `template/governance/kernel/skills/adopt/SKILL.md` |

Each has YAML frontmatter with `name`, `description` and `version`, followed by
a body (everything after the closing `---`) of at most 2,500 tokens
(`ceil(len(text) / 4)`).

### Check declarations

Two YAML files under `template/governance/kernel/checks/`:

| Declaration | Glob |
|---|---|
| skill-regression | `skill-regression-b*` |
| audit-reproducibility | `audit-reproducibility*` |

Each has `id`, `family`, `tier` (G1), `severity`, `command`.  The family
normalises (DEC-436) to one of the 17 known families
(`src/gov/check/runner.py::FAMILIES`).

## KPI lines and covers ids

| KPI | covers | file |
|---|---|---|
| S1 retrieval: facets in disposable subagents, validated bundle returns | CAP-16.b, CAP-56.a | `test_w1_36_retrieval_skill.py::TestRetrievalSubagents` (6) |
| S2 audit report: milestone, rows, six classes, decision packages | CAP-47.d | `test_w1_36_audit_skill.py::TestAuditReport` (4), `::TestAuditDecisionPackages` (4) |
| S3 each skill versioned, body ≤ 2.5k tokens | CAP-24.b | `test_w1_36_skill_form.py::TestSkillFrontmatter` (12), `::TestSkillTokenLimit` (4) |
| S4 no skill grants permissions; each cites sources | CAP-24.b | `test_w1_36_skill_form.py::TestSkillAuthority` (8) |
| S5 skill-regression and audit-reproducibility check declarations | CAP-38.b | `test_w1_36_check_declarations.py` (16) |
| S6 audit: fresh session, context pack + repository, pack hash | CAP-47.b | `test_w1_36_audit_skill.py::TestAuditFreshSession` (4) |
| S7 wave-exit covers every LITE feature spec | CAP-47.d | `test_w1_36_audit_skill.py::TestAuditWaveExit` (1) |
| F1 intermediate batches in main context | — | `test_w1_36_retrieval_skill.py::TestRetrievalFailure` (1) |
| F2 audit edits audited files | — | `test_w1_36_audit_skill.py::TestAuditReadOnly` (1) |
| F3 owner finding → ticket without package | — | `test_w1_36_audit_skill.py::TestAuditDecisionPackages::test_owner_finding_requires_decision_package_before_ticket` (1) |
| S5/DEC-447 audit check is "not applicable until the first audit" | CAP-38.b, DEC-447 | `test_w1_36_check_declarations.py` (4), `test_w1_36_check_integration.py` (5) |

## The first question

**Where are the dev scenarios (MR-A-06 and MR-B-06), and can they be run in
this wave before the exit run?**

MR-A-06 and MR-B-06 run at **W1-42** (the wave exit run) on the dev tiers.
They need a live model session on the a-dev and b-dev clones, which W1-42
orchestrates.  This ticket writes the skill text; the dev-scenario cases are
tested on the text as far as they go (S2 report form, S6 fresh session, S7
wave-exit scope), and the rest is returned as a package naming W1-42.

## Expected red before the implementation

All 57 cases fail at the fixture, for one of six reasons:

| Reason | Cases |
|---|---|
| `retrieval skill does not exist: template/governance/kernel/skills/retrieval/SKILL.md` | 13 (7 content + 6 form) |
| `audit skill does not exist: template/governance/kernel/skills/audit/SKILL.md` | 20 (14 content + 6 form) |
| `checkpoint skill does not exist: template/governance/kernel/skills/checkpoint/SKILL.md` | 6 (form) |
| `adopt skill does not exist: template/governance/kernel/skills/adopt/SKILL.md` | 6 (form) |
| `no skill-regression check declaration matches template/governance/kernel/checks/skill-regression-b*` | 6 |
| `no audit-reproducibility check declaration matches template/governance/kernel/checks/audit-reproducibility*` | 6 |

No case fails on a behaviour assertion before the file exists; none passes.

## Packages

### DEV-SCENARIO-LIVE → W1-42

The KPI line S2 says "on the MR-A-06 and MR-B-06 dev scenarios it reports the
planted divergence [CAP-47.d]".  The skill text is tested here as far as it
goes: the skill says the report names its milestone and uses the six classes
(S2), that the session is fresh with bounded inputs (S6), and that wave-exit
reports cover every LITE feature specification (S7).  Whether a live audit
session on the a-dev and b-dev clones actually reports the planted divergence
can only be measured by a live run on the dev tiers.  **That is W1-42's job**
(the wave exit run, which depends on W1-36).  The test designer names W1-42 and
does not silently drop this part of S2.

## Files

| File | Cases | KPI |
|---|---|---|
| `test_w1_36_retrieval_skill.py` | 7 | S1, F1 |
| `test_w1_36_audit_skill.py` | 14 | S2, S6, S7, F2, F3 |
| `test_w1_36_skill_form.py` | 24 (6 × 4 skills) | S3, S4 |
| `test_w1_36_check_declarations.py` | 16 | S5, DEC-447 |
| `test_w1_36_check_integration.py` | 13 | S5, DEC-447 |
| `conftest.py` | — | fixtures |
| `w1_36_support.py` | — | constants, parsers, helpers |

**Total: 74 cases** (7 + 14 + 24 + 16 + 13).

## What each case needs

* **No network, no model, no tool, no dev tier.**
* **PyYAML** (`yaml`): to parse YAML frontmatter and check declarations.
* Integration tests (`test_w1_36_check_integration.py`) build temporary git
  repos and call `run_checks` from `src/gov/check/runner.py`.

## Revised cases (DEC-447)

- `test_w1_36_check_integration.py::TestAuditReproGovCheck::test_red_when_no_audit_report` →
  `test_yellow_when_no_audit_report_folder_missing`: revised after implementation: owner
  decision DEC-447 — before the first audit, the family is YELLOW (warning), not RED.

## New cases (DEC-447)

- `test_w1_36_check_integration.py::TestAuditReproGovCheck::test_yellow_when_no_audit_report_folder_empty`:
  YELLOW when the reports folder exists but holds no report.
- `test_w1_36_check_integration.py::TestAuditReproGovCheck::test_yellow_reason_says_not_applicable`:
  the YELLOW reason says "not applicable until the first audit".
- `test_w1_36_check_integration.py::TestAuditReproGovCheck::test_yellow_alone_does_not_make_gov_check_fail`:
  a project with only this family YELLOW does not make `gov check` exit as failed.
- `test_w1_36_check_integration.py::TestAuditReproGovCheck::test_red_when_one_valid_and_one_invalid_report`:
  RED when one valid and one invalid report are present — the hard block holds.
- `test_w1_36_check_declarations.py::TestAuditReproNotApplicableField::test_allows_not_applicable_is_present`:
  the audit-reproducibility declaration carries `allows-not-applicable`.
- `test_w1_36_check_declarations.py::TestAuditReproNotApplicableField::test_allows_not_applicable_value_is_true`:
  the value is `"true"`.
- `test_w1_36_check_declarations.py::TestAuditReproNotApplicableField::test_severity_stays_hard_block`:
  severity stays `hard-block` with the field present.
- `test_w1_36_check_declarations.py::TestSkillRegressionNotApplicableAbsent::test_skill_regression_has_no_allows_not_applicable`:
  skill-regression declarations do not carry the field.

## Earlier tests revised

None beyond the DEC-447 revision above.

## KPI map after D-4's cut (DEC-1061)

Regenerated at the cut (tier 2: each KPI line's own case kept first, then at most 6 functions per line;
a parametrised function keeps its first row in the full run unless it is a line's own case). The rest stay
built in the opt-in suite `lifted` (`tests/optin-lifted*.txt`), run report-only with `--optin=lifted`.

| KPI line | case(s) in the full run | placed by |
|---|---|---|
| S1: Retrieval runs facets in disposable subagents and returns only the validated bundle [CAP-16.b, CAP-56.a] | `test_w1_36_retrieval_skill.py::TestRetrievalSubagents::test_the_skill_mentions_facets`, `test_w1_36_retrieval_skill.py::TestRetrievalSubagents::test_the_skill_says_subagents_are_disposable`, `test_w1_36_retrieval_skill.py::TestRetrievalSubagents::test_the_skill_cites_dec_032` | README |
| S2: Audit produces a report naming its milestone (DEC-088) with one row per contract item and decision in scope, each classed OK/MISSING/... | `test_w1_36_audit_skill.py::TestAuditReport::test_the_report_names_its_milestone`, `test_w1_36_audit_skill.py::TestAuditReport::test_the_skill_cites_dec_088`, `test_w1_36_audit_skill.py::TestAuditReport::test_the_report_has_rows_per_contract_item_and_decision` | README |
| S3: Contested and owner-level findings appear in chat as decision packages; agreed fixes become tickets; each skill versioned, body <= 2.... | `test_w1_36_skill_form.py::TestSkillFrontmatter::test_has_name_in_frontmatter`, `test_w1_36_skill_form.py::TestSkillFrontmatter::test_has_description_in_frontmatter`, `test_w1_36_skill_form.py::TestSkillFrontmatter::test_has_version_in_frontmatter` | README |
| S4: No skill file grants a permission or states a rule as its own authority: a skill is a method, holds no tool permissions, and cites th... | `test_w1_36_skill_form.py::TestSkillAuthority::test_no_permission_keys_in_frontmatter`, `test_w1_36_skill_form.py::TestSkillAuthority::test_cites_at_least_one_governing_source`, `test_w1_36_skill_form.py::TestSkillFrontmatter::test_has_name_in_frontmatter` | README |
| S5: Registers the skill-regression family check over its four skills and the audit-reproducibility family check (an audit report's cited ... | `test_w1_36_check_declarations.py::TestSkillRegressionCheck::test_at_least_one_declaration_exists`, `test_w1_36_check_declarations.py::TestSkillRegressionCheck::test_each_has_required_fields`, `test_w1_36_check_declarations.py::TestSkillRegressionCheck::test_family_normalises_to_skill_regression` | README |
| S6: The audit skill starts a fresh session whose only inputs are the bounded context pack from gov context and the repository, and the re... | `test_w1_36_audit_skill.py::TestAuditFreshSession::test_the_skill_says_the_session_is_fresh`, `test_w1_36_audit_skill.py::TestAuditFreshSession::test_the_skill_says_inputs_are_context_pack_and_repository`, `test_w1_36_audit_skill.py::TestAuditFreshSession::test_the_skill_says_report_states_pack_hash` | README |
| S7: A wave-exit audit report has one row per LITE feature specification closed in the wave (DEC-088) [CAP-47.d] | `test_w1_36_audit_skill.py::TestAuditWaveExit::test_wave_exit_covers_every_lite_feature_spec`, `test_w1_36_audit_skill.py::TestAuditReport::test_the_report_names_its_milestone`, `test_w1_36_audit_skill.py::TestAuditReport::test_the_skill_cites_dec_088` | README |
| F1: Intermediate retrieval batches appear in the main context | `test_w1_36_retrieval_skill.py::TestRetrievalFailure::test_the_skill_addresses_the_main_context_boundary`, `test_w1_36_retrieval_skill.py::TestRetrievalSubagents::test_the_skill_mentions_facets`, `test_w1_36_retrieval_skill.py::TestRetrievalSubagents::test_the_skill_says_subagents_are_disposable` | README |
| F2: The audit skill edits audited files | `test_w1_36_audit_skill.py::TestAuditReadOnly::test_the_skill_says_it_does_not_edit_audited_files`, `test_w1_36_audit_skill.py::TestAuditReport::test_the_report_names_its_milestone`, `test_w1_36_audit_skill.py::TestAuditReport::test_the_skill_cites_dec_088` | README |
| F3: An owner-level finding becomes a ticket without a decision package | `test_w1_36_audit_skill.py::TestAuditDecisionPackages::test_contested_findings_become_decision_packages`, `test_w1_36_audit_skill.py::TestAuditDecisionPackages::test_owner_level_findings_become_decision_packages`, `test_w1_36_audit_skill.py::TestAuditDecisionPackages::test_agreed_fixes_become_tickets` | README |

Tier 2's cap here: 60 functions (10 KPI lines x 6); 6 functions moved to `lifted` (listed in `tests/optin-lifted-breadth.txt`).
