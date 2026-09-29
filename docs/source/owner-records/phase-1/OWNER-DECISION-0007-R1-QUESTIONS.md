# OWNER-DECISION-0007 — Owner answers to the two open R1 questions

| Field | Value |
|---|---|
| Record | OWNER-DECISION-0007 |
| Date | 2026-09-18 |
| Raised by | AR-0025 (`SRR2-R1-C1`) and AR-0027 (`AR27-OD1`) |
| Classification | binding owner answers; **not** an R1 acceptance and **not** an implementation authorisation |

## 1. `AR27-OD1` / `GATE-OWNER-R1-MACHINE-STATE-ANCHOR` — KEEP CURRENT DERIVATION

**Owner answer.** Protected machine state continues to derive from `XDG_STATE_HOME`/`HOME`. It is **not** anchored to a
fixed machine-domain path.

**Binding effects.**
- No change to the accepted R0 bootstrap/trusted-boundary assumption. **`R0_OWNER_READJUDICATION_REQUIRED` is NOT
  triggered**, and `GATE-R0-ARCH-ACCEPT` stands satisfied on the accepted candidate.
- The residual asymmetry is accepted as an owner-adjudicated position, not a defect: `GOV_MACHINE_STATE_DIR` remains
  refused on a provisioned machine, while `HOME`/`XDG_STATE_HOME` relocation by an owner-privileged process remains
  possible and in-boundary under ARCH-0003 §1, which independently disclaims protection from a hostile local admin.
- The certification harness keeps its per-scenario `XDG_STATE_HOME` isolation.
- `AR27-OD1` is **closed**. It must not be raised as an R1 blocker, and no repair role may change machine-state path
  resolution on its account.

## 2. `SRR2-R1-C1` / `GATE-OWNER-R1-BREAK-GLASS-EXIT` — KEEP THE STRICTER READING (b)

**Owner answer.** Exit from `DEGRADED — RECOVERY ONLY` requires a verified, authenticated release at or above **both**
the signed minimum secure release **and** the protected local high-water.

**Binding effects.**
- This **confirms** the orchestrator's fail-safe interim rather than changing it. `breakglass::exit_satisfied` with
  `EXIT_POLICY = "b_stricter_both_floors"` is now the owner-decided policy, no longer an interim assumption. No code
  change is required.
- It **supplements** `OWNER-DECISION-0006` requirement 7, which named only the signed minimum secure version. Where the
  two differ, this record governs the exit condition: requirement 7's floor is necessary but not sufficient.
- A machine below its protected high-water stays marked `DEGRADED — RECOVERY ONLY` even after reaching the signed
  minimum secure release. The marking's lifetime is therefore defined over both floors, matching the ingress-wide floor
  rule accepted at R0.
- `SRR2-R1-C1` is **closed**. The single policy point stays single; it must not be widened.

## Scope discipline

This record answers two questions. It does not accept the R1 candidate, does not authorise a release, does not alter
D-0007, D-0009, the accepted ARCH-0003 body or the frozen R0/R1/R2/R3 boundary, and does not revive CP-1.
