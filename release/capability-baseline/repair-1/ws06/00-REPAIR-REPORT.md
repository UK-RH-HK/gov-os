# P2-AR-0019 — Repair iteration 1, round 1, WS-6 (part): knowledge fabric and retrieval

| Field | Value |
|---|---|
| Run | P2-AR-0019 (`capability-repair`), handoffs P2-HO-0010 (common protocol) + P2-HO-0016 |
| Agent model | `claude-opus-5[1m]` (Claude Opus 5, 1M context) |
| Branch / worktree | `phase2/repair-1-ws06` |
| Base | `c6b60bc760a0bb42907f74210fd9e644a420851a` (product code = `cap2-candidate-0`, `product_code_digest bd4d65d9…0547`) |
| Product work commit | `2f4ee5771d09d44cce2d842e6e51b61d8854a5ab` (`product_code_digest a441def4…5302`) |
| Classes | BC-P2-25, BC-P2-26, BC-P2-27, BC-P2-29, BC-P2-32 — all **REPAIRED_CLAIMED** |
| Not started (round 2) | BC-P2-28, BC-P2-30, BC-P2-31 |
| Owner decisions | none required |

This is a builder's claim. The evidence below is **regression evidence** (Contract v3 O3); acceptance is decided by
fresh independent verifiers. Nothing here claims a class is accepted, verified or closed.

## 0. What changed, in one table

| File (all owned by WS-6) | Change |
|---|---|
| `runtime/src/records.rs` (record-text/chunk region only: `Record::text`, new `Record::text_sections`, `render_value`, constants) | Every record field — list-valued and nested at any depth — becomes named record content |
| `runtime/src/memory/chunking.rs` | Record sections never dropped for size; hierarchical, line-complete code chunking (`chunk_code`), `uncovered_lines`, `CHUNKER_VERSION` |
| `runtime/src/memory/indexer.rs` | `current_view`; per-artefact `DerivationContext` keys; incremental re-derivation of reclassified files; `ImportResolver` (tree-based, src-layouts, crates, Go packages); `derive_cross_artifact_facts` (imports, CALLS, TESTS, inheritance edges, supersession) for incremental **and** full builds; route/model/relation storage; coverage tally; tool-failure recording |
| `runtime/src/memory/manifest.rs` | Manifest entries carry `derivation`; `freshness` evaluates the current policy/path map and reports `reclassified` entries stale; removed = no longer indexable |
| `runtime/src/memory/db.rs` | `derivation` table (created `IF NOT EXISTS`; cleared/deleted with artefacts) |
| `runtime/src/memory/coverage.rs` (new) | `verify(p, db)` whole-index content-coverage check; `expected_content`, `without_heading_markers` |
| `runtime/src/memory/failures.rs` (new) | Durable failure memory: `record`, `record_tool_failure`, `record_heldout_misses`, `link_follow_up`, `open_failures`, `list` |
| `runtime/src/memory/benchmark.rs`, `memory/mod.rs` | `record_failures: Some(false)` for benchmark candidate builds; module registration |
| `runtime/src/retrieval/mod.rs` | Admission before truncation and before the reranker; filename routing; code-entity graph routing; primary-route tier; content de-duplication; structural (route/model) lookups; evidence coverage and retrieval-miss recording; tool-failure recording |
| `runtime/src/code_intelligence/mod.rs`, `generic.rs` | `Relation`/`Route`/`Model` facts; lexer-level comment/string blanking; inheritance, routes, DB models for the languages in scope; `provider_identity`; plugins without the new keys completed from the builtin |
| `capabilities/python/govos_capabilities/code_intel_python_ast.py` | AST `relations`, `routes`, `models` (protocol fields) |

13 files, +4 815 / −477 lines. No edit to `cli/src/main.rs`, `runtime/src/lib.rs`, any other workstream's file, the
contract source, `release/verification/**`, `release/root-of-trust/**`, `release/releases/**`, phase-1 records or
`audit-0/**`. No new crate dependency; no language runtime is spawned by the core (`tests/certification/arch.rs` green).

## 1. BC-P2-25 — Index content coverage and chunk granularity — REPAIRED_CLAIMED

**Requirement** (repair-delta §1; Contract v3:234-249, :274, :323-327; framework §11.3, §11.4, §14.1): all governed record
content (list-valued and nested fields, worker returns) and every non-empty line of indexed code are held by at least one
chunk with section-level provenance; code is chunked to function/method units and symbol lookups return the unit's own
slice.

**What changed**
- `Record::text_sections()` (records.rs, record-text region): every field except the six held elsewhere
  (`id`, `type`, `status`, `state_class` are artefact-row columns, `title` is the document chunk, `body` is chunked as
  Markdown) is rendered — scalars as themselves, lists as `- item` lines, objects as `key: value` lines, nested values
  indented (YAML-like, so phrases stay contiguous). A field whose rendering reaches 40 characters becomes its own section
  named after the field (section-level provenance, e.g. `acceptance_criteria`, `return`); shorter fields are grouped in
  record order into one `fields` section. `Record::text()` now returns the complete content.
- `chunk_record` no longer drops short sections; the indexer passes `text_sections()` instead of the ≥40-char top-level
  strings.
- `chunk_code` (chunking.rs) is hierarchical and line-complete: units come from **all** symbols with spans (nested ones
  included, `indexer::chunk_units`), nesting is derived from span containment, decorator/annotation/attribute/doc-comment
  lines are attached to the unit below them, top-level units are `section` chunks, nested units (methods, `impl` items)
  are `child` chunks parented to their enclosing unit, a unit longer than `max_chars` keeps every line through size-split
  children of the lines its nested units do not hold, and every remaining non-empty line (header, module-level
  statements, registrations, trailing `__main__` blocks, exports) is emitted as `__module__` sections. Symbol lookups
  find the unit's own chunk (`retrieval::chunk_for` falls back to the parent unit, then the document).
- The chunker identity is part of the chunking pin (`"chunker": "2"`), so an index built by the previous chunker is
  reported incompatible (`pin_mismatch`) and fully rebuilt, never mixed.

**Product check that owns it**
- Every `rebuild` (full and incremental — index mutation, G1-equivalent; also the refresh inside task close and CIT-E)
  checks every artefact it (re)indexes: `IndexReport.coverage` (`checked_artifacts`, `uncovered_lines`, `complete`,
  `gaps`), runtime meta `index_coverage`, and an `INDEX_COVERAGE_GAP` problem when a gap exists.
- `memory::coverage::verify(p, db)` checks the whole live index against the tree (G5 / governance-suite check) —
  **integration point IP-2** (WS-2 wires it into the scheduler/audit; WS-1 maps it).

**Probes re-run** (audit-of-record probes, unedited; full lines in `evidence/PROBE-BEFORE-AFTER.txt`)

| Probe | Before (base) | After (`2f4ee57`) | Lines turned |
|---|---|---|---|
| C3-semantic-memory | 11 P / 3 F | 14 P / 0 F | `C3-b5-lists` FAIL→PASS (plus the two BC-P2-26 lines) |
| C4-lexical-memory | 21 P / 13 F | 33 P / 1 F | `C4-b5a-*`, `C4-b6l-*`, `C4-b6s-lexical`, `C4-cov-q1-*`, `C4-cov-q2-*`, `C4-coverage` FAIL→PASS; `C4-exactness` stays FAIL (see §7) |
| C7-episodic-memory | 6 P / 1 F | 7 P / 0 F | `C7-b6-discovery-indexed` FAIL→PASS |
| D3-hierarchical-retrieval | 4 P / 1 F | 5 P / 0 F | `D3-b2-chunks` FAIL→PASS |

**Tests added** (lib, regression): `memory::chunking::tests::every_non_empty_code_line_is_held_by_a_chunk`,
`methods_are_child_units_and_long_units_keep_every_line`, `record_sections_hold_list_and_nested_content`.

## 2. BC-P2-26 — Retrieval filtering, routing, de-duplication — REPAIRED_CLAIMED

**Requirement** (repair-delta §1; Contract v3:241, :246, :291, :316-321; framework §14): authority and namespace filters
apply before candidate truncation and before any plugin receives candidate text; filename-shaped queries reach a route
that resolves file names; dependency/impact questions (including code entities) deliver graph answers; content-level
duplicates are suppressed across artefacts.

**What changed** (`retrieval/mod.rs`)
- **Admission first.** `Admission::new` decides, once per query and before any route runs, which artefacts the query may
  return: the record-type filter, the namespace/role filter (`MEMORY_POLICY.namespaces[*].roles` via `authority::role_in`)
  and the authority filter (`AUTHORITY_POLICY.retrieval_default_excludes_statuses`, superseded, `default_retrieval=0`).
  Every route keeps only admitted candidates *before* it cuts its pool (`admit_ranked`); the lexical route streams FTS
  results in rank order until the pool holds `pool` admitted rows, so excluded near-duplicates cannot exhaust it. The
  reranker receives only fused, admitted candidates. `excluded_by_authority`/`excluded_by_namespace` count exclusions
  inside each route's unfiltered window.
- **Routing.** Bare file names (`runbook.md`, `ledger.rs`, also inside sentences) reach the path route (base-name
  lookup, shortest path first) and the lexical route; a dependency/impact question whose words name code entities
  (symbols or files of the index) reaches the graph route; URL paths and table/model names in a question are answered
  from the code-structural store (route and DB-model symbols → handler/model unit).
- **Primary route.** When a question has one direct answer route — an exact ID, path, file name or symbol lookup, or a
  dependency/impact question — that route's answers form the first tier (in its own order), fused candidates follow
  (also re-applied after a reranker). For the graph route the tier is its *answers* (a code entity's callers at the
  calling unit and subtypes/implementers, same file included; then the impact set of the defining artefacts or named
  IDs by distance); its remaining neighbourhood is context fused normally.
- **De-duplication.** Besides the two-slices-per-artefact cap: a file artefact whose content hash equals one already
  answering (a verbatim copy under another path) is withheld, and a slice whose normalised text (title/path line aside,
  ≥40 characters) equals one already returned from another artefact is withheld; both are reported in
  `duplicates_suppressed`. Context compilation uses `retrieve` and inherits all of this.
- New result fields: `primary_route`, `duplicates_suppressed`, `evidence_coverage`, `failure_record`.

**Product check that owns it:** the retrieval pipeline itself (every `gov memory query`, context compile, CIT-P candidate
list) and the held-out regression family (`verification` `memory_retrieval_regression`, `gov memory verify`, G5) that
measures it; the result's `excluded_by_*`, `primary_route` and `duplicates_suppressed` make each decision observable.
Mapping into the evidence map is **IP-1** (WS-1).

**Probes re-run**

| Probe | Before | After | Lines turned |
|---|---|---|---|
| C3-semantic-memory | 11 P / 3 F | 14 P / 0 F | `C3-b7-filter-before-truncation`, `C3-b7-no-excluded-text-to-plugin` FAIL→PASS |
| C4-lexical-memory | 21 P / 13 F | 33 P / 1 F | `C4-b3-router`, `C4-b3b-router` FAIL→PASS |
| D2-retrieval-router | 5 P / 4 F | 9 P / 0 F | `D2-b3-filename`, `D2-b4`, `D2-b4-code` FAIL→PASS; `D2-b1-rank1` (A0-D2-01, LOW, unclassed) FAIL→PASS as a consequence of the primary tier |
| C9-context-packet | 8 P / 2 F | 9 P / 1 F | `C9-b6-content-dups` FAIL→PASS; `C9-b3-policy-fields` (A0-C9-02, INFO, WS-4 packet field) unchanged |

Supplementary (my own, `evidence/SUPP-ws06-behaviours.py`): `S5-slice-dedup` (identical rationale in two different
records returned once, suppression reported), `S6-lexical-admission` (40 superseded near-duplicates cannot starve the
ACTIVE record on the lexical route alone at k=3) — PASS.

**Tests added:** `retrieval::tests::bare_file_names_reach_the_path_route`.

## 3. BC-P2-27 — Code-structural extraction — REPAIRED_CLAIMED

**Requirement** (repair-delta §1; Contract v3:251-259; framework §11.5): route registrations, database models and
inheritance/implementation relations are represented for the languages in scope; extraction is AST/LSP/SCIP-equivalent
(no symbols from comments/strings); test→code relationships exist for standard layouts; adapters resolved via the
capability registry.

**What changed**
- `generic::blank_non_code` lexes each file per language family (hash-comment languages incl. Python triple quotes and
  Ruby `=begin`; shell word-start `#`; C-like `//`, nested `/* */`, char literals vs Rust lifetimes, Rust raw strings,
  Go/JS backticks, Kotlin/Scala/C# triple quotes, C# verbatim strings; SQL) and replaces comment and literal contents
  byte-for-byte with spaces (positions and lines preserved; a literal spanning lines has its closer blanked too, so a
  continuation line never reads as code). Symbols, unit spans (braces/indentation), calls, relations, routes and models
  are read from the blanked code; string values (route paths, table names, import targets) are read from the original at
  positions the lexer classified as code. A `class`/`def`/`fn` in a docstring, comment or string is never a symbol and a
  brace in a string never moves a unit's end.
- Structure (`generic::structure`): **inheritance/implementation** — Python bases (keyword args excluded), JS/TS
  `extends`/`implements`, interface `extends`, Java `extends`/`implements`, Kotlin (after primary-constructor params),
  C#, Swift, Scala `extends … with`, C++ base lists, Rust `impl Trait for Type` and supertraits, Ruby `<` and
  `include`, Go struct/interface embedding; **routes** — decorator form (Flask/FastAPI/Sanic/Litestar), annotation form
  (Spring `@*Mapping`, NestJS, JAX-RS), Rust `#[get(..)]`, ASP.NET attributes and minimal APIs, call registrations with a
  handler (Express/Koa/Fastify, Go `HandleFunc`/gin/echo/chi, axum `.route`), Django `path()`, Rails/Sinatra verbs —
  HTTP-client calls (`requests.get("/x")`, `client.get`) and bare lookups (`cache.get("/x")`) are not routes; **DB
  models** — table declarations, column/field definitions, entity annotations/attributes, ORM derives, Go ORM tags and
  embedded `gorm.Model`, qualified ORM bases, call-registered models.
- Storage (indexer): routes as symbols `kind=route` (`name` = path, `parent` = handler) and `symbol_refs kind=route`;
  models as symbols `kind=db_model` (`parent` = class, signature carries table/evidence); relations as `symbol_refs kind
  inherits|implements`, resolved over the whole index to `DEPENDS_ON` (provenance `inherits:<Base>`) and `IMPLEMENTS`
  edges between files.
- Python AST adapter emits `relations`, `routes`, `models` from the AST (decorator calls, bases, `__tablename__`, Column,
  Django fields, qualified ORM bases). A registered adapter whose output lacks those keys is completed from the builtin
  for those facts only, and its provider string says so. Adapters are still resolved through the capability registry
  (`code_intelligence::analyze` → `capabilities::host::find`); nothing language-specific is spawned by the core.
- Test→code: `is_test_path` (test directories and ecosystem test-file naming) in addition to path class `test`;
  `ImportResolver` resolves Python packages anywhere in the tree by suffix (src-layouts; best match by shared directory),
  relative imports, Rust `crate::`/`self::`/`super::` and other crates of the tree by `Cargo.toml` package name, Go module
  paths, C/C++ includes; TESTS edges from resolved imports, from calls into non-test files, and for Go `_test.go` files
  to their package's files (provenance `tests:import|call|package`).

**Product check that owns it:** extraction runs on every index mutation (rebuild, G1-equivalent); the facts are
observable in `symbols`/`symbol_refs`/`edges` and through retrieval (graph answers for "what implements X", structural
answers for routes and tables). No dedicated scheduler check exists yet — **IP-1/IP-2**.

**Probes re-run**

| Probe | Before | After | Lines turned |
|---|---|---|---|
| C5-code-structural-memory | 7 P / 4 F | 10 P / 1 F | `C5-b3-inheritance`, `C5-b5`, `C5-b6`, `C5-b7-tests-dir` FAIL→PASS; **`C5-b1` PASS→FAIL by design** (below) |

`C5-b1` asserts `"NotARealClass" in trap_builtin` — i.e. that the *builtin extractor reads a class inside a docstring*
("builtin extractor is heuristic … the AST adapter is exact"). That observation was the defect A0-C5-02 names and the
requirement forbids ("no symbols from comments/strings"). The builtin now returns `real_function` only for the trap
file, as the AST adapter does; the line fails because its expectation encoded the defect. The verifier should read this
line as evidence *for* the repair, not as a regression.

Supplementary: `S7-java-model`, `S7-java-route`, `S7-java-inheritance-edge`, `S7-kotlin`, `S7-go-package-test`,
`S7-no-phantoms` — PASS.

**Tests added:** `code_intelligence::generic::tests::no_symbols_from_comments_or_strings`,
`blanking_preserves_positions_and_lines`, `inheritance_routes_and_models_across_languages` (Python, TypeScript, Rust,
Go, Java), `trait_method_declarations_are_single_line_units`; `memory::indexer::tests::test_paths_by_convention`,
`import_resolution_covers_src_layouts_and_crates`; `capabilities/tests/test_plugins.py` still 4/4.

## 4. BC-P2-29 — Incremental index invalidation — REPAIRED_CLAIMED

**Requirement** (repair-delta §1; Contract v3:308-313, :634-636, :888): incremental indexing invalidates derived facts
in other artefacts that depend on a changed artefact (incremental equals full); a path-map or classification change
re-derives every affected artefact before freshness reports fresh; CIT-E refreshes and verifies under the post-mutation
policy and path map and rolls back when the result is incompatible.

**What changed**
- **Current policy.** `indexer::rebuild` and `manifest::freshness` evaluate a fresh project view (`current_view`: policy
  set, overlay, path map, secret scanner re-read from disk; same root/session/role). CIT-E calls `rebuild` and
  `freshness` after applying its manifest, so its refresh and its `index_freshness` verification now run under the
  post-mutation policy/path map; a refresh that cannot be built (e.g. an unavailable pinned embedder) returns a typed
  error, and CIT-E rolls back. No edit to `cit/mod.rs` was needed.
- **Derivation keys.** `DerivationContext::key` hashes, per artefact, everything outside its content that shapes its
  rows: path-map decision (class, namespace, sensitivity, default retrieval, never-index, the four index flags), the
  code-intelligence adapter identity for its language (`plugin_id@version#pin` or the builtin extractor version), and the
  authority state-class mapping for record files. Keys are stored (`derivation` table) and written into each manifest
  entry. An incremental build re-derives an unchanged-content file whose key changed (`IndexReport.rederived`);
  `freshness` lists such files in `stale` and `reclassified`, so it is never green while an entry keeps its old
  classification. An entry no longer indexable under the current path map is `removed` (and is deleted by the next
  incremental build).
- **Global cross-artefact facts.** `derive_cross_artifact_facts` runs after every build, full or incremental: import
  resolution for every file (tree-based, no filesystem probing), `IMPORTS`, `CALLS`, `TESTS` and inheritance/
  implementation edges, `superseded_by` (own field, else first superseder in path order) and supersession conflicts. A
  fact owned by an unchanged file that depends on a changed one is therefore recomputed. Exclusions that no longer apply
  are removed from the `excluded` table in incremental mode. A *relative* import whose target is not in the tree stays
  an `IMPORTS` edge to the path it names, so graph integrity reports it as dangling in incremental and full builds alike
  (previously it existed only as a stale incremental artefact).

**Product check that owns it:** `memory::manifest::freshness` — task close (G2: `INDEX_STALE` refusal per
`MEMORY_POLICY.freshness.on_stale_close`), `gov memory freshness`, `gov status`, doctor, CIT-E `index_freshness`
verification and the audit `index_freshness` family (G5).

**Probes re-run**

| Probe | Before | After | Lines turned |
|---|---|---|---|
| D1-incremental-freshness | 8 P / 3 F | 11 P / 0 F | `D1-b2-dependants`, `D1-pathmap-freshness`, `D1-pathmap-incremental` FAIL→PASS |
| X-K2-D1-W6-interactions | 3 P / 2 F | 5 P / 0 F | `K2-D1-2` (failed refresh inside CIT-E → ROLLED_BACK, index usable), `K2-D1-3` (CIT-E path-map change reflected, no archive-as-current) FAIL→PASS |
| C2-relationship-graph | 7 P / 3 F (record) | 7 P / 3 F | identical to the audit of record — see note |

Note on `C2-b2-stale-dangling`: that line's setup (rename a relatively imported file, rebuild incrementally, look for the
stale edge) relied on the stale edge BC-P2-29 removes. With the global derivation alone the line would flip to FAIL
while the detector was intact; representing the broken relative import as an edge to the path it names keeps the break
visible in both build modes, and the line stays PASS for the right reason (`S8-dangling`).

Supplementary: `S1-register-stale`, `S1-register-equal`, `S1-remove` (registering/removing a `code_intel` adapter marks
the covered files stale, the incremental build re-derives them and equals a full build), `S8-dangling` — PASS.

**Tests added:** `memory::indexer::tests::import_resolution_covers_src_layouts_and_crates`.

## 5. BC-P2-32 — Durable failure memory — REPAIRED_CLAIMED

**Requirement** (repair-delta §1; framework §11.8, §18; Contract v3:276-283): retrieval misses and tool failures
produce durable, structured, kind-distinguishable records that survive memory rebuilds and link to the follow-up.

**What changed** (`memory/failures.rs`, producers in `indexer.rs` and `retrieval/mod.rs`)
- Record type `failure`, id `FAIL-nnnn`, `failure_kind` ∈ {bug, failed-approach, incorrect-assumption, retrieval-miss,
  regression, migration-failure, tool-failure}, `signature` (kind + what failed), `summary`, `detected_by`
  {operation, detection automatic|reported, session, role}, structured `subject`, `root_cause_candidates`, and
  `follow_up` {status open|linked, required_actions, task, heldout_query}. One record per signature; a repeat reports
  `existing`. Free text is sanitised (project-root paths removed; secret-scanner matches redacted). Every write goes
  through `control::guard_write` (FREEZE_WRITES, PAUSE, recovery-only, kernel trust) and `records::save_record` (the §6
  record-write sink); a refused write is reported `not_recorded` with the reason and never fails the observing
  operation.
- **Tool failures** → `spec/reports/failures/` (indexed evidence, recallable through the fabric): code-intelligence
  adapter failures/unusable output (grouped per adapter and error code with the affected paths), embedder
  resolution/bad-output failures, reranker resolution/invocation failures — observed by `rebuild` (a build that writes a
  new record indexes it in the same call, so the index stays fresh) and by `retrieve`.
- **Retrieval misses** → `spec/reports/memory-quality/` — memory-quality events, **never indexed** (the indexer and
  `freshness` skip the directory), like the held-out set: a record of a missed question must not answer that question,
  and recording one must not move the index a context packet was compiled against. For an agent's logged query
  (`RetrieveOptions.log`: `gov memory query`, context compile) with no exact-route answer, the product computes the
  IDF-weighted share of the question's terms held by the best returned artefact (framework §17 "retrieval-to-answer
  evidence coverage"); below 0.5 (or no hit) it records a miss with the measurements, the terms the index holds nowhere
  and the exclusions.
- Follow-up: `link_follow_up(p, id, task, heldout_query)` and `open_failures(p)` for BC-P2-24 work generation (IP-4);
  `record_heldout_misses` for producers that persist held-out regression results (IP-2); `record_tool_failure` for tool
  health checks (IP-3).

**Product check that owns it:** the producers above run on every index mutation (G1-equivalent) and every logged query;
reporting open failures in health/doctor and generating work from them are **IP-2/IP-4**.

**Probes re-run**

| Probe | Before | After | Lines turned |
|---|---|---|---|
| C8-failure-memory | 6 P / 2 F | 8 P / 0 F | `C8-b4-adhoc` (spec/reports/memory-quality/FAIL-0001.yaml), `C8-b7` (adapter crash and embedder bad output recorded under spec/reports/failures/) FAIL→PASS |

Supplementary: `S2-recorded`, `S2-not-indexed-fresh` (manifest hash unchanged, index fresh), `S2-packet-stable` (a
compiled packet's hash is unchanged by a recorded miss), `S2-dedup`, `S2-survives-rebuild`, `S3-frozen` (under
FREEZE_WRITES nothing is written, the outcome says `not_recorded`, the query still answers), `S4-recall` (a tool-failure
record is recalled by a query; the index is fresh after the failing build) — PASS.

**Tests added:** `memory::failures::tests::failure_kinds_signatures_and_locations`.

## 6. Regression and preservation (all at work commit `2f4ee57`)

| Suite | Result | Baseline | Evidence |
|---|---|---|---|
| `cargo test --lib` | **53 passed / 0 failed** | 42 (11 new tests, none changed) | `evidence/REG-cargo-test-lib.out` |
| `cargo test --test certification` | **79 passed / 0 failed** (incl. `section6::*`, `arch::*`) | 79 | `evidence/REG-cargo-test-certification.out` |
| capability plugin tests (pytest) | 4 passed | 4 | `evidence/REG-capabilities-python-plugins.out` |
| beta-r probes outside my classes (12 probes) | PASS/FAIL lines **identical** to the audit of record | audit of record | `evidence/after-other/`, `evidence/PROBE-BEFORE-AFTER.txt` |
| R1 AR-0027 (`4.1.6-r1`) | **26 passed / 3 failed** (`b1`, `b2`, `d3`) | 26 / 3, same tests | `evidence/R1-HELDOUT-RERUN.out` |
| R1 AR-0029 (`4.1.6-r1-2`) | **26 passed / 2 failed** of 28 compiled (`b3`, `b6`); `ho_f_preservation` does not compile (`AuthenticatedRelease` private fields) | same | same |
| R1 AR-0031 (`4.1.6-r1-3`) | **27 passed / 7 failed** (`a1`, `a5`, `a8`, `b6`, `c2`, `c3`, `d2`) | same | same |
| R1 AR-0033 (`4.1.6-r1-4`) | **30 passed / 1 failed** (`hv_a::a1`) | 31 / 0 | same + `evidence/R1-hv_a-a1-analysis.out` |

`records.rs` (the record-write sink file) is touched, so all four R1 suites were re-run: copied byte-identically
(`cmp` in the output), the worktree exposed at the `../wt/<name>` paths their `Cargo.toml` files expect by symlink,
each test binary single-threaded, `AR0033_GOV_BIN` = this worktree's release `gov` (`evidence/RERUN-r1-heldout.sh`).
AR-0027/0029/0031 match their recorded baselines test for test. **The one deviation is `hv_a::a1`**, which fails at its
first assertion `assert_eq!(files.len(), 84, "the product tree is not the size the census claims")`: the test pins the
product's size (84 files / 740 functions); this work adds two modules (86 files, 811 functions). Its §6 census, which
that assertion prevents from running, was run as a clearly-labelled derived copy with only the two scale assertions
removed (`evidence/R1-hv_a-a1-census-variant.rs.txt`): **0 violations** in every §6 activity (human_gate_create derived
37 / writers 34 / exempt 1 / violations 0; the other six activities 0 violations). The product's own derivation
(`tests/certification/section6.rs`) is green. The new writers (`failures::record`, `failures::link_follow_up`) persist
through `save_record` and conform. Every Phase-2 repair that adds a file will trip this pin; re-establishing R1 for the
integrated candidate is the AC-14 verifier's call.

## 7. Limits — what this work does not do

- **Extraction fidelity.** The builtin extractor is lexer-level: it never reads code structure from comments or string
  literals, but it is not a type-checked AST/LSP/SCIP. Names are resolved by the index (same file → imports → repository);
  Go interface satisfaction and dynamically registered routes are not claimed; route/model recognition covers the
  framework idioms listed in §3 (others fall back to plain symbols); JavaScript regex literals, C++ raw strings and shell
  heredocs are not lexed. The Python AST adapter (optional plugin) gives AST fidelity for Python; no LSP/SCIP adapter
  ships. Whether "lexer-level with no symbols from comments/strings" satisfies "AST/LSP/SCIP-equivalent" is for the
  verifier.
- **Miss detection is a measurement, not an oracle.** Low IDF-weighted artefact coverage flags vocabulary-mismatch
  paraphrases as misses (false positives are memory-quality events, cheap and unindexed) and cannot see a confidently
  wrong answer that shares the question's words. Context-compile queries are built from the task's own title/objective and
  usually match the task record itself, so compile-time misses are rarely detected.
- **Role-dependent adapter identity.** The derivation key uses the code-intelligence adapter usable *for the acting
  role* (the adapter the build actually runs). A role-restricted `code_intel` plugin therefore makes freshness differ by
  role — a pre-existing role dependence of indexing that the key now makes visible. Plugin authorisation belongs to WS-7.
- **Not addressed (not in my classes):** A0-C4-02 (identifier-shaped literals matched by OR-of-subtokens; `C4-exactness`
  still FAIL, LOW, unclassed); A0-C9-02 (packet field `semantic_candidates`, INFO, context packet = WS-4).
- **Round 2, not started:** BC-P2-28 (graph integrity; note §4: broken relative imports are now dangling edges),
  BC-P2-30, BC-P2-31.
- **Kernel policy knobs.** `MEMORY_POLICY.failure_memory.retrieval_miss.enabled` (default true),
  `.retrieval_miss.min_evidence_coverage` (0.5) and `.tool_failures` (true) are read with code defaults but not declared
  in `MEMORY_POLICY.yaml`: declaring them requires `ENFORCEMENT_MAP.yaml` entries (WS-3) or the
  `policy_enforcement_coverage` family fails (verified: declaring them turned `C8-b5`'s baseline audit UNHEALTHY) — IP-6.
- **Path map.** `spec/reports/memory-quality/**` is excluded by the product (indexer + freshness), not yet declared in
  the `REPOSITORY_CONTRACT` overlay template: a template change requires an overlay operation in the migration into the
  current version (`migrations/**`, WS-9; verified: `repair2::interface_contract_kernel_yaml_and_migration_substance_are_consistent`
  fails without one) — IP-7.
- No CLI surface added (`gov memory miss` / `gov memory failures` would need `cli/src/main.rs` additions after WS-3's
  role-resolution change and a command-contract authority class) — IP-6.

## 8. Integration points (for the owners and later rounds)

| ID | Owner | File / function | Call to add | Why |
|---|---|---|---|---|
| IP-1 | WS-1 | `tests/governance/capability-evidence-map.yaml` | Evidence owners: C3/C4/D3 → rebuild coverage (`IndexReport.coverage`, meta `index_coverage`) + `memory::coverage::verify`; C3/C4/C9/D2 → retrieval admission/routing/dedup observed by `memory_retrieval_regression`; C5 → code-structural facts (symbols `kind=route|db_model`, `symbol_refs kind=inherits|implements`, `TESTS` edges); D1 → `manifest::freshness` (`reclassified`, derivation keys); C8 → `memory::failures` producers and `open_failures` | AC-10: every class's check must appear in the map |
| IP-2 | WS-2 | new scheduler / `verification/mod.rs` / `doctor.rs` | `crate::memory::coverage::verify(p, &db)?` as check `index_content_coverage` (G1 after index mutation, G5 full audit; `complete=false` → DEGRADED); `crate::memory::failures::record_heldout_misses(p, &regression, "audit")` when the `memory_retrieval_regression` family *persists* a failing result (never under `--no-persist`); report `crate::memory::failures::open_failures(p).len()` in doctor/health | Owns the tier duties; keeps `--no-persist` side-effect free |
| IP-3 | WS-7 | `runtime/src/tools.rs` `health()` (and plugin health in `capabilities/**`) | For each failing check: `crate::memory::failures::record_tool_failure(p, &crate::memory::failures::ToolFailure { tool_kind: "tool".into(), tool_id, version, code: "TOOL_HEALTH_FAILED".into(), message, operation: "tools health".into(), affected: vec![] }, true)` | C8 "tool failures" for registered tools (probe C8-b7's third case) |
| IP-4 | WS-5 | work-generation engine (BC-P2-24) | Consume `crate::memory::failures::open_failures(p)`; after creating the linked task call `crate::memory::failures::link_follow_up(p, &id, Some(&task_id), None)` | "link to the follow-up"; §18 repair loop |
| IP-5 | WS-4 | `runtime/src/records.rs` (`TYPE_DIR`, `TYPE_PREFIX`); canonical-location checks | Register `("failure", "spec/reports/failures")` and prefix `("failure", "FAIL")`; accept `spec/reports/memory-quality/` as the canonical location of `failure_kind: retrieval-miss` records. Optional: context compile may exclude the task's own record from retrieved evidence so compile-time misses become observable. Note: CIT-E `graph_integrity` verification now also sees a broken relative import as a new dangling edge (a CIT that breaks one rolls back) | Records outside canonical locations are reported (BC-P2-21) |
| IP-6 | WS-3 | `framework/policies/ENFORCEMENT_MAP.yaml`, `MEMORY_POLICY.yaml`, `cli/src/main.rs` | If the knobs are declared: `MEMORY_POLICY.failure_memory.retrieval_miss.enabled` and `.min_evidence_coverage: {enforced_by: [retrieval::retrieve]}`, `MEMORY_POLICY.failure_memory.tool_failures: {enforced_by: [failures::record_tool_failure]}`. CLI (optional): `gov memory miss --query Q --expected REF…` → `failures::record(p, failures::retrieval_miss_event(q, &expected, detail, causes, "memory miss", "reported"), false)`; `gov memory failures` → `failures::open_failures(p)` | Policy coverage family; agent-reported misses (§18) |
| IP-7 | WS-9 (+ release) | `framework/overlay-templates/REPOSITORY_CONTRACT.yaml` + the migration into the current version | Rule after `spec/**`: `pattern: "spec/reports/memory-quality/**"`, `class: evidence`, all four index flags `false`, `namespace: spec`, with the migration's overlay operation | The path map should state what the product enforces |
| IP-8 | WS-2 (BC-P2-03) | evidence currency key | Include the index manifest (now carrying per-artefact derivation keys) among the inputs of memory/index evidence | A reclassification or adapter change then also stales green evidence |

## 9. Owner-decision questions

None. Every change stays inside ARCH-0001/ARCH-0003 and the active decisions: no trust boundary, no new external
dependency class, no language runtime in the core, no owner-controlled material touched.

## 10. Evidence index (`evidence/`)

`before/` (named probes on the base), `after/` (named probes at `2f4ee57`), `after-other/` (the other 12 beta-r probes),
`PROBE-BEFORE-AFTER.txt` (line-by-line table), `SUPP-ws06-behaviours.py` + `.out` (19 supplementary checks, regression
evidence only), `REG-cargo-test-lib.out`, `REG-cargo-test-certification.out`, `REG-capabilities-python-plugins.out`,
`R1-HELDOUT-RERUN.out`, `R1-hv_a-a1-analysis.out`, `R1-hv_a-a1-census-variant.rs.txt`, `RERUN-ws06-probes.sh`,
`RERUN-r1-heldout.sh`, `BUILD-base-release.log`. Probe outputs contain absolute scratch paths of this run.
