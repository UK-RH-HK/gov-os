# 03 — Residual determination

Each residual the architect declares in the compatibility/transaction area is judged against the review-r2 criteria:
a residual is acceptable iff **(1)** its trigger needs a capability the model excludes, **or (2)** it is unavoidable
under the chosen assumptions **and** its bound is stated correctly **and** the verdict surface does not overstate it
**and** no reasonable design removes it.

## Legacy-binary containment residuals (`26` §8)

| ID | Residual (pack) | Determination |
|---|---|---|
| LR-1 | Legacy binary on a working copy not yet on the RoT-1 commit operates on the legacy layout. | **Accepted.** Confirmed RV3-C-A09 (`git revert` and checkout-across-migration both leave a pure legacy project with no `governance/trust`, so nothing RoT-1 to damage; checkout back restores occupation exactly). Bound stated correctly. |
| LR-2 | A same-user process removes occupation entries → RoT-1 reports `PARTIAL`; "the result is not a RoT-1 layout; A3-class". | **Not accepted as stated.** The bound understates the reachable harm: removal + a legacy `init --force` yields a `verified:true` legacy install that serves restricted material while `governance/trust/` persists (RV3-C-A05). Finding **C-1**; the corrected bound (governance/trust never mutated, RoT-1 fails closed) is accepted, the wording/test are not. |
| LR-3 | Explicit operator output paths of producer commands write where pointed. | **Accepted.** Explicit A14/A10 action; RoT-1 detects PPS changes and strength weakening. Not exercised here (producer commands are RoT-1-only). |
| LR-4 | Fresh clones accept the repository overlay as current project configuration. | **Accepted** as A2 authority over project config; per-machine detection after the first record. Trust-security scope (reviewer B). |

## Transaction / recovery residuals (`18` §11, `20` §10)

| ID | Residual (pack) | Determination |
|---|---|---|
| VR-1 | A3 modifies installed files between two units of work; the next unit detects it (VU-11). | **Accepted at design level** (spec-only; RT-86). Closes the R2-M7 "no next process" gap for long-lived processes by bounding snapshot age. Not executable pre-implementation. |
| VR-2 | A3 ignores advisory locks → refusals only. | **Accepted.** |
| VR-3 | Non-`gov` subprocesses write PPS/overlay/records/VTS. | **Accepted at design level:** PPS detected next unit of work; overlay via the strength vector (`26` §6); records never authorise trust decisions (`27`); VTS same-user. This is the transaction-relevant part of R2-M1/M9 and is closed in design. |
| VR-4 | Plugin runtimes/model files consumed by path. | Accepted (scope of `10`). |
| RR-1 | Automatic rollback may leave an ineligible install; fails closed; remedy = complete an update. | **Accepted.** Fail-closed. |
| RR-2 | A2-delivered older eligible release accepted as installed content on a machine without a per-project record. | Trust-security scope (reviewer B); the transaction part (union record, no dropped statements) is addressed by `18` §5.2. |
| RR-3 | A3 deletes the per-project record/VTS. | Accepted (same-user); machine becomes `UNANCHORED`, fails closed under OP-7 (a)–(c). |

## Freshness-on-recovery interaction (noted, not a residual objection)
`20` §2 requires freshness `ANCHORED`/`WITNESSED` on downgrade/restore, so an **unanchored** machine cannot roll back or
restore-from-backup. This is bounded because a `PARTIAL`/`TAMPERED` install is repairable unanchored by
`kernel reinstall` of the **same** statement digest (`17` §7: "none (integrity remedy)"), so availability of recovery is
preserved for the common case. Carried as a note in `04` C-2. Trust-security aspects belong to reviewer B.
