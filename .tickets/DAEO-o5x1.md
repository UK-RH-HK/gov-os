---
id: DAEO-o5x1
status: in_progress
deps: []
links: [DAEO-t8mp]
created: 2026-11-09T20:40:06Z
type: task
priority: 1
assignee: engineer
external-ref: W2-152
tags: [wave-2, templates, brief, readiness, standard]
wbs_id: W2-152
title: 'gov brief: a filled brief from the ticket and the facts file, refused when the ticket is not READY by code (W2-128 TPL-3, TPL-2 S3, TPL-5 S3 and the dependency fields; the CTO''s split, DEC-1112 (3))'
class: tool
state_class: AUTHORITATIVE
role: engineer
depends_on: []
allowed_paths:
- src/gov/brief/**
- tests/unit/brief/**
- governance/project/facts.yaml
- template/governance/kernel/schemas/facts.schema.json
- docs/changes/W2-152-evidence.md
kpis:
  success:
  - 'S1 gov brief <role> <ticket> prints on stdout the filled T-0 (template/governance/kernel/templates/brief.md) for that role, from only the ticket file, governance/project/facts.yaml and the kernel templates; two runs on the same inputs are byte-identical. Verify: a golden-file test per worker role on a fixture repository [DEC-1050, DEC-1052] (W2-128 TPL-3 S1)'
  - 'S2 It refuses (GovError BRIEF_NOT_READY, non-zero exit) naming each placeholder left unfilled (PLACEHOLDER_LEFT <key>) and each KPI line without a verify (KPI_NO_VERIFY <S|F><n>). Verify: one test per refusal [DEC-1050] (TPL-3 S2)'
  - 'S3 It prints the ready check''s warnings and the filled size against R3 §C''s budget (facts.yaml budgets) on stderr; a warning never stops it. Verify: tests [DEC-1050] (TPL-3 S3)'
  - 'S4 --part <file> fills {LEAD_NOTE} and --repair <file> fills {REPAIR}, "none" when absent; no text of the role''s own template is in the stdin brief (the role template goes as the system prompt, W2-153), except for a lead the one run section S6 selects. Verify: a test that no line of role-<x>.md but that section appears in the output [DEC-1050] (TPL-3 S4)'
  - 'S5 It refuses (UNTIL_CLOSED <ticket>) a template line or a --part line holding "until <ticket>" when that ticket''s status is closed. Verify: a test with a closed fixture ticket [DEC-1050] (TPL-3 S6)'
  - 'S6 gov brief lead <ticket> --run tests|build|review|resume|land carries only that run kind''s block of T-7 (role-lead.md''s "## Your run: {RUN_KIND}" section, where each kind''s block begins with a line "**<kind>**:" and runs to the next such line or the section''s first {STEP:} line), with {RUN_KIND} filled. Verify: one golden file per kind [DEC-1050] (TPL-3 S7)'
  - 'S7 A steps switch in facts.yaml turned off removes its one {STEP:name} line from the filled brief and changes nothing else. Verify: a generator test with one switch flipped [DEC-1050] (W2-128 TPL-2 S3)'
  - 'S8 The ready check (inside gov brief) follows DEC-1052 and DEC-1083: a ticket missing a required field is not READY and is refused, naming each (ALLOWED_PATHS_EMPTY; KPI_NO_VERIFY; DEPENDS_NOT_CLOSED <id>); only advisory items warn and never refuse (NON_GOALS_MISSING; EST_LOC_OVER <n> above 400). Verify: one refusal test per required field, one warning test per advisory item, and one that it exits 0 with advisory warnings only [DEC-1052, DEC-1083] (TPL-5 S3)'
  - 'S9 Dependency fields (DEC-1088 (3)): a ticket created on or after facts.yaml ready.new_since without reads:, needs: or waits_on: is refused by name (READS_MISSING, NEEDS_MISSING, WAITS_ON_MISSING; an empty list is a declared none); each waits_on id or record path must exist (WAITS_ON_UNKNOWN <ref>); a ticket created before the date is not refused for them. Verify: the ready check on planted tickets either side of the date [DEC-1088, DEC-1052]'
  - 'S10 facts.yaml gains ready.new_since (an ISO date, the day this ticket lands) and the schema declares it; W2-128''s acceptance cases still pass. Verify: the schema test and gov accept W2-128 [DEC-1050]'
  failure:
  - 'Two runs of gov brief on the same inputs differ (TPL-3 F1).'
  - 'The ready check refuses a ticket for an advisory item, or lets a ticket missing a required field through as READY (TPL-5 F1, as DEC-1083 amends it).'
  - 'gov brief writes any file, or reads anything beyond the ticket file, facts.yaml, the kernel templates and the --part/--repair files (a filesystem-spy test).'
profile: STANDARD
sources:
- DEC-1050
- DEC-1052
- DEC-1083
- DEC-1088
- DEC-1112
- DEC-1109
est_loc: 380
acceptance_tests:
  path: tests/acceptance/W2-152/
  author: independent-test-designer (MR-3), from these KPI lines and W2-128's interface
track: A
list_rows: []
---
# W2-152 gov brief (W2-128's code half, part 1)

**Why.** W2-128 (`DAEO-t8mp`) holds the templates; its code half could not be built on a product-spec ticket. The CTO
split it into two engineer tickets (a delegated P2 under DEC-1112 (3); `governance/project/orchestration/packages/LIFT-1/D5-STATUS.md`):
this one (`gov brief`, the ready check) and W2-153 (delivery at launch). W2-128's S7, S6's S3, S10's S3 and S19's
refusals are built here; W2-128 closes after both.

**Interface (D5 row 9, stated before the pair starts).**
- **Command:** `src/gov/brief/command.py` (the CLI finds it as `gov brief`): `gov brief <role> <ticket> [--run <kind>] [--part <file>] [--repair <file>] [--root <repo>] [--json]`.
  `<role>`: `engineer`, `independent-test-designer`, `independent-auditor`, `product-spec`, `research`, `lead`;
  `<ticket>`: a tk id (`DAEO-…`) or a W2 id, resolved in `<root>/.tickets/`.
- **Inputs, read only:** the ticket's front matter and body; `<root>/governance/project/facts.yaml`; the kernel
  templates at `<root>/template/governance/kernel/templates/` (else `<root>/governance/kernel/templates/`), with
  `keys.yaml`. The role → template map: engineer `role-engineer`, independent-test-designer `role-test-designer`,
  independent-auditor `role-reviewer`, product-spec `role-product-spec`, research `role-research`, lead `role-lead`.
- **Placeholders** as W2-128's interface states (`{KEY}`, `{KEY: description}`, `{CMD:name}`, `{STEP:name}`);
  `{WRITE_TREE}` is `{TESTS_TREE}` for a test designer and `{TREE}` otherwise; `{STEP:name}` is the step's `line:`
  when `on: true`, and the whole line holding it is dropped when off.
- **A KPI line has a verify** when it is `{line, verify}` with a non-empty `verify`, or a string holding `Verify:`
  followed by text (so today's tickets need no rewrite).
- **Output:** without `--json`, stdout is the brief text alone; warnings and the size line on stderr, each
  `gov brief: <CODE> <detail>`. With `--json`, the API-0002 envelope with `result.brief`, `result.warnings`,
  `result.size`, `result.budget`. A refusal is `GovError("BRIEF_NOT_READY", …)` with `details.findings` a list of
  `{code, detail}`; nothing on stdout.
- **facts.yaml** gains `ready: {new_since: <ISO date>}`; nothing else in it changes here.

**Not here:** the launcher flag and the generated copies (W2-153); the templates' text (W2-128).
