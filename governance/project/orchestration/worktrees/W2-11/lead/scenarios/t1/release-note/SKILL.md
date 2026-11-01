---
name: release-note
version: "1.0.0"
description: "Writes a version's release note from the merged tickets and the decision register's entries since the last version. Used by the product-spec role when a version is cut."
metadata:
  version: "1.0.0"
---

# Release note

The method for writing a version's release note. The note says what changed for a user, what was fixed and what
was internal; which decisions change behaviour; and what a user must do to move to the version. The product-spec
role uses it when a version is cut. The guard, the launcher and the role file decide what a session may do; this
skill is a method only and grants nothing (CAP-24.b).

## When / not when

- Use it when a version is cut and its release note is to be written.
- Not when no version is being cut, for example when one change or one feature needs documenting: use
  <the project's documentation skill> instead. Not to publish a note either: publishing belongs to the
  orchestrator.

## Inputs

Read first, before anything else:

- the merged tickets since the last version, from <the project's ticket record>: each one's id, title and KPI
  lines;
- the decision register's entries since the last version, from <the decision register>: read each entry in full
  before citing it;
- the last version's id and date, from <the project's version record>, which mark where "since" starts;
- what it needs to know beyond those, through `gov retrieve` first (DEC-836).

## Steps

Copy this checklist into your notes and tick each step as you go.

- [ ] 1. List every ticket merged since the last version, by id and title. This list is the ticket list that the
      note is checked against.
- [ ] 2. Put each ticket in exactly one group: user-visible change, fix or internal. Decide from its title and
      KPI lines. If you cannot describe its change without reading the code, raise a P3 (see Escalation) and
      leave the ticket open until the answer arrives.
- [ ] 3. For each user-visible change, write one sentence a user understands, naming the command or file it
      changes. List fixes and internal changes by ticket id and title.
- [ ] 4. Read each register entry since the last version. Name every decision that changes behaviour, with its
      id and the behaviour it changes. Cite only entries you have read. If a decision contradicts the note,
      raise a P2.
- [ ] 5. State every migration step a user must take, next to the change that needs it. A breaking change with
      no migration path is a P1.
- [ ] 6. Date and version the note (`<version>`, `<date>`) and write it to `docs/releases/<version>.md`.
- [ ] 7. Ask whoever started the session for a second session that reads the note against the ticket list from
      step 1 and confirms none is missing. Record its confirmation. If it finds a gap, fix it and have the note
      read again.
- [ ] 8. Hand the note to the orchestrator. Do not publish it.

No reference file: the method fits this body.

## Done when

- Every merged ticket on the list appears in exactly one group; every behaviour-changing decision since the last
  version is cited by its id; the second reader confirms that none is missing; no P1 or P2 from this note is
  still open. If any check fails: fix, then check again.

## Output and handover

- The return starts with the twelve fields, each a labelled line, with any payload after them; refused twice for
  the same call, stop and return; an authentication error returns `AUTH_REQUIRED` (the orchestration skill's
  briefs-and-returns.md).
- <the project's handoff kind for a release note>, where the project has one: the note at
  `docs/releases/<version>.md`, handed to the orchestrator, with the second reader's confirmation and any open
  escalation listed after the twelve fields. The orchestrator publishes it.

## Escalation

- A ticket whose change cannot be described without reading the code: a P3, a question for that ticket's
  engineer.
- A decision that contradicts the note: a P2.
- A breaking change with no migration path: a P1, for the owner's decision.
- Each is ranked by the escalation rubric (P3, P2, P1, Emergency; DEC-957) and goes to whoever started the
  session, never to the owner directly.
- An Emergency (a secret exposed, a risk of losing data, the disk below its floor, the guard failing open) stops
  the affected work at once, then goes up as a P1.

## Never

Reminders only: the guard decides.

- Invent a feature, or describe a change that the tickets or their engineer do not support.
- Cite a decision you have not read.
- Publish the note yourself.

## Sources

DEC-959 item 5 (scenarios before text), DEC-832 item 2 (version in metadata), DEC-539 (project values as
placeholders), DEC-836 (`gov retrieve` first), DEC-957 (escalation rubric), CAP-24.b (a skill grants nothing);
<the decision that adopts the release-note method>.
