# 03 — Residual determinations

Each residual the architect declares in the compatibility/transaction area is judged against the review-r2/r3 criteria: a
residual is **ACCEPTED** iff **(1)** its trigger needs a capability the model excludes, **or (2)** it is unavoidable
under the chosen assumptions **and** its bound is stated exactly **and** no verdict surface overstates it **and** no
reasonable design removes it. Determinations: **ACCEPTED**, **ACCEPTED WITH CONDITION** (naming the carried requirement),
**NOT ACCEPTED** (naming the finding).

## Legacy-binary containment (`26` §8)

| ID | Residual (pack) | Determination |
|---|---|---|
| LR-1 | Legacy binary on a working copy not yet on the RoT-1 commit, incl. after `git revert`, operates a legacy layout. | **ACCEPTED.** `git revert` and checkout-across-migration leave a pure legacy tree with no `governance/trust`; RoT-1 is read-only `LEGACY` on it (`durability.json` §11, §8; `legacy_regain.json` C). Bound stated correctly. |
| LR-2 (restated, RV3-M6) | Occupation removed, or pre-migration paths restored by Git → legacy regains a `verified` install, serves post-migration material, can write `governance/trust/**`; RoT-1 fails closed; strength loss reported where recorded. | **ACCEPTED (bound holds).** Reproduced on the revision-4 layout: full removal + `init --force`, `git checkout <pre> -- governance`, and `git restore --source <pre> -- governance` each reach the documented legacy outcome, and a legacy CIT then mutates `governance/trust`. RoT-1 is `PARTIAL(occupation)` or `LEGACY` in every case (`legacy_regain.json` A/B/C/E). The `26` §8 statement is exact. **Not the source of RV4-C-H1** — H1 is the *intact-layout* subtree-write vector, which LR-2 does not cover. |
| LR-3 | Explicit operator output paths of producer commands. | ACCEPTED (RoT-1-only commands; not exercised). |
| LR-4 | Fresh clones accept the repository overlay as current project configuration. | ACCEPTED as A2/T4 authority; per-machine detection after a record. (Trust-security depth is reviewer B's scope.) |

## Transaction / recovery (`18` §11, `20` §10)

| ID | Residual (pack) | Determination |
|---|---|---|
| VR-1 | A3 modifies installed files between units of work; the next unit detects it (VU-11). | **ACCEPTED at design level** (spec-only; RT-86). Not executable pre-implementation. |
| VR-2 | A3 ignores advisory locks → refusals only. | ACCEPTED (spec). |
| VR-3 | Non-`gov` subprocesses / confined children write PPS, overlay, records, VTS. | **ACCEPTED at design level for the transaction scope** (PPS detected next unit of work; journals honoured only if VTS-registered; records never authorise trust). **Caveat:** VR-3 speaks of *processes other than `gov`*; RV4-C-H1 shows a **`gov` (legacy) process** itself writing the PPS undetected while RoT-1 is `COMPLETE`, which VR-3 does not cover. |
| VR-4 | Plugin runtimes/model files consumed by path. | ACCEPTED (scope of `10`). |
| RR-1 | Automatic rollback may leave an ineligible install; fails closed; remedy = complete an update. | ACCEPTED (fail-closed). |
| RR-2 | A2-delivered older eligible release accepted as installed content on a machine without a record. | **Transaction part ACCEPTED** (union record, no dropped statements, `18` §5.2). Freshness/eligibility depth is reviewer B's scope. Spec-only. |
| RR-3 | A3 deletes the per-project record / VTS. | ACCEPTED (`UNANCHORED`, fail closed). |

## Verify-and-use (`18` §11)

| ID | Determination |
|---|---|
| VU-10 “writes under the PPS happen only inside the install transaction” | **NOT ACCEPTED as an invariant that holds against pre-RoT binaries** → RV4-C-H1: a legacy `init`/`adopt baseline`/`migrate baseline` from inside `governance/trust/` writes the PPS, and `18` §9 still reports `COMPLETE`. The invariant governs the RoT-1 runtime's own writes only; the occupation was supposed to extend it to pre-RoT binaries, and does not, inside the tree. |

## Layout durability (new observations, not pack residuals)

| Observation | Determination |
|---|---|
| The occupation is spread across **three** tree roots (`governance/`, `spec/audits/`, `.governance-runtime/`). A cone-mode `sparse-checkout set governance` materialises only `governance/`, dropping `spec/audits/GOVERNANCE-ADOPTION` and `.governance-runtime/migration` → `PARTIAL`. | **ACCEPTED (fail-closed).** Bounded: RoT-1 refuses; a legacy binary still meets the `framework.lock` directory and is `NOT_INSTALLED`. Worth a doctor note, not a finding (`durability.json` §6, §7). |
| A symlinked occupation entry is caught by the `18` §9 `st_mode` type check → `PARTIAL`. | ACCEPTED (confirms C-4). |

## Summary

| Determination | Items |
|---|---|
| ACCEPTED | LR-1, LR-3, LR-4, VR-2, VR-4, RR-1, RR-3, sparse/ symlink observations |
| ACCEPTED at design level (spec-only) | VR-1, VR-3 (with caveat), RR-2 (tx part), VU-11/journal/cross-device (`04`) |
| ACCEPTED — bound holds | LR-2 / RV3-M6 |
| NOT ACCEPTED | VU-10 as a pre-RoT invariant → **RV4-C-H1** |
