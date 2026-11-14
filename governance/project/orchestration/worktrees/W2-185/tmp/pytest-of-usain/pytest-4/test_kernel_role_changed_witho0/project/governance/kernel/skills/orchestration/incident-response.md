# Orchestration: incident response

A reference file of the orchestration skill, one level below `SKILL.md`. It states the method; the guard decides
(CAP-24.b). A project's own values stand as `<placeholders>` (DEC-539).

An incident is an Emergency of the escalation rubric: a secret exposed, a risk of losing data, the disk below its
floor, or the guard failing open (DEC-957).

## Stop

- Stop the affected work at once: start no session that touches it, and stop the ones that do. Work it does not
  touch keeps running.

## Contain

- **A secret exposed:** never print it again; keep it out of every commit, log and record from here on; rotating it
  and rewriting pushed history are the owner's.
- **A risk of losing data:** stop every writer on the affected tree or branch; no reset, no clean, no forced
  checkout; keep what is there as it is.
- **The disk below its floor:** start nothing heavy; remove your own temporary trees; name what else holds the
  space (DEC-898).
- **The guard failing open:** start no session of the roles it lets through until it is closed.

## P1

- Send the owner a P1 package at once, in its six parts (DEC-818), by the project's notification route; only the
  orchestrator contacts the owner (DEC-850, DEC-855). An authentication or access error is `AUTH_REQUIRED` (DEC-420).

## A live handoff

- While the incident lasts, write the checkpoint at each step: what happened, what is stopped, what is contained,
  what is next (DEC-837 item 3). A session that takes over resumes from it, and says so.

## A blameless note

- After it, a short note in `<the project's incident record path>`: the timeline, the cause, what contained it, and
  what changes (a ticket or a row), with no blame. Its lesson goes to the lessons record.
