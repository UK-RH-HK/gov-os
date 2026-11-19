# Orchestration: incident response

A reference file of the orchestration skill, one level below `SKILL.md`. It states the method; the guard decides
(CAP-24.b). A project's own values stand as `<placeholders>` (DEC-539).

An incident is an Emergency of the escalation rubric (DEC-1219 (2), `docs/emergency-2/T2-ESCALATION-RUBRIC.md` §2): a
secret exposed outside the machine, a risk of losing data or work, the disk below its floor, or the machine over its
gate and not coming back.

## Stop

- Stop the affected work at once: start no session that touches it, and stop the ones that do. Work it does not
  touch keeps running.

## Contain

- **A secret exposed outside the machine:** never print it again; keep it out of every commit, log and record from here on; rotating it
  and rewriting pushed history are the owner's.
- **A risk of losing data:** stop every writer on the affected tree or branch; no reset, no clean, no forced
  checkout; keep what is there as it is.
- **The disk below its floor:** start nothing heavy; remove your own temporary trees; name what else holds the
  space (DEC-898).
- **The machine over its gate and not coming back:** start nothing heavy; name what holds the load (DEC-898).

## P1

- Stop the affected work first, then push the owner at once, at any hour, with a P1 package in its six parts (DEC-818),
  by the project's notification route; only the orchestrator contacts the owner (DEC-850, DEC-855). The push also
  appears in the morning brief (DEC-1217 (5)). An authentication or access error is `AUTH_REQUIRED` (DEC-420).

## A live handoff

- While the incident lasts, write the checkpoint at each step: what happened, what is stopped, what is contained,
  what is next (DEC-837 item 3). A session that takes over resumes from it, and says so.

## A blameless note

- After it, a short note in `<the project's incident record path>`: the timeline, the cause, what contained it, and
  what changes (a ticket or a row), with no blame. Its lesson goes to the lessons record.
