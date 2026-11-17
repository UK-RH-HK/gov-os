---
name: reviews-moderated-dec1010
description: owner 11-16: DEC-1010 for every review (ACTs, job runner, box): a moderator triages findings against scope; blocks only if reachable in ordinary work AND fails open or loses work; crafted tricks (decoys, booby-traps, chained escapes) = Wave 3 rows; max two rounds, then the owner once
metadata:
  type: feedback
---

The owner, 2026-11-16 ~16:3x: "DEC-1010 applies to every review, the ACTs, the job runner and the box included: a moderator triages each finding against the change's scope; a finding blocks only if it is reachable in ordinary work and fails open or loses work; a path that needs a deliberately crafted trick (decoys, booby-traps, chained escapes) is recorded as a Wave 3 row, not a blocker; at most two rounds, then it comes to me once. The job runner went ten rounds against this."

**Why:** adversarial reviews kept finding crafted escapes and sent designs round after round (the runner ten rounds, the box three) without shipping anything.

**How to apply:** every review brief I write asks the reviewer to class each finding: (a) reachable in ordinary work and fails open or loses work = blocking; (b) needs a crafted trick = a Wave 3 row, not blocking. Then I moderate (or a separate moderator does) before sending anything back. Two rounds at most, then the owner once. Applies at once to GF-8's round 2 and the box's exception package. Related: [[rename-defeats-link-checks]].

**GOLDEN RULE (owner 11-16 ~17:0x; DEC-1204 merges ADR-0001/DEC-039, DEC-801, DEC-1010 (1); skill `judging-work`, text drafts/golden-rule/SKILL.md 0fc1c502):** Threat model: honest agent mistakes and drift, not a same-privilege adversary. Blocks ONLY: within scope, an honest agent can hit it in ordinary work, AND it fails open or loses work. A deliberate construction (decoy, booby-trap, planted link, hand-set git env or replace refs, chained escape) = a Wave 3 row, never a new round. Convergence: a moderator (me until QA/SE run) triages each finding against scope before anything goes back; at most two rounds, then the owner once; READY computed by code from the verdict block. EVERY reviewer/auditor/probe/QA brief I write carries this rule (pasted from P-GOLDEN-RULE-1 §6) until gov brief injects it; every finding gets "Ordinary work: yes|no, because …" and "Consequence: fails open|loses work|other". CLAUDE.md/AGENTS.md and ~/.claude/CLAUDE.md are class (b): the rule goes there by ACT-GOLDEN-RULE-1, not by my edit.
