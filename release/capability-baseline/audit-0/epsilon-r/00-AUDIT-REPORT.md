# P2-AR-0008 — Iteration-0 capability baseline re-audit, family `epsilon`

| Field | Value |
|---|---|
| Run | P2-AR-0008 (fresh independent capability-family auditor; re-audit ordered by P2-HO-0008) |
| Family | `epsilon`: O1-O5, P1-P2, Q1-Q4, U (Framework Health SLOs), V1-V4 |
| Candidate | `cap2-candidate-0` = `57177a37ea296ece16b185874831462b6a76db18` |
| Audited worktree HEAD | `85e2ddfce4f0b1122bc8595dd869b98b316f5ea3` (candidate plus one orchestration-only commit that adds P2-HO-0008) |
| Binary | `target/release/gov` 4.1.5, sha256 `3271ce0e4e095561911e0d03d8641aa92fbeda39ef3c8a2ecb2a9f21cacbe81d`, built in this worktree |
| Verdict | `FAMILY_AUDIT_COMPLETE` |
| AC-5 (health scheduler) | **NOT MET** |
| AC-6 (oracle format) | **`QUALIFICATION_ORACLE_FORMAT_ABSENT`** |

## 1. Pinned-input verification (all verified, no STOP)

| Input | Expected | Observed |
|---|---|---|
| product_code_digest (HEAD and `cap2-candidate-0`) | `bd4d65d9…0547` | `bd4d65d9d5ffd6aedbd9435e2091a664dfc3e62f80614a76197cfaf87efd0547`; also equal for `srr1-r1-accepted` (c7d3fef) |
| Tag `cap2-candidate-0` → commit | 57177a3 | `57177a37ea296ece16b185874831462b6a76db18`; `git diff 57177a3 HEAD` = the P2-HO-0008 handoff file only |
| Contract v3 SHA-256 | `4c2df291…5ed3` | `4c2df29115c8d5389034b2e2d817772add80d61678807c23e0d520c937cb5ed3`; canonical import byte-identical (`cmp`) |
| Frozen gate contract SHA-256 | `ORCHESTRATOR_STATE.yaml frozen_gate_contract.sha256` | `d2f33e89d5459dd809e17271e46854cc886ed958ca63f89765e16d6a26a9f25e` = recorded value |
| Regression (AC-15) | zero failures | `cargo test --lib` 42 passed / 0 failed; `cargo test --test certification` 79 passed / 0 failed (`evidence/AC15-*.out`) |

## 2. Scope and method

**Universe.** I established the capability and bullet set from the owner source, not from the derived views: Contract v3 lines 749-866 (Gates O, P, Q) and 976-1062 (Gates U, V). That gives 16 capabilities and **146 checklist bullets**: O1 10, O2 17, O3 3, O4 2, O5 14, P1 13, P2 8, Q1 8, Q2 2, Q3 1, Q4 5, U 28 (15 SLOs and 13 HEALTHY conditions), V1 9, V2 7, V3 7, V4 12. The governing trace I read: framework §§62-68 and §§75-76 (plus Part XXIV §75A-H); release protocol §§7, 13-15 and 17; D-0004.

**Evidence standard.** Every bullet has its own executed demonstration: I built an input, ran `target/release/gov` (or the builder tests), and captured the observable result. I did not treat printed assertions, help text or the existence of a flag as evidence. The only exception is where the result is an *absence*. There I use behaviour as far as possible (a command is unrecognised; a record lacking every required field is accepted) and support it with a whole-tree search.

**Harness.** `evidence/lib.sh` creates a HEALTHY baseline project: the greenfield fixture copied to scratch, `gov init`, doctor HEALTHY, audit HEALTHY (`evidence/00-baseline-healthy-project.out`). Each probe then works on a **byte copy** of that baseline and changes exactly one thing, so every result is attributable to a single cause. Each project has its own simulated machine state (`XDG_STATE_HOME`). `evidence/RUN-ALL.sh` re-runs every probe against a fresh scratch area. The committed `.out` files come from that single final run (`evidence/RUN-ALL.out`: 15 probes, all exit 0). Nothing was written outside the evidence directory, and no product source was modified.

**Independence.** I authored none of the product, its tests or any earlier review. As instructed, I did not read `release/capability-baseline/audit-0/epsilon/`, `AGENT_RUNS/P2-AR-0005.*`, or any other family's evidence.

## 3. Per-capability summary

Counts: **PRESENT_AND_SUBSTANTIAL 1, PARTIAL 11, ABSENT 4, UNCLEAR 0, N/A_WITH_REASON 0** (16 capabilities). Bullet counts: 48 present, 51 partial, 47 absent.

| Cap | Status | Bullets P/Pa/A | Principal demonstrated gap | AC-3 impact |
|---|---|---|---|---|
| O1 Product test families | PARTIAL | 0/10/0 | Product-test results feed nothing. A failing suite leaves doctor and audit HEALTHY, `verify product` exits 0 on failure, and task close accepts a self-attested `passed` (A0-O1-01). | COULD_UNDERMINE |
| O2 Governance test families | PARTIAL | 15/2/0 | All 17 families detect an injected violation. Skill regression never executes its scenarios (A0-O2-01); deep audits are always reported reproducible (A0-O2-02). | COULD_UNDERMINE (skill regression) |
| O3 Independent test authorship | PARTIAL | 0/3/0 | Independence is self-attested. Builder tests pass as independent, and A5 "held-out" tests can be the planner's scaffold (A0-O3-01). | COULD_UNDERMINE |
| O4 Governance suite currency | PARTIAL | 0/2/0 | The currency key misses 6 of 14 input classes (A0-O4-01), the close gate is path-keyed (A0-O4-02), and DONE work is never re-staled (A0-O4-03). | COULD_UNDERMINE |
| O5 Governance Health Scheduler | PARTIAL | 1/9/4 | There is no scheduler: no impacted selection, parallelism, isolation, per-check cache or G6 tier. G0-G5 are incomplete, and health blocks nothing (A0-O5-01…13). | COULD_UNDERMINE |
| P1 Execution telemetry | PARTIAL | 6/6/1 | Tokens are absent. Model, cost, skill versions, files read and retries depend on schema-free caller input (A0-P1-01). | CANNOT_UNDERMINE |
| P2 Organisational questions | PARTIAL | 5/1/2 | Token effect and skill repair rate cannot be computed; cost is by class only (A0-P2-01). | CANNOT_UNDERMINE |
| Q1 Lesson lifecycle | PARTIAL | 2/4/2 | Validation and governed-version steps are absent (A0-Q1-01). Export "human approval" is a caller string (A0-Q1-02). | COULD_UNDERMINE (approval) |
| Q2 Decision vs lesson | PARTIAL | 1/1/0 | A lesson labelled AUTHORITATIVE, and FCPs, pass unflagged (A0-Q2-01). | CANNOT_UNDERMINE |
| Q3 Scope eligibility | PRESENT_AND_SUBSTANTIAL | 1/0/0 | — (A0-O1-03 concerns only the derived contract views) | — |
| Q4 Upstream Export Gate | PARTIAL | 3/2/0 | Raw `src/lib.rs` and vector rows leave the project inside "synthetic" fixtures (A0-Q4-01). | COULD_UNDERMINE |
| U Framework Health SLOs | PARTIAL | 14/11/3 | 9 of 15 SLOs lack an effective threshold or are absent, and suite freshness is keyed incompletely (A0-U-01). H11 has no check. No verdict is the §76 conjunction (A0-U-02). Gate U is missing from the compiled contract (A0-U-03). | COULD_UNDERMINE |
| V1 Fault manifest | ABSENT | 0/0/9 | No oracle format exists (A0-V1-01). | — |
| V2 Hidden path-map oracle | ABSENT | 0/0/7 | same | — |
| V3 Hidden memory oracle | ABSENT | 0/0/7 | same | — |
| V4 Quantitative scoring | ABSENT | 0/0/12 | same | — |

The per-bullet records are in `capability-audit.yaml`, and the full statements are in `findings.yaml`. For each capability, the YAML also records implementation lines, automated and independent evidence, freshness, tiers, evidence owners, qualification coverage, adoption obligation and residual risk.

## 4. AC-5 — Governance Health Scheduler determination: **NOT MET**

I exercised each required behaviour of the frozen contract §3 AC-5 against the product (evidence: `O5-scheduler-requirements.out`, `O5-tiers-G1-G6.out`, `O5-G0-guard-matrix.out`, `O5-G0-focus.out`, `O5-G5-update.out`, `O4-suite-currency.out`).

| AC-5 behaviour | Observed | Result |
|---|---|---|
| Impacted-test selection from a real mutation | A whitespace-only edit to one decision obsoletes the green record. The only remedy the product offers is `gov audit`, which runs all 20 families. Nothing selects checks from the changed path. | **absent** |
| Parallel execution of independent checks | A single sequential loop: one thread sampled for full, deep and doctor runs. The only child process is `git`. | **absent** |
| Safe isolation | `audit --deep` replaces the live `state.db` (new inode and hash) and writes into the live tree. The deep run changes the state its own second run measures. | **absent** |
| Cache reuse | No per-check cache: identical runs recompute everything. The only reuse is at whole-suite granularity, where task close and D021 accept a current green record. | **partial** |
| Cache invalidation | The inputs_hash covers kernel, overlay, governance tests, decisions and lock. Six Contract v3 input classes and the runtime are not keyed. A DAG cycle leaves the green record "current". | **partial** |
| Stale evidence | D021 marks an obsolete green DEGRADED, and close refuses on governance paths. DONE-task evidence never becomes stale (O4↔W6). | **partial** |
| RED/YELLOW/GREEN aggregation | HEALTHY/DEGRADED/UNHEALTHY by worst severity (exit 0/0/3) on doctor and on audit. The two surfaces are never aggregated with each other. | present (per surface) |
| Hard-block vs warning | Severity is explicit per check. An UNHEALTHY repository still allows task create, claim, close and CIT propose. A failed product suite exits 0. | **partial** |
| Health-result provenance | Audit records carry session, role, inputs_hash, result_hash and time, but no runtime identity or commit. Doctor results are not persisted. | **partial** |
| Remediation / task generation | Remediation strings are produced, but no task, gate or record is generated (0 → 0 tasks). | **partial (no generation)** |
| Tiers G0-G6 | G0 partial: 15 commands mutate under FREEZE_WRITES, and L0 can run `init --force`. G1 exists only on the CIT path. G2 misses readiness, references, test results and secrets. G3 is record-only. G4 is the CIT 3-check only. G5: update runs a 4-family subset and release runs none. G6 absent. | **incomplete** |
| Does a trivial mutation re-run the whole suite serially? | Nothing runs automatically on any mutation. When a re-check is needed, the only product mechanism is the whole suite, serially and twice. | **yes (fails the criterion)** |

Two cross-capability interactions required by AC-16 fall to this family. **U↔O5:** SLOs are observed only when someone runs doctor or audit by hand; no command records a health result automatically (S-U section). **O4↔W6:** an upstream change after a task is DONE leaves that task's evidence green (O4 §F). Both are **not satisfied**.

## 5. AC-6 — Qualification Oracle format determination: **`QUALIFICATION_ORACLE_FORMAT_ABSENT`**

No machine-checkable definition covering V1 (fault manifest), V2 (hidden path-map oracle), V3 (hidden memory oracle) or V4 (quantitative scoring) exists on this candidate:

- A whole-tree search for every V1-V4 field name, as an identifier, finds nothing outside the contract text, its derived views and the non-normative operator UI. The two "never indexed" hits are a hard-invariant name and a test function.
- `framework/schemas/` ships no oracle schema, and `release/orchestration/phase-2/` holds no oracle definition. `GATE-P2-ORACLE-FORMAT` is `NOT_SATISFIED`.
- A `fault-manifest` record missing every V1 field is accepted, and no qualify/oracle/score command exists (`V-oracle-format-and-contract-views.out` §A-§C).

Because no format exists, there is nothing to accept or reject. I generated no hidden fault. This leaves AC-6 unmet, V1-V4 ABSENT (AC-2), and V1-V4 with zero evidence owners (AC-10). I considered N/A for V and rejected it: the frozen contract places the *format* in Phase 2 (AC-6, §9.2); only generating the hidden faults belongs to Phase 4.

## 6. Most important findings

(Blocking status follows the frozen acceptance criteria. 36 findings in total: 17 HIGH, 13 MEDIUM, 3 LOW, 3 INFO; 27 blocking; none needs an owner decision.)

1. **A0-V1-01 (HIGH; AC-2, AC-6, AC-10):** the Qualification Oracle format is absent.
2. **A0-O5-01/02/03/04, 05-13 (AC-5):** there is no scheduler. The most material points:
   - **A0-O5-05 (G0).** An `independent-auditor` (L0) runs `gov init --force` while FREEZE_WRITES is active. This reinstalls the kernel, rewrites `framework.lock` and resets `PROJECT_POLICY.policy_overrides` to `{}`. The cause is that `init` evaluates authority on a project opened without the caller's `--role`; `adopt baseline` has no guard at all, and by code no adopt stage receives `--role`. The same role regenerates the held-out retrieval set, deleting a verifier-authored query.
   - **A0-O5-06 (G1/G2).** A task that writes an AWS key into `src/` and a schema-invalid requirement closes DONE.
   - **A0-O5-09 (G5).** An update was applied over a DAG cycle that the full suite reports UNHEALTHY, and `release build` mints a CERTIFIED manifest without running any suite.
3. **A0-O4-01 (HIGH; AC-10, AC-12, AC-5, AC-16):** the currency key omits spec/architecture, spec/requirements, spec/interfaces, source files, the index manifest, the tool registry and the runtime. **A0-O4-03 (AC-16):** DONE work is never re-staled.
4. **A0-O1-01 (HIGH; AC-3):** product-test failure is invisible to health and to task close.
5. **A0-O3-01 (HIGH; AC-12, AC-3):** test-authorship independence is self-attested.
6. **A0-Q4-01 and A0-Q1-02 (HIGH; AC-3):** the export gate fails *open*. A verbatim copy of product source and dumped vector rows leave as "synthetic" fixtures, contrary to release protocol §17 ("must fail closed"). An agent can approve its own export with `--approved-by`.
7. **A0-U-01 and A0-U-02 (HIGH; AC-3, AC-16):** most SLOs are unthresholded. Neither doctor nor audit implements "HEALTHY only when": doctor is HEALTHY with failing retrieval or a DAG cycle, audit is HEALTHY with legacy provider rules in the tree, and unresolved critical audit findings are never consulted.
8. **A0-U-03, A0-O5-14 and A0-O1-03 (AC-13):** Gate U is missing from the compiled contract and the evidence map, yet `gov contract verify` reports `CONTRACT_SOURCE_BOUND`. O5 and V1-V4 are compiled as ORIGINAL although the source marks them as refinements. The compiled form carries none of the 146 bullets or the per-capability fields, and every evidence-map row is `NOT_YET_MAPPED`.

These are all iteration-0 (`BASELINE`) findings. They form the blocker-class inventory for this family (frozen contract §8); the class identifiers are in the run report.

## 7. What held up (demonstrated present)

- All 17 governance families detect their injected violation. Context reproducibility's double-compile comparison caught a concurrent state change.
- Retrieval Recall@K is enforced at a threshold that can be raised but not lowered.
- Contradiction, legacy-authority, secret-isolation, index-freshness, rebuild and fresh-agent-budget checks each flip health when violated.
- Worker-return lessons become PROVISIONAL EVIDENCE candidates.
- Only FRAMEWORK lessons are exportable, and the overlay cannot widen that.
- Sanitisation, secret/sensitivity scans, destination and allowlist controls work.
- Decisions record the chosen option.
- Telemetry records session, role, duration, outcome, context-packet hash, handoffs, decisions and human answers.
- `telemetry summary` answers rework by role, gate concentration, per-model pass/cost and first-pass rate; `memory verify` names which retrieval route misses known knowledge.

## 8. Freshness, evidence owners, qualification coverage

- **Freshness (AC-10/AC-12).** All my evidence was produced on this candidate's code. I demonstrated invalidation for the governance-suite green record as a per-input-class matrix (`O4-suite-currency.out` §A): 8 classes invalidate it and 6 do not. P, Q and V carry no green-evidence state in the product.
- **Evidence owners (AC-10).** V1-V4 have **zero** owners. P1/P2 are observed only by the builder certification test (regression evidence). Owners for every other capability are listed per capability, with whether each owner actually runs.
- **Qualification coverage (AC-11).** Each capability has a Repo A and a Repo B challenge, a hidden-oracle fault class, and chaos/scale/soak and retrieval notes in `capability-audit.yaml`. V1-V4 cannot be challenged in synthetic repositories because they define the oracle itself; their alternative route is the fresh independent format review of AC-6.

## 9. What I could not establish, and limits

- **Runtime-binary invalidation** was not varied, because only one candidate binary exists. The code (`verification/mod.rs:54-71`) and the audit record's field list both show it is not keyed. I did not build a modified product to test it, since that would mean changing product source.
- **Adopt a11 (G5 at adoption)** rests on code reading plus the builder test `brownfield::brownfield_adoption_end_to_end` (regression evidence). I did not re-run a full A0-A11 adoption. A5/A7 independence I did run (`O3-independent-authorship.out`).
- `memory select` / `memory benchmark --record` were not exercised under the G0 matrix (they need benchmark candidates; `USAGE` in the baseline run).
- **Timing measurements** come from a tiny fixture: absolute durations (≈170-190 ms per full audit) say nothing about scale. The serial, twice-run, no-cache structure is shown by thread sampling and code, not by the timings.
- **Later-lifecycle notes** (not Phase-2 blockers): the CERTIFIED release status mintable without evidence (A0-O5-15) is an R2 certification matter.

## 10. Reproduce

```bash
cd <worktree>; ~/.cargo/bin/cargo build --release
bash release/capability-baseline/audit-0/epsilon-r/evidence/RUN-ALL.sh           # all probes, fresh scratch
~/.cargo/bin/cargo test --lib; ~/.cargo/bin/cargo test --test certification      # AC-15
```
Each probe can also be run on its own: `bash evidence/<probe>.sh`, or `python3 evidence/O5-G0-guard-matrix.py`.
