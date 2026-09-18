# HG-P2-0001 — Human Decision Gate: two owner decisions for Phase 2

| Field | Value |
|---|---|
| Gate | HG-P2-0001 |
| Raised by | fresh independent synthesis P2-AR-0007 (`owner-decisions-required.md`), classification confirmed by the Phase-2 orchestrator against the owner's Phase-2 directive |
| Presented | in the active chat, 2026-09-18, after repair round 1 was dispatched (presentation ≠ answer) |
| Decisions | **OD-P2-01** agent-role identity binding; **OD-P2-02** unprovisioned-machine posture |
| Blocks | only BC-P2-36's admission requirement and any agent-identity extension of BC-P2-34 |
| Does not block | every determined repair requirement — repair round 1 is already running (Contract v3 L4, non-global blocking) |
| Full analysis | `release/capability-baseline/audit-0/synthesis/owner-decisions-required.md` |

## Why these reach the owner

The owner's Phase-2 directive reserves security-policy trade-offs, availability/usability/cost trade-offs and changes to an
accepted boundary for the owner. Both items meet that test. OD-P2-02 falls in a class the owner has already reserved
(OWNER-DECISION-0005 §1: "an architecture role must not select this security-versus-availability posture on the owner's
behalf"). The other items the auditors flagged — the human-approval channel, the default role, plugin self-declaration,
the post-install integrity anchor and hiding unauthenticated installs — were ruled **already determined** by Contract v3,
D-0007, ARCH-0003 and OWNER-DIRECTIVE-0004/OWNER-DECISION-0006. They are ordinary repair requirements and are not asked.

## OD-P2-01 — Agent-role identity (L0–L4)

**Question.** For the private/local profile, may an *agent's* role (L0–L4) keep being declared by the harness or adapter
that launches it (D-0007 consequence 5), or must Governance OS itself bind each agent session to its assigned role?

Already required whatever you choose: human approval comes only from an authenticated human channel; a call with no
declared role gets no privileged authority; OS-written records are honoured only when an OS operation produced them.

| Option | Meaning | Consequence |
|---|---|---|
| **A — keep the adapter boundary** (recommended) | Agent roles stay declared by the launching harness. | No extra scope. Residual risk recorded: a misbehaving agent could claim a higher *agent* role (never a human one). Revisit at R2/R3. |
| B — OS-issued role credentials | The OS issues a role credential per dispatched agent and checks it on every privileged path. | Only effective with per-agent process/account isolation, which the private/local profile does not assume: infrastructure cost and operator friction; adds a new class to Phase 2. |
| C — bind L3/L4 only | Change-controller and orchestrator authority needs an owner/administrator-issued credential; L0–L2 stay declared. | Middle cost; protects the roles that approve and execute change; adds a new class to Phase 2. |

## OD-P2-02 — Machines with no trust anchor

**Question.** On a machine with no administrator-provisioned trust anchor (the product's current default), may privileged
kernel material still be installed — and must Phase-4 qualification run on provisioned machines?

Already required whatever you choose: an unauthenticated installation is never presented as current, verified or
certified, and doctor/audit disclose it. Provisioned machines already refuse unsigned, tampered and below-floor material.

| Option | Meaning | Consequence |
|---|---|---|
| **A — refuse external-source installs until provisioned** (recommended) | Contract v3 A2 bullet 1 read literally. Dev/test machines provision a throw-away root (as the test harness already does). The binary's own embedded payload may install only as an explicitly marked bootstrap mode. Phase-4 qualification and all release evidence run on provisioned machines. | Most secure; changes the documented first-run path (provision first); harness/docs updates; no production key material needed before R2. |
| B — allow as a marked non-production mode | External sources still install with authenticity UNKNOWN, visibly marked, never presented as current, excluded from qualification and release evidence. | Keeps availability; leaves an unauthenticated install path whose safety depends on every consumer honouring the marking. |
| C — ship or pre-install production root public keys | Every default machine is provisioned. | Needs owner-controlled production key material and custody (an R2 key-ceremony matter) before Phase 4. |

## Recording

The owner's answers will be recorded as `OWNER-DECISION-P2-0001` (OD-P2-01) and `OWNER-DECISION-P2-0002` (OD-P2-02) in
this directory and the Phase-2 orchestration resumes automatically from durable state.
