---
id: DAEO-esl1
status: open
deps: []
links: []
created: 2026-11-24T18:00:00Z
type: task
priority: 1
assignee: engineer
external-ref: W2-211
tags: [decisions, escalation, decisions-by-page, kit]
wbs_id: W2-211
title: "Decisions by page, slice (a): the record's fields, the sheet and `gov decisions answer`, with the escalation rubric's first slice (the level computed from stated facts, a decision below its level refused)"
class: implementation
kind: feature
state_class: AUTHORITATIVE
role: engineer
profile: FULL
depends_on: []
waits_on: []
specification: docs/emergency-2/proposals/DECISIONS-BY-PAGE-SPEC.md
allowed_paths:
- src/gov/decisions/**
- template/governance/kernel/templates/decision-package.md
- template/governance/kernel/templates/decision-record.md
- template/governance/kernel/assets/decisions-sheet.js
- template/governance/kernel/schemas/decision-package.schema.json
- governance/project/escalation.yaml
- tests/unit/decisions/**
- governance/project/path-map.yaml
kpis:
  success:
  - 'PG-1 A package carries question, what was found, 2 to 6 options each with a cost and a consequence, a recommendation that names one of them with a reason and a confidence, sources that exist, and `blocks`; `gov decisions page` takes a package only when all of that holds and within the limits, and says for each other open package the field that is missing, too long or false. Fails if: a package with a missing field, an over-limit text, a recommendation naming no option or a source that does not exist is put on a page, or a refusal names no field. Verify: build packages with each defect planted (a field missing, an over-limit text, a recommendation on option `z`, a source path that is not there, a bad `rubric`) and one clean: `page` takes the clean one and names exactly each planted field for the others; the schema accepts a package with none of the new fields'
  - 'PG-3 The sheet is the fixed block of the grammar above: the page and the Python writer produce byte-identical sheets for the same picks and notes (including `|`, quotes, accents, emoji and line breaks in a note), and the parser reads a sheet that the chat wrapped (a fence, quote marks, CRLF, text around it). Fails if: the two writers differ for any pick or note, a note is lost or altered beyond its line breaks, or a wrapped but intact sheet is refused. Verify: run the page''s script under `node` with a small stand-in for the document, for a fixed set of picks and notes; compare its text byte for byte with the Python writer''s; feed the parser the sheet inside a fence, with quote marks, with CRLF and with text around it. A missing `node` fails the test as an environment fault; it is never skipped'
  - 'PG-4 `gov decisions answer` on a valid sheet writes one register entry per picked option, in the form of DEC-1225 to DEC-1231 (title, an `ACCEPTED (owner, <date>, on the decisions page <batch>, answer <id>` status line, the option and the owner''s note verbatim, a basis naming the batch and the finding, the sources), with consecutive free ids in the sheet''s order; sets each package to ACCEPTED with its answer filled; stores the sheet; and makes one commit with `Task: decision-record`, `Role: orchestrator` and `Decided-by: owner (page <batch id>)`. Fails if: an entry differs from that form, an id is reused or skipped, a note is changed, a package stays PROPOSED after its entry, the commit lacks a trailer, more than one commit is made, or `gov decisions basis` or `gov links` finds something new in the written entries. Verify: on a scratch register with the real entry form, answer a sheet of three picks and one `skip`; compare each new entry with the expected text; read the status line with `owner_decision`; run `gov decisions basis --range HEAD^..HEAD` and `gov links --since HEAD~1`; read the commit''s trailers; read the three package files and the stored sheet'
  - 'PG-5 A sheet with the wrong hash, an unknown or missing or duplicate id, an option the card does not have, a changed or already answered or withdrawn package, a bad date, a bad count or a note over 400 characters, or run by a role other than the orchestrator, or over uncommitted decision files, is refused with its code and changes nothing. Fails if: any file, the register or the history differs after a refusal, a refusal carries no code, or a sheet of another batch is accepted. Verify: one sheet per refusal code (each from a good sheet with one change); compare a snapshot of the tree and `git rev-parse HEAD` before and after, and the code printed'
  - 'PG-6 The same sheet pasted twice changes nothing the second time and exits 0, naming the entries it already made; a `skip` leaves its package open, and a fuller sheet of the same batch answers only what is open; a different option for an answered package is refused. Fails if: a second paste writes an entry or a commit, a `skip` writes anything, or a later answer duplicates an earlier one. Verify: paste twice (second: no diff, exit 0); answer with a `skip`, then a fuller sheet of the same batch; then the same card with another letter'
  - 'EL-1 The level computed from stated facts. A decision record states three facts: `touches` (what it changes: a spec or KPI, a standing decision, the Contract or Charter, shared code, work across streams, kernel text, a secret or paid service, a model or effort, a release, or only its own ticket), `reversible` (yes or no) and `inside` (a worktree, the repository, or outside it). Code computes its level (P3 lead, P2 CTO, P1 owner, or emergency) from those facts by the escalation rubric (golden workflow rule 8 in `docs/emergency-2/GOLDEN-WORKFLOW.md`; `docs/emergency-2/T2-ESCALATION-RUBRIC.md`) and prints the level with the facts that set it. Verify: a table of planted fact sets in the test, each with its expected level; `gov decisions level` prints the level and the facts that set it.'
  - 'EL-2 A decision below its level is refused. A record whose `Decided-by` is below its computed level (a P1 record not decided by the owner; a P2 record decided by a lead) is refused with `DECISION_BELOW_LEVEL`, naming the computed level and the facts, at the check every decision-record commit runs (`gov decisions basis --range`) and by `gov decisions answer`; a P1 record without the owner''s decision becomes an open package (a card), never an ACCEPTED entry. Verify: a record with `touches: [spec]` and `Decided-by: CTO` is refused naming P1; a P2 choice written inside an owner''s decision (the form of DEC-1247) passes; a lead-decided P2 record is refused; `answer` runs the same check.'
  - 'EL-3 Through the kit. The record fields, the level rule and the check reach an adopted repository by `gov update` (PG-9''s road), and its own decisions are judged by the same rule. Verify: the fields are in the kit''s package template and schema, the level table is in the kit, and a scratch adopted repository''s record below its level is refused after `gov update`.'
  failure:
  - 'F-EL A decision below its level is accepted, an entry with stated facts gets a level the rubric table does not give, or a refusal names no level or no fact. Verify: the EL-1 and EL-2 tables.'
  - 'F-PG A refusal changes a file or the history, a second paste writes anything, or a package missing a field is put on a batch. Verify: the PG-1, PG-5 and PG-6 cases.'
non_goals:
- 'Slice (b): the page renderer, the push text, the --week and status lines (PG-2, PG-7, PG-8)'
- 'Kernel prose (rubric lines in skills and role files): the CTO''s change'
done_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]
sources: [DEC-1236, DEC-1242, DEC-1246, DEC-1247, docs/emergency-2/proposals/DECISIONS-BY-PAGE-SPEC.md, docs/emergency-2/T2-ESCALATION-RUBRIC.md, docs/emergency-2/GOLDEN-WORKFLOW.md]
acceptance_tests:
  path: tests/acceptance/W2-211/
  author: independent-test-designer (MR-3); written before implementation
track: F
---
# W2-211: decisions by page, slice (a), with the escalation rubric's first slice

Approved feature (DEC-1236 (1), DEC-1242 T-1 (b), R-6 (a), DEC-1246 (3)(b)); item 5-4 of the integration plan. Lead's
brief: `docs/emergency-2/briefs/LEAD-w2-211-*.md`. Slice (b) is a separate ticket.

## Interface (the lead's choices where the spec and the brief leave one)

**Files.** `src/gov/decisions/package.py` (fields, limits, `page_ready(package)`, content hash), `sheet.py` (`write_sheet`,
`parse_sheet`, `batch_hash`), `answer.py`, `level.py` (`compute_level(facts) -> {level, facts, reasons}`,
`judge_entry`), `command.py` gains `answer` and `level`; `template/governance/kernel/assets/decisions-sheet.js` is the
sheet writer in JavaScript (the page of slice (b) embeds it; PG-3's parity is run against it under `node`).
Batches live in `docs/decisions/batches/<batch>.manifest.json` (batch id, created date, hash, cards in order with each
package's content hash); `--batches <dir>` and `--register <path>` override; defaults as the spec's configuration.

**The record's facts.** In a package's frontmatter: `touches` (list; words below), `reversible` (yes|no), `inside`
(worktree|repository|outside), optional `spends` (yes|no), `rounds` (int), `emergency` (yes|no). In a register entry: a
status-line or bullet field `**Touches:** spec, kpi`, `**Reversible:** yes`, `**Inside:** repository` (also `**Spends:**`,
`**Rounds:**`, `**Emergency:**`). Words for `touches`: `spec`, `kpi`, `standing-decision`, `contract`, `charter`,
`shared-code`, `cross-stream`, `kernel-text`, `secret`, `paid-service`, `model-effort`, `release`, `own-ticket`.
`Decided-by` is the commit trailer of the commit that adds the entry: `owner (...)`, `CTO`, `lead`
(also `orchestrator`=CTO, `senior-engineer`=CTO). An entry with no stated facts is not judged (verdict `unstated`, listed);
a package with facts missing is not page-ready.

**The rule (data in `governance/project/escalation.yaml`, the code's default the same).** Level = the highest of the
touches level and the place level; `emergency: yes` gives `emergency`; `rounds` of 3 or more (a review not converged
after two) gives P1; `spends: yes` gives P1.

| touches | level |
|---|---|
| spec, kpi, standing-decision, contract, charter, secret, paid-service, model-effort, release | P1 |
| shared-code, cross-stream, kernel-text | P2 |
| own-ticket | P3 |

| reversible / inside | worktree | repository | outside |
|---|---|---|---|
| yes | P3 | P2 | P2 |
| no | P2 | P1 | P1 |

Deciders rank owner > CTO > lead; a decider at or above the level passes (the owner may decide any level; a P2 call inside an
owner's decision is not a separate record). `emergency` is the owner's. Refusal: `DECISION_BELOW_LEVEL`, message names the
level and the facts. `gov decisions level --touches a,b --reversible yes|no --inside worktree|repository|outside
[--spends] [--rounds n] [--emergency]` prints `level: P1 (touches spec; reversible yes; inside worktree)`, exit 0; a package
path in place of flags reads its frontmatter; an unknown word exits 1 `LEVEL_FACT_INVALID`.
