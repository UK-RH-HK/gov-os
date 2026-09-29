# OWNER-DECISION-P2-0001 — Agent-role identity (OD-P2-01): Option A, keep the adapter boundary

| Field | Value |
|---|---|
| Record | OWNER-DECISION-P2-0001 |
| Date | 2026-09-19 |
| Gate | HG-P2-0001 (`HG-P2-0001-OWNER-DECISIONS.md`), question OD-P2-01 |
| Channel | answered by the product owner in the active chat (AskUserQuestion), after presentation of the full gate package |
| Classification | binding owner security-policy decision for Phase 2 (private/local profile) |
| Raised by | fresh independent synthesis P2-AR-0007, `release/capability-baseline/audit-0/synthesis/owner-decisions-required.md` |

## Decision

**Option A — keep the adapter boundary for agent roles.** For the private/local profile through Phase-4 qualification, an
agent's role (L0–L4) may continue to be declared by the harness or adapter that launches it, as D-0007 consequence 5 states.
Governance OS is **not** required in Phase 2 to bind each agent session to its assigned role by an OS-issued credential.

## What remains required regardless (not changed by this decision)

- **BC-P2-10:** human answers, human-approval assertions and presentation evidence come only from an authenticated human
  channel the acting agent cannot operate (Contract v3 L3; D-0007 rule 2; ARCH-0003 §8; OWNER-DIRECTIVE-0004).
- **BC-P2-08:** an invocation that declares no role receives no privileged authority; the declared role is applied
  consistently on every path; guard coverage and FREEZE_WRITES/PAUSE hold.
- **BC-P2-09:** T2 facts are honoured only when an OS operation produced them.

## Recorded residual risk

A compromised or misbehaving agent can claim a higher **agent** role (never a human one). Phase-4 qualification treats
agents as honest about their assigned role; any adversarial-agent fault class measures this known, accepted gap. Revisit
at R2/R3, or if Phase-4 fault classes model hostile agents.

## Effect

No new Phase-2 blocker class. BC-P2-34 carries no agent-identity extension. D-0007 is unchanged; its explicit transition
record remains open and was not requested.
