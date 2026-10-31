---
name: qa-review
version: "1.0.0"
description: "The QA engineer's method: traces each KPI line to its tests and code, checks tests and code against the spec, probes in proportion to the profile and reports findings. Use for a ticket's QA before it merges."
metadata:
  version: "1.0.0"
---

# QA review

The QA engineer's method (DEC-957, DEC-959 items 1 and 3). The QA engineer alone reads the specification, the KPI lines, the tests and the code; it changes none of them and writes only its findings report. The guard and the role file decide what the session may do; this skill is a method only and grants nothing (CAP-24.b). Its three scenarios: [scenarios.md](scenarios.md).

## When / not when

- Use it when a ticket, or a batch of a stream's tickets, is ready to merge: a ticket that touches the core (the guard, the close, retrieval, anything that could fail open) is reviewed alone; the others in batches of up to about five (DEC-959 item 3).
- Not for a milestone or exit audit: use the audit skill. Not to fix anything: findings go back to the lead, who sends them to a test designer and an implementer.

## Inputs

Read first:

- the ticket file: its profile, its KPI lines (success and failure) and its `allowed_paths`;
- the specification and the decisions the ticket cites;
- the ticket's acceptance tests and their README, and the code at the head to review;
- the lead's results of its one scoped run, with the selection's scope;
- the project's threat-model record, `<the project's threat-model record>`, and the audit skill's judgement rules.

What else it needs to know, it asks `gov retrieve` first (DEC-836). It reads everything, tests and code alike (DEC-820 item 3).

## Steps

Copy this checklist into your notes and tick each step as you go.

- [ ] 1. **Trace.** For each KPI line, success and failure: the tests that cover it and the code behind it. Mark each line traced, or untraced with what is missing.
- [ ] 2. **Tests against the spec.** A missing failure line; a weak assertion; a test that would pass for the wrong reason; a test that reads the implementation's private parts; tests out of proportion to the change.
- [ ] 3. **Code against the spec.** Behaviour the tests miss; a write outside the ticket's paths; a guard or gate that fails open; work that can be lost (DEC-137, DEC-498).
- [ ] 4. **Probes, in proportion to the profile.** LITE: the trace only. STANDARD: the trace and a probe of each key failure line. FULL: a full probe of the final head. A probe is a small run of the code by the QA engineer; it never re-runs the ticket's suites (DEC-959 item 1).
- [ ] 5. **Judge each finding** by the audit skill's judgement rules: the two questions, word for word, and the two lines `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other` (DEC-808). Give it a severity (below).
- [ ] 6. **Write the findings report** at `<the QA findings path>/<ticket id>.md`, then check it against "Done when".

**Severity**, tied to the escalation rubric (DEC-957):

- **P1:** ordinary work "yes" and it fails open or loses work; or a KPI line neither tested nor built. It blocks the merge.
- **P2:** ordinary work "yes" and a wrong result or a broken KPI line, with no fail-open and no loss; or a failure line with no test. Fixed in the ticket's current round or its next resume (DEC-802).
- **P3:** ordinary work "no", which is a row for the project's hardening list, never a round (DEC-801); or a weak assertion or a gap that changes no result.

## Done when

- Every KPI line is traced or flagged; every finding has its two lines and a severity; the report names what was probed and found sound. If any check fails: fix the report, then check again.

## Output and handover

- The findings report is the only file written: one row per KPI line (traced or not), then each finding as a described behaviour, never as code (DEC-136): what was done, what happened, what should have happened, its two lines and its severity.
- The return starts with the twelve fields, each a labelled line, with the report's path after them; refused twice for the same call, stop and return; an authentication error returns `AUTH_REQUIRED` (the orchestration skill's briefs-and-returns.md).

## Escalation

- A P1, or any bug the lead's repair does not resolve, goes to the stream's Senior Engineer, then the orchestrator, then the owner (DEC-957); never to the owner directly.
- An Emergency (a secret exposed, a risk of losing data, the disk below its floor, the guard failing open) stops the review at once and goes up as a P1.

## Never

Reminders only: the guard decides.

- Change a test, the code, a ticket file or any record but the findings report.
- Re-run the ticket's suites; the lead ran them once.
- Read a secret, the held-out material's contents or the hidden half of an evaluation set (DEC-820).
- Turn a finding marked "no" into a round.

## Sources

DEC-136, DEC-137, DEC-498, DEC-801, DEC-802, DEC-808, DEC-820, DEC-836, DEC-957, DEC-959, CAP-24.
