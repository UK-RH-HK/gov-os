# OWNER-DECISION-0009 — Owner adoption of ARCH-0003 (Signed Release Root v1)

| Field | Value |
|---|---|
| Record | OWNER-DECISION-0009 |
| Date | 2026-09-18 |
| Classification | binding owner approval/adoption of an already independently accepted architecture |
| Architecture | `spec/architecture/ARCH-0003.yaml` — Signed Release Root v1 |
| Accepted body SHA-256 | `093cb78ef097413665bd34f468b2e7e0f5d9f20b0e9b532dcef517fd8f71536a` (unchanged by this record) |
| Not | a technical verdict; an R2 release certification; an R3 platform qualification; a release, publication or merge to `main`; the start of Phase 2 |

> Naming note: `OWNER-DECISION-*` records and `D-*` decision records are separate namespaces. This record is not
> `D-0009`, which is the owner direction that created the ARCH-0003 lineage.

## Decision

The product owner explicitly **adopts ARCH-0003**.

## What this records, and what it does not

**Records:** owner approval. `ARCH-0003` moves from `PROVISIONAL` / `in_effect: false` / `human_approved: false` to
`ACTIVE` / `in_effect: true` / `human_approved: true`, `approval_state: OWNER_ADOPTED`, following the repository's
existing conventions for an active, human-approved record (as used by `ARCH-0001` and `D-0009`).

**Does not record a new technical judgement.** The independent technical acceptance remains exactly what it was:

| Gate | Token | Independent run | Evidence |
|---|---|---|---|
| R0 architecture | `ROT_ARCHITECTURE_ACCEPTED_R0` | AR-0025 | `release/root-of-trust/signed-release-root-v1-review-r0-2/` |
| R1 implementation | `ROT_PHASE1_CANDIDATE_ACCEPTED_R1` | AR-0033 | `release/verification/4.1.6-r1-4/` |

The R1-accepted implementation is `srr1-r1-candidate-4` at `c7d3fefa12f7e5813d3c3d9d9d229b5993b7c112`, tag
`srr1-r1-accepted`. Neither the candidate, the tag, nor any R0/R1 verifier evidence is moved or rewritten by this record.

## Technical content preserved

The ARCH-0003 architecture `body` and `summary` are **byte-identical** before and after adoption (body SHA-256
`093cb78e…`, verified by digest). `r0_acceptance`, `corrections`, `governed_by`, `depends_on` and `affects` are unchanged.
Only adoption metadata changed: `status`, `proposal_state`, `approval_state`, `human_approved`, `approved_by`,
`approved_at`, `in_effect`, `updated`, `tags`, the stale `correction_state`, and the `title`'s now-false
"PROVISIONAL R0 CANDIDATE" prefix; plus an `owner_adoption` block citing this record.

## Scope of `in_effect: true`

ARCH-0003 is in effect as the **adopted release-authentication architecture** of the Governance OS repository,
implemented by the R1-accepted candidate. It does **not** certify any release (R2), qualify any platform (R3),
publish anything, or merge to `main`. Those remain separate, unopened gates.

## What this adoption deliberately does not change

- **D-0007 remains ACTIVE and unchanged.** ARCH-0003 §11 states that D-0007 "remains ACTIVE through R0 and
  transition", and the accepted transition map states that D-0007 "cannot be superseded or amended merely because R0 is
  accepted" and that "a later explicit transition record must identify which wording, if any, changes after the R1
  implementation is independently accepted". **That transition record was not requested here and remains open.** All
  D-0007 rules survive unaltered.
- **ARCH-0001 remains ACTIVE** as the overall Governance OS implementation architecture. ARCH-0003 `affects` it and does
  not replace it.
- **D-0008 and ARCH-0002** remain non-active historical CP-1 research, unchanged.
- The frozen R0/R1/R2/R3 acceptance boundary, Contract v3, and every prior owner record are unchanged.
