---
name: api
version: "1.0.2"
description: "The engineer's method for API work: conventions, a pre-commit checklist, unit-test focus, common mistakes and when to escalate. Used for a ticket that adds or changes an interface other code or clients call."
output: none
metadata:
  version: "1.0.2"
---

# API

The engineer's skill for interfaces that other code or other people call (DEC-957 Q5, DEC-959 item 4): HTTP and RPC
endpoints, events, command-line surfaces and library signatures that have callers outside the ticket. It is loaded
beside the engineer role and the engineer's vendored skills (test-driven-development, systematic-debugging,
verification-before-completion), and refers to them without restating them. The guard, the launcher and the role file
decide what the session may do; this skill is a method only and grants nothing (CAP-24.b). Its three scenarios:
[scenarios.md](scenarios.md); its own check: `check_domain_skill.py`, in this folder.

## When / not when

- Use it when the ticket adds an interface, changes a request or response, changes an error, or retires something a
  caller uses.
- Not when the work is the code behind the interface only (use the backend skill) or the stored data (use the data
  skill); load it beside them when a ticket spans two.

## Inputs

Read first, before anything else:

- the ticket: its KPI lines, its allowed paths and its sources;
- the existing contract file (an OpenAPI or schema file, a protocol description) and its published versions;
- who calls the interface today, as far as the repository and the ticket show;
- what else it needs to know beyond those, through `gov retrieve` first (DEC-836).

## Conventions

- Contract-first: the contract is written or changed before the code, the tests come from the contract, and the
  handler is checked against it last. The contract file is the one place the interface is described.
- Versioning: a published interface carries a version in its path, header or package; a breaking change gets a new
  version, never a quiet change to the old one.
- Backward compatibility: within a version only additive change (a new optional field, a new endpoint, a new
  enum value the caller can ignore). A rename, a removal, a type change or a stricter rule is breaking, so a rename
  is done as add-the-new, keep-the-old (below).
- Deprecation: mark the old shape deprecated in the contract, keep it working, and name what replaces it and when it can
  go; removal is its own change, later.
- A ticket that asks for a rename or removal inside a published version is made additive where it can be: keep the
  old field, add the new one beside it, mark the old one deprecated in the contract, and test the old client's
  request for the old shape. What cannot be made additive (the old field really must go) is the only part escalated.
- One error shape for the whole interface, one status code per kind of failure, stable error codes callers can match
  on; a message is for people, a code is for programs.
- Names: nouns for resources, one casing, the same word for the same thing everywhere; follow the existing contract.

## Steps

Copy this checklist into your notes and tick each step as you go.

- [ ] 1. Read the ticket's KPI lines and paths and the current contract; list who calls what you change.
- [ ] 2. Write or change the contract first: requests, responses, every error, the version.
- [ ] 3. Mark each change as additive or breaking against the published version; make a requested breaking one
  additive where it can be (Conventions), and escalate only the rest (Escalation); never make it in place.
- [ ] 4. Write the unit tests from the contract, following the test-driven-development skill, including a
  backward-compatibility test for the old shape where one is kept (Unit-test focus below).
- [ ] 5. Write the handler or client code, and check it against the contract.
- [ ] 6. Run the unit suite of the touched area and the Pre-commit checklist below.
- [ ] 7. Run the acceptance tests only through `gov accept`; read the pass or fail and never the test code.
- [ ] 8. Write the return (Output and handover) and commit with the ticket's trailers.

## Pre-commit checklist

- [ ] The contract changed in the same commit as the code, and the code matches it.
- [ ] Each change is marked additive or breaking; no breaking change within a published version.
- [ ] A deprecated field or endpoint still works and is marked in the contract.
- [ ] Every error uses the interface's one error shape, with a stable code.
- [ ] Inputs are checked at the boundary and unknown fields are ignored, not trusted.
- [ ] No secret, internal host or personal data in a response, an example or a log line.
- [ ] The diff touches only the ticket's allowed paths, and the suite of the touched area passes.

## Unit-test focus

The method is the test-driven-development skill's; this is only where an interface's tests look.

- Each response and each error of the contract, checked against its schema, not only the happy path.
- Backward compatibility: a request in the old shape still gets the old response shape. Name that test for the old
  client and the shape it reads (for example "old v1 client: GET /v1/orders/{id} still returns `total`, as published"),
  next to any test that the new and old fields agree; the second does not stand in for the first.
- Input at the edges: a missing field, an extra field, a wrong type, an empty list, a value at the limit.
- Versioning: the same call on two versions answers each as published.
- Idempotent verbs repeat safely; a pagination or sort order is stable across calls.

## Common mistakes

- Code first, contract afterwards, so the contract describes what the code happened to do.
- A field renamed or removed within a published version because "nobody uses it".
- A new required field on an existing request, which breaks every old caller.
- An error shape that differs by endpoint, or a message that callers have to parse.
- A new enum value that callers' code does not handle; a type quietly widened.
- Returning more than the caller needs (an internal id, a stack trace, an email address).

## Done when

- The contract states every change, and each is marked additive or breaking.
- The tests pass for each response and error of the contract and for the old shape where one is kept.
- The Pre-commit checklist is ticked line by line; a line that cannot be ticked is named in `risks`.
- `gov accept` reports pass for the ticket, or the return says it was not run and why. If it fails: fix, then check
  again.

## Output and handover

- The return starts with the twelve fields, each a labelled line (task, status, work_completed, files_changed,
  evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action), with any
  payload after them; refused twice for the same call, stop and return; an authentication error returns
  `AUTH_REQUIRED` (the orchestration skill's briefs-and-returns.md).
- This skill adds no output path of its own (`output: none`). Name in `discoveries` each point the contract left open
  and the simplest reading taken, and in `risks` each caller you could not identify.
- In `tests`, name each test with its input and the result it expects, including the backward-compatibility test for
  the old shape, whether it was written and run or only planned because a write or run was refused; say which.

## Escalation

**When to escalate:** ranked by the escalation rubric (P3, P2, P1, Emergency; DEC-957), to whoever started the
session, never to the owner directly.

- P3: a point the contract leaves open that is reversible, inside the ticket and changes no KPI (an error body, a
  field name in a new endpoint); take the simplest reading, add it to the contract, log it in `discoveries`, go on.
- P2: a breaking change another stream's callers would feel, a change to shared schemas, or a change to the ticket's
  scope or KPIs within the approved spec. Keep the old shape working and return the rest as a package.
- P1: the interface cannot stay compatible with what the spec requires, a published version would be retired, or the
  change touches secrets or security, costs money or changes a standing decision. A package with options and a
  recommendation; the work waits.
- Emergency: a secret exposed in a response or an example, a risk of losing data, the guard failing open. Stop the
  affected work at once, then go up as a P1.

## Never

Reminders only: the guard decides.

- This skill changes no role's reads or writes. Work that needs other writes goes back as a package for the role that
  holds them, never routed round (DEC-995, DEC-996).
- Change, rename or remove anything in a published version; add a required input to an existing request.
- Write the handler before the contract, or leave the contract to describe what the code does.
- Edit a caller's code or a shared schema outside the ticket's paths, or a test you dispute; both go up as a package.
- Read the acceptance tests, or code to make them pass; the code fulfils the spec and its KPIs.
- Edit the generated copy of this skill by hand: it is generated from this source (DEC-315).

## Sources

DEC-959 (items 4 and 5), DEC-957 (Q5 and the escalation rubric), DEC-832, DEC-616, DEC-645, DEC-315, DEC-1112 (3),
DEC-995, DEC-996, DEC-836, ROLES-RESEARCH-1 §2.7, CAP-24.b.
