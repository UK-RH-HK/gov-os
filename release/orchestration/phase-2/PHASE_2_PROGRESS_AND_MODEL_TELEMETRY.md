# Phase 2 — progress status and model/context telemetry snapshot

| Field | Value |
|---|---|
| Snapshot | 2026-09-19, taken while repair round 3 was running (observational only — no routing or execution changed) |
| Sources | committed durable state (`ORCHESTRATOR_STATE.yaml`, `AGENT_RUNS/`, `GATES/`, ledger, repair/integration reports) and the harness's completion notice for each finished agent (`subagent_tokens`, `tool_uses`, `duration_ms`) |
| Machine-readable twin | `PHASE_2_PROGRESS_AND_MODEL_TELEMETRY.yaml` (same directory) |
| Rule | Nothing is estimated where the harness does not expose it: such fields read **NOT_OBSERVABLE**. Inferences are labelled as inferences. |

---

# A. Phase-2 progress and status

## A1. Where Phase 2 is

- **Round:** repair iteration 1, **round 3 of 4**. Round 4 is the single BC-P2-02 evidence-map round.
- **Round-3 objective:** close the remaining dependency-wave classes (BC-P2-07 tier duties, BC-P2-13 in-task hook, BC-P2-23 W11 metrics, BC-P2-24 work generation, BC-P2-31 store moves, BC-P2-44 SLOs and the HEALTHY conjunction), every round-3 integration point, **P2-ADJ-0002** (T2 cross-machine continuity), and the **L4/O5 availability rule** (a health block refuses only what it protects, never its own remedy).
- **Lifecycle:** `P2_REPAIR_ITERATION_1`, loop `P2_REPAIR_1_ROUND_3_RUNNING`.

## A2. Agents

| Count | Value |
|---|---|
| Launched | **40** (P2-AR-0001 … P2-AR-0040) |
| Completed | **37** |
| Running | **3** — P2-AR-0033 (WS-2), P2-AR-0035 (WS-4), P2-AR-0036 (WS-5), all round-3 repair builders |
| Failed / INCOMPLETE | **0** |
| Completed but not relied on | **6** — the first-pass family audits P2-AR-0001…0006: five ruled `COMPLETED_NONCONFORMING`, one `COMPLETED_MODEL_DEVIATION`; all superseded by pinned-model re-audits |

| Kind | Runs |
|---|---|
| First-pass audit (superseded) | P2-AR-0001, 0002, 0003, 0004, 0005, 0006 |
| Re-audit (audits of record) | P2-AR-0008 ε, 0009 β, 0010 γ, 0011 δ, 0012 ζ, 0013 α |
| Synthesis / verdict | P2-AR-0007 → `GOVERNANCE_CAPABILITY_BASELINE_REJECTED` on `cap2-candidate-0` |
| Repair round 1 | P2-AR-0014…0021 (8) → integrated by P2-AR-0022 → merged `b7e6d52` |
| Repair round 2 | P2-AR-0023…0031 (9) → integrated by P2-AR-0032 → merged `e8e1ff2` |
| Repair round 3 | P2-AR-0033…0040 (8): 5 done (0034 WS-3, 0037 WS-6, 0038 WS-7, 0039 WS-8, 0040 WS-9/11), 3 running |
| Independent re-verification | **none yet** — iteration-1 verification follows `cap2-candidate-1` |

## A3. Workstreams (round 3)

| Workstream | Run | Status | Scope |
|---|---|---|---|
| WS-2 health/verification | P2-AR-0033 | RUNNING | BC-07, BC-23, BC-44; availability API in the catalogue; IF-1 |
| WS-3 authority/gates/T2/docs/spec | P2-AR-0034 | DONE, awaiting integration | P2-ADJ-0002 (WS-3 side), T2 completeness, control-state move, D-0010, docs, adapters |
| WS-4 change control/context | P2-AR-0035 | RUNNING | seal-writer completeness (O-7), product-release record type |
| WS-5 tasks/DAG/work generation | P2-AR-0036 | RUNNING | BC-24, BC-13 hook, WS-4 API wiring, claims-store move |
| WS-6 knowledge fabric | P2-AR-0037 | DONE, awaiting integration | freshness fix, heading chunks, template order, store classification |
| WS-7 plugin/tool trust | P2-AR-0038 | DONE, awaiting integration | registry move, artefact binding, pin cache |
| WS-8 root of trust | P2-AR-0039 | DONE, awaiting integration | P2-ADJ-0002 provisioning, 4.1.6 payload/version, update remedy |
| WS-9/11 adoption/export | P2-AR-0040 | DONE, awaiting integration | snapshots move, template migration op, command-test bound |
## A4. Open blockers

The iteration-0 inventory: **134 blocking findings in 52 blocker classes**. By each class's maximum severity: **39 HIGH, 13 MEDIUM**.
**All 52 remain OPEN** until an independent verifier grades them; builder claims are regression evidence only (Contract v3 O3).

Builder-claim coverage: **48 of 52 classes** have at least one builder claim. No claim yet:
- **BC-P2-02**: round 4.
- **BC-P2-23** and **BC-P2-44**: WS-2 round 3, running.
- **BC-P2-24**: WS-5 round 3, running.

| Class | Max severity | Findings | Builder claims (round/workstream:status) |
|---|---|---|---|
| BC-P2-01 Compiled contract views lose owner-source semantics and verification is self-referential | HIGH | 9 | r1/ws01-12:REPAIRED_CLAIMED |
| BC-P2-02 Evidence map declares no evidence owner for any capability | HIGH | 7 | — none yet |
| BC-P2-03 Green governance evidence currency: key omits relevant input classes and enforcement is path-keyed | HIGH | 6 | r1/ws02:REPAIRED_CLAIMED |
| BC-P2-04 Upstream change does not invalidate completed work, its evidence or compiled packets | HIGH | 6 | r2/ws04:REPAIRED_CLAIMED |
| BC-P2-05 Checkpoint and handoff continuity: triggers, staleness and handoff blocking | HIGH | 3 | r2/ws04:REPAIRED_CLAIMED; r3/ws06:REPAIRED_CLAIMED |
| BC-P2-06 Health scheduler mechanics absent | HIGH | 6 | r1/ws02:REPAIRED_CLAIMED |
| BC-P2-07 Health tiers G1-G6 do not perform their duties at their trigger events (incl. Gate-W duties) | HIGH | 6 | r2/ws09-11:REPAIRED_CLAIMED |
| BC-P2-08 Acting-role resolution and G0 guard coverage on privileged/mutating paths | HIGH | 6 | r1/ws03:REPAIRED_CLAIMED; r2/ws03:REPAIRED_CLAIMED; r2/ws03:REPAIRED_CLAIMED; r2/ws09-11:REPAIRED_CLAIMED |
| BC-P2-09 OS-written (T2) records honoured without binding to an OS operation; lower-role writes exempt at task close | HIGH | 3 | r1/ws03:REPAIRED_CLAIMED; r2/ws07:REPAIRED_CLAIMED |
| BC-P2-10 Human approval and presentation derived from caller-declared metadata | HIGH | 4 | r1/ws03:REPAIRED_CLAIMED; r2/ws09-11:REPAIRED_CLAIMED |
| BC-P2-11 Gate approval not bound to the subject and content it authorises | HIGH | 2 | r2/ws04:REPAIRED_CLAIMED; r2/ws07:REPAIRED_CLAIMED |
| BC-P2-12 Task-blocking gate semantics | HIGH | 1 | r1/ws03:REPAIRED_CLAIMED; r2/ws05:REPAIRED_CLAIMED |
| BC-P2-13 Material changes escape change control (materiality self-declared, in-task edits bypass CIT) | HIGH | 2 | r2/ws04:REPAIRED_CLAIMED |
| BC-P2-14 Task-contract fields and path scope not enforced | HIGH | 2 | r1/ws05:REPAIRED_CLAIMED |
| BC-P2-15 Claim atomicity and claim scope | HIGH | 2 | r1/ws05:REPAIRED_CLAIMED |
| BC-P2-16 Runnable / claimable / READY state not derived from the DAG | HIGH | 3 | r2/ws05:REPAIRED_CLAIMED |
| BC-P2-17 Mandatory task-input manifest semantics | HIGH | 3 | r1/ws04:REPAIRED_CLAIMED |
| BC-P2-18 Contradiction detection and resolution | MEDIUM | 3 | r1/ws03:REPAIRED_CLAIMED; r2/ws04:REPAIRED_CLAIMED |
| BC-P2-19 Context-packet delivery, provenance and outage behaviour | HIGH | 4 | r1/ws04:REPAIRED_CLAIMED |
| BC-P2-20 Consumption receipt and implementation traceability | HIGH | 4 | r1/ws04:REPAIRED_CLAIMED; r2/ws05:REPAIRED_CLAIMED |
| BC-P2-21 Artefact identity and relation-edge semantics | MEDIUM | 3 | r1/ws04:REPAIRED_CLAIMED; r1/ws09-11:PARTIAL |
| BC-P2-22 Orphan / unexplained output detection | HIGH | 1 | r2/ws02:REPAIRED_CLAIMED |
| BC-P2-23 Artifact-flow quantitative health absent | HIGH | 1 | — none yet |
| BC-P2-24 Governed work not generated from events | HIGH | 2 | — none yet |
| BC-P2-25 Index content coverage and chunk granularity | HIGH | 3 | r1/ws06:REPAIRED_CLAIMED; r3/ws06:REPAIRED_CLAIMED |
| BC-P2-26 Retrieval pipeline ordering, routing and de-duplication | HIGH | 4 | r1/ws06:REPAIRED_CLAIMED |
| BC-P2-27 Code-structural extraction | HIGH | 2 | r1/ws06:REPAIRED_CLAIMED; r3/ws06:REPAIRED_CLAIMED |
| BC-P2-28 Graph integrity detection | MEDIUM | 1 | r2/ws06:REPAIRED_CLAIMED |
| BC-P2-29 Incremental index invalidation | HIGH | 3 | r1/ws06:REPAIRED_CLAIMED; r3/ws06:REPAIRED_CLAIMED |
| BC-P2-30 Retrieval-profile component identity and change governance | HIGH | 3 | r2/ws06:REPAIRED_CLAIMED |
| BC-P2-31 Non-rebuildable authoritative state stored in, or classified as, derived/generated state | MEDIUM | 2 | r2/ws06:PARTIAL; r3/ws03:REPAIRED_CLAIMED; r3/ws03:PARTIAL; r3/ws06:REPAIRED_CLAIMED; r3/ws07:REPAIRED_CLAIMED; r3/ws08:REPAIRED_CLAIMED; r3/ws09-11:REPAIRED_CLAIMED; r3/ws09-11:REPAIRED_CLAIMED |
| BC-P2-32 Failure memory not durable | MEDIUM | 1 | r1/ws06:REPAIRED_CLAIMED |
| BC-P2-33 Legacy identification, extraction and retirement | HIGH | 4 | r1/ws09-11:REPAIRED_CLAIMED |
| BC-P2-34 Independence of test, review and verification authorship is self-attested | HIGH | 4 | r2/ws05:REPAIRED_CLAIMED; r2/ws09-11:REPAIRED_CLAIMED |
| BC-P2-35 Post-install kernel integrity anchored only in repository-controlled records | HIGH | 1 | r1/ws08:REPAIRED_CLAIMED; r2/ws08:REPAIRED_CLAIMED |
| BC-P2-36 Unauthenticated installation presented as current/verified (default posture) | HIGH | 1 | r1/ws08:REPAIRED_CLAIMED; r2/ws08:REPAIRED_CLAIMED; r3/ws09-11:REPAIRED_CLAIMED |
| BC-P2-37 Trust decisions and identity records taken from unauthenticated release fields | HIGH | 2 | r1/ws08:REPAIRED_CLAIMED |
| BC-P2-38 Provisioned-machine rollback/reinstall | MEDIUM | 1 | r1/ws08:REPAIRED_CLAIMED |
| BC-P2-39 Plugin elevation decided by descriptor self-declaration | MEDIUM | 1 | r2/ws07:REPAIRED_CLAIMED |
| BC-P2-40 Plugin implementation bytes not bound | HIGH | 2 | r2/ws07:REPAIRED_CLAIMED |
| BC-P2-41 Tool acquisition: review evidence and approval not bound to the tool installation | HIGH | 2 | r2/ws07:REPAIRED_CLAIMED |
| BC-P2-42 Skill regression never executed | MEDIUM | 2 | r1/ws02:REPAIRED_CLAIMED |
| BC-P2-43 Product-test results not governed | HIGH | 1 | r1/ws02:REPAIRED_CLAIMED |
| BC-P2-44 Health SLO thresholds and the HEALTHY conjunction | HIGH | 2 | — none yet |
| BC-P2-45 Project overlay files bypass POLICY_PRECEDENCE | MEDIUM | 2 | r1/ws03:REPAIRED_CLAIMED; r2/ws03:REPAIRED_CLAIMED |
| BC-P2-46 Scenario -> data -> test-data lineage and provenance | MEDIUM | 2 | r2/ws10:REPAIRED_CLAIMED |
| BC-P2-47 Research output completeness | MEDIUM | 1 | r2/ws10:REPAIRED_CLAIMED; r3/ws06:REPAIRED_CLAIMED; r3/ws06:REPAIRED_CLAIMED; r3/ws06:REPAIRED_CLAIMED |
| BC-P2-48 Experiment lifecycle absent | HIGH | 1 | r2/ws10:REPAIRED_CLAIMED |
| BC-P2-49 Human Decision Gate package not enforced | MEDIUM | 1 | r1/ws03:REPAIRED_CLAIMED |
| BC-P2-50 Upstream export gate fails open on content | HIGH | 1 | r1/ws09-11:REPAIRED_CLAIMED |
| BC-P2-51 Qualification Oracle format absent | HIGH | 1 | r1/ws01-12:REPAIRED_CLAIMED |
| BC-P2-52 Path map does not represent documentation citations | MEDIUM | 1 | r1/ws09-11:REPAIRED_CLAIMED |

## A5. Closing existing findings, or introducing new classes?

- **Convergence counter:** 0 verifier iterations since the baseline, so `consecutive_new_class_iterations = 0`. The threshold is **3**, and it is **not approaching**. No independent verification has run since the baseline; the counter moves only on verifier verdicts.
- **Rounds 1–3 are closing inventoried classes by claim.** Repair also surfaced or introduced issues that a verifier has not yet labelled:
  1. **T2 cross-machine continuity (S6).** It regressed because of the round-1 BC-P2-09 design. Adjudicated as P2-ADJ-0002 and in repair in round 3.
  2. **Health-block availability deadlocks.** The BC-P2-06 scheduler and the host guards could refuse remedies and all claims. The L4/O5 rule addresses this in round 3.
  3. **Kernel-cache materialisation race.** It was latent and exposed by concurrency; fixed in round 2.
  4. **R1 held-out AR-0031 `hx_a::a4` regression.** It was introduced twice (WS-2 round 1, WS-3 round 3), and both times caught and fixed before merge.
  5. **Backward compatibility for shipped 4.1.4/4.1.5 kernels (O-1).** Introduced in round 1 and fixed in round 2.
  6. **IF-1.** W7 treats consumption as implementation; in WS-2 round 3.
- **Most likely to be argued materially new** at iteration 1, if not fully closed: items 1, 2 and 5.

## A6. Candidate, gates and tests

- **Candidate:**
  - `cap2-candidate-0` (`57177a3`) was **rejected** by P2-AR-0007.
  - `cap2-candidate-1` is **not yet minted**.
  - The latest integrated tree `e8e1ff2` has `product_code_digest` `797da37c…1fe1`; it is not a candidate.
- **Gates:**

  | Gate | Status |
  |---|---|
  | GATE-P2-ENTRY | SATISFIED |
  | GATE-P2-FROZEN-CONTRACT | SATISFIED |
  | GATE-P2-BASELINE-AUDIT-0 | SATISFIED (verdict REJECTED) |
  | GATE-P2-ORACLE-FORMAT | NOT_SATISFIED (format built; independent review pending) |
  | GATE-P2-R1-PRESERVATION | re-opens for candidate 1 |
  | GATE-P2-CAPABILITY-BASELINE-ACCEPT | NOT_SATISFIED |
  | HG-P2-0001 | ANSWERED (OD-P2-01 A, OD-P2-02 A) |
  | GATE-P2-REPAIR-1 | OPEN |

- **Tests at merged HEAD `e8e1ff2`** (orchestrator-reproduced):
  - `cargo test --lib`: **207/0**.
  - `cargo test --test certification`: **136/0**.
- **R1 held-out suites:** at their recorded baselines.
  - AR-0027: 26/3.
  - AR-0029: 26/2, with `ho_f` not compiling.
  - AR-0031: 27/7.
  - AR-0033: 30/1. The one failure is `hv_a::a1`, which pins candidate 4's census size. The census with that pin removed shows 0 §6 violations.
- **Round-3 branches:** each builder reports its own tree green; not yet integrated.

## A7. Duplicated work

1. **First-pass audits.** Six ran, then six re-audits: a deliberate protocol-conformance re-run after the first pass came back self-reported `claude-opus-4-6` with status/finding contradictions.
2. **P2-ADJ-0002 was implemented twice in round 3.** WS-3 and WS-8 each built a full provisioning mechanism: `gov trust t2-binding --provision` versus `gov trust bind`. This is an **orchestrator routing ambiguity**: each handoff named a side, and each builder completed the whole mechanism. The round-3 integration handoff (P2-HO-0040) requires unifying them into one.
3. **No other duplication observed.**

## A8. Next deterministic action and remaining work

- **Next:** `AWAIT_REPAIR_1_ROUND_3`. Then integration-3 (P2-HO-0040), then round 4 (BC-P2-02), then mint `cap2-candidate-1`, then verification iteration 1.
- **Remaining work, counted in agents rather than time:**
  - **Round 3:** 3 builders running, then 1 integrator.
  - **Round 4:** 1 builder, then a merge.
  - **Verification iteration 1, about 9 agents:** AC-14 R1-preservation, AC-6 oracle-format review, 6 family verifiers, and 1 synthesis verifier. It must be a full re-audit: product code changed broadly, so under Contract v3 freshness all evidence is stale.
  - **If rejected:** repair iteration 2 (size unknown) and verification iteration 2.

---

# B. Model, context and usage telemetry

## B1. What is and is not observable

| Metric | Availability |
|---|---|
| Provider | Anthropic, via Claude Code's Agent tool |
| Exact model | Each agent's self-report in its run report, plus the dispatch parameter: `default` means the model parameter was omitted; `opus` means pinned |
| `subagent_tokens`, tool calls, wall-clock | The harness completion notice. **What `subagent_tokens` counts (cumulative, final context, or output) is not documented.** |
| Input tokens, output tokens, input/output split | **NOT_OBSERVABLE** |
| Reasoning/thinking level of subagents | **NOT_OBSERVABLE** |
| Peak context utilisation | **NOT_OBSERVABLE** |
| Compaction events | **NOT_OBSERVABLE** |
| Cost | **NOT_OBSERVABLE** |
| Retries/restarts | Observable at orchestration level only: 6 superseded runs; no agent was restarted mid-run |

## B2. Per agent

| Run | Phase | Role | WS/family | Dispatch | Model (self-reported) | subagent_tokens | Tool calls | Hours | Outcome | Yield |
|---|---|---|---|---|---|---|---|---|---|---|
| P2-AR-0001 | audit-0 first pass | family-auditor | alpha | default | claude-opus-4-6 | 63,277 | 116 | 0.50 | COMPLETED_NONCONFORMING | 4 findings / 0 blocking |
| P2-AR-0002 | audit-0 first pass | family-auditor | beta | default | claude-opus-4-6 | 69,863 | 79 | 0.47 | COMPLETED_NONCONFORMING | 4 findings / 0 blocking |
| P2-AR-0003 | audit-0 first pass | family-auditor | gamma | default | claude-opus-4-6 | 64,479 | 100 | 0.46 | COMPLETED_MODEL_DEVIATION | 3 findings / 0 blocking |
| P2-AR-0004 | audit-0 first pass | family-auditor | delta | default | claude-opus-4-6 | 69,460 | 81 | 0.45 | COMPLETED_NONCONFORMING | 4 findings / 0 blocking |
| P2-AR-0005 | audit-0 first pass | family-auditor | epsilon | default | claude-opus-4-6 | 69,715 | 74 | 0.43 | COMPLETED_NONCONFORMING | 7 findings / 1 blocking |
| P2-AR-0006 | audit-0 first pass | family-auditor | zeta | default | claude-opus-4-6 | 81,169 | 89 | 0.44 | COMPLETED_NONCONFORMING | 5 findings / 0 blocking |
| P2-AR-0008 | audit-0 re-audit | family-auditor | epsilon | opus | claude-opus-5[1m] | 678,030 | 185 | 0.82 | COMPLETED | 36 findings / 27 blocking |
| P2-AR-0009 | audit-0 re-audit | family-auditor | beta | opus | claude-opus-5[1m] | 955,317 | 261 | 1.20 | COMPLETED | 30 findings / 22 blocking |
| P2-AR-0010 | audit-0 re-audit | family-auditor | gamma | opus | claude-opus-5[1m] | 929,426 | 219 | 1.13 | COMPLETED | 36 findings / 19 blocking |
| P2-AR-0011 | audit-0 re-audit | family-auditor | delta | opus | claude-opus-5[1m] | 727,452 | 179 | 0.92 | COMPLETED | 26 findings / 17 blocking |
| P2-AR-0012 | audit-0 re-audit | family-auditor | zeta | opus | claude-opus-5[1m] | 772,313 | 180 | 1.00 | COMPLETED | 27 findings / 24 blocking |
| P2-AR-0013 | audit-0 re-audit | family-auditor | alpha | opus | claude-opus-5[1m] | 368,601 | 285 | 1.33 | COMPLETED | 25 findings / 7 blocking |
| P2-AR-0007 | audit-0 synthesis | baseline-synthesis | all | opus | claude-opus-5[1m] | 894,062 | 156 | 1.27 | COMPLETED (REJECTED verdict) | 10 findings / 8 blocking |
| P2-AR-0014 | repair r1 | repair-builder | WS-1/12 | opus | claude-opus-5[1m] | 644,373 | 146 | 1.18 | COMPLETED_INTEGRATED | 2 claimed, 0 partial, 0 not |
| P2-AR-0015 | repair r1 | repair-builder | WS-2 | opus | claude-opus-5[1m] | 892,479 | 286 | 2.27 | COMPLETED_INTEGRATED | 4 claimed, 0 partial, 0 not |
| P2-AR-0016 | repair r1 | repair-builder | WS-3 | opus | claude-opus-5[1m] | 244,051 | 343 | 2.21 | COMPLETED_INTEGRATED | 7 claimed, 0 partial, 0 not |
| P2-AR-0017 | repair r1 | repair-builder | WS-4 | opus | claude-opus-5[1m] | 726,000 | 208 | 1.52 | COMPLETED_INTEGRATED | 4 claimed, 0 partial, 0 not |
| P2-AR-0018 | repair r1 | repair-builder | WS-5 | opus | claude-opus-5[1m] | 679,943 | 230 | 1.78 | COMPLETED_INTEGRATED | 2 claimed, 0 partial, 0 not |
| P2-AR-0019 | repair r1 | repair-builder | WS-6 | opus | claude-opus-5[1m] | 785,452 | 212 | 1.62 | COMPLETED_INTEGRATED | 5 claimed, 0 partial, 0 not |
| P2-AR-0020 | repair r1 | repair-builder | WS-8 | opus | claude-opus-5[1m] | 928,942 | 247 | 1.99 | COMPLETED_INTEGRATED | 4 claimed, 0 partial, 0 not |
| P2-AR-0021 | repair r1 | repair-builder | WS-9/11 | opus | claude-opus-5[1m] | 850,682 | 249 | 2.03 | COMPLETED_INTEGRATED | 3 claimed, 1 partial, 0 not |
| P2-AR-0022 | repair r1 integration | integration-builder | all | opus | claude-opus-5[1m] | 865,332 | 318 | 1.72 | COMPLETED_MERGED | — |
| P2-AR-0023 | repair r2 | repair-builder | WS-2 | opus | claude-opus-5[1m] | 936,671 | 319 | 3.09 | COMPLETED_INTEGRATED | 1 claimed, 0 partial, 0 not |
| P2-AR-0024 | repair r2 | repair-builder | WS-3 | opus | claude-opus-5[1m] | 786,274 | 266 | 1.85 | COMPLETED_INTEGRATED | 10 claimed, 1 partial, 1 not |
| P2-AR-0025 | repair r2 | repair-builder | WS-4 | opus | claude-opus-5[1m] | 449,313 | 437 | 3.89 | COMPLETED_INTEGRATED | 5 claimed, 0 partial, 0 not |
| P2-AR-0026 | repair r2 | repair-builder | WS-5 | opus | claude-opus-5[1m] | 203,868 | 365 | 3.16 | COMPLETED_INTEGRATED | 4 claimed, 0 partial, 0 not |
| P2-AR-0027 | repair r2 | repair-builder | WS-6 | opus | claude-opus-5[1m] | 804,652 | 265 | 2.32 | COMPLETED_INTEGRATED | 2 claimed, 1 partial, 0 not |
| P2-AR-0028 | repair r2 | repair-builder | WS-7 | opus | claude-opus-5[1m] | 783,088 | 222 | 2.27 | COMPLETED_INTEGRATED | 5 claimed, 0 partial, 0 not |
| P2-AR-0029 | repair r2 | repair-builder | WS-8 | opus | claude-opus-5[1m] | 918,895 | 306 | 2.26 | COMPLETED_INTEGRATED | 2 claimed, 2 partial, 0 not |
| P2-AR-0030 | repair r2 | repair-builder | WS-9/11 | opus | claude-opus-5[1m] | 787,654 | 226 | 1.60 | COMPLETED_INTEGRATED | 5 claimed, 0 partial, 0 not |
| P2-AR-0031 | repair r2 | repair-builder | WS-10 | opus | claude-opus-5[1m] | 877,925 | 231 | 2.06 | COMPLETED_INTEGRATED | 3 claimed, 0 partial, 0 not |
| P2-AR-0032 | repair r2 integration | integration-builder | all | opus | claude-opus-5[1m] | 835,855 | 284 | 1.35 | COMPLETED_MERGED | — |
| P2-AR-0034 | repair r3 | repair-builder | WS-3 | opus | claude-opus-5[1m] | 140,375 | 309 | 3.26 | COMPLETED_AWAITING_INTEGRATION | 13 claimed, 3 partial, 1 not |
| P2-AR-0037 | repair r3 | repair-builder | WS-6 | opus | claude-opus-5[1m] | 808,403 | 278 | 2.63 | COMPLETED_AWAITING_INTEGRATION | 8 claimed, 0 partial, 0 not |
| P2-AR-0038 | repair r3 | repair-builder | WS-7 | opus | claude-opus-5[1m] | 810,731 | 286 | 2.32 | COMPLETED_AWAITING_INTEGRATION | 5 claimed, 0 partial, 0 not |
| P2-AR-0039 | repair r3 | repair-builder | WS-8 | opus | claude-opus-5[1m] | 825,364 | 262 | 2.93 | COMPLETED_AWAITING_INTEGRATION | 6 claimed, 3 partial, 0 not |
| P2-AR-0040 | repair r3 | repair-builder | WS-9/11 | opus | claude-opus-5[1m] | 610,209 | 203 | 2.27 | COMPLETED_AWAITING_INTEGRATION | 5 claimed, 0 partial, 0 not |
| P2-AR-0033 | repair r3 | repair-builder | WS-2 | opus | PENDING | PENDING | PENDING | PENDING | RUNNING | — |
| P2-AR-0035 | repair r3 | repair-builder | WS-4 | opus | PENDING | PENDING | PENDING | PENDING | RUNNING | — |
| P2-AR-0036 | repair r3 | repair-builder | WS-5 | opus | PENDING | PENDING | PENDING | PENDING | RUNNING | — |

**For every row:** reasoning level, input tokens, output tokens, peak context utilisation and compaction events are **NOT_OBSERVABLE**.

**Inference, not measurement:** five runs report `subagent_tokens` anomalously low relative to their tool calls.
- The clearest is P2-AR-0034: 140,375 tokens for 309 calls.
- The others are P2-AR-0016, P2-AR-0026, P2-AR-0025 and P2-AR-0013.
- If the metric reflects final context size, this is consistent with in-run compaction. It does not prove it.

## B3. Aggregates

### By model (self-reported)

| Group | Agents | subagent_tokens total | mean | median | tool calls total | mean | wall-clock h total | mean | median |
|---|---|---|---|---|---|---|---|---|---|
| claude-opus-4-6 | 6 | 417,963 | 69,660 | 69,588 | 539 | 89.8 | 2.75 | 0.46 | 0.46 |
| claude-opus-5[1m] | 31 | 22,521,732 | 726,507 | 787,654 | 7,963 | 256.9 | 61.24 | 1.98 | 1.99 |

### By role

| Group | Agents | subagent_tokens total | mean | median | tool calls total | mean | wall-clock h total | mean | median |
|---|---|---|---|---|---|---|---|---|---|
| baseline-synthesis | 1 | 894,062 | 894,062 | 894,062 | 156 | 156 | 1.27 | 1.27 | 1.27 |
| family-auditor | 12 | 4,849,102 | 404,092 | 224,885 | 1,848 | 154 | 9.16 | 0.76 | 0.66 |
| integration-builder | 2 | 1,701,187 | 850,594 | 850,594 | 602 | 301 | 3.07 | 1.54 | 1.54 |
| repair-builder | 22 | 15,495,344 | 704,334 | 786,964 | 5,896 | 268 | 50.49 | 2.3 | 2.26 |

### By phase

| Group | Agents | subagent_tokens total | mean | median | tool calls total | mean | wall-clock h total | mean | median |
|---|---|---|---|---|---|---|---|---|---|
| audit-0 first pass | 6 | 417,963 | 69,660 | 69,588 | 539 | 89.8 | 2.75 | 0.46 | 0.46 |
| audit-0 re-audit | 6 | 4,431,139 | 738,523 | 749,882 | 1,309 | 218.2 | 6.4 | 1.07 | 1.07 |
| audit-0 synthesis | 1 | 894,062 | 894,062 | 894,062 | 156 | 156 | 1.27 | 1.27 | 1.27 |
| repair r1 | 8 | 5,751,922 | 718,990 | 755,726 | 1,921 | 240.1 | 14.59 | 1.82 | 1.89 |
| repair r1 integration | 1 | 865,332 | 865,332 | 865,332 | 318 | 318 | 1.72 | 1.72 | 1.72 |
| repair r2 | 9 | 6,548,340 | 727,593 | 787,654 | 2,637 | 293 | 22.5 | 2.5 | 2.27 |
| repair r2 integration | 1 | 835,855 | 835,855 | 835,855 | 284 | 284 | 1.35 | 1.35 | 1.35 |
| repair r3 | 5 | 3,195,082 | 639,016 | 808,403 | 1,338 | 267.6 | 13.41 | 2.68 | 2.63 |

### By workstream / family

| Group | Agents | subagent_tokens total | mean | median | tool calls total | mean | wall-clock h total | mean | median |
|---|---|---|---|---|---|---|---|---|---|
| WS-1/12 | 1 | 644,373 | 644,373 | 644,373 | 146 | 146 | 1.18 | 1.18 | 1.18 |
| WS-10 | 1 | 877,925 | 877,925 | 877,925 | 231 | 231 | 2.06 | 2.06 | 2.06 |
| WS-2 | 2 | 1,829,150 | 914,575 | 914,575 | 605 | 302.5 | 5.36 | 2.68 | 2.68 |
| WS-3 | 3 | 1,170,700 | 390,233 | 244,051 | 918 | 306 | 7.31 | 2.44 | 2.21 |
| WS-4 | 2 | 1,175,313 | 587,656 | 587,656 | 645 | 322.5 | 5.41 | 2.71 | 2.71 |
| WS-5 | 2 | 883,811 | 441,906 | 441,906 | 595 | 297.5 | 4.94 | 2.47 | 2.47 |
| WS-6 | 3 | 2,398,507 | 799,502 | 804,652 | 755 | 251.7 | 6.56 | 2.19 | 2.32 |
| WS-7 | 2 | 1,593,819 | 796,910 | 796,910 | 508 | 254 | 4.59 | 2.3 | 2.3 |
| WS-8 | 3 | 2,673,201 | 891,067 | 918,895 | 815 | 271.7 | 7.18 | 2.39 | 2.26 |
| WS-9/11 | 3 | 2,248,545 | 749,515 | 787,654 | 678 | 226 | 5.89 | 1.96 | 2.03 |
| all | 3 | 2,595,249 | 865,083 | 865,332 | 758 | 252.7 | 4.34 | 1.45 | 1.35 |
| alpha | 2 | 431,878 | 215,939 | 215,939 | 401 | 200.5 | 1.83 | 0.91 | 0.91 |
| beta | 2 | 1,025,180 | 512,590 | 512,590 | 340 | 170 | 1.67 | 0.84 | 0.84 |
| delta | 2 | 796,912 | 398,456 | 398,456 | 260 | 130 | 1.37 | 0.68 | 0.68 |
| epsilon | 2 | 747,745 | 373,872 | 373,872 | 259 | 129.5 | 1.25 | 0.63 | 0.63 |
| gamma | 2 | 993,905 | 496,952 | 496,952 | 319 | 159.5 | 1.59 | 0.8 | 0.8 |
| zeta | 2 | 853,482 | 426,741 | 426,741 | 269 | 134.5 | 1.44 | 0.72 | 0.72 |

**All 37 completed agents:**
- **`subagent_tokens`:** 22,939,695 total; mean 619,992; median 783,088.
- **Tool calls:** 8,502 in total.
- **Wall-clock:** 63.99 agent-hours. Many agents ran in parallel, so this is not elapsed time.

**Input tokens, output tokens and context utilisation:** NOT_OBSERVABLE for every group.

## B4. Completion, finding yield and repair success

| Measure | Value |
|---|---|
| Completion rate | 37 of 37 finished runs produced a durable typed report (100%); 31 of 37 are relied on (84%) |
| First-pass audit yield (default tier, self-reported `claude-opus-4-6`) | 27 findings, **1 blocking**, across 6 families |
| Re-audit yield (pinned, `claude-opus-5[1m]`) | 180 findings, **116 blocking**, across the same 6 families |
| Synthesis | reviewed 180 family findings: 165 confirmed, 15 corrected, 0 refuted; added 10 (8 blocking); **134 blocking in 52 classes** |
| Builder claims (rounds 1–3 so far) | 105 items REPAIRED_CLAIMED, 11 PARTIAL, 2 NOT_REPAIRED |
| Independent repair success rate | **NOT_OBSERVABLE** until iteration-1 verification |

## B5. Does the task need frontier reasoning?

- **Family audits and synthesis: frontier required (observed).** On the same scope, the default-tier first pass found 1 blocking finding and the pinned frontier re-audit found 116. The synthesis reproduced the frontier findings (1,680 probe outcomes identical).
- **Integration builders: frontier justified by yield.** Both found real defects the builders missed: an R1 held-out regression, and cross-workstream seal/schema conflicts. The purely textual part of a merge could plausibly use a lower tier.
- **Repair builders: frontier plausibly required.** The work is trust-boundary and security design, and builders self-caught security flaws (for example, WS-7's operator-writable pin cache). Documentation, schema-version bookkeeping and evidence-map population are lower-tier candidates, but that is **not demonstrated: INCONCLUSIVE**.

## B6. Repeated context loading

Every fresh agent re-reads the common protocol, the frozen gate contract, the repair delta, the owner records and large parts of the codebase. This is by design: independence, and no shared memory between roles. Evidence: every handoff instructs these reads. Magnitude: **NOT_OBSERVABLE**.

## B7. Estimated avoidable frontier usage

- **Quantified:** NOT_OBSERVABLE (no cost or token split).
- **Qualitative:**
  1. **First-pass audits.** They cost 417,963 `subagent_tokens` and 2.75 agent-hours and produced no relied-on evidence. The fix would have been pinning the frontier model from the start, not downgrading.
  2. **Duplicate P2-ADJ-0002 work** in P2-AR-0034 and P2-AR-0039. The share is NOT_OBSERVABLE; a single-owner handoff would have avoided it.
  3. **Possible lower-tier sub-work** (docs, bookkeeping, textual merges). Not demonstrated.

## B8. Orchestrator session

| Field | Value |
|---|---|
| Model | `claude-opus-5[1m]` (system-declared) |
| Reasoning level | the harness shows the orchestrator a hint of 40 in some turns; semantics not documented |
| Budget indicator | the harness "total_tokens left" read 15,000,000 at start, 14,154,890 just before this request, and 15,000,000 on the next turn; semantics not documented |
| Input/output tokens, context utilisation, tool calls, compaction | NOT_OBSERVABLE |

---

## Record-keeping defects found while taking this snapshot (repaired)

1. **Unparseable run records.** 17 `AGENT_RUNS/*.run.yaml` files were not valid YAML. The orchestrator's recorder wrote free-text notes unquoted, so an embedded `": "` broke parsing. `check_state.py` did not parse run records, so this went undetected.
   - **Repaired** by quoting the affected note fields; the content is unchanged.
   - `check_state.py verify` now refuses any unparseable or duplicate-key run record.
   - The recorders now quote their notes.
2. **Stale `running_work`.** It still listed five completed round-3 runs; now pruned to the three truly running.

---

# C. Context and agent analysis (owner follow-up, 2026-09-19)

**Method.** This analysis is orchestrator-only and metadata-only. It is extracted by script from the transcript JSONL of the **37 completed** agents: per-request `usage`, `model`, `effort`, tool names, file paths and patterns in tool inputs, and the size of each tool result. No message or thinking text was loaded, and the three running builders were excluded. The Phase-2 transcript prohibition exists to keep roles independent, and it was lifted for this purpose only, at your request (ledger P2-L-0021). Per-agent data: `telemetry/P2-CONTEXT-TELEMETRY.json`.

**Corrections to section B (which was written before the transcripts were used):**

- **Now observed rather than NOT_OBSERVABLE:** the actual model and effort level; context per request (input + cache-read + cache-creation tokens); output tokens; compaction; and the time split.
- **What `subagent_tokens` counts:** it is approximately the agent's **final context size**.
- **The first pass ran on `claude-opus-4-6` at effort `high`, not `claude-opus-5`.** Every re-audit, synthesis, builder and integrator ran on **`claude-opus-5` at effort `xhigh`**.

## C1. Token consumption by role

| Role | n | Peak context median | Output tokens total | Input processed total (incl. cache reads) | Model time | Tool time |
|---|---|---|---|---|---|---|
| first-pass auditor (opus-4-6) | 6 | 150,968 | 369,753 | 39.7M | 1.2 h | 0.6 h |
| re-auditor (opus-5) | 6 | 840,156 | 2,223,752 | 506.7M | 3.1 h | 0.6 h |
| synthesis (opus-5) | 1 | 889,623 | 322,469 | 74.5M | 0.5 h | 0.5 h |
| repair builder (opus-5) | 22 | 812,006 | 8,314,275 | 2,655.2M | 14.7 h | 27.9 h |
| integration builder (opus-5) | 2 | 843,411 | 594,962 | 282.8M | 1.1 h | 1.4 h |

**Builders vs verifiers vs synthesis (tokens processed, input plus output):**

- Builders (repair plus integration, 24 agents): **2.95B**.
- Verifiers (re-auditors, 6 agents): **0.51B**.
- Synthesis (1 agent): **0.07B**.
- **Ratio: about 5.8 : 1 : 0.15.**
- Per agent, builders process about 1.4× what a verifier does. Builders run longer and loop through build/test repeatedly.
- More than 99% of processed input is cache reads of an ever-growing context. No cost figure is exposed.

## C2. Context-size thresholds

| Threshold | Agents that crossed it |
|---|---|
| ≥ 200k | 31  |
| ≥ 500k | 31  |
| ≥ 750k | 25  |
| ≥ 1M | 0  |

- **Every one of the 31 `claude-opus-5` agents exceeded 500k.** Their peaks ranged 606,793–964,988.
- **None reached 1M.**
- **Compaction occurred** (a context drop of more than 40% after exceeding 100k) in 11 agents: P2-AR-0001, P2-AR-0002, P2-AR-0003, P2-AR-0004, P2-AR-0005, P2-AR-0006, P2-AR-0013, P2-AR-0016, P2-AR-0025, P2-AR-0026, P2-AR-0034.
  - The six `claude-opus-4-6` first-pass auditors compacted once each at 130k–167k.
  - Five `opus-5` agents compacted once each, at about 910k–965k.
- **The orchestrator session itself** is at **943,882** tokens after 247 requests (`claude-opus-5`, `xhigh`, no compaction yet). A checkpoint and handoff are being written.

## C3. Repeated loading of Contract v3

- **Re-auditors:** loaded the whole contract 0–3 times each and their own gate sections 2–5 times each.
- **Synthesis:** loaded the whole file 5 times.
- **P2-AR-0014 (contract-binding builder):** 19 loads (4 whole-file), which its task explains.
- **Other builders:** mostly 1–9 targeted loads; eight of them (P2-AR-0015, 0019, 0026, 0030, 0032, 0034, 0037, 0039, 0040) loaded the whole file at least once although their classes touch 1–4 gates.
- **The cost is small.** Contract v3 is 42 KB. Contract reads are **0.7% (builders) to 4.4% (verifiers, synthesis)** of tool-result characters, so repeated contract loading is **not** a material driver of context size.

## C4. Where the context came from: repo history versus task scope

Shares of tool-result characters read into context. The agent's own output, which is 33–62% of context growth, comes on top of this.

| Role | Instructions & normative | Repo history & prior evidence | Task scope (source/tests/kernel) | Own execution/probe output | Unclassified searches & large-output re-reads |
|---|---|---|---|---|---|
| first-pass auditor (opus-4-6) | 19% | 1% | 62% | 16% | 3% |
| re-auditor (opus-5) | 14% | 6% | 52% | 4% | 25% |
| synthesis (opus-5) | 11% | 50% | 4% | 16% | 18% |
| repair builder (opus-5) | 4% | 20% | 44% | 7% | 25% |
| integration builder (opus-5) | 3% | 25% | 21% | 33% | 19% |

**Repo history and prior evidence is the second-largest source for repair builders.** It covers audit-0 evidence, earlier rounds' repair reports, git history and orchestration state, and repair builders were directed to read their predecessors' reports and integration points.

**Re-reads of identical file ranges are negligible** (0–1%). The high repeated-read counts are chunked reads of different ranges of the same large files.

## C5. Did builders receive whole-repository context unnecessarily?

This compares product-source characters read inside each builder's **owned files** against characters read outside them.

| Run | WS | In scope | Outside owned scope | Outside % |
|---|---|---|---|---|
| P2-AR-0014 | WS-1/12 | 37,373 | 62,576 | 63% |
| P2-AR-0015 | WS-2 | 106,197 | 175,220 | 62% |
| P2-AR-0016 | WS-3 | 231,464 | 264,277 | 53% |
| P2-AR-0017 | WS-4 | 87,090 | 143,450 | 62% |
| P2-AR-0018 | WS-5 | 108,524 | 122,171 | 53% |
| P2-AR-0019 | WS-6 | 200,329 | 68,448 | 25% |
| P2-AR-0020 | WS-8 | 287,905 | 61,770 | 18% |
| P2-AR-0021 | WS-9/11 | 213,332 | 85,885 | 29% |
| P2-AR-0023 | WS-2 | 262,924 | 218,541 | 45% |
| P2-AR-0024 | WS-3 | 238,627 | 102,795 | 30% |
| P2-AR-0025 | WS-4 | 299,610 | 309,154 | 51% |
| P2-AR-0026 | WS-5 | 150,128 | 203,525 | 58% |
| P2-AR-0027 | WS-6 | 157,499 | 159,169 | 50% |
| P2-AR-0028 | WS-7 | 111,804 | 136,954 | 55% |
| P2-AR-0029 | WS-8 | 335,734 | 91,256 | 21% |
| P2-AR-0030 | WS-9/11 | 184,551 | 168,525 | 48% |
| P2-AR-0031 | WS-10 | 15,614 | 347,810 | 96% |
| P2-AR-0034 | WS-3 | 196,242 | 150,879 | 43% |
| P2-AR-0037 | WS-6 | 252,825 | 159,806 | 39% |
| P2-AR-0038 | WS-7 | 162,553 | 128,016 | 44% |
| P2-AR-0039 | WS-8 | 170,584 | 160,157 | 48% |
| P2-AR-0040 | WS-9/11 | 208,200 | 131,444 | 39% |

- **Median outside-scope share: about 45%.**
- **The outside reads are mostly the integration surfaces** a builder must call or not break: `cli/src/main.rs`, `gates.rs`, `t2.rs`, `tasks.rs`, `breakglass.rs`, `records.rs`. Much of this reading is necessary, because the handoffs required builders to use cross-workstream APIs and preserve R1/§6.
- **WS-10 (P2-AR-0031) at 96% outside** is expected: its module was new.
- **The waste is real but bounded.** No agent was *handed* whole-repository context; each explored by search. About 10% of builder tool-result characters are unscoped directory-wide searches, and about 25% are unclassified searches or re-reads of large persisted outputs.

## C6. Was 1M-context Opus genuinely needed?

- **As run, yes.** Every `opus-5` agent's working context reached 606k–965k.
  - **At 200k (opus-4-6 behaviour):** the first-pass auditors compacted at about 130k–167k and produced the shallow, nonconforming audits.
  - **For the task, partly.** About half the peak context is the agent's own accumulated output (thinking, notes, code written). The rest is exploration history retained verbatim, not a simultaneous working set.
- **The simultaneous working set is smaller.** Product source is now 3.4 MB (about 1.0M–1.65M tokens), and each workstream's *owned* files alone are 180–520 KB, about 50k–250k tokens.
- **Conclusion:**
  - Audits and synthesis over a whole family genuinely benefited from a large window: they cross-reference many modules, the contract and prior evidence.
  - Builders did not *need* 1M as a working set. They filled it because nothing bounded exploration, and every tool result stays in context.

## C7. Tasks that could work from a bounded 50k–150k context pack

**Plausibly bounded (estimates, not demonstrated):**
- **Integration builders' mechanical part:** merge conflicts, G0 registration, schema-version mirroring.
- **Docs and spec-record amendments:** D-0010, API-0001, COMMANDS/ARCHITECTURE.
- **Single-class repairs with narrow owned files:** e.g. WS-7's pin/registry move, WS-9's command-test bound, WS-1/12's oracle schema, WS-10's lifecycle module if built from a spec.
- **Round 4's evidence map (BC-P2-02):** mostly mapping existing check IDs to capabilities.

**A pack for any of these:**
- handoff and protocol, about 10k;
- the class requirements, 5k–15k;
- owned files trimmed to the touched functions, 20k–80k;
- the signatures of consumed APIs, 5k–15k;
- the relevant findings and probes, 10k–20k.

**Not plausibly bounded:**
- **Family audits and synthesis:** they are exhaustive by contract and cross-module by design.
- **Cross-cutting trust and scheduler work:** WS-2 scheduler, WS-3 T2/human channel, WS-8 admission. This needed R1 held-out re-runs and wide invariants.

## C8. Were long-running agents reasoning or reading?

| Role | Estimated thinking share of output | Model time | Tool time (build/test/probe) | Tool-call mix |
|---|---|---|---|---|
| first-pass auditor (opus-4-6) | 0.00 | 1.2 h (66%) | 0.6 h | execute_probe 36%, read_file 33%, other_bash 13%, search 8% |
| re-auditor (opus-5) | 0.32 | 3.1 h (84%) | 0.6 h | read_file 40%, execute_probe 31%, write_edit 12%, search 11% |
| synthesis (opus-5) | 0.40 | 0.5 h (46%) | 0.5 h | read_file 37%, execute_probe 36%, write_edit 10%, search 9% |
| repair builder (opus-5) | 0.41 | 14.7 h (34%) | 27.9 h | read_file 43%, execute_probe 22%, search 12%, build_test 9% |
| integration builder (opus-5) | 0.46 | 1.1 h (44%) | 1.4 h | execute_probe 47%, read_file 18%, git 17%, search 7% |

- **Re-auditors were reasoning-heavy.** 84% of their wall time was model time, and about a third of output was estimated thinking.
- **Builders spent about two-thirds of wall time in tools** (cargo build/test under a machine load average of 40–100, and probe runs). Their generation was split between thinking (about 40%) and code written through Write/Edit (about half of tool-input characters).
- **So long builder runs were mostly execution-bound, not reasoning-bound.**
- **This split is an estimate.** Thinking text is redacted in the transcripts, so thinking tokens were estimated as output tokens minus visible text and tool-input characters at the calibrated 2.08 characters per token.

## C9. Observations only (routing unchanged, per instruction)

1. **Bounded exploration.** Most builder context was retained exploration. A per-workstream context pack (owned-function excerpts, API signatures, class requirements, findings), plus a rule to write findings to a scratch file instead of re-reading large outputs, would likely keep builders well under 500k.
2. **Contract reloading is not a cost problem** (≤ 4.4% of tool-result characters).
3. **The model tier matters for audits.** The only runs on a smaller window and older model were also the only audits that failed the evidence standard.
4. **The orchestrator session has reached about 94% of its window.** It is checkpointing now (P2-CP-0006, handoff P2-HO-ORCH-0001) so it can continue after compaction or in a replacement session from durable state.
