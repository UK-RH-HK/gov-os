---
name: judging-work
description: "The one rule for judging work (ADR-0001, DEC-801, DEC-1010, merged by DEC-1204): the threat model, what may block, how reviews converge. Preloaded by every role that judges work; loaded by the CTO whenever it triages findings."
version: "1.0.0"
metadata:
  version: "1.0.0"
---

# Judging work

The golden rule for every review, probe, audit, QA check, moderation and triage of findings in a Gov OS project,
and in every repository that adopts it. It grants nothing; the guard and the role file decide what a session may do
(CAP-24.b). Source: DEC-1204, which merges ADR-0001 (DEC-039), DEC-801 and DEC-1010.

## 1. The threat model
- Gov OS guards against **honest agent mistakes, plausible accidents and drift in ordinary work**.
- It is **not** a security boundary against a process with the same privileges, built to defeat it on purpose.
  The hard boundary is git history, CI on a protected branch and the owner's signed approvals (ADR-0001).
- Judge every change against that model, not against an imagined adversary.

## 2. What may block
Ask of every finding, word for word:
1. "Can an honest agent hit this in ordinary work?"
2. "Does it fail open or lose work?"

- **A finding blocks only if the answer to both is yes, and it is within the change's scope.**
- **A finding that needs a deliberate construction** (a decoy, a booby-trap, a link planted at a protected name, git
  environment variables or replace refs set by hand, alternates, a chained escape, an interpreter used to evade a
  rule) **is a Wave 3 row, never a new round.**
- **A finding outside the change's scope** is a row for the ticket that owns it, never a round for this one.
- Every finding in a probe, review or audit record carries two lines:
  `Ordinary work: yes|no, because ...` and `Consequence: fails open|loses work|other`.

## 3. How reviews converge
- **A moderator, not a circle of reviewers.** The moderator (the QA engineer or the Senior Engineer; the CTO until
  those layers run) triages every finding against the change's own scope and KPI lines, by section 2, before
  anything goes back to the builder.
- **At most two review rounds.** If something still blocks after the second, it goes to the owner once, with
  options and costs. No third routine round, no exception by habit.
- **No extra round on its own:** when a ticket resumes anyway, accepted fixes ride along in that resume.
- **A risk that exists only when a feature is on** is an entry criterion of the ticket that switches it on.
- **READY is computed by code, never declared by an agent:** each reviewer ends its record with one fenced
  `verdict` block, unquoted, a structured verdict per KPI line (pass or fail, each finding's scope and class);
  the close and the merge queue compute READY from it.

## 4. Doing it
- **As a reviewer, auditor, probe or QA engineer:** read the change, its ticket and its KPI lines; judge each line;
  class each finding by section 2; write the two lines per finding; end with the verdict block. Never repair what
  you judge.
- **As a moderator or the CTO triaging:** take the reviewer's findings, keep only the blocking ones for the
  builder, turn the rest into rows (Wave 3, or the owning ticket), count the round, and send the third one to the
  owner, never back to the builder.
- **In a package that proposes a round:** state the classification of its findings on one line, before the
  recommendation.

## 5. What this skill is not
- It does not lower a wall: a finding an honest agent can hit that fails open is fixed, always.
- It does not replace the guard, the walls or the held-out rules; those still decide what any session may read.
