---
id: ADR-0001
title: Threat model — the Gov OS guards against mistakes and drift, not a same-privilege adversary
type: decision
status: ACCEPTED
date: 2026-09-30
depends_on: []
decisions: [DEC-039, DEC-075, DEC-007, DEC-046, DEC-083, DEC-095, DEC-096, DEC-152, DEC-156, DEC-161, DEC-163, DEC-1204, DEC-1211, DEC-1214, DEC-1219]
supersedes: []
constrains: [CHARTER-v6, CONTRACT-v5, ADR-0002]
state_class: AUTHORITATIVE
---

# ADR-0001 — Threat model

> **Revised 2026-11-19 to Charter v6 and Contract v5** (EMERGENCY-2 §2, DEC-1211; the owner's decisions DEC-1214 G5 and
> DEC-1219). The threat model stands unchanged: mistakes and drift, not a same-privilege adversary. What changed is how
> mistakes are met: the guard, the sandbox and the permission prompts of the first text are retired, and the boundary and
> the catching are as Charter v6 §2 states them. The text of the 2026-09-30 decision is in git history.

## Context and Problem Statement

The Rust Gov OS spent Phase 2 (about 97 agent runs, eight review rounds) trying to make a process that runs with the
owner's OS privileges secure against itself. Every round found new HIGH findings. The project's own records named the
cause: a confused-deputy, ambient-authority problem. An HMAC seal whose key the same user can read is not proof-grade
authority (register §4A, DEC-039). Contract v3 and the Framework never stated a threat model. So acceptance drifted
towards exhaustive adversarial closure (DEC-058).

What must the Gov OS defend against, and where is the hard boundary?

## Decision Drivers

- Keep agents accurate, bounded and traceable at low token cost (Charter v6 §1, DEC-004).
- One solo owner, one workstation, and a private GitHub repository without GitHub Pro (DEC-074 Q13).
- Machinery against an adversary the design cannot stop produces endless review loops. A review therefore runs at most
  two rounds and then goes to the owner once, with options (EMERGENCY-2 §3.6, DEC-1204; DEC-044 as amended by DEC-096
  and by DEC-1214).
- Prevention by guards, sandboxes and permission prompts cost more work than the mistakes it stopped, and a shell command
  can reach anywhere the owner can. Mistakes are caught and corrected, not prevented (EMERGENCY-2 §2.1, DEC-1211).

## Considered Options

1. **Mistakes and drift only.** The deterministic landing catches agent mistakes and corrects them. The hard boundary
   lives outside the agent's process: git, the owner's push and release, hourly bundles, pre-push and CI.
2. **Same-privilege adversary.** Root of trust, sealed authority state, plugin byte-binding, install-authority
   envelopes, break-glass recovery.
3. **Mistakes and drift, with branch protection as the boundary.** Needs GitHub Pro.

## Decision Outcome

Chosen: **option 1**, as DEC-039 states it and DEC-075 amends it.

- **Purpose.** The Gov OS keeps agents accurate, bounded and traceable. It is **not** a security boundary against a
  process running with the owner's OS privileges.
- **Catch and correct, do not prevent.** There is no guard, no sandbox, no box and no permission prompt (EMERGENCY-2
  §2.2, DEC-1211; this retires the path guard of DEC-041, the OS sandbox of DEC-152 and DEC-161, and the guard-and-sandbox
  reading of DEC-007 and DEC-076). Agents have full permission in the repository, the worktree and the run folder they
  work in. Sessions stay apart by where they start, the folders they are given and their brief; nothing enforces it. A
  mistake is caught by the deterministic landing (it merges, runs the impact-selected tests and checks paths and who
  wrote the tests; a path outside the ticket's allowed paths is a notice, a test-authorship breach is refused) and by
  the transcript scan for hidden question sets (CAP-66), then corrected by finding and removing its cause.
- **The hard boundary (DEC-075, as Charter v6 §2 states it):**
  1. git history, which is never rewritten;
  2. the owner's own `git push` and release from the owner's own terminal, with two settings deny lines, `git push` and `sudo`,
     that hold in every permission mode (EMERGENCY-2 §2.4, §2.5);
  3. an hourly `git bundle` of each repository, kept outside the tree (CAP-67);
  4. the lefthook **pre-push gate (G3)** on the owner's machine, with **GitHub Actions CI (G4–G5)** on every push as a
     visible **advisory** result. It runs the deterministic checks; model-dependent tests run at G3 and leave an
     evidence record bound to the head commit, which CI checks (DEC-087).

  The landing merges into integration; only the owner pushes. `main` is not branch-protected. Enabling protection later
  changes no other decision.
- **Approval facts.** "Approved", "verified" and "registered" are facts only when they come from git records plus the
  owner's account: an owner commit, a signed tag or a PR approval. This is the simplified D-0007 rule (DEC-046). There
  are no in-process trust classes.
- **Tool installs.** The Gov OS runs no automated install gate and no argv classification. The CTO approves and records
  every install in the tool registry; no prompt stands in the way, and an agent installs nothing outside its own
  worktree's folders without the CTO's approval (DEC-1214 G7, Contract v5 §2 Tool installs). `sudo` stays with the owner
  (DEC-083, amending DEC-040).
- **Secrets.** Sensitivity classes keep secret-class files out of every index. One full gitleaks scan runs once before a
  repository goes public or is shared with a third party, and no scan runs while it is private (EMERGENCY-2 §2.11,
  DEC-1219; CAP-03).
- **Mistake scenarios.** Qualification scenarios phrased as attacks become mistake scenarios. For example, "policy
  tampering" becomes "an agent edits a policy file by mistake, and CI must catch it" (DEC-067).

### Consequences

- **Good:**
  - The loop that produced Phase 2's findings cannot recur. The contract's acceptance checks are observable
    behaviours, not closure proofs.
  - The design is small: no key management, sealed state or plugin trust.
- **Bad:**
  - A deliberate same-privilege actor can bypass the landing's checks.
  - Until branch protection exists, the boundary rests partly on the owner's own push and release discipline.
  - A shell command can reach anywhere the owner can; that is caught after the fact, by the landing and the transcript
    scan, not prevented.
  - Both costs are accepted.
- **Non-goals this creates** (Charter v6 §7):
  - CAP-26 plugin trust boundary;
  - CAP-60 below-floor recovery and break-glass;
  - full root of trust (CAP-02 is LITE: releases are pinned and hash-verified, with no signing; signing waits for
    friction, CAP-02.c);
  - in-process L0–L5 authority (CAP-21 is LITE);
  - the install-authority envelope (CAP-25 is LITE: the CTO approves and records every install).

### Confirmation

- The fidelity audit at the release acceptance and at adoption stages A5, AS, A7 and A10 checks that nothing
  reintroduces same-privilege-adversary machinery or the retired guard, sandbox and prompts (DEC-070; MR-4, DEC-1214
  G6).
- The landing, CI and the pre-push gate re-run the deterministic checks (DEC-007, DEC-025).
- The qualification scorecard counts any forbidden outcome as a failure (SCORECARD_FORMAT M15).

## More Information

- **Sources:** register DEC-039, DEC-075, DEC-007, DEC-046, DEC-083, DEC-152, DEC-156, DEC-161 (the last three on the
  retired sandbox), DEC-1211 and DEC-1214 (EMERGENCY-2 §2), DEC-1219; the Phase-2 owner records (OWNER-DECISION-P2-0003,
  P2-0005, OWNER-CLARIFICATION-P2-0004), which are superseded where they assume a same-privilege adversary.
- **Revisit trigger:** multiple humans with different authority, or a hosted multi-tenant deployment.
