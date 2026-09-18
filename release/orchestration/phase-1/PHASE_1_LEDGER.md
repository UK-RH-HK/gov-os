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

## L-0017 — 2026-09-14 — revision-4 reviewer B completed; panel merged

| Field | Value |
|---|---|
| Iteration | architecture revision 4, Phase-1 review cycle 2 |
| Role | rot-reviewer-trust-security (`AR-0006`) |
| Input commit | `7a23900` (architecture `bca05a7`) |
| Work performed | Reproduced the architect's checker, P4r4, VA4 and P1r4 byte-identical. Re-ran review r3 probes. Built an independent 336-row machine × OP-7 × adversary matrix. Authored held-out RV4-B-A01…A17 (5 executed, 8 computed, 4 design). |
| Report / evidence | `AGENT_RUNS/AR-0006.report.yaml`; `release/root-of-trust/4.1.6-review-r4/B-trust-security/` |
| Verdict | `BLOCKING_FINDINGS_PRESENT` (role verdict) |
| Output commit | work `152e68e`, report `d18cbcc`, merged `5583571`. Reviewer C's branch merged after B completed: `5c20d23`. |
| Findings | **HIGH RV4-B-H1:** one build-attestation key plus pipeline control yields an accepted malicious production binary, because downstream signers never rebuild; also via one verification-attestation key when a REJECTED verdict does not reach the publisher. **HIGH RV4-B-H2:** the first binary on a machine bypasses revocation, anchor and currency checks, and build-from-source compares a self-reported digest. **HIGH RV4-B-H3:** per-leaf content registration lets one `release-final` key ship a newer release carrying old registered content; a secret was indexed on 4.1.5. **MEDIUM:** M1–M4. **LOW:** L1–L7. **INFO:** I1. **Prior status:** BC-1 closed (but §3.1 open via H3); BC-2 narrowed (H2); BC-3 open (H1); BC-4 open. No scope deviation. |
| Next action | synthesis reviewer D |

## L-0018 — 2026-09-14 — revision-4 synthesis handed off

| Field | Value |
|---|---|
| Iteration | architecture revision 4, Phase-1 review cycle 2 |
| Role | orchestrator |
| Input commit | `5c20d23` |
| Work performed | Wrote HO-0008 for the independent synthesis reviewer (sole architecture verdict). Claimed AR-0008. Added the review-r4 B and C directories to immutable evidence. |
| Report / evidence | `HANDOFFS/HO-0008-rot-review-r4-d-synthesis.md`, `CHECKPOINTS/CP-0006.yaml` |
| Verdict | — |
| Output commit | the commit adding these records |
| Findings | — |
| Next action | spawn AR-0008 |

## L-0019 — 2026-09-14 — revision-4 synthesis reviewer spawned

| Field | Value |
|---|---|
| Iteration | architecture revision 4, Phase-1 review cycle 2 |
| Role | rot-review-synthesis (`AR-0008`, fresh Opus 5 context) |
| Input commit | `9349d8c` (worktree `wt/review-r4-d`, branch `phase1/rot1-r4-review-d`) |
| Work performed | spawned on HO-0008; running. Asked to classify each confirmed blocking class as a narrowed remainder or materially new, naming the root invariant, so the escalation rule can be applied. |
| Report / evidence | expected `AGENT_RUNS/AR-0008.report.yaml`; `release/root-of-trust/4.1.6-review-r4/{00,10,11}*`, `D-synthesis/` |
| Verdict | pending |
| Output commit | pending |
| Findings | — |
| Next action | on completion: verify, merge; route per verdict and novelty (specialist escalation, revision-5 architect, or GATE-OWNER-D0008) |

## L-0020 — 2026-09-14 — revision 4 REJECTED by synthesis

| Field | Value |
|---|---|
| Iteration | architecture revision 4, Phase-1 review cycle 2 |
| Role | rot-review-synthesis (`AR-0008`) |
| Input commit | `9349d8c` (architecture `bca05a7`; B `152e68e`; C `c6b8ba9`) |
| Work performed | Reproduced every architect and panel probe, including C's full 10,618-invocation matrix. Adjudicated B and C. Authored held-out RV4-D-A01…A10 (2 executed, 2 computed, 6 design). Classified each blocking class as a narrowed remainder or materially new. |
| Report / evidence | `AGENT_RUNS/AR-0008.report.yaml`; `release/root-of-trust/4.1.6-review-r4/{00-REVIEW-REPORT,10-BLOCKING-FINDINGS,11-CORRECTION-DELTA}.md`, `D-synthesis/` |
| Verdict | **`ROOT_OF_TRUST_ARCHITECTURE_REJECTED`** |
| Output commit | review `97a5545`, report `49ba96b`, merged `15f0a06` |
| Findings | **HIGH RV4-H1:** threshold-1 build-attestation or verification-attestation key plus pipeline control; a root co-signature does not stop it. **HIGH RV4-H2:** first-binary acceptance is not anchored and compares self-reported values; ceremonies and Phase 4 migration run on the unaccepted binary. **HIGH RV4-H3:** content registration is not release-scoped. **MEDIUM:** RV4-M1…M7 (RV4-C-H1 re-rated to MEDIUM as RV4-M1; C's "R2-H4 not closed" claim refuted as stated). **LOW:** L1–L10. **INFO:** I1. **Classes:** BC4-1…BC4-4, all narrowed remainders, none materially new. **HO-0001:** §3.1–§3.3 NOT SATISFIED; §3.4 SATISFIED with carried items. |
| Next action | persistent-remainder escalation |

## L-0021 — 2026-09-14 — escalation: specialist alternatives before revision 5

| Field | Value |
|---|---|
| Iteration | architecture revision 5 (escalation), Phase-1 review cycle 3 |
| Role | orchestrator |
| Input commit | `15f0a06` |
| Work performed | Persistent-remainder streak reached 2, the threshold recorded in CP-0004 before revision 4's outcome. Applied the protocol §5 escalation pattern: HO-0009 (specialist A, lens: verifier's minimal trusted inputs) and HO-0010 (specialist B, lens: release, build and custody supply chain), both covering all classes and every HO-0001 §3 requirement. Claimed AR-0009 and AR-0010. Added review-r4 consolidated files to immutable evidence. Added a standing prohibition on writing held-out or in-progress material into the auto-memory, whose index is visible to subagents (disclosed by AR-0008). |
| Report / evidence | `HANDOFFS/HO-0009-*.md`, `HANDOFFS/HO-0010-*.md`, `CHECKPOINTS/CP-0007.yaml` |
| Verdict | — |
| Output commit | the commit adding these records |
| Findings | — |
| Next action | spawn AR-0009 and AR-0010 in parallel |

## L-0022 — 2026-09-14 — specialist architects spawned

| Field | Value |
|---|---|
| Iteration | architecture revision 5 (escalation), Phase-1 review cycle 3 |
| Role | rot-specialist-architect `AR-0009` (lens A: verifier's minimal trusted inputs) and `AR-0010` (lens B: release, build and custody supply chain), fresh Opus 5 contexts, in parallel |
| Input commit | `6ea45a5` (worktrees `wt/spec-r5-a`, `wt/spec-r5-b`; branches `phase1/rot1-r5-specialist-a`, `phase1/rot1-r5-specialist-b`) |
| Work performed | spawned on HO-0009 and HO-0010; running |
| Report / evidence | expected `AGENT_RUNS/AR-0009.report.yaml`, `AGENT_RUNS/AR-0010.report.yaml`; `release/root-of-trust/4.1.6-alternatives-r5/specialist-{a,b}/` |
| Verdict | pending |
| Output commit | pending |
| Findings | — |
| Next action | hold the first completed branch unmerged; on both completions verify, merge, write HO-0011, spawn synthesis architect AR-0011 |

## L-0023 — 2026-09-14 — specialist B completed

| Field | Value |
|---|---|
| Iteration | architecture revision 5 (escalation), Phase-1 review cycle 3 |
| Role | rot-specialist-architect (`AR-0010`, lens B: release, build and custody supply chain) |
| Input commit | `6ea45a5` (latest rejected revision `bca05a7`; review r4 `97a5545`) |
| Work performed | Root-cause analysis across revisions 1–4; alternative mechanism; falsification (12 r4 blocking probes, 11 r3 blocking probes, 25 new attacks: 10 executed, 10 computed, 5 design); owner choices |
| Report / evidence | `AGENT_RUNS/AR-0010.report.yaml` (on branch); `release/root-of-trust/4.1.6-alternatives-r5/specialist-b/` |
| Verdict | `ALTERNATIVE_PROPOSED` (proposal; not reviewed) |
| Output commit | work `ed07926`, report `d984181` on `phase1/rot1-r5-specialist-b`; held unmerged until specialist A completes |
| Findings | Specialist's claims, not adjudicated. **Common root:** trust judged per input, not per fact (pass-through, selection from a permitted set, evaluator inside the object). **Proposal:** first-hand-fact acceptance predicate with two-verification source legitimacy and a rebuilder quorum q ≥ 2, retiring `release-artifact`; a separate admitter `gov-admit` for first TCB acceptance over measured bytes; single value per release sequence for registrations; an attack-set calculator generating the owner-option consequence table. **Falsification:** r4 blocking probes 9 flipped, 1 flipped with residual, 1 holds, 1 not run; r3 11/11 hold; 32/32 owner configurations need ≥ 2 first-hand establishers. **Owner choices:** OC-1…OC-5. **Costs:** rebuilders, second verifier, admitter maintenance, possible per-release root ceremony. |
| Next action | await AR-0009; then merge both, write HO-0011, spawn synthesis architect AR-0011 |

## L-0024 — 2026-09-14 — specialist A completed; specialists merged

| Field | Value |
|---|---|
| Iteration | architecture revision 5 (escalation), Phase-1 review cycle 3 |
| Role | rot-specialist-architect (`AR-0009`, lens A: verifier's minimal trusted inputs) |
| Input commit | `6ea45a5` |
| Work performed | Root-cause analysis with a selector audit over 43 decision rows across revisions 1–4. Alternative mechanism. Falsification of 54 items: 15 r4 blocking probes, 9 r3 blocking probes, 30 new attacks. Owner choices. |
| Report / evidence | `AGENT_RUNS/AR-0009.report.yaml`; `release/root-of-trust/4.1.6-alternatives-r5/specialist-a/` |
| Verdict | `ALTERNATIVE_PROPOSED` (proposal; not reviewed) |
| Output commit | work `afda663`, report `89c6736`, merged `1c46100`. Specialist B merged after A completed: `fd2eac4`. |
| Findings | Specialist's claims, not adjudicated. **Root:** SEL-1 — the selector of a fact must hold at least the authority and currency the fact confers; flags all 18 HIGH rows and none of 12 confirmed-sound mechanisms. **Proposal:** per-release source and input registration by root or a delegated quorum ≥ 2; quorum ≥ 2 first-person reproductions submitted outside the pipeline; an independent first-acceptance executor (Python plus OpenSSL) over one typed state fingerprint, never running the candidate; exact per-release registration of non-join units. **Falsification:** 37 refuted, 14 confirmed as stated residuals, 2 pass, 1 not run. **Owner choices:** OC-1…OC-8. **Scope deviations (non-material):** a temporary file moved from the scratch root; other handoff and scratch names seen in listings, not opened. |
| Next action | synthesis architect writes revision 5 |

## L-0025 — 2026-09-14 — synthesis architect handed off

| Field | Value |
|---|---|
| Iteration | architecture revision 5 (escalation), Phase-1 review cycle 3 |
| Role | orchestrator |
| Input commit | `fd2eac4` |
| Work performed | Wrote HO-0011 for a fresh synthesis architect: compare A and B, author revision 5 as architect of record, apply review r4 §6 and §7, reconcile owner options into one set without deciding. Claimed AR-0011. Added both specialist directories to immutable evidence. |
| Report / evidence | `HANDOFFS/HO-0011-rot-synthesis-architect-r5.md`, `CHECKPOINTS/CP-0008.yaml` |
| Verdict | — |
| Output commit | the commit adding these records |
| Findings | — |
| Next action | spawn AR-0011 |

## L-0026 — 2026-09-14 — revision-5 synthesis architect spawned

| Field | Value |
|---|---|
| Iteration | architecture revision 5 (escalation), Phase-1 review cycle 3 |
| Role | rot-synthesis-architect (`AR-0011`, fresh Opus 5 context) |
| Input commit | `c8cdfac` (worktree `wt/arch-r5`, branch `phase1/rot1-r5-synthesis-architect`) |
| Work performed | spawned on HO-0011; running |
| Report / evidence | expected `AGENT_RUNS/AR-0011.report.yaml`; `release/root-of-trust/4.1.6-alternatives-r5/SYNTHESIS.md`; pack `release/root-of-trust/4.1.6/` |
| Verdict | pending |
| Output commit | pending |
| Findings | — |
| Next action | on completion: verify, merge, instantiate revision-5 B/C handoffs, spawn B and C in parallel |

## L-0027 — 2026-09-14 — revision 5 authored (escalation synthesis)

| Field | Value |
|---|---|
| Iteration | architecture revision 5 (escalation), Phase-1 review cycle 3 |
| Role | rot-synthesis-architect (`AR-0011`) |
| Input commit | `c8cdfac` |
| Work performed | Wrote `SYNTHESIS.md` comparing specialists A and B. Pack revision 5: new `29` (FD-1 fact-decision rule, decision register, root-version threshold check, attack-set calculator), `30`, `31`; rewrote 00, 05, 06, 21, 22, 25 and 28; amended the rest. Checker gains release-scoped registration. Schemas 4 new, 9 revised, 2 withdrawn. `examples/rev5`, `evidence/r5`. D-0008 and ARCH-0002 PROPOSED revision 5. Owner options OP-1…OP-15. |
| Report / evidence | `AGENT_RUNS/AR-0011.report.yaml`; `release/root-of-trust/4.1.6/evidence/r5/`; `release/root-of-trust/4.1.6-alternatives-r5/SYNTHESIS.md` |
| Verdict | `ARCHITECTURE_REVISION_READY_FOR_REVIEW` (author's readiness claim; not an acceptance) |
| Output commit | work `cdb4e14`, report `42dbfbd`, merged `ec96583` |
| Findings | Architect-reported claims, to be independently tested: CS5 calculator 408 configurations with 0 invariant or monotonicity failures and no single-key-plus-pipeline acceptance; FA5 45/45, vectors 17/17, mutants 26/27 (1 equivalent); REG5 15/15 mixed releases refused, secret excluded on real 4.1.5; ST5 6,292 subdirectory invocations with all 112 trust-path writes and 200 nested installs detected; DA03r5 20/20 and 17/17; checker self-test 71/71; P1r4, P4r4 and P3r3 unchanged. Disclosed non-material scope notes (helper sessions within the authoring role; folder names seen). |
| Next action | independent review panel B and C on revision 5 |

## L-0028 — 2026-09-14 — revision-5 review panel handed off

| Field | Value |
|---|---|
| Iteration | architecture revision 5, Phase-1 review cycle 3 |
| Role | orchestrator |
| Input commit | `ec96583` |
| Work performed | Wrote HO-0012 (B) and HO-0013 (C) from the generic reviewer templates (prior review r4 `97a5545`; escalation proposals listed as background). Claimed AR-0012 and AR-0013. Created separate worktrees and branches. |
| Report / evidence | `HANDOFFS/HO-0012-*.md`, `HANDOFFS/HO-0013-*.md`, `CHECKPOINTS/CP-0009.yaml` |
| Verdict | — |
| Output commit | the commit adding these records |
| Findings | — |
| Next action | spawn AR-0012 and AR-0013 in parallel |

## L-0029 — 2026-09-14 — revision-5 review panel spawned

| Field | Value |
|---|---|
| Iteration | architecture revision 5, Phase-1 review cycle 3 |
| Role | rot-reviewer-trust-security (`AR-0012`) and rot-reviewer-compat-transaction (`AR-0013`), fresh Opus 5 contexts, in parallel |
| Input commit | `bfaa943` (worktrees `wt/review-r5-b`, `wt/review-r5-c`; branches `phase1/rot1-r5-review-b`, `phase1/rot1-r5-review-c`) |
| Work performed | spawned on HO-0012 and HO-0013; running. Prompts add the revision-5 surfaces (FD-1 register, calculator, release registration, reproducer quorum, gov-admit and fingerprint, C0 mode, protected install location, OP-1…OP-15) and forbid listing the scratchpad root. |
| Report / evidence | expected `AGENT_RUNS/AR-0012.report.yaml`, `AGENT_RUNS/AR-0013.report.yaml`; `release/root-of-trust/4.1.6-review-r5/{B-trust-security,C-compat-transaction}/` |
| Verdict | pending |
| Output commit | pending |
| Findings | — |
| Next action | hold the first completed branch unmerged; on both completions verify, merge, write HO-0014, spawn synthesis reviewer D |

## L-0030 — 2026-09-14 — revision-5 reviewer B completed

| Field | Value |
|---|---|
| Iteration | architecture revision 5, Phase-1 review cycle 3 |
| Role | rot-reviewer-trust-security (`AR-0012`) |
| Input commit | `bfaa943` (architecture `cdb4e14`) |
| Work performed | Reproduced the architect's CSI, CS5, P4r5, DA03r5, FA5, REG5 and P1r4, plus the r4 and r3 trust probes. Authored held-out RV5-B-A01…A19 (10 executed, 6 computed, 3 design); A01, A04, A09 and A12 repeated byte-identical. |
| Report / evidence | `AGENT_RUNS/AR-0012.report.yaml` (on branch); `release/root-of-trust/4.1.6-review-r5/B-trust-security/` |
| Verdict | `BLOCKING_FINDINGS_PRESENT` (role verdict) |
| Output commit | work `248f12a`, report `9aa5c3f` on `phase1/rot1-r5-review-b`; held unmerged until reviewer C completes |
| Findings | **HIGH RV5-B-H1:** a tampered channel page alone, with no genuine key, admits a malicious binary on a new machine (the fingerprint selects the lineage, the same page selects the admitter, and the two-channel rule comes from the selected policy); declared minimum sets wrong in 288/288 configurations. **HIGH RV5-B-H2:** the build image decides production bytes and is checked only against an unassigned "owner's image record", so honest and diverse reproducers reproduce the malicious binary. **HIGH RV5-B-H3:** under OP-2 (b), E7 never checks verification records; delegated custodians plus `release-final`, or stolen registration, trust-state and `release-final` keys, make malicious content effective; OP-2 (b), OP-4 and OP-8 consequences false. **MEDIUM:** M1–M5. **LOW:** L1–L6. **Prior:** BC4-1 open (H2); BC4-2 and BC4-3 narrowed (H1, H3); BC4-4 open; RV4-H1…H3 closed as stated. No scope deviation. |
| Next action | await AR-0013; then merge B and C, write HO-0014, spawn synthesis reviewer D |

## L-0031 — 2026-09-14 — revision-5 reviewer C completed; panel merged

| Field | Value |
|---|---|
| Iteration | architecture revision 5, Phase-1 review cycle 3 |
| Role | rot-reviewer-compat-transaction (`AR-0013`) |
| Input commit | `bfaa943` (architecture `cdb4e14`) |
| Work performed | Built independent registers (104/109/115/119). Ran 30,165 rows plus 1,335 `--root` rows over real 4.1.2–4.1.5 on the revision-5 layouts, using an independently encoded installation-state predicate. Reproduced review-r4 C probes, ST5, D-A01 and P3r3. Authored held-out RV5-C-A01…A13 (9 executed, 3 model, 1 design). |
| Report / evidence | `AGENT_RUNS/AR-0013.report.yaml`; `release/root-of-trust/4.1.6-review-r5/C-compat-transaction/` |
| Verdict | `NO_BLOCKING_FINDINGS` (role verdict) |
| Output commit | work `840d583`, report `033e1f2`, merged `7267371`. Reviewer B merged first: `0203580`. |
| Findings | **Carried (fail-closed or inert):** RV5-C-M1 (no `.gitattributes`; autocrlf clones fail closed), RV5-C-M2 (out-of-project ignore sources drop the occupation; fail closed), RV5-C-L1 (LP-1s prose overclaims; inert litter), RV5-C-L2 (transaction area omitted from the §9.1/§9.2 closure; inert), RV5-C-L3 ("first admission" undefined; re-run discards the monotonic VTS). **Prior:** R2-H4 CLOSED as a class (0 of 30,165 violations); RV4-M1 and RV4-M6 closed for their stated scope, with narrowed residuals. No scope deviation. |
| Next action | synthesis reviewer D on revision 5 |

## L-0032 — 2026-09-14 — revision-5 synthesis handed off

| Field | Value |
|---|---|
| Iteration | architecture revision 5, Phase-1 review cycle 3 |
| Role | orchestrator |
| Input commit | `7267371` |
| Work performed | Wrote HO-0014 for the independent synthesis reviewer. Added §2a asking, for each confirmed blocking class, remainder vs materially new and engineering correction vs genuine owner trade-off (options and consequences, not chosen). Claimed AR-0014. Added the review-r5 B and C directories to immutable evidence. |
| Report / evidence | `HANDOFFS/HO-0014-rot-review-r5-d-synthesis.md`, `CHECKPOINTS/CP-0010.yaml` |
| Verdict | — |
| Output commit | the commit adding these records |
| Findings | — |
| Next action | spawn AR-0014 |

## L-0033 — 2026-09-14 — revision-5 synthesis reviewer spawned

| Field | Value |
|---|---|
| Iteration | architecture revision 5, Phase-1 review cycle 3 |
| Role | rot-review-synthesis (`AR-0014`, fresh Opus 5 context) |
| Input commit | `59c1e5c` (worktree `wt/review-r5-d`, branch `phase1/rot1-r5-review-d`) |
| Work performed | spawned on HO-0014; running. Must classify each confirmed blocking class as a remainder or materially new, and as ENGINEERING_CORRECTION or OWNER_TRADE_OFF. |
| Report / evidence | expected `AGENT_RUNS/AR-0014.report.yaml`; `release/root-of-trust/4.1.6-review-r5/{00,10,11}*`, `D-synthesis/` |
| Verdict | pending |
| Output commit | pending |
| Findings | — |
| Next action | on completion: verify, merge; route per verdict and classification (owner D-0008 gate, owner trade-off gate, or revision-6 architect) |

## L-0034 — 2026-09-14 — revision 5 REJECTED by synthesis

| Field | Value |
|---|---|
| Iteration | architecture revision 5, Phase-1 review cycle 3 |
| Role | rot-review-synthesis (`AR-0014`) |
| Input commit | `59c1e5c` (architecture `cdb4e14`; B `248f12a`; C `840d583`) |
| Work performed | Reproduced the architect's and both panels' decisive probes, including C's 30,165-row `matrix5`. Adjudicated B and C. Authored held-out RV5-D-A01…A08. Classified each blocking class by remainder and by kind of fix. |
| Report / evidence | `AGENT_RUNS/AR-0014.report.yaml`; `release/root-of-trust/4.1.6-review-r5/{00-REVIEW-REPORT,10-BLOCKING-FINDINGS,11-CORRECTION-DELTA}.md`, `D-synthesis/` |
| Verdict | **`ROOT_OF_TRUST_ARCHITECTURE_REJECTED`** |
| Output commit | review `d1228cb`, report `ed6ea29`, merged `aad29de` |
| Findings | **HIGH RV5-H1:** the first binary is selected by the channels alone (fingerprint selects lineage and quorum rule; one channel selects the admitter). **HIGH RV5-H2:** the build image selects every production binary's bytes, with no assigned authority. **HIGH RV5-H3:** registered constitutional content is not established first-hand (pipeline plus threshold-1 release keys; secret indexed on 4.1.5). **MEDIUM:** RV5-M1…M9. **LOW:** L1–L9. **Classes:** BC5-1 (engineering plus owner trade-off T1-a…T1-d), BC5-2 (engineering plus owner trade-off E-a…E-c), BC5-3 and BC5-4 (engineering). All are remainders, as new instances. **Confirmed closed:** R2-H4 as a class. **HO-0001:** §3.1–§3.3 NOT SATISFIED; §3.4 SATISFIED. |
| Next action | revision-6 architect |

## L-0035 — 2026-09-14 — routing decision; revision-6 architect handed off

| Field | Value |
|---|---|
| Iteration | architecture revision 6, Phase-1 review cycle 4 |
| Role | orchestrator |
| Input commit | `aad29de` |
| Work performed | **Routing decision.** The synthesis review routes BC5-1 and BC5-2 "architect, then owner" and requires (§7 item 4) that T1-a…T1-d and E-a…E-c be presented with computed consequences, without choosing. The orchestrator follows that route: the trade-offs become computed owner options in revision 6 and are decided in the single consolidated D-0008 gate (protocol §7). This supersedes the provisional CP-0010 rule to raise them before another revision, and avoids presenting options without computed consequences or splitting the owner gate. The specialist escalation has already run; no materially new class has appeared (streak 0), so the protocol §5 new-class escalation is not triggered. Wrote HO-0015. Claimed AR-0015. Added the review-r5 consolidated files to immutable evidence. |
| Report / evidence | `HANDOFFS/HO-0015-rot-architect-r6.md`, `CHECKPOINTS/CP-0011.yaml` |
| Verdict | — |
| Output commit | the commit adding these records |
| Findings | — |
| Next action | spawn AR-0015 |

## L-0036 — 2026-09-14 — revision-6 architect spawned

| Field | Value |
|---|---|
| Iteration | architecture revision 6, Phase-1 review cycle 4 |
| Role | rot-architect (`AR-0015`, fresh Opus 5 context) |
| Input commit | `17acb8b` (worktree `wt/arch-r6`, branch `phase1/rot1-r6-architect`) |
| Work performed | spawned on HO-0015; running |
| Report / evidence | expected `AGENT_RUNS/AR-0015.report.yaml`; pack `release/root-of-trust/4.1.6/` |
| Verdict | pending |
| Output commit | pending |
| Findings | — |
| Next action | on completion: verify, merge, instantiate revision-6 B/C handoffs, spawn B and C in parallel |

## L-0037 — 2026-09-14 — revision 6 authored

| Field | Value |
|---|---|
| Iteration | architecture revision 6, Phase-1 review cycle 4 |
| Role | rot-architect (`AR-0015`) |
| Input commit | `17acb8b` |
| Work performed | New `32` first-contact root, `33` build environment, `34` first-hand constitutional content, and `decision-register/` (35 decisions; `register_check`, `statements_check`). Rewrote 00, 06, 21, 22, 25 and 28–31; amended the rest. Schemas 4 new, 8 revised. `examples/rev6`, `evidence/r6`. D-0008 and ARCH-0002 PROPOSED revision 6. Owner options OP-1…OP-16, with T1 mapped to OP-13 (a)–(d) and E mapped to OP-16 (a)–(c). |
| Report / evidence | `AGENT_RUNS/AR-0015.report.yaml`; `release/root-of-trust/4.1.6/evidence/r6/` |
| Verdict | `ARCHITECTURE_REVISION_READY_FOR_REVIEW` (author's readiness claim; not an acceptance) |
| Output commit | work `4106885`, report `0175b0c`, merged `2080255` |
| Findings | Architect-reported claims, to be independently tested: FA6 refuses every attack outside the stated root for 7 OP-13 answers, and executed minimal sets equal CS6 for 7/7; ENV6 21/21 bit-identical; CON6 17/17; CSI self-test 78/78; DA07r6 22/22; 2(e) instruments byte-identical; reviewer C's matrix on the r6 layout 30,735 rows with R2-H4 at 0 violations; CS6 1,648 configurations, 0 invariant or monotonicity failures. Unsupported combinations stated. **Disclosures:** stray scratch file; helper sessions LAY6 and ENV6. The architect searched the session transcript for path strings; the results showed names of other orchestration files (none opened). |
| Next action | independent review panel B and C on revision 6 |

## L-0038 — 2026-09-14 — independence control added; revision-6 review panel handed off

| Field | Value |
|---|---|
| Iteration | architecture revision 6, Phase-1 review cycle 4 |
| Role | orchestrator |
| Input commit | `2080255` |
| Work performed | **Independence control.** Subagent transcripts and task-output files hold other roles' work, including the orchestrator's tool calls. Reading them could let parallel reviewers see each other's findings, or a builder see held-out verifier tests. Added a standing prohibition on reading, listing or searching them to every role template (patched in scratch drafts) and to `forbidden_until_gate`, together with a rule that no builder runs concurrently with a verifier before its verdict is committed. Assessed AR-0015's search as non-material for an architect, which may read completed evidence. Wrote HO-0016 (B) and HO-0017 (C) with the prohibition. Claimed AR-0016 and AR-0017. |
| Report / evidence | `HANDOFFS/HO-0016-*.md`, `HANDOFFS/HO-0017-*.md`, `CHECKPOINTS/CP-0012.yaml` |
| Verdict | — |
| Output commit | the commit adding these records |
| Findings | — |
| Next action | spawn AR-0016 and AR-0017 in parallel |

## L-0039 — 2026-09-14 — revision-6 review panel spawned

| Field | Value |
|---|---|
| Iteration | architecture revision 6, Phase-1 review cycle 4 |
| Role | rot-reviewer-trust-security (`AR-0016`) and rot-reviewer-compat-transaction (`AR-0017`), fresh Opus 5 contexts, in parallel |
| Input commit | `cd4526a` (worktrees `wt/review-r6-b`, `wt/review-r6-c`; branches `phase1/rot1-r6-review-b`, `phase1/rot1-r6-review-c`) |
| Work performed | spawned on HO-0016 and HO-0017; running. Prompts carry the transcript prohibition and the revision-6 surfaces: B covers the decision register, CS6, first-contact root under OP-13, build environments under OP-16, first-hand content and OP-1…OP-16; C covers the r6 layout, transaction-area closure, `.gitattributes` and ignore sources, and admission and re-admission transactions. |
| Report / evidence | expected `AGENT_RUNS/AR-0016.report.yaml`, `AGENT_RUNS/AR-0017.report.yaml`; `release/root-of-trust/4.1.6-review-r6/{B-trust-security,C-compat-transaction}/` |
| Verdict | pending |
| Output commit | pending |
| Findings | — |
| Next action | hold the first completed branch unmerged; on both completions verify, merge, write HO-0018 (v3 template), spawn synthesis reviewer D |

## L-0040 — 2026-09-14 — reviewer C (revision 6) stopped early; same run resumed

| Field | Value |
|---|---|
| Iteration | architecture revision 6, Phase-1 review cycle 4 |
| Role | orchestrator (routing), concerning rot-reviewer-compat-transaction `AR-0017` |
| Input commit | `73228fd` |
| Work performed | AR-0017's turn ended while its own matrix probes were still executing in its scratch root. Its branch had no commits and no report, so the run was INCOMPLETE at that point and advanced no gate. The orchestrator checked only Git and process state, not the transcript. It then resumed the same run by message: wait for its own probes, then complete every HO-0017 deliverable. No findings content was exchanged, and independence is unchanged. |
| Report / evidence | `AGENT_RUNS/AR-0017.run.yaml` (interruptions) |
| Verdict | — |
| Output commit | the commit adding this entry |
| Findings | — |
| Next action | await AR-0016 and AR-0017 completion |

## L-0041 — 2026-09-14 — revision-6 reviewer B completed

| Field | Value |
|---|---|
| Iteration | architecture revision 6, Phase-1 review cycle 4 |
| Role | rot-reviewer-trust-security (`AR-0016`) |
| Input commit | `cd4526a` (architecture `4106885`) |
| Work performed | Reproduced every architect instrument (CS6, P4r6, DA03r6, DA07r6, FA6, CON6, ENV6, SRC6, UW6, ATTR6, CSI, `register_check`, `statements_check`) and the retained r5 instruments and probes. Authored held-out RV6-B-A01…A16 (8 executed, 6 computed, 2 design). A11 (352 machine rows) and A12 (246,608 key subsets) hold. |
| Report / evidence | `AGENT_RUNS/AR-0016.report.yaml` (on branch); `release/root-of-trust/4.1.6-review-r6/B-trust-security/` |
| Verdict | `BLOCKING_FINDINGS_PRESENT` (role verdict) |
| Output commit | work `5128086`, report `0736ad4` on `phase1/rot1-r6-review-b`; held unmerged until reviewer C completes |
| Findings | **HIGH RV6-B-H1:** the trust-state publisher composes the first-contact code and the independent sources only carry it, so one party selects lineage, state and evaluator on first install under OP-13 (a), (b), (c)-either and (d); the declared root and the OP-9/OP-13 statements are false. **HIGH RV6-B-H2:** under OP-13 (c)-either, a package submitter or a replayed old signed package (optional `valid_until`) selects the first TCB; FA6 lacks both paths. **HIGH RV6-B-H3:** no party establishes the environment manifest, so its writer selects binary bytes under OP-16 (a) and (b), and (b) counts diversity by label; executed with real `rustc`. **MEDIUM:** M1 (re-admission ignores the stored high-water), M2 (generated CONTENT block misprint), M3 (register completeness checked over rule ids, not selectors). **LOW:** L1–L4. **Prior:** BC5-3 closed as a class within B's attacks; BC5-1, BC5-2 and BC5-4 narrowed; OP-6, OP-9, OP-13 and OP-16 statements false. Non-material scope disclosures recorded; canonical checkout verified clean. |
| Next action | await AR-0017; then merge B and C, write HO-0018, spawn synthesis reviewer D |

## L-0042 — 2026-09-14 — revision-6 reviewer C completed; panel merged; owner briefed

| Field | Value |
|---|---|
| Iteration | architecture revision 6, Phase-1 review cycle 4 |
| Role | rot-reviewer-compat-transaction (`AR-0017`, resumed once); orchestrator |
| Input commit | `cd4526a` (architecture `4106885`) |
| Work performed | **C:** independent registers (104/109/115/119 from help and source). Pre-RoT matrix of 62,036 rows (61,520 run, 516 skipped, 0 timeouts) across root, subdirectory, environment-variable, nested and 22 Git-operation trees. Reproduced LAY6 (30,735 rows), ADM6 and UW6. Authored held-out RV6-C-A01…A19. **Orchestrator:** at the owner's request, gave in chat a summary of revision verdicts and the OP-1…OP-16 options, with reviewer B's caveats. The owner said they will answer; answers are to be recorded verbatim as owner-initiated input. |
| Report / evidence | `AGENT_RUNS/AR-0017.report.yaml`; `release/root-of-trust/4.1.6-review-r6/C-compat-transaction/` |
| Verdict | `NO_BLOCKING_FINDINGS` (role verdict) |
| Output commit | work `02bb905`, report `b2c4cbe`, merged `2583388`. Reviewer B merged first: `b4d6b9a`. |
| Findings | **Carried MEDIUM:** RV6-C-M1 (global or `.git/info` ignore drops the migration occupation; fails closed), M2 (first-install layout migration and exchange-to-journal window not journalled; half-migrated trees, never `COMPLETE`), M3 (per-project record identity under worktree, move, fork or template), M4 (contradictory re-recording rules), M5 (verifier trust-store location specified two ways). **LOW:** L1–L6. **Prior:** R2-H4 CLOSED as a class; RV5-M3 and RV5-M6 closed; RV5-M7 and RV5-L7 narrowed; C-2, C-3 and C-5 open (implementation-only). **Record clarification for L-0041:** the canonical checkout's tracked tree was clean; three ignored Python caches under `capabilities/` date from 2026-09-12, before Phase 1, and were written by no Phase-1 role. |
| Next action | synthesis reviewer D on revision 6 |

## L-0043 — 2026-09-14 — revision-6 synthesis handed off

| Field | Value |
|---|---|
| Iteration | architecture revision 6, Phase-1 review cycle 4 |
| Role | orchestrator |
| Input commit | `2583388` |
| Work performed | Wrote HO-0018 from the v3 synthesis template (classification addendum §2a, transcript prohibition). Claimed AR-0018. Added the review-r6 B and C directories to immutable evidence. |
| Report / evidence | `HANDOFFS/HO-0018-rot-review-r6-d-synthesis.md`, `CHECKPOINTS/CP-0013.yaml` |
| Verdict | — |
| Output commit | the commit adding these records |
| Findings | — |
| Next action | spawn AR-0018 |

## L-0044 — 2026-09-14 — revision-6 synthesis reviewer spawned

| Field | Value |
|---|---|
| Iteration | architecture revision 6, Phase-1 review cycle 4 |
| Role | rot-review-synthesis (`AR-0018`, fresh Opus 5 context) |
| Input commit | `b9bed32` (worktree `wt/review-r6-d`, branch `phase1/rot1-r6-review-d`) |
| Work performed | spawned on HO-0018; running. The prompt carries the transcript prohibition, the §2a classification requirement and an instruction to keep its turn active while its own probes run. |
| Report / evidence | expected `AGENT_RUNS/AR-0018.report.yaml`; `release/root-of-trust/4.1.6-review-r6/{00,10,11}*`, `D-synthesis/` |
| Verdict | pending |
| Output commit | pending |
| Findings | — |
| Next action | on completion: verify, merge, route per verdict. Owner OP answers pending; record them verbatim on receipt. |

## L-0045 — 2026-09-14 — product-owner design requirements recorded

| Field | Value |
|---|---|
| Iteration | architecture revision 6 synthesis (running); revision 7 planned |
| Role | product owner (source); orchestrator (recording and routing) |
| Input commit | `9dcbf7a` |
| Work performed | Recorded the owner's message verbatim as OWNER-DESIGN-REQUIREMENTS-0001: binding design inputs for RoT-1 revision 7, **not** D-0008 approval. **Direction:** Option C / RoT-1; A, B, D, E and F unsupported as production alternatives. **Selections:** OP-1 3 keys 2-of-3 with three custodial roles; OP-2 (b) 2-of-3; OP-3 mode A; OP-4 separate candidate key plus purpose-separated 2-of-3 authorities; OP-5 30 days; OP-6 (a); OP-7 (a) with 90d/7d/24h limits; OP-8 2; OP-9 (b)+(d); OP-10 (b); OP-11 (b); OP-12 (a); OP-13 (b); OP-14 (b); OP-15 (a); OP-16 (b). First-contact trust base approved by root 2-of-3, never by the trust-state publisher. The environment manifest is deterministic and authoritative only with reproducer agreement plus registration 2-of-3. Initial certified profile only, with exclusions. Registered in the gate register; state updated: revision 7 is mandatory after the revision-6 synthesis, D-0008 fields are kept, D-0007 stays ACTIVE, and selected parameters are not reopened without a genuinely new trade-off. AR-0018 continues unaffected. |
| Report / evidence | `GATES/OWNER-DESIGN-REQUIREMENTS-0001.md` (verbatim, sha256 `c85d80c2402b94bf…`), `GATES/OWNER-DESIGN-REQUIREMENTS-0001.yaml` (derived index), `CHECKPOINTS/CP-0014.yaml` |
| Verdict | — (owner input; not a verdict and not a ratification) |
| Output commit | the commit adding these records |
| Findings | — |
| Next action | await AR-0018; then revision-7 architect on revision-6 findings plus owner requirements |

## L-0046 — 2026-09-14 — revision 6 REJECTED by synthesis

| Field | Value |
|---|---|
| Iteration | architecture revision 6, Phase-1 review cycle 4 |
| Role | rot-review-synthesis (`AR-0018`) |
| Input commit | `b9bed32` (architecture `4106885`; B `5128086`; C `02bb905`) |
| Work performed | Reproduced all of B's probes, the architect's revision-6 and retained revision-5 instruments, C's 62,036-row matrix and C's probes, and review r5's decisive probes. Adjudicated B and C. Authored held-out RV6-D-A01…A10. Classified the blocking classes. |
| Report / evidence | `AGENT_RUNS/AR-0018.report.yaml`; `release/root-of-trust/4.1.6-review-r6/{00-REVIEW-REPORT,10-BLOCKING-FINDINGS,11-CORRECTION-DELTA}.md`, `D-synthesis/` |
| Verdict | **`ROOT_OF_TRUST_ARCHITECTURE_REJECTED`** |
| Output commit | review `ab6b1f8`, report `57af7ee`, merged `248c635` |
| Findings | **HIGH:** RV6-H1 (first-contact values selected outside the declared root: publisher-composed manifest and code, source list printed by an unadmitted binary, platform package submitter); RV6-H2 (first-contact values have no age limit; replay selects an old state, including on re-admission); RV6-H3 (no party establishes the environment manifest). **MEDIUM:** RV6-M1…M6; M2 needs an architecture change. **LOW:** L1–L12. **INFO:** I1–I2. **Adjudications:** B's OP-11 claim refuted; B-M1 re-rated LOW; C's R2-H4 CLOSED confirmed. **HO-0001:** §3.1 and §3.4 SATISFIED; §3.2 and §3.3 NOT SATISFIED. **Classes:** BC6-1 (engineering plus owner trade-off F1-a…c), BC6-2 (engineering plus owner trade-off C-a…c), BC6-3 and BC6-4 (engineering); all remainders. |
| Next action | revision 7 per owner design requirements |

## L-0047 — 2026-09-14 — revision-7 architect handed off (concrete certified profile)

| Field | Value |
|---|---|
| Iteration | architecture revision 7, Phase-1 review cycle 5 |
| Role | orchestrator |
| Input commit | `248c635` |
| Work performed | **Routing.** Per OWNER-DESIGN-REQUIREMENTS-0001, revision 7 follows the revision-6 verdict. The requirements already select the parameters governing the synthesis trade-offs: F1 is answered by root 2-of-3 approval of the first-contact trust base and admitter, with the publisher never composing it; C is answered by the OP-7 (a) windows, the OP-13 (b) offline media channel and the OP-14 (b) high-water. The architect applies the stricter reading and must surface any uncovered residual as a precise owner trade-off, not decide it. No specialist re-escalation: the owner's concretisation is the lever. **Actions:** wrote HO-0019 from the revision-7 template; claimed AR-0019; added the review-r6 consolidated files and the owner requirements record to immutable evidence. |
| Report / evidence | `HANDOFFS/HO-0019-rot-architect-r7.md`, `CHECKPOINTS/CP-0015.yaml` |
| Verdict | — |
| Output commit | the commit adding these records |
| Findings | — |
| Next action | spawn AR-0019 |

## L-0048 — 2026-09-14 — revision-7 architect spawned

| Field | Value |
|---|---|
| Iteration | architecture revision 7, Phase-1 review cycle 5 |
| Role | rot-architect (`AR-0019`, fresh Opus 5 context) |
| Input commit | `4ed71cc` (worktree `wt/arch-r7`, branch `phase1/rot1-r7-architect`) |
| Work performed | spawned on HO-0019 (concrete certified profile per OWNER-DESIGN-REQUIREMENTS-0001); running. The prompt carries the transcript prohibition, the keep-turn-active instruction, and permission to read the owner requirements record. |
| Report / evidence | expected `AGENT_RUNS/AR-0019.report.yaml`; pack `release/root-of-trust/4.1.6/` |
| Verdict | pending |
| Output commit | pending |
| Findings | — |
| Next action | on completion: verify, including the D-0008 fields; merge; spawn the revision-7 B/C panel with concrete-profile handoffs |

## L-0049 — 2026-09-14 — revision-7 architect stopped early; same run resumed

| Field | Value |
|---|---|
| Iteration | architecture revision 7, Phase-1 review cycle 5 |
| Role | orchestrator (routing), concerning rot-architect `AR-0019` |
| Input commit | `4f2bed1` |
| Work performed | AR-0019's turn ended while its own matrix6 re-run was still executing in its scratch root. It had 67 uncommitted entries and no commits or report, so the run was INCOMPLETE at that point and advanced no gate. The orchestrator checked only Git and process state, not the transcript. It then resumed the same run by message: wait for the probes itself, finish the remaining steps, commit and report. No findings content was exchanged. |
| Report / evidence | `AGENT_RUNS/AR-0019.run.yaml` (interruptions) |
| Verdict | — |
| Output commit | the commit adding this entry |
| Findings | — |
| Next action | await AR-0019 completion |

## L-0050 — 2026-09-14 — revision 7 authored (concrete certified profile CP-1)

| Field | Value |
|---|---|
| Iteration | architecture revision 7, Phase-1 review cycle 5 |
| Role | rot-architect (`AR-0019`, resumed once) |
| Input commit | `4ed71cc` |
| Work performed | New `35-CERTIFIED-PROFILE.md` and `profile/CP-1.yaml`: every owner selection mapped to its enforcement point, exclusions EX-01…EX-24, option-selecting fields, schemas, commands and calculator axes removed from the certified surface (withdrawn schemas under `schemas/withdrawn-non-production/`). Pack 00–34 amended; decision register over schema fields, procedure inputs and exclusions; new first-contact-authority and environment-lock schemas; `examples/rev7`, `evidence/r7`. D-0008 and ARCH-0002 PROPOSED revision 7 (fields verified). Initial targets `x86_64-unknown-linux-musl` and `aarch64-unknown-linux-musl`, both NOT CERTIFIED pending CC-1…CC-9. |
| Report / evidence | `AGENT_RUNS/AR-0019.report.yaml`; `release/root-of-trust/4.1.6/evidence/r7/` |
| Verdict | `ARCHITECTURE_REVISION_READY_FOR_REVIEW` (author's readiness claim; not an acceptance) |
| Output commit | work `d07d200`, report `a1fb884`, merged `f4b964e` |
| Findings | Architect-reported claims, to be independently tested: register_check PASS (45 decisions, 578 fields); statements_check PASS (216 atom sets); FA7 13/13; CS7 39 configurations, 0 invariant failures; CUR7 14/14; ADM7 12/12; ENV7 14/14 (real rustc); DA09r7 7/7 held-out register mutations detected; BA12r7 0 accepts with ≤ 1 key over 99,772 subsets; PROF7 24/24 exclusions and 113/113 checks; `matrix6` R2-H4 0 violations over 62,036 rows. **Owner-parameter conflicts surfaced (not decided):** OT-1, offline media versus 24 h freshness (interim: 24 h applies to media); OT-2, OP-10 (b) not evidenced for the current compiler (no target certifiable yet). Five review probes cannot run unmodified because they open withdrawn artefacts; they are re-expressed. |
| Next action | independent review panel B and C on CP-1 |

## L-0051 — 2026-09-14 — revision-7 review panel handed off

| Field | Value |
|---|---|
| Iteration | architecture revision 7, Phase-1 review cycle 5 |
| Role | orchestrator |
| Input commit | `f4b964e` |
| Work performed | Wrote HO-0020 (B) and HO-0021 (C) from the v3 concrete-profile templates. They require attacking CP-1's real combinations and exclusions, flagging deviation from OWNER-DESIGN-REQUIREMENTS-0001, not reopening owner parameters without a genuinely new trade-off, and checking the D-0008 fields; they also carry the transcript prohibition. Claimed AR-0020 and AR-0021. Recorded OT-1 and OT-2 as architect-surfaced owner conflicts pending independent confirmation. |
| Report / evidence | `HANDOFFS/HO-0020-*.md`, `HANDOFFS/HO-0021-*.md`, `CHECKPOINTS/CP-0016.yaml` |
| Verdict | — |
| Output commit | the commit adding these records |
| Findings | — |
| Next action | spawn AR-0020 and AR-0021 in parallel |

## L-0052 — 2026-09-14 — revision-7 review panel spawned

| Field | Value |
|---|---|
| Iteration | architecture revision 7, Phase-1 review cycle 5 |
| Role | rot-reviewer-trust-security (`AR-0020`) and rot-reviewer-compat-transaction (`AR-0021`), fresh Opus 5 contexts, in parallel |
| Input commit | `7e50c6e` (worktrees `wt/review-r7-b`, `wt/review-r7-c`; branches `phase1/rot1-r7-review-b`, `phase1/rot1-r7-review-c`) |
| Work performed | Spawned on HO-0020 and HO-0021; running. The prompts target concrete profile CP-1, its combinations and exclusions EX-01…EX-24, conformance with OWNER-DESIGN-REQUIREMENTS-0001, the D-0008 fields and the assessment of OT-1 and OT-2. They carry the transcript prohibition and the keep-turn-active instruction. The owner is informed of OT-1 and OT-2 in chat (non-blocking). |
| Report / evidence | expected `AGENT_RUNS/AR-0020.report.yaml`, `AGENT_RUNS/AR-0021.report.yaml`; `release/root-of-trust/4.1.6-review-r7/{B-trust-security,C-compat-transaction}/` |
| Verdict | pending |
| Output commit | pending |
| Findings | — |
| Next action | hold the first completed branch unmerged; on both completions verify, merge, write HO-0022 (D v4 template), spawn synthesis reviewer D |

## L-0053 — 2026-09-14 — revision-7 reviewer B completed

| Field | Value |
|---|---|
| Iteration | architecture revision 7, Phase-1 review cycle 5 |
| Role | rot-reviewer-trust-security (`AR-0020`) |
| Input commit | `7e50c6e` (architecture `d07d200`) |
| Work performed | Re-ran the architect's runner from a scratch export and compared 68 outputs: 53 byte-identical, 8 differ only in run-dependent fields, 2 committed outputs stale with no verdict change, 5 prior probes blocked by withdrawn artefacts (CP-1 equivalents reproduce). Re-ran PROF7 (113/113) with injected excluded fields detected. Authored held-out RV7-B-A01…A13 (9 executed). |
| Report / evidence | `AGENT_RUNS/AR-0020.report.yaml` (on branch); `release/root-of-trust/4.1.6-review-r7/B-trust-security/` |
| Verdict | `BLOCKING_FINDINGS_PRESENT` (role verdict) |
| Output commit | work `54be694`, report `44858be` on `phase1/rot1-r7-review-b`; held unmerged until reviewer C completes |
| Findings | **HIGH RV7-B-H1:** a revocation counts at first contact only if a Trust State lists it, and no party must list it; a revoked binary was admitted on 11 daily states with its revocation up to 342 h old. **HIGH RV7-B-H2:** C3 checks only the age of the confirmation or pin, not of the named state; C3 was allowed on a 4-month-old state and on a re-stamped CI pin. **MEDIUM RV7-B-M1 (blocking per B):** one onboarding record names both first-contact sources. **LOW:** L1–L6. **INFO:** I1, I2. **Prior:** BC6-3 closed within B's attacks; BC6-1, BC6-2 and BC6-4 narrowed; RV6-H1, H2, H3 closed as stated. **Owner conformance:** exclusions EX-01…EX-24 conform; deviations via H1 (OP-4), H2 (OP-7 (a)) and M1 (OP-13 (b) stated consequence); D-0008 fields conform. **OT-1:** genuine owner trade-off, understated. **OT-2:** real, but already answered by the owner's "not certified" rule. |
| Next action | await AR-0021; then merge B and C, write HO-0022 (D v4), spawn synthesis reviewer D |

## L-0054 — 2026-09-14 — product-owner resolutions of OT-1 and OT-2 recorded

| Field | Value |
|---|---|
| Iteration | architecture revision 7, Phase-1 review cycle 5 (panel in progress) |
| Role | product owner (source); orchestrator (recording and routing) |
| Input commit | `7c8415d` |
| Work performed | Recorded the owner's message verbatim as OWNER-DESIGN-REQUIREMENTS-0002, binding resolutions clarifying OP-7, OP-10 and OP-13 (not D-0008 activation). **OT-1:** both OP-13 (b) channels independently provide matching immutable first-contact identity material (offline media allowed as the second identity source); current trust state stays under OP-7 (a) at 24 h with no media window and no grace period; without fresh state the machine may only inspect immutable material at the bounded diagnostic/bootstrap level and never reaches production admission or C1–C3; the high-water is never lowered. **OT-2:** no interim certification exception and no upstream-archive fallback; the criterion targets the trusting-trust class with a practical, independent, non-circular evidence route; distributions or mirrors are not independence, and byte-identity across different compilers is not required as a ritual; an unmet target is labelled "NOT CERTIFIED — TOOLCHAIN ASSURANCE INCOMPLETE"; architecture acceptance does not require a certified target if the criterion is explicit, executable/testable and non-circular. **Routing:** gate register and state updated, forbidden actions added, handoff templates for synthesis D, later reviewers and later architects patched to carry both owner records. Reviewer B's completed OT-1 assessment is superseded by the resolution; its H1/H2/M1 findings stand for adjudication. Running reviewer C will be informed of the record. |
| Report / evidence | `GATES/OWNER-DESIGN-REQUIREMENTS-0002.md` (verbatim, sha256 `914720488a63e121…`), `GATES/OWNER-DESIGN-REQUIREMENTS-0002.yaml`, `CHECKPOINTS/CP-0017.yaml` |
| Verdict | — (owner input; not a verdict and not a ratification) |
| Output commit | the commit adding these records |
| Findings | — |
| Next action | message AR-0021 with the record; await it; synthesis D with both owner records |

## L-0055 — 2026-09-14 — reviewer C (revision 7) given the owner resolutions

| Field | Value |
|---|---|
| Iteration | architecture revision 7, Phase-1 review cycle 5 |
| Role | orchestrator (routing), concerning rot-reviewer-compat-transaction `AR-0021` |
| Input commit | `30542e5` |
| Work performed | Sent the running AR-0021 a message carrying owner input only. It is permitted to read exactly `GATES/OWNER-DESIGN-REQUIREMENTS-0002.md` and `.yaml` via `git show 30542e5` (not the ledger or state, which summarise reviewer B's findings). It is instructed to treat OT-1 and OT-2 as resolved, attack the resulting design within its scope, and disclose receipt. Reviewer B had already completed before the resolutions; its findings stand for synthesis adjudication. Added the -0002 record to immutable evidence. |
| Report / evidence | `AGENT_RUNS/AR-0021.run.yaml` (messages_received) |
| Verdict | — |
| Output commit | the commit adding this entry |
| Findings | — |
| Next action | await AR-0021 |

## L-0056 — 2026-09-14 — owner directive: freeze the RoT loop after revision 7

| Field | Value |
|---|---|
| Iteration | architecture revision 7, Phase-1 review cycle 5 (panel in progress) |
| Role | product owner (source); orchestrator (recording) |
| Input commit | `7b86bf3` |
| Work performed | Recorded OWNER-DIRECTIVE-0003 verbatim. It stops the Root-of-Trust revision loop after revision 7: no revision 8, and no architecture author after the verdict. Only in-flight revision-7 work completes: reviewer B's evidence preserved, reviewer C finishing, the planned synthesis reviewer, and recording of the final verdict. Rejected findings are recorded, not routed; acceptance is recorded without implementation or D-0008 activation. A complete durable checkpoint follows, with next action `PHASE_1_ROOT_OF_TRUST_LOOP_FROZEN_PENDING_META_ARCHITECTURE_REVIEW`. The state now carries `loop_status: FREEZING_AFTER_REVISION_7` and forbids revision 8, further authors, routing, implementation, key ceremony, the Capability Contract, Prompt 2, D-0008 activation and new owner options. The synthesis handoff template notes that the loop is frozen, without changing the reviewer's method. |
| Report / evidence | `GATES/OWNER-DIRECTIVE-0003-FREEZE-ROT-LOOP.md` (sha256 `b1b3aa1feace9d79…`), `CHECKPOINTS/CP-0018.yaml` |
| Verdict | — (owner directive) |
| Output commit | the commit adding these records |
| Findings | — |
| Next action | await AR-0021; merge the panel; run synthesis AR-0022; record the verdict; frozen checkpoint; stop |

## L-0057 — 2026-09-14 — revision-7 reviewer C completed; panel merged

| Field | Value |
|---|---|
| Iteration | architecture revision 7, Phase-1 review cycle 5 |
| Role | rot-reviewer-compat-transaction (`AR-0021`) |
| Input commit | `7e50c6e` (architecture `d07d200`); received OWNER-DESIGN-REQUIREMENTS-0002 mid-run (disclosed) |
| Work performed | Reproduced review-r6 C's `matrix6` (62,036 rows) and 11 probes byte-identical. Ran an independent matrix7 of 118,732 rows over real 4.1.2–4.1.5 with its own registers and predicate. Authored held-out RV7-C-A01…A25 (15 executed, 6 on the reference executor, 3+ design). |
| Report / evidence | `AGENT_RUNS/AR-0021.report.yaml`; `release/root-of-trust/4.1.6-review-r7/C-compat-transaction/` |
| Verdict | `BLOCKING_FINDINGS_PRESENT` (role verdict) |
| Output commit | work `34633cc`, report `d7b0850`, merged `2856bd7`. Reviewer B merged first: `733c2ba`. |
| Findings | **HIGH RV7-C-H1:** the running-mode C3 currency proof bounds the anchoring event age (≤ 24 h), not the Trust State's age; an air-gapped admitted machine performs production C3 on a state up to 90 days stale (executed: 882 h). This contradicts RS-1b and OWNER-DESIGN-REQUIREMENTS-0002 OT-1. **MEDIUM:** M1 (protected-store loss makes the next admission a first admission that discards the account-store high-water), M2 (per-project record identity not realizable), M3 (first-install journal never honoured), M4 (untracked in-migration overlay removable by `git clean`), M5 (roll-forward relies on in-memory state; stubbed in crashmig7). **LOW:** L1–L4. **Prior:** R2-H4 CLOSED as a class (0 violations over 118,732 rows); RV6-M3 and RV6-M4 narrowed; RV6-M5 closed. **Conformance:** OP-3, OP-15 and the exclusions conform; OT-1 conforms at admission and deviates at use; OP-14 (b) deviates on protected-store loss; D-0008 and D-0007 states hold. |
| Next action | planned synthesis reviewer AR-0022 (final under freeze) |

## L-0058 — 2026-09-14 — revision-7 synthesis handed off (final under freeze)

| Field | Value |
|---|---|
| Iteration | architecture revision 7, Phase-1 review cycle 5 |
| Role | orchestrator |
| Input commit | `2856bd7` |
| Work performed | Wrote HO-0022 from the v4 synthesis template. It carries owner records -0001 and -0002 as binding, the acceptance rule's owner-conformance clause (no certified target required if the criterion is explicit, testable and non-circular), the panel-timing fact and the freeze context note (findings are recorded as evidence, not routed). Claimed AR-0022. Added the review-r7 B and C directories to immutable evidence. |
| Report / evidence | `HANDOFFS/HO-0022-rot-review-r7-d-synthesis.md`, `CHECKPOINTS/CP-0019.yaml` |
| Verdict | — |
| Output commit | the commit adding these records |
| Findings | — |
| Next action | spawn AR-0022 |

## L-0059 — 2026-09-14 — final revision-7 synthesis reviewer spawned

| Field | Value |
|---|---|
| Iteration | architecture revision 7, Phase-1 review cycle 5 (final under OWNER-DIRECTIVE-0003) |
| Role | rot-review-synthesis (`AR-0022`, fresh Opus 5 context) |
| Input commit | `1d4d9f3` (worktree `wt/review-r7-d`, branch `phase1/rot1-r7-review-d`) |
| Work performed | Spawned on HO-0022; running. The prompt includes the freeze context (the verdict is recorded as evidence, not routed), owner records -0001 and -0002 as binding, the panel-timing fact, the transcript prohibition and the keep-turn-active instruction. |
| Report / evidence | expected `AGENT_RUNS/AR-0022.report.yaml`; `release/root-of-trust/4.1.6-review-r7/{00,10,11}*`, `D-synthesis/` |
| Verdict | pending |
| Output commit | pending |
| Findings | — |
| Next action | on completion: verify and merge; record the verdict and findings without routing; build the frozen evidence package and final checkpoint; set the frozen next action; stop |

## L-0060 — 2026-09-14 — revision 7 REJECTED by final synthesis (recorded, not routed)

| Field | Value |
|---|---|
| Iteration | architecture revision 7, Phase-1 review cycle 5 (final under OWNER-DIRECTIVE-0003) |
| Role | rot-review-synthesis (`AR-0022`) |
| Input commit | `1d4d9f3` (architecture `d07d200`; B `54be694`; C `34633cc`; owner records -0001 `fbd09d5`, -0002 `30542e5`) |
| Work performed | Reproduced the architect's 15 revision-7 instruments byte-identical, B's probes and C's probes and matrix7 (196 position aggregates equal after re-running P-TXN positions with resolved paths). Adjudicated B and C. Authored held-out RV7-D-A01…A10. Assessed conformance with both owner records. |
| Report / evidence | `AGENT_RUNS/AR-0022.report.yaml`; `release/root-of-trust/4.1.6-review-r7/{00-REVIEW-REPORT,10-BLOCKING-FINDINGS,11-CORRECTION-DELTA}.md`, `D-synthesis/` |
| Verdict | **`ROOT_OF_TRUST_ARCHITECTURE_REJECTED`** (final revision-7 verdict) |
| Output commit | review `4c7735b`, report `7c66d66`, merged `3e1442e` |
| Findings | **HIGH:** RV7-H1 (first-contact listing of restrictive facts), RV7-H2 (running-machine C3 currency of the named state). **MEDIUM:** RV7-M1…M10, of which M1–M4 are blocking. **LOW:** RV7-L1…L12. **INFO:** RV7-I1…I6. **Classes:** BC7-1…BC7-4 (BC7-4 and the OT-2 criterion part are materially new). **HO-0001:** §3.2 NOT SATISFIED; §3.1, §3.3 (as a class), §3.4 and §4 SATISFIED. **Owner records:** deviations from -0001 and -0002. **Routing:** NOT ROUTED — loop frozen. |
| Next action | freeze and final evidence package |

## L-0061 — 2026-09-14 — Root-of-Trust loop FROZEN; final evidence package

| Field | Value |
|---|---|
| Iteration | Phase 1 Root-of-Trust architecture loop — frozen after revision 7 |
| Role | orchestrator |
| Input commit | `3e1442e` |
| Work performed | Per OWNER-DIRECTIVE-0003: recorded the final revision-7 verdict and all findings without routing; set lifecycle_state and next_deterministic_action to `PHASE_1_ROOT_OF_TRUST_LOOP_FROZEN_PENDING_META_ARCHITECTURE_REVIEW`; emptied running_work; marked GATE-ARCH-ACCEPT frozen with its last verdict; added the review-r7 consolidated files and the directive to immutable evidence. Built the final evidence package with `tools/build_frozen_package.py` from committed records: `CHECKPOINTS/CP-FINAL-ROT-LOOP-FROZEN.yaml` and `ROT-1-FROZEN-EVIDENCE-PACKAGE.md`. No revision 8, no architecture author, no implementation, no D-0008 activation, no new owner options. D-0008 PROVISIONAL / PROPOSED / human_approved false / in_effect false; D-0007 ACTIVE and unchanged since Phase 1 start. |
| Report / evidence | `CHECKPOINTS/CP-FINAL-ROT-LOOP-FROZEN.yaml`, `ROT-1-FROZEN-EVIDENCE-PACKAGE.md` |
| Verdict | — (orchestration frozen) |
| Output commit | the commit adding these records |
| Findings | — |
| Next action | `PHASE_1_ROOT_OF_TRUST_LOOP_FROZEN_PENDING_META_ARCHITECTURE_REVIEW` |

## L-0062 — 2026-09-17 — owner adopts Signed Release Root rebase; fresh R0 review opened

| Field | Value |
|---|---|
| Iteration | new Signed Release Root lineage, before R0 review |
| Role | product owner (decision); governance recorder (records only) |
| Input commit | `09f8b4f13b76e19acef4612a0b985a14cfed350b` (completed forensic meta-review) |
| Work performed | Recorded OWNER-DIRECTIVE-0004 and active owner decision D-0009. Created separate provisional architecture lineage ARCH-0003 and `release/root-of-trust/signed-release-root-v1/`, including frozen R0/R1/R2/R3 boundary, owner OP-1…OP-16 dispositions and transition map. Retired CP-1 as the Phase-1 target without changing D-0008/ARCH-0002 or creating Revision 8. Preserved D-0007 ACTIVE. Updated the durable gate/state path and prepared HO-0023 for a fresh R0 reviewer. No implementation or review performed. |
| Report / evidence | `GATES/OWNER-DIRECTIVE-0004-SIGNED-RELEASE-ROOT-REBASE.md`; `spec/decisions/D-0009.yaml`; `spec/architecture/ARCH-0003.yaml`; `release/root-of-trust/signed-release-root-v1/`; `CHECKPOINTS/CP-0020.yaml`; `HANDOFFS/HO-0023-signed-release-root-r0-review.md` |
| Verdict | — (owner direction and architecture preparation, not an R0 verdict) |
| Output commit | the single governance/architecture rebase commit containing this entry |
| Findings | none; historical RoT-1 findings remain evidence and are not automatically R0 blockers |
| Next action | `FRESH_R0_ARCHITECTURE_REVIEW_OF_ARCH_0003_AT_COMMITTED_REBASE_CANDIDATE` |

## L-0063 — 2026-09-17 — fresh Phase-1 orchestrator session; R0 review AR-0023 dispatched

| Field | Value |
|---|---|
| Iteration | Signed Release Root (SRR-1) R0 review cycle 1 |
| Role | orchestrator (routing only) |
| Input commit | `5fd83583f36a32b045d3943dd5ee6f2c7a491822` |
| Work performed | New persistent orchestrator session self-located from committed state only. Verified: HEAD/branch reconcile with `ORCHESTRATOR_STATE.yaml` (`check_state.py verify` → `STATE_CONSISTENT`); repo-root Capability Acceptance Contract v3 present, SHA-256 `4c2df29115c8d5389034b2e2d817772add80d61678807c23e0d520c937cb5ed3`, no canonical import/lock exists yet so nothing to cross-verify; canonical operator UI unique at its recorded path with matching SHA-256 `54730e8e…`; frozen R0/R1/R2/R3 boundary `70977d11…` and OWNER-DIRECTIVE-0004 `26243019…` match their recorded digests; all seven reviewed candidate inputs byte-identical between the rebase record `2d78f6b` and HEAD, so the control-panel install commit does not alter the candidate. Landed on Phase 1 / R0 per the rebase landing rule (D-0009 / OWNER-DIRECTIVE-0004 / ARCH-0003 committed, `ROT_ARCHITECTURE_ACCEPTED_R0` absent). Read the V8.1 Phase-1 R0 card and its role prompt as a non-normative template and parameterized it with exact commits, paths and hashes. Dispatched one fresh isolated R0 reviewer (AR-0023) in worktree branch `phase1/srr1-r0-review`. No implementation, no Revision 8, no D-0008/ARCH-0002 change, no owner interruption. |
| Report / evidence | `AGENT_RUNS/AR-0023.run.yaml`; report pending at `AGENT_RUNS/AR-0023.report.yaml` |
| Verdict | — (orchestrator routes; the R0 verdict is the reviewer's alone) |
| Output commit | the commit containing this entry |
| Findings | — |
| Next action | `ADJUDICATE_AR_0023_R0_VERDICT__IF_NO_COMMITTED_AR_0023_REPORT_RERUN_A_FRESH_R0_REVIEW_AT_THE_SAME_CANDIDATE` |

## L-0064 — 2026-09-17 — R0 REJECTED for ARCH-0003 (AR-0023); one bounded correction cycle opens, blocked on an owner trade-off

| Field | Value |
|---|---|
| Iteration | Signed Release Root (SRR-1) R0 review cycle 1 |
| Role | fresh independent R0 architecture reviewer (AR-0023); orchestrator routing only |
| Input commit | `166ac4cff484160c7176e0ce15b23e59820074f2` (candidate `5fd8358`) |
| Work performed | Fresh isolated reviewer applied the frozen R0 boundary `70977d11…` to D-0009/ARCH-0003 and the `signed-release-root-v1` pack. It verified the owner directive, frozen boundary and Contract v3 digests, ran 16 mandatory attacks (13 refuted) and dispositioned the fourteen frozen R0 items (9 satisfied, 1 thin, 4 not satisfied). Orchestrator verified the evidence independently before merging: both commits exist, the report names the work commit, only review paths changed, and D-0007/D-0008/ARCH-0002/D-0009/ARCH-0003 and the candidate pack are byte-identical at the branch tip. Evidence merged unmodified with `--no-ff`. |
| Report / evidence | `AGENT_RUNS/AR-0023.report.yaml`; `release/root-of-trust/signed-release-root-v1-review-r0/` (00 report, 10 blocking findings, 11 correction delta, 20 later-lifecycle conditions, evidence/) |
| Verdict | **`ROT_ARCHITECTURE_REJECTED_R0`** — the reviewer's alone; the orchestrator issued none |
| Findings | **R0 blockers (2):** `SRR-R0-H1` HIGH, NECESSARY-DERIVED, frozen items 5 and 8 — signed floors are lexically scoped to the `rollback` ingress while `recovery` admits a floor-free, non-metadata-authenticated restore; falsifies the candidate's own one-policy-across-ingresses and floor-refusal claims. `SRR-R0-M1` MEDIUM, OWNER-ADDED-NORMATIVE, frozen items 10 and 12 — no time/clock assumption or non-guarantee is declared although the whole expiry/freshness/stale-honesty model is evaluated against it. **Non-blocking later-lifecycle (9):** L1–L5, L7 (R1), L6 (R1/R2), L9 (R2), L8 (INFO) — recorded and removed from the active repair queue. Three stronger-assurance proposals recorded as non-binding, none routed into the delta. |
| Adjudication | Active R0 repair queue is exactly `SRR-R0-H1` and `SRR-R0-M1`. Correction delta CD-R0-1/CD-R0-2 is text-level across `ARCH-0003.yaml` and `00-ARCHITECTURE.md`; it changes no trust chain, metadata model, ingress set or transaction invariant. The single permitted bounded R0 correction cycle is unused. CD-R0-1 carries a genuine owner security-versus-availability trade-off, so no architecture role is dispatched until the owner answers. |
| Output commit | aa72e5062a72bd74fcd3dc36fca06605a33d00a7 (merge); review work `2dc08c2`, report `024057f` |
| Next action | `AWAIT_OWNER_ANSWER_ON_GATE_OWNER_R0_BELOW_FLOOR_RECOVERY` then the single permitted bounded R0 correction cycle in a fresh isolated architecture role, then a new fresh R0 reviewer |

## L-0065 — 2026-09-17 — owner selects break-glass; the single bounded R0 correction cycle opens

| Field | Value |
|---|---|
| Iteration | SRR-1 bounded R0 correction cycle 1 of 1 |
| Role | product owner (decision); orchestrator (routing only) |
| Input commit | `6a2fcb3bf61362826345a905c9afa12a6691a1e3` |
| Work performed | Recorded `OWNER-DECISION-0006`: below-floor recovery is **(b) break-glass**, authorised and recorded — an authentic Governance OS release only, under an owner-controlled local/out-of-band authority that repository content, environment variables, caller fields, plugins and model output cannot manufacture; durably recorded on entry; the machine marked `DEGRADED — RECOVERY ONLY`; normal privileged operation, Human Gate creation/approval, certification, trust-policy mutation, privileged plugin/profile acquisition and floor reset all forbidden below floor; the signed floor never lowered; the floor rule governing every backward-capable privileged ingress; and network access explicitly not the sole authority. `GATE-OWNER-R0-BELOW-FLOOR-RECOVERY` moved to SATISFIED, unblocking CD-R0-1. Prepared HO-0024 and dispatched one fresh isolated architecture-correction role (AR-0024) scoped to exactly `SRR-R0-H1` and `SRR-R0-M1`, forbidden from touching the frozen boundary, D-0009/D-0007/D-0008/ARCH-0002, review evidence or product source, and forbidden from grading its own work. |
| Report / evidence | `GATES/OWNER-DECISION-0006-BELOW-FLOOR-RECOVERY.md`; `HANDOFFS/HO-0024-srr1-r0-bounded-correction.md`; `AGENT_RUNS/AR-0024.run.yaml` |
| Verdict | — (owner decision and routing; no architecture verdict) |
| Output commit | the commit containing this entry |
| Findings | — |
| Next action | complete AR-0024, then dispatch a NEW fresh independent R0 reviewer scoped to the corrected text and `OWNER-DECISION-0006` |

## L-0066 — 2026-09-17 — bounded R0 correction applied (AR-0024); fresh R0 re-review dispatched

| Field | Value |
|---|---|
| Iteration | SRR-1 bounded R0 correction cycle 1 of 1, then R0 review cycle 2 |
| Role | fresh isolated architecture-correction role (AR-0024); orchestrator routing only |
| Input commit | `73227a1594265743b18eb7115394d639e6c659a2` |
| Work performed | AR-0024 applied CD-R0-1 and CD-R0-2 only. **CD-R0-1:** the floor rule is now stated over the ingress set — no `init`, `adopt`, `update`, `reinstall`, `rollback` or `recovery` may place the machine below its protected high-water or the signed minimum secure release; `recovery`'s installed-integrity object is qualified as establishing *intact*, never *admissible*; offline authenticity derives from the machine's own protected record of the release it previously verified, never from the manifest, lock or repository; below-floor recovery is stated as owner-authorised break-glass with all ten OWNER-DECISION-0006 requirements in architecture text; and the revoked-binary allowance is reconciled so a revoked binary can neither re-establish itself nor issue its own break-glass entry. **CD-R0-2:** the local time source is declared inside the trusted local boundary on the OS/admin side, with a two-directional non-guarantee bounded to freshness (no floor lowered, no unauthorised release admitted, verified-byte binding intact), no claim of unseen future revocations, a conditional currency-honesty claim, and excluded time mechanisms named as excluded. Orchestrator verified before merging: exactly the three permitted files changed; frozen boundary re-hashed byte-identical; D-0007/D-0008/D-0009/ARCH-0002, packs 02/03, review evidence and Contract v3 unchanged; candidate still PROVISIONAL / not in effect / not human-approved. No new owner trade-off surfaced. |
| Report / evidence | `AGENT_RUNS/AR-0024.report.yaml`; `release/root-of-trust/signed-release-root-v1/04-R0-CORRECTION-1.md` |
| Verdict | `ARCHITECTURE_CORRECTION_READY_FOR_REVIEW` — the correction did not grade itself |
| Output commit | d34478aa945617a93b1c962fcc363b1c3f835ab3 (merge); correction `29516f8`, report `032ffbb` |
| Findings | AR-0024 disclosed one judgement call: `SRR-R0-L8` not fixed, two traceability rows re-pointed because their target sections moved. Routed to AR-0025 to verify. |
| Next action | AR-0025 fresh independent R0 re-review; on acceptance continue automatically into R1, on rejection stop with `R0_OWNER_READJUDICATION_REQUIRED` |

## L-0067 — 2026-09-17 — R0 ACCEPTED for the corrected ARCH-0003 (AR-0025); R1 build dispatched

| Field | Value |
|---|---|
| Iteration | SRR-1 R0 review cycle 2, then R1 implementation |
| Role | NEW fresh independent R0 reviewer (AR-0025); orchestrator routing only |
| Input commit | `2b36b440915f0052d92153748cea914846955418` |
| Work performed | AR-0025 re-reviewed the corrected candidate against the frozen boundary. It re-ran AR-0023's probes rather than trusting the correction record: PR-5's five floor statements are all replaced and each of the six counterexample steps is blocked by named text; PR-3's time sweep went from 0 matches to 14. It authored 16 fresh held-out attacks (NA-1…NA-16), of which 14 passed clean and 2 produced new non-blocking R1 conditions. Notable results: break-glass relaxes only the floor check, never authenticity; all five owner-named manufacturing classes are excluded plus self-authorisation by a below-floor or revoked binary; no revoked-binary re-establishment loop; no deadlock, since restoration is explicitly permitted; the `DEGRADED — RECOVERY ONLY` token is byte-identical to the owner's at all five sites; the offline authenticity basis is not circular, flowing metadata → verification → protected machine state; and the wrong-clock claim holds because both floors are anchored to monotonic version state rather than to time. All ten OWNER-DECISION-0006 requirements were verified directly in architecture text in both documents, requirement 2 being a superset of the owner's. Orchestrator verified independently before merging: the reviewer added only its six evidence files, and ARCH-0003, 00-ARCHITECTURE.md, the frozen boundary, D-0007, D-0009 and Contract v3 are byte-identical at the review tip. |
| Report / evidence | `AGENT_RUNS/AR-0025.report.yaml`; `release/root-of-trust/signed-release-root-v1-review-r0-2/` — `10-BLOCKING-FINDINGS.md` present and explicitly empty |
| Verdict | **`ROT_ARCHITECTURE_ACCEPTED_R0`** — 14 of 14 frozen R0 items SATISFIED, 6 strengthened, none weakened; `SRR-R0-H1` and `SRR-R0-M1` both CLOSED, neither residual |
| Findings | No R0 blocker, residual or new, so no owner readjudication triggered. Non-blocking R1: `SRR2-R1-C1` (MEDIUM, owner question — break-glass exit clears on the minimum secure release alone while "below floor" spans two floors), `SRR2-R1-C2` (MEDIUM — bind the offline record to verified digests, not the version), `SRR2-R1-C3` (LOW — floor durability across uninstall). `SRR-R0-L8` carried INFO; its two re-points verified accurate. `SRR-R0-L6`/`L7` correctly not reopened. |
| Gate | `GATE-R0-ARCH-ACCEPT` **SATISFIED**. `ARCH-0003` annotated `review_state: R0_ACCEPTED` with the accepted digests; architecture **body verified byte-identical** before and after annotation; `status: PROVISIONAL`, `in_effect: false`, `human_approved: false` unchanged, since R0 acceptance authorises no implementation by itself and implies no owner adoption. `GATE-OWNER-CAC-UPLOAD` marked SATISFIED with a **logged precedence conflict**: the gate expected an owner copy into `framework/contracts/source/` after builder scaffolding, but the owner supplied the source at the repo root and directed that it be used and hash-bound; an active owner directive outranks a frozen gate convention, so the root file is authoritative and the destination copy becomes a builder-produced canonical import bound to it. |
| Output commit | 7858b6d7ce750ebcd2e2e3acbb48101eebd917d5 (merge); review work `5635955`, report `57294b9` |
| Next action | AR-0026 R1 build under HO-0026, then a NEW fresh independent R1 verifier and the automatic repair/reverification loop until `ROT_PHASE1_CANDIDATE_ACCEPTED_R1` |
| Owner question routed | `GATE-OWNER-R1-BREAK-GLASS-EXIT` (non-blocking). R1 proceeds under the orchestrator's recorded fail-safe interim: exit requires at-or-above **both** floors, implemented as one isolated policy point the owner can flip. Recorded as an assumption, not an owner answer. |

## L-0068 — 2026-09-18 — R1 implementation built (AR-0026); candidate 1 minted; independent verification dispatched

| Field | Value |
|---|---|
| Iteration | SRR-1 R1 implementation, candidate 1 |
| Role | fresh isolated builder (AR-0026); orchestrator routing only |
| Input commit | `1e31f6b5cb4e112d4ec86b45839e093c7b50d687` |
| Work performed | Implemented the R0-accepted ARCH-0003. Verification uses **ed25519-dalek 2.2.0** (`verify_strict`) over the exact bytes of the `signed` member via `serde_json::value::RawValue`, so the verified byte-string and the parsed policy are provably the same document; the builder implemented the TUF **role model** explicitly rather than adopting a fixed client crate, because the release role must bind product/repository identity, channel, monotonic sequence, payload digests, schema and migration identities and the minimum secure release. `kernel::install_kernel` now takes an `AuthenticatedRelease` constructible **only** by `srr::verifier::admit` and has no path-taking variant, so the no-bypass property is enforced by the compiler; all six privileged ingresses route through it. Three separately durable monotonic floors live in protected machine state **outside every repository**; the effective floor is checked inside the one verifier, so it binds every ingress. Break-glass authority is an owner-signed `recovery`-role token, machine-bound, single-use nonce, payload-digest-bound, dropped out of band into a protected inbox — env vars are refused outright, `--break-glass` only *requests*, and the running binary holds no signing key. `SRR2-R1-C1` sits at exactly one function (`breakglass::exit_satisfied`, flag `EXIT_POLICY`) at the stricter both-floors interim. Contract v3 scaffolding is hash-bound to the owner root source and fails closed on divergence. New `gov trust` and `gov contract` surfaces. |
| Report / evidence | `AGENT_RUNS/AR-0026.report.yaml`; `release/root-of-trust/signed-release-root-v1-r1-build/` (build report, requirement-to-code map, test output, digests) |
| Verdict | `READY_FOR_INDEPENDENT_OS_VERIFICATION` — readiness only; the builder issued no acceptance token |
| Orchestrator verification | No prohibited path touched; no private-key filenames or key blocks; canonical contract import byte-identical to the owner source at `4c2df291`; ARCH-0003 body unchanged; **regression independently reproduced** — `cargo test --lib` 26 passed / 0 failed, `cargo test --test certification` 64 passed / 0 failed, exit 0. The builder's figures match exactly. |
| Findings | Five residuals disclosed rather than concealed, all routed to the independent verifier for judgement: RES-1 unprovisioned posture (floors advance only from `Authentic`, so a never-verified machine enforces no release floor); RES-2 protected-state relocation by an owner-privileged process, resting on the ARCH-0003 §1 trusted boundary; RES-3 expiry as a lexicographic RFC-3339 comparison at second precision; RES-4 delegated targets verified and enforced but with no issuing tooling, so a privileged remotely-acquired capability has no admission path — which bears directly on whether `SRR-R0-L6` is genuinely closed; RES-5 certification harness now isolates `XDG_STATE_HOME` per scenario. No `todo!()`, no stub, no path that appears to verify but does not. |
| Correction recorded | `42681978` had been logged as the ARCH-0003 *body* digest; it is the whole-file digest at the acceptance commit. Disclosed by AR-0026. The body scalar digest is `093cb78e`, byte-identical at the acceptance commit and at HEAD, so the accepted architecture text is unchanged by the post-verdict annotation. State corrected; CP-0025 retains the original label as a point-in-time snapshot. |
| Output commit | 229d1543be0357b52f7c7e6405918171bc8e6631 (merge), tagged `srr1-r1-candidate-1`; builder work `949c4d3`, report `cedb3e6` |
| Next action | AR-0027 fresh independent R1 verification under HO-0027; on acceptance Phase 1 completes, on blocking findings the automatic repair/reverification loop runs, and any `REQUIRES_R0_OR_OWNER_ADJUDICATION` finding stops for the owner |

## L-0069 — 2026-09-18 — R1 candidate 1 REJECTED (AR-0027); bounded repair 1 dispatched

| Field | Value |
|---|---|
| Iteration | SRR-1 R1 verification 1, repair cycle 1 |
| Role | fresh independent R1 verifier (AR-0027); orchestrator routing only |
| Input commit | `0ce7f9f0a7028d54bc5beef57f0ef35a935e244d` (candidate `srr1-r1-candidate-1`) |
| Work performed | AR-0027 authored **29 held-out tests in a standalone cargo crate outside the product tree and its workspace**, depending on `gov-runtime` by path, so verification required no product edit — confirmed by an empty diff over `runtime/`, `cli/`, `tests/`, `framework/`, `spec/` and the Cargo files. All twelve crypto/TUF adapter attacks failed closed, including signature-over-different-document, role confusion against timestamp and snapshot keys, threshold-by-repetition, four trailing-byte variants, duplicate `signed` member and a malleated non-canonical `S`. The transaction-abort path was probed and confirmed **not** a bypass: `rollback_internal` is private with two callers, `transaction_abort` occurs only in the error arm, `admit` has already passed, and `record_installed` is never called so no floor advances. Floor refusal was demonstrated at **all six** ingresses, not just `rollback`. Regression reproduced exactly at 26 lib and 64 certification tests. |
| Report / evidence | `AGENT_RUNS/AR-0027.report.yaml`; `release/verification/4.1.6-r1/` including the held-out test sources |
| Verdict | **`BLOCKING_FINDINGS_PRESENT`** — 11 of 12 frozen R1 criteria SATISFIED |
| Blocking finding | `AR27-B1` (MEDIUM, `OWNER-ADDED-NORMATIVE`, R1, **not** requiring R0 or owner adjudication): `OWNER-DECISION-0006` §6 bullet 1 is enforced as a 26-string substring deny-list, so any unlisted operation proceeds on a machine marked `DEGRADED — RECOVERY ONLY`. Measured across all 35 `guard_write` labels: 23 refused, 12 permitted, of which **seven are normal privileged governed operation** covered by no §5 activity — `cit approve`, `cit reject`, `gate revoke`, `handoff return`, `plugins unregister`, `adopt extract-legacy`, `adopt build-memory`. It also falsifies the module's own documented "default is refuse" claim and its requirement map. |
| Residual judgements | RES-1 unprovisioned posture **accepted** — the latch is never cleared, so an adversary cannot return a machine to it inside the declared boundary. RES-2 protected-state reliance **sound, not circular** — `GOV_MACHINE_STATE_DIR` is genuinely refused on a provisioned machine, and ARCH-0003 §1 independently disclaims hostile-admin protection. RES-3 expiry a **real but non-blocking defect** (`AR27-N1`). RES-4 **`SRR-R0-L6` genuinely closed** — `OWNER-DECISION-0005` asks R1 to distinguish the classes and decide how delegated targets apply, and both limbs are met; issuing tooling is R2 by the frozen boundary, and treating its absence as a blocker would be exactly the promotion the owner forbade. RES-5 harness **clean against history** — 2026 insertions and **0 deletions** across the test tree, so no assertion could have been weakened; 49 pre-existing scenarios pass unmodified. |
| Adjudication | Active R1 repair queue: `AR27-B1` (mandatory) plus same-gate `AR27-N1`, `AR27-N2`, `AR27-N4`, which the verifier recommended for this cycle as local to the same files. R2-lifecycle `AR27-N3`, `N5`, `N6`, `N7` recorded and removed from the active queue. `SRR2-R1-C1` stays at its interim; `SRR-R0-L7` stays absent. Blocker class **BC-R1-1** recorded; consecutive new-class count 1 of 3. |
| Owner adjudication routed | `AR27-OD1` → `GATE-OWNER-R1-MACHINE-STATE-ANCHOR`, flagged `REQUIRES_R0_OR_OWNER_ADJUDICATION` and explicitly **not** routed to repair: anchoring protected machine state to a fixed machine-domain path would change the accepted R0 bootstrap assumption and collides with the certification harness's own isolation mechanism. Non-blocking for repair 1. |
| Output commit | d10c2a552f71462209f53977d272eaf38a35f93f (merge); verification work `26c2dc5`, report `6bb62cb` |
| Next action | AR-0028 bounded repair under HO-0028, then candidate 2 and a NEW fresh independent verifier rerunning AR-0027's held-out tests plus fresh ones |

## L-0070 — 2026-09-18 — owner answers both open R1 questions; no R0 readjudication

| Field | Value |
|---|---|
| Iteration | SRR-1 R1 repair cycle 1 (running) |
| Role | product owner (decisions); orchestrator (records only) |
| Input commit | `a271eedc2bfd545fdfc2042f355631b81fd46ecd` |
| Work performed | Recorded `OWNER-DECISION-0007`. **`AR27-OD1`:** keep the current derivation of protected machine state from `XDG_STATE_HOME`/`HOME`; it is not anchored to a fixed machine-domain path. The accepted R0 bootstrap/trusted-boundary assumption is therefore unchanged, **`R0_OWNER_READJUDICATION_REQUIRED` is not triggered**, `GATE-R0-ARCH-ACCEPT` stands, and the certification harness keeps its per-scenario isolation. The residual asymmetry — `GOV_MACHINE_STATE_DIR` refused on a provisioned machine while `HOME`/`XDG_STATE_HOME` relocation by an owner-privileged process remains possible and in-boundary under ARCH-0003 §1 — is now an owner-adjudicated position rather than a defect, and may not be raised as an R1 blocker. **`SRR2-R1-C1`:** keep the stricter reading — exit from `DEGRADED — RECOVERY ONLY` requires a verified authenticated release at or above **both** the signed minimum secure release and the protected local high-water. This confirms the orchestrator's fail-safe interim rather than changing it, so **no code change is required**; `EXIT_POLICY = "b_stricter_both_floors"` is now owner-decided policy. It supplements `OWNER-DECISION-0006` requirement 7, whose floor is necessary but not sufficient for clearing the marking. Both owner gates moved to SATISFIED; no owner gate is now pending. The running repair AR-0028 needed no redirection, because HO-0028 already forbade touching machine-state path resolution and required the interim to stand. |
| Report / evidence | `GATES/OWNER-DECISION-0007-R1-QUESTIONS.md` (SHA-256 `4a0f61c0…`) |
| Verdict | — (owner decisions; no gate verdict) |
| Output commit | the commit containing this entry |
| Findings | `AR27-OD1` and `SRR2-R1-C1` both CLOSED by owner decision |
| Next action | unchanged — complete AR-0028, mint candidate 2, dispatch a NEW fresh independent verifier |

## L-0071 — 2026-09-18 — bounded R1 repair 1 complete (AR-0028); candidate 2 minted; re-verification dispatched

| Field | Value |
|---|---|
| Iteration | SRR-1 R1 repair cycle 1, then verification iteration 2 |
| Role | fresh isolated repair role (AR-0028); orchestrator routing only |
| Input commit | `7a2ebcfad6cd54375dd0b2b214e51d94ce48ebdc` |
| Work performed | **`AR27-B1` closed by inversion, not extension.** `guard` and `guard_light` now decide through `permitted_activity(operation) -> Option<&'static str>`, an exact-match allow-list derived from `OWNER-DECISION-0006` §5 where `None` means refuse — so nothing is consulted in order to refuse and an operation added tomorrow is refused by construction. `REFUSED_OPERATIONS` is renamed `REFUSAL_CLASSES` and **decides nothing**: it only selects which §6 bullet a refusal is reported under. `REFUSAL_POLICY = "allow_list_default_refuse"` names the shape in one checkable place. The below-floor permitted set is four operations, each mapped to a §5 activity: `checkpoint` (backup/export), `kernel reinstall` (uninstall/reinstall), `update --apply` and `update --rollback` (restoration of an authenticated release). A marking record that exists but cannot be read now **refuses** (`Marking::Unreadable`) rather than returning `Ok`, with the allow-list consulted before any state read so the exit path stays open. **`AR27-N1`** closed by a canonical-form expiry gate failing closed on absent, non-canonical or stale values. **`AR27-N2`** closed by removing the false claim and naming `ROOT_EXPIRY_PROFILE`, on the evidence that `provision` refuses to re-anchor a provisioned machine, so barring an expired root from signing its successor would make root rotation permanently impossible. **`AR27-N4`** closed by making `crypto::verify` strict-only and removing the permissive trait import. The falsified doc comment and requirement-map row are corrected. |
| Report / evidence | `AGENT_RUNS/AR-0028.report.yaml`; `release/root-of-trust/signed-release-root-v1-r1-repair-1/` |
| Verdict | `READY_FOR_INDEPENDENT_OS_VERIFICATION` — readiness only; the repair did not grade itself |
| Orchestrator verification | Exactly the declared files changed. `runtime/src/srr/state.rs` is **absent from the diff**, so `AR27-OD1` was neither implemented nor partially implemented and machine-state path resolution is unchanged. `exit_satisfied` is **byte-identical** (function-body SHA-256 matches before and after) so the owner's stricter exit policy is preserved, and `EXIT_POLICY` is untouched. AR-0027's held-out test sources are **byte-identical**, so prior verification evidence was not tampered with. No `release/verification`, `*-review*`, `release/releases`, spec or owner-record path touched. **Regression independently reproduced: `cargo test --lib` 31 passed / 0 failed, `cargo test --test certification` 65 passed / 0 failed, exit 0** — matching the repair's figures exactly. |
| Findings | Three judgement calls routed to AR-0029 rather than accepted: the allow-list is **narrower** than AR-0027 suggested (`task status` and `cit simulate` refused because both mutate in code — `tasks::set_status` behind `mutate_task_status`, and `cit simulate` writing `cit_status = SIMULATED`), justified on §5 being permissive while §6 is a MUST NOT; the `AR27-N2` disposition removes a claim rather than implementing a control; and `Marking::Unreadable` refusing introduces a deadlock risk if the exit path were ever gated behind a state read. INFO items `AR28-R1`/`R2`/`R3` recorded, including a now-stale sentence in the candidate-1 build report deliberately left unedited as historical record. |
| Evidence invalidation | AR-0027's verdict now applies only to candidate 1; AR-0026's regression figures are superseded. **Not** invalidated: the R0 acceptance (no architecture document changed), AR-0027's held-out test sources (byte-identical and rerunnable, with three `OBSERVED` assertions expected to flip), and the historical verification packs. |
| Output commit | 678402feacdf47235dba794e5b6c663cc5655dcd (merge), tagged `srr1-r1-candidate-2`; repair work `4c7c40c`, report `60767bb` |
| Next action | AR-0029 fresh independent re-verification under HO-0029 — a different verifier from AR-0027, required to confirm the class property, judge both judgement calls, rerun AR-0027's held-out tests and author fresh ones |

## L-0072 — 2026-09-18 — candidate 2 REJECTED (AR-0029): repair 1 converged, a new class surfaced one level deeper

| Field | Value |
|---|---|
| Iteration | SRR-1 R1 verification iteration 2, repair cycle 2 |
| Role | NEW fresh independent verifier (AR-0029, not AR-0027); orchestrator routing only |
| Input commit | `2baff074095532d0e7ff42dad2f6fa316f771207` (candidate `srr1-r1-candidate-2`) |
| Work performed | AR-0029 authored 35 held-out tests in a standalone crate with an **independently written forge sharing no line with AR-0027's**, and reran AR-0027's suite byte-identical. It confirmed **`AR27-B1` is structurally closed**: exact match held against **63 near-miss forms with zero permitted** — case, whitespace, tab, newline, NUL, `gov ` prefix, NBSP, em dash, a Cyrillic homoglyph, truncations, `--force` and `-unverified` suffixes — and a sweep of all 28 labels reaching a break-glass guard permits exactly the four §5 operations, with all seven `AR27-B1` operations now refused. `REFUSAL_CLASSES` is inert. `AR27-N1`, `N2` and `N4` are closed. It then asked the question the repair had not: **is the guard on the path at all?** |
| Report / evidence | `AGENT_RUNS/AR-0029.report.yaml`; `release/verification/4.1.6-r1-2/` including its held-out sources |
| Verdict | **`BLOCKING_FINDINGS_PRESENT`** — 12 of 12 frozen R1 items SATISFIED (R1-9 qualified); `OWNER-DECISION-0006` §6 **partly** satisfied |
| Blocking findings | `AR29-B1` (MEDIUM, §6 bullet 4) — `provision::root_update` calls **no guard at all**; measured end to end on a degraded machine, `gov trust root-update` returned `Ok(true)`, the anchor advanced 1 → 2, a key was revoked and the high-water advanced, while the machine stayed marked. The guard *would* refuse it — `permitted_activity` is `None` and `REFUSAL_CLASSES` maps that very label to `trust_policy_mutation` — but nothing asks it. `AR29-B2` (MEDIUM, §6 bullet 2) — `gates::create_system` (line 143) creates Human Gates with no guard, unlike its guarded sibling `gates::create` (line 132); reachable below floor via `kernel kernel override` and, more awkwardly, from **inside** the allow-listed `update --apply`. Orchestrator confirmed both in source. |
| Classification | Both are **materially new** — blocker class **BC-R1-2, guard COVERAGE**, distinct from BC-R1-1 which was the guard DECISION shape. Why AR-0027 missed them: its sweep pushed operation *labels* through `guard_light` directly, and eight of those labels have no guard call site anywhere in the product, so refusing a label proved nothing about an operation. |
| Judgement calls resolved | **Deadlock risk: repair 1's claim was half right.** Restoration stays open under an unreadable marking, but *exit* does not — `try_exit` goes through `Degraded::load`, which reads the same record with the opposite disposition, so a machine above both floors still refuses while `gov trust status` reports `degraded: null`. Two readers of one record disagree. Graded LOW/non-blocking (`AR29-C1`) with reasons stated, and labelled a **residual** of `AR27-B1`. **Narrower allow-list: reasoning holds, nothing stranded** — all 27 `guard_write` labels enumerated from source, none is a read surface. **`ROOT_EXPIRY_PROFILE`: sound and measured, not accepted** — rotation is genuinely impossible under the alternative, since `root_update` requires the outgoing quorum and `provision` refuses to re-anchor. |
| Correction to a previously reported claim | `AR29-N1`: "constructible only by `admit`" is an **enumeration property, not a type property** — every field of `AuthenticatedRelease`, `Staged`, `MachineState` and `Floors` is `pub`, so a struct literal outside the module compiles; AR-0029's test is one. The 5/5 call-site census is what actually holds. AR-0027's "no public constructor" and the repair's preservation row overstate it, and the orchestrator repeated that overstatement upward. Routed into repair 2 with sealing preferred, so the claim becomes true. |
| Adjudication | Active R1 repair queue: `AR29-B1`, `AR29-B2` (blocking) plus `AR29-C1`, `AR29-N1`, `AR29-N3`, `AR29-N4`, `AR29-N5`. R2-lifecycle `AR29-N2` and the four carried `AR27-N*` items stay out. Required fix shape is **a single enforcement point every trust-changing and gate-creating path must pass, plus a path-enumerating coverage test** — not two bolted-on guard calls, which would close the instances and leave the class open. |
| Convergence | New-class count **2**; iterations that failed to close their assigned queue: **0**. Iteration 2 closed its assignment completely, so the protocol's literal "instead of closing" condition is not met — but the orchestrator treats the new-class count as operative and will **stop with `PHASE_CONVERGENCE_ESCALATION_REQUIRED` if iteration 3 produces another materially new class**, rather than rationalise a third away. |
| Output commit | 1bc4427d0f9ceba0da23892d5897cdfc863e2cee (merge); verification work `d3f52c6`, report `fcc7bd8` |
| Next action | AR-0030 bounded repair 2 under HO-0030, then candidate 3 and a NEW fresh independent verifier |
