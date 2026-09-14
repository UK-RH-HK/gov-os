# Phase 1 ledger (append-only)

Each entry records:
- iteration;
- role;
- input commit;
- work performed;
- report and evidence path;
- verdict;
- output commit;
- findings;
- next action.

Entries are never edited after they are written. Corrections are made by a later entry.

---

## L-0000 — pre-Phase-1 history (context, not orchestrated)

| Field | Value |
|---|---|
| Iteration | RoT-1 revisions 1–2 |
| Role | architect (rev 1, rev 2); fresh independent reviewer (review 1, review 2) |
| Input commit | `da9c851` (4.1.5, rejected: `c8a138f`) |
| Work performed | Rev 1 committed `676dfce` and rejected by `1c6027c`. Rev 2 committed `d37b05c` and rejected by `e5a6b8a`. |
| Report / evidence | `release/root-of-trust/4.1.6-review/`, `release/root-of-trust/4.1.6-review-r2/` |
| Verdict | `ROOT_OF_TRUST_ARCHITECTURE_REJECTED` (both) |
| Output commit | `e5a6b8a` |
| Findings | Rev 2: HIGH R2-H1…H4, MEDIUM R2-M1…M10, LOW R2-L1…L3 |
| Next action | Phase 1 orchestration begins with revision 3 |

## L-0001 — 2026-09-14 — orchestration initialised

| Field | Value |
|---|---|
| Iteration | architecture revision 3, Phase-1 review cycle 1 |
| Role | orchestrator |
| Input commit | `e5a6b8a` on `release/4.1.5-rc1`, clean working tree |
| Work performed | Created integration branch `release/4.1.6-rc1` at `e5a6b8a`. Created this control record. Archived legacy `gov` 4.1.2 and 4.1.5 and built 4.1.3 and 4.1.4 in session scratch for the pre-RoT matrix. Wrote HO-0001. |
| Report / evidence | `ORCHESTRATOR_STATE.yaml`, `GATES/GATE-REGISTER.yaml`, `HANDOFFS/HO-0001-rot-architect-r3.md`, `CHECKPOINTS/CP-0001.yaml` |
| Verdict | — (routing only) |
| Output commit | the commit adding this directory |
| Findings | none new; R2 findings carried as unresolved |
| Next action | spawn fresh RoT architect AR-0001 |

## L-0002 — 2026-09-14 — revision-3 architect spawned

| Field | Value |
|---|---|
| Iteration | architecture revision 3, Phase-1 review cycle 1 |
| Role | rot-architect (`AR-0001`, fresh Opus 5 context) |
| Input commit | `71581dc` (worktree `wt/arch-r3`, branch `phase1/rot1-r3-architect`) |
| Work performed | spawned on HO-0001; running |
| Report / evidence | expected `AGENT_RUNS/AR-0001.report.yaml`; pack `release/root-of-trust/4.1.6/` |
| Verdict | pending |
| Output commit | pending |
| Findings | — |
| Next action | on completion: verify report, merge, spawn reviewers B and C in parallel |

## L-0003 — 2026-09-14 — revision 3 authored

| Field | Value |
|---|---|
| Iteration | architecture revision 3, Phase-1 review cycle 1 |
| Role | rot-architect (`AR-0001`) |
| Input commit | `71581dc` |
| Work performed | Pack `release/root-of-trust/4.1.6/` rewritten (00–22) plus new 23 constitutional surface, 24 freshness anchoring and machine bootstrap, 25 binary and trust-base authenticity, 26 legacy-binary containment, 27 trust-decision authorisation. Machine-readable constitutional surface inventory and checker. Schemas revised or added. D-0008 and ARCH-0002 PROPOSED revision 3. OP-7 added; OP-2, OP-3 and OP-4 restated. |
| Report / evidence | `AGENT_RUNS/AR-0001.report.yaml`; `release/root-of-trust/4.1.6/evidence/` (CSI checks, P1r3, P3r3, P4r3, G1) |
| Verdict | `ARCHITECTURE_REVISION_READY_FOR_REVIEW` (author's readiness claim; not an acceptance) |
| Output commit | work `ca77a43`, report `b795a6b`, merged into `release/4.1.6-rc1` as `5f6a83b` |
| Findings | Architect-reported (claims, to be independently tested): coverage checker passes on framework/ and 4.1.5 payload, 26/26 self-test; P1r3 three harms flipped; P3r3 695 invocations and 40 chains over real 4.1.2–4.1.5 with 0 tracked-byte changes; P4r3 34/34. INFO AR1-F1 (V3 layout alone insufficient; adoption and migration occupations added), AR1-F2 (ROLES role ids registered), AR1-F3 (mechanisms that are specification-only until implementation). |
| Next action | independent review panel B and C |

## L-0004 — 2026-09-14 — review panel handed off

| Field | Value |
|---|---|
| Iteration | architecture revision 3, Phase-1 review cycle 1 |
| Role | orchestrator |
| Input commit | `5f6a83b` |
| Work performed | Wrote HO-0002 (reviewer B, trust and security) and HO-0003 (reviewer C, compatibility and transactions). Claimed AR-0002 and AR-0003. Created separate worktrees and branches. |
| Report / evidence | `HANDOFFS/HO-0002-*.md`, `HANDOFFS/HO-0003-*.md`, `CHECKPOINTS/CP-0002.yaml` |
| Verdict | — |
| Output commit | the commit adding these records |
| Findings | — |
| Next action | spawn AR-0002 and AR-0003 in parallel |
