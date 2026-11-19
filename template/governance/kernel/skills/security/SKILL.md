---
name: security
version: "1.0.1"
description: "The engineer's method for security-flagged work: conventions, a pre-commit checklist, unit-test focus, common mistakes and when to escalate. Used for a ticket that touches input, authentication, access, secrets or dependencies."
output: none
metadata:
  version: "1.0.1"
---

# Security

The engineer's skill for work that touches a trust boundary (DEC-957 Q5, DEC-959 item 4): input from outside,
authentication and access, secrets, data that must stay private, and dependencies. It is loaded beside the engineer
role and the engineer's vendored skills (test-driven-development, systematic-debugging,
verification-before-completion), and refers to them without restating them; the QA engineer loads the same skill for
its review. The guard, the launcher and the role file decide what the session may do; this skill is a method only and
grants nothing (CAP-24.b). Its three scenarios: [scenarios.md](scenarios.md); its own check: `check_domain_skill.py`,
in this folder.

## When / not when

- Use it when the ticket is security-flagged, or its change reads input from outside, decides who may do what, handles
  a credential or a personal value, or adds or updates a dependency.
- Not when the work has no trust boundary (use the skill of its area); load it beside the backend, api or data skill
  when a ticket spans two.

## Inputs

Read first, before anything else:

- the ticket: its KPI lines, its allowed paths and its sources;
- the trust boundary of the change: where input enters, who may call it, what it can reach, and which secrets it uses;
- the project's existing checks for input, access and secrets, to follow them before adding another;
- what else it needs to know beyond those, through `gov retrieve` first (DEC-836).

## Conventions

NIST's Secure Software Development Framework (SSDF, SP 800-218) is the frame, in its four groups; each says what the
engineer does with a ticket.

- Prepare the Organization: read the ticket's security flags and the project's standards before the first line; where
  a tool or a rule the work needs is missing, say so in `risks`.
- Protect the Software: secrets never in code (the environment or the secret store holds them, and a test uses a fake);
  the change keeps to the ticket's paths; a dependency is added only when the ticket names it, pinned.
- Produce Well-Secured Software: input check at every boundary (allow-list the shape, length and type; never trust a
  header, a path or a file name); queries parameterised; output encoded for where it lands; least privilege for every
  role, token and file mode, the narrowest that works; a denied request by default; no secret, token or personal value
  in a log or an error.
- Respond to Vulnerabilities: a weakness seen in the work goes up at once, as Escalation says, with where it is, how it
  can be reached, and a recommended fix; it is neither fixed quietly outside the ticket's paths nor left for later.

The checks follow OWASP's practices (validate input, parameterise queries, encode output, control access, protect
data); this skill names them and copies none of its text.

## Steps

Copy this checklist into your notes and tick each step as you go.

- [ ] 1. Read the ticket's KPI lines, paths and flags; draw the boundary: input in, access decided, secrets used.
- [ ] 2. Write the unit tests first, following the test-driven-development skill, with hostile input and a denied
  caller (Unit-test focus below).
- [ ] 3. Write the smallest code that passes: input checked, query parameterised, role narrowest, secret from outside.
- [ ] 4. Read what the change added: each new input, role, token, dependency or log line, against the Pre-commit
  checklist below.
- [ ] 5. If you see a weakness anywhere you read, stop adding to it and write the P1 package (Escalation).
- [ ] 6. Run the unit suite of the touched area, then the Pre-commit checklist below.
- [ ] 7. Run the acceptance tests only through `gov accept`; read the pass or fail and never the test code.
- [ ] 8. Write the return (Output and handover) and commit with the ticket's trailers.

## Pre-commit checklist

- [ ] Every input from outside is checked for shape, length and type at the boundary before use.
- [ ] No query, command or path is built by joining input into a string.
- [ ] No secret, key, token or personal value in the diff, a fixture, a log line or an error; the values come from the
  environment or the secret store.
- [ ] Each role, token and file mode is the narrowest that works; nothing runs as an administrator for convenience.
- [ ] Access is denied unless allowed, and each path to the new code checks who is calling.
- [ ] A new or updated dependency is named in the ticket and pinned.
- [ ] The diff touches only the ticket's allowed paths, and the suite of the touched area passes.

## Unit-test focus

The method is the test-driven-development skill's; this is only where security tests look.

- Hostile input at each boundary: quotes and separators, an oversized value, the wrong type, a path with `..`, an
  empty value.
- The denied caller: no credential, a wrong credential, a credential with too little access; each is refused and
  nothing leaks in the reply.
- A missing secret: the code fails closed with an error that does not print the secret's name or value.
- Output that holds input: it comes back encoded for where it lands.
- A log line or error built from a failing request holds no secret or personal value.

## Common mistakes

- Building a query or a command by joining input into a string.
- Checking input in the client only, or checking it after it was already used.
- A constant token or password in source, in a test, or in a sample configuration.
- Running as the administrator role because it worked first.
- Checking who the caller is but not whether this caller may do this.
- Printing the whole request or the whole exception to a log or a reply.
- Fixing a weakness found in another ticket's code in passing, without a package or a record.

## Done when

- Each boundary the ticket touches has a test with hostile input and a test of the denied caller.
- The Pre-commit checklist is ticked line by line; a line that cannot be ticked is named in `risks`.
- No secret or personal value stands in the diff, the fixtures or the return.
- `gov accept` reports pass for the ticket, or the return says it was not run and why. If it fails: fix, then check
  again.

## Output and handover

- The return starts with the twelve fields, each a labelled line (task, status, work_completed, files_changed,
  evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action), with any
  payload after them; refused twice for the same call, stop and return; an authentication error returns
  `AUTH_REQUIRED` (the orchestration skill's briefs-and-returns.md).
- This skill adds no output path of its own (`output: none`). A security package goes in the return's `risks` and
  `unresolved`, with where, how it can be reached, the options and a recommendation; it never repeats a secret's value.

## Escalation

**When to escalate:** ranked by the escalation rubric (P3, P2, P1, Emergency; DEC-1219 (2)), to whoever started the
session, never to the owner directly. Secrets and security are P1 (DEC-1219 (2)).

- P3: a naming or layout choice inside the ticket that touches no security control; decide, log it in `discoveries`
  and go on.
- P2: a matter outside security that touches shared code or another stream, or changes the ticket's scope within the
  approved spec; make what stays inside the paths and return the rest as a package.
- P1: any security finding is a P1, whatever its size and wherever it is seen, in the ticket's paths or outside them.
  So is anything that concerns secrets, weakens a guard rule or fails open, is irreversible, costs money or changes a
  standing decision. A package with the evidence, the options and a recommendation; the affected work waits.
- Emergency: a secret exposed, a risk of losing data, the disk below its floor, the guard failing open. Stop the
  affected work at once, repeat no secret value, rewrite no history, then go up as a P1 asking for the rotation.

## Never

Reminders only: the guard decides.

- This skill changes no role's reads or writes. Work that needs other writes goes back as a package for the role that
  holds them, never routed round (DEC-995, DEC-996).
- Rank a security matter below P1, or leave it for a later ticket.
- Repeat a secret's value in a reply, a note, a commit, a fixture or a log.
- Fix code outside the ticket's paths because the fix is small; the package goes up and the owner of that code acts.
- Widen a role, a token or a file mode to make a test or a run pass.
- Read the acceptance tests, or code to make them pass; the code fulfils the spec and its KPIs.
- Edit the generated copy of this skill by hand: it is generated from this source (DEC-315).

## Sources

DEC-959 (items 4 and 5), DEC-957 (Q5 and the escalation rubric), DEC-832, DEC-616, DEC-645, DEC-315, DEC-1112 (3),
DEC-995, DEC-996, DEC-836, ROLES-RESEARCH-1 §2.7 and §2.12, NIST SP 800-218 (SSDF), OWASP's practices, CAP-24.b.
