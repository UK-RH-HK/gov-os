# 03 — Residual determinations

Each residual the architect declares in the compatibility/transaction area is judged against explicit criteria (review
r2/r3/r4 lineage): a residual is **ACCEPTED** iff **(1)** its trigger needs a capability the model excludes, **or (2)**
it is unavoidable under the chosen assumptions **and** its bound is stated exactly **and** no verdict surface overstates
it **and** no reasonable design removes it. **ACCEPTED WITH CONDITION** names the carried requirement; **NOT ACCEPTED**
names the finding. Determinations are made against revision 5 as written.

## Legacy-binary containment (`26` §8)

| ID | Residual (pack) | Determination |
|---|---|---|
| LR-1 | Legacy binaries on a working copy not on the RoT-1 layout commit (incl. after `git revert`) operate a legacy layout. | **ACCEPTED** (R-2). CHECKOUT_PRE and RESTORE_PRE_GOV are `LEGACY`; a RoT-1 binary is read-only on them (`gitops.json`). Bound stated. |
| LR-2 (restated, RV3-M6) | Occupation removed, or pre-migration paths restored by Git → legacy regains a `verified` install, serves post-migration material, writes `governance/trust/**`; RoT-1 fails closed; strength loss reported where recorded. | **ACCEPTED (bound holds).** `legacy_regain` reproduced byte-identical; every resulting tree is `PARTIAL(occupation)`/`LEGACY`/`KERNEL_TAMPERED`. The revision-5 §9.1 closed entry sets additionally make the **intact-layout subdirectory trigger** fail closed (the RV4-M1 residual is closed): a subtree write can no longer leave `COMPLETE`. |
| LR-3 | Explicit operator output paths; nested installs outside `governance/`. | **ACCEPTED** (R-2). Nested installs in `product/`, `vendor/` and the transaction area are reported (`NESTED_LEGACY_PROJECT`/D039), state unchanged; contained (RV5-C-A13). |
| LR-4 | Fresh clones accept the repository overlay as current project configuration. | **ACCEPTED** as A2/T4 authority; per-machine detection after a record (reviewer B's freshness scope). Overlay litter from a subtree legacy adopt is within this bound. |

## Layout durability (new determinations)

| Observation | Determination |
|---|---|
| The occupation spans three tree roots (`governance/`, `spec/audits/`, `.governance-runtime/`); cone/non-cone sparse checkout drops entries → `PARTIAL(occupation)`. | **ACCEPTED (fail closed).** Worth a doctor note (C-6). |
| A `core.autocrlf=true` / `* text=auto` Windows checkout corrupts the kernel bytes → `KERNEL_TAMPERED`/`PARTIAL`. | **NOT ACCEPTED as a silent-valid state, but fail closed → carried RV5-C-M1.** The layout ships no `.gitattributes`; the pack does not address line endings. Availability/portability defect, not a trust bypass. |
| The `.gitignore` surgery closes the untracking idiom only for the project `.gitignore`; a global `core.excludesFile` / `.git/info/exclude` carrying `.governance-runtime/` re-drops the occupation. | **carried RV5-C-M2** (fail closed; the surgery cannot reach out-of-project ignore sources). |
| Clean/shallow/partial clone, `git archive`, `clean -fdx`, `stash -u`, `worktree add`, checkout-across-migration-and-back preserve the occupation and types → `COMPLETE`. | **ACCEPTED** (`gitops.json`). |

## Transaction / recovery (`18` §11, `20` §10) — spec-only, unimplemented

| ID | Residual (pack) | Determination |
|---|---|---|
| VR-1 | A3 modifies installed files between units of work; the next unit detects it (VU-11). | **ACCEPTED at design level** (RT-86). Not executable pre-implementation. |
| VR-2 | A3 ignores advisory locks → refusals only. | ACCEPTED (spec). |
| VR-3 | Non-`gov`/confined children write PPS, overlay, records, VTS. | **ACCEPTED at design level.** PPS detected next unit of work; journals honoured only if VTS-registered (`18` §5.1) — this gate is what makes the transaction-area litter of RV5-C-L2 inert. |
| VR-4 | Plugin runtimes/model files consumed by path. | ACCEPTED (`10` scope). |
| RR-1 | Automatic rollback may leave an ineligible install; fails closed. | ACCEPTED (fail closed). |
| RR-2 | A2-delivered older eligible release on a machine without a record; `kernel reinstall` uses the lock identity. | **Transaction part ACCEPTED** (union record, no dropped statements, `18` §5.2; registration-scoped E7 at use, `20` §9 revision-5). Freshness/eligibility depth is reviewer B's scope. Spec-only. |
| RR-3 | A3 deletes the per-project record / VTS. | ACCEPTED (`UNANCHORED`, fail closed). |
| C-2 | Cross-device transaction area refusal before any write; unanchored `PARTIAL` repairable by same-digest reinstall. | **ACCEPTED at design level** (`18` §3, `20` §8). Not executable pre-implementation → `04`. |

## Verify-and-use (`18` §11)

| ID | Determination |
|---|---|
| VU-10 "writes under the PPS happen only inside the install transaction" (against pre-RoT binaries) | **ACCEPTED for `governance/trust/**` and the occupation** — the revision-5 closed entry sets (`18` §9.1) make every pre-RoT write there leave a non-`COMPLETE` state (matrix5 `R2-H4`, 0 violations). **NARROWED for `.governance-runtime/trust-tx/**`** (RV5-C-L2): a pre-RoT write there leaves `COMPLETE` (reported, inert). |

## Independent admission (`31` §9) — model-level

| ID | Residual (pack) | Determination |
|---|---|---|
| TB-1′ | A malicious binary run directly, outside admission | ACCEPTED (GB rules bind genuine binaries; the procedure never runs a candidate — `admit_tx` A08 confirms C0-only without a record). |
| AD-2 | Same-account code executed before the first admission | ACCEPTED as intended **only once first-admission is defined** — the fresh-store step (R-ADM-8) that provides AD-2's bound is the same mechanism that, undefined, discards monotonic state on a re-run (RV5-C-L3). Carried. |
| VR-B1 | Same-account replacement of a user-writable binary is A3; such an install is C0–C2 only (GB-4). | ACCEPTED (`admit_tx` INS2 analogue: a user-owned location is `location_protected: false`, C3 refused). |

## Summary

| Determination | Items |
|---|---|
| ACCEPTED | LR-1, LR-2 (bound holds; RV4-M1 intact-layout trigger now closed), LR-3, LR-4, sparse/clone/archive durability, VR-2, VR-4, RR-1, RR-3, TB-1′, VR-B1 |
| ACCEPTED at design level (spec-only) | VR-1, VR-3, RR-2 (tx part), C-2 |
| ACCEPTED WITH CONDITION | VU-10 as a pre-RoT invariant (→ RV5-C-L2 for the transaction area); AD-2 (→ RV5-C-L3) |
| NOT ACCEPTED (carried, fail closed) | Windows/EOL durability (→ RV5-C-M1); out-of-project untracking idiom (→ RV5-C-M2) |
