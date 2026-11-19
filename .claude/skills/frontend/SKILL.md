---
name: frontend
description: >-
  The engineer's skill for frontend tickets: interface conventions,
  accessibility, state and browser support, with a pre-commit checklist and the
  unit-test focus. Use beside the engineer role when a ticket changes interface
  code.
metadata:
  version: 1.2.0
---
# Frontend

The engineer's skill for a ticket that changes interface code: components, styles and client-side state (DEC-957 Q5,
DEC-959 item 4). An engineer loads it beside the engineer role. The guard, the launcher and the role file decide what
a session may do; this skill is a method only and grants nothing (CAP-24.b). Its three scenarios:
[scenarios.md](scenarios.md); its check: `check_domain_skill.py`, in this folder.

## When / not when

- Use it when the ticket's paths hold interface code: a component, its styles, its client-side state and its unit
  tests.
- Not for the design of a user flow: use the ui-ux skill, where the owner reviews the flow as scenarios before it is
  built. Not for a build or release pipeline: use the devops skill.

## Inputs

Read first, before anything else:

- the ticket: its KPI lines and `allowed_paths`, and the spec it cites, with the browser-support list and any
  approved user-flow scenarios;
- the project's own values: `<the project's component layout and naming>`, `<the supported browser list>`,
  `<the design system or style guide>`;
- the components, styles and tests next to the code you change;
- what else it needs to know, through `gov retrieve` first (DEC-836).

## Steps

Copy this checklist into your notes and tick each step as you go.

- [ ] 1. Read the support list and the approved flow; find the existing component to reuse before writing one.
- [ ] 2. Write a unit test for the behaviour first (the test-driven-development skill: your own unit tests, never
  code shaped to the acceptance tests).
- [ ] 3. Build it by the conventions and the three points below: accessibility, state, browser support.
- [ ] 4. Run your unit tests, then go through the pre-commit checklist.
- [ ] 5. Run the acceptance tests only through `gov accept`, once they are ready; you see pass or fail, never the
  tests (the engineer role).

**Conventions:**

- Naming and layout follow `<the project's component layout and naming>`: one component per file, named as its
  export, its test beside it, its styles at its own level with no global override.
- Native HTML first; add ARIA only for what no native element does.
- Use the design system's components and tokens before a new one; no colour or size outside the tokens.
- Text goes through `<the project's text mechanism>`, never as a string in the markup, where the project has one.

**Accessibility:** a native control for each job (a button acts, a link navigates, a label names a field); every
control reachable and usable by keyboard alone, with a visible focus style; an accessible name on every control and
`alt` text on every informative image (empty for a decorative one); colour never the only signal, contrast to
`<the project's contrast target>`; a change the user cannot see is announced; motion respects the reduced-motion
setting.

**State:** one source of truth; derive a value, never copy it into a second state; update immutably; keep state as
local as it can be and lift it only when two parts need it; server data apart from interface state; every
asynchronous view shows loading, error and empty; a side effect (fetch, timer, subscription) stays out of the render
and is cleaned up.

**Browser support:** the spec's list is the contract, `<the supported browser list>`. Check a feature against it before
you use it; build a newer feature as an enhancement behind a feature check, with a working fallback, and test both
paths. You never edit the list: that changes the spec (Escalation).

**Unit-test focus:** the behaviour a user sees, found the way a user finds it (by role and accessible name, not by
class or position); state transitions (loading, loaded, error, empty); keyboard use of each control; the fallback
path. Not snapshots of markup, not the framework's own work.

**Common mistakes:**

- A `div` or `span` with a click handler standing for a button; `outline: none` with no other focus style.
- An image with no `alt`; an icon-only control with no name; a field with no label.
- A prop copied into state; a second state holding what can be derived; an array or object changed in place.
- A fetch in the render body; no loading, error or empty view.
- A feature used that a browser on the list lacks, with no fallback.
- A unit test that finds a control by class, or tests the framework instead of the behaviour.

**Pre-commit checklist:**

- [ ] Every interactive element is a native control, or has role, name and key handling; keyboard alone reaches it.
- [ ] Every image has `alt`, every icon-only control a name, every field a label; focus is visible.
- [ ] No prop copied into state, no state changed in place; loading, error and empty shown.
- [ ] Every feature used is on the browser list or behind a feature check with a fallback.
- [ ] Existing components and tokens reused; no value outside the tokens.
- [ ] Unit tests pass, the new behaviour has one, none is skipped or limited with `.only`; no debug output left.
- [ ] Only the ticket's paths changed; no dependency added.

## Done when

- [ ] The pre-commit checklist is ticked, each item checked in the code, not remembered.
- [ ] The unit tests pass; the acceptance tests, if ready, were run once through `gov accept`.
- [ ] `python3 <skill folder>/check_domain_skill.py <SKILL.md>` prints PASS, when this skill itself changed.

If any is false: fix, then check again.

## Output and handover

- The code and its unit tests, written only at the ticket's paths.
- The return starts with the twelve fields, each a labelled line (task, status, work_completed, files_changed,
  evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action); refused
  twice for the same call, stop and return; an authentication error returns `AUTH_REQUIRED` (the orchestration
  skill's briefs-and-returns.md).
- An interface point the ticket leaves open (a name, a layout, a detail inside its paths) goes in `discoveries`: take
  the simplest reading, never widen the scope.
- A question the spec leaves open about what its browser-support list or an approved flow promises for a browser on
  the list (for example whether a plain page change meets the design's intent) is not an interface point: build the
  safe, reversible fallback meanwhile, and send the question as a P1 package (Escalation), not as a note alone.

## Escalation

**When to escalate:** ranked by the escalation rubric (P3, P2, P1, Emergency; DEC-1219 (2)), to whoever started the session,
never to the owner directly.

- P3: a naming or layout choice inside the ticket's paths that changes no KPI; note it in `discoveries`.
- P2: a change to a component or style shared with another stream; a change to the ticket's scope or KPIs within the
  approved spec.
- P1: a change to the spec's browser-support list or to an approved flow; a question the spec leaves open about what
  its support list or an approved flow promises for a browser on the list, since settling it reads the spec: send it
  with the options and their cost and a recommendation, to whoever started you, and build the safe fallback
  meanwhile; a KPI that only an inaccessible control can meet; a new dependency or install; anything that fails open.
- Emergency: a secret or key found in client code or in the bundle; a risk of losing the user's data; the guard failing
  open. Stop the affected work at once, then go up as a P1.

## Never

Reminders only: the guard decides.

- This skill changes no role's reads or writes. Work that needs other writes goes back as a package for the role that
  holds them, never routed round (DEC-995, DEC-996).
- Ship a control a keyboard cannot reach, or an image with no `alt`.
- Edit the browser-support list or an approved flow to fit the code.
- Put a secret, key or token in client code: everything in the bundle is public.
- Read an acceptance test, or shape code to pass one.

## Sources

DEC-957 (Q5 and the escalation rubric), DEC-959 (items 4 and 5), DEC-995, DEC-996, DEC-836, DEC-616, DEC-645,
DEC-315, DEC-1112 (3), CAP-24.b, ROLES-RESEARCH-1 §2.7.
