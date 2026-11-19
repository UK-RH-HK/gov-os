---
name: ui-ux
version: "1.1.0"
description: "The engineer's skill for user-flow tickets: writes each flow as scenarios the owner reviews, never as code, then builds to them. Use beside the engineer role when a ticket adds or changes what a user sees or does."
output: "<allowed_path>/** (one entry of the ticket's allowed_paths)"
metadata:
  version: "1.1.0"
---

# UI/UX

The engineer's skill for a ticket that adds or changes what a user sees or does: a flow, a screen, a message
(DEC-957 Q5, DEC-959 item 4). An engineer loads it beside the engineer role. The owner reviews the flow as scenarios,
not as code (DEC-103). The guard, the launcher and the role file decide what a session may do; this skill is a method
only and grants nothing (CAP-24.b). Its three scenarios: [scenarios.md](scenarios.md); its check:
`check_domain_skill.py`, in this folder.

## When / not when

- Use it when the ticket changes a user flow: the steps a user takes, what each screen shows, the words on it, the
  empty, error and keyboard paths.
- Not for the code of a component: use the frontend skill once the flow is approved. Not for a build or release
  pipeline: use the devops skill.

## Inputs

Read first, before anything else:

- the ticket: its KPI lines and `allowed_paths`, the spec it cites and any mock or description of the flow;
- the flows already built next to this one, and `<the design system or style guide>`;
- the scenario form of the discovery skill (a user, a situation, the steps, the outcome);
- what else it needs to know, through `gov retrieve` first (DEC-836).

## Steps

Copy this checklist into your notes and tick each step as you go.

- [ ] 1. Read the request and the flows and components that exist; note what the mock leaves silent.
- [ ] 2. Write the flow as scenarios in plain language: the happy path, then each alternative, empty, error and
  keyboard-only path. Where the mock is silent, take the simplest reading and name it.
- [ ] 3. Put the scenarios in front of the owner through whoever started the session; build nothing of the flow until
  they are reviewed.
- [ ] 4. Build to the reviewed scenarios, reusing existing components and tokens (the frontend skill for the code); one
  unit test per scenario.
- [ ] 5. If a step cannot be built as reviewed, stop that step and send the changed scenario back (Escalation); never
  change the flow quietly.
- [ ] 6. Go through the pre-commit checklist.

**Conventions:**

- A scenario names a user, the situation, the steps in order, what the user sees at each step and the outcome, in the
  words the owner uses; no component, class or function name.
- One flow, one set of scenarios, numbered; the build, the tests and the return refer to them by number.
- Reuse the design system's components, patterns and wording before a new one.
- Every message says what happened and what the user can do next; no dead end; a destructive step is confirmed or can
  be undone.

**User flows as scenarios:** the owner reviews a user flow as scenarios, not as code. Hand the owner the scenarios (and
a mock where there is one), never a component, a diff or a branch. A reviewed flow is the spec for the build: a change to
it goes back as a changed scenario, reviewed again.

**Unit-test focus:** one test per scenario step that has a visible result: what the user sees after each action; the
empty, error and loading views; the words of each message; keyboard-only completion of the flow. Not pixel positions,
not the framework's own work.

**Common mistakes:**

- Showing the owner code, or asking the owner to approve a flow by reading a diff.
- A flow with only the happy path; no empty, error, wrong-input or keyboard path.
- A flow changed in the build without going back to the owner.
- A new pattern, colour or component where the design system has one.
- A message that says "error" and nothing more; a dead end with no next step; a destructive step with no confirmation.
- A step that needs a mouse, or colour alone, to be understood.

**Pre-commit checklist:**

- [ ] Every scenario has a test, and every built step has a scenario; numbers match.
- [ ] The flow built is the flow the owner reviewed; any change went back as a changed scenario.
- [ ] Empty, error, loading and keyboard-only paths are built, not only the happy path.
- [ ] Existing components, tokens and wording reused; no new pattern without a reason in the scenarios.
- [ ] Each message says what happened and what to do next; each destructive step is confirmed or undoable.
- [ ] Only the ticket's paths changed.

## Done when

- [ ] The scenarios were reviewed, and the build matches them step by step.
- [ ] The pre-commit checklist is ticked, each item checked against the built flow.
- [ ] The unit tests pass; the acceptance tests, if ready, were run once through `gov accept`.
- [ ] `python3 <skill folder>/check_domain_skill.py <SKILL.md>` prints PASS, when this skill itself changed.

If any is false: fix, then check again.

## Output and handover

- The flow's scenarios, at the ticket's paths where the ticket names them, and the build with its unit tests, only at
  the ticket's paths.
- The return starts with the twelve fields, each a labelled line (task, status, work_completed, files_changed,
  evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action), with the
  scenarios' numbers after them; refused twice for the same call, stop and return; an authentication error returns
  `AUTH_REQUIRED` (the orchestration skill's briefs-and-returns.md).
- Each reading taken where the mock is silent goes in `discoveries`.

## Escalation

**When to escalate:** ranked by the escalation rubric (P3, P2, P1, Emergency; DEC-1219 (2)), to whoever started the session,
never to the owner directly; the owner sees scenarios, carried by the one who started you.

- P3: a wording choice inside a reviewed scenario that changes no step; note it in `discoveries`.
- P2: a change to a shared component or pattern that another stream uses; a change to the ticket's scope or KPIs
  within the approved spec.
- P1: a step that cannot be built as the owner reviewed it, or any change to a reviewed flow: it goes back as a
  changed scenario with its options, their cost and a recommendation; a flow that conflicts with the spec or with
  accessibility; a new dependency or install.
- Emergency: a flow that exposes a secret or another user's data, or risks losing the user's data; the guard failing
  open. Stop the affected work at once, then go up as a P1.

## Never

Reminders only: the guard decides.

- This skill changes no role's reads or writes. Work that needs other writes goes back as a package for the role that
  holds them, never routed round (DEC-995, DEC-996).
- Ask the owner to review code, or build a flow before its scenarios are reviewed.
- Change a reviewed flow in the build without sending the changed scenario back.
- Show a user another user's data, or hide a destructive step.

## Sources

DEC-957 (Q5 and the escalation rubric), DEC-959 (items 4 and 5), DEC-103, DEC-995, DEC-996, DEC-836, DEC-616,
DEC-645, DEC-315, DEC-1112 (3), CAP-24.b, ROLES-RESEARCH-1 §2.7.
