---
name: backend
description: >-
  The engineer's method for backend work: conventions, a pre-commit checklist,
  unit-test focus, common mistakes and when to escalate. Used for a ticket that
  changes server-side code, jobs, queues or migrations.
metadata:
  version: 1.0.1
---
# Backend

The engineer's skill for server-side work (DEC-957 Q5, DEC-959 item 4): services, handlers, jobs, queues and the
migrations that go with them. It is loaded beside the engineer role and the engineer's vendored skills
(test-driven-development, systematic-debugging, verification-before-completion), and refers to them without restating
them. The guard, the launcher and the role file decide what the session may do; this skill is a method only and grants
nothing (CAP-24.b). Its three scenarios: [scenarios.md](scenarios.md); its own check: `check_domain_skill.py`, in this
folder.

## When / not when

- Use it when the ticket changes code that runs on a server: request handlers, background jobs, queue consumers, data
  access, configuration read at start-up, or a migration that serves them.
- Not when the work is an interface's contract or version (use the api skill), the shape or quality of stored data
  (use the data skill), or a security control (use the security skill); load it beside them when a ticket spans two.

## Inputs

Read first, before anything else:

- the ticket: its KPI lines, its allowed paths and its sources;
- the code beside the change, to follow its naming, layout and error style before adding another;
- what else it needs to know beyond those, through `gov retrieve` first (DEC-836).

## Conventions

- Follow the repository's own naming, layout and error types first; where it has none, one module per concern, and the
  handler thin: parse, call, respond.
- Error handling: a failure is caught where it can be handled and raised or returned where it cannot; the error carries
  what failed and the inputs' identity, never a secret; a retryable failure is told apart from a permanent one; no
  bare catch-all that swallows.
- Idempotence: any operation a retry, a redelivery or a double click can repeat is made safe to repeat, by a key taken
  from the request or the message and a unique constraint or an upsert, never by hoping it runs once.
- Migration: a schema change ships as small reversible steps (add, write both, backfill, switch, remove later), each
  with its way back, and never in the same change as the code that needs the old shape gone.
- Configuration comes from the environment or the project's config, never from a constant in code; timeouts and
  retry limits are set, not left at a default.

## Steps

Copy this checklist into your notes and tick each step as you go.

- [ ] 1. Read the ticket's KPI lines and paths; list the operations that change state, and for each say what happens if
  it runs twice or fails half-way.
- [ ] 2. Write the unit test first, following the test-driven-development skill; the test names the failure, not only
  the success (Unit-test focus below).
- [ ] 3. Write the smallest code that makes it pass, with the error handling and the idempotence stated in Conventions.
- [ ] 4. For a migration, write the steps and each way back, and run them forward and back on a copy of the data (the
  copy is a fixture or a throw-away database in the sandbox, never a live one).
- [ ] 5. Run the whole unit suite of the touched area, then the Pre-commit checklist below.
- [ ] 6. Run the acceptance tests only through `gov accept`; read the pass or fail and never the test code.
- [ ] 7. Write the return (Output and handover) and commit with the ticket's trailers.

## Pre-commit checklist

- [ ] Every state-changing operation is safe to repeat, or the return says why it cannot be.
- [ ] No `except` that swallows: each is logged, returned or raised, and none hides a failed write.
- [ ] No secret, host or credential in the diff; configuration read from the environment.
- [ ] Each migration has its down step and was run forward and back; none drops data in the change that stops using it.
- [ ] Timeouts, retry limits and batch sizes are set on every outbound call and loop.
- [ ] Logs carry identifiers, never personal data or tokens.
- [ ] The diff touches only the ticket's allowed paths, and the suite of the touched area passes.

## Unit-test focus

The method is the test-driven-development skill's; this is only where a backend's tests look.

- The failure path of every handler: bad input, a failing dependency, a timeout.
- A duplicate delivery or a second call: the state after two runs equals the state after one.
- A migration forward and back on a small fixture, and the old reader against the new shape.
- A half-failed batch: what is committed, what is retried, what is reported.
- Boundaries (empty, one, many, at the limit) rather than a single typical case; no test waits on a clock or the network.

## Common mistakes

- A catch-all that logs and carries on, so a failed write looks like a success.
- An insert on every delivery, so a retry makes a second row.
- A rename or drop in one migration while an older version of the service still runs.
- A retry loop with no limit or no backoff, which turns one slow dependency into an outage.
- A default timeout of none; a constant where the environment's value belongs.
- A fix made in shared code outside the ticket's paths (Escalation).

## Done when

- The unit suite of the touched area passes, and each state-changing operation has a test of its second run.
- The Pre-commit checklist is ticked line by line; a line that cannot be ticked is named in `risks`.
- `gov accept` reports pass for the ticket, or the return says it was not run and why. If it fails: fix, then check
  again.
- The diff holds only the ticket's paths.

## Output and handover

- The return starts with the twelve fields, each a labelled line (task, status, work_completed, files_changed,
  evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action), with any
  payload after them; refused twice for the same call, stop and return; an authentication error returns
  `AUTH_REQUIRED` (the orchestration skill's briefs-and-returns.md).
- This skill adds no output path of its own (`output: none`). Name in `discoveries` an interface point the ticket left
  open and the simplest reading taken; name in `risks` a checklist line that could not be ticked.

## Escalation

**When to escalate:** ranked by the escalation rubric (P3, P2, P1, Emergency; DEC-1219 (2)), to whoever started the
session, never to the owner directly.

- P3: a choice that is reversible, inside the ticket and changes no KPI (a name, a module split, a timeout value);
  decide, log it in `discoveries` and go on.
- P2: the fix needs shared code or another stream's files, or a change to the ticket's scope or KPIs within the
  approved spec. Make what stays inside the paths, and return the rest as a package with the evidence.
- P1: the change is irreversible or destructive (a drop, a backfill that overwrites), weakens a guard rule or
  fails open, concerns secrets or security, costs money, or changes the spec or a standing decision. A package with
  options and a recommendation; the work waits.
- Emergency: a secret exposed, a risk of losing data, the disk below its floor, the guard failing open. Stop the
  affected work at once, then go up as a P1.

## Never

Reminders only: the guard decides.

- This skill changes no role's reads or writes. Work that needs other writes goes back as a package for the role that
  holds them, never routed round (DEC-995, DEC-996).
- Swallow an error, or retry without a limit.
- Run a migration against a live database, or one with no way back.
- Edit shared code outside the ticket's paths, or a test you dispute; both go up as a package.
- Read the acceptance tests, or code to make them pass; the code fulfils the spec and its KPIs.
- Edit the generated copy of this skill by hand: it is generated from this source (DEC-315).

## Sources

DEC-959 (items 4 and 5), DEC-957 (Q5 and the escalation rubric), DEC-832, DEC-616, DEC-645, DEC-315, DEC-1112 (3),
DEC-995, DEC-996, DEC-836, ROLES-RESEARCH-1 §2.7, CAP-24.b.
