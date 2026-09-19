# WS-5 (part) repair report — BC-P2-14, BC-P2-15 (run P2-AR-0018)

| Field | Value |
|---|---|
| Run | P2-AR-0018, role `capability-repair`, repair iteration 1, round 1 |
| Handoffs | P2-HO-0010 (common protocol), P2-HO-0015 (WS-5 part) |
| Base | `c6b60bc760a0bb42907f74210fd9e644a420851a` (product identical to `cap2-candidate-0`, `product_code_digest bd4d65d9…0547`) |
| Work commits | `a5e1788` (main repair), `3339ba9` (claims-table compatibility, close error precedence), `ddf722a` (close held to the claim's reserved scope) |
| Product digest after | `4bd2b58121f31e2af37b6ad3ec8f71c4a2faca9850864fdc6da917cb6160651d` (`release/orchestration/phase-2/tools/product_identity.py ddf722a`) |
| Claims | BC-P2-15 `REPAIRED_CLAIMED`; BC-P2-14 `REPAIRED_CLAIMED` (WS-5 side; three Accept probe lines wait on WS-2/WS-4 round-2 integration, §2.4) |
| Owner decisions | none raised |

This is a builder's claim. Everything below is regression evidence (Contract v3 O3); acceptance is decided by fresh
independent verifiers. "Before" means the pre-repair binary (sha256 `3271ce0e…1d`, byte-identical to the one the
audits of record used); "after" means the binary built from `ddf722a` (sha256 `aebc7078…70e`). Every audit probe
was run **unedited**, from disposable clones of the base and final commits, with the family runner
`synthesis/evidence/RERUN-family-probes.sh` (delta-r's probes looped directly to skip the runner's embedded
`cargo test`).

---

## 1. BC-P2-15 — claim atomicity and claim scope

**Requirement** (repair-delta BC-P2-15; Contract v3:388-392; findings A0-E4-01, A0-E4-03). A claim is granted to
exactly one session under concurrent attempts; the unit of isolation (session/worktree) is recorded; parallel claims
are refused or serialised when mutation scopes overlap.

### 1.1 What changed

| File | Function(s) | Change |
|---|---|---|
| `runtime/src/memory/claims.rs` | `ClaimsStore::claim_exclusive` | One `BEGIN IMMEDIATE` transaction reads every claim, then decides in order: another session's live claim → `TASK_CLAIMED`; the same session holding it live from another worktree → `CLAIM_WORKTREE_MISMATCH`; a new session beyond `max_parallel_agents` → `BUDGET_EXCEEDED`; a live claim of another session whose mutation scope may share a path → `CLAIM_SCOPE_CONFLICT`; otherwise it writes the claim and its isolation record and commits. SQLite's write lock serialises this across processes (busy timeout 20 s; `CLAIMS_BUSY` if exceeded). A renewal keeps its original `claimed_at`. |
| | `release_row`, `sweep_expired` | Read and delete in one transaction, deleting only the exact row decided on (a claim re-granted to another session is never deleted by the previous holder's release or by a sweep). |
| | schema | The `claims` table keeps its original five columns so anything that writes it positionally keeps working (epsilon-r O2's fault injection does). The isolation unit and scope live in `claim_isolation`, joined on the exact claim instance (task, session, claimed_at); a row written by anything else reads as an unknown worktree with an unrestricted scope. |
| | `path_for`, `shared_runtime_dir` | A project inside a **linked** git worktree uses the claims store of the same project in the main worktree (bare repository: inside the git common dir). Every worktree of one repository therefore claims against one table. Pure filesystem reads of `.git`/`commondir`. |
| `runtime/src/orchestration/claims.rs` | `isolation`, `worktree_id`, `scope_of_task`, `scope_of_claim`, `scopes_overlap`, `patterns_may_overlap`, `claim_with`, `release_row`, `get`, `live` | The isolation unit is the canonical project root plus the worktree's git dir, branch and HEAD. The scope is the task's `allowed_paths`; a task with none is **unrestricted** (`**`). `scopes_overlap` is a segment-wise glob-intersection test that is sound (never says "disjoint" when one path can match both) and conservative (undecidable cases count as overlap). |
| `runtime/src/orchestration/tasks.rs` | `claim` | The grant, budget and overlap are decided by the store transaction; the budget gate is raised after a refusal. The task status is re-read after the grant, and a claim that raced a concurrent close is withdrawn. |
| | `close` | A close now requires the claim: the closing session must hold it (`CLAIM_REQUIRED` otherwise), and close from the worktree it was made in (`CLAIM_WORKTREE_MISMATCH`). Another session's live claim is still `TASK_CLAIMED`, checked first as before; the evidence-payload checks keep their earlier precedence. An L3+ `--force` close proceeds and records every override it used in the report (`mutation_evidence.overrides`). |
| | `observe`, `closed_states` | So that disjoint parallel work in one worktree can actually close: a changed path outside the closing task's scope, inside another live claim's scope in the same worktree and changed since that claim's baseline, is attributed to that claim; a path whose content is exactly what a close inside this window accepted is attributed to that close (reports now record `mutation_evidence.observed_hashes`). No mutation escapes: each one is checked against some claim's or close's contract. |
| `runtime/src/status.rs` | `continue_work`, `partition_for_session` | `gov continue` offers only work the session can claim (not held by another session, not overlapping another session's live claim, not designated for another role) and says why the rest is deferred. |

### 1.2 Product checks that own it

The claim path itself runs on every `gov task claim` / `gov continue --claim`. Product unit tests (`cargo test --lib`):
`memory::claims::tests::concurrent_processes_claiming_one_task_grant_exactly_one` (the test binary re-executes itself
as five OS processes racing on one store, five trials), `concurrent_claims_of_one_task_grant_exactly_one` (six
connections × ten trials), `overlapping_scopes_of_other_sessions_are_refused_and_disjoint_ones_granted`,
`budget_is_decided_in_the_same_transaction`, `a_claim_is_bound_to_its_worktree_and_renewal_keeps_claimed_at`,
`release_and_sweep_only_touch_the_rows_they_decided_on`, `legacy_store_is_migrated`,
`linked_worktrees_share_the_main_worktree_store`; `orchestration::claims::tests::*` (four, including a soundness
check of the overlap test against the matcher). The G-tier mapping belongs to WS-1's evidence map (integration
point §5).

### 1.3 Probes re-run (unedited audit-of-record probes)

| Probe line | Before | After |
|---|---|---|
| gamma-r `E4-claims` E4.b2.race (Accept) | `trials=15 more-than-one-session-told-it-holds-the-claim=12 exactly-one=3` | `trials=15 … =0 exactly-one=15`; with `TRIALS=50`: `=0 exactly-one=50` |
| gamma-r `E4-claims` E4.b5 mutation overlap (Accept) | second session's claim of TASK-M2 (`src/**`) while TASK-M1 (`src/**`) is held: `exit=0 ok=true` | `exit=1 code=CLAIM_SCOPE_CONFLICT … TASK-M1 (session S-m1, scope ["src/**"])` |
| gamma-r `E4-claims` E4.b1 schema line | five columns | unchanged **by design** (§1.1 schema); the isolation unit and scope are returned by `gov claims list` and the claim result (supplementary WS5-A4) |
| gamma-r `E4-claims` E4.b2 sequential, E4.b3, E4.b4 recovery | as audited | unchanged, except E4.b4's TASK-D claim (§4) |

Supplementary probe (`evidence/probes/ws05_supplementary.py`, fresh projects, real OS processes) — after: all pass;
before (negative control): every non-control check fails.

| Check | What it attacks | Before | After |
|---|---|---|---|
| WS5-A1.race | 20 trials × 6 processes claiming one task | FAIL | PASS |
| WS5-A2.overlap-race | 20 trials × 4 processes claiming four tasks with the same scope at once | FAIL | PASS |
| WS5-A3.budget-race | `max_parallel_agents=2`, five processes, five disjoint tasks at once: exactly two granted | FAIL | PASS |
| WS5-A4.isolation-recorded | worktree, git dir, branch, HEAD and scope recorded on the claim | FAIL | PASS |
| WS5-A5 / A5b | from a linked `git worktree`: same task `TASK_CLAIMED`, overlap `CLAIM_SCOPE_CONFLICT`, disjoint granted, holder cannot re-claim or close from the other worktree | FAIL | PASS |
| WS5-A6.disjoint-close | two sessions, disjoint scopes, one worktree: both close declaring only their own change | FAIL | PASS |
| WS5-A7.continue-disjoint | second agent is offered the disjoint task; a third is told why the unrestricted task is deferred | FAIL | PASS |
| WS5-A8.close-requires-claim | unclaimed close refused; L3 `--force` proceeds and records the override | FAIL | PASS |
| WS5-A9.stale-holder-release | control: after expiry + takeover, the old holder's release cannot delete the new claim | PASS | PASS |

### 1.4 Limits and what was not done

* **Unrestricted scope is conservative.** A task without `allowed_paths` may mutate anything, so it overlaps every
  other claim and such tasks run one session at a time (Contract v3:392 "only where … mutation constraints permit").
  In one worktree, two unrestricted claims could never both close anyway: each would see the other's changes. This
  changes several audit fixtures built on unscoped tasks (§4).
* Claims are machine-local: one store per repository per machine. Clones on different machines do not share claims
  (unchanged design; E4.b3 still shows a fresh clone has none). The worktree identity is its canonical path.
* Session and role identity remain caller-declared (BC-P2-08, OD-P2-01).
* The claim does not consult the DAG (BC-P2-16, a later WS-5 round).
* `task release` still has no `guard_write` (A0-A5-01, BC-P2-08 — see §5).

---

## 2. BC-P2-14 — task-contract fields and path scope enforced

**Requirement** (repair-delta BC-P2-14; Contract v3:563-569, :614; findings A0-I2-01, A0-I2-02; handoff P2-HO-0015
adds the designated role). `blocks` orders work; required data and tools gate readiness; production merge is
refused where not permitted (experiments); a mutation outside a task's allowed paths is accepted only when a CIT
governing that specific change covers it; path scope is not permanently widened by earlier CITs; the designated
role is enforced.

### 2.1 What changed

| Field | File / function | Enforcement |
|---|---|---|
| `blocks` | `dag.rs::compute` | `A.blocks = [B]` is the ordering edge B→A, exactly like `B.dependencies ∋ A`: B is blocked while A is not DONE (reason names A), `replan` stores it BLOCKED, cycles and the longest chain include the edge, and a `blocks` entry naming no task is reported in `dangling_blocks`. |
| `required_data` | `dag.rs::InputResolver::data` | Resolves to a governed record (any type, typically `data`) in a current lifecycle status (not in `AUTHORITY_POLICY.retrieval_default_excludes_statuses`), or to a repository path/glob that exists inside the repository (a path escaping it never resolves). Otherwise the task is blocked with the reason. |
| `required_tools` | `dag.rs::InputResolver::tool` | Registered **and active** in the kernel/project tool registry, the MCP registry or as a capability plugin; otherwise blocked ("not registered" / "registered but proposed, not active"). |
| `required_skills` | `dag.rs::InputResolver::skill` | A kernel or project skill not in a retired status; otherwise blocked. (Contract v3:566 is "required skills/tools".) |
| production merge | `tasks.rs::production_merge_allowed`, `is_production_path`, `close` | A task whose contract forbids production merge — and every `experiment` task, whatever its record says — cannot close with observed mutations in the production tree: `PRODUCTION_MERGE_NOT_ALLOWED`, naming the paths, with the remediation (keep output under `spec/experiments/**` or a path the repository contract classifies as evidence; promote it through a CIT). The production tree is everything outside the contract's `spec`/`archive`/`governance` roots and outside the evidence, narrative, historical, generated, derived and runtime-data classes. Paths an in-window CIT wrote are exempt (a CIT is the governed promotion). |
| allowed/forbidden paths vs CITs | `tasks.rs::cit_window_paths`, `scope_violations`, `observe` | The permanent exemption (`cit_governed_paths`: every path any COMMITTED CIT ever touched) is gone. A CIT covers an out-of-scope path only if it was **committed after this task's claim baseline**; the baseline records which CITs were already committed, so the window is exact rather than clock-based (a CIT committed in the same second before the claim covers nothing — this was a real failure of a timestamp rule, caught by WS5-B8). |
| path scope cannot be reset | `tasks.rs::establish_baseline`, `carry_forward` | Re-claiming by the same session keeps the baseline; a release (or an expired/abandoned claim taken over) carries the window's attributable mutations into the next baseline, so release + re-claim or a takeover cannot launder an out-of-scope change. |
| reserved scope | `tasks.rs::reserved_scope`, `scope_violations` | The close is held to the scope the claim reserved: widening `allowed_paths` in the task record after the claim does not widen what the claim may close with (the reservation is what other sessions were checked against). |
| designated role | `tasks.rs::designated_role_refusal`, `claim`, `close`, `create`; `status.rs::partition_for_session` | A task's `role` binds claim and close (`ROLE_NOT_DESIGNATED`; an L3 `--force` close records the override); `task create` refuses a `role` that is not a kernel role (`UNKNOWN_ROLE`); `gov continue` does not offer a task designated for another role. |
| no-baseline fallback | `tasks.rs::uncommitted_paths` | A forced close with no claim baseline reads uncommitted paths from NUL-separated, path-only git output, not from porcelain status columns (the `project.rs` porcelain slice, A0-I2-03, is not used by close any more; `project.rs` itself is not mine and is unchanged). |

APIs added for round-2 consumers (read-only): `tasks::contract_enforcement` (resolution of required inputs, blocked-by,
designated role, merge permission, scope), `tasks::production_merge_findings`, `tasks::observe`,
`tasks::cit_window_paths`, `dag::required_inputs`, `dag::InputResolver`.

### 2.2 Product checks that own it

`dag::compute` runs in `gov task dag`, `gov status`, `gov continue`, `gov task replan` and the governance suite;
`tasks::close` enforces merge, scope, claim and role on every close; `tasks::claim` enforces the role. End-to-end
regression coverage is the supplementary probe (checks below); `tests/certification/greenfield.rs` now also asserts
the designated-role refusal. Mapping these to G-tiers is WS-1's evidence map (§5).

### 2.3 Probes re-run

| Probe line | Before | After |
|---|---|---|
| gamma-r `I1I2-tasks` I2.b3 (`blocks`) | `TASK-BLOCKED-BY-FULL runnable: True` | `… runnable: False` |
| gamma-r `I1I2-tasks` I2.b6 (tools/skills) | `TASK-FULL runnable despite TOOL-DOES-NOT-EXIST and SKL-DOES-NOT-EXIST: True` | `… : False` |
| gamma-r `I1I2-tasks` I2.b8.x (Accept) | `exit=0 ok=true`; REQ-0001 rewritten by a `src/**`-only task | refused, `exit=1 code=CLAIM_REQUIRED`. In this fixture TASK-FULL (`src/**`) is still claimed by another session, so TASK-LATER's claim (`src/**`) is refused and its close never reaches the scope rule. The scope rule itself: supplementary WS5-B8 (`MUTATION_SCOPE_VIOLATION` naming REQ-0001, CIT committed before the claim) with WS5-B8b as control (in-window CIT covers). |
| gamma-r `I1I2-tasks` I2.b9 (experiment → `src/lib.rs`) | `exit=0 ok=true` | refused, `CLAIM_REQUIRED` (same fixture effect); the merge rule: delta-r J2.merge.enforced and WS5-B6/B6b |
| gamma-r `I1I2-tasks` I2.b8.y (no-claim close) | `MUTATION_SCOPE_VIOLATION` on the truncated path `EADME.md` | `CLAIM_REQUIRED` |
| gamma-r `I1I2-tasks` I2.b4 required_data in packet; I2.b9 merge flag in packet | `False`; `False` | `False`; `False` — the context packet is WS-4's (`contract_enforcement` provided, §5) |
| delta-r `J1-J2` J2.merge.enforced (Accept) | FAIL | **PASS** — `PRODUCTION_MERGE_NOT_ALLOWED` naming `product/gateway_async.py` |
| delta-r `J1-J2` J2.merge.flag / .flag2 / .schema | PASS | PASS |
| delta-r `J1-J2` J2.merge.detected (Accept) | FAIL | FAIL — needs a governance-suite finding (WS-2's `verification/**`; `production_merge_findings` provided, §5) |
| gamma-r `E1-authority` E1.b4.b (designated role) | implementer claims and closes the independent-test-designer task: `exit=0`, `exit=0` | claim `ROLE_NOT_DESIGNATED`; close `CLAIM_REQUIRED` |
| gamma-r `F2F3-tools` (h) | `TASK-NEEDS-TOOL runnable: True` | `False` |

| Supplementary check | What it attacks | Before | After |
|---|---|---|---|
| WS5-B1 / B1b | `blocks`: blocked with reason, replan BLOCKED, mutual blocks → cycle; released when A is DONE (B1b is a control) | FAIL / PASS | PASS / PASS |
| WS5-B3 / B3b | missing data record, missing path, path escaping the repository, unregistered tool, proposed tool, missing skill → blocked; providing data unblocks; superseding blocks again | FAIL / FAIL | PASS / PASS |
| WS5-B6 / B6b / B6c | experiment (created asking for merge) into `src/` refused, into `spec/experiments/` accepted; any `production_merge_allowed: false` task held to it; a contract-classified evidence sandbox accepted (control) | FAIL / FAIL / PASS | PASS / PASS / PASS |
| WS5-B8 / B8b | CIT committed before the claim covers nothing; in-window CIT covers (control) | FAIL / PASS | PASS / PASS |
| WS5-B9 | out-of-scope change survives renewal, release + re-claim, takeover by another session | FAIL | PASS |
| WS5-B11 | task record widened after the claim | FAIL | PASS |
| WS5-B10 | designated role at claim, close (same session, other role), continue; unknown role at create | FAIL | PASS |

### 2.4 Accept lines that depend on other workstreams

* delta-r J2.merge.detected → WS-2 governance-suite finding (`tasks::production_merge_findings`).
* gamma-r I2.b4 / I2.b9 packet visibility → WS-4 context packet (`tasks::contract_enforcement`).
* Content binding of "that specific change" → WS-4 receipt (§5). Until then, a worker that modifies a path **again**
  after an in-window CIT touched it is covered by that CIT.

### 2.5 Limits and what was not done

* Forging OS-managed records (task records, close reports, CIT records) can still defeat scope checks. This is the
  pre-existing OS-managed exemption (BC-P2-09); the attribution rules trust those records exactly as the old CIT
  exemption did. WS-3's T2 primitive replaces the exemption in round 2.
* `blocks` and required inputs gate the DAG, `replan` and `continue`; a direct `gov task claim` does not consult the
  DAG yet (BC-P2-16, later WS-5 round).
* `required_tools` checks registration and active status, not binary availability or per-role approval;
  `required_data` checks existence and lifecycle, not version/hash constraints (BC-P2-17, WS-4).
* Root-level files (`README.md`, `Cargo.toml`) count as production for the merge rule.
* The readiness planner's generated tasks still carry no designated role, and cross-task independence (the same
  session implementing after test-designing) is not enforced here — both are BC-P2-34.

---

## 3. Regression

| Suite | Base | Final (`ddf722a`) |
|---|---|---|
| `cargo test --lib` | 42 passed | **55 passed, 0 failed** (+13 new unit tests) |
| `cargo test --test certification` | 79 passed | **79 passed, 0 failed** |

Changed builder test: `greenfield::greenfield_end_to_end`. The implementation task's contract designates
`backend-engineer`, and the test claimed and closed it as `orchestrator`. The designated role now binds claim and
close (BC-P2-14), so the test asserts that the orchestrator is refused (`ROLE_NOT_DESIGNATED`) and continues as
`backend-engineer`. No assertion was weakened.

R1 held-out suites were not run: no file in the common protocol's R1 list was touched. `tests/certification/section6.rs`
(the §6 derivation) passes inside the certification run. `cargo fmt` (rustfmt, edition 2021) is clean on every file
I touched.

---

## 4. Effect on the other audits of record (full re-run, before vs after)

All six families were re-run on the pre-repair and repaired binaries and compared with the synthesis tool
`COMPARE-family-outputs.py` (outputs in `evidence/probe-reruns/families/`). **No PASS/FAIL verdict marker (beta-r,
delta-r, zeta-r) changed from PASS to FAIL**; alpha-r's observation markers, and the gamma-r and epsilon-r outputs
(which carry no verdict markers), were adjudicated line by line below. Verdict markers that changed from FAIL to PASS: delta-r J2.merge.enforced; zeta-r W5-c2-no-claim-observed-paths-correct
(this one passes because an unclaimed close is now refused before observation, not because of a porcelain fix in
`project.rs`). Every other difference is one of the following. None is a regression of a capability that held, but a
re-verifier running these fixtures unedited will see the lines below change, so each one is named here.

| Family / line | Before → after | Why |
|---|---|---|
| gamma-r E4.b4 "force release of a live claim needs L3" | S-eta's claim of TASK-D `ok` → `CLAIM_SCOPE_CONFLICT` | TASK-C and TASK-D are unscoped and TASK-C is held live by S-zeta (§1.4). The L3 check still shows `AUTHORITY_DENIED` for L2 and `ok` for L3. |
| gamma-r I4.b5 two agents | S-w2 `TASK_CLAIMED` → `NO_RUNNABLE_WORK` (offered none, with `deferred` reasons) | All I4 tasks are unscoped, so the other runnable tasks overlap S-w1's claim. With disjoint scopes the second agent gets independent work (WS5-A7). The single-session line (gate presented, independent work offered) is unchanged. |
| gamma-r F2F3 (h) | `continue -> TASK-DOC` → `continue -> None` | TASK-DOC requires `TOOL-DOES-NOT-EXIST`, so it is no longer runnable (required-tool gating). |
| gamma-r E2-roles | +1 grep line | The probe greps the source for `ROLES.yaml`; the new `UNKNOWN_ROLE` message mentions it. |
| alpha-r A4 [B2] "parallel agents" | 3 claims granted (a fourth session, [B1]'s `S-spender`, already held a claim), then 3 × `BUDGET_EXCEEDED` with gates → all six `CLAIM_SCOPE_CONFLICT`; later gate ids shift | Every task in the fixture is unscoped and `S-spender`'s claim from [B1] is still live, so each further session is refused for overlap before the budget can be reached. The budget still decides first whenever parallelism is possible: WS5-A3 (five processes, five disjoint tasks, max 2: two granted, three `BUDGET_EXCEEDED`) and `repair::budget_parallel_agents_threshold_raises_gate` (certification). The alpha-r audit cites [B2] as evidence that the parallel-agent threshold is executable, so a re-verifier needs a scoped fixture for that line. |
| alpha-r A5 [E2] `task release` under FREEZE_WRITES | "governed files changed: [spec/tasks/TASK-0002.yaml]" → "[]" | Fixture effect only: the probe's second session's claim of TASK-0002 is now refused (overlapping unscoped tasks), so there is nothing to release. `task release` still does not call `guard_write` (A0-A5-01 is unchanged and belongs to BC-P2-08). |
| delta-r L3-gate-presentation-attacks | probe aborts at L3.b5.9 (the three checks after it were FAIL before) | Its worker session claims a `product/**` task while the probe's main session still holds another `product/**` claim → `CLAIM_SCOPE_CONFLICT`, which the probe does not expect. Re-verification needs that fixture to release the first claim; the probe is not mine to edit. |
| epsilon-r O2 audit-reproducibility race; O2 context race | flagged at attempt 0 / 4 → attempt 8 / 3 | Timing race probes; same outcome (non-reproducible run observed and flagged). |
| epsilon-r O5-tiers, O1, P1, U; zeta-r W03/W05; beta-r | extra fields (`overrides`, claim isolation fields, baseline `at`/`carried`), timings, status length ±1 | Additive output fields and noise; no marker changed. |
| epsilon-r O5-G0 `gate present` | varied between runs | Timing: re-presenting a gate in the same second as its first presentation writes identical bytes. Reproduced directly: in one run the pre-repair binary mutated and the repaired one did not. `gates.rs` is not mine and is unchanged. |
| epsilon-r O2 (intermediate build only) | — | My first build widened the `claims` table and broke O2's positional `INSERT INTO claims VALUES (5 values)` fault injection. The final layout keeps the five-column table (§1.1), and O2 runs as before. |
| beta-r C7-b5 (intermediate build only) | — | My first build checked the claim before the evidence payload, so an unclaimed close with failing tests returned `CLAIM_REQUIRED` instead of `EVIDENCE_REQUIRED`. The final code keeps the old precedence and C7-b5 passes. |

---

## 5. Integration points (for later rounds; not implemented here)

| # | Owner / file | Exact change | Why |
|---|---|---|---|
| IP-1 | WS-4 · `runtime/src/context/mod.rs` (deterministic authority block `det`) | add `"task_contract": crate::orchestration::tasks::contract_enforcement(p, &store, task),` | Puts required_data / required_tools / required_skills resolution, blocked-by, designated role and production-merge permission in the worker's context packet (gamma-r I2.b4, I2.b9). |
| IP-2 | WS-2 · `runtime/src/verification/mod.rs` (a task-contract family, or `graph_integrity`) | for `f in crate::orchestration::tasks::production_merge_findings(p, &store)`: push `finding("high", &fam, f["message"], …)`; optionally one finding per `dag.dangling_blocks` entry | The suite detects experimental output that reached the production tree outside the OS (delta-r J2.merge.detected). |
| IP-3 | WS-4 · CIT execution (`runtime/src/cit/mod.rs`) → tasks.rs in round 2 | CIT execution records, per touched path, the hash of what it wrote (receipt); `tasks::observe` / `scope_violations` then accept an out-of-scope observed path only when its current hash equals an in-window CIT's recorded hash | Binds "a CIT governing that specific change" to content, not only to the claim window (§2.4). This is the "receipt validation" integration the handoff assigns to round 2. |
| IP-4 | WS-3 · `tasks::release` (my file; WS-3 to supply) | `control::guard_write(p, "task release")?` as the first statement | A0-A5-01 / BC-P2-08 (freeze bypass). Not added here because it changes the §6 / R1 allow-list behaviour below floor. |
| IP-5 | WS-3 · round-2 T2 primitive into `tasks.rs` | replaces `OS_MANAGED_PREFIXES`; `closed_states`, `cit_window_paths` and the task record then read authenticated records | BC-P2-09: the attribution rules trust OS-managed records, as the old CIT exemption did. |
| IP-6 | WS-1 · `tests/governance/capability-evidence-map.yaml` | E4 claim collision / parallel work → `memory::claims::tests::*`, `orchestration::claims::tests::*`; I2 fields → `evidence/probes/ws05_supplementary.py` checks | AC-10 evidence owners (I own neither the map nor `tests/certification/main.rs`, so I added no new certification module). |
| IP-7 | WS-2 · `runtime/src/doctor.rs` D017 message | name `ClaimsStore::path_for(p)` instead of the literal `.governance-runtime/claims.db` | For a linked worktree the store is the main worktree's. |
| IP-8 | docs owner · `docs/COMMANDS.md`, `docs/ARCHITECTURE.md` | document `CLAIM_REQUIRED`, `CLAIM_SCOPE_CONFLICT`, `CLAIM_WORKTREE_MISMATCH`, `ROLE_NOT_DESIGNATED`, `PRODUCTION_MERGE_NOT_ALLOWED`, `CLAIMS_BUSY`, `UNKNOWN_ROLE` on `task create`, and the claim-window CIT rule | These docs describe close refusals and the old "committed CIT" exemption. |
| IP-9 | WS-5 round 3 (BC-P2-16) · `tasks::claim` | refuse a claim when `dag::compute` does not list the task as runnable | Makes `blocks` and required-input gating bind a direct claim as well. |

No `cli/src/main.rs` or `runtime/src/lib.rs` change was needed. I edited no file outside my ownership except the
builder test named in §3.

---

## 6. Owner-decision questions

None. One design choice to note, which I do not consider open under the sources: a task with no `allowed_paths`
has an unrestricted mutation scope and therefore conflicts with every concurrent claim (Contract v3:392). Exempting
unscoped tasks from the overlap refusal would reopen A0-E4-03 for them: the overlap would again surface only at close,
as mutual refusals.

---

## 7. Evidence index and reproduction

| Path (under `evidence/`) | Content |
|---|---|
| `probes/ws05_supplementary.py` | the supplementary probe (builder regression evidence) |
| `supplementary/ws05-supplementary.repaired.out` | 22/22 PASS on `ddf722a` |
| `supplementary/ws05-supplementary.pre-repair.out` | negative control on the pre-repair binary: 4 PASS (controls A9, B1b, B6c, B8b), 18 FAIL |
| `probe-reruns/gamma-r/*.{pre-repair,repaired}.out` | E4-claims, I1I2-tasks, I4-parallel, E1-authority, F2F3-tools; `E4-claims.TRIALS50.repaired.out` |
| `probe-reruns/delta-r/*.{pre-repair,repaired}.out` | J1-J2-research-experiments, L3-gate-presentation-attacks |
| `probe-reruns/families/rerun-{pre-repair,repaired}-<family>.log` | per-family run logs (clone HEAD and binary sha256 in each header) |
| `probe-reruns/families/compare-final-<family>.txt` | `COMPARE-family-outputs.py <pre-repair clone> <repaired clone> <family>`; `compare-final-gamma-r-E1E4.txt` diffs E1–E4 with the same normaliser (the tool's regeneration heuristic skipped them) |
| `regression/cargo-test-lib.out`, `regression/cargo-test-certification.out` | final regression |

Reproduce: build `target/release/gov` in a clone of `ddf722a`, then
`GOV_BIN=<gov> PROBE_SCRATCH=<dir> python3 release/capability-baseline/repair-1/ws05/evidence/probes/ws05_supplementary.py`;
the audit probes run unchanged per `synthesis/evidence/RERUN-family-probes.sh` (`CLONE=<clone> SCR=<dir> bash … <family>`).

## 8. Process disclosures

* Model: Claude Opus 5 (1M context), `claude-opus-5[1m]`. No sub-agents; the owner was not contacted; no transcripts,
  task-output stores or user auto-memory were read.
* I never edited probes under `release/capability-baseline/audit-0/`. They were run in disposable clones under my
  scratchpad (their runners write `.out` files next to themselves), and the committed audit directories in this
  worktree are unchanged.
* Behaviour changes I introduced and then corrected while testing, both caught by the family re-run: the widened
  `claims` table (epsilon-r O2) and the close refusal precedence (beta-r C7-b5). The same-second CIT window was caught
  by my own probe (WS5-B8).
