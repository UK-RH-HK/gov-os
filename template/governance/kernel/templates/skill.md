---
name: <skill-name>
version: "1.0.0"
description: "<In the third person: what the skill does and when to use it, under 60 tokens.>"
metadata:
  version: "1.0.0"
---

<!-- For whoever writes a skill from this template. Delete this comment from a written skill.

How a skill is written (DEC-959 item 5):
- Scenarios first: write the skill's three test scenarios in `scenarios.md` in its folder (a situation, the expected
  behaviour, a pass line a fresh session is judged by) and commit them before the text. Run them on a fresh
  session before the skill is promoted.
- The body stays under about 150 lines. Detail goes into reference files directly in the skill's folder, each
  linked from the body; a reference file links to no further reference file.
- The front matter: `name`, `version`, and a third-person `description` of what the skill does and when, under 60
  tokens; `metadata.version` repeats `version`, so the generated copy states it (DEC-832 item 2). A skill whose text
  changes raises its version.
- A project's own values stand as `<placeholders>` (DEC-539). Every `gov <command>` in a code span is a recorded
  command. Sources stand at the end, not on every line; each rule stays traceable to its decision.
- The skill states a method and grants nothing: the guard decides (CAP-24.b). Rules the briefs already carry are
  referred to, not restated.
- An imported skill (from another collection) is adopted only when its source, version and licence are recorded in
  <the project's skill-import record> with a licence that allows the use, and its three scenarios pass.

The template's own three scenarios (DEC-959 item 5), written before its text. Each is run on a fresh session that
has only this template and the inputs named; it passes when its pass line holds.

1. A new skill from the template.
   - Situation: a fresh session is given this template and a one-page description of a method, and asked to
     write the skill.
   - Expected: it writes the skill's three scenarios first and commits them, then the skill's text in a later
     commit; the front matter has name, version and a third-person description of what it does and when; the
     sections stand in the template's order, with the sources at the end.
   - Pass line: the skill validator finds nothing; every section heading of the template is present, in order; the
     body is under about 150 lines; the scenarios' commit is older than the text's.
2. More method than fits.
   - Situation: the method described needs about 300 lines of detail.
   - Expected: the body keeps the steps and the checks; the detail goes into reference files directly in the
     skill's folder, each linked from the body; no reference file links on to another.
   - Pass line: the body is under about 150 lines; every reference file sits one level below the skill and is
     linked from it; the validator finds nothing.
3. An imported skill.
   - Situation: the session is asked to adopt a skill from another collection whose licence is not stated.
   - Expected: it does not adopt it; it records what it found of the source, version and licence in
     <the project's skill-import record>, and returns a package; with a licence that allows the use, it writes the
     skill's three scenarios and adopts it only once all three pass.
   - Pass line: no skill is marked adopted without a licence record and three passing scenarios.
-->

# <Skill name>

<One paragraph: what the method is for, and which role uses it. The guard, the launcher and the role file decide
what a session may do; this skill is a method only and grants nothing (CAP-24.b).>

## When / not when

- Use it when <the situation>.
- Not when <the situation it does not fit>: use <the other skill> instead.

## Inputs

Read first, before anything else:

- <what the session reads, by name: the ticket, the specification, the records>;
- what it needs to know beyond those, through `gov retrieve` first (DEC-836).

## Steps

Copy this checklist into your notes and tick each step as you go.

- [ ] 1. <a step, with the command or check it takes>
- [ ] 2. <a step>
- [ ] 3. <a step>

Detail that does not fit here: [<reference file>](<reference-file>.md).

## Done when

- <the check that shows the work is done>. If it fails: fix, then check again.

## Output and handover

- The return starts with the twelve fields, each a labelled line, with any payload after them; refused twice for
  the same call, stop and return; an authentication error returns `AUTH_REQUIRED` (the orchestration skill's
  briefs-and-returns.md).
- <the typed handoff kind, where the project has one>; <what this skill's output adds to the return, and where it
  is written>.

## Escalation

- <what this skill's user cannot settle>, ranked by the escalation rubric (P3, P2, P1, Emergency; DEC-957), goes
  to <whoever started the session>, never to the owner directly.
- An Emergency (a secret exposed, a risk of losing data, the disk below its floor, the guard failing open) stops
  the affected work at once, then goes up as a P1.

## Never

Reminders only: the guard decides.

- <what a session using this skill never does>.

## Sources

<the decision and Contract ids the skill follows, here at the end>.
