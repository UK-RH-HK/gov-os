---
id: DAEO-t8mp
status: open
deps: []
links: [DAEO-k7hz, DAEO-lrre, DAEO-wnnz]
created: 2026-11-06T09:58:49Z
type: task
priority: 1
assignee: product-spec
external-ref: W2-128
tags: [wave-2, templates, kernel, cit-p, standard]
wbs_id: W2-128
title: 'The templates: one per role, the ticket and the brief envelope, filled from the ticket and one facts file, delivered at launch, their use measured (P1-7, R3 TPL-1 to TPL-8, DEC-1050 TEMPLATES)'
class: skill
state_class: AUTHORITATIVE
role: product-spec
depends_on: []
allowed_paths:
- template/governance/kernel/templates/**
- template/governance/kernel/schemas/facts.schema.json
- template/governance/kernel/schemas/ticket.schema.json
- template/governance/kernel/schemas/lesson.schema.json
- template/governance/kernel/schemas/failure.schema.json
- template/governance/kernel/schemas/research.schema.json
- template/governance/kernel/roles/*.md
- template/governance/kernel/skills/test-design/SKILL.md
- template/governance/kernel/skills/orchestration/SKILL.md
- .rulesync/subagents/*.md
- template/.rulesync/subagents/*.md
- governance/project/facts.yaml
- governance/project/orchestration/brief-gaps.md
- tests/unit/templates/test_w2_128*
- docs/changes/W2-128-CIT-P.md
kpis:
  success:
  - 'TPL-1 S1 template/governance/kernel/templates/ holds T-0 to T-8 as in R3-TEMPLATES.md''s Appendix, each with name, version and role front matter. Verify: a unit test lists the nine files and parses their front matter [DEC-1050]'
  - 'TPL-1 S2 The prose of each template (fenced tables of paths and commands excluded) is within R3 §C''s budget. Verify: the test measures the characters [DEC-1050]'
  - 'TPL-1 S3 No template restates a rule that DEC-957, DEC-959, DEC-963, DEC-1010 or DEC-1050 superseded: the engineer template holds no instruction to read tests/acceptance/; the test designer''s permits reading code on w2/integrate; the reviewer''s carries the verdict block in DEC-1010''s form. Verify: string tests on those three facts [DEC-957, DEC-959, DEC-963, DEC-1010, DEC-1050] (folds W2-11b S1, F1)'
  - 'TPL-1 S4 brief-engineer.md, brief-test-designer.md, brief-reviewer.md, brief-product-spec.md and brief-lead.md are removed or a one-line pointer, and roles/engineer.md line 5 says "to fulfil the spec and its KPIs". Verify: a test [DEC-957, DEC-1050]'
  - 'TPL-1 S5 Every placeholder in a template is a key the generator knows. Verify: a test against TPL-3''s key list [DEC-1050]'
  - 'TPL-2 S1-S4 governance/project/facts.yaml holds paths, commands, dod, steps and budgets and validates against template/governance/kernel/schemas/facts.schema.json; each commands entry has a check: form (--help, a dry run or a no-op) that a unit test runs in a temporary repository; a steps switch turned off removes its one line and nothing else; dod has at most six lines, quoted by reference by the ticket and lead templates. Verify: a schema test, the check-runner test, a generator test with one switch flipped, a dod test [DEC-1050]'
  - 'TPL-3 S1-S4, S6, S7 gov brief <role> <ticket> prints a filled T-0 with the role section from only the ticket file and facts.yaml, byte-identical for identical inputs; exits non-zero naming each leftover placeholder and each KPI line without verify; prints the ready-check warnings and the filled size, a warning never stopping it; the lead''s hand-written part only "what the lead knows" and "repair input" (--part, --repair), no role-template text in the stdin brief; refuses a line holding "until <ticket>" when that ticket is closed; gov brief lead {ID} --run tests|build|review|resume|land carries only that run kind''s section of T-7. Verify: a golden-file test, one per run kind, and one test per refusal and warning [DEC-1050]'
  - 'TPL-3 S5 The three scripts (tools/lead_verify.sh, launch_worker.sh, wait_for.sh: built in the CTO''s tools lane, 2026-11-06) are the commands facts.yaml names for verify, launch and wait, and the templates name them in one line each. Verify: the facts check-runner test runs each one''s check form [DEC-1050]'
  - 'TPL-4 S1-S4 gov launch <role> <ticket> passes --append-system-prompt-file <root>/.claude/templates/<role>.md and refuses to start when the file is missing; the dispatcher''s lead launch passes the same flag with role-lead.md; .claude/agents/<role>.md bodies are generated from the kernel role templates by rulesync with a skills: list, and .claude/templates/*.md are generated copies, both reported consistent by gov.adapters.portability. Verify: a launcher unit test on the built argv, a test on the dispatcher''s command, the portability tests extended by one case each [DEC-1050] (folds W2-11b F2) (folds W2-99 S6, F7)'
  - 'TPL-5 S1-S3 ticket.schema.json allows non_goals: [str] and a KPI line of the form {line, verify} beside the plain string, so every existing ticket stays valid; T-1 is the kernel ticket template, its verify the observable check; the ready check inside gov brief follows DEC-1052: a ticket missing a required field is not READY, computed by code (allowed_paths empty, a KPI line without verify, a depends_on not closed), and gov brief refuses it naming each; only advisory items warn and never refuse (non_goals missing, est_loc over 400). Verify: schema tests on both forms, the template test, one refusal test per required field, one warning test per advisory item, and one that it exits 0 with advisory warnings only [DEC-1050, DEC-1052, DEC-1083]'
  - 'TPL-6 S1-S4 Appendix A of governance/project/prompts/w2-orchestrator.md is a pointer to the templates under 600 characters; LEAD-w2-common.md is replaced by T-7 plus facts and build_lead_brief.py by gov brief lead; skills/test-design/SKILL.md''s read rule matches DEC-963 and skills/orchestration/SKILL.md "Briefs" points to the templates (K-4''s two lines in the same CIT-P); JUDGEMENT.md is a section of T-6 that no brief copies. Verify: a size test, the file removed or a pointer, string tests [DEC-963, DEC-1050]'
  - 'TPL-7 S1-S3 check_return.py <log.json> reports per return the twelve fields, the template: receipt equal to the injected version and the T-0 sections; template_report.py prints M1 to M6 for a date range, read-only, in under 60 s on the current logs, M3 per template line from each step''s match: pattern in facts.yaml; brief-gaps.md lists every brief_gaps line with its kind and its fix or "won''t fix" and why. Verify: fixture tests on 3 good and 3 bad returns, a fixture plus one timed run, a count of unrouted lines by kind [DEC-793, DEC-943, DEC-1050]'
  - 'TPL-8 S1-S3 Three tickets of different roles and run kinds (an engineer build, a product-spec, a FULL review) run with the new templates, and template_report.py reports M1 to M6 against R2''s baselines in the pilot record; target M1 = M2 = 100 %, M3 at least 90 % per kept line, M4 at most 2 non-contention gap lines a return, M5 refusals only where no working form was given, M6 wait calls at most 5 % of calls, no wrappers written, at most 1 harness denial a session, at most 12 calls before the first launch; a target missed goes to the gap log and a facts, template or tool fix, never a new paragraph; after the pilot every new lead and worker brief comes from gov brief. Verify: the pilot record; M1 over a week [DEC-943, DEC-1050]'
  - 'Links recorded at the source (DEC-1073 (5)(c)): each role template (T-2 to T-8), the ticket template (T-1) and the record templates (decision-record, lesson, research, checkpoint, failure) carry LINK-INTEGRITY.md §5''s lines for the records that role writes. Verify: a string test per template, and gov links on a planted record filled from each template''s example gives no finding [DEC-1073, DEC-866, DEC-182, DEC-927]'
  - 'The facts file''s commands hold links (gov links --since {BASE}) with its check form; the lead template''s return quotes its first line [DEC-1073, DEC-927]'
  - 'The lesson, failure and research schemas allow sources (ids), and research decisions, both optional; every existing record stays valid [DEC-1073]'
  - 'The kernel part goes through one CIT-P under CAP-33 (evidence R2 and R3, an independent review, the owner''s approval, a versioned promotion), recorded in docs/changes/W2-128-CIT-P.md; the .claude/ copies are installed by the owner''s operator as an ACT [CAP-33, DEC-1050, DEC-1081]'
  - 'The reviewer states, per finding, what evidence would reverse it [DEC-1014, SMART-WORK-4 line 4] [moved from W2-11b S2, DEC-1083]'
  failure:
  - 'A template names a path or command that is not in facts.yaml (TPL-1 F1, TPL-2 F1).'
  - 'Two runs of gov brief on the same inputs differ (TPL-3 F1).'
  - 'A launched session starts without its role template (TPL-4 F1).'
  - 'The ready check refuses a ticket for an advisory item, or lets a ticket missing a required field through as READY (TPL-5 F1, as DEC-1083 amends it).'
  - 'Two template-bearing files state different rules for the same step: /doctor prompt-audit, run once by the reviewer, reports a conflict in .claude/ (TPL-6 F1; a review step, not a gate).'
  - 'A measure blocks a launch, a close or a landing: none is called from gov launch, gov close or land.py (TPL-7 F1, a grep test).'
  - 'A template line that states a rule cites a PROPOSED or superseded decision as the rule.'
profile: STANDARD
sources:
- DEC-1050
- DEC-1052
- DEC-1083
- DEC-1081
- DEC-974
- DEC-1079
- DEC-1073
- DEC-866
- DEC-182
- DEC-927
- DEC-957
- DEC-959
- DEC-963
- DEC-1010
- DEC-793
- DEC-943
- CAP-33
est_loc: 400
acceptance_tests:
  path: tests/acceptance/W2-128/
  author: independent-test-designer (MR-3), from R3's KPI lines
track: A
list_rows: []
---
# W2-128 The templates (P1-7, R3-TEMPLATES §D)

Filed 2026-11-06 by the CTO on the owner's approval (DEC-1081 (2), DEC-974). The work package is R3's eight
packages TPL-1 to TPL-8 (`governance/project/orchestration/packages/LIFT-1/R3-TEMPLATES.md` §D, the templates in its
Appendix), shaped by R2's evidence (P1-PLAN P1-7), plus LINK-INTEGRITY.md §6.1's three lines for this ticket.

- **Why:** bad briefs lose work (7,669 brief-gap minutes stated in 83 returns); four layers of brief text contradict
  one another, and role files never reach launched sessions (R3-1 to R3-3).
- **Order (R3 §D):** TPL-3b's scripts are done (CTO's tools, 2026-11-06); then TPL-2 and TPL-1 in parallel, then
  TPL-3, then TPL-4; TPL-5 beside TPL-3; TPL-6 after TPL-4 and the owner's row decisions; TPL-7 beside TPL-3; TPL-8
  last. The guard's G-1/G-2 fixes land before the templates drop the "the guard refuses here-documents" lines.
- **Roles:** product-spec writes the templates, the schemas and the kernel texts; an independent test designer writes
  the tests from these KPI lines first; one independent review. TPL-2's facts and TPL-6's project prompt are the
  CTO's lane. **The code parts, TPL-3's `gov brief` in the product and TPL-4's launcher flag, are an engineer's**,
  and `gov launch` starts an engineer only on an engineer's ticket: when they are reached, the CTO brings the owner a
  split (one engineer's ticket for them), so the paths here hold no `src/` path.
- **Unchanged:** W2-11 and W2-11b land as built and W2-128's lines replace theirs; W2-33's role files get the lines
  through these templates (TPL-4).
- **Estimate:** about 4 to 5 working days in all, parts in parallel (R3 §D, est.).
