---
name: spec-writing
version: "1.0.0"
description: "The product-spec session's method for writing a spec: problem, goals and non-goals, KPIs as observable behaviour each with a failure line, test data with its owner, open questions as packages. Use for a spec the ticket asks for."
metadata:
  version: "1.0.0"
---

# Spec writing

The product-spec session's method for writing a specification (DEC-959 item 8). The spec states what is to be true
and how anyone will see it, without naming code. The guard and the role file decide what the session may do; this
skill is a method only and grants nothing (CAP-24.b). Its form is in [spec-form.md](spec-form.md); its check is
`check_spec.py`, in this folder.

## When / not when

- Use it when a ticket asks for a spec: a specification section, a KPI set or a decision package for the owner.
- Not for a schema, a template or a role file, which have their own forms; not for the tests (use the test-design
  skill) or for the code.

## Inputs

Read first, before anything else:

- the ticket: its sources, its KPI lines and its allowed paths;
- the decisions the ticket cites, and the files the spec changes or replaces;
- the test data the future tests need, and who holds it;
- what else it needs to know, through `gov retrieve` first (DEC-836).

## Steps

Copy this checklist into your notes and tick each step as you go.

- [ ] 1. **Problem.** What is wrong or missing, and for whom, in a short paragraph.
- [ ] 2. **Users and scenarios.** Who uses it and the situations they meet, each as a short story.
- [ ] 3. **Goals.** What the change makes true.
- [ ] 4. **Non-goals.** What it does not try to do, though a reader might expect it.
- [ ] 5. **KPIs.** Each as `- K<n>: <behaviour>` an observer can see, then a `Fails if:` line with the observable
  failure. No code named: no code span, call, path, dotted or snake_case name ("What names code" in spec-form.md).
- [ ] 6. **Test data.** One table row per source: its source, imported or synthetic, its owner, its licence or its
  recipe, its privacy, its secrets, its hidden half where it measures, and whether it is secured. Data that cannot be
  secured is escalated as a P1, never skipped (Escalation below).
- [ ] 7. **Out of scope.** What goes to other work, and where.
- [ ] 8. **Open questions.** Each as a package: the question, the options with their cost, a recommendation.
- [ ] 9. **Accepted by.** Who accepts the spec, and on what evidence.
- [ ] 10. **Run the check:** `python3 <skill folder>/check_spec.py <spec.md>`. Fix each `REFUSED` line, then run it
  again. A `P1` line goes up as a package; the spec is not passed until the owner decides it.
- [ ] 11. **Copied text.** Where any text is imported, check its licence, record it in `imports.yaml`, mark the text
  and run `python3 <skill folder>/check_spec.py --imports <folder>`.

Detail that does not fit here: [spec-form.md](spec-form.md).

## Done when

- [ ] Every KPI line is testable without naming code: each states behaviour an observer sees, names no code, and has
  its `Fails if:` line.
- [ ] Every data source has its owner and its licence (imported) or its recipe (synthetic); each measuring source
  has its hidden half stated.
- [ ] The spec has all nine parts, each with content; none is missing.
- [ ] The check prints PASS and exits 0, with no REFUSED line and no P1 line.
- [ ] Every imported part has a licence record in `imports.yaml`, or nothing is imported.

If any is false: fix the spec, then check again.

## Output and handover

- The spec file is the output, written only at the ticket's paths. A P1 package for unsecurable data is written
  beside it by the check as `<spec stem>.P1.md`; it is part of the handover, never deleted.
- The return starts with the twelve fields, each a labelled line (task, status, work_completed, files_changed,
  evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action), with
  the check's output after them; refused twice for the same call, stop and return; an authentication error
  returns `AUTH_REQUIRED` (the orchestration skill's briefs-and-returns.md).
- A source decision that is not in the ticket's sources, or an interface left open, goes in `discoveries`.

## Escalation

Ranked by the escalation rubric (P3, P2, P1, Emergency; DEC-957), to whoever started the session, never to the owner
directly.

- P3: a wording or ordering choice that changes no KPI; note it in `discoveries`.
- P2: an open question that changes a KPI or a scope line; put it in the spec as a package, with its options and
  cost.
- P1: test data that cannot be secured (no licence, private data, secrets, no owner who can hold it), or a KPI
  that cannot be stated without naming code. Never skipped: the package carries the options (secure it another way,
  replace it with synthetic data, drop the KPI with the owner's approval) and a recommendation.
- Emergency: a secret found in the data or the spec, a risk of losing data, the guard failing open. Stop the work
  at once, then go up as a P1.

## Never

Reminders only: the guard decides.

- This skill changes no role's reads or writes. Work that needs other writes goes back as a package for the role
  that holds them, never routed round (DEC-995, DEC-996).
- Mark a spec passed with a REFUSED line or a P1 line standing; PASS is only the check's.
- Name code in a KPI line, or leave a KPI with no failure line.
- Skip test data that cannot be secured, or give a source no owner.
- Copy imported text without a licence record that allows it (DEC-1084).
- Write the `.claude/skills/` copy by hand: it is generated from this source (DEC-315).

## Sources

DEC-959 (items 5 and 8), DEC-957, DEC-1084, DEC-1156 (5), DEC-616, DEC-645, DEC-315, DEC-836, DEC-995, DEC-996,
ROLES-RESEARCH-1 §2.4, CAP-24.
