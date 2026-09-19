# P2-AR-0037 — Repair iteration 1, round 3, WS-6: knowledge fabric and retrieval

| Field | Value |
|---|---|
| Run | P2-AR-0037 (`capability-repair`), handoffs P2-HO-0036 + P2-HO-0031 + P2-HO-0020 + P2-HO-0010 |
| Agent model | Claude Opus 5 (1M context), `claude-opus-5[1m]` |
| Branch / worktree | `phase2/repair-1-r3-ws06` |
| Base | `53897c1a44157e5af81b176017bc7ded6a63b9cd` (integrated round-2 tree, `product_code_digest 797da37c…1fe1`) |
| Product work commits | `73819b8`, `b8f145d`, `7cd1fbb`. At `7cd1fbb`: `product_code_digest d01dca822266aa146bbb2e5d4862610cbcbf3f5244d9430af62cbd0df94acaf7`, `governed_state_digest 8f191e39…948f` (unchanged). The evidence/report commit changes no product file. |
| Items | R2-10 **REPAIRED_CLAIMED** · R2-11 **REPAIRED_CLAIMED** · R3-4 **REPAIRED_CLAIMED** · IP-W7-2 **REPAIRED_CLAIMED** · IP-WS10-03/04/05 **REPAIRED_CLAIMED** · BC-P2-31 (classification + template rules, WS-6 side) **REPAIRED_CLAIMED** · WS-9 IP-R2-2 / own O-1 / own IP-R2-11 **done on WS-6's side**; delivery to installed projects is WS-9's migration (IP recorded) |
| Regression | `cargo test --lib` **212 / 0** (207 + 5 new); `cargo test --test certification` **144 / 0** (136 + 8 new `ws06r3`); rustfmt clean on every touched Rust file; no build warnings |
| R1 | AR-0027 26/3, AR-0029 26/2 (+`ho_f` not compiling), AR-0031 27/7, AR-0033 30/1 (`hv_a::a1` size pin only) — the recorded baselines. Census 118 files / 2009 functions, 0 violations in every §6 activity |
| Probes | 29 audit-of-record probe runs (+3 labelled derived copies), base vs branch, through the round-2 integration's root-channel evidence adapter: **4 FAIL→PASS, 0 PASS→FAIL, 319 same**. Supplementary `SUPP-ws06-r3`: **16/16** on this branch, **1/16** on the base (every scenario discriminates) |
| Owner decisions | none required |

This is a builder's claim. Everything below is regression evidence (Contract v3 O3); acceptance is decided by fresh
independent verifiers. Nothing here claims a class or item is accepted, verified or closed.

## 0. What changed

| File (owner) | Change |
|---|---|
| `runtime/src/memory/indexer.rs` (WS-6) | `admit` — the one admission decision the indexer and freshness share; content-level exclusions carry content hash + derivation key; record-id ranking over the whole tree (`record_rank`, the record store's rule); derivation key includes the secret-scanning rules; research/experiment state class from the lifecycle standing, re-evaluated for unchanged artefacts; refused `code_intel` adapters recorded; `IndexOptions::observe_boundaries`, `content_changes`, `observe_significant_mutation`; report field `boundaries` |
| `runtime/src/memory/manifest.rs` (WS-6) | `freshness` rewritten on `admit`; manifest `excluded` entries carry what decided a content-level exclusion |
| `runtime/src/memory/chunking.rs` (WS-6) | `atx_heading` (one heading definition); `chunk_markdown` holds every heading (chunker version 3); `uncovered_lines_with` (Markdown comparison on both sides, every uncovered line) |
| `runtime/src/memory/coverage.rs` (WS-6) | heading-consistent comparison; `gap_row` lists every uncovered line; `unlisted_artefacts` |
| `runtime/src/memory/benchmark.rs` (WS-6) | `run_for(.., task)`: `--record` writes concluded research through the lifecycle stamps, validated and sealed; `--task` recorded as influenced |
| `runtime/src/memory/profile.rs` (WS-6) | `select` requires citable evidence (`lifecycle::require_citable`) and records the decision on the research (`lifecycle::record_influence`) |
| `runtime/src/security/secrets.rs` (WS-6) | `SecretScanner::signature` |
| `runtime/src/paths.rs` (WS-6) | `to_framework_json` projects the kernel store rules (`kernel_paths`, `precedence`); `RepositoryContract::shadowed_rules` (the O-1 defect class, generally); tests |
| `framework/overlay-templates/REPOSITORY_CONTRACT.yaml` (WS-6) | BC-P2-31 store rules, narrowed derived/generated rules, specific rules after general ones, the `spec/reports/memory-quality/**` rule |
| `framework/schemas/repository-contract.schema.json` (WS-6) | class `operational`, mutation `os-only` (1.1.0) |
| `framework/schemas/index-manifest.schema.json` (WS-6) | `excluded` entries documented (1.2.0) |
| `cli/src/main.rs` (declared exceptions, §9) | `memory benchmark --task` (new flag on WS-6's own command; its arm passes it); `rebuild-memory` and `memory rebuild` pass `observe_boundaries: true` |
| `tests/certification/ws06r3.rs` (new), `main.rs` (one `mod` line) | eight regression tests (§8) |
| `tests/certification/repair2.rs` | the migration-substance assertion checks the next version's migration once the current version is released (§8) |

15 files, +2 313 / −225 (`git diff --stat 53897c1..7cd1fbb`). No edit to `records.rs`, `graph/**`, `cit/**`, `checkpoints.rs`,
`lifecycle/**`, `capabilities/**`, any SRR/kernel/lock/update/release/recovery file, another workstream's policy, schema or
migration, the contract source, `release/verification/**`, `release/root-of-trust/**`, `release/releases/**`, phase-1 records,
`audit-0/**` or another `repair-1/` directory. No new crate dependency; the core spawns no language runtime.

## 1. R2-10 — index freshness judges exactly what the indexer indexes (pre-existing defect)

**Requirement** (WS-4 r2 R2-10; Contract v3 D1 "Required stale indexes degrade/block task close according to policy",
"Content-hash … based invalidation"; BC-P2-29 "incremental equals full"). A file the indexer skips must not read as
unindexed to freshness — before this repair every file over 2 MB and every duplicate-id record was "added" forever, so every
CIT-E failed its `index_freshness` verification and every freshness check after a build reported the index stale. Repaired
generally, in both directions: freshness must also never trust an exclusion that no longer holds.

**What changed**
- `indexer::admit(abs, rel, decision, scanner)` is the single admission decision. It answers, in this order: memory-quality
  event (outside), path-map / sensitivity / secret-path exclusion (`secret_class`, `sensitivity:<c>`), no index flag
  (outside), `binary`, `too_large` (`MAX_INDEXED_FILE_BYTES`), `unreadable`, `not_utf8` (a text file that is not UTF-8
  was also skipped silently and was also "added" forever), else a candidate with its text. The indexer and
  `manifest::freshness` both call it, so they agree by construction.
- Content-level exclusions — `secret_content`, and `duplicate_id` — are recorded in the manifest's `excluded` list with the
  **content hash and derivation key** they were decided under (a duplicate also names the id and the occurrence the index
  holds). Freshness honours such an exclusion only while both still match. A path-level exclusion is re-derived from the
  path map every time and never trusted from the manifest — the old `excluded.contains(path) → skip` rule hid a file whose
  exclusion had been lifted (a `DATA_SENSITIVITY` classification removed, a secret removed from a file).
- **Duplicate record ids.** Which occurrence the index holds is now a function of the tree, ranked before anything is
  written, by the rule the record store (`records::RecordStore::load`) resolves an id with: outside `archive/` before
  archived, `spec/` before `governance/project/` before elsewhere, then walk order. Before, a full build kept the first
  file in walk order (so `archive/X` and `governance/project/X` outranked `spec/X`: the index served a different record
  than governance resolved) and an incremental build kept whichever was indexed first (full ≠ incremental). The ranking pass
  reuses the previous manifest for content already derived under the same key and caches what it scans and parses for the
  build loop, so no file is secret-scanned or parsed twice.
- The derivation key includes the secret-scanning rules (`SecretScanner::signature`): a secret-policy change re-derives,
  and so re-scans, every artefact instead of leaving content indexed or excluded under the old rules. An unchanged artefact
  with an unchanged key is therefore no longer re-scanned on every incremental build.
- Research/experiment standing (IP-WS10-05, §6) depends on state outside the record; incremental builds and freshness
  re-evaluate it for unchanged artefacts (`recorded_state_class_holds`), so a standing change is stale until re-derived.

**Product check that owns it** — `manifest::freshness` (task close G2, CIT-E `index_freshness` verification, status, doctor
D010/D025, checkpoint state references) and every index build.

**Evidence** — certification `ws06r3::freshness_judges_exactly_what_the_indexer_indexes` (too large, not UTF-8, secret
content, three duplicates of one id incl. `governance/project/` and `archive/`, a lifted sensitivity exclusion; the held
occurrence removed and outranked; incremental manifest hash = full manifest hash after every step) and
`ws06r3::a_change_transaction_commits_while_the_tree_holds_files_the_indexer_skips`; lib
`indexer::tests::admission_decides_every_skip_reason_from_the_file`,
`record_rank_follows_the_record_store_and_changes_count_content_only`. Supplementary S1–S3 (base: `fresh: false` with
`added: [product/big.txt, product/latin1.txt, spec/requirements/REQ-0101.yaml]`, CIT `ROLLED_BACK` with
`VERIFICATION_FAILED: index not fresh after refresh: 0 stale/3 added`; the lifted exclusion unreported; the governance copy
held — all PASS on this branch).

## 2. R2-11 — a significant mutation observed at rebuild is a checkpoint boundary

**Requirement** (WS-4 r2 R2-11 → delta-r N2.b4; Contract v3 N2 "significant mutation"; framework §60). An index rebuild
that indexes at least the significant-mutation threshold of changes writes a checkpoint, without relying on the agent.

**What changed** — `IndexOptions::observe_boundaries`. At the end of a successful build it measures the mutation the build
observed — artefacts added, content-changed or removed relative to the index before it (`content_changes`; a pure
re-derivation is not a mutation) — against `CHECKPOINT_POLICY.watchdog.max_operations_between_checkpoints`. At or above it
the build calls `checkpoints::observe_boundaries` (WS-4's API: every trigger not yet checkpointed), and when that wrote no
`significant_mutation` checkpoint (it counts files by one-second modification time since the previous checkpoint and can
miss changes made in that second) it writes one with `checkpoints::create`, carrying the latest checkpoint's next action
forward. The checkpoint is never allowed to fail the build: a refusal (authority, FREEZE_WRITES — rebuild itself stays a
recovery operation) is reported typed in `boundaries.error` and as `CHECKPOINT_NOT_WRITTEN` in `problems`. The index is
current again afterwards (`checkpoints::create` refreshes it; the report names the final manifest hash).

**Scope, deliberately** — the operator's rebuild commands (`gov rebuild-memory`, `gov memory rebuild`) opt in. The 28 other
rebuild call sites (CIT-E refresh and verification, task close, update, adoption, recovery, checkpoint creation itself,
the audit's determinism rebuild) keep it off: each of those operations records its own boundary (accepted CIT, task
transition, migration batch), and a checkpoint record written in the middle of a CIT-E refresh would become an unindexed
file the transaction's own `index_freshness` verification then fails on. The CLI wiring is a declared exception (§9).

**Evidence** — certification `ws06r3::a_significant_mutation_observed_at_rebuild_is_a_checkpoint_boundary` (5 files: none;
30 files: `significant_mutation` checkpoint with the carried next action, index fresh; under FREEZE_WRITES: rebuild runs,
typed error reported); derived `N2-b4-significant-mutation.P2-AR-0037` (the N2.b4 block verbatim) FAIL→PASS; SUPP S4.

## 3. WS-2 R3-4 — Markdown headings held and compared the same way on both sides

**Requirement** (WS-2 r2 R3-4; BC-P2-25 "every non-empty line of an indexed document is held by at least one chunk";
Contract v3:249, :325). The coverage verifier reported held heading lines as gaps; "normalise heading markers on both sides
(or hold headings without markers consistently); list every uncovered line".

**What changed** — both, because measuring the base showed the reported gaps were not only a verifier artefact: a heading
directly followed by another heading (the ubiquitous `# Title` + `## Section`) or at the end of a document was held by **no
chunk at all** (the chunker only emitted non-empty sections), and a multi-line `\s+` in the chunker's heading regex could
swallow the next line as a heading while the verifier's per-line reading did not. Now:
- `chunking::atx_heading` is the single, single-line heading definition (CommonMark ATX: 1–6 `#` then a space/tab or end of
  line) used by the chunker and the verifier.
- `chunk_markdown` holds every heading: a heading with no content of its own is carried as a context line into the next
  section's chunk (a heading breadcrumb, which also helps retrieval), and trailing headings are held by a final section.
  `CHUNKER_VERSION` 2 → 3: an index built by chunker 2 is pin-incompatible and fully rebuilt, never mixed.
- `uncovered_lines_with(.., markdown)` compares heading lines by their text on both sides for records and documents (code
  keeps its `#` lines literally — a Python comment is not a heading); every uncovered line is listed per gap row
  (`coverage::gap_row`), and `verify` reports `unlisted_artefacts` beyond its 50 rows.

**Product check** — the build's coverage tally (`IndexReport.coverage`, meta `index_coverage`) and `coverage::verify`
(WS-2's `index_content_coverage` family at G1/G4–G6). WS-2's confirmation step can be retired (IP-R3-WS06-4).

**Evidence** — lib `chunking::tests::every_heading_is_held_and_headings_compare_the_same_way_on_both_sides`; certification
`ws06r3::markdown_headings_are_held_and_coverage_reports_no_false_gap`; SUPP S5 (base: build `complete: false`, suite
family 3 uncovered lines `Operating guide / Appendix / Glossary`, a confirmed medium finding; branch: complete, no finding).
WS-2's derived supplementary: `SUITE.coverage` PASS before and after.

## 4. WS-7 IP-W7-2 — a refused code-intelligence adapter is a recorded degradation

**Requirement** (D-0005: a code_intel degradation is recorded; beta-r `C5-b8-degrade`; round-2 integration O-6). Since WS-7
(BC-P2-39) an unregistered or tampered executable adapter is refused rather than run, and the indexer fell back to the
built-in extractor silently.

**What changed** — the build reads the refused `code_intel` descriptors from the governed plugin set (`PluginSet::denied`
and `rejected`, languages from the descriptor, the typed refusal code from `PluginSet::refusal`) — adapters stay resolved
through the capability registry. For every file of a covered language that no usable adapter serves: a per-file
degradation `"<path>: code_intel plugin <id> refused (<code>); built-in extractor used"`; for every build while files of
that language exist (also when nothing was re-analysed): a build-level degradation; and a `tool-failure` record in failure
memory (deduplicated by signature, indexed by the same build).

**Evidence** — certification `ws06r3::a_refused_code_intelligence_adapter_is_a_recorded_degradation`; beta-r C5 unedited
`C5-b8-degrade` FAIL→PASS; WS-6 round-1 probe unedited `S4-recall` FAIL→PASS (17/19; its two `S1-register-*` lines need the
unregistered adapter to run, which BC-P2-39 refuses by design — the registered derived copy is 19/19); SUPP S6.

## 5. WS-10 IP-WS10-04 / IP-WS10-03 — benchmark research and the profile decision's backlink

**Requirement** (Contract v3 J1 "influenced decisions/tasks"; WS-10 r2 §1.4).
- **IP-WS10-04** — `gov memory benchmark --record [--task <TASK>]`: the research record is written through the research
  lifecycle's own path — `research_state: CONCLUDED`, `recorded_by`/`concluded_by` stamps, lifecycle history,
  `lifecycle::validate_seal_save` (schema validation, T2 seal) — and names the commissioning task in `influences`
  (`TASK_NOT_FOUND` for a non-task, `USAGE` for `--task` without `--record`; `guard_write` before any write).
- **IP-WS10-03** — `profile::select` refuses evidence that is not governed (`lifecycle::require_citable`,
  `EVIDENCE_NOT_CITABLE`) before raising or applying the change gate, and after the decision is persisted records it on
  the research (`lifecycle::record_influence`, re-sealing only a record whose seal verified). The result reports
  `influence_recorded`.

**Evidence** — certification `ws06r3::the_benchmark_is_governed_research_and_the_profile_decision_is_recorded_as_its_influence`
(governed standing, seal `VERIFIED` after the backlink); derived `J1-J2-research-experiments.select-gate.P2-AR-0037`
`J1.a.influence_backlink` FAIL→PASS; SUPP S8/S9; WS-10's derived supplementary 35/35 before and after.
`J1.a.influences` as the unedited probe states it (non-empty at creation without a task) stays FAIL: nothing was influenced
yet; with `--task` the commissioning task is recorded (WS-10's reading, their §1.4).

## 6. WS-10 IP-WS10-05 — non-governed evidence held reference-only in the index

**What changed** — the index derives a research/experiment record's state class from `lifecycle::indexed_state_class`
(non-governed evidence presented as EVIDENCE/AUTHORITATIVE/DERIVED is held NARRATIVE); a historical path stays HISTORICAL.
Because the standing depends on other state (an experiment's input bytes, seals, promotions), incremental builds and
freshness re-evaluate it for unchanged artefacts (§1). Plain files of path class `evidence` now map to state class
EVIDENCE (they mapped to NARRATIVE; with the template's evidence areas taking effect, §7, this is what those areas state).

**Evidence** — certification `ws06r3::the_index_holds_research_and_experiments_at_their_evidence_standing` (incomplete
research NARRATIVE, complete EVIDENCE, a reproduced experiment EVIDENCE; its input drifts → freshness stale with the
experiment `reclassified` → incremental re-derives it NARRATIVE → equals a full build); SUPP S7 (base: the unsupported
conclusion retrieved as EVIDENCE — delta-r OBSERVE `J1.b.retrieval`).

## 7. BC-P2-31 — classification and template rules (WS-6 side); WS-9 IP-R2-2; own O-1 and IP-R2-11

**Requirement** (repair-delta BC-P2-31; Contract v3 B1:188, B3:202, D6:352; D-0007 T2; S0-B1B3-01): the product's repository
contract and documentation classify the storage of claims, emergency-control state and plugin registration truthfully, and
they survive deletion of everything classified derived/generated. WS-6 owns the classification and the template; the
writers are WS-3/4/5/7/8/9's (their round-3 moves); template delivery to installed projects is WS-9's migration.

**What changed**
- **Template** (`REPOSITORY_CONTRACT.yaml`, new installations): the file states the classification the product applies —
  under the file's own documented reading (last match decides) *and* under any other reading (every matching rule, as
  synthesis AC16-X2 reads it) no location of an OS store is derived or generated:
  - `governance/registry/**` authoritative, `mutation: os-only`, not indexed (D-0007 T2);
  - `governance/generated/**` narrowed to the regenerable views (`*-manifest.json`, `tool-registry.json`, `adapters/**`);
    the legacy registry location and `skill-bindings.json` (OS-written first-seen bindings, not regenerable) authoritative,
    `os-only`;
  - `.governance-runtime/**` narrowed to what is rebuilt (`state.db*`, `context/**`, `health/**`, `plugins/**`,
    `benchmarks/**` derived) and what is machine-local observation (`telemetry/**`, `routing/**`, `outbound/**`
    `runtime-data`); the legacy store locations (`claims.db*`, `control.json`, `tasks/**`, `cit/**`, `update/**`,
    `migration/**`) `operational`, `os-only`; `.governance-state/**` `operational`, `os-only`;
  - **O-1 fixed**: a general rule now precedes the rules that refine it — `spec/**` before `spec/decisions|reports|lessons|
    research|experiments|audits/**` (the evidence class had never applied; `spec/decisions`' `mutation: restricted` had
    never applied either), `product/**` before `product/tests/**` (tests were classified `source`);
  - **WS-9 IP-R2-2**: `spec/reports/memory-quality/**` evidence, all four index flags false, after `spec/reports/**`.
- **Schema**: `repository-contract` admits class `operational` and mutation `os-only` (1.1.0) — the overlay stays valid.
- **framework.json** (`to_framework_json`) projects the kernel store rules (`kernel_paths`) and states the precedence, so the
  generated path-map view is truthful even for an overlay that tries to call a store derived.
- **`RepositoryContract::shadowed_rules`** — the O-1 defect class, generally: a rule a later rule overrides for every path
  it matches ("list a specific rule after the general rule it refines"), the input for a doctor/audit finding and for a
  migration that reorders an installed contract. The shipped template has none; the 4.1.5 template had seven (the six
  spec evidence/decision areas under `spec/**`, and `product/tests/**` under `product/**`).
- **Confirmation against the writer moves**: the store ids and `store_path`/`relocate_legacy` are unchanged (the API the
  other workstreams implement against this round); lib tripwire `paths::tests::every_writer_location_is_classified_as_its_store`
  asserts that wherever the writers that expose their location keep a store today (`ClaimsStore::path_for`,
  `control::path`, `registry::path`, `migrations::executor::snapshot_dir`) and wherever `store_path` puts each store, the
  product classifies it as that store (class and `os_store`), under the shipped template and a hostile overlay. At
  integration it fails if a writer moves a store somewhere `OS_STORES` does not declare.
- **Test change**: the migration-substance certification assertion (`repair2::interface_contract_kernel_yaml_and_
  migration_substance_are_consistent`) checked the migration *into* the current version against the working-tree
  templates. With 4.1.5 released (its payload immutable under `release/releases/4.1.5`), a template change is a 4.1.6
  change: the assertion now checks migrations into 4.1.5 against the released payload they shipped with, and requires every
  migration *from* 4.1.5 (`M-4.1.5-4.1.6`, WS-9's) to account for the working tree's changes since that payload. The
  property ("a template change reaches installed projects only through a migration") is kept and extended; before the
  version is released, the check is the original one. It passes whether WS-8 keeps `VERSION` at 4.1.5 or bumps it.

**Not done here, and why** — the migration operations that bring installed projects' contracts to the new rules
(WS-9, IP-R3-WS06-1); `KERNEL.yaml` `schema_versions` (WS-8, IP-R3-WS06-2); `docs/ARCHITECTURE.md` (WS-3); the writer moves
themselves. Deleting the whole `.governance-runtime/` still loses a store until its writer moves (the kernel classifies it
operational wherever it is, and `misplaced_os_state` reports it at every build).

**Evidence** — certification `ws06r3::the_repository_contract_states_where_the_os_keeps_its_state` (any-match reading of
the installed overlay, last-match classes, memory-quality not indexed, framework.json `kernel_paths`, doctor D008 in sync,
overlay schema-valid); lib `the_shipped_template_states_the_store_classification_under_any_reading`,
`every_writer_location_is_classified_as_its_store`; derived `AC16-X2-B1B3.P2-AR-0037` (the X2-B1B3 block verbatim)
FAIL→PASS; SUPP S10 (base: `.governance-runtime/**: derived` and `governance/generated/**: generated` match the store paths;
reports/research authoritative, product tests `source`; no kernel_paths).

## 8. Tests added and changed

| Test | Kind |
|---|---|
| `chunking::tests::every_heading_is_held_and_headings_compare_the_same_way_on_both_sides` | lib, new |
| `indexer::tests::admission_decides_every_skip_reason_from_the_file` | lib, new |
| `indexer::tests::record_rank_follows_the_record_store_and_changes_count_content_only` | lib, new |
| `paths::tests::the_shipped_template_states_the_store_classification_under_any_reading` | lib, new |
| `paths::tests::every_writer_location_is_classified_as_its_store` | lib, new (tripwire) |
| `ws06r3::freshness_judges_exactly_what_the_indexer_indexes` | certification, new |
| `ws06r3::a_change_transaction_commits_while_the_tree_holds_files_the_indexer_skips` | certification, new |
| `ws06r3::a_significant_mutation_observed_at_rebuild_is_a_checkpoint_boundary` | certification, new |
| `ws06r3::markdown_headings_are_held_and_coverage_reports_no_false_gap` | certification, new |
| `ws06r3::a_refused_code_intelligence_adapter_is_a_recorded_degradation` | certification, new |
| `ws06r3::the_index_holds_research_and_experiments_at_their_evidence_standing` | certification, new |
| `ws06r3::the_benchmark_is_governed_research_and_the_profile_decision_is_recorded_as_its_influence` | certification, new |
| `ws06r3::the_repository_contract_states_where_the_os_keeps_its_state` | certification, new |
| `repair2::interface_contract_kernel_yaml_and_migration_substance_are_consistent` | certification, changed (§7: why) |

No other existing test changed; every existing lib and certification test passes unchanged.

## 9. Declared exceptions to file ownership

- `cli/src/main.rs`: (a) `memory benchmark --task` — a new flag on WS-6's own command (the variant gains a field and its arm
  passes it to `benchmark::run_for`, as the append requires); (b) the `rebuild-memory` and `memory rebuild` arms now pass
  `observe_boundaries: true` — WS-6's own commands, no role-resolution or guard semantics touched, labels and
  `COMMAND_GUARDS` unchanged (`rebuild_memory`, Write, on the FROZEN/PAUSED recovery allow-lists: a checkpoint it cannot
  write under a freeze is reported, not written). (b) changes an existing line; it is how R2-11 reaches N2.b4's command. If
  WS-3 as semantic owner prefers otherwise, the runtime API stays and the two arms revert to the default (IP-R3-WS06-3).
- `tests/certification/repair2.rs`: one assertion extended (§7).
- `tests/certification/main.rs`: one `mod` line.

## 10. Probes re-run (method and results)

Runner `evidence/RERUN-probes.sh` (derived from this workstream's round-2 runner; the only change is the evidence adapter:
the round-2 integration's root-channel shim, used unedited, and a `shim5` mode with its derived WS-5 receipt adapter, also
unedited). `before` = a read-only `git archive` export of `53897c1` with its own release binary (`sha256 5ff6ce9c…6b82`);
`after` = this worktree at `7cd1fbb` (`sha256 ffb673b4…b472`), 0 product files differing. Private scratch per run.
`evidence/compare_probes.py` pairs every verdict line (`PROBE-BEFORE-AFTER.txt`).

| Probe | Before | After | Lines |
|---|---|---|---|
| beta-r C5-code-structural-memory (unedited) | 8/11 | **9/11** | `C5-b8-degrade` FAIL→PASS |
| beta-r C1, C2, C3, C4, C6–C10, D1–D6, DERIVED, FRESH, R1-R2, R3, SCALE, X-K2-D1-W6 (unedited) | — | identical | 0 changes (several stop at the same by-design refusal of another workstream on both binaries: D1 at D1-b5 plugin registration WS-7, D6 at task claim WS-5, R1-R2 at adopt review WS-9) |
| delta-r N1-N2 (unedited; shim and shim5) | 14/14 | 14/14 | stops before N2.b4 on both (task close: WS-5 receipt / untraceable implementation) |
| derived `N2-b4-significant-mutation.P2-AR-0037` | 0/1 | **1/1** | `N2.b4` FAIL→PASS |
| delta-r J1-J2 (unedited) | 8/9 | 8/9 | stops at `memory select` on both (BC-P2-30's R5 gate, by design) |
| derived `J1-J2-research-experiments.select-gate.P2-AR-0037` | 9/11 | **10/11** | `J1.a.influence_backlink` FAIL→PASS; `J1.a.influences` FAIL both (§5) |
| synthesis AC16-X2 (unedited) | 1/1 | 1/1 | stops at `task claim TASK-W` on both (WS-5 BC-P2-16) |
| derived `AC16-X2-B1B3.P2-AR-0037` | 0/1 | **1/1** | `X2-B1B3-nonrebuildable-state-not-classified-derived` FAIL→PASS |
| zeta-r FR-freshness-invalidation, W01 (unedited) | — | identical | 0 changes |
| **Total** | | | **4 FAIL→PASS, 0 PASS→FAIL, 319 same** |

Each derived copy's header lists its changes (`evidence/derived/`). Builder probes (`RUN-builder-probes.sh`, the round-2
integration's derived copies unedited, base vs branch): WS-2 supplementary 50/51 both (W7.2b = IF-1, routed to WS-2);
WS-6 round-1 registered 19/19 both; WS-6 round-2 8/8 both; WS-10 35/35 both; WS-6 round-1 **unedited** 16/19 → **17/19**
(`S4-recall` FAIL→PASS). Supplementary `SUPP-ws06-r3.py` (`RUN-SUPP.sh`): base 1/16, branch **16/16**.

## 11. Regression and R1 preservation (at `7cd1fbb`)

| Suite | Result | Evidence |
|---|---|---|
| `cargo test --lib` | **212 / 0** (207 + 5) | `evidence/regression/final-lib.out` |
| `cargo test --test certification` | **144 / 0** in four runs (59 + 23 + 10 + 52; `--list` = 144; includes `section6::*` 9, `srr::*` 21, `arch::*` 8, `ws03::*` 15) | `evidence/regression/final-cert-*.out` |
| rustfmt `--check` (edition 2021) on every touched Rust file; build / test build warnings | 0 hunks; 0 warnings | — |
| R1 AR-0027 / AR-0029 / AR-0031 / AR-0033, unedited, private scratch | **26/3, 26/2 (+`ho_f` not compiling), 27/7, 30/1** — the recorded baselines, same failing tests; AR-0033's only failure is `hv_a::a1`'s size pin | `evidence/r1-heldout/r1-heldout-final.out` |
| AR-0033 census (labelled unpinned copy) | **118 files / 2009 functions; 0 violations** in all seven §6 activities; `derive.py` agrees in all three splitter configurations | same |

No R1-listed file was touched; the suites were run anyway (P2-HO-0020 rule 7). The census counts
`human_gate_create` derived 46 / writers 41 (round-2 integration 47 / 42): `memory benchmark --record` now writes through
`lifecycle::validate_seal_save` instead of calling `save_record` itself, so one function no longer carries the literal
write signature; the write is made by the lifecycle helper, already counted, and every writer still carries its accessor.

## 12. New integration points (for integration / round 4)

| ID | Owner | File / function | What | Why |
|---|---|---|---|---|
| IP-R3-WS06-1 | WS-9 | `migrations/M-4.1.5-4.1.6.yaml` (+ an op if needed in `migrations::framework`) | Deliver §7's template rules to installed projects: add `governance/registry/**`, the narrowed `governance/generated/*` rules, the legacy-registry and `skill-bindings.json` rules, the narrowed `.governance-runtime/*` rules, the legacy store rules and `.governance-state/**`; retire the blanket `.governance-runtime/**` and `governance/generated/**` rules; and put each refining rule after the general rule it refines (`spec/**` before its evidence areas, `product/**` before `product/tests/**`). `set_overlay_rule` appends only, so reordering needs a remove-and-append (or move) op; apply it to rules still equal to the template default, and report a customised contract's dead rules with `RepositoryContract::shadowed_rules()` instead of rewriting it. Keep `regenerate_adapters` (framework.json gains `kernel_paths`) | truthful classification in installed projects; the substance check is per file, so it cannot see a missing rule |
| IP-R3-WS06-2 | WS-8 (release owner) | `framework/KERNEL.yaml` `schema_versions` | `repository-contract: 1.1.0`, `index-manifest: 1.2.0` | kernel payload/version consistency |
| IP-R3-WS06-3 | WS-3 | `cli/src/main.rs` review | confirm §9 (b) (`rebuild-memory`/`memory rebuild` observe boundaries) and (a) (`memory benchmark --task`); `docs/ARCHITECTURE.md`: `.governance-state/`, `governance/registry/`, the template's last-match semantics, framework.json `kernel_paths` | semantic owner; documentation truthful |
| IP-R3-WS06-4 | WS-2 | `doctor.rs` / a governance family; `verification::reporting::index_content_coverage` | a finding per `p.contract().shadowed_rules()` entry (low: a path-map rule that never decides); retire `gap_is_heading_marker_artefact` (the verifier now compares headings consistently and lists every line; `verify` reports `unlisted_artefacts`) | O-1 detected generally; R3-4 follow-up |
| IP-R3-WS06-5 | WS-5 | `memory::claims::shared_runtime_dir` / `ClaimsStore::path_for` | a linked worktree's shared claims store must also move out of the main checkout's `.governance-runtime/` (e.g. `<main>/<rel>/.governance-state/claims.db`, or `<git common dir>/governance-state/<rel>/`); `paths::tests::every_writer_location_is_classified_as_its_store` checks the main-worktree location at integration | claims survive deleting derived state in every worktree layout |
| IP-R3-WS06-6 | WS-1 | `tests/governance/capability-evidence-map.yaml` | D1 → `memory::indexer::admit` + `manifest::freshness`, `ws06r3::freshness_*`, `ws06r3::a_change_transaction_*`; N2 → `IndexOptions::observe_boundaries`, `ws06r3::a_significant_mutation_*`; C3/C4 (BC-P2-25) → chunker 3, `ws06r3::markdown_headings_*`; C5/F4 (D-0005) → `ws06r3::a_refused_code_intelligence_*`; J1 → `indexed_state_class` in the indexer, `ws06r3::the_index_holds_*`, `ws06r3::the_benchmark_*`; B1/B2/B3 (BC-P2-31) → template + `shadowed_rules` + `kernel_paths`, `ws06r3::the_repository_contract_*` | AC-10 evidence owners |
| IP-R3-WS06-7 | WS-2 (writer) + WS-6 | `skills.rs` `BINDINGS_REL` | `governance/generated/skill-bindings.json` is OS-written, non-rebuildable (first-seen content binding): move it beside the registry (`governance/registry/`), then WS-6 adds it to `OS_STORES` (not added now: `misplaced_os_state` would report it at every build while its writer has not moved, and IP-R2-12 makes that a finding) | BC-P2-31 generally |

Round-2 IPs recorded against WS-6's files that this round implemented: WS-4 R2-10, R2-11; WS-2 R3-4; WS-7 IP-W7-2;
WS-10 IP-WS10-03/04/05; WS-9 IP-R2-2; WS-6 IP-R2-11 (WS-6 side). The other round-2 WS-6 IPs are other owners' this round
(IP-R2-1/3/5/12 WS-2, IP-R2-2/6/10 WS-4, IP-R2-7 WS-5, IP-R2-8 WS-3, IP-R2-9/13 WS-7, IP-R2-10 WS-8/WS-9).

## 13. Observations for routing (not changed here)

| Id | What | Owner |
|---|---|---|
| O-1 | `checkpoints::files_changed_since` counts files modified strictly after the previous checkpoint's second, so a mutation in that same second is not a significant mutation to `observe_boundaries`; the rebuild-observed count (§2) covers the operator rebuild path only | WS-4 |
| O-2 | Several unedited audit probes stop at another workstream's by-design refusal on both binaries (beta-r D1 at D1-b5, D6 at task claim, R1-R2 at adopt review; delta-r N1-N2 at task close, J1-J2 at gated select then at SCHEMA_INVALID propose; synthesis AC16-X2 at task claim). Verifiers need derived copies or fresh probes for their later lines | verifiers / probe authors |
| O-3 | `J1.a.influences` (non-empty at creation without a task) has no product meaning (§5) | WS-10 / verifiers |

## 14. Limits — what this work does not do

- **Freshness semantics.** Fresh means the index holds exactly what a build would hold: every candidate file with its
  current content hash, derivation key and standing, or excluded for its content under the same hash and key; nothing held
  that should not be. The manifest's informational list of path-level and file-level exclusions (a secret file, a binary,
  a too-large file) is brought current by the next build and does not make the index stale (as before this repair).
- **Duplicate ranking outside the record store's roots.** A record outside `spec/`, `governance/project/` and `archive/`
  (a `.md` with front matter under `docs/`) ranks after the governed roots and before `archive/`; the record store does not
  load it at all.
- **Boundary observation** is on for the operator's rebuild commands only (§2); a first checkpoint is written at a
  significant mutation even when none exists yet (its next action states that it was product-observed).
- **The template changes reach new installations only** until WS-9's migration delivers them (IP-R3-WS06-1); installed
  projects keep their contract (the kernel's store classification applies regardless).
- **Headings in fenced code blocks** are still read as headings by both the chunker and the verifier (consistently; no
  false gap), as before.

## 15. Owner-decision questions

None. Everything stays inside ARCH-0001/ARCH-0003 and the active decisions: no trust boundary moved, no new external
dependency class, no language runtime in the core, no owner-controlled material touched, no default role, no
unauthenticated answer path, the standalone human-gate anchor stays off (the evidence adapter relays owner-signed answers
through the provisioned throw-away root).

## 16. Evidence index (`evidence/`)

| Path | Content |
|---|---|
| `RERUN-probes.sh`, `compare_probes.py`, `PROBE-BEFORE-AFTER.txt` | audit-of-record probe runner, verdict pairing, the comparison |
| `probes/before/`, `probes/after/` | every probe run (outputs, adapter logs) on the base and this branch |
| `derived/` | three labelled derived probe copies (headers list every change) |
| `SUPP-ws06-r3.py`, `RUN-SUPP.sh`, `supp/` | supplementary S1–S10, base (1/16) and branch (16/16) |
| `RUN-builder-probes.sh`, `builder-probes/` | the round-2 integration's derived builder probes (WS-2, WS-6 r1/r2, WS-10) and WS-6 round 1 unedited, base and branch |
| `regression/` | final lib and certification runs |
| `r1-heldout/` | runner (relabelled copy of round 2's), the labelled `hv_a` copy, the final run (census, S1, S2) |

Outputs contain absolute scratch paths of this run.

## 17. Process disclosures

- Model Claude Opus 5 (1M context), `claude-opus-5[1m]`; fresh context. No sub-agents; the product owner was not
  contacted; no session or agent transcripts, task-output stores or user auto-memory were read. Every command ran in the
  foreground; results were read only from files this run wrote.
- A shell command that would have deleted a scratch directory (`rm -rf`) was denied by the permission system; it was not
  retried — fresh `mktemp` directories were used instead.
- The first "after" probe runs used a release binary from `73819b8`; after the last product commit (`7cd1fbb`, the
  manifest's exclusion entries no longer carry a size) the binary was rebuilt and every "after" run was repeated; the
  recorded runs are the `7cd1fbb` ones.
- Three of my own test drafts had wrong expectations, fixed before the recorded runs: the significant-mutation checkpoint
  is sometimes written by `checkpoints::observe_boundaries` rather than the rebuild's fallback; the failure-memory outcome
  names the record path, not the plugin; a directory store is probed through a file inside it.
- The certification harness writes scenario trees under `/tmp` (`gov-cert-*`); the `arch` test leaves a git-ignored
  `__pycache__/` in `capabilities/python/` (pre-existing behaviour; not committed).
