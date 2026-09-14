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
