# Copy: DEC-1204 (how work is judged) and the judging-work skill's approved text

Source: `docs/DECISION_REGISTER.md`; the skill `governance/project/orchestration/packages/judging-work.SKILL.md` (sha256 `0fc1c502f553eb780bb0af4652b04f676853b10e097270c2d6ad2bea89a5f5c7`, the owner's yes 0fc1c502). Note: W2-195 (not merged; held by the emergency) quotes one front-matter value (`description:`) in the kernel copy because the approved text's YAML does not parse; every other byte as approved. The skill's front matter is shown in a fenced block.

### DEC-1204 — How work is judged: one golden rule (merges ADR-0001 / DEC-039, DEC-801 and DEC-1010 item 1) (standing); P-GOLDEN-RULE-1 (a); the skill `judging-work` approved (0fc1c502); W2-195 filed
- **Status:** ACCEPTED (owner, 2026-11-16 before 16:00, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-11-16)`; standing) · **Under:** DEC-039, DEC-801, DEC-802, DEC-803, DEC-1010, DEC-974, CAP-33 · **Changes:** DEC-039, DEC-801, DEC-1010 (1): each keeps its id and now points here
- **Decision:**
  - (1) **The threat model:** Gov OS guards against honest agent mistakes, plausible accidents and drift in ordinary work, not a same-privilege adversary; the hard boundary is git history, protected-branch CI and the owner's signed approvals.
  - (2) **What may block:** only a finding, within the change's scope, that an honest agent can hit in ordinary work and that fails open or loses work; a finding that needs a deliberate construction (decoys, booby-traps, planted links, hand-set git environment or replace refs, chained escapes) is a Wave 3 row, never a new round.
  - (3) **How reviews converge:** a moderator triages every finding against the change's scope; at most two rounds, then the owner once with options; no extra round on its own; READY computed by code from each reviewer's structured verdict.
  - (4) It applies to every review, the ACTs, the job runner and the box included (the owner, 2026-11-16 before 16:00).
  - (5) It lives in one kernel skill, `judging-work`, preloaded by every role that judges work and put into every such brief by `gov brief`; it ships through the kit and every release.
  - (6) **P-GOLDEN-RULE-1 (a):** this entry's text; the product ticket W2-195 (the skill preloaded, briefed and checked, shipped; section 3) on the owner's P1 (DEC-974), top priority, started today; EXAMIN by section 5 (a) (the text by REPLIES.md, applied by hand until its copy installs the release carrying W2-195); the interim paragraph (section 6) pasted word for word into every reviewer, auditor, probe and QA brief the CTO or a lead writes until W2-195 lands.
  - (7) **`yes judging-work 0fc1c502`:** the skill's text (`judging-work.SKILL.md`, sha256 `0fc1c502f553eb780bb0af4652b04f676853b10e097270c2d6ad2bea89a5f5c7`) is approved; the kernel files go by W2-195's CIT-P, whose approval is on the committed bytes (the same text).
  - (8) **The golden rule in the agent instructions:** CLAUDE.md and AGENTS.md (with their source `.rulesync/rules/governance.md`) gain one section, "## Golden rule: how work is judged (DEC-1204)", by ACT-GOLDEN-RULE-1 (class (b), DEC-1173: a reviewed bundle, the owner's yes, applied by the operator agent), so no brief misses it.
- **Basis:** the owner's messages of 2026-11-16 before 16:00 ("make ADR-0001 (DEC-039), DEC-801 and DEC-1010 one golden rule, so they are never forgotten again …"), before 16:00 ("add it your self as a golden decision to your claude.md, or agent.md whatever works, so its never missed in any briefs. also need that package to establish this rule, as priority now …; both need to end today") and before 16:00 ("P-GOLDEN-RULE-1 (a). yes judging-work 0fc1c502. Both today, top priority.").
- **Governing sources:** DEC-039 (ADR-0001); DEC-801 to DEC-803; DEC-1010; DEC-1173; DEC-974; CAP-33; CAP-24.b; packages `P-GOLDEN-RULE-1.md` and `judging-work.SKILL.md`.

---

## The judging-work skill (approved text)

```yaml
---
name: judging-work
description: The one rule for judging work (ADR-0001, DEC-801, DEC-1010, merged by DEC-1204): the threat model, what may block, how reviews converge. Preloaded by every role that judges work; loaded by the CTO whenever it triages findings.
version: "1.0.0"
metadata:
  version: "1.0.0"
---
```

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
