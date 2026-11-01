---
name: migration-review
version: "1.0.0"
description: "Reviews a database schema migration against ten checks, from reversibility and locking to the runbook, before it merges. Used by the engineer whose ticket adds or changes a migration."
metadata:
  version: "1.0.0"
---

# Migration review

The method an engineer follows to review a schema migration before it merges. There are ten checks. Each one
passes, or fails and is fixed or recorded as an exception. A runbook and rollback note is left beside the
migration. The guard, the launcher and the role file decide what a session may do; this skill is a method only and
grants nothing (CAP-24.b).

## When / not when

- Use it when a ticket adds or changes a schema migration in <the project's migrations folder>, before it merges.
- Not when the change is to data only, with no schema change: use <the project's data-fix procedure> instead.
- Not when a fresh session audits a migration that has already merged: use the audit skill instead.
- Not when the migration is being run or released: that belongs to <the project's release procedure>, not to this
  skill.

## Inputs

Read first, before anything else:

- the ticket, its acceptance tests and its allowed paths;
- the migration and its down migration, as the diff to be merged;
- the engine and its version: <the project's database engine>;
- the row count of each table the migration touches, from <the project's row-count source>;
- the application change that ships with it, and the deploy plan if there is one;
- what it needs to know beyond those, through `gov retrieve` first (DEC-836).

## Steps

Copy this checklist into your notes and tick each step as you go. A check that fails is either fixed and checked
again, or recorded as an exception in <the project's exception record>, with its reason and who accepted it.

- [ ] 1. Reversibility. A down migration exists. It was run on <a copy of the database>: up, down, up again, with
  the schema compared after each run. How to do this per engine: [reversibility.md](reversibility.md).
- [ ] 2. Locking. No statement takes a table-wide lock on a table over 1M rows. Look up each statement's lock
  level for the engine: [locking.md](locking.md). A lock that cannot be avoided escalates (P2).
- [ ] 3. Backfill in batches. Existing rows are filled in bounded, resumable batches, never in one statement over
  the whole table: [backfill.md](backfill.md).
- [ ] 4. Defaults on new non-null columns. A new NOT NULL column either has a default, or is added nullable,
  backfilled and then constrained: [defaults.md](defaults.md).
- [ ] 5. Indexes created concurrently. Every new index on a live table is built without blocking writes, in the
  engine's own way: [indexes.md](indexes.md).
- [ ] 6. Foreign keys validated separately. A new foreign key is added without validation and validated in a later
  statement: [foreign-keys.md](foreign-keys.md).
- [ ] 7. Types widened, never narrowed in place. A narrowing goes through a new column and expand/contract:
  [types.md](types.md).
- [ ] 8. Renames in expand/contract. No column or table is renamed in place. The rename follows the five steps,
  each step in its own deploy: [renames.md](renames.md).
- [ ] 9. Deploy order. The order of migration and application deploy is stated, and the application works with the
  schema both before and after the migration: [deploy-order.md](deploy-order.md).
- [ ] 10. Runbook and rollback note. Written from the template at <the project's runbook path>. It states whether
  a rollback loses data: [runbook.md](runbook.md). A rollback that loses data escalates (P1).
- [ ] 11. Record the result: the ten checks, each marked pass or exception, with the exception record's id.

## Done when

- All ten checks pass, or each failure is a recorded exception in <the project's exception record>. If one does
  not: fix it, then run the checks again.
- Any change to the migration after review means the ten checks are run again.

## Output and handover

- The return starts with the twelve fields, each a labelled line, with any payload after them; refused twice for
  the same call, stop and return; an authentication error returns `AUTH_REQUIRED` (the orchestration skill's
  briefs-and-returns.md).
- <the project's handoff kind for a reviewed migration>. The payload adds a table of the ten checks, each marked pass
  or exception; the ids of any exception records; the path of the runbook and rollback note; and any escalation
  raised.

## Escalation

- A lock that cannot be avoided on a table over 1M rows: P2, after the alternatives in locking.md have been tried.
- A rollback that loses data (a dropped column, a narrowed type, a destructive backfill): P1.
- Each goes, ranked by the escalation rubric (P3, P2, P1, Emergency; DEC-957), to whoever started the session,
  never to the owner directly.
- An Emergency (a secret exposed, a risk of losing data, the disk below its floor, the guard failing open) stops
  the affected work at once, then goes up as a P1.

## Never

Reminders only: the guard decides.

- Run a migration on production yourself, whether up, down or a "harmless" one, including to test or fix it.
- Point the reversibility test at anything other than <a copy of the database>.

## Sources

CAP-24.b (a skill grants nothing); DEC-836 (`gov retrieve` first); DEC-957 (escalation rubric); DEC-959 item 5
(scenarios first, body length, reference files); DEC-539 (project values as placeholders); DEC-832 item 2
(`metadata.version`); <the decision that adopts this skill>.
