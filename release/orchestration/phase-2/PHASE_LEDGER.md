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

## P2-L-0030 — 2026-09-20 — Verification iteration 1: first two verdicts recorded (AC-6 and AC-14)

| Field | Value |
|---|---|
| P2-AR-0045 (AC-6) | **`ORACLE_FORMAT_ACCEPTED`** at `format_sha256` `f89a3e2f…16fd`. Coverage established against the owner-source bytes with the verifier's own parser (35 Gate V bullets + 5 prose statements, 0 problems); 93-sample attack matrix 93/93 as expected; 11 physical separation attacks (4 succeeded → finding V1-OF-01); G6 entry point exercised with typed refusals, `FORMAT_SAMPLE` never counting as qualification. BC-P2-51 disposed **CLOSED** limb by limb. Six findings, none blocking AC-6; MEDIUM V1-OF-01 (leak scan misses record-typed manifests, reflowed hidden truths, fault/class ids) and V1-OF-02 (eleven score-report metrics unbound) are for the synthesis verifier to dispose of. `GATE-P2-ORACLE-FORMAT` recorded SATISFIED. |
| P2-AR-0044 (AC-14) | **`R1_PRESERVED`** — `ROT_PHASE1_CANDIDATE_ACCEPTED_R1` remains valid for `cap2-candidate-1`, not re-issued (§9.3). All four prior suites at baseline (26 files cmp-verified byte-identical, run twice under ambient and stripped environments); AR-0033 `hv_a::a1` judged on its property — 123 files / 2392 functions, 0 §6 violations. 41 fresh held-out tests over the changed areas: the T2 binding authority (with a positive cross-machine control and refusal for a foreign owner), `gov update` admission under OD-P2-02 with payload consistency, tamper detection and rollback, the relocated OS stores, and OD-P2-03 tool-installation change control against nine attacker declarations. **All twelve frozen R1 items hold**; HO-0033 structural invariants 8/8 with no count changed. Regression reproduced by the verifier: lib 276/0, certification 207/0. `GATE-P2-R1-PRESERVATION` recorded SATISFIED for this candidate. |
| Findings carried | V1-R1P-01 (LOW, MATERIALLY_NEW): `paths::relocate_legacy` treats two **unreadable** files as identical and deletes a non-rebuildable legacy store claiming it was identical — a different mechanism from BC-P2-31, in the function that repair wrote. Open for the synthesis verifier. |
| Orchestrator tooling fix | V1-R1P-02: `tools/product_identity.py` printed the **tag object** for annotated tags, so `srr1-r1-accepted` appeared as `b78b5c68…` rather than `c7d3fefa…` — and every iteration-1 verifier is told to treat an identity mismatch as a STOP. Fixed to resolve `<rev>^{commit}`; digests unchanged (re-checked on `srr1-r1-accepted` and `cap2-candidate-1`). Non-product orchestration tooling. |
| Disclosed deviations | P2-AR-0044 listed the session task-output directory once before recognising it and opened no file; its consolidated `RUN-ALL` re-run was stopped under machine load after being exercised end to end, with per-section transcripts retained. Recorded for the synthesis verifier to weigh. |

## P2-L-0031 — 2026-09-21 — Verification iteration 1: **cap2-candidate-1 REJECTED**; Phase 2 stopped for owner review

| Field | Value |
|---|---|
| Verdict | **`GOVERNANCE_CAPABILITY_BASELINE_REJECTED`** by **P2-AR-0052**, a fresh independent synthesis verifier and the sole issuer. AC-3, AC-4 and AC-5 unmet; the other thirteen hold. The orchestrator records the verdict and neither confirms nor overrules it. |
| Verification iteration 1 | Nine runs, all recorded and merged: P2-AR-0044 `R1_PRESERVED`, P2-AR-0045 `ORACLE_FORMAT_ACCEPTED` (`format_sha256 f89a3e2f…16fd`), P2-AR-0046 alpha (2 blocking; cross-machine attack 74/74), P2-AR-0047 beta (1 blocking; AC-7 holds), P2-AR-0048 gamma (3 blocking), P2-AR-0049 delta (0), P2-AR-0050 epsilon (1 blocking; AC-5 not met), P2-AR-0051 zeta (0; AC-8 met), P2-AR-0052 synthesis. The synthesis verifier re-ran every family suite and reproduced every recorded figure exactly, confirmed all 55 verifier findings, refuted none, corrected one label (delta's M1 → CANNOT_UNDERMINE) and raised one finding of its own (S1-A1-01, correcting alpha's A1 to PARTIAL after reconciling it with gamma's demonstrated overlay edit). |
| Blocking | 8 findings over 7 classes: BC-P2-53 (new — `installation_authority` defeated by interpreter wrapping), BC-P2-41 (review not bound to the installation), BC-P2-45 (three project overlay files bypass `POLICY_PRECEDENCE`), BC-P2-33 (adoption stalls at A6 on a tree the OS itself classified secret), BC-P2-37 (trust report from an unauthenticated release field), BC-P2-32 (failure memory has four kinds with no writer), BC-P2-07 (a tier run leaves a third of its declared membership unevaluated and reports complete). |
| Convergence | 52 iteration-0 classes: 37 CLOSED, 14 PARTIALLY_CLOSED, 1 RESIDUAL; 193 findings: 142 CLOSED, 43 RESIDUAL, 8 N/A. `introduces_materially_new_blocker_classes: true` (BC-P2-53). **Counter 1 of 3.** Both consequential labels were checked in the direction that would have reduced the count and neither was shaded. |
| Owner decisions | The verifier records **none** required, explicitly, and adjudicated zeta's cross-repository candidate and alpha's posture flag as not owner decisions at this gate. |
| Stop | Under the owner's condition of 2026-09-20 the orchestrator stopped after recording the evidence: no repair iteration 2, no repair or build agents, no candidate change. Decision package `PHASE_2_DECISION_PACKAGE.md`; checkpoint `P2-CP-0011`; continuity handoff `P2-HO-ORCH-0003` (supersedes -0002). Orchestrator assessment of the failure's nature, recorded in the package: primarily implementation (five classes), one architectural question (BC-P2-45/-53, whether the envelope's authorising documents should be OS-protected state) and one orchestration lesson (the new class sits in last-round code merged on builder claims; earlier rounds with more adversarial passes produced no new class). |

## P2-L-0032 — 2026-09-21 — Repair iteration 2: provider experiment paused; native Sonnet 5 routing adopted

| Field | Value |
|---|---|
| Owner routing policy | Outer orchestrator and formal acceptance verifier: **Opus 5**. Architecture/security synthesis: Opus 5. Difficult cross-cutting and normal engineering repair: **Sonnet 5**. Cheap mechanical work: **Haiku**. Build/test/schema work: deterministic tooling. Defaults, not an inflexible rule — a task is promoted when evidence shows its tier inadequate. Effort is chosen for the problem rather than front-loaded at maximum. Model selection is **per spawn**, never a global setting that would alter the orchestrator. |
| DeepSeek | **Paused as an execution provider** until the owner explicitly re-enables it. Everything it produced is preserved as V8.3 input: `tools/api_worker.py` (formerly `ds_worker.py`), `tools/worker_bootstrap.py`, `tools/prep_packet.py`, `packets/**`, `telemetry/P2-R2-MODEL-TELEMETRY.jsonl`, `telemetry/checkpoints/**`, and the six `phase2/repair-2-*` branches. |
| What the experiment produced | Five of seven blocking classes carry claimed repairs. Verified by the orchestrator's own full-suite runs: **WS-C 208/0**, **WS-E 208/0**, **WS-G 209/0** clean; **WS-D** build 0 warnings, lib 276/0, no failing certification tests (exact count deferred to integration). **WS-B** and **WS-F** left honest PARTIALs with named residuals (9 and 2 failures, down from 20 and 7). WS-A not started. |
| Substrate lessons (V8.3 evidence) | (1) A model that can read a repository does **not** thereby know how the repository works: four of the first six provider runs explored heavily, wrote almost nothing and ran no checks until a governed bootstrap gave them the authority model, the quoted requirement, the conventions and the completion semantics. (2) The narrow per-task check list let workers claim repairs that broke other families — the full suite is now a required check before any repair claim. (3) The check wrapper piped cargo through `tail`, so a red suite reported exit 0; fixed with bash `pipefail` and an explicit PASS/FAIL, verified with a deliberately failing test (FAIL exit 101 through a pipe; PASS preserved). (4) Runs cost 1–3 hours each, mostly re-running a 20–30 minute suite; targeted tests during development with one genuine full run at the end is the right shape. |
| Native routing this round | **P2-AR-0064** (WS-B) and **P2-AR-0065** (WS-F) dispatched as fresh native Sonnet 5 subagents at high effort, continuing from the preserved branches and checkpoints rather than restarting, under the same bounded-scope, mutation-ownership, checkpoint, targeted-test-then-one-full-suite and no-weakening rules. Authority, independence, worktree isolation, evidence and held-out-test rules are unchanged by the change of model. |
| Next | WS-A (tool-install surface, BC-P2-53 + BC-P2-41) on Sonnet 5 only after WS-B establishes the trusted-overlay foundation, then strong independent adversarial review before minting `cap2-candidate-2`. With DeepSeek paused, that review is a fresh Opus 5 role. Formal acceptance verification remains fresh Opus 5. |

## P2-L-0033 — 2026-09-22 — Owner authorises Option A: one final bounded round, with a hard stop after it

| Field | Value |
|---|---|
| What happened first | P2-ADJ-0006's stopping rule **fired**. The structural round landed and P2-AR-0075 (fresh Opus 5, independent of every repair and both prior reviews) confirmed the classifier's fail-open default was genuinely inverted — but returned `RESIDUAL_DEFECTS` (2 HIGH, 1 LOW). The orchestrator stopped, as it had committed in writing to doing, and escalated with `PHASE_2_PRE_MINT_DECISION_PACKAGE.md` rather than ordering a fourth round on its own authority. |
| What the third review established | **All eighteen findings from the two earlier reviews are closed**, each by its own reproduction; every negative control passes; ordinary acquisition still works. The reviewer independently reproduced build 0 warnings, lib 280/0, certification **244/0** (2,742 s) and `CONTRACT_SOURCE_BOUND`. Its verdict on the stopping rule, verbatim: "**The inversion itself holds. What still breaks is the premise of the positive list, for two of its six names.**" |
| The two HIGH defects | **AR75-F1** (BC-P2-53): `cp` and `curl` are on `plain_argument_programs` on the stated ground that they carry no file-execution meaning — but `cp` writes *through* a symlink and `curl -K` reads the rest of its command line from a file. With the per-token scan treating a token as a path only if it contains a slash, six shapes install `not_gated` and write in the project's parent; five contain no slash, no `..` and no absolute path anywhere in argv, and two re-fire on every later `gov tools health`. **AR75-F2** (BC-P2-45 / OC-P2-04): `class` is authority-bearing via `tasks::contract_generated`, and `overlap_is_no_less_restrictive` deliberately does not compare it — so `{pattern: product/*.yaml, class: derived}`, stricter on every compared dimension, turns a refused `MUTATION_SCOPE_VIOLATION` into an accepted close with every reporting surface clean. `globprobe` confirmed the check **saw** the overlap and passed the rule. |
| AR75-F3 (LOW) | The second pair of eyes P2-AR-0074 asked for, and it matters for honesty: the justification written into the secret-class mutation exclusion is **factually wrong** — `decide` applies a later secret rule in full, so the appended rule's own `mutation` wins. Not exploitable today, for reasons the reviewer measured. |
| Owner answer | **Option A** (`OWNER-AUTHORISATION-P2-0006`, OA-P2-06): one final bounded round for exactly AR75-F1 and AR75-F2, plus correction of AR75-F3's reasoning, then one fresh Opus 5 adversarial review. AR75-F1 must be closed **without returning to an interpreter/program denylist** — by evaluating every relevant non-flag argument against the project boundary and proving escape behaviour including symlink-resolved destinations. AR75-F2 by treating `class` as authority-bearing in the restrictiveness/overlay comparison. |
| The stop the owner set | `cap2-candidate-2` must **not** be minted while either HIGH finding remains open; and if the fourth review finds another materially new HIGH blocker on the install-trust surface, or leaves AR75-F1 or AR75-F2 materially open, the orchestrator **stops and returns an architecture/meta-review package**. There is no fifth round on this surface without a further owner decision — a stricter stop than the orchestrator's own. |
| Dispatched | **P2-AR-0076** — capability repair, native Sonnet 5, worktree-isolated on `phase2/repair-3-boundary` (base `c34c439`), under handoff `P2-HO-0052`. Scope is exactly the three findings; `allow_write` is four files plus one new property-test file. Acceptance evidence must be a **property over the default** per P2-ADJ-0006, with the reviewer's shapes demoted to regression guards. Targeted tests while iterating; exactly one genuine full suite at the end. |
| Dispatched in parallel | **P2-PERF-0001** — performance diagnostician, native Opus 5, on `phase2/perf-diag`. Answers the owner's eleven questions about the ~2.5 h certification cost by deterministic instrumentation, labelling each answer MEASURED / INFERRED-FROM-RECORD / NOT DETERMINED. **Measurement only**: the owner barred a major performance refactor during this bounded repair. It gates nothing. |
| V8.3 | `V8_3_EVIDENCE_PACKAGE.md` opened as an explicitly **non-normative** input file for a fresh post-Phase-2 architecture session, covering the nine areas the owner listed. Its headline, from the provider telemetry: peak worker context was 41k–139k tokens against 120k–220k budgets and **no run ever approached its ceiling**, yet half returned `INCOMPLETE` — context size was almost never the binding constraint and task comprehension almost always was. V8.3 must not be designed, installed or activated until Phase 2 earns `GOVERNANCE_CAPABILITY_BASELINE_ACCEPTED`. |
| Record hygiene | Five pre-existing YAML line-continuations in `ORCHESTRATOR_STATE.yaml` (present since `c6b60bc`) were unfolded after the owner reported editor errors; the parsed state is byte-for-byte semantically identical, verified by comparing the loaded documents. `phase-1/ORCHESTRATOR_STATE.yaml` was checked and is untouched since `3374db4`, parses strictly, and has no duplicate keys. `GATE-REGISTER.yaml` was regenerated by `yaml.safe_dump` when `ESC-P2-0001` was added, which reformats the whole file; the parsed gates were diffed and no pre-existing gate changed. |

## P2-L-0034 — 2026-09-22 — Round 4 review: stop condition triggered on both limbs; architecture review escalated

| Field | Value |
|---|---|
| Repair | **P2-AR-0076** (Sonnet 5, `e25ca70`) landed both fixes cleanly. Orchestrator-verified: files exactly within `allow_write`, worktree clean, `cargo test --lib` 280/0, release build 0 warnings, and **one** full certification suite machine-exclusive at default threads from a verified-quiet machine — **252 passed / 0 failed / 0 ignored**, 2,966 s. It also reversed its own first approach on the orchestrator's objection, building a correctly-named `argument_indirection_flags` class rather than mislabelling `-K` as inline code, and disclosed three coverage gaps in its own work unprompted. |
| Review | **P2-AR-0077** (Opus 5, independent of every repair and all three prior reviews, `b96109d`) — **`RESIDUAL_DEFECTS`: 3 HIGH, 1 MEDIUM, 1 LOW.** Own harness from scratch, `review_subject` reimplemented and verified byte-for-byte against the product (4/4), and a **differential control** — the parent `c34c439` extracted and built separately — so every "closed" and every "materially new" claim is measured rather than asserted. |
| What the repair achieved | **Both AR75 witnesses are dead**, each proven to have fired at `c34c439` and to gate now. All three of the builder's self-declared gaps hold. **All twelve prior findings remain closed.** **Every negative control passes and there is no over-gating** — conforming installs proceed with zero gate records, `gov init` on brownfield refuses nothing, ~14 boundary edge cases are inert. OD-P2-03 requirement 6 holds. |
| Why it stopped anyway | Three **materially new** HIGHs. **AR77-F1**: `endpoint_host`'s `(!host.is_empty()).then(…)` means a `file://` URL with an empty authority skips the network branch and resolves *under* the root, so four shapes install ungated with zero gate records while writing outside the project — the `health_check` variant recreating its marker on every later `gov tools health`. **AR77-F2**: an absolute path embedded behind any prefix other than the first `=` is invisible to `token_values`/`leaves_project`; `curl --write-out %output{…}` writes outside the root ungated. **AR77-F3**: `class` has a **second** authority-bearing consumer, `is_production_path`, exempting **six** values where the repair compares **two** — one hand edit to a project-editable file silently converts a refused `EXPERIMENT_OUTPUT_IN_PRODUCTION` into an accepted experiment. Verified independently by the orchestrator at `tools.rs:1408`, `tasks.rs:1865-1868` and `policy_precedence.rs:586-587`. **AR77-F1 and F2 are pre-existing, not regressions** — they fire at `c34c439` too. |
| The meta-finding | Every failure on this surface has been an **enumeration** failure: programs, then shapes, then list entries' premises, now `class` values *and the set of consumers of `class`*. The P2-ADJ-0006 inversion **held** and is not the problem; what fails is that every exception to a fail-closed default is an enumeration nobody can prove complete. `curl` sits on `plain_argument_programs` because the suite needs it, on a premise now falsified three times for that one program. |
| The method finding | **P2-ADJ-0006 failed one level up.** Its property-over-the-default standard was met faithfully — and `repair4.rs:616` reads `for cand_class in ["generated", "derived"]` inside a test named "…for_any_class_value…". The builder wrote both the mechanism and its generator, so the generator's domain is the implementation's domain and the property proved is "the fix does what it does". The old failure encoded the last reviewer's shape list; this one encodes the implementation's own value set. This vindicates the owner's test-author-independence challenge, raised while the tests were still running, and extends the frozen contract's line 57 ("builder tests are regression evidence, not independent certification") to **property** tests, which the orchestrator had implicitly assumed immune. |
| Disposition | **STOPPED.** `cap2-candidate-2` not minted; no fifth repair round; no formal verification dispatched. `PHASE_2_ARCHITECTURE_REVIEW_PACKAGE.md` escalates with options A–E: (A) empty the exception list so installs must execute pinned artefacts; (B) constrain effects by isolation instead of predicting them; (C) make the `class` exemption set derived rather than enumerated; (D) re-scope the surface to R2; (E) mint and disclose. Orchestrator recommends **A + C** as a bounded round, notes **B** as the right long-term answer and beyond this phase, and marks **D** as the owner's alone. |

## P2-L-0035 — 2026-09-22 — Owner decides A + C: remove the pattern, not another enumeration

| Field | Value |
|---|---|
| Decision | **OD-P2-07.** A + C as one bounded **structural architecture remediation**, explicitly authorising continuation beyond OA-P2-06's stop condition. The owner's framing: *"Do NOT treat this as another local enumeration/patch round. The purpose is to remove the architectural pattern responsible for the repeated failures."* |
| Property A | **No raw or unbound command may acquire ungated installation authority.** The ungated path requires that every executed file be pinned in the descriptor and byte-verified immediately before execution; anything not reducible to an exact bound artefact is `undetermined` and gates. Adding another curl flag, command shape, program, path syntax or parser exception is **forbidden by name**. Raw commands may still run through a gate; ordinary acquisition survives by wrapping installation logic in a pinned reviewed artefact. |
| Property C | **Project-editable classification state cannot silently increase effective authority or obtain a governance exemption.** One authoritative predicate — *does this class confer any exemption from any governed control?* — from which every authority-bearing consumer derives. Adding the four missing values to another list is forbidden. The capability to classify paths as evidence/generated/derived through an **authorised governed change** is preserved; the defect is obtaining it by hand edit. |
| Applied first, before any dispatch | **Worker stall protection, `ACTIVE`** (owner §1), eight rules recorded in `ORCHESTRATOR_STATE.yaml` and validated at write time: no unbounded coordinator handshake; timeout **and** default action required; prefer self-evaluable preconditions; six distinct worker states including `BLOCKED_ON_COORDINATOR`; rising elapsed time with unchanged status is a stall signature; never report liveness from a stale observation. Procedural only — it touches nothing normative. Recorded as `IMPLEMENTED_DURING_PHASE_2`. |
| Evidence classes now fixed | `BUILDER_REGRESSION`, `BUILDER_DEVELOPMENT_EVIDENCE`, `INDEPENDENT_ADVERSARIAL`, `HELD_OUT_ACCEPTANCE` — never collapsed into "tests passed". **A property test is not independent merely because it is generative**: P2-AR-0077 showed a test named *"for any class value"* quantifying over exactly the two values its own author implemented, against a real vocabulary of six. When one worker defines both the implementation and the generator's domain, the two share a blind spot. This supersedes P2-ADJ-0006's weaker "acceptance evidence must be a property". |
| V8.3 reconciled | §6.3e evidence classes; §6.3f the five failed enumerations (programs, shapes, list premises, class values, **consumers**) with the transferable rule that *a fail-closed default is weakened by exceptions whose completeness cannot be proven*; §6.3g cross-check independence; §6.3h derived verdicts and substrate-enforced checkpoints; and **§5.0 CURRENT TRUTH**, which supersedes every later figure in §5 — full suite **≈50 min**, single-threaded ≈2.5 h, penalty **≈3×** (not 7×), scheduling floor **≈40–43 min**, milestone SLO **≤55 min**, all retracted figures labelled as such. |
| Dispatched | **P2-AR-0078**, fresh Sonnet 5, worktree-isolated on `phase2/remediation-ac` off `e25ca70`, under `P2-HO-0054`. Its brief carries the anti-enumeration framing, an explicit pre-authorisation to change what existing raw-command tests assert (stricter, never weaker, no renames, each listed), a requirement to verify rather than assume that `review_subject` binds argv, a requirement to survey **all** `class()` consumers and justify which are descriptive, and the stall-protection rule that it must evaluate its own machine precondition rather than wait for the coordinator. |
| Hard stop ahead | After the implementation freezes, one fresh Opus 5 independent adversarial/property review that did not implement, did not participate in the builder session and did not author its tests. If it finds another materially new HIGH on the install-trust architecture, the raw-command authority boundary, the authority-enumeration pattern or project-editable exemption semantics — **or leaves a known HIGH materially open** — the orchestrator STOPS and returns to the owner, escalating toward Option B rather than another local round. |
| Option B | Recorded as deferred, high-priority post-Phase-2 architecture input: *constrain executable effects through an isolation/sandbox boundary rather than depending on complete semantic prediction* — **predicted effect is weaker than enforced execution boundary**. Not authorised for this remediation. |

## P2-L-0036 — 2026-09-23 — A+C implemented; orchestrator closes the evidence gap at 263/0; implementation frozen for independent review

| Field | Value |
|---|---|
| Implementation | **P2-AR-0078** (Sonnet 5, `35461c9`) returned an honest **`PARTIAL`** — both properties implemented, but the one required full certification suite never run, and it said so rather than claiming it. Scope verified: files changed exactly within `allow_write`, worktree clean. |
| Property A as built | `plain_argument_programs` shrunk from six names to `["true","false"]`, `cp`/`curl`/`sudo`/`apt-get` removed with **no replacement parsing rule**. The structural fix is a new `Unreadable` enum separating `Opaque` from `UnrecognisedProgram`: every unreadable reason still gates, but only the latter also runs the per-token scan, so **the human at the gate still learns why** — which is why the seven-sub-case `a_tool_installation_is_gated_for_each_way_it_expands_authority` passed with zero edits. `review_subject` was verified **operationally** to bind argv, not assumed: `installation_subject` hashes the whole descriptor minus only gate/approval/status metadata. |
| Honest disclosure | **AR77-F1, F2 and F4 close *by construction*, not by fixing their bugs.** The empty-authority `file://` bug and the hard-link blindness remain untouched in the code, unreachable only because `curl`/`cp` left the list — and the builder's own hard-link test **explicitly asserts that `broader_filesystem_or_project_access` does not fire**, proving the residual rather than hiding behind a green test. |
| Property C as built | One `CLASS_EXEMPTIONS` table plus an `Exemption` enum in `paths.rs`; `contract_generated` and `is_production_path` both derive from it; `overlap_is_no_less_restrictive` checks it generally, so **all six exempting values are protected and a future class added to the table needs no change to that function**. AR77-F3's exact exploit reproduced end-to-end and proven refused, reported via `gov policy overrides` and D027, and without effect on `is_production_path` — with a positive control proving the governed capability survives. |
| Judgement calls, all flagged by the builder | `derived_deletion_set` left separate (operational, and coupling it could let a future exemption silently widen deletion scope); `SECRET_CLASS`/`historical` branches judged narrowing-only, which OC-P2-04 permits freely; `lineage.rs` W7/W11 judged **descriptive**; and nothing mechanically prevents a future consumer writing its own `matches!` again — only doc comments naming AR77-F3 as the failure mode. |
| Test assertions changed | Six, under the P2-HO-0054 §2a pre-authorisation, **no renames**, each listed with old and new claim. Raw `curl`/`cp` installs that asserted *ungated* now assert *gated* — and each change is paired with a positive control proving a **pinned wrapper script still installs ungated with zero gate records**, so Property A did not become "gate everything". |
| Evidence gap closed by the orchestrator | The worker's declared gap was the full suite. The orchestrator ran it on `35461c9`, machine-exclusive at default `--test-threads` from a machine verified idle by `pgrep` (load 0.90, zero competing processes): **263 passed, 0 failed, 0 ignored**, 3,084 s, exit 0, reconciling exactly as 252 previous + 11 new. CPU 41,622 s over 3,199 s wall = **P 13.0**, consistent with the 12.95 measured independently on the previous tree — the corrected performance model reproducing itself. |
| Builder-declared generator gaps | Six classes named unprompted, including the one the builder judged most likely to be wrong: adversarial argv attacking the **`UnrecognisedProgram` decoupling** rather than the list shrink. Also: the 23-program sweep is itself hand-enumerated; the 4×3 overlap shapes do not cover the full glob grammar; no non-UTF8, Windows or TOCTOU coverage; the `lineage.rs` call was reasoned, not tested; `derived_deletion_set`'s separation was never exercised against a real deletion run. |
| Frozen and dispatched | Implementation **FROZEN** at `35461c9` per OD-P2-07 §7. **P2-AR-0079** dispatched: fresh Opus 5, `INDEPENDENT_ADVERSARIAL` evidence class, on `phase2/remediation-ac-review`, under `P2-HO-0055`. Briefed to derive its own attack domain, and aimed first at the builder's own nominated blind spot, then at whether **another route still reaches the two unfixed bugs** — since closed-by-construction holds only while the construction holds. |
| Hard stop live | If P2-AR-0079 finds another materially new HIGH on this architecture, or leaves a known HIGH materially open, the orchestrator STOPS and returns to the owner, escalating toward Option B rather than a further local round. |

## P2-L-0037 — 2026-09-23 — A+C independently reviewed: both properties FAIL; stop condition triggered on both limbs; escalate toward Option B

| Field | Value |
|---|---|
| Review | **P2-AR-0079** (Opus 5, `INDEPENDENT_ADVERSARIAL`, `d296e6b`/`7f78ede`) against the frozen `35461c9` — **`RESIDUAL_DEFECTS`: three materially new HIGH**, plus AR77-F1/F2/F4 narrowed but not closed. Its own judgement: *"Is the architecture sound? No."* It registered its 2,461 lines of probes as a **separate `[[test]]` target** so the orchestrator's 263/0 figure stayed meaningful and the evidence classes stayed distinct — enforcing OD-P2-07's evidence separation at the build level rather than only in a report. |
| **P79-F11** (HIGH, new) | **Verified bytes are not the executed bytes, on the *conforming* path.** `env --chdir=decoy sh install.sh` with `install.sh` correctly pinned: the OS hashed and verified `<root>/install.sh`, declared it readable, installed **ungated** — and the kernel executed `<root>/decoy/install.sh`. **Orchestrator-verified**: `tools.rs:995` skips any `-`-prefixed token so `--chdir=decoy` is consumed and `prog` becomes `sh`; `util.rs:322` sets `current_dir` to the root but `env --chdir` overrides it after the process starts. **It defeats pinning itself and does not depend on `plain_argument_programs` at all** — Option A's core deletion closes P79-F1 and leaves this untouched. `env -C decoy` gates; `env --chdir=decoy` does not. |
| **P79-F1** (HIGH, new) | `env PATH=. true` installs ungated and the kernel executes `<root>/true`, a project file in no `pinned_files` entry, hashed by nothing. **Orchestrator-verified**: `tools.rs:994` consumes every `NAME=value` token, and `util.rs:320` execs with **no `env_clear()`**, so the inherited environment rebinds the program after classification. 26 of 26 rebinding shapes classify readable. The product **already** treats loader variables as code substitution for plugins (`binding::LOADER_ENV_VARS`, BC-P2-40); the install envelope does not. |
| **P79-F8** (HIGH, new) | **The "single authoritative predicate" is one-directional**: it models classes that *grant exemptions* and cannot express the *obligations* `class` carries. A hand edit appending `{pattern: "product/*.py", class: test}` confers no exemption, is equal on every compared field, and is **accepted, applied, refused by nothing and reported nowhere** — `gov policy overrides` empty, doctor **D027 passes**. Effect with its own control: a `documentation`-class task changed `product/app.py` and **closed**, where the identical task is refused `MATERIAL_CHANGE_REQUIRES_CIT` without the edit. **Orchestrator-verified**: `policy_precedence.rs:677` refuses only a *gained* index flag, and 12 further `class()` consumers sit in `cit/`, `context/` and `memory/` alone. |
| The generalisation | **The check reasons about a representation; the effect comes from somewhere the representation does not cover.** For A the representation is `argv` and the effect comes from the environment and cwd; for C it is "exemptions gained" and the effect comes from obligations lost. Five rounds, five enumerations: programs → command shapes → list-entry premises → class values → consumers of class → **obligations of class**. |
| What the remediation did achieve | AR77-F3 genuinely closed for all six values; every previously closed attack still closed (AR68-F1..F5, AR73-F1/F2/F4/F5/F6, AR75-F1/F2 across 72 cases, with 210 `HDG-*` records written confirming gates are real); `review_subject` independently re-derived to bind argv; pin re-verification at execution lifetime holds; **every negative control passes and the surface does not gate everything** — a conforming pinned install runs ungated with zero gate records *and the script actually executes*; **1,176 adversarial cases produced no panic, no non-JSON answer, always gated, never installed**; full suite green at **263/0** on the orchestrator's own machine-exclusive run. All six changed test assertions audited against `git show 35461c9` — each stricter or equal-plus-more, **none weakened to pass**. |
| The builder's judgement calls, graded | `["true","false"]` residual **WRONG** and the direct cause of P79-F1; `argument_indirection_flags` **RIGHT and load-bearing**; `derived_deletion_set` **RIGHT** on reasoning but **not probed**, and the reviewer declined to grade what it had not tested; `lineage.rs` **HALF WRONG** — and routing it through the predicate would not have helped, because membership is an *obligation* the predicate cannot express, which **is** P79-F8. |
| The prerequisite the owner must settle | **P79-F10**: the product has **no mechanism anywhere** to distinguish a governed contract change from a hand edit — the reviewer searched and found none. Until that exists, "require change control for class changes" cannot be implemented, so **Property C cannot be completed**. The reviewer deliberately graded it MEDIUM rather than HIGH because the builder's own test asserts this as the *preserved capability*, making it architectural rather than a slip. |
| Disposition | **STOPPED.** No mint, no sixth round, no formal verification. `PHASE_2_OPTION_B_ESCALATION_PACKAGE.md` escalates. Orchestrator recommendation: authorise the **minimal execution-boundary** work for A (controlled environment, pinned cwd, execute the verified artefact by resolved absolute path rather than by the `argv` string) — Option B's principle applied at its cheapest increment, closing two proven HIGHs at the root rather than by enumeration; for C, **decide the F10 prerequisite first**; and consider re-scoping to R2, which is the owner's alone. |
| Record hygiene | The orchestrator broke `ORCHESTRATOR_STATE.yaml` once more while editing it (a flow-sequence replacement left `running_work:` and `[]` on separate lines) — caught immediately by parse validation before sealing, repaired, and two stale `RUNNING` rows corrected to their true terminal states in the same pass. This is the same recurring weakness already recorded in the V8.3 package at §6.2, and the reason the owner's §14 requires write-time validation. |

## P2-L-0038 — 2026-09-23 — Trust-architecture prior-art study complete; two corrections owed to the owner

| Field | Value |
|---|---|
| Nature | **Read-only decision support.** No product, runtime, kernel, policy, schema or test file was modified; nothing was implemented; Phase 2 stayed STOPPED throughout, under a standing prohibition on adopting anything the study found. |
| Shape | 6 researchers (Sonnet 5) → synthesis (Opus 5) → independent challenge (Opus 5) → amended synthesis. ~5,900 lines of evidence under `RESEARCH/`. Owner report: `TRUST_ARCHITECTURE_EXISTING_SOLUTIONS_REVIEW.md`. |
| **Correction 1** | **P79-F10 is wrong.** The escalation package told the owner the product has no way to distinguish a governed change from a hand edit, and that Property C could not proceed without building one. `runtime/src/cit/binding.rs` already implements exactly that — T2-sealed, bound to an owner-signed Human Decision Gate, with *"consumers never trust the record's top-level fields for an authority decision"* and *"a hand edit of any field breaks the whole-record seal"*. `t2::seal_value`/`seal_record`/`verify_file` are general; `SEALED_RECORD_TYPES = ["human-gate","cit","task"]` and the path map is simply not a member. The reviewer had said its search was "targeted, not exhaustive"; the orchestrator relayed the conclusion without testing it. |
| **Correction 2** | **The Property-A fix the orchestrator recommended is measured wrong on two of three limbs.** Under a *fully cleared* environment with cwd pinned to the project root, `env --chdir=decoy sh install.sh` still ran the decoy and `env PATH=. true` still ran the project-local binary; only executing the resolved absolute artefact ran the verified bytes. `env` is not an environment variable — it is a program, and `PATH=.`/`--chdir=` are arguments it applies after `gov` has lost control. Everyone — six researchers, the escalation package, the orchestrator — inherited the brief's framing of P79-F1 as an *environment* defect. It is a *wrapper-execution* defect. |
| **The study then did it to itself** | The challenger defeated the synthesis's own replacement fix by execution: a hash-pinned artefact with `#!./w` ran an unpinned project file, and the control proves the attack **requires the cwd the OS itself pins** — the mitigation supplied the attacker's resolution root. `#!/usr/bin/env -S PATH=. sh` discarded the OS-constructed environment one exec hop later. Cause: `execveat` hands the kernel a verified *object*, and the kernel then performs a **second resolution from bytes inside it**. Three levels, same shape, each time caught by measurement rather than argument. |
| What the study established | The defect class is the **confused deputy** (Hardy 1988), with Miller 2006's *No Ambient Authority* as its formal statement — five rounds rediscovered it in a private vocabulary. The product's own `tools.rs` already concedes *"the OS cannot confine a spawned process"*. `PathDecision` is constructed at **exactly one site**, so OD-P2-07 C's "find all consumers" is dischargeable **by typing**, not search. `class` is a **label, not a level**, so the bidirectional predicate the escalation package offered is impossible. Landlock is real here (ABI 3, unprivileged, measured) but closes **no open HIGH**. |
| Recommendation | **Option 1 — resolve once, execute the object; floor the class.** Four changes, no new dependency for the minimum, deletes 45 of 106 envelope entries + a 30-entry loader denylist + ≈250 lines, net TCB reduction, reversible at code level. Option 2 (+ Landlock) is the R2 successor. Option 3 (full hermetic execution) **needs Option 1 inside it regardless** — `./w` is a declared input, so both defeats survive a bubblewrap jail. |
| Carried forward, unresolved | **P1** (precondition): `gov adopt` native layouts are unfloored, so floor composition closes **zero** of P79-F8/F9 there. **P2** (obligation, not run): pinned dynamically-linked ELF with project-controlled `RUNPATH`/`$ORIGIN`/`LD_*` — `LOADER_ENV_VARS` is stripped on the plugin path only. Plus: the T2 seal is HMAC under a symmetric key readable by an agent on the owner's account — *"detection-grade, not proof"*, and a forgery is honoured on the owner's other machines. And `pinned_files` appears 7 times in `tools.rs` and 0 times in its schema. |

## P2-L-0039 — P2-AR-0092 returns RESIDUAL_DEFECTS; AR92 repair dispatched (2026-09-24)

The sixth independent adversarial review of `a01f0c9` returns **`RESIDUAL_DEFECTS`**, committed at `4686e8d` on
`phase2/review-6` with product source untouched (verified by the orchestrator).

**Property A HOLDS for the second consecutive round.** The AR90-F2 over-gate repair is correct in both directions and
AR88-F4 is not re-opened (both proved by the reviewer's own probes). No divergence constructible.

**Property C FAILS.** `other_live_claim` — the first mechanism in six rounds to ask a question the attacker cannot
answer for the OS — conditions its answer on `Path::exists()` of an attacker-chosen string. Four HIGH: the donor can
be moved aside (C1, measured **permanent**), made unreadable so `exists()` fails open on `EACCES` (C1B), or minted
*inside the victim* so that **the owner's own rename** completes the attack with no attacker move at all (C1C); and
the sandbox exemption is a four-component path-shape match reachable by `mkdir -p` outside any governed project
(C2). Two MEDIUM: a second same-machine checkout permanently loses its floor (C3, pre-existing); a bare relocation is
silent (C4) — and that silence is the enabling condition for every HIGH.

All seven OD-P2-08 §8 stop conditions were evaluated and answered NO. The orchestrator independently re-verified the
three that decide it: portability survives dropping the conjunct (`resolve_state_root` is per-machine and env-locked
once provisioned); `project_identity` is a v4 uuid never derived from repository content, so "any entry, live or
stale" opens no pre-poisoning denial channel; and `is_health_sandbox_root` consults no OS record.

**Disposition: automatic repair per §8.** `P2-AR-0093` dispatched on `P2-HO-0057` from `4686e8d`, with four
non-deferrable obligations — delete the liveness conjunct; grant the sandbox exemption from the OS's own record;
**demonstrate a working re-anchor remedy end-to-end**; disclose the relocation. The third is the escalation trigger:
if fail-closed relocation cannot be given a working exit without inventing a new trusted authority, that is a genuine
§8 stop and returns to the owner.

Both repairs are deletions and substitutions, and both are smaller than any predecessor's. Seventh enumeration
failure recorded: programs → shapes → list premises → class values → consumers → obligations → **a liveness predicate
on an attacker-chosen string.**

## P2-L-0040 — P2-AR-0093 lands all four non-deferrable obligations (363/0); seventh review dispatched (2026-09-24)

`a376cc4` on `phase2/remediation-ar92`, base `4686e8d`, full suite **363/0** in 3,486 s at default threads. Product
diff confined to five files; `exec_resolve.rs` untouched, so Property A is carried forward unmodified.

**All four §1 obligations landed.** The `&& Path::new(minted_for).exists()` conjunct is deleted (`paths.rs:765`), so
`other_live_claim` now refuses on any store entry at a different path, live or stale. `is_health_sandbox_root`
requires an OS-written marker under the protected state root in addition to the four-component shape. `gov
floor-reanchor` exists, gated at the **same `install_kernel` tier as `init`** — the §1.3 escalation trigger did
**not** fire, because no new trusted authority was invented — and is demonstrated end-to-end. A genuine foreign
clone's bootstrap adoption is now disclosed through a channel deliberately separate from D027.

**Orchestrator verification.** Each of the four mechanisms read and confirmed at the commit. One suspected G0 bypass
chased and **ruled out**: `command_name` spells the command `"floor-reanchor"` while `COMMAND_GUARDS` holds `"floor
reanchor"`, but `g0_label` — the authority-bearing mapping — matches, and `command_name` feeds display only. The two
parallel hand-maintained label tables are handed to review 7 as the AR90-C6 / AR92-D2 defect class.

**The builder's disclosures were good and are the reason this round is reviewable.** It declined to claim AR92-C3
closed, stating plainly that re-anchoring is an identity **transfer** that removes the prior entry, so running it
from a second live checkout steals the identity from the first. It named the missing positive control for a
legitimate sandbox, the `health-sandboxes/` marker leak, unprobed concurrency, and that re-anchor never reads
`bound_cit`.

**Dispatched `P2-AR-0094`** on `P2-HO-0058` at `a376cc4`, branch `phase2/review-7`, with two primary targets — both
the mechanisms this round introduced, per the standing prediction that each repair's new mechanism is the next
round's defect. The orchestrator derived and handed over one attack chain: `Sandbox::create` bases sandboxes at
`p.runtime_dir()`, **inside the project**, so the random sandbox path is observable by an ordinary project-scoped
actor; if the marker leaks because `Drop` never ran, recreating a directory at that observed path may reconstitute
the exemption. The builder classified that leak as storage hygiene; this round made the marker authority-bearing,
which is why it is now a capability question and not a hygiene one.

## P2-L-0041 — P2-AR-0094 returns RESIDUAL_DEFECTS; AR94 repair dispatched; convergence question raised with the owner (2026-09-24)

The seventh independent review of `a376cc4` returns **`RESIDUAL_DEFECTS`**, committed at `f2a9ab9` with product
source untouched.

**Property A holds for the third consecutive round** — `exec_resolve.rs` unchanged, closure re-run 22/0, the
predecessor's held-out probes unmodified and green.

**Property C fails on both mechanisms this round introduced**, exactly as the standing prediction says.
**AR94-C2 (HIGH)** is the sharpest finding in the phase so far: `reanchor_project_identity` reads
`bound_project_identity` **from the floor document**, then scans the store for that identity and moves it — it never
asks whether this checkout is entitled to it. The T2 seal carries no path or identity (AR84-C3) and git lineage is
public (AR86-C1), so the attacker's whole contribution is **one project-scoped file copy**; the owner completes it by
relocating their own checkout and following the advice the OS itself prints. **AR94-C1 (HIGH)**: the sandbox marker
is a capability and minting one is free — the adversary kills their **own** `gov` process, since `remove_sandbox_record`
has exactly one caller, in `Drop`, and there is no GC. Three MEDIUMs compose with these.

**Orchestrator verification.** C1, C2 and C3 each confirmed by reading the code at `a376cc4`. The reviewer's
adjudication of the previous builder's changes to two held-out probes was checked against AR92's own text and is
sound: `ar92_c4` was a strengthening of a probe that still passed; `ar92_c3`'s original contradicted its own author's
measurement, prose, severity and repair direction. The docstring's claim that a working remedy answers the cost is
false, and that is AR94-C4.

**Dispatched `P2-AR-0095`** on `P2-HO-0059` from `f2a9ab9` with five non-deferrable items. Both HIGH repairs are a
**deletion** (the durable marker, replaced by a process-local registry that cannot leak) and a **narrowing** (`--from`,
taking the identity from the store and making the operator name it). The brief forbids adding a third mechanism to
guard the second, and explicitly warns that the reviewer's child-process suggestion rests on an environment variable —
ambient authority, the class this phase exists to refuse.

**Raised with the owner, not decided here.** Seven reviews under Option 1, every one finding something, with the
defect each time in the mechanism the previous repair introduced. OD-P2-08 §8's seven stop conditions are all NO and
none of them is a round budget, so the loop has no terminating condition other than a reviewer finding nothing. The
repair proceeds meanwhile — both findings are HIGH, and §10 requires every HIGH closed before minting under any
policy the owner might choose — so nothing is blocked while they consider it.

## P2-L-0042 — OD-P2-09 and OD-P2-10 recorded; the loop gains a budget and a conditional exit (2026-09-24)

Two owner records land while `P2-AR-0095`'s certification suite runs (left untouched per OD-P2-09 §3; liveness
verified from process state, not assumed).

**OD-P2-09** closes the round-budget gap the orchestrator raised after review 7. **Review 8 is the convergence
decision point**; there is no automatic Review 9 on the same mechanism-hardening loop. The simplification principle
becomes binding: an optional recovery feature that repeatedly produces HIGH findings is **deleted or simplified, not
wrapped**. A mandatory pre-final owner-question sweep precedes Review 8, and three questions must be checked
explicitly — whether `floor-reanchor` is required at all, concurrent re-anchor semantics, and sandbox exemption
lifetime. The acceptance standard is stated finitely and explicitly is **not** "no conceivable defect can ever be
found".

**OD-P2-10** adds one mandatory step before Review 8 — a **whole-system / impact context pack** — and one conditional
branch after it. If Review 8 fails with another blocking HIGH, the Phase-2 product **freezes** and a separate fresh
session builds a **V8.3 Context/Retrieval Bridge** before any further product repair. The owner's reasoning is
recorded because it diagnoses this phase's own failure mode: *independence must mean independent reasoning plus
complete relevant context, not independent reasoning plus architectural ignorance.* After the bridge, every finding
must run `finding → whole-system context pack → fresh root-cause synthesis` classifying the answer as
REPAIR/REUSE/DELETE/NARROW/DEFER/OWNER DECISION **before** product code changes — aimed squarely at the loop this
phase has been in.

**Orchestrator correction to a premise.** OD-P2-09 §5B states AR95 has already produced evidence of a genuine
nondeterministic concurrent re-anchor race. That is not confirmable from durable state: AR95 has committed nothing
and has not reported. The race evidence on record is P2-AR-0094's `ar94_c5`, which **constructed** the interleaving
but observed the invocations serialise — explicitly *not ruled out* rather than proven. Flagged to the owner so the
sweep does not inherit an unverified premise.

**First sweep finding, verified at `f2a9ab9`.** `init.rs:303` and `adopt.rs:1840` both gate
`write_project_adoption_floor` on `!already_installed`, and a relocated checkout carries `framework.lock` — so
neither onboarding path re-establishes a floor at a new path (`--force` explicitly reinstalls the kernel without
re-running the adoption decision). **Deleting `floor-reanchor` is therefore not a pure deletion**: it removes the
identity-transfer surface but leaves same-machine relocation with no in-product remedy unless a re-onboarding path is
also provided. Mitigating half, also verified: `PolicySet::load` reconstructs from native layout plus AR86-C6
`last_known_rules`, so a refused floor leaves the checkout DEGRADED/UNHEALTHY rather than unprotected.

## P2-L-0043 — P2-AR-0095 lands all five items (373/0); the sweep answers 5B and 5C from evidence (2026-09-24)

`92982ff` on `phase2/remediation-ar94`, base `f2a9ab9`, full suite **373/0** in 3,617 s (60m17s). Scope confined to
`paths.rs`, `cli/src/main.rs`, two test files and a checkpoint; **`exec_resolve.rs` untouched**, so Property A is
carried forward unmodified for the fourth round.

**All five non-deferrable items landed.** `gov floor-reanchor` now requires `--from <previous path>` and compares the
document's `bound_project_identity` against the entry at that **operator-named** key (`paths.rs:1555`) — AR94-C2
closed by narrowing, with the whole-store identity scan deleted rather than guarded.

**The builder declared one deviation rather than burying it**, which is the reason this round is adjudicable. It did
**not** delete the durable sandbox marker as §1.2 prescribed; it re-keyed the marker to the OS-created object's own
`(device, inode)` and added GC. Its stated reason: `ar94_nc2` — the AR94 reviewer's own positive control — requires
**post-mortem** recognition, and a process-local registry cannot satisfy that by construction.

**Orchestrator verification settled two of the owner's three sweep questions from evidence.**

**5B — the concurrent re-anchor race is CONFIRMED real.** OD-P2-09 §5B asserted this; the orchestrator flagged it as
unverifiable from durable state at the time and that caution is now **withdrawn**. AR95 reproduced two store entries
for one identity in one run and observed serialisation in another — stronger evidence than AR94's `ar94_c5`, which
constructed the interleaving but saw it serialise. `reanchor_project_identity`'s lookup→write→remove holds no lock.
Left unfixed, correctly, as outside the round's five items.

**5C — production never needs post-mortem sandbox recognition.** `skills.rs:528 execute_check` holds its `Sandbox`
alive across every child `gov` call (`run_gov`), so the creating process is alive for **every** production read;
`ar94_nc2` (`ar94_floor.rs:490`) uses `spawn_and_kill_when` to SIGKILL the creator **deliberately**. The requirement
that forced the builder's deviation therefore comes from a **test**, not from any product path — which makes the
owner's proposed simpler semantic (creator dies → exemption no longer authoritative → fail closed) available, and
would allow deleting the inode binding and the GC outright.

**5A — restated crux.** `init.rs:303` and `adopt.rs:1840` gate the floor write on `!already_installed`, so no
onboarding path re-establishes a floor at a relocated path. Deleting `floor-reanchor` outright removes the
identity-transfer surface but leaves relocation with no in-product remedy.

**Sweep presented to the owner in one consolidated message. Review 8 is blocked** until it is answered and any
resulting delta implemented (OD-P2-09 §4, OD-P2-10 §1).

## P2-L-0044 — the owner-approved delta: a round that mostly deletes (2026-09-24)

The owner accepted the Option-C probe, approved fresh-identity re-onboarding, and **corrected an orchestrator
error**: the proposed never-weaker mitigation would have inherited rules from the T2-verified floor document, but
OD-P2-08 §2 makes the T2 seal **detection, never proof-grade**, because its symmetric key is readable inside the
local OS trust domain. The proposal re-admitted the document as an authority source through the back door — the exact
shape this phase exists to remove. Withdrawn; the document is not consulted for rules at all.

**`HISTORICAL_RULE_SOURCE_REUSES_EXISTING_PROOF_GRADE_PRIMITIVE`** (`RESEARCH/P2-HISTORICAL-RULE-SOURCE.md`). The
source is `FloorIdentity::last_known_rules` under the protected machine state root — outside every project and
unreachable by an ordinary actor (AR88). The association problem, which is what would have forced trusting a
project-editable identity claim, is **dissolved by the owner's own conservative-union suggestion**: `policy.rs`'s
existing AR86-C6 union is pattern-additive (`if !fresh_patterns.contains(p)`), so unioning across every store entry
can only **add** patterns the fresh derivation missed, with the fresh derivation always winning on conflict. No
historical identity has to be declared the owner of the new checkout. Every failure direction — missing, wrong,
conflicting — resolves toward *more* obligation, never less. No new authority mechanism.

**Dispatched `P2-AR-0096`** on `P2-HO-0060` from `92982ff`. The delta is mostly deletion: `gov floor-reanchor` goes
entirely, taking AR94-C2/C3/C4/D1/D5 and the confirmed C5 race with it; relocation recovery becomes ordinary governed
re-onboarding minting a **fresh** identity, which falls out of existing code (`FloorIdentity::advance` already mints
a uuid when a checkout has no entry) and fixes AR92-C3 as a side effect; the sandbox exemption becomes creator
liveness, deleting the inode-binding and GC. Net: one command, one race and five findings removed; one condition and
one read added.

**The detail most likely to be got wrong, named in the brief:** the union must be applied in the derivation
`init`/`adopt` hand to `write_project_adoption_floor`, **not only** in `PolicySet::load`'s reconstruction fallback —
because once a floor is written reconstruction never fires, so a weak derived floor would be promoted to
*authenticated*, strictly worse than the case it replaces.

## P2-L-0045 — the approved delta lands (368/368); Review 8 dispatched as the convergence decision point (2026-09-25)

`3c880d8` on `phase2/approved-delta`, base `92982ff`, **full suite 368/368, 0 filtered, 3,631 s (60m31s)**.
Arithmetic: 373 base − 8 deleted + 3 new. `exec_resolve.rs` untouched, so Property A carries forward for a fourth
round.

**The first round in this phase that mostly deletes.** `gov floor-reanchor` is gone whole — command,
`reanchor_project_identity`, error codes, guard row, `g0_label`/`command_name` arms — taking **AR94-C2, C3, C4, D1,
D5 and the confirmed C5 concurrency race** with it. C5 is *moot, not fixed*: the function it was a property of no
longer exists. The `(device,inode)` marker binding and its GC are also deleted, replaced by creator liveness — and
deleting the GC is sound, because a liveness marker decays to inert the instant its creator dies, which is precisely
what the P2-AR-0095 sweep existed to bound.

Relocation is now ordinary governed re-onboarding under unchanged `install_kernel` authority, minting a **fresh**
identity out of unchanged code (`FloorIdentity::advance`). A second working copy gets its own identity **without
disturbing the first** — AR92-C3's and AR94-C4's measured costs both vanish structurally rather than being
documented.

**Orchestrator verification** confirmed: the deletion is real (every surviving grep hit is documentation of it;
`cli/src/main.rs` is 20 deletions, 0 additions); the four new functions exist; `process_start_time` reads
`/proc/<pid>/stat` field 22 correctly past the comm field, with PID reuse defeated by start-time comparison and
non-Linux failing closed.

**The orchestrator raised a finding against the revised positive control and then WITHDREW it, wrongly raised.**
`execute_check`'s sandbox is `git: true`, which runs a fresh `git init`, so its lineage can never match the copied
floor — and `read_project_adoption_floor` returns early on lineage mismatch at `paths.rs:1200`, **before**
`reconcile`. The exemption is therefore never consulted for that sandbox, the builder's in-process probe matches the
only production shape, and the proposed "correction" would have tested a path where the mechanism never decides. This
is the **second** load-bearing claim the orchestrator got wrong this phase by verifying that a path *exists* without
verifying that it *reaches the decision* — the same authority-versus-representation confusion the product keeps
failing on, appearing in the orchestrator's own reasoning. Recorded, not erased.

The verification did surface a real adjacent fact, handed to Review 8 rather than rediscovered: **inside a
`skills::execute_check` scenario sandbox the project floor is always refused on lineage**, so scenario checks run
with no floor applied at all. AR84-C3-shaped, unrelated to the exemption, correctly out of scope for a bounded delta.

**`REVIEW_8_CONTEXT_PACK.md` built and completed** (OD-P2-10 §1) — the trust model stated explicitly, the eight-round
failure pattern, what is settled, and six inherited residuals including the builder's own named creator-liveness
residual.

**Dispatched `P2-AR-0097`** on `P2-HO-0061` at `3c880d8`. Because this round deleted rather than added, the brief
inverts the standing question: **did the deletions remove protection?** — above all, whether a planted floor document
can gain authority through the new re-onboarding path, which is where the deleted command's worst finding lived.

## P2-L-0046 — Review 8 returns RESIDUAL_DEFECTS; the Phase-2 product is FROZEN; two owner rules trigger (2026-09-25)

`P2-AR-0097` reviewed `3c880d8` and committed at `58219d5`. **Three HIGH**, all independently confirmed by the
orchestrator before any routing decision. **Property A HOLDS for a fourth consecutive round** — `exec_resolve.rs`
byte-identical to `a01f0c9`, `t2.rs` byte-identical to `92982ff`. **Property C FAILS.**

**F1 (HIGH, mechanism this round introduced — reopens AR94-C1).** `creator_is_alive` accepts a dead-but-**unreaped**
creator. A zombie keeps `/proc/<pid>/stat` with `starttime` unchanged; `process_start_time` reads field 22 and never
reads field 3, so the state `Z` is invisible to it. Reaping is the *parent's* job and the attacker is the parent of
the `gov` process, so the attacker simply never calls `wait()`. The reviewer's reproduction is `ar94_c1`'s own, with
exactly one line removed — the reap — and the exemption is reconstituted, `reconcile` and therefore
`other_live_claim` are skipped, and a planted donor floor is adopted **with no finding at all**. Every existing test
reaps, so none could see it. **The orchestrator confirmed this end to end**: an unreaped child retains `starttime`
with state `Z`; once reaped the file disappears. (The first attempt at that measurement was invalid — bash job
control auto-reaps — and was redone with an explicit fork that never waits, rather than reported as a refutation.)

**The sandbox exemption has now produced a HIGH in three consecutive rounds under three different mechanisms**: path
shape (AR92-C2) → OS marker plus `(device,inode)` (AR94-C1) → creator liveness (F1). OD-P2-09's binding
simplification principle addresses exactly this, and Review 8 verified independently that the exemption can be
**deleted** rather than given a fourth mechanism, because no production consumer needs a cross-process signal.

**F2 (HIGH, OLD UNTOUCHED CORE — new).** `native_layout_rules` builds `format!("{d}/**")` with **no glob escaping or
validation** (`init.rs:146`, confirmed). So `mkdir '*'` plus deleting the floor — two ordinary project-scoped writes —
mints `*/**`, which matches every path containing a slash, is restored **last** by `evaluate_path_rules_overlay`, and
under last-match-wins displaces `governance/project/**`'s `mutation: restricted` with `mutation: allowed`. That
attribute is **enforced**, not merely reported (`tools.rs:1817`). Disclosed (D027 red), but *applied* rather than
refused — and OD-P2-08 §2 is explicit that detection is not a substitute for authority.

**F3 (HIGH, mechanism this round introduced — new).** `union_last_known_rules_across_store` writes an unvalidated
**foreign** pattern into this project's authenticated floor. `partition_floor_rules_against_kernel` exists precisely
because the floor unions onto the kernel template, and it has exactly **one** call site — the CIT route
(`cit/mod.rs:1623`, confirmed) — so restored rules bypass it entirely.

**This is the orchestrator's own design error, and the third instance of one shape.** The approved design rested on
the orchestrator's claim that the union is *additive only, so it can only add patterns and never displace a class*.
The flaw: conflict is decided by **exact pattern-string equality**, so a *broader* foreign pattern is never detected
as conflicting, "fresh wins on conflict" never fires for it, and last-match-wins does the rest. Ties break by sorted
`sha256(path)` — not by strength. The orchestrator verified that the union was additive without verifying that
additivity **reached the decision** — the same error as proposing the T2-verified document as a rules authority, and
as the withdrawn positive-control finding. The first two were caught before they shipped; this one shipped into an
owner-approved design.

**What the deletion did NOT break, verified:** `ar97_c2` passes — a planted floor document **cannot** steer the
re-onboarding it triggers, which was the key question after `gov floor-reanchor` was removed, and where AR94-C2 had
lived. `ar97_c1` passes — AR88-C10B is not reopened. Required regression subset 64/0; R1's hard constraints green;
all five OC-P2-04 cases reachable and reportable.

**Two owner rules trigger together, and both point the same way.** OD-P2-10 §3: Review 8 failed with blocking HIGHs,
so the Phase-2 product **freezes** and no narrow repair cycle may start; a separate fresh session builds the V8.3
Context/Retrieval Bridge first. OD-P2-09 §5: F2 is a material HIGH in an old, untouched core subsystem, which is an
explicit **STOP and return to the owner**. Review 8 argued F2 is *not* scope expansion and invited the owner to
overrule it — a judgement that belongs to the owner, not to the orchestrator or the reviewer.

**Action: product frozen at `3c880d8`. No repair dispatched. Returned to the owner.**
