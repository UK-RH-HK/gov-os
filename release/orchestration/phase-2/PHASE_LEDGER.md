# Phase 2 ledger — Governance Capability Baseline

Append-only, human-readable chronology. Entry IDs are `P2-L-NNNN`. Facts, evidence references, verdicts and next
actions only.

## P2-L-0001 — 2026-09-18 — Self-location: Phase 2 — GOVERNANCE CAPABILITY BASELINE

| Field | Value |
|---|---|
| Role | Phase-2 outer orchestrator (routing, adjudication of provenance, durable state). Issues no verdict. |
| Input commit | `3374db452008628074824faacb030ad841ce4ed9` on `release/4.1.6-rc1`, working tree clean |
| Method | Committed state and evidence only. The launcher's assertion that Phase 1 passed was **not** trusted; it was checked. |
| R0 | `ROT_ARCHITECTURE_ACCEPTED_R0` — AR-0025, work `5635955`, report `57294b9`, evidence `release/root-of-trust/signed-release-root-v1-review-r0-2/` (`00-REVIEW-REPORT.md` §`ROT_ARCHITECTURE_ACCEPTED_R0`; `10-BLOCKING-FINDINGS.md` empty). All cited commits exist and are ancestors of HEAD. |
| R1 | `ROT_PHASE1_CANDIDATE_ACCEPTED_R1` — AR-0033 (`verifier-d`, independent of the build and all three repairs), work `5c4a4eb`, report `6dc1b0a`, evidence `release/verification/4.1.6-r1-4/`, `10-BLOCKING-FINDINGS.md` present and explicitly empty. Candidate `srr1-r1-candidate-4` = `c7d3fef` = tag `srr1-r1-accepted` (annotated). |
| Reconciliation | AR-0033 verified at worktree HEAD `84b9ee8`; `c7d3fef..84b9ee8` touches only three Phase-1 orchestration files. `c7d3fef..3374db4` touches only `README.md`, `docs/DECISIONS.md`, ARCH-0003 adoption metadata and orchestration records. New `product_identity.py`: `product_code_digest` `bd4d65d9…0547` at both `c7d3fef` and `3374db4`. |
| ARCH-0003 | `status: ACTIVE`, `in_effect: true`, `human_approved: true`, `approval_state: OWNER_ADOPTED`, record `OWNER-DECISION-0009` (SHA-256 `a0d3325f…` matches CP-0034). Body SHA-256 `093cb78e…` identical at the R0-accepted commit `2b36b44`, at `c7d3fef` and at HEAD — adoption changed metadata only. |
| Contract v3 | Root owner source SHA-256 `4c2df291…5ed3`. Canonical import byte-identical. `gov contract verify` → `CONTRACT_SOURCE_BOUND`, 100 compiled capability IDs. The lock's `compiled_sha256` (`30cec97c…`) differs from the compiled file's byte digest (`3bc27e10…`) **by design**: it is `util::hash_value`, a canonical-JSON digest of the parsed YAML (`runtime/src/contracts.rs:153`). Not a conflict. |
| Control panel | V8.2 SHA-256 `6fecfb6b…8269c` = owner-expected value; `NON_NORMATIVE_OPERATOR_UI`; V8.1 retained as labelled historical evidence; no competing canonical copy. |
| Phase-1 state | `check_state.py verify` → `STATE_CONSISTENT`. |
| Regression reproduced | `cargo build --release` ok; `cargo test --lib` **42 passed / 0 failed**; `cargo test --test certification` **79 passed / 0 failed** at `3374db4`. |
| Earliest unearned target | `GOVERNANCE_CAPABILITY_BASELINE_ACCEPTED` → **Phase 2**. No `PHASE_STATE_CONFLICT`. |

## P2-L-0002 — 2026-09-18 — Phase 2 initialised; gate contract frozen; iteration-0 audit prepared

| Field | Value |
|---|---|
| Work performed | Created `release/orchestration/phase-2/` (state, ledger, gate register, agent-run schema, handoffs, checkpoints, tools). Phase-1 state untouched. |
| Frozen gate contract | `GATES/PHASE-2-FROZEN-GATE-CONTRACT.md`, SHA-256 `d2f33e89…f25e`, frozen **before** any dispatch. Compiles Contract v3's pre-advanced-qualification items 1–9 verbatim plus the status, evidence, freshness, authority-model and O3 rules into **AC-1…AC-16**. Adds no product requirement. |
| Logged interpretations | §9.1 item 7 (provisional retrieval profile) — satisfied at Phase 2 by an executable path to establish a provisional profile, with selection earned in Phase 3 before any qualification repository executes; derived from Contract v3's own PROPOSED ORDER and V8.2's Phase 3 card. §9.2 oracle-format acceptance by a fresh independent reviewer. §9.3 R1 re-verification applied as AC-14 R1-preservation per changed candidate. §9.4 Gate U in the audit universe despite having no numbered heading. All four are owner-overridable. |
| V8.2 conflicts logged | `P2-CONFLICT-1` (CAP-1 "R1 verification again") and `P2-CONFLICT-2` (Phase-3 ordering vs item 7), each resolved by precedence in the frozen contract. |
| Audit design | Iteration 0 is exhaustive. Six fresh independent family auditors in parallel, partitioned so each capability has exactly one owner: **alpha** A/B/S/T; **beta** C/D/R (+AC-7); **gamma** E/F/G/H/I; **delta** J/K/L/M/N; **epsilon** O/P/Q/U/V (+AC-5 scheduler, +AC-6 oracle format); **zeta** W (+AC-8 artifact-flow matrix). A seventh fresh synthesis auditor then assembles all six and checks the cross-cutting criteria and issues the verdict. Bullet-level evaluation; executable evidence required; probes kept outside the product tree. |
| Handoffs | `P2-HO-0000` (common protocol, SHA-256 `333764e7…`), `P2-HO-0001`…`P2-HO-0006` (families). |
| Inherited | `PHASE-1-RESIDUAL-RISKS.md` (`b08678b0…`) as input; its items are R1-LOW/R2 and none is a Phase-2 obligation. |
| Next action | Tag this commit `cap2-candidate-0`; create six worktrees/branches; dispatch P2-AR-0001…0006. |

## P2-L-0003 — 2026-09-18 — Iteration-0 audit dispatched on `cap2-candidate-0`

| Field | Value |
|---|---|
| Candidate | `cap2-candidate-0` = `57177a37ea296ece16b185874831462b6a76db18` (annotated tag). `product_code_digest` `bd4d65d9…0547` = `srr1-r1-accepted`; AC-14 R1-preservation therefore not required for this candidate. |
| Runs | P2-AR-0001 alpha (A/B/S/T) · P2-AR-0002 beta (C/D/R, AC-7) · P2-AR-0003 gamma (E/F/G/H/I) · P2-AR-0004 delta (J/K/L/M/N) · P2-AR-0005 epsilon (O/P/Q/U/V, AC-5, AC-6) · P2-AR-0006 zeta (W, AC-8) |
| Isolation | One git worktree and branch per run (`phase2/cap-audit-0-<family>`), all at the tag; evidence confined to `release/capability-baseline/audit-0/<family>/`. |
| Independence | Each auditor is a fresh context; none authored the implementation or any Phase-1 role; the families cannot read each other's unmerged evidence. |
| Next action | Await the six reports; verify and merge each; then dispatch the fresh synthesis auditor P2-AR-0007. |

## P2-L-0004 — 2026-09-18 — First-pass family audits ruled nonconforming; all six families re-audited on the pinned model

| Field | Value |
|---|---|
| Returned | P2-AR-0001 alpha (16 P&S / 1 PARTIAL, 0 blocking) · P2-AR-0002 beta (17/2, 0 blocking) · P2-AR-0003 gamma (16/3, 0 blocking) · P2-AR-0004 delta (16/2, 0 blocking) · P2-AR-0005 epsilon (10 P&S + U / 1 PARTIAL / 4 ABSENT, 1 blocking) · P2-AR-0006 zeta (12/0, 0 blocking). Each touched only its own evidence directory and report. |
| Model deviation | Every run self-reported `agent_model: claude-opus-4-6`; the run claims recorded `claude-opus-5`, the model Phase 1 used for every role. |
| Conformance (orchestrator, procedure only) | Mechanical scan of each `capability-audit.yaml` against its own `findings.yaml`: capabilities recorded `PRESENT_AND_SUBSTANTIAL` while the same run records unmet bullets — alpha T1, A5 (and S4 claimed for A0–A11 while adopt was driven A0–A6); beta C9, R3; delta M4; epsilon P1, U (all 28 U bullets on one doctor output); zeta W7, W9, W11 (with artifact-flow gaps mislabelled lifecycle `P3`). Evidence concentration: beta 123 bullets on 8 distinct references; delta 93 on 12; epsilon's O5 probe records tier semantics as printed `echo` assertions and a U↔O5 output reading `UNHEALTHY` was recorded PASS. Gamma: no contradiction found; retained as corroboration. |
| Rulings | P2-AR-0001/0002/0004/0005/0006 `COMPLETED_NONCONFORMING`; P2-AR-0003 `COMPLETED_MODEL_DEVIATION`. **No capability status was adopted, overruled or issued by the orchestrator**; the rulings concern protocol conformance only. All first-pass evidence merged unchanged as historical record (`bdc1375`, `5907e7d`, `ad5af95`, `9c232a3`, `96f1031`, alpha merge). |
| Re-dispatch | Model pinned explicitly (`opus`). P2-AR-0008 epsilon-r (P2-HO-0008), P2-AR-0009 beta-r, P2-AR-0010 gamma-r, P2-AR-0011 delta-r, P2-AR-0012 zeta-r, P2-AR-0013 alpha-r (P2-HO-0009, which restates the common protocol's standard and adds nothing new). Re-auditors are barred from reading their family's first-pass evidence. |
| Next action | Await the six re-audits; verify, merge; dispatch synthesis P2-AR-0007 on the audits of record. |

## P2-L-0005 — 2026-09-18 — P2-AR-0008 epsilon re-audit merged (audit of record)

| Field | Value |
|---|---|
| Run | P2-AR-0008, self-reported `claude-opus-5`; work `787942b`, report `24c5f7c`, merge `ebe77fa` |
| Result | FAMILY_AUDIT_COMPLETE. 16 capabilities / 146 bullets from the owner source, one run per bullet, `evidence/RUN-ALL.sh` reproduces all 15 probes. Capabilities: 1 P&S (Q3), 11 PARTIAL, 4 ABSENT (V1–V4). Bullets: 48 present / 51 partial / 47 absent. 36 findings, **27 blocking**, 0 owner decisions. |
| Determinations | AC-5 **NOT MET** (no scheduler: no impacted selection, parallelism or isolation; partial cache/staleness/hard-block/provenance; no remediation tasks; G6 absent). AC-6 **QUALIFICATION_ORACLE_FORMAT_ABSENT**. Also reports AC-13/AC-10 contract-view defects (Gate U absent from the compiled contract while `contract verify` passes; V1–V4 mislabelled ORIGINAL; no bullets/fields in the compiled form) and AC-16 interaction failures (U↔O5, O4↔W6). |
| Orchestrator checks | Scope confined to own evidence and report; no status/finding contradiction; regression reproduced by the auditor 42/79. Contrast with the first-pass epsilon audit (1 blocking finding, printed assertions) is recorded as calibration for the re-dispatch decision. |
| Next action | Await P2-AR-0009…0013. |

## P2-L-0006 — 2026-09-18 — P2-AR-0011 delta re-audit merged (audit of record)

| Field | Value |
|---|---|
| Run | P2-AR-0011, self-reported `claude-opus-5`; work `aacc9a0`, report `2e12353`, merge `79ae966` |
| Result | FAMILY_AUDIT_COMPLETE. 18 capabilities / 93 bullets, each with an executable check (17 probes incl. SIGKILL mid-transaction, forged records, modified binary). Capabilities 3 P&S (K1, L4, N4) / 14 PARTIAL / 1 ABSENT (J2). Bullets 29/50/14. 26 findings, **17 blocking**. |
| Headline blockers | L3 human approval derivable from caller claims (CLI defaults, `--role human`, `GOV_ROLE`), forged gate/decision files, approval not bound to content, tasks runnable past declined/missing gates; J2 no experiment lifecycle; K2 CIT-E staleness stops at open work (K2↔W6 fails); K3 materiality self-labelled; N2 four of eight checkpoint triggers never fire; N3 nothing marks a checkpoint stale (N↔W9 fails); M1 routing overrides lower kernel tier floors. |
| Owner-decision flags | A0-L3-01 and A0-L3-05 — "how a human is authenticated to the product" (the human-presence channel). **Held for synthesis adjudication**: whether ARCH-0003 §8 ("Interactive trust changes use local administrator/Human Gate authority. Repository gate records remain requests"), D-0007 trust direction and the break-glass owner-authority precedent (OWNER-DECISION-0006) already determine the channel, or whether a genuine owner choice remains. Not presented to the owner yet. |
| Out-of-family observations | Passed to the synthesis as leads, not findings: I4 BLOCKED task handed out as runnable; E3/E1 any role can return any handoff; C7/D2 nested worker return not indexed; C9 duplicate impact candidates. |
| Next action | Await P2-AR-0009, 0010, 0012, 0013. |

## P2-L-0007 — 2026-09-18 — P2-AR-0012 zeta re-audit merged (audit of record)

| Field | Value |
|---|---|
| Run | P2-AR-0012, self-reported `claude-opus-5[1m]`; work `f705341`, report `459987b`, merge `3b8eb2d` |
| Result | FAMILY_AUDIT_COMPLETE. W1–W12: 0 P&S / 11 PARTIAL / 1 ABSENT (W11). Bullets 19/34/32 + 1 N/A (W12 G6 — Phase 4 per frozen contract §7). 27 findings, **24 blocking**, 0 owner decisions. |
| AC-8 | **NOT MET** — matrix 14 rows × 140 cells: 24 proven / 55 partial / 61 GAP; all three rejection conditions hold (some declared inputs reach workers only via retrieval or not at all; superseded inputs satisfy READY/DONE while audit stays HEALTHY; close records no consumption and accepts fabricated traceability). W10 attack 4 fails: index outage/corruption or a re-pinned embedder makes `context compile`/`continue` fail outright, withholding mandatory inputs. |
| Next action | Await P2-AR-0009, 0010, 0013. |

## P2-L-0008 — 2026-09-18 — P2-AR-0010 gamma re-audit merged (audit of record)

| Field | Value |
|---|---|
| Run | P2-AR-0010, self-reported `claude-opus-5[1m]`; work `9523978`, report `851f2a9`, merge `aeabdc5` |
| Result | FAMILY_AUDIT_COMPLETE. 19 capabilities / 167 items: 4 P&S (G2, H1, H2, I1) / 15 PARTIAL. Items 115/42/10. 36 findings, **19 blocking**. |
| AC-4 (F4) | **NOT MET.** R1 acceptance still holds for this candidate (digest identical; R1-4 held-out 31/31 re-run unedited), but above-floor plugin-trust defects outside R1's scope: any answered-yes gate authorises elevated plugin registration (A0-F4-01); forged registry undetected and does not stale the suite (A0-F4-02); security review satisfied by naming any record (A0-F4-05). |
| Headline blockers | E1 init/adopt ignore `--role`, L0 reinstalled the kernel and ran a migration; E1 L1 worker forges gate answers/decisions, unblocking gated work and executing a human-method CIT (L3↔E1 fails); E4 claims non-atomic (15/15 races) and ignore the DAG; F3 approved tool install can never proceed; G1 spec edits inside tasks bypass impact/gates; I3 9 of 11 generation sources generate nothing. |
| Owner-decision flags | A0-E1-04 (acting role = caller's declaration; conflicts with ARCH-0003 §8) — same question as delta's A0-L3-01/05, the human-presence/role-authentication channel. A0-F4-03 (plugin self-declaration decides whether a gate is needed). **Both held for synthesis adjudication** against ARCH-0003 §8–9, D-0007 and F4 bullet 1 ("Descriptor cannot authorise itself"). |
| Next action | Await P2-AR-0009 (beta-r) and P2-AR-0013 (alpha-r). |
