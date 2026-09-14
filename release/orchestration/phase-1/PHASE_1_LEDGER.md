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

## L-0005 — 2026-09-14 — review panel spawned

| Field | Value |
|---|---|
| Iteration | architecture revision 3, Phase-1 review cycle 1 |
| Role | rot-reviewer-trust-security (`AR-0002`) and rot-reviewer-compat-transaction (`AR-0003`), fresh Opus 5 contexts, in parallel |
| Input commit | `83aa822` (worktrees `wt/review-r3-b`, `wt/review-r3-c`; branches `phase1/rot1-r3-review-b`, `phase1/rot1-r3-review-c`) |
| Work performed | spawned on HO-0002 and HO-0003; running |
| Report / evidence | expected `AGENT_RUNS/AR-0002.report.yaml`, `AGENT_RUNS/AR-0003.report.yaml`; `release/root-of-trust/4.1.6-review-r3/{B-trust-security,C-compat-transaction}/` |
| Verdict | pending |
| Output commit | pending |
| Findings | — |
| Next action | on both completions: verify, merge, write HO-0004, spawn synthesis reviewer D |

## L-0006 — 2026-09-14 — reviewer C completed

| Field | Value |
|---|---|
| Iteration | architecture revision 3, Phase-1 review cycle 1 |
| Role | rot-reviewer-compat-transaction (`AR-0003`) |
| Input commit | `83aa822` (architecture `ca77a43`) |
| Work performed | independent pre-RoT matrix over real 4.1.2–4.1.5 (84 destructive invocations on the intact layout: 0 tree, trust or Git writes); held-out RV3-C-A01…A10 (6 executed); transaction and layout-durability analysis |
| Report / evidence | `AGENT_RUNS/AR-0003.report.yaml` (on branch); `release/root-of-trust/4.1.6-review-r3/C-compat-transaction/` |
| Verdict | `NO_BLOCKING_FINDINGS` (role verdict) |
| Output commit | work `9e013c1`, report `c19fbc1` on `phase1/rot1-r3-review-c`; held unmerged until reviewer B completes |
| Findings | MEDIUM C-1 (carried): removing the occupation entries lets legacy `init --force` reproduce the R2-H4 harm; RoT-1 fails closed and `governance/trust/**` is untouched; the LR-2 bound and RT-50/RT-81 need occupation-absent assertions. Carried items C-2…C-5. Prior: R2-H4 NARROWED; R2-M7, M8, M9, L2 closed by design; R2-L3 closed. |
| Next action | await AR-0002; then merge B and C, write HO-0004, spawn synthesis reviewer D |

## L-0007 — 2026-09-14 — reviewer B completed; panel merged

| Field | Value |
|---|---|
| Iteration | architecture revision 3, Phase-1 review cycle 1 |
| Role | rot-reviewer-trust-security (`AR-0002`) |
| Input commit | `83aa822` (architecture `ca77a43`) |
| Work performed | Re-executed r2 P1, P2 and P4. Ran the architect's checker and P4r3. Authored held-out RV3-B-A01…A18 and injections I01–I09. Built a 132-row machine-class × OP-7 × adversary matrix. |
| Report / evidence | `AGENT_RUNS/AR-0002.report.yaml`; `release/root-of-trust/4.1.6-review-r3/B-trust-security/` |
| Verdict | `BLOCKING_FINDINGS_PRESENT` (role verdict) |
| Output commit | work `7d8c73a`, report `d7282e9`, merged `a945f4d`. Reviewer C's branch merged after B completed: `5741b51`. |
| Findings | HIGH RV3-B-H1 (precedence mode order lets a surface-passing kernel discard project strengthening; executed on 4.1.5); HIGH RV3-B-H2 (freshness anchoring lets attacker-selected stale state become anchored-current on CI and first-install machines); HIGH RV3-B-H3 (binary acceptance does not bind compiled source to verified source; `release_commit` chosen by threshold-1 `release-final`). MEDIUM M1–M5, LOW L1–L5, INFO I1. Prior: R2-M4 and R2-M6 closed; R2-H1, H2, H3 and others narrowed. |
| Next action | synthesis reviewer D |

## L-0008 — 2026-09-14 — synthesis handed off

| Field | Value |
|---|---|
| Iteration | architecture revision 3, Phase-1 review cycle 1 |
| Role | orchestrator |
| Input commit | `5741b51` |
| Work performed | Wrote HO-0004 for the independent synthesis reviewer (sole architecture verdict). Claimed AR-0004. Added B and C directories to immutable evidence. |
| Report / evidence | `HANDOFFS/HO-0004-rot-review-r3-d-synthesis.md`, `CHECKPOINTS/CP-0003.yaml` |
| Verdict | — |
| Output commit | the commit adding these records |
| Findings | — |
| Next action | spawn AR-0004 |

## L-0009 — 2026-09-14 — synthesis reviewer spawned

| Field | Value |
|---|---|
| Iteration | architecture revision 3, Phase-1 review cycle 1 |
| Role | rot-review-synthesis (`AR-0004`, fresh Opus 5 context) |
| Input commit | `90efd29` (worktree `wt/review-r3-d`, branch `phase1/rot1-r3-review-d`) |
| Work performed | spawned on HO-0004; running |
| Report / evidence | expected `AGENT_RUNS/AR-0004.report.yaml`; `release/root-of-trust/4.1.6-review-r3/{00,10,11}*`, `D-synthesis/` |
| Verdict | pending |
| Output commit | pending |
| Findings | — |
| Next action | on completion: verify, merge; route per verdict (revision-4 architect, or owner decision gate GATE-OWNER-D0008) |

## L-0010 — 2026-09-14 — revision 3 REJECTED by synthesis

| Field | Value |
|---|---|
| Iteration | architecture revision 3, Phase-1 review cycle 1 |
| Role | rot-review-synthesis (`AR-0004`) |
| Input commit | `90efd29` (architecture `ca77a43`; B `7d8c73a`; C `9e013c1`) |
| Work performed | Reproduced 14 panel and architect probes, all reproduced. Adjudicated B and C. Authored held-out RV3-D-A01…A18 (5 executed, 7 computed, 6 design). Determined HO-0001 §3 status and residuals. |
| Report / evidence | `AGENT_RUNS/AR-0004.report.yaml`; `release/root-of-trust/4.1.6-review-r3/{00-REVIEW-REPORT,10-BLOCKING-FINDINGS,11-CORRECTION-DELTA}.md`, `D-synthesis/` |
| Verdict | **`ROOT_OF_TRUST_ARCHITECTURE_REJECTED`** |
| Output commit | review `79a09a1`, report `d3d4154`, merged `e462748` |
| Findings | **HIGH:** RV3-H1 (precedence counts only refusals, so project strength is lost), RV3-H2 (anchor satisfied by sequence number, non-expiring pins, witness with a single threshold-1 key), RV3-H3 (built source not bound to verified source). **MEDIUM:** RV3-M1…M9. **LOW:** RV3-L1…L8. **INFO:** RV3-I1. **Classes:** BC-1…BC-4, not materially new (remainders of R2-H1…H3). **Closed as class:** R2-H4. **HO-0001:** §3.1–§3.3 NOT SATISFIED; §3.4 SATISFIED. |
| Next action | revision-4 architect on CD3-1…CD3-4 |

## L-0011 — 2026-09-14 — revision-4 architect handed off

| Field | Value |
|---|---|
| Iteration | architecture revision 4, Phase-1 review cycle 2 |
| Role | orchestrator |
| Input commit | `e462748` |
| Work performed | Wrote HO-0005 (routing to BC-1…BC-4, §6 carried items, §7 entry criteria). Claimed AR-0005. Recorded escalation counters: rejections 1, materially-new streak 0, persistent-remainder streak 1 (threshold 2 triggers the specialist-alternatives pattern). Added the review-r3 consolidated files to immutable evidence. |
| Report / evidence | `HANDOFFS/HO-0005-rot-architect-r4.md`, `CHECKPOINTS/CP-0004.yaml` |
| Verdict | — |
| Output commit | the commit adding these records |
| Findings | — |
| Next action | spawn AR-0005 |

## L-0012 — 2026-09-14 — revision-4 architect spawned

| Field | Value |
|---|---|
| Iteration | architecture revision 4, Phase-1 review cycle 2 |
| Role | rot-architect (`AR-0005`, fresh Opus 5 context) |
| Input commit | `f83da03` (worktree `wt/arch-r4`, branch `phase1/rot1-r4-architect`) |
| Work performed | spawned on HO-0005; running |
| Report / evidence | expected `AGENT_RUNS/AR-0005.report.yaml`; pack `release/root-of-trust/4.1.6/` |
| Verdict | pending |
| Output commit | pending |
| Findings | — |
| Next action | on completion: verify, merge, instantiate revision-4 B/C handoffs, spawn B and C in parallel |

## L-0013 — 2026-09-14 — revision 4 authored

| Field | Value |
|---|---|
| Iteration | architecture revision 4, Phase-1 review cycle 2 |
| Role | rot-architect (`AR-0005`) |
| Input commit | `f83da03` |
| Work performed | Pack 00–27 revised; new `28-CLASS-REMAINDER-ANALYSIS.md`. Constitutional surface floor schema v3. Schemas (2 new: freshness witness, decision pin). `examples/rev4`. 38 evidence files. D-0008 and ARCH-0002 PROPOSED revision 4. OP-2, OP-3, OP-4 and OP-7 restated. |
| Report / evidence | `AGENT_RUNS/AR-0005.report.yaml`; `release/root-of-trust/4.1.6/evidence/` |
| Verdict | `ARCHITECTURE_REVISION_READY_FOR_REVIEW` (author's readiness claim; not an acceptance) |
| Output commit | work `bca05a7`, report `9c24821`, merged `fd0a368` |
| Findings | Architect-reported claims, to be independently tested: checker self-test 56/56; P1r4 9/9 strengthening kept, lattice 0/343 unsound; P4r4 54/54 with 9/9 mutants caught, 132-row matrix 77 refused / 42 stated core / 13 OP-7 (d) residual / 0 unstated; verify-artifact source scenarios 16/16; P3r3 unchanged (2085 jobs equal); review probes re-run or rebuilt. Disclosed non-material scope deviation (read 60 lines of the completed AR-0004 report as format reference). |
| Next action | independent review panel B and C on revision 4 |

## L-0014 — 2026-09-14 — revision-4 review panel handed off

| Field | Value |
|---|---|
| Iteration | architecture revision 4, Phase-1 review cycle 2 |
| Role | orchestrator |
| Input commit | `fd0a368` |
| Work performed | Wrote HO-0006 (B) and HO-0007 (C) from the generic reviewer templates (prior review r3 `79a09a1`). Claimed AR-0006 and AR-0007. Created separate worktrees and branches. |
| Report / evidence | `HANDOFFS/HO-0006-*.md`, `HANDOFFS/HO-0007-*.md`, `CHECKPOINTS/CP-0005.yaml` |
| Verdict | — |
| Output commit | the commit adding these records |
| Findings | — |
| Next action | spawn AR-0006 and AR-0007 in parallel |

## L-0015 — 2026-09-14 — revision-4 review panel spawned

| Field | Value |
|---|---|
| Iteration | architecture revision 4, Phase-1 review cycle 2 |
| Role | rot-reviewer-trust-security (`AR-0006`) and rot-reviewer-compat-transaction (`AR-0007`), fresh Opus 5 contexts, in parallel |
| Input commit | `7a23900` (worktrees `wt/review-r4-b`, `wt/review-r4-c`; branches `phase1/rot1-r4-review-b`, `phase1/rot1-r4-review-c`) |
| Work performed | spawned on HO-0006 and HO-0007; running. Prompts restrict orchestration reads to the reviewer's own handoff, HO-0001 and `AGENT_RUNS/README.md`, and require disclosure of any out-of-scope read. |
| Report / evidence | expected `AGENT_RUNS/AR-0006.report.yaml`, `AGENT_RUNS/AR-0007.report.yaml`; `release/root-of-trust/4.1.6-review-r4/{B-trust-security,C-compat-transaction}/` |
| Verdict | pending |
| Output commit | pending |
| Findings | — |
| Next action | hold the first completed branch unmerged; on both completions verify, merge, write the synthesis HO, spawn D |

## L-0016 — 2026-09-14 — revision-4 reviewer C completed

| Field | Value |
|---|---|
| Iteration | architecture revision 4, Phase-1 review cycle 2 |
| Role | rot-reviewer-compat-transaction (`AR-0007`) |
| Input commit | `7a23900` (architecture `bca05a7`) |
| Work performed | Derived registers independently (104/109/115/119 leaves). Ran 10,618 invocations and 168 chains on real 4.1.2–4.1.5. Authored held-out RV4-C-A01…A10 (7 executed, 3 design). |
| Report / evidence | `AGENT_RUNS/AR-0007.report.yaml` (on branch); `release/root-of-trust/4.1.6-review-r4/C-compat-transaction/` |
| Verdict | `BLOCKING_FINDINGS_PRESENT` (role verdict) |
| Output commit | work `c6b8ba9`, report `0b5320b` on `phase1/rot1-r4-review-c`; held unmerged until reviewer B completes |
| Findings | **HIGH RV4-C-H1:** the occupation protects only the project root. Pre-RoT `init`, `adopt baseline` and `migrate baseline` run from a subdirectory without `--root` write inside `governance/trust/**`, and the RoT-1 state machine still computes `COMPLETE`. 336 subdirectory rows wrote, 56 of them into trust paths; rooted invocations: 2,504 rows, 0 writes. **MEDIUM RV4-C-M1 (carried):** a retained legacy `.gitignore` line lets the untrack idiom drop the migration occupation. **Prior findings:** R2-H4 NOT CLOSED as a class (narrowed); RV3-M6 open residual with correct bound; RV3-L7 narrowed; C-1 addressed; C-2…C-5 carried and specification-only. No scope deviation. |
| Next action | await AR-0006; then merge B and C, write the synthesis HO, spawn D |
