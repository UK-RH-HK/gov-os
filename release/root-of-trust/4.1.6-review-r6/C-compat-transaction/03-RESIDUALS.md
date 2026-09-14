# 03 — Residual determinations

Every residual the architect declares in the compatibility/transaction area is judged against explicit criteria (the
review r2/r3/r4/r5 lineage): a residual is **ACCEPTED** iff **(1)** its trigger needs a capability the model excludes, or
**(2)** it is unavoidable under the chosen assumptions **and** its bound is stated exactly **and** no verdict surface
overstates it **and** no reasonable design removes it. **ACCEPTED WITH CONDITION** names the carried requirement;
**NOT ACCEPTED** would name a finding. Determinations are made against revision 6 as written (`4106885`).

## Legacy-binary containment (`26`)

| ID | Residual (pack) | Determination |
|---|---|---|
| LR-1 | Legacy binaries on a working copy not on the RoT-1 layout commit (incl. after `git revert`) operate a legacy layout. | **ACCEPTED** (R-2). `CHECKOUT_PRE` and `RESTORE_PRE_GOV` are `LEGACY` (occupation absent), `KERNEL_TAMPERED`; a RoT-1 binary is read-only on them. Bound stated. |
| **LR-2** (restated, RV3-M6) | Occupation removed, or pre-migration paths restored by Git → the legacy binary regains a `verified` install and can write `governance/trust/**`; RoT-1 fails closed; strength loss reported where recorded. | **ACCEPTED (bound holds).** Every removed/restored/merged tree with legacy entries is `PARTIAL(occupation)` or `LEGACY` (struct6 occupation-removal → `PARTIAL`; gitops6 `CHECKOUT_PRE`/`RESTORE_PRE_GOV` → `LEGACY`); the revision-6 closed entry sets keep the intact-layout subdirectory trigger fail-closed (matrix R2-H4 property). No RoT-1 mechanism can stop a legacy binary writing paths the layout no longer occupies; the pack states exactly that. |
| LR-3 | Explicit operator output paths; nested installs outside `governance/`. | **ACCEPTED** (R-2). Nested installs in `vendor/` and the transaction area are reported (`NESTED_LEGACY_PROJECT`/D039), the outer state unchanged (R6V, matrix P-VEND). |
| LR-4 | Fresh clones accept the repository overlay as current project configuration. | **ACCEPTED** as A2/T4 authority; per-machine detection after a record (reviewer B's freshness scope). |

## Layout durability

| Observation | Determination |
|---|---|
| The occupation spans three tree roots (`governance/`, `spec/audits/`, `.governance-runtime/`); cone/non-cone sparse checkout drops entries → `PARTIAL(occupation)`. | **ACCEPTED (fail closed).** Doctor note carried (C-6). |
| `core.autocrlf=true`, project `* text=auto`+`core.eol=crlf`, project `* text eol=crlf` clones. | **ACCEPTED (member protects).** The revision-6 `.gitattributes` member keeps the kernel bytes; the trees are `COMPLETE`, byte-equal to `RCS(D)` (gitops6; attrprec6; struct6). RV5-C-M1/RV5-M6 closed. |
| `.git/info/attributes` `* text` (out-of-tree, highest precedence) overrides the member. | **ACCEPTED (fail closed).** The clone converts and is `PARTIAL(kernel_content_mismatch)`/`KERNEL_TAMPERED`; the stated condition is exact; doctor names the source. Availability/portability, not a trust bypass. Carried CR6-C-1. |
| A repo-root or deeper in-tree `.gitattributes` overriding the member. | **ACCEPTED (fail closed).** A root `.gitattributes` cannot override (member wins by depth); a kernel-level `.gitattributes` converts but is an extra kernel file → `kernel_content_mismatch` (attrprec6). |
| A global `core.excludesFile` / `.git/info/exclude` carrying `.governance-runtime/` re-drops the occupation under the untracking idiom. | **ACCEPTED (fail closed; condition stated + detected).** `PARTIAL(occupation)`, `check-ignore` names the source (gitops6). RV5-C-M2/RV5-M7 carried CR6-C-2. |
| Clean/shallow/partial clone, `git archive`, `clean -fdx`, `stash -u`, `worktree add`, checkout-across-migration-and-back, case-insensitive clone. | **ACCEPTED.** All `COMPLETE`, kernel intact (gitops6). |

## Transaction / recovery / snapshots (`18`, `20`) — design-level, unimplemented

| ID | Residual (pack) | Determination |
|---|---|---|
| VR-1 | A3 modifies installed files between units of work; the next unit detects it (VU-11). | **ACCEPTED at design level.** Not executable pre-implementation. |
| VR-2 | A3 ignores advisory locks → refusals only. | ACCEPTED (spec). |
| VR-3 | Non-`gov`/confined children write PPS, overlay, records, VTS. | **ACCEPTED at design level.** PPS detected next unit of work; journals honoured only if VTS-registered (`18` §5.1). |
| VR-4 | Plugin runtimes/model files consumed by path. | ACCEPTED (`10` scope). |
| RR-1 | Automatic rollback may leave an ineligible install; fails closed. | ACCEPTED (fail closed). |
| RR-2 | A2-delivered older eligible release on a machine without a record; `kernel reinstall` uses the lock identity. | **Transaction part ACCEPTED** (union record, no dropped statements, `18` §5.2; registration-scoped E7 at use, `20` §9). Freshness/eligibility depth is reviewer B's scope. Spec-only. |
| RR-3 | A3 deletes the per-project record / VTS. | ACCEPTED (`UNANCHORED`, fail closed). |
| Foreign / copied journal (RV2-A24) | A committed or copied journal, or crash-transaction residue, affects no clone. | **ACCEPTED (fail closed).** The transaction area is untracked (`.gitignore /.governance-runtime/*`), so a clone carries none of it; a local crash journal (R6CRASH) is `FOREIGN_TRANSACTION_ARTEFACT`, reported and inert (state stays `COMPLETE`, never `IN_TRANSACTION`). Confirmed by `build6`/`state_r6`. |
| C-2 | Cross-device transaction-area refusal; unanchored `PARTIAL` repairable. | **ACCEPTED at design level** (`18` §3, `20` §8). Not executable pre-implementation → carried. |

## Independent admission (`31`) — model-level

| ID | Residual (pack) | Determination |
|---|---|---|
| AD-1′ | The first-contact root admits a malicious first TCB with no key (root set of `32` §6). | Reviewer B's scope (trust/security); not a compatibility/transaction residual. |
| TB-1′ | A malicious binary run directly, outside admission, ignores every rule. | ACCEPTED (GB rules bind genuine binaries; the documented procedure never runs a candidate — `admtx6` T1 confirms C0-only without a record). |
| AD-2 | Same-account code executed before the first admission. | **ACCEPTED** — the fresh-store step now fires only at first admission (`31` R-ADM-8′; `admtx6` T2 keeps the store on re-admission; T3a moves aside a store that holds no record). |
| VR-B1′ | A same-account replacement of a user-writable binary is A3; such an install reaches only `31` §7.1. | ACCEPTED (`admtx6` T1/T7: a user-writable executable refuses C3 with `TCB_WRITABLE_BY_GOVERNED_ACCOUNT`). |
| (new, AR-0017) | A store that holds anchors but **no** admission record is treated as first admission and moved aside, discarding those anchors. | **ACCEPTED (fail safe).** Admission precedes anchoring (R-ADM-9), so this state does not arise in normal operation; if it is produced (partial state / crash during move-aside), the machine becomes `UNANCHORED` and must re-anchor — no stale anchor is read (`admtx6` T3a, T7). Noted for `31` R-ADM-8′ clarity; not blocking. |
| (new, AR-0017) | The reference honours an admission record by `binary_digest` across every `vts-<16>` store under the protected record root, without binding the store's lineage to the binary's own compiled lineage (GB-1′ says "for the lineage"). | **ACCEPTED (within the A3/RS-3 boundary).** Planting a record in the protected VTS root needs the protected account (A3), which can equally replace the binary; the binary's lineage is independently enforced (`TRUST_ROOT_LINEAGE_MISMATCH`, `31` §4). A model-clarity item, cross-scope with reviewer B on the genuine-binary rule; carried, not blocking (`admtx6` T8). |

## Conditions added after the transaction-state attacks (RV6-C-A15…A19)

The determinations above are qualified as follows. Each condition is a bound stated exactness or rule that the pack lacks;
none leaves a residual that grants trust beyond an accepted one, so none is NOT ACCEPTED.

| Residual | Condition | Reason |
|---|---|---|
| **LR-2** | ACCEPTED WITH CONDITION **RV6-C-M2** (CR6-C-7) | Its trigger list omits a crash during the first install transaction followed by the documented recovery, which reaches the same legacy outcome (crashmig6); the bound (RoT-1 never `COMPLETE`) holds on every executed prefix. |
| **LR-2 bound (2), LR-4** | ACCEPTED WITH CONDITION **RV6-C-M3** (CR6-C-8) | "Reported on every machine that recorded the vector" and "a machine with no record" are stated per machine; the record is keyed per path and/or `project_trust_id`, which ordinary duplication defeats. |
| **RR-2** (transaction part) | ACCEPTED WITH CONDITION RV6-C-M3 | E10's per-project sequence has the same identity defect. |
| **AD-2** | ACCEPTED WITH CONDITION **RV6-C-M5** (CR6-C-10) | The fresh store it rests on is undefined when the admission store and the account VTS differ (protected and CI installs). |
| Remedies never clear project-strength reports (`26` §6 item 3, `20` RB-3) | ACCEPTED WITH CONDITION **RV6-C-M4** (CR6-C-9) | `19` §9 item 4 and `18` §4 re-record at commit; the claim holds only under the rule CR6-C-9 states. |
| Crash in any phase (`18` §10, RT-16) | ACCEPTED WITH CONDITION RV6-C-M2 | The layout-migration steps and the exchange-to-journal window are not phases. |
| Governance-tree litter "inert: nothing reads it" (`26` §4) | ACCEPTED WITH CONDITION **RV6-C-L4** (CR6-C-3) | `governance/overlay/spec` litter is read as a default-deny overlay file (fail-safe weakening report). |
| Binary rollback keeps its record (`20`, `31` R-ADM-7′) | ACCEPTED WITH CONDITION **RV6-C-L6** (CR6-C-12) | The accepted-TBM high-water refuses a lower-TBM rollback above C0; unstated. |

## Summary

| Determination | Items |
|---|---|
| ACCEPTED | LR-1, LR-3; sparse/clone/archive/case-insensitive durability; member protection under autocrlf/text=auto/text-eol; foreign/crash journal inert; VR-2, VR-4, RR-1, RR-3, TB-1′, VR-B1′; the two AR-0017 admission-reference items (fail-safe / A3-bounded) |
| ACCEPTED at design level (spec-only) | VR-1, VR-3, C-2 |
| ACCEPTED WITH CONDITION (carried) | LR-2 (RV6-C-M2, RV6-C-M3); LR-4 and RR-2 tx part (RV6-C-M3); AD-2 (RV6-C-M5); remedies-never-clear (RV6-C-M4); crash in any phase (RV6-C-M2); `.gitattributes` override (RV6-C-L1); out-of-project ignore sources (RV6-C-M1); `done/` scan (RV6-C-L2); overlay litter (RV6-C-L4); binary rollback (RV6-C-L6) |
| NOT ACCEPTED (blocking) | none |
