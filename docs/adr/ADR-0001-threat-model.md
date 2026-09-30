---
id: ADR-0001
title: Threat model — the Gov OS guards against mistakes and drift, not a same-privilege adversary
type: decision
status: PROPOSED
date: 2026-09-30
depends_on: []
decisions: [DEC-039, DEC-075, DEC-007, DEC-046, DEC-083]
supersedes: []
constrains: [CHARTER-v5, CONTRACT-v4, ADR-0002]
---

# ADR-0001 — Threat model

## Context and Problem Statement

The Rust Gov OS spent Phase 2 (about 97 agent runs, eight review rounds) trying to make a process that runs with the
owner's OS privileges secure against itself. Every round found new HIGH findings. The project's own records named the
cause: a confused-deputy, ambient-authority problem. An HMAC seal whose key the same user can read is not proof-grade
authority (register §4A, DEC-039). Contract v3 and the Framework never stated a threat model. So acceptance drifted
towards exhaustive adversarial closure (DEC-058).

What must the Gov OS defend against, and where is the hard boundary?

## Decision Drivers

- Keep agents accurate, bounded and traceable at low token cost (Charter v5 §1, DEC-004).
- One solo owner, one workstation, and a private GitHub repository without GitHub Pro (DEC-074 Q13).
- Machinery against an adversary the design cannot stop produces endless review loops (DEC-044).

## Considered Options

1. **Mistakes and drift only.** Guardrails catch agent mistakes early. The hard boundary lives outside the agent's
   process: git, pre-push, CI, and owner-only merge.
2. **Same-privilege adversary.** Root of trust, sealed authority state, plugin byte-binding, install-authority
   envelopes, break-glass recovery.
3. **Mistakes and drift, with branch protection as the boundary.** Needs GitHub Pro.

## Decision Outcome

Chosen: **option 1**, as DEC-039 states it and DEC-075 amends it.

- **Purpose.** The Gov OS keeps agents accurate, bounded and traceable. It is **not** a security boundary against a
  process running with the owner's OS privileges.
- **Guardrails, not a boundary.** The harness hooks, the default-deny path guard (DEC-041) and the post-command
  containment check (DEC-076) exist to catch mistakes. A stalled or bypassed hook is not a breach of the model, because
  the boundary sits downstream of it (DEC-007).
- **The hard boundary (DEC-075):**
  1. git history, which is never rewritten;
  2. the lefthook **pre-push gate (G3)** on the owner's machine;
  3. **GitHub Actions CI (G4–G5)** on every push, as a visible **advisory** result. It runs the deterministic checks;
     model-dependent tests run at G3 and leave an evidence record bound to the head commit, which CI checks (DEC-087);
  4. the owner's rule that **only the owner merges, and only on green**.

  `main` is not branch-protected. Enabling protection later changes no other decision.
- **Approval facts.** "Approved", "verified" and "registered" are facts only when they come from git records plus the
  owner's account: an owner commit, a signed tag or a PR approval. This is the simplified D-0007 rule (DEC-046). There
  are no in-process trust classes.
- **Tool installs.** The Gov OS runs no automated install gate and no argv classification. The orchestrator installs
  a tool only after the owner approves a decision package in chat, and records the install in the tool registry.
  Install commands are `ask` for the orchestrator and denied for every other role. `sudo` stays with the owner
  (DEC-083, amending DEC-040).
- **Mistake scenarios.** Qualification scenarios phrased as attacks become mistake scenarios. For example, "policy
  tampering" becomes "an agent edits a policy file by mistake, and CI must catch it" (DEC-067).

### Consequences

- **Good:**
  - The loop that produced Phase 2's findings cannot recur. The contract's acceptance checks are observable
    behaviours, not closure proofs.
  - The design is small: no key management, sealed state or plugin trust.
- **Bad:**
  - A deliberate same-privilege actor can bypass the guardrails.
  - Until branch protection exists, the boundary rests partly on the owner's merge discipline.
  - Both costs are accepted.
- **Non-goals this creates** (Charter v5 §7):
  - CAP-26 plugin trust boundary;
  - CAP-60 below-floor recovery and break-glass;
  - full root of trust (CAP-02 is LITE: SSH-signed tags plus a hash manifest);
  - in-process L0–L5 authority (CAP-21 is LITE);
  - the install-authority envelope (CAP-25 is LITE).

### Confirmation

- The S1-A fidelity audit and every wave-exit audit check that nothing reintroduces same-privilege-adversary
  machinery (DEC-070).
- CI and the pre-push gate re-run every hook check (DEC-007, DEC-025).
- The qualification scorecard counts any forbidden outcome as a failure (SCORECARD_FORMAT M15).

## More Information

- **Sources:** register DEC-039, DEC-075, DEC-007, DEC-046, DEC-083; the Phase-2 owner records (OWNER-DECISION-P2-0003,
  P2-0005, OWNER-CLARIFICATION-P2-0004), which are superseded where they assume a same-privilege adversary.
- **Revisit trigger:** multiple humans with different authority, or a hosted multi-tenant deployment.
