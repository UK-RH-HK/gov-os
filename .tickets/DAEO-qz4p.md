---
id: DAEO-qz4p
status: open
deps: []
links: [DAEO-52ku, DAEO-61vm, DAEO-k1e2, DAEO-p8tv]
created: 2026-11-11T01:26:23Z
type: task
priority: 2
assignee: engineer
external-ref: W2-173
tags: [wave-2, implementation, memory, audit, full, after-the-lift]
wbs_id: W2-173
title: 'The launch script''s follow-ups for the audit: the brief''s effort passed to the session, a stop word for writers and checkers, the notes'' and classes'' form checked at delivery (DEC-1120, DEC-1101 (2))'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: []
allowed_paths:
- governance/project/orchestration/tools/indep_launch.py
- governance/project/orchestration/tools/indep-schemas/**
- tests/unit/orchestration/test_w2_173*
- docs/changes/W2-173-evidence.md
kpis:
  success:
  - 'S1 A brief''s front matter may name `effort` (one of `low`, `medium`, `high`, `xhigh`, `max`), and the launch script passes it to the session as `--effort <value>` and records it in `WALL.json` and in `counts.json` (the counts schema gains one field, `effort`, a string or null). A brief with no `effort` runs as today, with no `--effort` flag and `effort: null`; a value outside the five refuses with code 10 before anything is built. Verify: planted briefs with `high`, no line, and `loud`: the stub `claude` receives `--effort high`, no `--effort`, and the third launch exits 10 with the wall folder unchanged; the five set-up A briefs (no `effort`) still pass stage 10 and build dry walls [DEC-1120 (2)-(3), DEC-1101 (2)]'
  - 'S2 A writer''s or checker''s `result.json` may carry `stopped`, one of the closed words the labellers use (`none`, `input-missing`, `input-malformed`, `decisions-conflict`, `forbidden-read-needed`, `form-not-writable`, `not-sealed`); a result that says it stopped delivers nothing and ends with code 21 (`stopped`), with the word in `counts.json`, instead of the schema or missing-file code 20. The two result schemas gain `stopped` as an optional property. Verify: planted writer and checker results with each word: nothing delivered, exit 21, the word in the counts; a result with `none` and a set delivers as before; the first-version schemas still accept a result without `stopped` [DEC-1101 (2)]'
  - 'S3 The checker''s `notes.md` is checked at delivery against the audit briefs'' fixed form: the heading `# Cross-check notes`, a `## Questions` section with one line per file of the set in id order (`<id> | accept|revise|reject | <codes or -> | also: <...> | <sentence>`), a `## The set` section with its five lines; and the three verdict counts in `result.json` equal the lines'' counts. A notes file that does not fit delivers nothing and ends with code 20. Verify: planted notes: well formed (delivered); a missing line, a fourth verdict word, an id not in the set, counts that disagree (each refused 20, nothing written to the set''s folder) [DEC-1101 (2)]'
  - 'S4 The auditor''s `classes.json` is checked at delivery: one entry for each line of `input/misses.jsonl`, none for another id, each `class` one of the five, each `reason` one line of at most 200 characters, and the five counts of `result.json` equal the classes'' counts. Anything else delivers nothing and ends with code 20. Verify: planted classes: well formed (delivered); a missing id, an extra id, a sixth class, a two-line reason, counts that disagree (each refused 20) [DEC-1101 (2)]'
  - 'S5 Nothing else about the launch script changes: every existing exit code, check and the five set-up A flows behave as at `2f98aecbc`. Verify: `gov accept W2-149`''s cases pass unchanged (206/0/3 passed, failed and skipped at the merge; the live cases run by the CTO), and a diff of the script outside the four changes above is empty [DEC-1112 (3), DEC-1113]'
  failure:
  - 'A session started without the effort its brief names; an invalid `effort` that builds a wall. Verify: S1''s planted briefs: with `high` the stub `claude` receives `--effort high`; with `loud` the launch exits 10 and the wall folder is unchanged'
  - 'A stopped or malformed result delivered into a set''s folder or an audit''s folder. Verify: S2''s planted results with each stopped word, S3''s planted notes with a missing line and S4''s planted classes with a missing id: each is refused (21 or 20) and the set''s and the audit''s folders are byte-identical before and after'
  - 'A change to the walls'' template files, the approved list, the path map or the guard; to a set-up A brief''s bytes; to any exit code''s meaning. Verify: `git diff --name-only` of the ticket''s branch against its base lists none of those files, and S5''s diff of the script outside the four changes is empty with `gov accept W2-149`''s cases unchanged'
  - 'Any change outside the paths above. Verify: `git diff --name-only` of the ticket''s branch against its base lists only paths matched by the ticket''s allowed_paths'
profile: FULL
sources:
- DEC-1101
- DEC-1120
- DEC-1112
- DEC-1113
- DEC-1050
- DEC-1073
est_loc: 200
acceptance_tests:
  path: tests/acceptance/W2-173/
  author: 'independent-test-designer (MR-3), Sonnet high (RUBRIC-2, class C2), from these KPI lines and W2-149''s tests, before the engineer: planted sets root, HOME and repository, a stub `claude` on PATH; never the real ~/gov-os-eval, ~/gov-os-runs or ~/.claude'
track: B
list_rows: []
reads:  # declared by the CTO 11-11 (gov brief READS_MISSING; DEC-1121): what it reads that it does not write
- governance/project/indep-walls/kinds.yaml
- governance/project/orchestration/packages/MEMORY-AUDIT-1.md
needs:
- governance/project/orchestration/tools/indep_launch.py
waits_on: []
---
# W2-173 The launch script's follow-ups for the audit

Found while drafting the memory audit's fixed briefs (`packages/MEMORY-AUDIT-1.md`): the launch script builds the
memory kinds' walls, but three gaps stand between it and the audit. It passes no `--effort`, so RUBRIC-2's effort high
(DEC-1120 (2)) is not enforced for an independent session. A writer or checker that must stop has no word for it (only
set-up A's results have one), so its stop reads as a missing file. And the checker's notes and the auditor's classes are
delivered unchecked, though the next steps read them by their form.

- **Base:** W2-149, merged at `2f98aecbc` (its ticket stays open for rows F37 and F40, which are not here). A change to
  the script after the owner's approved list is applied runs under that list unchanged (ACT-W2-149-INSTALL-1 §3, F34),
  so no new yes is needed; the walls' template files are not touched.
- **Alternatives (one line each):** put effort in the walls' `kinds.yaml` (rejected: a template change, so an ACT and
  the owner's new hash); leave the notes unchecked and let W2-170 reject a malformed file (rejected: the delivery
  would already have replaced the set's folder).
- **From W2-170's Interface (row 147, the CTO's reading 1, 2026-11-11):** the auditor's copy of an audit's set excludes
  `hidden/dropped/` (the dropped questions); every other file of the set is copied as today.
- **Not here:** the briefs, the schedule, the measure.

[DEC-1120 (2)-(3); DEC-1101 (2)]
