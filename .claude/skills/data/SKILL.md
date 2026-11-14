---
name: data
description: >-
  The engineer's method for data work: conventions, a pre-commit checklist,
  unit-test focus, common mistakes and when to escalate. Used for a ticket that
  changes a schema, moves or transforms stored data, or loads data from outside.
metadata:
  version: 1.0.2
---
# Data

The engineer's skill for stored data (DEC-957 Q5, DEC-959 item 4): schemas, migrations, backfills, imports, exports and
the pipelines that move and transform records. It is loaded beside the engineer role and the engineer's vendored
skills (test-driven-development, systematic-debugging, verification-before-completion), and refers to them without
restating them. The guard, the launcher and the role file decide what the session may do; this skill is a method only
and grants nothing (CAP-24.b). Its three scenarios: [scenarios.md](scenarios.md); its own check:
`check_domain_skill.py`, in this folder.

## When / not when

- Use it when the ticket changes a table, a column, an index or a constraint, runs a backfill, loads or exports
  records, or changes what a stored value means.
- Not when the work is the service code around the data (use the backend skill) or an interface's contract (use the api
  skill); load it beside them when a ticket spans two.

## Inputs

Read first, before anything else:

- the ticket: its KPI lines, its allowed paths and its sources;
- the current schema and the migrations already written, and what reads and writes the data today;
- a sample of the data or a fixture of its shape, with its volume and who owns it;
- what else it needs to know beyond those, through `gov retrieve` first (DEC-836).

## Conventions

- Schema change: small steps in a fixed order (add as nullable or with a default, backfill in batches, then constrain;
  stop reading the old column before it is removed), each its own migration, never one step that locks a large table or
  breaks the running code.
- Migration: forward and down steps in the same change, named and ordered as the project's migration tool expects;
  written to be run twice without harm; the data moved is counted before and after.
- Rollback: every step states its way back; a step that cannot be undone (a drop, an overwrite) says so, keeps a copy
  first, and goes up as a P1 (Escalation).
- Data quality: rules stated per field (present, unique, in range, in a set, a valid reference) and applied before the
  load; a row that breaks one goes to a rejected-rows place with its reason, never silently dropped or silently fixed.
- Names, types and units follow the existing schema; a unit or a time zone is in the column's name or its comment.
- Personal or secret values are marked as such in the schema and are not copied into fixtures, logs or examples.

## Steps

Copy this checklist into your notes and tick each step as you go.

- [ ] 1. Read the ticket's KPI lines and paths, the current schema and a sample; list what reads and writes the data.
- [ ] 2. State the data-quality rules for each field the ticket touches, and the counts that will be reported.
- [ ] 3. Write the unit tests first, following the test-driven-development skill, with bad rows and a small fixture
  (Unit-test focus below); name each test with its bad row, in your notes and in the return.
- [ ] 4. Write the schema change as small steps, each with its down step, and say which are reversible.
- [ ] 5. Run each step forward and back on a fixture or a throw-away database in the sandbox, never on live data,
  comparing counts before and after.
- [ ] 6. Run the unit suite of the touched area, then the Pre-commit checklist below.
- [ ] 7. Run the acceptance tests only through `gov accept`; read the pass or fail and never the test code.
- [ ] 8. Write the return (Output and handover) and commit with the ticket's trailers.

## Pre-commit checklist

- [ ] Every migration has a down step, or says why it has none and was escalated.
- [ ] No step takes a long lock or breaks the code that is running while it runs.
- [ ] A backfill runs in batches and can be stopped and restarted.
- [ ] Row counts match before and after, and rejected rows are kept with a reason.
- [ ] Each data-quality rule has a test with a row that breaks it.
- [ ] No personal data, secret or production extract in a fixture, log or example.
- [ ] The diff touches only the ticket's allowed paths, and the suite of the touched area passes.

## Unit-test focus

The method is the test-driven-development skill's; this is only where data tests look.

- Each data-quality rule with a row that breaks it (empty, duplicate, out of range, orphaned) and a row that passes.
  Name the test for the rule and its bad row, and the reason the row is rejected with (for example "test_blank_key:
  a row with a blank key is rejected as `key_missing` and kept in the rejected rows"); a count of tests is
  not a name.
- A migration forward and back on a small fixture: the shape, the counts and a sample of values.
- A backfill stopped half-way and restarted: no row done twice, none skipped.
- The old reader against the new schema, and the new reader against old rows.
- Boundaries of types and units: null, empty string, the largest value, a time zone change at midnight.

## Common mistakes

- One migration that adds a NOT NULL column to a table that holds rows, or rewrites a large table in one transaction.
- A drop or a rename in the same change that stops using the old name.
- A migration with no down step, or a down step never run.
- Loading whatever parses: bad rows dropped without a trace, or "fixed" without a record.
- A backfill that overwrites without keeping the old value, or runs on live data to try it.
- A fixture copied from production with real names in it.

## Done when

- Each migration step ran forward and back on a fixture, with counts that match, and each irreversible step is named.
- Each data-quality rule has a passing test with a bad row.
- The Pre-commit checklist is ticked line by line; a line that cannot be ticked is named in `risks`.
- `gov accept` reports pass for the ticket, or the return says it was not run and why. If it fails: fix, then check
  again.

## Output and handover

- The return starts with the twelve fields, each a labelled line (task, status, work_completed, files_changed,
  evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action), with any
  payload after them; refused twice for the same call, stop and return; an authentication error returns
  `AUTH_REQUIRED` (the orchestration skill's briefs-and-returns.md).
- This skill adds no output path of its own (`output: none`). State in `evidence` the counts before and after, and in
  `risks` each step that cannot be undone and each rule left unchecked.
- In `tests`, list each test by name with its bad row and the rejection reason it expects, one line per rule, whether
  it was written and run or only planned because a write or run was refused; say which. Never only a count of tests.

## Escalation

**When to escalate:** ranked by the escalation rubric (P3, P2, P1, Emergency; DEC-957), to whoever started the
session, never to the owner directly.

- P3: a choice that is reversible, inside the ticket and changes no KPI (a column's name, a batch size, a rejected-rows
  table's layout); decide, log it in `discoveries` and go on.
- P2: the change touches a table or a pipeline another stream reads, changes the ticket's scope or KPIs within the
  approved spec, or revises older tests under an existing decision. Make what stays inside the paths and return the
  rest as a package.
- P1: a step that is irreversible or destructive (a drop, an overwrite, a delete without a kept copy), personal data
  that cannot be secured, a change to the spec or a standing decision, cost or a paid service. A package with options
  (export first, keep, drop with approval) and a recommendation; the step is not run.
- Emergency: a secret in the data, a risk of losing data, the disk below its floor, the guard failing open. Stop the
  affected work at once, then go up as a P1.

## Never

Reminders only: the guard decides.

- This skill changes no role's reads or writes. Work that needs other writes goes back as a package for the role that
  holds them, never routed round (DEC-995, DEC-996).
- Run a destructive step, or any step, against live data; try it on a fixture or a throw-away copy.
- Drop or rewrite the only copy of data, or write a migration with no way back and no kept copy.
- Drop bad rows without a trace, or put real personal data in a fixture, log or example.
- Edit another stream's tables or pipelines, or a test you dispute; both go up as a package.
- Read the acceptance tests, or code to make them pass; the code fulfils the spec and its KPIs.
- Edit the generated copy of this skill by hand: it is generated from this source (DEC-315).

## Sources

DEC-959 (items 4 and 5), DEC-957 (Q5 and the escalation rubric), DEC-832, DEC-616, DEC-645, DEC-315, DEC-1112 (3),
DEC-995, DEC-996, DEC-836, ROLES-RESEARCH-1 §2.7, CAP-24.b.
