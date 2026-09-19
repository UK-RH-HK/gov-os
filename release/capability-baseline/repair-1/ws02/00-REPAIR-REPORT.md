# P2-AR-0015: WS-2 (part) repair report, iteration 1, round 1

| Field | Value |
|---|---|
| Run | P2-AR-0015 (`capability-repair`), handoff P2-HO-0012 under the common protocol P2-HO-0010 |
| Classes | BC-P2-03, BC-P2-06, BC-P2-42, BC-P2-43 |
| Base | `c6b60bc760a0bb42907f74210fd9e644a420851a` (product code identical to `cap2-candidate-0`: the base binary's SHA-256 `3271ce0e…` equals delta-r `F.impl.bins` `original_sha256`) |
| Work commits | `0683a20` (main repair), `81f2dec` (kernel-trust warm-up before concurrent checks), `f8a7396` (concurrent scenario execution), `463ff71` (authority for skill binding; `lib.rs` limited to the `pub mod` line) |
| Binary under test | `target/release/gov` SHA-256 `9c82578416b27a155dbd8abce86bb6a92ba9cd5fc2a43be53ffa45a0aa5fe7b4` |
| Claims | all four classes `REPAIRED_CLAIMED` for the WS-2 side, with host call sites recorded as integration points ([`claims.yaml`](claims.yaml)) |
| Owner decisions | none raised; OD-P2-01/OD-P2-02 were not touched |

These are builder claims. Everything here is regression evidence (Contract v3 O3). No class is claimed accepted.

## 0. What changed, in one view

| Area | Files (all owned by WS-2, or additive under the hot-spot rule) |
|---|---|
| Evidence currency (BC-P2-03) | `runtime/src/verification/currency.rs` (new), `runtime/src/verification/mod.rs`, `runtime/src/doctor.rs` (D021) |
| Health scheduler and tier contract (BC-P2-06) | `runtime/src/scheduler/{mod,catalogue,sandbox,store}.rs` (new module), `runtime/src/verification/mod.rs` (`run_family`, `audit_with`, `close_gate`), `runtime/src/doctor.rs` (concurrent groups, D031, persisted result) |
| Product-test evidence (BC-P2-43) | `runtime/src/verification/product.rs` (new), doctor D030, `product_test_health` family |
| Skill regression (BC-P2-42) | `runtime/src/skills.rs`, `framework/health/SKILL_SCENARIO_CHECKS.yaml` (new kernel-data file of the scheduler module) |
| Re-check families for J–N records (A0-J1-03) | `runtime/src/verification/families_ext.rs` (new): `human_gate_integrity`, `change_control_integrity`, `continuity_checkpoint_handoff`, `model_routing_integrity` |
| Policy and schema | `framework/policies/TEST_POLICY.yaml` (five families appended to `governance_families`; **no new keys**, so `ENFORCEMENT_MAP` coverage is unchanged), `framework/schemas/audit.schema.json` (provenance fields documented, `x-schema-version` 1.1.0) |
| Hot spots (additive) | `runtime/src/lib.rs`: `pub mod scheduler;` only. `cli/src/main.rs`: one `Health` variant, one `HealthCmd` enum, one `health_cmd` function, two match arms, all marked `WS-2 additive`. No existing line changed. |

`KNOWN_CLI` includes `health`. The `gov health` surface consists of `run`, `status`, `checks`, `history`, `show`, `guard`, `currency`, `product`, `skills`, and `close-check`.

## 1. BC-P2-03: green-evidence currency key and enforcement

**Requirement** (repair-delta §1; Contract v3:95-111, :788-789; AC-10, AC-3, AC-5). Green governance evidence must be keyed by every Contract v3:97-109 input class that is relevant to it. That includes authoritative spec beyond decisions, source files, the index manifest, tool and plugin registries, research, experiment, checkpoint and handoff records, adoption evidence, machine trust state and the runtime implementation identity. A change to any of them must make the evidence stale before work relies on it. Every governance-affecting task, identified by its class and by the governed records it touches, must be refused close on stale evidence.

**What changed**

- `verification::currency` is now the single digest point for evidence inputs:
  - **Path classes.** An ordered path partition (`PATH_CLASSES`, 27 classes) assigns every file that the suite reads (`paths::iter_repo_files`) to exactly one class. Anything unmatched is the 28th file class, `source`, so no file falls outside the key. With the two non-file classes below there are 30 classes in all. The classes are kernel policy, schema, migration, skills, tools and other; `framework_lock`; project policy; path map; sensitivity; model profile; tools/plugins; project skills; other overlay files; governance tests; index manifest; other generated files; decisions; requirements, features and scenarios; architecture and interfaces; tasks; research and experiments; checkpoints and handoffs; reports; adoption evidence; other spec; archive.
  - **Non-file classes.** Two classes cover inputs outside the tree:
    - `runtime_identity`: the SHA-256 of the executing binary plus the crate versions. The digest is re-used across processes only for the same file identity (dev, inode, size, mtime, ctime).
    - `machine_trust`: the trust anchor, the provisioning latch and the break-glass marking of the protected state root. It is read-only and creates nothing.
  - **Health outputs are excluded.** The health system's own outputs never enter the key: top-level `spec/audits/*.yaml` records of `type: audit` whose `scope` is `governance-suite` or `product-tests`, recognised by content. Their entries are also removed from the index manifest before it is digested. The manifest's volatile fields (`built_at`, `repo_commit`, `counts`, `manifest_hash`) are replaced by a `self_consistent` bit (`normalized_index_manifest`). A new result record therefore never stales itself, and adoption evidence in `spec/audits/<dir>/` stays an input.
  - **Stored beside the key.** `Snapshot::key()` is the suite key (`inputs_hash`). The per-class digests are stored beside it as `inputs`, so staleness names the classes that changed (`Currency::message`).
- **Doctor D021** evaluates `Currency` and reports, for example, `green record "AUD-0002" is obsolete (inputs changed: index_manifest, spec_decisions)`. Its remediation is `gov health run`.
- **Close gate API.** `currency::enforce_close(p, task, touched, force)` and `verification::close_gate(…)` apply the rule to governance-affecting tasks. A task is governance-affecting by class (`GOVERNANCE_AFFECTING_TASK_CLASSES`: governance, specification, decision-preparation, architecture, release, memory, migration) or because it touches any non-`source` input; the task's own record is ignored. Such a close is refused as `GOVERNANCE_SUITE_STALE` or `GOVERNANCE_SUITE_MISSING` with details. `force` records the degradation instead.
- **Currency-aware records.** `audit_with` writes a governance-suite record whose `green` requires a *complete* suite (every family executed or reused under an identical key) and a HEALTHY verdict over all families. Before this change, a one-family `gov audit --family X` could mint a green record.
- **Re-check families (A0-J1-03).** The re-check triggered by staleness now exercises the decision, change-control, continuity and routing records through four new families (`families_ext.rs`).

**Product check and tier.** The key is recorded on every suite result at G1–G6 and read by D021 at G1/doctor. `close_gate` runs at G2 once the host call site IP-WS02-01 lands. The existing `tasks::close` path gate already uses the broader key through `verification::inputs_hash`.

**Probes re-run** (before = base binary on an exported base tree; after = `9c825784…`; full outputs under `evidence/before|after/`):

| Probe (audit of record) | Before | After |
|---|---|---|
| alpha-r `FRESH-invalidation.py` | Four `[F]` classes left D021 current: spec/requirements, product source, index manifest, adoption evidence. `[F-A2]` provisioning and root rotation left it current. | All 13 `[F]` lines invalidate (class named). Both `[F-A2]` lines invalidate (`machine_trust`). |
| beta-r `FRESH-evidence-invalidation.py` | 2 PASS / 3 FAIL (source, spec, manifest) | 5 PASS / 0 FAIL |
| delta-r `FRESH-invalidation.py` | 6/13, failing RES, EXP, CKPT, HND, TASK, `F.impl.1`, `F.families.1` | 13/13 |
| epsilon-r `O4` §A | 8/14 classes invalidate | 14/14 |
| epsilon-r `O4` §B | DAG cycle UNHEALTHY while D021 reports "current" | D021 obsolete (`index_manifest, spec_tasks`); doctor UNHEALTHY via D031 |
| epsilon-r `O4` §D | A class=governance task changing spec/architecture closes on a stale green | Unchanged through `tasks.rs`. Refusal is available through `close_gate` (supplementary S-F.2/S-F.3) and is **pending IP-WS02-01**. |
| epsilon-r `O4` §F (currency part) | D021 current after an upstream REQ change | D021 obsolete. Re-staling of DONE-task evidence is BC-P2-04 (WS-4). |
| zeta-r `FR-freshness-invalidation.py` | 7/13 | 13/13 |
| AC16-X1 `X1-O4-green-stale-after-direct-spec-change` | FAIL | PASS |
| Runtime identity (delta `F.impl.1`, supplementary S-I.1) | A modified binary had the same key | The key changes, and the only changed class is `runtime_identity`. |

**Tests added.** In `verification::currency`: `every_contract_input_class_has_an_owner_class`, `health_outputs_are_recognised_by_content_not_by_name`, `governance_affecting_by_class_and_by_touched_inputs`, `snapshot_attributes_changes_to_classes_and_ignores_its_own_outputs`, `manifest_normalisation_drops_volatile_fields_only`.

**Limits and what was not done**

- **Floors and installed record excluded.** `floors/` and `installed/` are outside `machine_trust` because init and update advance them *after* their own conformance run (init.rs step 9); including them would stale every fresh install. If kernel trust starts consulting the installed record (BC-P2-35), see IP-WS02-14.
- **Exclusion by scope.** Exclusion is by record scope. A forged `governance-suite` record is excluded from the key, and `latest_green` would honour it. That is the T2-binding problem (BC-P2-09, IP-WS02-22).
- **Interim behaviour.** Until IP-WS02-01 lands, the unchanged `tasks.rs` gate (governance paths only) uses the broader key. After any close writes its report and checkpoint, the next close of a governance-path task is refused until `gov health run`, which re-executes only the impacted checks.

## 2. BC-P2-06: health scheduler mechanics and the tier contract

**Requirement** (repair-delta §1; Contract v3:791-808; AC-5). The requirement has seven parts:

- G0–G6 tiers that select checks from the dependency relation between changed inputs and checks;
- concurrent execution of independent checks;
- isolation of checks that mutate state;
- a cache keyed by the content, policy and framework hashes;
- hard-block versus warning declared per check, with the governed operations refused;
- every health result recorded with tier, checks, inputs, runtime identity, repository state, actor and time;
- a trivial mutation that does not re-run the whole suite serially.

**What changed** (`runtime/src/scheduler/`)

- **Catalogue** (`catalogue.rs`). The catalogue declares every check: 25 suite families and 31 doctor checks. Each declaration carries:
  - its **input classes**, with groups `@kernel/@overlay/@records/@files` plus implicit runtime, kernel policy, schema, lock and project-policy dependencies;
  - the **extras** it reads outside the tree (live index content digest excluding the retrieval log; `claims.db`; product-test evidence; skill and plugin observations; deep mode);
  - its **isolation** (`InProcess`, `Sandbox`, `OwnSandboxes`);
  - its **reproducibility** (`DoubleRun` or `SelfChecked`);
  - whether it is **cacheable**;
  - its **tiers**;
  - its **hard-block rules** (`min_severity`, `operations`, scope `global` or `covered-paths`). A check with no rule is a warning.

  The operation vocabulary is `task.create/claim/close`, `cit.propose/approve/execute`, `handoff.create`, `release.build`, `update.apply`, `adopt.migrate`. The remedies, checkpoints and gate answers are deliberately outside it. `gov health checks` prints the whole catalogue, captured in `evidence/supplementary/gov-health-checks.json`.
- **Selection and cache.** Each check's key is `hash(check, digests of exactly its declared classes and extras)`. A run executes the wanted checks whose key has no cache entry (or all of them under `Refresh`) and reuses every other check under an identical key (`store.rs`, `.governance-runtime/health/cache/`). A trivial mutation therefore re-executes only the checks whose declared inputs changed (S-A.5). Time- and session-dependent checks are `Cache::Never` and always run; they are cheap.
- **Concurrency.** A worker pool (2–4 threads, `gov-health-N`) runs the checks. `DoubleRun` checks execute twice concurrently, and differing result hashes become an `audit_reproducibility` finding. Refreshed checks are also compared with their cached result under an identical key. Doctor runs its four check groups on threads.
- **Isolation.** `context_reproducibility`, `memory_retrieval_regression` and `recovery_rebuild` run against a disposable copy of the tree and runtime stores (`sandbox.rs`, under `.governance-runtime/health/sandboxes/`, removed on drop). Paths in their results are relocated back to the live root. `skill_regression` creates one sandbox per scenario.
- **Provenance.** Every run, doctor included, writes a ledger result (`.governance-runtime/health/results/HR-*.json`: tier, tier duty, trigger, selection, cache mode, per-check status/key/threads/isolation/reproducibility/enforcement, inputs, `inputs_hash`, runtime, machine trust, repository commit/dirty/content key, actor, times, verdict, state, blocks). Governance-suite records carry the same fields. `gov health history|show` read them.
- **State and blocks.** `state.json` keeps the latest outcome per check. Active hard-blocks are derived from the declared rules. `health_state` is RED when a block is active, YELLOW when a warning check fails, and GREEN otherwise (`gov health status`). Doctor D031 reports suite-origin blocks, splitting current from stale ones.
- **Tier contract (API for hosts).**

  ```rust
  scheduler::guard(p, op, &paths) -> Result<Value>              // G0: HEALTH_HARD_BLOCK, typed, with blocks + remediation
  scheduler::tier_run(p, Tier::Gk, Trigger{event, subject, paths}) -> Result<Value>
  verification::close_gate(p, &task, &report, &touched, force) -> Result<Value>   // G0 + G2 re-check + O4 + O1 at close
  scheduler::run_suite(p, &RunOptions{tier, trigger, selection, cache, deep, surface, record, workers, ledger})
  ```

  - **G0 guard.** Before refusing, the guard re-evaluates only those blocking checks whose inputs have changed (S-C.5).
  - **Defaults.** G1–G4 run the tier's checks with the cache. G5 and G6 run every check fresh (`Refresh`) and compare against the cache. A tier run writes a governance-suite record only when it re-establishes currency (`RecordPolicy::WhenCompleteAndStale`).
  - **Tier membership** is declared per check (`gov health checks` → `tiers`).
- **Kernel-trust warm-up** (`81f2dec`). Running checks concurrently exposed a defect in `kernel::embedded_kernel_dir`, which stages the embedded baseline into `.staging-<pid>`. Several threads of one process materialising it at once interleave their writes and leave a corrupt cache marked complete: a later `gov init` fails with `UNKNOWN_ROLE` or `KERNEL_SOURCE_NOT_FOUND`. The scheduler and doctor now resolve kernel trust once on the calling thread before spawning workers. Negative control: supplementary S-J.1 fails 2/2 on `0683a20` (1 of 127 files) and passes on the final binary. The root cause is in WS-8's `kernel.rs` (IP-WS02-15).

**Probes re-run** (epsilon-r `O5-scheduler-requirements.sh`, unedited):

| Line | Before | After |
|---|---|---|
| S1 impacted selection | The only remedy was the whole suite, serially and twice | D021 names the changed classes (`index_manifest, spec_decisions`). `gov health run` re-executes only impacted checks and re-establishes currency (supplementary S-A.4–S-A.6). The probe does not call `gov health run`. |
| S2 parallelism | `max_threads` 1 for audit, deep and doctor | 9 (audit, including scenario threads), 4 (deep), 5 (doctor); child processes for scenario sandboxes |
| S3 isolation | Deep audit replaced the live `state.db` (new inode and hash) | Rebuilds run in a sandbox (`isolated_in_sandbox: true`), same inode. With `--no-persist` the live db is byte-identical (S-B.1). A persisted run changes only the index rows of the new evidence record (S-B.2). The probe runs the persisted form, so its hash still differs. |
| S4 cache | Identical second run recomputed everything (208/199 ms) | Second identical run served from the cache: 62 ms against 309 ms cold, 3 threads |
| S5 aggregation | Per-surface verdicts only | Plus `gov health status` RED/YELLOW/GREEN over doctor and the suite |
| S6 hard-block | Nothing refused; checks carried no block/warn field | Every check carries `enforcement` (`hard-block` or `warning` with operations). `gov health guard` refuses task.create/claim/close and cit.propose in the RED state (S-C.3) and releases after repair (S-C.5). A DAG cycle refuses task.claim but not task.create (S-C.6). The probe's own direct commands still succeed; that is **pending IP-WS02-02/03/05/08**. |
| S7 provenance | Audit record without runtime or commit; doctor not persisted | Audit record keys include `runtime` (binary sha256), `repository`, `actor`, `tier`, `trigger`, `checks`, `inputs`, `started_at`/`finished_at`, `health_result`. Doctor results are persisted (S-D.1) and `health.run` telemetry is emitted. |
| S8, U↔O5 | No generation; no automatic health | Unchanged. Generation is BC-P2-24 (WS-5). Automatic host triggers are the BC-P2-07 call sites (§6). |

**Tests added.** In `scheduler`: `tiers_parse_and_default_selection`, `blocks_are_derived_from_declared_rules_and_scoped`. In `scheduler::catalogue`: `every_policy_family_is_declared_and_every_dependency_is_a_known_class`, `checks_that_write_derived_state_are_isolated`, `hard_blocks_are_explicit`.

**Limits and what was not done**

- **Host wiring is outside WS-2.** Refusal at the operation sites needs the host call sites (§6), which are other workstreams' files.
- **State is last-writer-wins.** `state.json` is updated by atomic rename. Concurrent `gov` processes can drop each other's check entries until the next run.
- **Local state is not a trust boundary.** Cache, ledger and state are derived, machine-local state that a local agent can write. G5 and G6 lifecycle runs use `Refresh` and do not reuse the cache.
- **Sandbox cost.** Sandboxes copy the whole tracked tree plus the runtime stores, so the cost scales with repository size.
- **Coarse project-policy dependency.** Every check depends on `project_policy`, so any override re-runs every check (S4 third line).
- **Timing.** A cold suite run now takes about 0.3–0.4 s against 0.2 s (double runs and five scenario sandboxes). The certification suite takes 142–166 s against 128 s at baseline.

## 3. BC-P2-42: skill regression executed; versions bound to content

**Requirement** (repair-delta §1; Contract v3:399-402, :774). The skill-regression family must execute each skill's validation scenarios, or equivalent executable checks, and fail when an expectation is not met. A skill version must identify its content, for project and kernel skills.

**What changed** (`runtime/src/skills.rs`)

- **Content digest.** The digest is the canonical JSON of the skill (`content_sha256`). `list_skills` and `resolve` carry it, so an execution record captures the exact version used (framework §27).
- **Version binding.** Different content under an already-seen `id@version` is a HIGH finding against either of two records:
  - the tracked, OS-written `governance/generated/skill-bindings.json`, written by `gov health skills --record` only when every scenario passed or is declared, refused for a conflicting version (`SKILL_VERSION_CONTENT_CONFLICT`), and requiring authority `record_skill_binding` (conservative L3 default);
  - the machine-local first-seen observation ledger.
- **Executable scenarios.**
  - A scenario is executable when it carries a `check`: a list of `gov` steps with expectations (`ok`, `error_code`, `equals`, `one_of`, `nonempty` over bracket-aware dotted paths), `write` steps and `yaml_set` steps.
  - The `gov` binary itself executes each check against a disposable copy of the project in a fresh Git repository. Scenarios run concurrently, up to four, with nested execution prevented by `GOV_HEALTH_SANDBOX`.
  - A failed expectation is a MEDIUM finding.
  - A scenario with neither a check nor a declared mode cannot pass and is reported MEDIUM.
  - Scenarios declared `execution: agent|qualification` with a reason are listed as not executed (LOW) for the G6 harness.
- **Kernel scenarios.** Kernel skills stay unedited: `framework/skills/**` is not assigned to any workstream. Their executable checks live in `framework/health/SKILL_SCENARIO_CHECKS.yaml`, each bound to the exact scenario statement by `statement_sha256`, so a changed statement makes the check inapplicable. The installed kernel's copy is used when the kernel ships one; otherwise the copy compiled into the runtime is used (IP-WS02-16).
  - 5 executable checks pass on this product: TASK-CLOSE V1, BACKEND-IMPL V1, API-CONTRACT-REVIEW V1, MEMORY-RECONSTRUCTION V1, TOOL-INSTALL V1.
  - 4 are declared `agent` and 3 `qualification`.
  - **2 are declared `deferred` because their executable form is FALSE on this product.** These are SKL-IMPACT-ANALYSIS V1 (CIT-P on `governance/project` yields radius R2, not R5) and SKL-RESEARCH-BENCHMARK V1 (a research record without `method` passes schema validation). Their checks are written and can be run on request (`gov health skills --include-deferred`); `evidence/supplementary/gov-health-skills-include-deferred.json` shows both failing. They are routed to BC-P2-13 (WS-4) and BC-P2-47 (WS-10) as IP-WS02-20/21.

**Probes re-run**

| Probe | Before | After |
|---|---|---|
| epsilon-r `O2` §11 (no scenarios) | family_ok false | family_ok false (same findings) |
| epsilon-r `O2` §11b (false scenario) | family_ok **true**: never executed | family_ok **false**: reported as not executable, so it cannot pass |
| gamma-r `F1-skills.sh` F1.b3 (method changed, version not) | ok true, 0 findings | HIGH: `SKL-BARE@1.0.0: content changed without a version change since this machine first observed it` |
| supplementary S-G.1–S-G.5 | New surface | Executable false expectation FAILED and true one PASSED; binding recorded; content change under a bound version reported; re-binding refused |

**Tests added.** In `skills`: `content_digest_ignores_annotations_and_detects_method_changes`, `scenario_plans`, `lookup_and_expectations`, `every_kernel_scenario_has_a_bound_check_or_declared_mode` (reads `framework/skills` at test time).

**Limits.** Scenarios need the `gov` executable. Inside a cargo test harness process they are reported `not-run` (LOW) and never faked. Agent and qualification scenarios are not executed here (G6 / Phase 4). The machine observation ledger resets with `.governance-runtime`; the tracked binding does not.

## 4. BC-P2-43: product-test results governed

**Requirement** (repair-delta §1; Contract v3:751-761, :980, :1004). Per-family product-test results must be recorded as governed, freshness-bound evidence. A failing family changes the health state and blocks close of the work it covers. The test outcome at close is verified from recorded evidence, not self-attested. A failed suite must not be reported as a successful command.

**What changed** (`runtime/src/verification/product.rs`)

- **Families.** Families come from `PROJECT_POLICY.tests.families.<family>: {command, cwd?, covers?}` (the `tests` object is free-form in the project-policy schema). Without it, the Cargo convention applies: `unit` = `cargo test --lib/--bins`, `integration` = `cargo test --test '*'`, with covered paths `src/**`, `tests/**`, `Cargo.toml`, `Cargo.lock`, `build.rs`. A configured or detected single command is recorded as the unattributed family `all` with a note.
- **Evidence record.** `gov verify product` (and `gov health product --family`) runs each family and records an `audit` record with `scope: product-tests` and `state_class: EVIDENCE`. The record holds per-family status, exit, command, cwd, covers and a **freshness key**: the digest of the covered source-class files and the command, taken after the run. It also carries provenance (runtime, repository, actor). The index is refreshed, and the `product_test_health` state is refreshed for the guard. A failing family returns `PRODUCT_TESTS_FAILED` (non-zero exit) with the full per-family result in `details`.
- **Health.** `product_test_health` (family) and D030 (doctor) report a failing family HIGH (UNHEALTHY), and stale or missing evidence LOW. The declared hard-block refuses `task.close` for paths under the failing family's `covers`, and refuses `release.build` and `update.apply` globally. SLO fields: failing families, threshold 0.
- **Close API.** `product::enforce_close` works in two ways:
  - a failing family refuses the close of any task touching its covered paths;
  - a report claiming `passed` needs current, passing evidence for the covering families (or all families when none covers the task), and otherwise fails with `PRODUCT_TEST_EVIDENCE_REQUIRED`, `PRODUCT_TESTS_FAILED` or `PRODUCT_TEST_EVIDENCE_STALE`.

  It is wired through `close_gate` (IP-WS02-01).

**Probes re-run**

| Probe | Before | After |
|---|---|---|
| epsilon-r `O1` §F | One family-blind command and exit | `unit` and `integration` are run and recorded separately (S-E.1/S-E.2). The probe's projection prints only the first family's command. |
| epsilon-r `O1` §G | `verify product` exit 0 on failure; doctor and audit HEALTHY | `verify product` exit 1 `PRODUCT_TESTS_FAILED` (the probe's Python projection then raises, because the envelope is an error); doctor exit 3 UNHEALTHY (D030); audit exit 3 UNHEALTHY (`product_test_health`) |
| epsilon-r `O1` §H | Close accepted a self-attested `passed` | `tasks.rs` close still accepts it (**pending IP-WS02-01**). `gov health close-check` refuses with `PRODUCT_TESTS_FAILED` (S-E.6) and with `PRODUCT_TEST_EVIDENCE_STALE` after a covered change (S-E.8), and allows the close once a passing run is recorded (S-E.7). |
| epsilon-r `U` SLO-2 | Doctor and audit HEALTHY with a failing suite | Doctor exit 3 UNHEALTHY (D030); audit exit 3 UNHEALTHY |

**Limits.**

- **Test runs mutate the live tree.** Product test runs execute in the live tree, as before, because the product's own tests may need its build state. A run that writes a lock file (for example `Cargo.lock`) stales governance evidence, correctly, as a source change.
- **Only Cargo is split into families.** Ecosystems other than Cargo record `all` unless `tests.families` is declared.
- **Strict claim rule.** `enforce_close` refuses a `passed` claim where no product test can run (`PRODUCT_TEST_EVIDENCE_REQUIRED`). WS-5 decides how that interacts with task classes that have no product tests.

## 5. Regression and R1 preservation (AC-14 inputs)

| Suite | Result | Baseline |
|---|---|---|
| `cargo test --lib` | 56 passed, 0 failed | 42 (+14 new tests above; none changed or removed) |
| `cargo test --test certification` | 79 passed, 0 failed (142–166 s) | 79 (128 s) |
| R1 AR-0027 held-out (`4.1.6-r1`) | 12/0, 6/2, 4/1, 4/0: the same failing tests (b1, b2, d3) | Identical to the rerun recorded in `4.1.6-r1-4` |
| R1 AR-0029 held-out (`-r1-2`) | 6/0, 4/2 (b3, b6), 5/0, 5/0, 6/0, `ho_f` compile error | Identical |
| R1 AR-0031 held-out (`-r1-3`) | 5/3, 5/1, 6/2, 11/1: the same seven failing tests | Identical |
| R1 AR-0033 held-out (`-r1-4`) | 9/1, 7/0, 6/0, 8/0 | 10/0, 7/0, 6/0, 8/0 |

The only R1 difference is `hv_a_derivation::a1`, which pins the product source census at 84 `.rs` files. WS-2 adds 7 files (`scheduler/{mod,catalogue,sandbox,store}.rs` and `verification/{currency,families_ext,product}.rs`), giving 91. No behavioural R1 test changed outcome. WS-2 touched none of the files that the common protocol lists as R1-sensitive. The suites were run as a precaution because `hv_*` names `doctor.rs::run`, which was refactored and still calls `srr::present::presentation("doctor")` on every return path. `tests/certification/section6.rs` is green.

`rustfmt --check` is clean for every WS-2 file. In `cli/src/main.rs` only the four pre-existing base hunks remain, all outside the WS-2 block. `cargo clippy` reports no warning in WS-2 files.

## 6. Integration points

These are the host call sites and owner actions that other workstreams apply. File and line anchors refer to the base commit.

| ID | Owner | Where | Exact change | Why |
|---|---|---|---|---|
| IP-WS02-01 | WS-5 | `orchestration/tasks.rs::close`, the `// --- governance currency` block (lines 495-515) | Replace the block with `let gate = crate::verification::close_gate(p, &t.data, &report, &touched, force)?;` where `touched` = `files_changed` ∪ `observed`, both already computed above. Then extend `degraded` with `gate["degraded"]`. | G0 + G2 re-check before reliance; BC-P2-03 class and governed-record currency gate (O4 §D); BC-P2-43 close from evidence (O1 §H) |
| IP-WS02-02 | WS-5 | `tasks::create` (line 26) | `crate::scheduler::guard(p, crate::scheduler::catalogue::ops::TASK_CREATE, &[])?;` after the existing guards | O5 S6 |
| IP-WS02-03 | WS-5 | `tasks::claim` (line 128) and `status::continue_work` when `claim` (status.rs:114) | `crate::scheduler::guard(p, ops::TASK_CLAIM, &[])?;` | O5 S6 |
| IP-WS02-04 | WS-5 | `status::status` (status.rs:10) | Add `"health": crate::scheduler::status(p)?` (state, blocks, currency, product tests) | A fresh agent sees RED/YELLOW/GREEN |
| IP-WS02-05 | WS-4 | `cit::propose` (51), `cit::approve` (459), `cit::execute` (813) | `crate::scheduler::guard(p, ops::CIT_PROPOSE / CIT_APPROVE / CIT_EXECUTE, &targets)?;` at entry | O5 S6 |
| IP-WS02-06 | WS-4 | `cit::execute` after COMMITTED | `crate::scheduler::tier_run(p, Tier::G4, Trigger::cit_execute(id, &touched))` | BC-P2-07 G4 (X1-W12-G4) |
| IP-WS02-07 | WS-4 | `checkpoints::create` (16), `handoffs::create` (8) | `tier_run(p, Tier::G3, Trigger::new("checkpoint.create" / "handoff.create").with_subject(task))`; handoffs also `guard(p, ops::HANDOFF_CREATE, &[])?` | BC-P2-07 G3 |
| IP-WS02-08 | WS-3 | `orchestration::control::guard_write` (control.rs:58) | After the FREEZE/PAUSE checks, map the operation label to the `catalogue::ops` vocabulary and call `crate::scheduler::guard(p, op, &[])?` for governed-work operations | The single G0 site that makes hard-blocks refuse every governed operation |
| IP-WS02-09 | WS-3 | `AUTHORITY_POLICY.authority_levels_required`; G0 allow-list | Declare `record_skill_binding` (L3 is applied by default today). Decide the FREEZE_WRITES and authority class of the evidence-writing commands `gov audit`, `gov health run` and `gov verify product`; they write governed evidence records, as `gov audit` did before. | BC-P2-08 guard coverage |
| IP-WS02-10 | error.rs (unassigned) | `GovError::exit_code` | Optionally map `HEALTH_HARD_BLOCK` to exit 4 (blocked class); it is 1 today | Exit-code class consistency (API-0002) |
| IP-WS02-11 | WS-3 | `TEST_POLICY` + `ENFORCEMENT_MAP` | If policy-level configuration is wanted, lift `currency::GOVERNANCE_AFFECTING_TASK_CLASSES` into `TEST_POLICY.governance_affecting_task_classes` with an ENFORCEMENT_MAP entry. WS-2 added no new key, to keep coverage intact. | Configurability |
| IP-WS02-12 | WS-8 | `update::apply_update_opts` (the four-family `verification::audit` at ~line 330) | Replace it with `crate::scheduler::tier_run(p, Tier::G5, Trigger::new("update.apply").with_subject(version))` and refuse on UNHEALTHY or RED; `guard(p, ops::UPDATE_APPLY, &[])?` at entry | O5-G5-update |
| IP-WS02-13 | WS-8 | `release::build` (release.rs:69) | `guard(p, ops::RELEASE_BUILD, &[])?` + G5 `tier_run` before minting | A0-O5-09/15 |
| IP-WS02-14 | WS-8 | `init::init` (lines 312-331); `currency::machine_trust_state` | Run the conformance suite after `srr::record_installed` (or add `tier_run(G5)` after it). Only then may `installed/<product>.json` join the `machine_trust` class (tell WS-2). | Needed if kernel trust consults the installed record (BC-P2-35) |
| IP-WS02-15 | WS-8 | `kernel::embedded_kernel_dir` (kernel.rs:~40-75) | Stage into a per-call unique directory (for example `.staging-<pid>-<uuid>`), and check an existing directory against the embedded listing before re-using it | Root cause of the corruption found in §2; WS-2 only serialises its own first use. `~/.cache/gov/kernels/4.1.5-2120db97b369` (an intermediate WS-2 build) still holds 61 of 127 files and is safe to delete. |
| IP-WS02-16 | release/kernel owner | `framework/KERNEL.yaml` `payload_dirs` | Add `health` | Installs `health/SKILL_SCENARIO_CHECKS.yaml` with the kernel skills it verifies. The runtime's compiled copy is used until then; statement-hash binding prevents misapplication. |
| IP-WS02-17 | WS-2 (later round) ← WS-8, WS-7 | `doctor.rs` | Add the posture and authenticity check (BC-P2-36) and the plugin checks against the APIs WS-8 and WS-7 expose; declare them in `scheduler::catalogue` | Doctor is WS-2's file (§3.1) |
| IP-WS02-18 | WS-9 | `adopt::a11_audit` (adopt.rs:1298) and `adopt::a6_migrate` (572) | `tier_run(p, Tier::G5, Trigger::new("adopt.a11"))` in place of `verification::audit(deep)`; `guard(p, ops::ADOPT_MIGRATE, &[])?` in A6 | BC-P2-07 G5 at adopt |
| IP-WS02-19 | WS-1 | `tests/governance/capability-evidence-map.yaml` | Evidence owners: O4 → `verification::currency` (D021 at G1, `close_gate` at G2); O5 → `scheduler` (G0–G6, `gov health checks`); O1 and U product-test health → `product_test_health` + D030; O2 skill regression and F1 → `skill_regression` (G5); L/K/N/M re-check → the four `families_ext` families (G3–G5) | AC-10 |
| IP-WS02-20 | WS-4 → WS-2 | `framework/health/SKILL_SCENARIO_CHECKS.yaml` | When BC-P2-13 lands, set SKL-IMPACT-ANALYSIS V1 to `mode: executable`; the check is already written and observed FALSE today (R2) | Kernel skill scenario truth |
| IP-WS02-21 | WS-10 → WS-2 | same file | When BC-P2-47 lands, set SKL-RESEARCH-BENCHMARK V1 to `mode: executable`; observed FALSE today | Same |
| IP-WS02-22 | WS-3 (BC-P2-09) | `currency::latest_green`, `product::latest_records` | Honour only records bound to an OS operation (the T2 binding primitive); a forged green or product-test record is currently read like any record | T2 binding |

## 7. Owner-decision questions

None. Every choice made here (the class partition, the governance-affecting classes, the block rules, the deferred kernel scenarios with their reasons) is determined by the cited sources or recorded above as an integration point for its owner.

## 8. Evidence index (`evidence/`)

| Path | Contents |
|---|---|
| `RERUN-probes.sh` | Runs the named audit-of-record probes unedited against a tree (a private kernel cache is used; see its header) |
| `before/` | Base binary (`3271ce0e…`) on a `git archive` of the base commit: `O4`, `O5`, `O1`, `O2`, `U`, `alpha-r`, `beta-r`, `delta-r`, `zeta-r`, `gamma-r F1`, `AC16-X1` |
| `after/` | The same probes on the final binary (`BINARY.txt`) |
| `supplementary/WS02-supplementary.py`, `.out` | 42 builder checks S-A…S-J, all PASS on the final binary |
| `supplementary/WS02-supplementary-negative-control-0683a20-run{1,2}.out` | S-J.1 fails on the pre-fix commit |
| `supplementary/gov-health-checks.json` | The tier contract and check catalogue |
| `supplementary/gov-health-skills-include-deferred.json` | Kernel scenarios; deferred checks shown FALSE |
| `regression/` | `cargo test --lib`, `--test certification`, and the four R1 held-out suites (`r1-*`) with `COMMIT.txt` |
