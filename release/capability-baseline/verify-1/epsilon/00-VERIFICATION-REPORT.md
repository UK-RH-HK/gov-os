# P2-AR-0050 — Phase-2 verification iteration 1, capability family `epsilon`

| Field | Value |
|---|---|
| Run | **P2-AR-0050** — fresh independent capability-family verifier, iteration 1 |
| Family | `epsilon` — O1–O5, P1–P2, Q1–Q4, **U**, V1–V4 (146 checklist bullets, 16 capabilities) |
| Candidate | `cap2-candidate-1`, commit `0bad524d836f179964ffbac31972856ea6434682` |
| `product_code_digest` | `e6332fc7d5af5c73adbe0f200003db30fe5a6fd0b7f24d047d3e340e6f972220` |
| `governed_state_digest` | `3d2aeba2fc3b52a95c369c49a854bb9d443b0b03da1180db5339f01d892620c0` |
| Worktree | `phase2/verify-1-epsilon`, at orchestration commit `8588813` (identical product code and governed state) |
| Verdict | **FAMILY_VERIFICATION_COMPLETE** |
| Blocking findings | **1** — `E-O5-01` (MEDIUM, AC-5), labelled **RESIDUAL** of `BC-P2-07` |
| Non-blocking findings | 3 — `E-P2-01`, `E-Q1-01`, `E-Q2-01`, all **RESIDUAL** |
| Materially new findings | **none** |

## 1. Scope, independence and method

I authored none of the Governance OS implementation, none of its tests, none of the iteration-0 audits, none of
the repairs and no Phase-1 role. I am not the orchestrator. I modified no product source: everything I wrote is
under `release/capability-baseline/verify-1/epsilon/` and the run report.

This is a **full re-audit**. Every iteration-0 status was treated as stale; every one of the 146 bullets was
established afresh on this candidate from my own evidence. I read the repair and integration reports under
`release/capability-baseline/repair-1/**` only as claims to attack, and cite none of them as evidence.

**What I ran.** `CARGO_BUILD_JOBS=2 cargo build --release` in my own worktree, then 167 held-out probes I wrote
myself (`heldout/`, eight files plus a `RUN-ALL` driver), driving `target/release/gov` against disposable
projects. The probes are written from Contract v3 and the product's observable behaviour, not by copying builder
tests or builder probes; none of them enters the product tree.

**Provisioned posture.** Several bullets (a GREEN health state, the authenticated human channel, the owner-signed
gate answer the Q4 export gate requires) are unreachable on an unprovisioned machine by design (OD-P2-02, and
doctor D032 keeps such a machine YELLOW). Rather than record them as not establishable, I wrote my own
administrator-domain signer (`heldout/srr.py`, ~160 lines of Python over `cryptography`), reproduced the Signed
Release Root document shapes from `runtime/src/srr/`, published a signed release of the payload, provisioned a
throw-away root per probe project and installed through `gov init --source`. This is test material by
construction (published constant seeds) and it is mine, not the product's certification harness. It let me
establish GREEN, the `human-gate` delegation, and the full Q4 path end to end.

**Reproduce everything:** `release/capability-baseline/verify-1/epsilon/heldout/RUN-ALL`
(needs `python3` with `cryptography` and `PyYAML`, and the candidate built in the worktree).

## 2. Pinned inputs (all verified — `evidence/pinned-inputs.out`)

| Input | Result |
|---|---|
| `git rev-list -n1 cap2-candidate-1` | `0bad524d836f179964ffbac31972856ea6434682` ✓ matches dispatch |
| `product_identity.py 0bad524…` | both digests ✓ match dispatch |
| `product_identity.py HEAD` (`8588813`) | both digests identical to the tag's ✓ |
| Contract v3 SHA-256 | `4c2df29115c8d5389034b2e2d817772add80d61678807c23e0d520c937cb5ed3` ✓ |
| Frozen gate contract SHA-256 | `d2f33e89d5459dd809e17271e46854cc886ed958ca63f89765e16d6a26a9f25e` ✓ |
| Governing documents | the three `*.md` at the repository root, present ✓ |

No STOP condition. Regression on the candidate, reproduced in my own worktree
(`evidence/AC-15-regression.out`): `cargo test --release --lib` **276 passed, 0 failed**;
`cargo test --release --test certification` **207 passed, 0 failed**. Builder tests are regression evidence
only (O3); the independent-evidence column throughout is what I ran.

## 3. Per-capability summary

| Cap | Title | Status | Bullets met | Findings |
|---|---|---|---|---|
| O1 | Product test families | **PRESENT_AND_SUBSTANTIAL** | 10/10 | — |
| O2 | Governance test families | **PRESENT_AND_SUBSTANTIAL** | 17/17 | — |
| O3 | Independent test authorship | **PRESENT_AND_SUBSTANTIAL** | 3/3 | — |
| O4 | Governance suite currency | **PRESENT_AND_SUBSTANTIAL** | 2/2 | — |
| O5 | Governance Health Scheduler | **PARTIAL** | 12/14 | E-O5-01 |
| P1 | Execution telemetry | **PARTIAL** | 9/13 | E-P2-01 |
| P2 | Organisational questions | **PARTIAL** | 4/8 | E-P2-01 |
| Q1 | Lesson lifecycle | **PARTIAL** | 3/8 | E-Q1-01 |
| Q2 | Decision vs lesson | **PARTIAL** | 1/2 | E-Q2-01 |
| Q3 | PROJECT/PRODUCT/FRAMEWORK scope | **PRESENT_AND_SUBSTANTIAL** | 1/1 | — |
| Q4 | Upstream Export Gate | **PRESENT_AND_SUBSTANTIAL** | 5/5 | — |
| U | Framework Health SLOs | **PARTIAL** | 27/28 | E-O5-01 |
| V1 | Fault manifest | **PRESENT_AND_SUBSTANTIAL** | 9/9 | — |
| V2 | Hidden path-map oracle | **PRESENT_AND_SUBSTANTIAL** | 7/7 | — |
| V3 | Hidden memory oracle | **PRESENT_AND_SUBSTANTIAL** | 7/7 | — |
| V4 | Quantitative qualification scoring | **PRESENT_AND_SUBSTANTIAL** | 12/12 | — |

No capability is `ABSENT` or `UNCLEAR`; no capability is recorded `N/A_WITH_REASON`. Every `PARTIAL` carries its
AC-3 argument in `capability-audit.yaml` (`partial_qualification_impact`). Two of them — O5 and U — argue
`COULD_UNDERMINE`, for the same single cause (E-O5-01); the other three argue `CANNOT_UNDERMINE`, with the
reasoning stated against what the V4 metrics actually measure.

## 4. AC-5 — the health-scheduler determination, item by item

AC-5 is established **by exercising** the scheduler, not by reading it. Each row below was driven on a
provisioned, converged project.

| AC-5 item | Result | What I observed |
|---|---|---|
| impacted-test selection | **MET** | A one-line source comment executed **18 of 39** checks and reused 21; a decision-record change selected a **different** set of 28; with no change, 32 reused and only the 7 never-cacheable checks ran. Selection is derived from each check's declared input classes, not guessed. |
| parallel execution of independent checks | **MET** | `parallelism.workers: 4`, four named worker threads, and a run wall clock of **2338 ms against 5772 ms** of executed check time — arithmetically impossible serially. |
| safe isolation | **MET** | `memory_retrieval_regression`, `context_reproducibility`, `skill_regression`, `recovery_rebuild` declare `Sandbox`/`OwnSandboxes`, report `isolated_in_sandbox: true`, leave the live derived state (`.governance-runtime/index`, `governance/generated`, `.governance-state`) byte-identical, and dispose of their sandboxes. |
| cache reuse | **MET** | 32 of 39 served from a per-check cache under unchanged inputs; every reused result names the health result it was computed in. |
| cache invalidation | **MET** | Keyed on the digests of exactly the declared inputs: a project-policy change (implicit dependency of every check) re-executed all 39; an unrelated file change re-executed 18 and reused 21. |
| stale evidence | **MET** | A relevant input change moved the green record from `current: true` to `current: false`, naming the changed class, and 60 checks were reported stale; doctor checks appear in `stale_checks` too. |
| RED/YELLOW/GREEN aggregation | **MET, with a caveat** | GREEN on a clean provisioned repository, YELLOW on a warning-only failure, RED on an active hard-block — all three observed. Caveat: the aggregate ignores staleness and the repository verdict, so it can read GREEN while the same output reports DEGRADED — see E-O5-01, whose cause is the unrun doctor half. |
| hard-block vs warning semantics | **MET** | All **74** catalogue entries declare `enforcement.mode`. A warning failure (index_freshness, medium) lowered the state and refused nothing; a hard-block failure (schema_invariants, high) refused exactly its scope with typed refusals. |
| health-result provenance | **NOT MET** | The record is rich (tier, tier duty, trigger, per-check status/duration/cache source/enforcement, per-class input digests and their hash, runtime identity incl. the gov binary's sha256, repository state, actor, machine trust, parallelism, cache mode, selection, times) — but it reports `complete: true, not_evaluated: 0` over a tier whose 35 doctor members it never enumerated. **E-O5-01.** |
| remediation / task generation | **MET** | A high finding generated a governance task whose `generated_from` names the source (`audit-finding`), the subject (the check), a stable generation key and the detecting surface, and whose record declares `remedies: [<check>]`. When the finding survived a close, the generator produced the successor with `recurrence: 1`. |
| does **not** serially re-run the whole suite for a trivial mutation | **MET** | 18 of 39 checks, concurrently, in 1.3 s wall, against 39 serially before. |
| G0–G6 tiers exist and perform their duties | **MET for G0–G4 and G6; PARTIAL for G5** | Every tier is declared with a duty and a non-empty membership and was executed (G1 27, G2 28, G3 33, G4 39, G5 39 checks evaluated). G0 guards every mutating command (census under `FREEZE_WRITES`). G1 observes a mutation *however made*. G2 runs at close. G3 runs at `handoff create` and judges input currency. G4 is the milestone tier. G6 exists as `gov health qualify`. **G5 does not execute the doctor half of its own declared membership (E-O5-01).** |

**AC-5 determination: NOT MET on this candidate**, on one item (health-result provenance) plus the G5 tier
duty, both from the single cause recorded as `E-O5-01`. Every other AC-5 behaviour is met and was exercised.

## 5. Availability-rule attacks (Contract v3 L4 and O5 :807; P2-HO-0031) — 15/15

Attacks were driven against real governed operations, not only `gov health guard`. A subject-scoped `high`
`schema_invariants` block was induced over two named decision records, with a second, independent work stream in
the same project.

| Required property | Result | Evidence |
|---|---|---|
| a block refuses only within its scope | **HOLDS** | Closing work on the independent record `D-AV-2` and on an unrelated source path was admitted while the block's own subjects were refused. |
| its listed remedy stays available | **HOLDS** | `cit.propose` on the block's own subjects was admitted **as its remedy** (`remedy_for: [schema_invariants]`); the generated remediation task, declaring `remedies: [schema_invariants]`, was claimable under the block it repairs. |
| independent work stays available | **HOLDS** | `task.create`, `task.claim`, `handoff.create`, `cit.propose`, `cit.approve` all admitted; a real `gov task create` succeeded. Diagnosis and repair commands (`doctor`, `audit`, `health status`, `status`, `recover`, `rebuild-memory`, `checkpoint list`) were never refused by a block. |
| no block refuses its own remedy | **HOLDS** | The block lists `cit.propose/approve/execute`, `task.create/claim`, `handoff.create` among its remedies and admitted them. |
| every refusal is typed and names its scope | **HOLDS** | `HEALTH_HARD_BLOCK`, with each named block carrying `check`, `severity`, `scope` and `subjects`, plus the remedy sentence. |
| a committing remedy that does not clear its block does not commit | **HOLDS** | Closing the repair task after touching the blocked subject **without** repairing it was refused (`HEALTH_HARD_BLOCK`); `task.close` is not in any block's remedy list, so a close must clear the condition. `HEALTH_REMEDY_INCOMPLETE` is the `admit` + `confirm_remedy` counterpart, reached by `update --apply`; I did not exercise that path (see §8). |
| a block whose inputs changed is re-evaluated before it refuses | **HOLDS** | After repairing the condition with a plain file move and **no** `gov health run`, the next `gov health guard task.close` observed the change itself (`observed.tier: G1`, 1 changed path, 14 checks re-executed), cleared the block and admitted the operation. |
| …and does not stop refusing spuriously | **HOLDS** | Re-introducing the duplicate made the very next guard refuse again. |
| L4 "global stop only when policy or critical-path state requires" | **HOLDS as interpreted** | Only a **critical** finding refuses all ten governed operations globally (14 checks carry such a rule, every one at `critical`). Two `high` rules are global but narrow: `release.build` and `update.apply`, which rely on the whole repository — consistent with L4, and `update.apply` remains admissible as its own remedy. |

## 6. Gate U — SLOs and the HEALTHY conjunction

**Every one of the 15 SLOs (Contract v3:979–993) is tracked with a declared threshold and a declared owning
check**, from `framework/health/HEALTH_SLOS.yaml`, compiled into the runtime and reported by the `health_slos`
suite family, `gov health status` and doctor D035.

I crossed **14 of 15** and each crossing changed the health state away from GREEN: stale-index count,
orphan-graph count, unresolved contradictions, unresolved human gates, task traceability, feature-readiness
coverage, context-packet size, tokens per completed task, first-pass completion, handoff failure, memory-rebuild
success, fresh-agent reconstruction, retrieval Recall@K, product-test health. Real repository state was used
where it was cheap (a duplicate id, an orphan requirement, four untraced tasks, an empty-readiness feature, a
failing configured test family, a DONE task recording 4 000 000 tokens with `repair_count: 2`, a handoff returned
`failed`, a mismatched index manifest); where it was not, the threshold was tightened through
`PROJECT_POLICY.policy_overrides`, which is the mechanism the declaration itself reads and which
`gov policy overrides` confirmed applied (`refused: []`).

The fifteenth, **governance-suite freshness**, crosses exactly as the contract requires (`current: false`, the
changed class named) and the HEALTHY conjunction fails H10 on it — but the **RED/YELLOW/GREEN** state stays GREEN
until `gov doctor` runs, because the SLO's declared owner is the doctor check D021 that no tier run executes.
That is E-O5-01 reaching Gate U; it is not a second defect and it is not a missing threshold.

**The HEALTHY conjunction is implemented.** `gov health status` → `repository.verdict` evaluates all thirteen
conditions of Contract v3:996–1008; each cites its contract line and names the checks that enforce it; the verdict
is HEALTHY only when all thirteen hold, and doctor D035 enforces the same conjunction. I drove eight of the
thirteen from HOLDS to FAILS individually (H1, H4, H5, H7, H9, H10, H11, H12) and watched the verdict leave
HEALTHY naming them. For the remaining five (H2, H3, H6, H8, H13) I did not flip the condition itself; I
demonstrated the detection of their owning checks one at a time (`legacy_authority`; `change_control_integrity`,
`os_binding_integrity`, `task_contract_integrity`; `path_map_compliance` and `secrets_sensitivity_indexing`;
`concurrency_claims`; `recovery_rebuild`), and the conjunction is the same mechanism that was shown to fail for
the eight. I record that distinction rather than claim more than I ran.

## 7. O4 currency, and the rest of Gate O

**O4.** From a legitimately current green baseline (P2-ADJ-0003: the baseline is built to be legitimately green,
not asserted), I changed **nine input classes one at a time** — `project_policy`, `spec_decisions`,
`spec_requirements`, `spec_architecture`, `source`, `sensitivity`, `path_map`, `tools_plugins`, `model_profile` —
and each one alone moved the green record from current to stale, naming exactly that class. The currency key
covers 32 declared classes, including the gov binary's sha256 (`runtime_identity`) and `machine_trust`. A
governance-affecting close is decided on a suite result the close gate runs **itself** for the current inputs
(`g2.complete: true`, `g2.inputs_hash` = the post-change key), never on the pre-change record — verified with the
green record demonstrably stale at close time. Iteration-0's BC-P2-03 defect as stated is closed.

**O1.** All ten families (including `smoke` for "live/smoke") run by name, sealed into governed records; a failing
family turns health RED and raises scoped blocks; a report claiming `tests.status: passed` against failing
recorded evidence is refused `PRODUCT_TEST_EVIDENCE_REQUIRED`.

**O2.** All 17 families exist and execute. I injected a defect of its own class into 13 of them and each raised
the finding (`heldout/t08_o2_detection.py`). For three — context reproducibility, product traceability, audit
reproducibility — I could not construct a failing case in a synthetic project and instead evidenced the
measurement they perform (a packet's deterministic hash and delivery state; the traceability population; **31
checks compared by concurrent double run, 0 mismatches**). I say so rather than claim detection I did not see.

**O3.** Independence is no longer self-attested. An obligation declaring `independent_of_implementer: true` and
`author_role: qa` does not open the DAG gate; the refusal says those are "the artefact's own claims, not
evidence", and independence is taken from the recorded author of a sealed close report.

## 8. Findings I raise

| Id | Capability | Severity | Blocking | AC | Label |
|---|---|---|---|---|---|
| `E-O5-01` | O5, U | MEDIUM | **yes** | AC-5 | **RESIDUAL** of `BC-P2-07` |
| `E-P2-01` | P2, P1 | LOW | no | — | **RESIDUAL** (`inventoried_class: null`; A0-P2-01 / A0-P1-01) |
| `E-Q1-01` | Q1 | MEDIUM | no | — | **RESIDUAL** (`inventoried_class: null`; A0-Q1-01) |
| `E-Q2-01` | Q2, Q1 | MEDIUM | no | — | **RESIDUAL** (`inventoried_class: null`; A0-Q2-01) |

**None is materially new.** On labelling: the inventory I was given contains blocking classes only, so a
non-blocking finding cannot name one. Rather than label three non-blocking findings `MATERIALLY_NEW` on a
technicality — which would misstate convergence — I labelled them `RESIDUAL` with `inventoried_class: null` and
named the iteration-0 finding each restates. The orchestrator can see the reasoning in `findings.yaml`; I flag
the ambiguity here rather than resolve it silently.

`E-O5-01` in one paragraph: `gov health checks` declares D001–D035 at tiers G1 and G5 (15 of them hard-blocking,
8 at critical over every governed operation), but `run_suite` iterates the governance-suite families only, and
`doctor::run` is reached from exactly two places — the G0 guard's block re-evaluation and the `gov doctor` CLI.
So `gov health run --tier G1/G5`, `gov audit`, `update --apply` and `release build` evaluate 39 of 74 declared
checks while reporting `complete: true, not_evaluated: 0`. Observable consequence: after a relevant input change,
`gov health status` reads **GREEN** with no failing check while the same output reads
`repository.verdict: DEGRADED`, `currency.current: false` and 18 stale checks; `gov doctor` then makes it YELLOW
on D021. The loss is bounded — doctor checks *are* reported stale, the G0 guard *does* re-evaluate them before
refusing, and `gov adopt audit` and `gov init` *do* run doctor — but a tier that claims a full suite and leaves a
third of its declared membership unevaluated does not meet AC-5's provenance and G5 requirements.

## 9. Iteration-0 findings: dispositions

38 prior findings were in scope (36 from the epsilon audit of record `P2-AR-0008`, 2 from synthesis).
Full reasoning in `prior-findings-disposition.yaml`.

| Disposition | Count | Of which were blocking |
|---|---|---|
| **CLOSED** | 25 | 22 |
| **RESIDUAL** | 6 | 1 |
| **NOT_APPLICABLE** | 7 | 5 |

**Closed (blocking):** A0-O1-01 (product tests governed), A0-O2-01 (skill scenarios executed), A0-O3-01
(independence not self-attested), A0-O4-01 and A0-O4-02 (currency key and close gate), A0-O5-01…04
(selection, parallelism, isolation, cache), A0-O5-05 (G0 command census), A0-O5-06 (G1/G2), A0-O5-07 (G3),
A0-O5-08 (G4), A0-O5-10 (G6 exists), A0-O5-11 (block vs warn), A0-O5-12 (provenance persisted), A0-O5-13
(remediation generated), A0-Q1-02 (owner-signed export approval), A0-Q4-01 (export gate no longer fails open),
A0-U-01 (SLO thresholds), A0-U-02 (HEALTHY conjunction), A0-V1-01 (oracle format exists). Also closed, non-blocking:
A0-O2-02, A0-O2-03, A0-O5-15.

**Residual:** A0-O5-09 → `E-O5-01` (the G5 doctor half); A0-P1-01 and A0-P2-01 → `E-P2-01`; A0-Q1-01 →
`E-Q1-01`; A0-Q2-01 → `E-Q2-01`; A0-O1-02 (`TEST_POLICY.product_families` is still `overridable`).

**Not applicable here:** A0-O1-03, A0-O5-14, A0-U-03 (contract-view and evidence-map defects — AC-13/AC-10,
the synthesis verifier's); A0-O4-03 (W6/K2 upstream propagation — zeta's and delta's); A0-O5-05's role-resolution
half and S0-I4-01 (E1/A5/S3/S4/T1 and I4 — alpha's and gamma's); A0-Q1-03 (canonical-repository intake, and
non-blocking); S0-R1-01 (AC-14, the R1-preservation verifier's). In each case I say which family owns it rather
than restate a judgement that is not mine.

## 10. Gate V — capability statuses (not the AC-6 acceptance)

V1–V4 are all `PRESENT_AND_SUBSTANTIAL`. A machine-checkable format exists (`gov oracle format`, format sha256
`f89a3e2f…16fd`, a JSON Schema plus semantic rules, bound to the owner source's sha256) whose crosswalk maps
**every one of the 35 V1–V4 checklist bullets** to a field, by owner-source line. It fails closed: removing any
one of the 37 V1–V4 field pointers from a conforming document is refused, naming the removed pointer and its
Contract v3 element (9/9, 9/9, 7/7, 12/12 field removals refused). Score-report arithmetic and the oracle binding
are checked, not trusted. The Contract v3:1062 separation rule is enforced both for an oracle stored inside the
public suite and for a *trace* of one found there. The iteration-0 record — a "fault manifest" with none of the V1
fields — is refused `ORACLE_RECORD_INVALID`. G6 accepts a conforming oracle + bound score report and refuses a
non-conforming one.

**The AC-6 format *acceptance* is P2-AR-0045's and is not restated here.** The format's own status field reads
`PROPOSED — no hidden fault may be generated against this format until a fresh independent oracle-format reviewer
issues QUALIFICATION_ORACLE_FORMAT_ACCEPTED`. I generated no hidden fault.

## 11. What I could not establish

1. **`HEALTH_REMEDY_INCOMPLETE` on its own code path.** I demonstrated the property it protects — a committing
   operation that does not clear its block does not commit — through `task.close`, which is refused
   `HEALTH_HARD_BLOCK` because it is never a remedy. The `admit` + `confirm_remedy` obligation that raises
   `HEALTH_REMEDY_INCOMPLETE` is used by `update --apply`; exercising it needs a kernel-level condition plus a
   signed successor release, which I did not build. The rule is implemented (`scheduler::confirm_remedy`, called
   from `update.rs:469`); I did not see it fire.
2. **Three O2 families' detection** (context reproducibility, product traceability, audit reproducibility): I
   could not construct a failing case in a synthetic project and evidenced the measurement instead (§7).
3. **Five HEALTHY conditions flipped individually** (H2, H3, H6, H8, H13): evidenced through their owning checks'
   demonstrated detection rather than by flipping the condition (§6).
4. **Q1's "execution/report" stage from a task-closing report**, and an FCP linked to a governed release: I
   established the cluster step and `release_action: accumulate`, not an FCP or its release link (folded into
   `E-Q1-01`).
5. **O3 under a hostile single actor.** Independence rests on the recorded role and session of a sealed close
   report. Under OD-P2-01 (agent roles stay adapter-declared) one actor controlling two declared roles and
   sessions is outside what this mechanism can distinguish. That is the D-0007 trust-class question, in force as
   an owner decision, not an O3 defect — recorded as residual risk, not as a finding.
6. **Later-lifecycle notes (never Phase-2 blockers).** `TEST_POLICY.product_families` remains `overridable`
   (adoption/operations); token accounting would come from the adapter surface (operations); the oracle format's
   PROPOSED status resolves at AC-6 and hidden faults are Phase 4; production key custody for the release role
   that authenticates a certification claim is R2.

## 12. Outputs

| File | Contents |
|---|---|
| `00-VERIFICATION-REPORT.md` | this report |
| `capability-audit.yaml` | 16 capabilities, all **146** bullets, per-bullet status / implementation / automated / independent evidence / gap, tiers, freshness, qualification coverage, adoption obligation, residual risk |
| `findings.yaml` | 4 findings, each labelled RESIDUAL with its reason |
| `prior-findings-disposition.yaml` | all 38 iteration-0 findings in scope, disposed with my own evidence |
| `heldout/RUN-ALL` | re-runs all 8 probe files; **163 PASS, 4 FAIL** on this candidate, the 4 being exactly the 4 findings |
| `heldout/*.py` | the probes (`lib.py` harness, `srr.py` signer, t01…t08) |
| `evidence/RUN-ALL.out` | the recorded run |
| `evidence/E-O5-01-doctor-tier-gap.{sh,out}` | the blocking finding, reproduced standalone |
| `evidence/G0-G3-tier-duties.{sh,out}` | the G0 command census and the G3 currency duty |
| `evidence/AC-15-regression.out`, `evidence/pinned-inputs.out` | regression and pinned-input verification |
