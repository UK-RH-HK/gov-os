# P2-AR-0012: iteration-0 capability re-audit, family `zeta` (Gate W)

| Field | Value |
|---|---|
| Run | P2-AR-0012 (fresh, independent re-audit under P2-HO-0009; scope = P2-HO-0006) |
| Role | capability-family-auditor |
| Agent model | claude-opus-5[1m] (Claude Opus 5, 1M context) |
| Candidate | `cap2-candidate-0` → commit `57177a37ea296ece16b185874831462b6a76db18` |
| Audited tree | `7eddf9103311a8e2ad144bcf61788f16b460782c` (candidate + one orchestration-only commit carrying P2-HO-0009) |
| Capabilities | W1–W12, Contract v3 lines 1066–1194 (Gate W, the W10 hard invariant, the Gate W advanced-qualification challenge) |
| Date | 2026-09-18 |
| Verdict | `FAMILY_AUDIT_COMPLETE` |

## 1. Result in one paragraph

Gate W is **partially implemented and does not meet AC-8**. Eleven of twelve W capabilities are `PARTIAL` and W11 is
`ABSENT`. Of the 86 checklist bullets: 19 are present and substantial, 34 partial, 32 absent, 1 N/A (the G6 injection bullet,
which is Phase-4 execution). The product has a sound core. Mandatory inputs of the core spec types are resolved
deterministically from governed records, independent of the index. The authority block is separated from retrieval and is never
displaced by token pressure. Session and model switches rebuild the same inputs. CIT-E propagates retest flags to open tasks.
Around that core, artefact flow is not governed end to end:
- tasks become READY and are closed with absent, superseded or conflicting inputs;
- several declared input types reach the worker only through retrieval;
- the context packet's hash does not change when the normative content of its inputs changes;
- task close records no consumption receipt and accepts fabricated traceability;
- completed work and its evidence are never invalidated by upstream change;
- orphans go undetected;
- none of the nine artefact-flow metrics exists;
- no G0–G6 tier performs its Gate-W duty beyond fragments;
- a retrieval or index outage withholds the deterministic inputs, which violates the W10 hard invariant.

All three AC-8 rejection conditions are met.

## 2. Pinned-input verification (all verified; no STOP)

| Input | Expected | Observed |
|---|---|---|
| `product_identity.py HEAD` product_code_digest | `bd4d65d9…0547` | `bd4d65d9d5ffd6aedbd9435e2091a664dfc3e62f80614a76197cfaf87efd0547` ✓ |
| governed_state_digest (HEAD) | recorded | `3dabf06a25e694f30182fd52549747826edcec29e9574f5a9c2c79705223ad91` |
| tag `cap2-candidate-0` | 57177a3 | `57177a37ea296ece16b185874831462b6a76db18` ✓ (HEAD adds only `P2-HO-0009-audit-0-reaudit-common.md`) |
| Contract v3 owner source SHA-256 | `4c2df291…5ed3` | ✓, and the canonical import is byte-identical ✓ |
| Frozen gate contract SHA-256 (ORCHESTRATOR_STATE.yaml) | `d2f33e89…f25e` | `d2f33e89d5459dd809e17271e46854cc886ed958ca63f89765e16d6a26a9f25e` ✓ |
| Frozen R0–R3 boundary SHA-256 | `70977d11…99c1` | ✓ |
| `gov contract verify` | CONTRACT_SOURCE_BOUND | ✓ (evidence/DV-derived-view-reconciliation.out) |
| `~/.cargo/bin/cargo build --release` | builds | ✓ (`gov version` 4.1.5) |
| Builder regression `cargo test --lib` / `cargo test --test certification` | green | 42 passed / 79 passed, 0 failed (evidence/builder-tests/). This is regression evidence only (O3). |

## 3. Method

* **Owner source first.** I read Contract v3 lines 1–130 and 1060–1255 (W1–W12, the W10 hard invariant at line 1164, the
  challenge at line 1194). I also read the capability sections Gate W names (C9, D1, H1, I2, K2, N1–N4, O3–O5) and framework
  §§15, 36–39, 41–44, 47–49 and 59–64. I established the bullet universe (86 bullets) from the owner source and then reconciled
  the derived views against it.
* **Code paths.** I read `runtime/src/context/mod.rs`, `records.rs`, `orchestration/{tasks,dag,readiness,handoffs}.rs`,
  `checkpoints.rs`, `cit/mod.rs`, `graph/mod.rs`, `retrieval/mod.rs`, `memory/{indexer,embedder,manifest}.rs`,
  `verification/mod.rs`, `doctor.rs`, `status.rs`, `observability.rs`, `contracts.rs`, `project.rs`, the record/task/report/
  handoff/checkpoint schemas and the policies Gate W depends on.
* **Executable evidence.** There are 17 probe scripts under `evidence/`, built on a small harness `evidence/lib/zprobe.py`.
  Each probe drives `target/release/gov` against disposable projects created from `fixtures/greenfield` and
  `fixtures/brownfield`. The environment mirrors the certification harness: `GOV_CANONICAL_ROOT` is set to the repository root,
  `XDG_STATE_HOME` to a per-project simulated machine, and every call passes `--json --root --session --role`.
  * Every `gov` call is logged verbatim with the product's JSON result.
  * Every observation line (`OBS <id>: PASS|FAIL -- …`) is computed from that output.
  * `evidence/OBSERVATIONS-INDEX.tsv` indexes all 333 observations (176 PASS, 157 FAIL).
  * `evidence/run-all.sh` re-runs everything, and `evidence/run-all.log` records the final run. W04b and W09 were re-run
    individually after last-minute additions; this is noted in the log.
* **Bullet-level.** Every bullet has its own observation(s). Where one output supports several bullets, the capability record
  names the exact observation ids.
* **Corrections I made to my own probes, recorded for the synthesis auditor.** Each was caught by re-reading the product
  output before any conclusion was drawn.
  1. An early readiness helper parsed the flow-style `READINESS_DIMENSIONS.yaml` wrongly. Every feature was left with all cells
     MISSING, which would have produced false "blocked" results. It now parses YAML, and all DAG observations were re-run.
  2. I found and fixed several false PASSes:
     - a keyword match on `conflicting_decisions`;
     - a packet "invalidation" match on the layer-3 key `staleness`;
     - close refusals caused by state left over from a previous scenario (W5 now uses one fresh project per scenario);
     - a no-op path-map edit;
     - probe files placed outside the contract's code roots.
  3. One observation was a tautology. I replaced it with a real persisted-field check.

## 4. Per-capability summary

| Cap | Title | Status | Bullets P / Pa / A / NA | Principal gap | Findings |
|---|---|---|---|---|---|
| W1 | Stable artefact identity | PARTIAL | 3 / 6 / 0 / 0 | Migration plans and audit findings lack stable identity; authored records carry no provenance; misplaced records undetected | A0-W1-01, A0-W2-01 |
| W2 | Typed output → input contracts | PARTIAL | 3 / 3 / 2 / 0 | No required/optional distinction; NARRATIVE records promoted into the authority block; no consumption schemas; inverted and missing edges | A0-W2-01/02, A0-W3-02 |
| W3 | Mandatory task-input manifest | PARTIAL | 2 / 3 / 4 / 0 | READY and claim with absent inputs; superseded inputs satisfy silently; no state/version/reason fields; conflicts not handled | A0-W3-01..04 |
| W4 | Context compiler delivery proof | PARTIAL | 2 / 4 / 0 / 0 | Normative content and versions not delivered; hash insensitive to them; datasets, experiments, research and task-level interfaces not delivered deterministically; missing inputs silent | A0-W4-01..05 |
| W5 | Consumption receipt & traceability | PARTIAL | 1 / 5 / 3 / 0 | No receipt of consumed inputs, implemented requirements or applied decisions; fabricated trace accepted; no refusal; no back-links | A0-W5-01..03 |
| W6 | Upstream-change staleness propagation | PARTIAL | 0 / 3 / 4 / 0 | DONE work never invalidated; no rework tasks; close clears retest; non-CIT changes propagate nothing; packets never invalidated | A0-W6-01..05, A0-W2-01 |
| W7 | Orphan / unexplained output detection | PARTIAL | 0 / 2 / 4 / 0 | Only dangling consumers named plus an anonymous orphan count; no remediation | A0-W7-01 |
| W8 | Forward and reverse lineage | PARTIAL | 0 / 4 / 1 / 0 | Lineage stops before code, tests, evidence and release; stale links undetected; no cross-language link | A0-W8-01, A0-W5-02 |
| W9 | Session/handoff continuity | PARTIAL | 4 / 1 / 1 / 0 | Handoff never blocked or degraded for missing or stale inputs; checkpoint state reference can lag | A0-W9-01, A0-W5-03 |
| W10 | Deterministic inputs outrank retrieval | PARTIAL | 4 / 0 / 1 / 0 | An index outage withholds the deterministic block (hard invariant) | A0-W10-01 |
| W11 | Artifact-flow quantitative health | **ABSENT** | 0 / 0 / 9 / 0 | None of the nine metrics exists | A0-W11-01 |
| W12 | Health-scheduler integration | PARTIAL | 0 / 3 / 3 / 1 | No tiering; G1–G3 duties absent; G0 does not guard current-version substitution; G5 HEALTHY on superseded consumption | A0-W12-01, A0-W6-05, A0-W-01 |

**AC-3 argument for every PARTIAL.** Every PARTIAL is `COULD_UNDERMINE`. Each gap sits on a path that the Gate W
advanced-qualification challenge (Contract v3 line 1194) or its hidden oracle exercises directly: *"correct required
input/version and expected downstream propagation"*. `capability-audit.yaml` states the argument per capability.

## 5. AC-8: Artifact Flow Coverage Matrix and determination

`artifact-flow-coverage-matrix.yaml` has 14 rows, one per W1-named type plus two equivalents:
- requirement, feature, scenario, decision, dataset, experiment, architecture record, interface, test design, migration plan,
  audit finding and benchmark result;
- equivalents: research record and execution report.

Each row has the 10 evidence columns plus a dedicated qualification challenge (W-QC-*). Of the 140 cells, 24 are EVIDENCED,
55 PARTIAL and 61 GAP. Every non-GAP cell names an executed observation.

**Determination: AC-8 NOT MET.** All three rejection conditions are triggered:

| Rejection condition | Triggered | Decisive evidence |
|---|---|---|
| Semantic retrieval relied on to rediscover mandatory inputs | **yes** (partially) | Experiments and research declared via `derived_from`, and interfaces declared on the task, are absent from the authority block and reachable only through retrieval. Datasets in `required_data` are not delivered at all (W04b). Deterministic delivery also depends on retrieval being available (W10-a4). Not triggered for requirements, decisions, scenarios, feature interfaces or architecture. |
| Stale versions can silently satisfy downstream work | **yes** | Superseded requirement → task READY → DONE, and audit HEALTHY (W3-r2, AC16-W12xO5). After a direct spec change plus an index rebuild, the dependent task closes on the pre-change packet (AC16-W6xD1). Close clears retest (W6). |
| Completion cannot be traced to upstream evidence | **yes** | No receipt; fabricated trace accepted (W5-c1, W5-r3r4). Lineage and impact never reach code or evidence (W5-c3, W8-l1/l2). |

## 6. W10 hard-invariant attacks (by construction; evidence/W10-hard-invariant-attacks.py)

| # | Attack | Construction | Result |
|---|---|---|---|
| 1 | Current spec absent from the semantic index | (i) Contract rule `semantic_index:false, lexical_index:false` for REQ-0002. Precondition verified: 0 vectors, and a semantic query for its own title does not return it. (ii) Its chunks, vectors and FTS rows deleted from state.db. | **PASS**: delivered in both cases |
| 2 | Superseded spec with higher similarity | REQ-0001 SUPERSEDED, worded like the task query. Verified to outrank the current REQ-0002 (semantic rank 2 vs absent). Variant: supersession recorded only on the successor. | **PASS**: never in either block. *Structured* stale reference: FAIL (recorded under W3) |
| 3 | Token pressure | `CONTEXT_POLICY.max_packet_chars` overridden to det+1500, det+400 and 300 | **PASS**: only retrieved slices dropped; explicit warning when the authority block alone exceeds budget |
| 4 | Retrieval/index outage | state.db deleted (the INV-010 case); corrupted; vector table dropped; embedder re-pinned before reindex; pinned reranker missing | **FAIL** 4/5: `context compile` and `continue` abort with INDEX_MISSING, DB_ERROR, EMBEDDER_MISMATCH or RERANKER_UNAVAILABLE. Only the dropped-table case passes, because the schema init recreates the table. |
| 5 | Independently testable | deterministic_authority and deterministic_hash exposed separately | **PASS**. The product's own suite does not test delivery against the declared inputs. |

## 7. W12: each G0–G6 tier's Gate-W duty (evidence/W12-scheduler-integration.py)

There is no G-tier scheduler in the candidate: no tier identifiers, no RED/YELLOW/GREEN, and no impacted-check selection in
`runtime/` or `cli/`. Each duty was exercised at the hook point that plays that tier's role.

| Tier | Duty | Observed |
|---|---|---|
| G0 | Block invalid authority / current-version substitution | Authority substitution **blocked**: a superseded approval decision makes `cit execute` refuse with GATE_REVOKED. Current-version substitution **not blocked**: a task on a SUPERSEDED input is claimed, and a CIT editing a SUPERSEDED record executes. |
| G1 | Invalidate dependency/lineage evidence after a mutation | Index staleness detected; **nothing invalidated** |
| G2 | Verify input, consumption and traceability at close | **absent**: close succeeds with a never-existing input and no receipt |
| G3 | Verify mandatory-input continuity at checkpoint/handoff | **absent**: stale-packet handoff, missing-input handoff and missing-input checkpoint all succeed |
| G4 | Wider propagation after CIT/spec/decision/architecture changes | Via an architecture_change CIT (R3): retest plus stale tests (**PASS**). A non-CIT architecture change: nothing. |
| G5 | Audit end-to-end lineage and orphans | A dangling missing input is reported (DEGRADED). A DONE task on a SUPERSEDED input still yields audit **HEALTHY**. The doctor there is DEGRADED only through D022, the unrelated ecosystem check. No lineage audit; orphans not named. |
| G6 | Inject hidden artefact-flow failures | N/A_WITH_REASON: this is Phase-4 execution (frozen contract §7, AC-6). The tier's existence is O5/AC-5, owned by another family. |

## 8. AC-16 interactions exercised (W side)

| Interaction | Exercise | Outcome |
|---|---|---|
| W12 ↔ O5 | Health verdict with Gate-W faults (W12 G5 block) | Verdict reflects a dangling input; blind to superseded consumption; no tier structure |
| W6 ↔ K2 | CIT-E propagation at R1, R2 and R3 (W06 paths A/A2, W12 G4) | Open tasks retest; tests stale at R2 or above; DONE work, reports and packets untouched; close clears retest |
| W6 ↔ D1 | Direct spec edit, then index freshness, close, rebuild, close (W06 B1) | D1 detects the change and blocks close until rebuild; the rebuild then licenses consumption of the pre-change packet |
| W6 ↔ O4 | D021 green-record currency after spec/task/source/index changes (FR, W06 B1) | Green record stays current (see §9) |
| W9 ↔ N | before_handoff checkpoint on a stale packet; checkpoint state reference; doctor checkpoint checks (W09) | Stale hash recorded unmarked; reference taken before reindex; no checkpoint-freshness check |

## 9. Freshness and invalidation (AC-10), shown rather than assumed (evidence/FR-freshness-invalidation.py)

The only persisted green evidence is the governance-suite audit record, whose currency doctor D021 reports. It is keyed by
`inputs_hash`, which covers governance/kernel, governance/project, governance/tests, spec/decisions and framework.lock.

| Input class changed (Contract v3 lines 97–109) | Green record invalidated? |
|---|---|
| Policy, installed schema, retrieval profile, path map, sensitivity policy, decision | yes |
| Requirement, interface, architecture record, task input manifest, source file, index manifest | **no** (stays green) |
| Runtime binary | not attempted (the audited binary is the pinned candidate) |

Every W capability's evidence is fresh for the exact candidate. Its product-side invalidation is not demonstrated for the
Gate-W-relevant input classes (finding A0-W6-05).

## 10. Derived views (frozen contract §1; evidence/DV-derived-view-reconciliation.py)

The compiled YAML lists W1–W12 with correct titles, requirement class and source lines. However, it carries:
- 0 of the 86 Gate W bullets;
- neither the W10 hard-invariant text nor the Gate W challenge;
- none of the per-capability fields in lines 53–73.

The evidence map marks all twelve W capabilities `NOT_YET_MAPPED`, with no automated checks. The generated view lists them.
This is recorded as A0-W-01 (AC-13 and AC-10). Cross-gate adjudication belongs to the synthesis auditor.

## 11. Findings (27; 24 blocking; none requires an owner decision)

| Severity | Blocking | IDs |
|---|---|---|
| HIGH (15) | yes | A0-W3-01, A0-W3-02, A0-W3-03, A0-W4-01, A0-W4-02, A0-W4-03, A0-W5-01, A0-W6-01, A0-W6-02, A0-W6-05, A0-W7-01, A0-W9-01, A0-W10-01, A0-W11-01, A0-W12-01 |
| MEDIUM (9) | yes | A0-W1-01, A0-W2-01, A0-W2-02, A0-W3-04, A0-W5-02, A0-W6-03, A0-W6-04, A0-W8-01, A0-W-01 |
| LOW (2) | no | A0-W4-04 (duplicate delivery), A0-W5-03 (porcelain path truncation) |
| INFO (1) | no | A0-W4-05 (over-budget packet dispatched with a warning) |

Every repair direction is stated as a requirement and derived from the owner source. None needs a choice that the accepted
sources do not make, so `owner_decision_required` is false throughout.

All findings are `BASELINE`, which establishes the iteration-0 blocker-class inventory. Each finding carries a `blocker_class`
id of the form `W<n>/<mechanism>`.

## 12. What I could not establish, and why

* **Migration-plan consumption beyond A4.** I did not independently run A5 review or A6 migrate. The consumption cell cites the
  builder's brownfield certification test, which is regression evidence only.
* **Invalidation by a runtime-binary change.** Not attempted, because the audited binary is the pinned candidate.
  `inputs_hash()` does not include a runtime identity (runtime/src/verification/mod.rs:54-71).
* **Invalidation of a benchmark-derived decision when a later benchmark disagrees.** Not probed. The absence is stated from code:
  the only writer of staleness is CIT-E.
* **Cross-repository lineage.** The product is single-repository by design, and I found no normative text that requires
  multi-repository lineage for this candidate. Recorded as a note, not a gap.
* **R1 item on Gate W mappings.** R1 (frozen boundary §R1) lists *"the original product controls, Gate W and G0–G6
  implementation mappings remain valid"* as accepted. I did not examine how R1 evaluated that item. AC-14 is the synthesis
  auditor's.

## 13. Later-lifecycle notes (not Phase-2 blockers)

* G6 hidden artefact-flow fault injection and generation of the W-QC-* repositories are Phase 4.
* R2 requires *"Gate W dependency/consumption evidence"* (frozen boundary §R2). The gaps above will recur there if not closed.
* Phase 3 retrieval-profile selection re-pins the embedder. Until A0-W10-01 is closed, every re-pin makes context delivery fail
  until a full rebuild completes (W10-a4 embedder case).

## 14. Evidence index

| Path | Content |
|---|---|
| `capability-audit.yaml` | 12 capabilities, 86 bullets, schema per P2-HO-0000 |
| `findings.yaml` | 27 findings |
| `artifact-flow-coverage-matrix.yaml` | AC-8 matrix and determination |
| `evidence/lib/zprobe.py` | Probe harness |
| `evidence/W00…W12*.py` / `.out` | Per-capability probes and outputs (W01b migration plan; W04b per-type delivery) |
| `evidence/FR-freshness-invalidation.*` | AC-10 demonstration |
| `evidence/DV-derived-view-reconciliation.*` | Derived-view reconciliation |
| `evidence/OBSERVATIONS-INDEX.tsv` | Every observation: file:line, id, result |
| `evidence/run-all.sh`, `evidence/run-all.log` | Reproduction script and final run log |
| `evidence/builder-tests/*.out` | `cargo test --lib`, `cargo test --test certification` |

Reproduce: from the worktree root run `~/.cargo/bin/cargo build --release`, then
`release/capability-baseline/audit-0/zeta-r/evidence/run-all.sh`. It needs python3 with PyYAML and git.
