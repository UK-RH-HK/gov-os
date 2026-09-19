# P2-AR-0027 — Repair iteration 1, round 2, WS-6: knowledge fabric and retrieval

| Field | Value |
|---|---|
| Run | P2-AR-0027 (`capability-repair`), handoffs P2-HO-0025 + P2-HO-0020 + P2-HO-0010 |
| Agent model | Claude Opus 5 (1M context), `claude-opus-5[1m]` |
| Branch / worktree | `phase2/repair-1-r2-ws06` |
| Base | `843d79c33e8a8db8b223611abc23d317edbc82a1` (integrated round-1 tree, `product_code_digest b1ab1c8c…fbb1`) |
| Product work commits | `e67ea4d`, `0a93907` (`product_code_digest 99704522e6a85cd077521e34eb35a722a49c50afd428d34a9ce1fa70420ea262` at `0a93907`; the evidence commit changes no product file) |
| Classes | BC-P2-28 **REPAIRED_CLAIMED** · BC-P2-30 **REPAIRED_CLAIMED** · BC-P2-31 **PARTIAL** (classification side done; the writer moves are other owners' integration points, as the handoff routes them) |
| Integration points routed here | WS-3 IP-8 **done** · WS-4 IP-12 **done** · WS-4 IP-13 **done** |
| Owner decisions | none required |

This is a builder's claim. Everything below is regression evidence (Contract v3 O3); acceptance is decided by fresh
independent verifiers. Nothing here claims a class is accepted, verified or closed.

## 0. What changed

| File (owner) | Change |
|---|---|
| `runtime/src/memory/integrity.rs` (new, WS-6) | BC-P2-28 graph-integrity check: orphan, dangling, stale, reversed, ill-typed and supersession-cycle findings over the canonical record edges (`Record::edges`, `graph::canonical_of`) plus the index's dangling edges; per-relation-type endpoint signatures |
| `runtime/src/memory/profile.rs` (new, WS-6) | BC-P2-30: component identity (adapter / model artefact / inference runtime) of the executed embedder and reranker; query-time binding; retrieval profile and its governance state; the governed `select` (evidence, radius gate, human approval through `gates::human_approval_for`, full re-index, recorded regression, rollback) |
| `runtime/src/memory/embedder.rs` (WS-6) | Revision binding (`EMBEDDER_REVISION_MISMATCH`, `RERANKER_REVISION_MISMATCH`); `for_query` checks component identity; `Reranker::resolve_id`; `for_query_with` |
| `runtime/src/memory/indexer.rs` (WS-6) | Pins carry the component identity; runtime drift escalates to a full build; meta `embedder_identity`/`reranker_identity`/`graph_integrity`/`retrieval_profile`; report fields `graph_integrity`, `retrieval_profile`, `os_state`; manifest `components`/`retrieval_profile` (outside the hashed core); `expected_pins_with` |
| `runtime/src/memory/manifest.rs` (WS-6) | Freshness compares the identity-carrying pins (one plugin-set classification per call) |
| `runtime/src/memory/benchmark.rs` (WS-6) | Candidates run at the plugin's executed revision; every row carries the measured profile identity; the research record is T2-sealed and carries `version`, `content_hash` and a `benchmark` block (IP-13); `select` delegates to `profile::select` |
| `runtime/src/retrieval/mod.rs` (WS-6) | Reranker identity checked at query; `+rerank:none` and executed revision for benchmark rerankers; one plugin set per held-out run (`RetrieveOptions.plugins`); revision codes are pin errors, not tool failures |
| `runtime/src/paths.rs` (WS-6) | BC-P2-31: `OS_STORES` (kernel classification of non-rebuildable OS stores) applied after the overlay's rules in `RepositoryContract::decide`; class `operational`; `.governance-state/` location API (`store_path`, `ensure_state_dir`, `relocate_legacy`); `misplaced_os_state`; `derived_deletion_set` |
| `runtime/src/memory/mod.rs` (WS-6) | module registration |
| `framework/schemas/index-manifest.schema.json` (WS-6) | documents `embedder` identity fields, `reranker`, `components`, `retrieval_profile` (1.1.0) |
| `cli/src/main.rs` (additive) | `memory select --gate`; new read-only `memory integrity`, `memory profile` |
| `runtime/src/orchestration/control.rs` (additive) | `COMMAND_GUARDS`: `memory integrity`, `memory profile` → `read` / Read |
| `tests/certification/ws06.rs` (new), `main.rs` (one `mod` line) | four regression tests (§6) |
| `tests/certification/repair.rs` | the select step of `benchmark_records_evidence_and_selection_pins_through_decision` follows the governed flow (§6) |

15 files, +3 237 / −126. No edit to `records.rs`, `graph/**`, any SRR/kernel/lock/update/release/recovery file,
`tools.rs`/`capabilities/**`, another workstream's policy or schema, the contract source, `release/verification/**`,
`release/root-of-trust/**`, `release/releases/**`, phase-1 records, `audit-0/**` or another `repair-1/` directory. No new
crate dependency; the core spawns no language runtime of its own (identity hashing reads files; `tests/certification/arch.rs` green).

## 1. BC-P2-28 — Graph integrity detection — REPAIRED_CLAIMED

**Requirement** (repair-delta §1; Contract v3 C2:231 "Graph integrity checks detect orphan/stale/reversed/invalid
relationships"; :356 "graph edges stale"; A0-C2-01): integrity checks raise (not merely count) orphan relationships,
relationships to superseded/retired/historical targets, and reversed or ill-typed relationships per relation type.

**What changed** — `memory::integrity::check(p, &store, db)` returns every finding with its kind, severity, the edge, the
declaring record and a remediation:

- `orphan` (low): a current traceability record (feature, requirement, scenario, test obligation, interface,
  architecture, decision, task) no relationship reaches or leaves. An architecture record every task consumes implicitly
  (`graph::IMPLICIT_CONSUMERS`) is not an orphan while a current task exists.
- `dangling` (medium): the index's dangling edges (`graph::dangling_edges`, code included), or record targets that
  do not exist when no index is available.
- `stale` (medium): a record that still asserts its relationships (current; not evidence; not closed work such as a
  DONE task, a committed CIT, an answered gate, a checkpoint or handoff) whose **in-force** relationship (DEPENDS_ON,
  IMPLEMENTS, REALISES, GOVERNED_BY, CONSTRAINS, VALIDATED_BY, TESTS, USES, CONSUMES, BLOCKS, OWNS, CALLS, IMPORTS)
  points at a target that is superseded (status or successor), retired, deprecated, rejected, legacy, historical,
  archived, or a file the path map classifies `historical`. Provenance relations (DERIVED_FROM, LEARNED_FROM,
  FAILED_BECAUSE, GENERATED_FROM, PRODUCES, AFFECTS, SUPERSEDES) record history and are never stale.
- `reversed` / `ill_typed` (medium): per relation type, `SIGNATURES` states which kinds (project, feature,
  requirement, design, verification, work, code, evidence) may be its source and destination. An edge that fits only
  the other way round is `reversed` (a requirement that IMPLEMENTS an architecture record; a requirement that TESTS a
  test obligation); one that fits in neither direction is `ill_typed` (an architecture record that CALLS a requirement),
  as is a relation type outside the framework's twenty. Endpoints of a kind the kernel does not know are not judged.
- `supersession_cycle` (high): records superseding each other.

Edges are read canonically through `Record::edges()` (`graph::canonical_of`), so target-side fields (`consumers`,
`producers`, `task`, `human_gate`, `superseded_by`) are judged in the direction of their meaning (**WS-4 IP-12**).

**Product check that owns it and its tier** — every index build (`indexer::rebuild`: G1-equivalent, including the
refresh inside task close and CIT-E) runs it, records a summary in runtime meta `graph_integrity` and returns it in the
report (`graph_integrity.ok/counts/findings`); `gov memory integrity` runs it on demand. The full-audit
`graph_integrity` family and doctor D015 are WS-2's files and still read only `graph::dangling_edges`/`orphan_nodes`:
wiring them to this check is **IP-R2-1** (round 3); CIT-E's `graph_integrity` verification is **IP-R2-2** (WS-4).

**Dogfooding** — run over the canonical repository's own 42 `spec/` records (273 edges) in a scratch project: no
stale, reversed or ill-typed finding; 16 dangling edges to skills and an owner directive that are not records of that
copy (what D015 already counts).

**Probes re-run** (`evidence/before`, `evidence/after`, `evidence/probes/`)

| Probe | Base `843d79c` | This branch | Lines |
|---|---|---|---|
| beta-r `C2-relationship-graph` (unedited) | 7 P / 3 F | 7 P / 3 F | `C2-b2-orphan-flagged`, `-stale-superseded-target`, `-reversed-direction` read only `gov audit` / doctor D015 → pending IP-R2-1 |
| derived `C2-relationship-graph.integrity.P2-AR-0027` | — | 14 P / 3 F | the same 3 unedited lines FAIL; all 7 added `*-product` lines (orphan, stale, dangling, both reversed, cycle, unknown type, dangling target) PASS |

**Tests added** — lib `memory::integrity::tests::signatures_judge_direction_and_type`; certification
`ws06::graph_integrity_raises_orphan_stale_reversed_ill_typed_and_cycles`; supplementary `SUPP-ws06-r2` R6.

## 2. BC-P2-30 — Retrieval-profile component identity and change governance — REPAIRED_CLAIMED

**Requirement** (repair-delta §1; framework §14.2-14.3; Contract v3 D1 "Index manifest records compatible component
identity", D4:329-340, D5:342-348; frozen gate contract §9.1; A0-D4-01, A0-D5-01, A0-D5-02): the embedding model
artefact and inference runtime are separately identified and content-bound in the index manifest; pins bind the
revision actually executed and fail closed on mismatch; a profile change needs benchmark evidence for the chosen
candidate, a recorded held-out regression after re-indexing, and the change-control gate for its radius; ungoverned pin
edits are detected; a re-pin does not withhold deterministic inputs.

**What changed**

1. *Component identity* (`profile::embedder_identity` / `reranker_identity`). **Adapter**: builtin implementation, or
   plugin id, executed descriptor revision, a hash of the execution-relevant descriptor fields (command, cwd, version,
   languages, timeout, permissions — not provenance notes) and the SHA-256 of every local implementation file.
   **Model artefact**: for the builtin, algorithm revision and parameters; for a plugin, the SHA-256 of every file
   shipped beside its implementation (its own directory, or its module package for `python -m`), other declared
   plugins' implementations excluded; an implementation at the repository root or outside the repository binds only the
   implementation file (noted in the identity). **Inference runtime**: the interpreter a local script names on its `#!`
   line, a local binary itself, or the program resolved on `PATH`, content-hashed. Adapter and model are repository
   content: their digest is part of the pinned `embedder` value in the manifest's **hashed core** (a clone at another
   path reproduces the manifest hash). The runtime's bytes are machine-specific: bound in runtime meta and recorded in
   the manifest's `components` block outside the core.
2. *Binding, fail closed.* Query time: `for_query` requires, component by component, the identity the live index
   recorded (`EMBEDDER_MISMATCH` naming the changed component — e.g. "model artefact … changed: tools/probe-plugins/
   weights.json"); the reranker likewise (`RERANKER_MISMATCH`). Build time: an incremental build escalates to a full
   re-embed on any identity or runtime change. Freshness: the pins carry the identity, so a changed adapter or model
   artefact is `pin_mismatch` (index not fresh; task close refuses). A descriptor revision that is not the pinned one
   never executes (`EMBEDDER_REVISION_MISMATCH`; for the reranker when a revision is pinned). Benchmark candidates run at
   the plugin's executed revision (no hard-coded `"1"`); the manifest records the reranker's **executed** revision
   (`version`) beside the pinned one.
3. *The governed change* (`gov memory select`, `profile::select`):
   - **Evidence**: `--research` must be a T2-verified benchmark research record (`benchmark.format retrieval-benchmark/1`)
     measured on the held-out set as it stands, containing a usable row whose **profile identity** equals the
     candidate's current identity (`PROFILE_EVIDENCE_REQUIRED` / `_UNBOUND` / `_STALE`).
   - **Gate for its radius**: the pins live in `governance/project/**`, so the radius is
     `CHANGE_POLICY.radius_rules.governance_paths_radius` (R5); above `auto_approve_max_radius` a system gate
     (`trigger: retrieval_profile_change`, full OS-computed decision package, `subject.sha256` over from/to identities,
     the evidence id and hash and the held-out set) is raised and nothing is applied (`applied: false`, re-reported on
     repeat calls). Above `HUMAN_GATE_POLICY.agent_resolvable_when.max_radius` only `gates::human_approval_for(p, gate,
     subject)` authorises it — an owner-signed answer bound to that exact change. A declined, stale or already-applied
     gate authorises nothing (`GATE_DECLINED`, `APPROVAL_STALE`, `GATE_ALREADY_APPLIED`).
   - **Apply**: baseline regression on the live index, pin (embedder id/revision/dimensions, reranker provider and
     executed revision), full re-index, a check that the built profile is the approved one (`PROFILE_IDENTITY_CHANGED`
     otherwise), then the held-out regression under the new pins, recorded as a T2-sealed evidence audit record
     (`scope: retrieval-profile-regression`, never a governance-suite record, so it cannot become green suite evidence).
     Accepted when the policy thresholds are met, or the result is not worse than the previous profile on any held-out
     measure; an unmeasured or regressed result (or a re-index/regression error) **rolls back** (overlay bytes restored,
     full re-index) and writes a `regression` failure record (`PROFILE_REGRESSION_FAILED` / `_UNMEASURED`).
   - **Decision**: T2-sealed; options A (adopt) / B (keep), `chosen_option: A`, measured `alternatives`, a factual
     rationale naming the benchmark, the regression audit and the approval; `derived_from: [gate, research, audit]`;
     `human_approved` only from the verified owner answer (**WS-3 IP-8**); `retrieval_profile.digest` of what was built.
4. *Ungoverned change detection* (`profile::governance`): `KERNEL_DEFAULT` (the kernel's own pin), `GOVERNED` (an
   ACTIVE, T2-verified profile decision pins exactly this identity), `GOVERNED_UNVERIFIED` (a decision pins it but is
   not verifiable here — hand-edited or from another machine), `UNGOVERNED_CHANGE` (differs from the latest decision;
   the changed fields are named), `UNGOVERNED` (no decision). Reported by every build (`retrieval_profile` in the
   report, runtime meta, manifest) and by `gov memory profile`.
5. *Benchmark research record* (**WS-4 IP-13**): `version`, `content_hash` (SHA-256 of the canonical benchmark result:
   format, held-out hash, rows, recommendation), a `benchmark` block, T2 seal.

**Product checks that own it** — the pin/identity binding runs at every build (G1-equivalent), every query and every
freshness evaluation (task close G2, status, doctor D025 through `pin_differences`); the change governance is the only
code path that writes the pins (`select`); the ungoverned-change report runs at every build and on demand. The
full-audit and doctor surfaces for the governance state are WS-2's (**IP-R2-3**); CIT-P materiality of a profile change
is WS-4's BC-P2-13 (**IP-R2-6**, round 3).

**Probes re-run**

| Probe | Base | This branch | Lines |
|---|---|---|---|
| beta-r `D4-component-separation` (unedited, direct and shim) | 9 P / 2 F | **11 P / 0 F** | `D4-b2-identified`, `D4-b2-drift` FAIL→PASS; nothing else changed |
| beta-r `D5-model-selection` (unedited) | 7 P / 4 F | stops at D5-b5 (4 P, then `KeyError: 'decision'`) | by design: the first `select` raises the R5 change gate and applies nothing; the probe never answers a gate |
| derived `D5-model-selection.owner-channel.P2-AR-0027` | — | **11 P / 1 F** | D5-b5, `-revision-bound`, `-b6-reindex`, `-authority`, `-evidence` (select refuses the unbenchmarked `builtin:8`), `-regression`, and the added `-ungoverned-product` PASS; `D5-b6-ungoverned` (reads `gov audit` findings only) FAIL → IP-R2-3 |
| zeta-r `W10` (shim) | 42 / 46 | 42 / 46 | `W10-a4-embedder-repinned-before-reindex(profile-change)` and `-continue` PASS (a re-pin never withholds deterministic inputs) |
| zeta-r `W01` (shim) | 118 / 140 | **120 / 140** | `W1-b6-benchmark-hash-in-record` FAIL→PASS (IP-13) |
| delta-r `L3` (shim) | 27 P / 12 F | 27 P / 12 F | stops at `L3.b5.6` on WS-3's T2 refusal before reaching `L3.b5.11` (both trees); `L3.b5.11` as worded → `SUPP-ws06-r2` R1 PASS |

The derived D5 copy changes only what its header lists: the helper library import path, one `governed_select()` that
answers the change gate through WS-3's test-material owner signer (`repair-1/ws03/evidence/hc_owner.py`, seed 7), the
refusal of `select builtin:8` checked with `g.run`, and one added product-surface line.

**Tests added** — certification `ws06::embedder_components_are_identified_bound_and_fail_closed_on_change` (a local
embed plugin with a model artefact beside it: identity in manifest and meta, weights changed → `EMBEDDER_MISMATCH` naming
the model artefact, freshness stale, incremental → full; descriptor revision 2 under a revision-1 pin → refused at query
and build) and `ws06::a_profile_change_needs_evidence_the_radius_gate_and_a_recorded_regression` (no evidence, forged
unsealed evidence, evidence not measuring the candidate, gate raised and re-reported, not answered, `--role human`
refused, agent resolution refused, owner answer → applied with decision/audit, `GOVERNED`, single-use gate, stale
approval, direct pin edit → `UNGOVERNED_CHANGE`). Supplementary `SUPP-ws06-r2` R1-R5 (8/8).

## 3. BC-P2-31 — Non-rebuildable state classified as derived — PARTIAL

**Requirement** (repair-delta §1; Contract v3 B1:188, B3:202, C1 claims, D6:352; D-0007 T2; A0-D6-01, A0-D6-02,
S0-B1B3-01): claims, emergency-control state and OS plugin registration survive deletion of every path the product
classifies derived or generated, and the repository contract and documentation classify their storage truthfully.
Handoff: WS-6 owns the classification (repository contract / paths); WS-5, WS-3 and WS-7 own the writers of claims,
control state and the plugin registry — IPs for any writer move.

**What changed** (`paths.rs`)

- `OS_STORES` declares the OS's non-rebuildable stores once — `claims`, `emergency-control`, `claim-trees` (claim-time
  tree snapshots task close attributes against), `cit-snapshots`, `update-snapshots`, `migration-snapshots` (class
  `operational`: machine-local, authoritative for what it records, never derived) and `plugin-registry` (class
  `authoritative`, tracked, D-0007 T2) — each with where it belongs (`.governance-state/…`;
  `governance/registry/plugin-registry.json`), where its writer keeps it today (inside `.governance-runtime/`,
  `governance/generated/`) and the writer that owns it.
- `RepositoryContract::decide` applies these kernel rules **after** the overlay's rules, at both locations: whatever a
  project overlay says (the shipped template's blanket `.governance-runtime/**: derived` and `governance/generated/**:
  generated`, or a hostile `**: derived`), the product never classifies these stores derived or generated; they are
  never indexed, retrieved or exported and are `mutation: os-only`. A `secret` classification still wins. Everything
  else in the runtime and generated directories keeps the overlay's classification.
- Location API for the writers: `store_path(root, id)`, `ensure_state_dir` (creates `.governance-state/` with a
  `.gitignore` that ignores its whole content, so it never reaches `git status`, a commit or a task's mutation scope),
  `relocate_legacy(root, id)` (moves a legacy store; identical copies removed; different copies →
  `STATE_LOCATION_CONFLICT`, nothing overwritten); `.governance-state` joins `ALWAYS_EXCLUDED_DIRS`.
- Detection: `misplaced_os_state(root)` lists every store still kept inside the derived runtime directory or the
  generated-views directory; every build reports it (`os_state`). `derived_deletion_set(root, contract)` lists what the
  product classifies derived/generated under those directories — by construction never a store.

**What is not done here, and why** (the handoff routes it): the writers still create the stores at their legacy paths —
`ClaimsStore::path_for` (WS-5), `control::path` (WS-3), `registry::REGISTRY_PATH` (WS-7), the snapshot writers (WS-4,
WS-8, WS-9) — so deleting the *whole* `.governance-runtime/` or `governance/generated/` still loses them
(**IP-R2-7…10, -12**). The overlay template `REPOSITORY_CONTRACT.yaml` cannot change this round without an overlay
operation in `migrations/M-4.1.4-4.1.5.yaml` (WS-9's file this round; `repair2::interface_contract_kernel_yaml_and_
migration_substance_are_consistent` enforces it) — **IP-R2-11**; `docs/ARCHITECTURE.md` (§3, §4, §4.3) is WS-3's this
round — **IP-R2-8**.

**Product check** — the classification is structural (every `decide`); `misplaced_os_state` runs at every build (G1)
and is the API for doctor/audit (**IP-R2-12**).

**Probes re-run**

| Probe | Base | This branch | Why |
|---|---|---|---|
| beta-r `D6-rebuild-guarantee` (unedited) | stops at `gate create` (`GATE_PACKAGE_INCOMPLETE`, WS-3 BC-P2-49) | same | probe predates BC-P2-49 |
| same through the integration's adapter (shim) | stops: `rebuild-memory` refused `FROZEN` (integration O-4, WS-3's decision this round) | same | D6-B also needs the writer moves (IP-R2-7…9) |
| synthesis `AC16-X2` `X2-B1B3-*` (direct and shim) | FAIL | FAIL | reads the overlay file with any-match semantics for the literal legacy paths; needs IP-R2-11 (template) — see §7 |

**Tests added** — lib `paths::tests::os_stores_are_never_classified_derived_or_generated` (shipped template and a
hostile overlay), `legacy_stores_relocate_and_are_reported_until_moved`; certification
`ws06::deleting_everything_classified_derived_keeps_claims_control_and_registration` (live claim, FREEZE_WRITES, a
registered plugin; every file the product classifies derived/generated deleted → claim, freeze and registration intact;
full rebuild; the claim still binds another session).

## 4. Integration points routed to WS-6

| IP | From | Status | How |
|---|---|---|---|
| IP-8 | WS-3 §9 | **done** | `profile::select` derives `human_approved` only from `gates::human_approval_for(p, gate, subject_sha256)` over the exact change; the CLI refusal of `--role human` stands (L3.b5.11 → `SUPP` R1 PASS) |
| IP-12 | WS-4 §7 | **done** | `memory::integrity` reads record edges through `Record::edges()` (`graph::canonical_of`) |
| IP-13 | WS-4 §7 | **done** | research record `version`, `content_hash`, `benchmark.result_sha256`; zeta-r `W1-b6-benchmark-hash-in-record` FAIL→PASS |

## 5. Regression and preservation (at `0a93907`)

| Suite | Result | Baseline | Evidence |
|---|---|---|---|
| `cargo test --lib` | **149 / 0** | 146 (+3 new) | `evidence/regression/cargo-test-lib.out` |
| `cargo test --test certification` | **104 / 0** (incl. `section6::*`, `arch::*`, `ws03::*`, `srr::*`) | 100 (+4 `ws06`) | `evidence/regression/cargo-test-certification.out` |
| rustfmt on touched leaf files; `cargo build` | 0 hunks; no warnings | — | — |
| beta-r, all 22 probes, unedited, direct and shim, base vs branch | **0 PASS→FAIL**; `D4-b2-*` FAIL→PASS; D5 stops at D5-b5 by design | base `843d79c` | `evidence/probes/`, `evidence/PROBE-BEFORE-AFTER.txt` |
| zeta-r W01, W10; synthesis AC16-X2; delta-r L3 | 0 PASS→FAIL | base | same |
| WS-6 round-1 `SUPP-ws06-behaviours.py` (unedited) | **19 / 19** | 19 / 19 | `evidence/after/round1-SUPP-ws06-behaviours.out` |
| R1 AR-0027 / AR-0029 / AR-0031 / AR-0033, unedited, private paths | **26/3, 26/2 (+`ho_f` not compiling), 27/7, 30/1** — the recorded baselines; AR-0033's only failure is `hv_a::a1`'s size pin | same | `evidence/r1-heldout/r1-heldout-final.out` |
| AR-0033 census (labelled copy, size assertions printed) | **107 files / 1527 functions; 0 violations** in all seven §6 activities (human_gate_create 43/38/1); `derive.py` agrees in all three splitter configurations | integration 105 / 1457, 0 violations | same |

R1 runs used a fresh private scratch directory per run (P2-HO-0020 item 7); the census line above is the one this
tree produced. `profile::select` raises its gate through `gates::create_system`, which asks §6 (`guard_effect`) itself;
its decision/audit writes go through `records::save_record` (the §6 record-write sink).

## 6. Existing builder test changed

`tests/certification/repair.rs::benchmark_records_evidence_and_selection_pins_through_decision` called `memory select
builtin:64 --research RES --by owner` and expected the pin applied at once. That is exactly A0-D5-02's defect (an R5
change applied with no gate). The test now takes the governed path — the first call returns `applied: false` with the
gate, the owner answers through `crate::ws03::human_decide`, `select … --gate` applies — and every original assertion
(decision file, overlay pin 64, 64-d vectors, fresh index, query works) is kept.

## 7. Limits — what this work does not do

- **Model artefacts outside the plugin's directory** (e.g. a model cache under the user's home, site-packages of the
  runtime) are not bound: the product cannot know them without a declaration. The descriptor schema (WS-7,
  `additionalProperties: false`) has no field for it — **IP-R2-13**. The default binding of the plugin's own directory is
  conservative: any file there (other plugins' implementations excluded) changes the identity and forces a re-embed.
- **Query-time checks use size and mtime** to skip re-hashing unchanged files (builds hash everything). A same-size,
  same-mtime substitution is caught at the next build, not the next query; plugin implementation integrity itself
  remains WS-7's pin (`plugin_set` re-hashes on every call).
- **Profile decisions are T2-sealed and machine-local** (WS-3's primitive): on a clone the profile reads
  `GOVERNED_UNVERIFIED` until re-selected there. Owner-signed human evidence in the decision remains verifiable anywhere.
- **Regression acceptance rule**: policy thresholds met, or not worse than the previous profile on recall@k, MRR,
  stale/superseded hit rates and forbidden hits. A profile that is worse on one measure but better overall is refused
  and rolled back — the owner can still change the held-out set or thresholds through their own governance.
- **Graph signatures** are the kernel's reading of the framework's relation semantics; custom record types are not
  judged. A requirement listing `tests:` (meaning "tested by") is reported `reversed` by design.
- **BC-P2-31** is PARTIAL (§3). Deleting the whole `.governance-runtime/` still loses claims and the freeze until the
  writers move; AC16-X2's literal-path check will also need the template to stop matching the legacy store paths with a
  blanket derived rule (IP-R2-11). **D6/X2 therefore still FAIL** on this branch.
- **Audit and doctor surfaces** of BC-P2-28/30/31 are WS-2's files (IP-R2-1, -3, -12); the unedited `C2-b2-orphan-flagged`,
  `-stale-superseded-target`, `-reversed-direction` and `D5-b6-ungoverned` lines read only those surfaces.
- `framework.json` (`to_framework_json`) does not yet project the kernel store rules (changing it makes every existing
  project's `framework.json` "out of sync" until regenerated) — part of IP-R2-11.

## 8. New integration points (round 3)

| ID | Owner | File / function | Call to add | Why |
|---|---|---|---|---|
| IP-R2-1 | WS-2 | `verification::run` family `graph_integrity`; `doctor.rs` D015 | `let gi = crate::memory::integrity::check(p, &store, db)?;` raise each `gi.findings[*]` (kind, severity, message, path); D015 fails on any non-`low` finding; detail `gi.counts`. Prefer its `stale` kind over `graph::lineage::stale_links` (which also flags provenance edges, §9 O-2) or keep both | C2-b2 orphan/stale/reversed lines; BC-P2-28 at G5 |
| IP-R2-2 | WS-4 | `cit/mod.rs` CIT-E `graph_integrity` verification | compare `memory::integrity::check` before and after the manifest; new non-`low` findings fail the verification (roll back) | a CIT must not introduce reversed/stale/ill-typed edges |
| IP-R2-3 | WS-2 | `doctor.rs` D025 and an audit family (`index_freshness` or a new `retrieval_profile`) | `let s = crate::memory::profile::status(p);` finding when `s["governed"] != true` with `s["severity"]`/`s["message"]`; in D025 also compare `db.get_meta("embedder_identity")["runtime_digest"]` with `profile::embedder_identity(p, &emb, meta).runtime_digest` | `D5-b6-ungoverned`; runtime drift in doctor |
| IP-R2-4 | WS-1 | `tests/governance/capability-evidence-map.yaml` | C2 → `memory::integrity::check` (G1 rebuild, `gov memory integrity`, family after IP-R2-1), `ws06::graph_integrity_*`; D1/D4/D5 → `memory::profile` binding and `select`, `ws06::embedder_components_*`, `ws06::a_profile_change_*`; B1/B3/D6 → `paths::OS_STORES`, `misplaced_os_state`, `ws06::deleting_everything_*` | AC-10 evidence owners |
| IP-R2-5 | WS-2 | evidence currency key | include `governance/generated/index-manifest.json` (now carries the embedder identity in its core) — completes round-1 IP-8 | a profile/identity change stales green memory evidence |
| IP-R2-6 | WS-4 (BC-P2-13, round 3) | CIT-P materiality | classify a change to `MEMORY_POLICY.embedding.*` / `reranker.*` overlay keys or a new `retrieval-profile` decision as material (every semantic answer and context packet changes) and route it to impact simulation; optionally let `profile::select` open a CIT for the overlay write once CIT-E supports policy-overlay operations | handoff: link BC-P2-30 to CIT-P materiality |
| IP-R2-7 | WS-5 | `memory::claims::ClaimsStore::path_for`/`open`; `orchestration::tasks::task_runtime_dir` | `crate::paths::store_path(root, "claims")` (linked worktrees: `<main worktree>/.governance-state/claims.db`, or `<git common dir>/governance-state/…`) and `store_path(root, "claim-trees")`; call `crate::paths::relocate_legacy(root, "claims")` / `("claim-trees")` under the store lock before opening | BC-P2-31: claims survive deleting `.governance-runtime/` |
| IP-R2-8 | WS-3 | `orchestration::control::path`; `docs/ARCHITECTURE.md` §3/§4/§4.3; `t2` OS-managed prefixes | `store_path(root, "emergency-control")` + `relocate_legacy(root, "emergency-control")` before read/write; docs state the `OS_STORES` classification (the runtime directory is derived *except* legacy stores until moved; `.governance-state/` is operational; the registry is tracked T2); recognise `governance/registry/` as OS-managed | FREEZE_WRITES survives; documentation truthful |
| IP-R2-9 | WS-7 | `capabilities::registry::REGISTRY_PATH`/`path`; `TOOL_POLICY.plugins.registry_path`; `plugin-registry.schema.json` description; `verification/currency.rs` registry path (WS-2) | `crate::paths::PLUGIN_REGISTRY_PATH`; move an existing registry with `relocate_legacy(root, "plugin-registry")` (a tracked move) | registration survives deleting `governance/generated/` (A0-D6-02) |
| IP-R2-10 | WS-4, WS-8, WS-9 | `cit::snapshot_dir`/`prune_snapshots`; `update::snapshot_dir`; `migrations::executor::snapshot_dir` | `store_path(root, "cit-snapshots" / "update-snapshots" / "migration-snapshots")` joined with the id/target/batch; relocate the legacy directory once | rollback material survives (A0-D6-01) |
| IP-R2-11 | WS-9 (migration) + WS-6 (template), round 3 together | `framework/overlay-templates/REPOSITORY_CONTRACT.yaml`; `migrations/M-4.1.4-4.1.5.yaml`; `paths::to_framework_json` | template rules for `.governance-state/**` (operational), the registry location (authoritative), the round-1 IP-7 `spec/reports/memory-quality/**` rule, and derived rules for the runtime directory that do not match the legacy store paths (e.g. `.governance-runtime/state.db*`, `…/context/**`, `…/benchmarks/**`, `…/health/**`, `…/plugins/**` instead of the blanket `**`); the migration's overlay operation; the `framework.json` projection of the kernel store rules | the overlay file itself states the truthful classification (AC16-X2) |
| IP-R2-12 | WS-2 | `scheduler/sandbox.rs` (copies `claims.db` from the runtime dir), `scheduler/mod.rs` currency input (hashes `claims.db` there), doctor D017/D026 messages; doctor/audit | read `paths::store_path(root, "claims")` after IP-R2-7; report `paths::misplaced_os_state(root)` as a finding (medium) | keeps the scheduler and doctor pointing at the real stores |
| IP-R2-13 | WS-7 | `plugin-descriptor.schema.json` | optional `model: {artefacts: [paths]}` / `runtime: {artefacts: [paths]}` for embed/rerank plugins; `memory::profile` then binds them (relative → manifest core, absolute → runtime meta) | model artefacts outside the plugin directory |

No new `cli/src/main.rs` semantics: the additions (`memory select --gate`, `memory integrity`, `memory profile`) are
additive and classified in `g0_label` and `COMMAND_GUARDS` (Read for the two new read-only commands; `memory select`
keeps its Write / `memory_select` L3 classification).

## 9. Observations for routing (not changed here)

| Id | What | Owner |
|---|---|---|
| O-1 | `REPOSITORY_CONTRACT.yaml` template: last-match semantics and `spec/**` listed after `spec/reports/**`, `spec/research/**`, `spec/audits/**` … make every spec file `authoritative`; the `evidence` class never applies to those paths | template (WS-6) + migration (WS-9), with IP-R2-11 |
| O-2 | `graph::lineage::stale_links` treats every relation except SUPERSEDES as a stale link — e.g. a new decision `derived_from` the decision it supersedes is reported stale | WS-4 (and IP-R2-1) |
| O-3 | `capabilities::governance::authorize` re-hashes every declared plugin's implementation on every `plugin_set` call; with the 150 MB debug `gov` as a test plugin the certification test `repair::benchmark_…` takes ~3 min (retrieval now classifies once per held-out run) | WS-7 |

## 10. Owner-decision questions

None. Every change stays inside ARCH-0001/ARCH-0003 and the active decisions: no trust boundary moved, no new external
dependency class, no language runtime in the core, no owner-controlled material touched. Agent identity is not built
(OWNER-DECISION-P2-0001); human answers come only from WS-3's owner-signed channel.

## 11. Evidence index (`evidence/`)

| Path | Content |
|---|---|
| `before/`, `after/` | the named beta-r probes (C2, D4, D5, D6) on the base and this branch; `after/derived.*.P2-AR-0027.out` (derived C2/D5 at the final build); `after/round1-SUPP-ws06-behaviours.out` |
| `derived/` | the two labelled derived probe copies (header lists every change) |
| `probes/` | every beta-r probe, zeta-r W01/W10, synthesis AC16-X2 and delta-r L3 on the base (`before/`) and this branch (`after/`), direct and shim, with shim logs and summaries |
| `PROBE-BEFORE-AFTER.txt` | line-by-line comparison (`compare_probes.py`) |
| `RERUN-probes.sh`, `compare_probes.py` | the runner (private scratch per run; the round-1 integration's adapter used unedited in shim mode) and the comparison |
| `SUPP-ws06-r2.py` / `.out` | supplementary behaviours R1-R6 (8/8) |
| `regression/` | `cargo test --lib`, `--test certification` |
| `r1-heldout/` | `run-r1-heldout.sh` (private paths), `r1-heldout-final.out`, the labelled `hv_a_derivation.a1-unpinned.P2-AR-0027.rs.txt` |
| `BUILD-base-release.log` | base build |

`after/derived.D5-model-selection.owner-channel.out` and `after/derived.C2-relationship-graph.integrity.out` are one-line
notes: interim runs on an earlier build of this branch, superseded by the `.P2-AR-0027.out` runs. Outputs contain
absolute scratch paths of this run.

## 12. Process disclosures

- Model Claude Opus 5 (1M context), `claude-opus-5[1m]`; fresh context. No sub-agents; the product owner was not
  contacted; no session or agent transcripts, task-output stores or user auto-memory were read (two long commands were
  moved to the background by the tool's time limit; their results were read only from files this run wrote in its
  evidence directory).
- Base-tree runs used a read-only `git archive` export of `843d79c` with the base binary, in private scratch; no other
  branch or worktree was touched.
- Shell commands deleting scratch or evidence files (`rm`, `rm -rf`) were denied by the permission system; they were not
  retried — fresh directories were used, and two superseded evidence files were replaced by one-line notes.
- The certification suite's `arch.rs` cross-implementation check (`python3` importing
  `capabilities/python/govos_capabilities`) leaves a git-ignored `__pycache__/` in the worktree; it is not committed and
  is not product code (pre-existing behaviour of that test).
