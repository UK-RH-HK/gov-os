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

## P2-L-0009 — 2026-09-18 — P2-AR-0009 beta re-audit merged (audit of record)

| Field | Value |
|---|---|
| Run | P2-AR-0009, self-reported `claude-opus-5[1m]`; work `a3d6b66`, report `73b2381`, merge `158a128` |
| Result | FAMILY_AUDIT_COMPLETE. 19 capabilities / 123 bullets: 2 P&S (C1, C6) / 17 PARTIAL. Bullets 86/31/5 + 1 N/A (D4 generative/query-planning model — optional per framework §14.2; synthesis to confirm). 30 findings, **22 blocking**, 0 owner decisions. |
| AC-7 | **NOT MET** by the auditor's determination: the benchmark/select/pin/reindex path works end to end, but runtime/model artefacts are not identified (A0-D4-01), pins are not bound to the executing implementation (A0-D5-01), and profile changes need no evidence/regression/gate (A0-D5-02); retrieval-pipeline defects (A0-C3-01/02, A0-C4-01, A0-D2-03) limit quality under any profile. |
| Other headline blockers | D1 path-map reclassification not applied incrementally so archived material is served as current; D1/K2 CIT-E refresh uses stale cached policy (K2↔D1 fails); R1 retirement without dependency proof — adoption A6 rewrote live code to read archived legacy rules; D6 deleting the "derived" runtime directory loses claims and lifts FREEZE_WRITES. |
| Protocol deviation | Disclosed by the run: one read of its **own** background build output in the task-output store. Ruled immaterial to independence (no other role's transcript or context); recorded. |
| Next action | Await P2-AR-0013 (alpha-r); then synthesis. |

## P2-L-0010 — 2026-09-18 — P2-AR-0013 alpha re-audit merged; all six audits of record in

| Field | Value |
|---|---|
| Run | P2-AR-0013, self-reported `claude-opus-5[1m]`; work `04d8197`, report `3cfe881`, merge `fdc4f32` |
| Result | FAMILY_AUDIT_COMPLETE. 17 capabilities / 100 bullets: 3 P&S (B1, B3, S1) / 14 PARTIAL. Bullets 61/39. 25 findings, **7 blocking**. |
| AC-4 (A2) | **NOT MET.** R1 acceptance still valid for the candidate (digest identical; R1 behaviours re-established with an independent signing harness). But bullets 146, 149, 150 fail on every machine and 143/147 hold only on a provisioned machine while the product default is unprovisioned. Areas R1 did not examine: consistent post-install rewrite; identity recorded in framework.lock; unsigned certification claim used as an update-gate input; offline verification beyond break-glass. |
| Other blockers | A0-A2-04 editing the unsigned manifest to CERTIFIED removes the update Human Gate, any role can build a CERTIFIED release; A0-T2-01 adoption verdicts not bound to what the reviewer approved (executor emptied tests and turned a keep into an ungated delete; A7 accepted with 0 tests); A0-A1-02 compiled contract headings only; A0-B3-01 green record not staled by spec/source/index/binary/trust-anchor changes. |
| Owner-decision flags | A0-A2-01 (post-install integrity anchor — the auditor says it needs a D-0007 trust-class amendment) and A0-A2-02 (unprovisioned-machine posture: embed/pre-install production root keys vs refuse vs accept; R1's AR-0027 accepted the posture as an implementation choice). **Held for synthesis adjudication** against ARCH-0003 §§3, 5, 7, 8, 11, D-0007, OWNER-DIRECTIVE-0004, the frozen SRR boundary and the R1 evidence. |
| Audit-of-record totals | alpha-r 7 · beta-r 22 · gamma-r 19 · delta-r 17 · epsilon-r 27 · zeta-r 24 = **116 blocking findings** across 102 capability records (family counts; synthesis will dedupe and classify). Every family reports its derived-contract-view defect independently. |
| Next action | Dispatch the fresh synthesis auditor P2-AR-0007 at this merge commit. |

## P2-L-0011 — 2026-09-19 — Iteration-0 synthesis: REJECTED; repair iteration 1 round 1 dispatched; HG-P2-0001 presented

| Field | Value |
|---|---|
| Synthesis | P2-AR-0007 (fresh, pinned model, self-reported `claude-opus-5[1m]`), work `ea6abea`, report `8ad351c`, merge `395df8d`. **`GOVERNANCE_CAPABILITY_BASELINE_REJECTED`** on `cap2-candidate-0`. Re-ran all six families' probes in a throwaway clone — 1,680 PASS/FAIL outcomes identical to the committed evidence; regression 42/79 green. |
| Statuses | 11 PRESENT_AND_SUBSTANTIAL / 84 PARTIAL / 6 ABSENT (J2, V1–V4, W11) of 101 capabilities (100 numbered + Gate U). |
| Acceptance criteria | HOLD AC-1, AC-9, AC-11, AC-12, AC-14, AC-15. FAIL AC-2, AC-3, AC-4, AC-5, AC-6, AC-7, AC-8, AC-10, AC-13, AC-16. |
| Findings | 180 family findings: 165 confirmed, 15 corrected, 0 refuted; 10 added. **134 blocking in 52 blocker classes BC-P2-01…52** — the iteration-0 inventory against which convergence is measured. |
| Owner flags adjudicated | Determined by accepted sources, so routed as repairs: human-approval channel (BC-P2-10), default role (BC-P2-08), plugin self-declaration (BC-P2-39), A2 post-install anchor (BC-P2-35), unauthenticated-install presentation (BC-P2-36). Genuine owner decisions: **OD-P2-01** (agent-role identity binding) and **OD-P2-02** (unprovisioned-machine admission posture). The orchestrator re-checked both classifications against the owner's Phase-2 directive: OD-P2-01 is a security/cost trade-off against D-0007 consequence 5; OD-P2-02 is a security-versus-availability posture the owner already reserved (OWNER-DECISION-0005 §1). |
| Human Gate | **HG-P2-0001** (`GATES/HG-P2-0001-OWNER-DECISIONS.md`) presented in the active chat after the builders were dispatched. It blocks only BC-P2-36's admission part and any agent-identity extension of BC-P2-34 (non-global blocking, Contract v3 L4). |
| Repair plan | repair-delta §2 dependency waves grouped into rounds. **Round 1** (eight builders, pinned model, disjoint owned files, CARGO_BUILD_JOBS=2): P2-AR-0014 WS-1/12 (BC-01, 51) · P2-AR-0015 WS-2 (03, 06, 42, 43) · P2-AR-0016 WS-3 (08, 09, 10, 12a, 18r, 45, 49) · P2-AR-0017 WS-4 (21r, 17, 19, 20c) · P2-AR-0018 WS-5 (14, 15) · P2-AR-0019 WS-6 (25, 26, 27, 29, 32) · P2-AR-0020 WS-8 (35, 36-presentation, 37, 38) · P2-AR-0021 WS-9/11 (33, 52, 21c, 50). Handoffs P2-HO-0010 (common) and P2-HO-0011…0018. |
| Housekeeping | 13 audit worktrees removed after confirming each branch merged and clean (branches retained). |
| Next action | Await round 1 and the owner's answer; integrate; round 2. |

## P2-L-0012 — 2026-09-19 — HG-P2-0001 answered by the product owner

| Field | Value |
|---|---|
| Channel | Active chat (AskUserQuestion), presented after the round-1 builders were dispatched so that no independent work waited on it |
| OD-P2-01 | **Option A** — agent roles (L0–L4) stay declared by the launching harness/adapter (D-0007 consequence 5). Recorded as `OWNER-DECISION-P2-0001` (SHA-256 `612849ba…`). No new class; residual risk recorded (an agent could claim a higher *agent* role, never a human one). BC-P2-08/09/10 unaffected and still required. |
| OD-P2-02 | **Option A** — refuse external-source kernel ingress on unprovisioned machines; the binary's embedded payload only as a marked bootstrap mode; dev/test provision a throw-away root; Phase-4 qualification and release evidence on provisioned machines. Recorded as `OWNER-DECISION-P2-0002` (SHA-256 `5d73bbe3…`). BC-P2-36's admission part becomes a determined, owner-added requirement for round 2 (WS-8, with harness/fixture/docs provisioning). |
| Unchanged | D-0007 text (its explicit transition record stays open, not requested); ARCH-0001; ARCH-0003; the frozen gate contract. |
| Next action | Continue awaiting round 1. |

## P2-L-0013 — 2026-09-19 — Round 1: six builders complete; trial integration exposes two semantic conflicts

| Field | Value |
|---|---|
| Completed | P2-AR-0014 WS-1/12 (BC-01, 51 claimed) · P2-AR-0017 WS-4 (21r, 17, 19, 20 claimed) · P2-AR-0018 WS-5 (14, 15 claimed) · P2-AR-0019 WS-6 (25, 26, 27, 29, 32 claimed) · P2-AR-0020 WS-8 (35, 36-presentation, 37, 38 claimed) · P2-AR-0021 WS-9/11 (33, 52, 50 claimed; 21 catalogue side PARTIAL pending a WS-2 hook). All self-reported `claude-opus-5[1m]`; all verdicts `READY_FOR_INDEPENDENT_CAPABILITY_VERIFICATION`; none raised an owner question. |
| Orchestrator checks | Each branch's changed files are within its owned set plus declared additive hot-spot edits; builder-test edits are declared and strengthen rather than weaken (WS-5 greenfield, WS-8 repair2 flips assertions that encoded the BC-P2-37 defect, WS-9 brownfield/migration). Builder claims are regression evidence only. |
| R1 note for AC-14 | WS-4, WS-6 and WS-8 each report AR-0033 `hv_a::a1` failing because it pins candidate 4's census size (84 files / 740 functions); each re-ran the §6 census separately and found 0 violations. AR-0027/0029/0031 match their recorded baselines. The AC-14 verifier must judge `hv_a::a1` on property, per AR-0033's own precedent for AR-0031's shape-asserting tests. |
| Trial integration | Branch `phase2/integration-1` (worktree in scratchpad). WS-4, WS-5, WS-6, WS-8, WS-9/11 merge cleanly (including the two disjoint `records.rs` regions). WS-1/12 conflicts textually in `cli/src/main.rs` with WS-4 (both appended a `Cmd` variant) — trivial union, left for the integration builder. Build OK; `cargo test --lib` 100/0; `cargo test --test certification` **86/2**: `brownfield_adoption_end_to_end` and `path_migration_with_rollback_and_memory_rebuild` fail at A11 — WS-9 writes `MPLAN-GOVERNANCE-ADOPTION.consumers` as objects while WS-4's `record.schema.json` makes `consumers` a string relation field (3 HIGH schema_invariants findings), plus WS-4's packet dropped `semantic_candidates` still listed in `CONTEXT_POLICY.retrieved_fields`. Cross-workstream semantic conflicts → integration builder. |
| Next action | Await WS-2 (P2-AR-0015) and WS-3 (P2-AR-0016); then dispatch a fresh integration builder over all eight branches. |

## P2-L-0014 — 2026-09-19 — Round 1 complete (8/8 builders); WS-3 owner question adjudicated; integration dispatched

| Field | Value |
|---|---|
| WS-3 (P2-AR-0016) | BC-08, 09, 10, 12a, 18r, 45, 49 claimed. Human channel: Ed25519 answers signed by an owner `human-gate` key held off the agents' machine, bound to gate instance, rendered-package hash, option, nonce and expiry, verified against the release root's `human-gate` delegation, re-verified at every use; T2 HMAC seal primitive; `control::g0` classifies all 111 commands; undeclared role → L0. `srr/**` and Contract v3 byte-identical. Builder tests updated for intended changes (declared); lib 53/0, certification 91/0; R1 held-out only the `hv_a::a1` size pin. |
| WS-2 (P2-AR-0015) | BC-03, 06, 42, 43 claimed: 30-class currency key incl. binary and trust state; G0–G6 scheduler with catalogue, concurrency (up to 9 threads), sandboxed state-writing checks, per-check cache (62 ms vs 309 ms cold), provenance, RED/YELLOW/GREEN; product-test families as governed evidence; skill versions bound to content with executed scenarios. Found a kernel-cache race in `kernel::embedded_kernel_dir` (root cause → WS-8 round 2). Its leftover partial cache `~/.cache/gov/kernels/4.1.5-2120db97b369` was inspected; removal was denied by the permission system and not retried (harmless; surfaced to the owner). |
| P2-ADJ-0001 | WS-3's question (standalone human-gate anchor on machines with no release root) ruled **determined** by OWNER-DECISION-P2-0002 Option A and ARCH-0003 §2/§3: default `false`; owner-overridable; routed to round 2. |
| Totals | 36 class claims across 8 branches (35 REPAIRED_CLAIMED + BC-21 catalogue side PARTIAL). None is acceptance. |
| Integration | Fresh integration builder **P2-AR-0022** (P2-HO-0019): merge all eight (WS-3 first), resolve `main.rs` unions, register every new subcommand with WS-3's G0 guard, reconcile the two known semantic conflicts (migration-plan `consumers`; `semantic_candidates`) and WS-3's role-default fallout in other workstreams' tests without weakening, register `framework/health` in the kernel payload if needed, run all suites and every R1 held-out suite. The orchestrator's trial branch `phase2/integration-1` was a probe only and is superseded. |
| Next action | Await P2-AR-0022; then round 2. |

## P2-L-0015 — 2026-09-19 — Round-1 integration merged; round 2 dispatched

| Field | Value |
|---|---|
| Integration | P2-AR-0022 (fresh, `claude-opus-5[1m]`), work `9126a07`, report `90fe225`, product tip `811317b`. All eight round-1 branches merged `--no-ff` in order (WS-3 first); textual conflicts only in `tests/certification/main.rs` and `cli/src/main.rs`, resolved as unions. Eight declared product commits beyond the merges (+163/−18, none in an R1-listed file): compile reconciliation; G0 registration of every round-1 subcommand (146 labels; `verify product` reclassified Write/`record_audit` so it cannot write evidence under FREEZE_WRITES); migration-plan consumers moved to `expected_consumers` (WS-9 × WS-4); packet carries `semantic_candidates`; migration re-pointing never rewrites a T2-sealed record (WS-3 × WS-9); WS-8/WS-9 tests answer gates via the owner-signed channel; rustfmt; **`currency.rs` reads the trust anchor through `srr::verifier::trusted_root`** — WS-2's hand-built path had failed R1 AR-0031 `hx_a::a4`, undetected because WS-2's recorded R1 re-run measured another builder's tree via shared scratch symlinks. |
| Results | lib 146/0, certification 100/0 (95/5 straight after the merges), Python 4/4; R1 held-out AR-0027 26/3, AR-0029 26/2 (`ho_f` n/c), AR-0031 27/7, AR-0033 30/1 (`hv_a::a1` size pin; census with only the size assertions removed: 0 violations in all seven §6 activities; AR-0033 `derive.py` agrees). No integration regression against any builder's own probes; 152 audit-of-record probe runs re-run with every difference explained. Kernel-cache race not tripped (5 cold-cache trials). |
| Merge | `phase2/repair-1-integration` → `release/4.1.6-rc1` at **`b7e6d52`**; `product_code_digest` `b1ab1c8c…fbb1`. The orchestrator reproduced `cargo test --lib` 146/0 at the merged HEAD (certification reproduction recorded in P2-L-0016). |
| Routed forward | O-1 (WS-3: shipped 4.1.4/4.1.5 kernels' descriptive policy keys refused → D027 CRITICAL, update rollback — S5/A1), O-4 (WS-3: `rebuild-memory` under FREEZE_WRITES), O-2/O-6 (WS-2), O-5 (R1 re-runs must use private paths — added to the round-2 common protocol and to every future verifier handoff), O-8 (P2-ADJ-0001 → WS-3). |
| Round 2 | Nine fresh builders from `b7e6d52`: P2-AR-0023 WS-2 · P2-AR-0024 WS-3(+docs) · P2-AR-0025 WS-4 · P2-AR-0026 WS-5 · P2-AR-0027 WS-6 · P2-AR-0028 WS-7 · P2-AR-0029 WS-8 (OWNER-DECISION-P2-0002 admission + harness provisioning + kernel-cache race) · P2-AR-0030 WS-9/11 · P2-AR-0031 WS-10. Handoffs P2-HO-0020…0029. Checkpoint P2-CP-0004. |

## P2-L-0016 — 2026-09-19 — Orchestrator regression reproduction at merged round-1 HEAD `b7e6d52`

`cargo build --release` ok; `cargo test --lib` **146/0**; `cargo test --test certification` **100/0** (191 s). Matches the
integration builder's figures. Regression reproduction only — not a verdict.

## P2-L-0017 — 2026-09-19 — Round 2: seven of nine builders complete; P2-ADJ-0002 (T2 cross-machine continuity)

| Field | Value |
|---|---|
| Completed | P2-AR-0023 WS-2 (BC-22 + 20 IPs) · P2-AR-0024 WS-3 (P2-ADJ-0001 applied, O-1 compatibility, O-4, BC-08 remainder, docs) · P2-AR-0027 WS-6 (BC-28, 30 claimed; BC-31 PARTIAL — writer moves routed) · P2-AR-0028 WS-7 (BC-39, 40, 41, 11-plugin, 09-registry; D-0005 c3 narrowed → governed amendment routed) · P2-AR-0029 WS-8 (OWNER-DECISION-P2-0002 admission implemented; UNADMITTED state closes the clone/rewrite bypass; harness provisions a throw-away root; kernel-cache race fixed; found a planted `AKIA…EXAMPLE` literal in WS-2's `SKILL_SCENARIO_CHECKS.yaml`) · P2-AR-0030 WS-9/11 (BC-34 adoption side, adopt host sites, export approval) · P2-AR-0031 WS-10 (BC-46, 47, 48). All self-reported `claude-opus-5[1m]`; all R1 held-out runs measured on their own trees via private paths (census file/function counts recorded) and at baseline except the known `hv_a::a1` size pin with 0 §6 violations. |
| Still running | P2-AR-0025 WS-4, P2-AR-0026 WS-5. |
| P2-ADJ-0002 | `t2.rs` seals are machine-keyed: OS-written facts from machine A are `Foreign` (not honoured) on machine B. Conflicts with Contract v3 S6 / framework §1 continuity. Ruled **determined** (S6 + D-0007 rule 2 + ARCH-0003 §8 provisioning boundary + OWNER-DECISION-P2-0002): round 3 must make T2 facts portable across the owner's provisioned machines while forged/unauthorised records stay refused; mechanism is the builder's within the provisioning boundary. Recorded `GATES/P2-ADJ-0002-T2-CROSS-MACHINE-CONTINUITY.md`; owner-overridable. |
| Integration notes collected | WS-2's three D032 test relaxations must be removed once WS-8's provisioned harness is merged; heavy test-setup overlap between WS-3, WS-8 and WS-9 round-2 test edits; WS-10/WS-6/WS-2/WS-7 added CLI subcommands and `COMMAND_GUARDS` entries additively. |

## P2-L-0018 — 2026-09-19 — Round-2 integration merged; round 3 dispatched

| Field | Value |
|---|---|
| Round 2 | Nine builders complete (P2-AR-0023…0031); WS-4 (P2-AR-0025) last: BC-11 CIT side, BC-13 materiality (not self-labelled), BC-04 propagation to completed work/reports/receipts/packets, BC-05 checkpoint/handoff continuity, BC-18 contradiction detection; 88 FAIL→PASS in its probe sweep, 4 PASS→FAIL explained (K4 relabel fixture), three self-found regressions fixed. |
| Integration | P2-AR-0032, work `cd423a6`: nine `--no-ff` merges; two declared product fixes (memory::profile compile reconciliation; CIT propagation re-seals only previously-verified seals); harness converged on WS-8's provisioned root; WS-2's D032 relaxations removed. lib **207/0**, certification **136/0** (109/27 right after merges), Python 4/4; G0: 177 labels, every round-2 label classified once. R1 held-out at baselines, census 118 files / 1991 functions, 0 §6 violations. |
| Merge | `phase2/repair-1-r2-integration` → `release/4.1.6-rc1` at **`e8e1ff2`**; `product_code_digest` `797da37c…1fe1`. Orchestrator regression reproduction recorded in P2-L-0019. |
| Routed | IF-1 (W7 semantics: consumption ≠ implementation) and O-1/O-5 → WS-2 r3; O-7 (OS writers modifying sealed records) → WS-4 r3. |
| Round 3 | Eight builders from the merged tree: P2-AR-0033 WS-2 (BC-07, BC-23, BC-44, availability rule in the catalogue) · P2-AR-0034 WS-3 (P2-ADJ-0002, T2 completeness, BC-31 control state, D-0005/API-0001 governed amendment, docs, adapters) · P2-AR-0035 WS-4 · P2-AR-0036 WS-5 (BC-24, BC-13 hook, WS-4 API wiring, claims-store move) · P2-AR-0037 WS-6 · P2-AR-0038 WS-7 · P2-AR-0039 WS-8 (P2-ADJ-0002 provisioning, kernel payload/version consistency) · P2-AR-0040 WS-9/11. Common protocol P2-HO-0031 adds a binding **availability rule** (Contract v3 L4/O5): blocks scoped to what they protect; remedies and independent work stay available. Checkpoint P2-CP-0005. |
| Next | Round-3 integration; round 4 (BC-P2-02 evidence map); mint `cap2-candidate-1`; independent verification. |

## P2-L-0019 — 2026-09-19 — Orchestrator regression reproduction at merged round-2 HEAD `e8e1ff2`

`cargo build --release` ok; `cargo test --lib` **207/0**; `cargo test --test certification` **136/0** (260 s). Matches the
integration builder. Regression reproduction only — not a verdict.

## P2-L-0020 — 2026-09-19 — Owner-requested progress and model/context telemetry snapshot (observational only)

| Field | Value |
|---|---|
| Request | Product owner: a non-disruptive Phase-2 status plus model/context telemetry snapshot; routing and execution unchanged. |
| Produced | `PHASE_2_PROGRESS_AND_MODEL_TELEMETRY.md` and machine-readable `PHASE_2_PROGRESS_AND_MODEL_TELEMETRY.yaml`. Sources: committed durable state and the harness completion notices (`subagent_tokens`, `tool_uses`, `duration_ms`). Input/output token split, subagent reasoning level, context utilisation, compaction and cost are recorded as NOT_OBSERVABLE. |
| Headline | 40 agents launched, 37 completed, 3 running, 0 failed; 6 superseded (first-pass audits). Round 3 of 4 in repair iteration 1. 52 classes / 134 blocking findings all OPEN pending independent verification; 48 of 52 carry at least one builder claim. Convergence counter 0 of 3. Merged tree `e8e1ff2`: lib 207/0, certification 136/0; R1 held-out at baselines. |
| Record defects found and repaired | 17 run records were unparseable YAML (orchestrator recorder wrote notes unquoted) — quoted, content unchanged; `check_state.py verify` now refuses unparseable or duplicate-key run records (reports of runs awaiting integration are checked on their branch); `running_work` pruned to the three truly running runs. |
| Routing | Unchanged. Round 3 continues. |

## P2-L-0021 — 2026-09-19 — Context/agent analysis (owner follow-up); pre-compaction checkpoint

| Field | Value |
|---|---|
| Request | The owner asked for a deeper context/agent analysis: token use by role, 500k/750k/1M crossings, Contract-v3 reloading, history-versus-scope context, whole-repository context, builder/verifier/synthesis ratios, whether 1M was needed, where a bounded pack would suffice, reasoning versus reading. |
| Scoped exception | The Phase-2 prohibition on reading transcripts protects role independence. It was lifted **once, for the orchestrator only**, at the owner's request. Scope: metadata-only extraction by script from the **completed** agents' transcript JSONL — usage fields, model/effort, tool names, file paths and patterns, block sizes. No message or thinking text was loaded, no running agent was read, and nothing propagates to any role's handoff. |
| Findings (report §C) | `subagent_tokens` ≈ final context size. The first pass actually ran `claude-opus-4-6`/`high` and compacted at 130k–167k; every later agent ran `claude-opus-5`/`xhigh`. All 31 opus-5 agents exceeded 500k (606,793–964,988), none reached 1M, and 5 compacted near 910k–965k. Contract v3 reloading is ≤ 4.4% of tool-result characters. Exact re-reads are negligible. About half of peak context is the agent's own output. Builders read a median ~45% of their source outside their owned files, mostly integration surfaces. Builders process ~3–4× a verifier's tokens and spend ~2/3 of wall time in build/test. |
| Durable tooling | `tools/record_builder_round.py` (JSON-quoted outcome recorder), `tools/telemetry_context_extract.py`, `tools/telemetry_usage_table.py`; per-agent data in `telemetry/P2-CONTEXT-TELEMETRY.json`. |
| Pre-compaction | The orchestrator context is at 943,882 tokens. Checkpoint **P2-CP-0006** and continuity handoff **P2-HO-ORCH-0001** record the exact next actions: await P2-AR-0033/0035/0036 → integration-3 (P2-HO-0040, unify the two P2-ADJ-0002 mechanisms) → round 4 (BC-P2-02) → mint `cap2-candidate-1` → verification iteration 1. |
| Routing | Unchanged. |

## P2-L-0022 — 2026-09-19 — Round 3: all eight builders complete; P2-ADJ-0003 (H4 gaps and green-baseline probes)

| Field | Value |
|---|---|
| Recorded | P2-AR-0035 WS-4 (`2324548`), P2-AR-0036 WS-5 (`d7db8dc`), P2-AR-0033 WS-2 (this entry). All eight round-3 runs are `COMPLETED_AWAITING_INTEGRATION` with verdict `READY_FOR_INDEPENDENT_CAPABILITY_VERIFICATION`; every branch sits on base `53897c1`; scope checked against each handoff (WS-5 declared three additive exceptions — CLI, `COMMAND_GUARDS`, `mod.rs`; WS-2 none). Builder-reported regression on their own trees: WS-2 lib 213/0, certification 136/0; WS-5 lib 215/0, certification 146/0; R1 held-out at baselines with census on each tree. These are builder claims, not acceptance. |
| Adjudication | **P2-ADJ-0003** (`GATES/P2-ADJ-0003-H4-GAPS-AND-GREEN-PRECONDITIONS.md`). WS-2 asked whether WS-10's `medium` H4 scenario-chain findings should degrade suite health (they turn two audit-of-record probe preconditions, zeta-r FR baseline and AC16-X1 X1-O4, from PASS to FAIL). Ruled **determined**: Contract v3 H2/H3/H4 and HEALTHY ("tests/traceability satisfy policy") make an incomplete scenario chain not green; no availability trade-off, since no hard-block fires below `high` and the close gate accepts a complete, current non-green suite result. Probe preconditions are read against the contract: green baselines use contract-valid fixtures; X1-O4's precondition contradicts Contract v3:1136. Not an owner decision; owner-overridable. |
| Routed | WS-5 R3-WS5-1..11 (incl. deferred task-record sealing, ordered after WS-3/WS-4 re-sealing) and WS-2 IP-R3-WS02-01..11 (incl. one availability host API across scheduler and task hosts) into `HANDOFFS/P2-HO-0040-integration-3.md`. |
| Disclosed | WS-2 left one superseded R1 run output in its evidence (`rm` denied in this environment; its report says so). Harmless; not deleted. |
| Next | Integration-3: P2-AR-0041 on `phase2/repair-1-r3-integration`. |

## P2-L-0023 — 2026-09-19 — Round 3 integrated (P2-AR-0041, merge `e4cb662`); round 4 dispatched as two parallel builders

| Field | Value |
|---|---|
| Integration | P2-AR-0041 (fresh integration builder, `claude-opus-5[1m]`) merged the eight round-3 branches `--no-ff` and made eight product commits plus one test commit (report `release/capability-baseline/repair-1/integration-3/00-INTEGRATION-REPORT.md`). One P2-ADJ-0002 mechanism (`srr/binding.rs` + `t2.rs`; `gov trust bind`/`reseal`; `trust t2-binding` removed; WS-8's expiry/rotation semantics kept as the stronger); one availability host API (WS-2's `Request`/`admit`/`confirm_remedy`/`guard`); `cit` and `task` sealed record kinds, ordered after WS-3/WS-4 re-sealing. Stopped: R3-WS5-11 (not reproduced). Verdict `READY_FOR_INDEPENDENT_CAPABILITY_VERIFICATION` — builder claims, not acceptance. |
| Orchestrator checks | Branch tip digests equal the merged tree: `product_code_digest` `1d3e9f59…85df7`, `governed_state_digest` `2514b9fb…35be`. Contract v3, the frozen gate contract, `GATES/` and `release/verification/` unchanged. Governed-record changes come from WS-3's round-3 commit `f50e37c` (D-0010 amending D-0005 consequence 3 under Contract v3 F4 / ARCH-0003 §9; API-0001 1.2; docs). |
| Reproduction at `e4cb662` | `cargo build --release` ok, 0 warnings; `cargo test --lib` **262/0**; `cargo test --test certification` **189/0/0** (813 s). Matches the integration builder. Regression reproduction only — not a verdict. |
| Round 4 (re-planned) | P2-HO-ORCH-0001 planned a single BC-P2-02 builder. The integration report left substantive IPs unrouted (e.g. `handoff.create` remedy scope, registry relocation at upgrade, INT3-O1/O2), so round 4 runs **two parallel builders with disjoint files**: **P2-AR-0042** WS-1 evidence map (P2-HO-0041; owns `contracts.rs`, `framework/contracts/**`, the acceptance schema, `capability-evidence-map.yaml`, `docs/generated/**`) and **P2-AR-0043** residual integration points (P2-HO-0042; everything else; no test renames). Fixing known items before candidate 1 saves a verification iteration. |
| Routing rulings | INT3-O1 (plugin registration inside a claimed task refused at close for its descriptor): determined by Contract v3 K3 (impact simulation auto-triggers for material security and governance changes) and F4 (elevated permissions reference an authoritative gate) — both hold, so the registration approval does not replace the CIT; mechanism is the builder's. INT3-O2: direct upstream change propagates when observed at the G1 rebuild as well as at claim (W6 + O5). Not owner decisions. INT3-O4 (legacy unsealed records reported, never blessed) left for the verifier. |

## P2-L-0024 — 2026-09-19 — SAFE HOLD ordered by the owner (model usage limit)

| Field | Value |
|---|---|
| Order | Owner: usage at ~99% of the model limit, resetting next day. Enter USAGE-PRESERVATION / SAFE-HOLD: no new builders, integrations, candidate minting, independent verification or repair round, and no replacement or follow-on agents, until the owner explicitly confirms the reset. Do not rush to acceptance; do not change model routing or acceptance criteria. |
| State at hold | Round 3 merged (`e4cb662`, digest `1d3e9f59…85df7`). Round 4 running: P2-AR-0042 (BC-P2-02 evidence map) at branch tip `9bafcb3`, 9 uncommitted files; P2-AR-0043 (residual IPs) with no commits, 26 uncommitted files. Neither has reported. Both agents were left running (not stopped); their uncommitted work was snapshotted, without touching their worktrees, to `refs/safe-hold/P2-AR-0042` (`7d94516`) and `refs/safe-hold/P2-AR-0043` (`b7e1e55`). `cap2-candidate-1` not minted; verification iteration 1 prepared (P2-HO-0043…0047, `d267f97`), not dispatched. 52 classes open; convergence counter 0 of 3; no owner gate pending. |
| Durable records | Checkpoint `CHECKPOINTS/P2-CP-0008.yaml`; continuity handoff `HANDOFFS/P2-HO-ORCH-0002-safe-hold-continuity.md` (supersedes P2-HO-ORCH-0001) with the exact resume procedure; `next_deterministic_action` = SAFE_HOLD → RESUME_ROUND_4; a hold prohibition added to `current_prohibitions`. |

## P2-L-0025 — 2026-09-19 — During SAFE HOLD: P2-AR-0042 (BC-P2-02 evidence map) completed and recorded; nothing merged

P2-AR-0042 reported `READY_FOR_INDEPENDENT_CAPABILITY_VERIFICATION` on `phase2/repair-1-r4-ws01` (product tip `9bafcb3`,
work `2ed8ab1`, report `d1487e8`; `product_code_digest` `d0c6a0d4…a4c9`). Scope checked against P2-HO-0041; recorded
`COMPLETED_AWAITING_INTEGRATION` (collection only, as the hold allows). Builder-reported lib 271/0, certification 193/0, R1 at
baselines. Disclosed gaps for the verifier: 16 capabilities owned only by builder tests, 9 without a G-tier owner, no G6
owner, 127 checklist items unowned. Remaining IPs IP-R4-WS01-1…6 — at merge, run `gov contract verify` after P2-AR-0043
merges (IP-R4-WS01-3). P2-AR-0043 still running. Hold unchanged.

## P2-L-0026 — 2026-09-20 — Recovery from the usage-limit interruption; round 4 continues

| Field | Value |
|---|---|
| What happened | The weekly model usage limit terminated **P2-AR-0043** (round-4 residual IPs) mid-run on 2026-09-19, after its five product commits but before `claims.yaml`, its run report and one adjacent check. The previous session's safe-hold records (P2-CP-0008, P2-HO-ORCH-0002, `refs/safe-hold/*`) held; the owner lifted the hold on 2026-09-20 and ordered normal continuation. |
| Reconstruction | From Git and the orchestration evidence only: `check_state.py verify` = STATE_CONSISTENT at `26c5459`, 0 uncommitted entries; branches, worktrees and safe-hold refs inspected; no transcript or task-output store read. P2-AR-0042 was already recorded COMPLETED_AWAITING_INTEGRATION (P2-L-0025). P2-AR-0043's branch carried `e752bed`, `00615f1`, `e5336d9`, `3a384d8`, `34e3725`; its report and evidence survived as untracked files in its worktree. |
| Recovery | Snapshot `refs/safe-hold/P2-AR-0043-2` (`e62bbcd`), then commit `55af199`: the run's own `00-REPAIR-REPORT.md` and `evidence/` committed unchanged, with provenance — the orchestrator authored none of it and graded nothing. Run recorded `INCOMPLETE_USAGE_LIMIT_RECOVERED` with its self-reported figures (lib 265/0, certification 198/0/0, R1 at baselines, census 123 files/2329 functions, 0 §6 violations) marked as unverified builder claims. |
| Preserved gap | The check P2-AR-0043 was starting when it stopped: whether `gov tools install` / `tools/<id>.yaml` writes governed files that task close treats as INT3-O1 did (Contract v3 K3 + F4). Routed as item 1 of **P2-HO-0048**. |
| Continuation | **P2-AR-0053** dispatched on `phase2/repair-1-r4-residual-b` from `55af199` with P2-HO-0048: the preserved gap, `claims.yaml` for the whole run, regression and R1 re-established on its own tree, and a continuation report. It must not redo P2-AR-0043's committed work, edit P2-AR-0042's files, or rename any test (the evidence map names 441 by path). |
| Owner stop condition | Recorded in `ORCHESTRATOR_STATE.yaml` and P2-CP-0009: if verification of `cap2-candidate-1` does not accept, stop after recording evidence and produce the owner decision package. |

## P2-L-0027 — 2026-09-20 — Round 4: P2-AR-0053 completed with an owner question; OD-P2-03 answered; P2-AR-0055 dispatched

| Field | Value |
|---|---|
| P2-AR-0053 | Continuation of the recovered P2-AR-0043 run. Delivered `claims.yaml` (24 claims), regression and R1 re-run on its own tree (lib 266/0, certification 200/0/0, all four R1 suites at baseline, census 123 files/2340 functions, 0 §6 violations, failure messages identical to P2-AR-0043's), and the continuation report. Recorded `COMPLETED_AWAITING_INTEGRATION`; branch tip `d96c8ab`, product `ab0a075`, digest `dcf4c591…0a13`. Scope checked against P2-HO-0048; no test renamed, removed or ignored. Builder claims, not acceptance. |
| Owner gate HG-P2-0002 | Item R4-O1: `gov tools install` writing `governance/project/tools/<id>.yaml` is a material governance **and** security change, so Contract v3 K3 change-controls it; the shipped `CHANGE_POLICY` gates every `governance_change`; but WS-7's round-3 IP-W7-1 / BC-P2-41 work and `TOOL_POLICY.auto_install_conditions` let a review-evidenced installation proceed ungated. Contract v3 F3 says "approval **when required**" and leaves *when* to policy, so the orchestrator escalated rather than adjudicating. |
| Answer | **OD-P2-03 "gate only elevated installs"** (`GATES/OWNER-DECISION-P2-0003-TOOL-INSTALL-GATE.md`). Ungated when authenticated/pinned, independently governed-reviewed, registered, reversible and entirely inside the project's already-authorised permission and trust envelope. Gated when the install expands authority: privilege escalation, broader filesystem/project access, new secret/credential access, host-level authority, governance/security-policy mutation, or a new/unrestricted network trust boundary. Ordinary already-authorised network use (approved registries, allowlisted services) is not by itself elevated. Every installation is recorded with its security and CIT evidence either way. |
| Consequence | P2-AR-0053's `ab0a075` implemented "always gate" and is superseded: its K3 change-control machinery is kept, its unconditional gating and its edit to `ws07::a_governed_security_review_by_another_role_lets_the_installation_proceed` are dropped. |
| Dispatched | **P2-AR-0055** on `phase2/repair-1-r4-residual-c` from `d96c8ab` with **P2-HO-0050**: compute the authorised envelope from trusted OS state (never the descriptor's own declarations — F4, BC-P2-39), fail closed and gated when anything cannot be evaluated, record which branch applied and why, and test both branches including every authority-expansion trigger and the allowlisted-network case. |

## P2-L-0028 — 2026-09-20 — OD-P2-03 implemented (P2-AR-0055); round-4 integration dispatched

| Field | Value |
|---|---|
| P2-AR-0055 | `READY_FOR_INDEPENDENT_CAPABILITY_VERIFICATION` on `phase2/repair-1-r4-residual-c` (product tip `4bd7468`, work `854980c`; `product_code_digest` `2fbbbd6c…9d82`). A tool installation raises the Human Gate only when it expands authority; otherwise an authenticated/pinned, independently reviewed, registered, reversible install inside the project's authorised envelope proceeds ungated, and every installation is recorded either way. The envelope is computed from trusted OS state (`TOOL_PERMISSIONS`, `AUTHORITY_POLICY`, the path map, `DATA_SENSITIVITY`/`SECURITY_POLICY`, `TOOL_POLICY.installation_envelope`, the kernel tool registry's `network_allowlist`) plus what the OS itself reads in the installation's commands — never from the descriptor's declarations (F4, BC-P2-39). The verdict is derived at request, at CIT-P (inside the bound impact) and again at CIT-E, which refuses and rolls back if the envelope changed. Rule written in `CHANGE_POLICY.change_classes.tool_installation` and `TOOL_POLICY.installation_envelope`, enforced entries in `ENFORCEMENT_MAP`, carried by governed decision record `spec/decisions/D-0011.yaml`; `POLICY_PRECEDENCE` unchanged (its immutable catch-alls already cover the new keys, shown by a weakening probe). |
| Evidence (builder claims) | lib 267/0; certification 203/0/0 in fourteen chunks all at `4bd7468`, union equal to the full list; Python 4/0; 0 warnings; R1 all four at baseline; census 123 files/2356 functions, 0 §6 violations in every splitter configuration; failure messages identical to P2-AR-0053's. Tests added: one per authority-expansion trigger with a non-elevated control, the allowlisted-network control in three states, a fail-closed-at-the-write test, and a lib test that the OS reads the installation's own commands. `ws07::a_governed_security_review_by_another_role_lets_the_installation_proceed` restored to asserting no gate, and strengthened. No test renamed, removed or ignored. |
| Disclosed for the verifiers | The command-token envelope derivation is a kernel floor, not process confinement — which is why the ungated branch also requires the independent review. `privileged_plugin_acquisition` census differs by splitter (13/3 vs 12/2) on `tools::network_allowlist`; 0 violations in every configuration. |
| Dispatched | **P2-AR-0054**, fresh round-4 integration builder, `phase2/repair-1-r4-integration` with P2-HO-0049: merge `phase2/repair-1-r4-ws01` and `phase2/repair-1-r4-residual-c`, reconcile the evidence map against the residual branch's new tests so `gov contract verify` passes (IP-R4-WS01-3), regenerate the matrix with the product, run every suite and all four R1 suites. Its tree becomes `cap2-candidate-1`. |

## P2-L-0029 — 2026-09-20 — Round 4 integrated; **cap2-candidate-1 minted**; verification iteration 1 dispatched

| Field | Value |
|---|---|
| Integration | P2-AR-0054 merged `phase2/repair-1-r4-ws01` and `phase2/repair-1-r4-residual-c` `--no-ff`, both conflict-free, with one change beyond the merges: 36 additive evidence-map owners for the residual branch's 19 new tests, applied through P2-AR-0042's documented route and regenerated by the product (R4-IP-2 / IP-R4-WS01-3). No Rust, policy, schema, KERNEL.yaml, migration, fixture or test file changed. Verdict `READY_FOR_INDEPENDENT_CAPABILITY_VERIFICATION` — builder claims, not acceptance. |
| Orchestrator reproduction at merge `0bad524` | `cargo build --release` ok, **0 warnings**; `gov contract verify` **CONTRACT_SOURCE_BOUND**; `cargo test --lib` **276/0**; `cargo test --test certification` **207/0** (1058 s). Matches the integrator. Regression reproduction only — not a verdict. |
| Candidate | **`cap2-candidate-1`** tagged at `0bad524`: `product_code_digest` `e6332fc7…2220`, `governed_state_digest` `3d2aeba2…20c0`. `GATE-P2-REPAIR-1` SATISFIED (rounds 1–4 integrated). `GATE-P2-R1-PRESERVATION` **reopened**: the candidate's product code differs from `srr1-r1-accepted`, so AC-14 requires a fresh independent R1-preservation verification. |
| Verification iteration 1 | Eight fresh independent verifiers dispatched on the candidate, all `model: opus`, isolated worktrees, none a builder: **P2-AR-0044** AC-14 R1 preservation (P2-HO-0045), **P2-AR-0045** AC-6 oracle format (P2-HO-0046), **P2-AR-0046…0051** families alpha, beta, gamma, delta, epsilon, zeta (P2-HO-0044), all under the common protocol P2-HO-0043. Each labels every finding RESIDUAL or MATERIALLY_NEW against the iteration-0 inventory and disposes of every prior finding in its scope. The fresh synthesis verifier **P2-AR-0052** (P2-HO-0047) follows and is the sole issuer of the verdict. |
| Owner stop condition | Recorded in the state and P2-CP-0010: a non-acceptance stops Phase 2 for owner review rather than starting repair iteration 2. |
