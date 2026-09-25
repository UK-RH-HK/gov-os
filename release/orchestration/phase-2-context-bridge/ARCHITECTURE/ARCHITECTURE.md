# Governance OS self-memory/context bridge: architecture (BR-AR-0001)

| Field | Value |
|---|---|
| Record | Architecture design produced by run **BR-AR-0001** (fresh Context/Retrieval Architect), lifecycle `P2X-FAIL-1-BRIDGE` |
| Class | `ORCHESTRATION_RECORD`: a design. **It is not an authority source**, it does not amend any owner record, and nothing a builder derives from it becomes authority. |
| Governing inputs | OD-P2-10 §3–§12, OD-P2-10A/B, OWNER-LAUNCHER-BR-0001, **OC-BR-02** (corpus and purpose), BR-HO-0001 and its addendum BR-HO-0001-A1 (which governs where they differ), `ORCHESTRATOR_STATE.yaml → mandatory_bridge_inputs` |
| Refs read | records at bridge base `6e7a2a3` (and bridge tip `72f648d`), frozen product `3c880d8`, Review-8 evidence `58219d5`, all 95 `phase2/*` branch tips |
| Evidence | Every measured number below cites a spike output `SO-NN` = `ARCHITECTURE/spike-outputs/NN-*.out`, whose command, exit code and sha256 are in `AGENT_RUNS/BR-AR-0001.checkpoint.yaml`. Spike scripts are in `ARCHITECTURE/spike-scripts/`. They are **spikes, not bridge code**. |
| Companion files | `REUSE_VS_BUILD.yaml`, `IMPLEMENTATION_DAG.yaml`, `SEMANTIC_ROUTE.md`, `DEMONSTRATION_DESIGN.md`, `demonstration-queries.yaml`, `schemas/*.yaml` |

## 0. What this is, in one page

**Purpose (OC-BR-02).** This is a **generic, provider/model-replaceable, whole-repository Governance OS self-memory and
context foundation.** It lets a fresh agent get complete *relevant* context: why a mechanism exists, what requires it,
which decisions constrain it, what it depends on, what depends on it, which approaches already failed, and where the
enforcement decision is actually made. The agent should not have to read the repository or rely on chat. It is
orchestration support only (OD-P2-10 §3), and it is designed so that it can be promoted into V8.3 (§10) and qualified
by Phase 3 (OD-P2-10 §10).

**The design test (BR-HO-0001-A1).** *If every Review-8 reference were deleted from this document, would the
architecture change?* No. Review 8 appears only as **data and evidence**:

* the demonstration query set and the oracle's examples;
* the canonical-view configuration that names today's refs;
* the registry seed entries for this lifecycle's mandatory inputs;
* the architect's measurement tables (§4.6, §5.2), which record what was verified.

No component's logic, no rule and no schema field depends on F1–F6, on a Phase-2 file name or on a Review-8 symbol.
Delete them and only data changes.

**The shape.** Git is the only source of truth. The bridge reads **Git objects**, never working trees. It builds one
content-addressed store keyed by blob id: whatever number of refs are indexed, a blob is chunked, embedded and parsed
once. Over that store run six **routes**: structured, exact, lexical, semantic, graph and code. A deterministic
**authority/lifecycle classifier** labels every record *before* any ranking happens. A deterministic
**mandatory-input resolver** is the **only** source of packet section A. A **context compiler** assembles bounded
packets A–J, each with an exact manifest and a hash. A worker returns a **consumption receipt**, which is checked
mechanically. No step invokes an LLM. Every replaceable component (embedder, code intelligence) is a
**`gov-capability/1` plugin**, the product's own D-0006 protocol, so that it can be swapped without redesign.

**Why this is the minimum.** Each component maps to a line of Contract v3 Gates C, D and W. Those gates are the
product's own statement of what a knowledge fabric, retrieval and artefact flow must do (§11). The bridge builds the
smallest faithful instance of them as orchestration tooling, and reuses the product's vocabulary: W1 identity fields,
W3 manifest fields, W5 receipt fields, and `MEMORY_POLICY` retrieval parameters. **Phase 3 can then qualify it against
the gates it will eventually be held to**, instead of against a bespoke rubric.

### 0.1 What exists today, and whether it runs (full table: `REUSE_VS_BUILD.yaml → inventory`)

| Primitive | Operational? | Evidence |
|---|---|---|
| `phase-2/tools/worker_bootstrap.py` (canonical bootstrap compiler) | **Runs.** It compiles a ~5.6k-token brief, but its "where you are" block is hard-coded and stale (it prints `cap2-candidate-1` and `GATE-P2-REPAIR-2`). | SO-01 |
| `phase-2/tools/product_identity.py` | **Runs.** Recomputes `f6b1b886…d8ef` for `3c880d8`. | SO-01 |
| `phase-2/tools/check_state.py show` | **Runs.** It shows stale keys (`running P2-AR-0092 … RUNNING`) while `lifecycle_state` is FROZEN, which is itself evidence that state keys have different freshness. | SO-01 |
| `phase-2/tools/prep_packet.py`, `api_worker.py` | **Not usable by the bridge.** Both write into `release/orchestration/phase-2/packets/` (`prep_packet.py:58,93`), and API workers are paused. | SO-01 |
| `phase-2/tools/telemetry_context_extract.py` | **Runs only on one old session's task outputs.** The paths and run IDs are hard-coded. | file:2-3 |
| `capabilities/` D-0006 plugin protocol (`gov-capability/1`) | **Runs**, and is identical at `6e7a2a3` and `3c880d8` (tree `bfac2954`). The hashed-ngram `embed` plugin answers. | SO-02 |
| `capabilities/…/embed_sentence_transformers.py` | **Not operational.** It fails closed with `MODEL_UNAVAILABLE`; no torch, onnxruntime, sentence-transformers, fastembed or tokenizers is installed. | SO-02 |
| `capabilities/…/code_intel_python_ast.py` | **Runs** (stdlib AST). It handles Python only. | SO-02 |
| Product memory/retrieval/context engine at `3c880d8` (`runtime/src/{memory,retrieval,context,graph,code_intelligence}`, about 20k lines; `gov memory`, `gov context`) | **Not invocable without mutation.** See §0.2. | SO-03 |
| `framework/policies/{MEMORY,CONTEXT,ARCHIVE,SECURITY}_POLICY.yaml` | **Parameters, reused as data.** RRF k=60, chunk 1200/120, `never_index_classes`, `secret_path_patterns`, `secret_content_patterns`, `fresh_agent_read_budget_files: 25`, archive `default_retrieval: false`. | file:line in §1, §4 |
| `spec/decisions/*.yaml` metadata | **Carries status and supersession**: `status`, `supersedes`, `superseded_by`, `amends`, `in_effect`, `approval_state`. Owner records in `GATES/*.md` carry them only as free-text header rows, and not uniformly. | §5.2 |
| rust-analyzer / ctags / tree-sitter | None is installed; rust-analyzer is a rustup proxy without the component. tree-sitter wheels are installable. | SO-06 |

### 0.2 Why the bridge does not run the product's own memory engine

Calling a built binary would not change product code, so it would be permitted in principle. Four measured facts
rule it out:

1. **This repository is not an adopted project.** There is no `governance/framework.lock` at `6e7a2a3` or `3c880d8`,
   and `gov memory`/`gov context` call `open_project(cli, true)` → `require_installed()` (`cli/src/main.rs:1472-1481`).
   Making it one would mean running `gov init`, which writes `governance/` at the repository root. That is outside the
   bridge domain (SO-03).
2. **Running it would perturb the evidence under study.** `gov init` anywhere on this machine adds an entry to
   `~/.local/state/governance-os/machine/adoption-floors/`, which holds 44 entries today (SO-03). That is the store
   `union_last_known_rules_across_store` enumerates (`paths.rs:1453-1467`).
3. **It would be circular.** The product indexer classifies every file through `contract.decide(rel)`
   (`memory/indexer.rs:1395,1472`), which is the path-rule composition that the Review-8 synthesis must investigate.
   A tool used to examine a mechanism must not depend on that mechanism.
4. **It indexes one working tree.** The bridge corpus spans several refs (§1.2). No `gov` binary exists for
   `3c880d8` (`target/release/gov` was built on 2026-09-20; SO-03), and the product must not be built in its frozen
   worktree.

The product's **designs**, however, are reused deliberately: W1 identity, W3 manifest slots, W5 receipt fields,
`MEMORY_POLICY` parameters and the `gov-capability/1` protocol. The bridge is therefore *field-compatible* with the
product, and that is what makes promotion into V8.3 cheap (§10).

---

## 1. Corpus inclusion/exclusion rules

### 1.1 The rule file: `config/corpus-rules.yaml` (versioned; sha256 recorded in every build manifest)

The corpus is **every blob reachable from the canonical view's trees** (§1.2). It is read from the Git object
database, so untracked files are excluded *by construction*. They are not part of "the canonical repository", and
this is also why `.env` files, `target/` and `.claude/worktrees/` never appear unless someone commits them. The rules
below then apply to each tracked `(path, blob)`. Evaluation is **monotone**: any matching exclusion excludes, and
order never changes the outcome. **Repository path names are subjects only; they are never interpolated into a
pattern.** Every rule cites its source.

| Rule id | Effect | Matches | Source |
|---|---|---|---|
| `X-SEC-PATH` | excluded from every layer; the path is listed in coverage | `**/.env`, `**/.env.*`, `**/*.pem`, `**/*.key`, `**/id_rsa*`, `**/secrets/**`, `**/*secret*.{yaml,yml,json}`, `**/*credentials*`; plus `**/*.env`, `**/.secrets/**`, `**/deepseek*.env` | `framework/policies/SECURITY_POLICY.yaml:6-16` (`secret_path_patterns`; `never_index_classes: [secret, restricted]` at :4); `.gitignore:12-14` |
| `X-SEC-CONTENT` | excluded from every content layer; the path and blob id are listed; the content is never stored | blob text matches any `secret_content_patterns` regex | `SECURITY_POLICY.yaml:17-26`, `:27` (`on_secret_outside_secret_class: block_index_and_report`) |
| `X-BUILD` | excluded | `target/**`, `**/target/**`, `.claude/worktrees/**`, `**/__pycache__/**`, `**/*.pyc`, `**/.pytest_cache/**`, `**/.governance-runtime/**`, `build/**`, `dist/**`, `**/*.egg-info/**`, `release/evidence/tmp/**` | `.gitignore:1-9,15`; `MEMORY_POLICY.yaml:3` (`runtime_dir`) |
| `X-BINARY` | excluded from content layers; metadata (path, blob, size) is kept | NUL byte in the first 8000 bytes, or not valid UTF-8 | generic text test, the same shape as the product's `util::is_text_file` |
| `X-SELF` | excluded | the bridge's own derived outputs: `<domain>/{INDEX,COVERAGE,DEMONSTRATION,telemetry}/**`, `<domain>/ARCHITECTURE/spike-outputs/**`, `<domain>/ARCHITECTURE/spike-scripts/**`, `<domain>/tests/fixtures/**` | a memory system must not index its own packets, manifests and answers, or packets start retrieving old packets (a feedback loop). The bridge's design and orchestration records stay indexed; a task spec may add `retrieval_exclusions`, which the demonstration uses (DEMONSTRATION_DESIGN §2) |
| `M-LARGE` | **metadata-only**: exact retrieval by path still works; not chunked or embedded | text blob larger than 1 MiB | cost rule (OD-P2-10 §11). The 6 blobs caught total 26.3 MB of machine output (SO-04) |
| `M-ARCHIVE` | indexed, but `default_retrieval: false` | `archive/**` | `ARCHIVE_POLICY.yaml:8`; `MEMORY_POLICY.yaml:52` |
| `L-MACHINE-OUTPUT` | lexical and exact only, **not embedded** | kinds `out, log, shimlog, stderr, diff, patch, tsv, jsonl, summary`, and `json` larger than 64 KiB | cost rule: paraphrase recall over machine logs has little value, while the exact tokens in them (test names, error codes) are fully served by the lexical route. `config/embed-profile.yaml` |
| `INCLUDED` | every layer the kind admits | everything else | — |

`UNCLASSIFIED` exists as an outcome only if a rule is malformed or a blob cannot be read. The coverage node treats any
non-zero count as a failure. Every tracked file at every view ref appears in the coverage report **exactly once**,
with one outcome and the rule id that produced it.

**What this means on the real repository.** At `3c880d8`: 6,567 tracked files; 6,489 INCLUDED (75.4 MB of text,
1.29 M lines); 65 `X-SEC-CONTENT`; 2 `X-SEC-PATH`; 5 `X-BINARY`; 6 `M-LARGE` (SO-04, SO-05). The records ref
`6e7a2a3` has 6,585 files with 6,507 included (74.3 MB). **Named coverage cost.** The policy-faithful content rule
excludes 8 product files: `runtime/src/security/secrets.rs` and 7 `tests/certification/*.rs` files, including
`brownfield.rs`. They contain fake test keys that match the `aws-access-key` pattern (SO-05). They stay reachable
through the exact route as `(path, blob, excluded: X-SEC-CONTENT)`, and a packet that needs them says so, so that the
agent reads them directly. The bridge does **not** redact and index them. That would be the bridge deciding that
policy does not apply, and OC-BR-02 says to follow policy.

### 1.2 The canonical multi-ref model: what "the canonical repository" means at a ref

**Problem, measured.** The repository today is not one tree:

* the records ref (`release/4.1.6-rc1` = `6e7a2a3`) carries `runtime/` at the *candidate-1* state:
  `6e7a2a3:runtime` = `974ea126`, identical to `cap2-candidate-1` (`0bad524:runtime`), and last changed at `c38a406`;
* the frozen product `3c880d8` carries a *different* `runtime/` (`cda71d7c`), `probes/` (the AR88–AR94 review
  reports) and `telemetry/`. None of these exists at `6e7a2a3`. It also carries an *older copy* of
  `release/orchestration/phase-2/`, where `ORCHESTRATOR_STATE.yaml` is blob `136e825a`, not the records ref's `314605ba`;
* Review-8's probes exist only at `58219d5` (SO-22);
* failed approaches live on 95 `phase2/*` branch tips (SO-00, SO-22).

A naive single-ref index would return candidate-1 code as "the product", or an old `ORCHESTRATOR_STATE.yaml` as
current. The lexical spike shows the hazard concretely: the phrase query found
`release/orchestration/phase-2/telemetry/checkpoints/P2-AR-0069-f3.checkpoint.json` **only at `3c880d8`/`58219d5`**
(SO-16).

**Model.** A **canonical view** (`config/canonical-view.yaml`, schema `govbridge-canonical-view/1`) is data, not code:

```yaml
view_id: <name>
refs:                       # each resolves to exactly one commit per build; the manifest records it
  - {name: records,  ref: refs/heads/bridge/p2-context-retrieval, follow: tip,    role: primary}
  - {name: product,  ref: refs/heads/phase2/approved-delta,       follow: pinned, pinned_commit: 3c880d80…, role: product}
  - {name: evidence, ref: refs/heads/phase2/review-8,             follow: pinned, pinned_commit: 58219d56…, role: evidence}
  - {name: history,  ref_glob: refs/heads/phase2/*,               follow: tip,    role: history, layers: [exact, lexical, records, graph]}
partitions:                 # which ref OWNS (is canonical for) which paths; first matching partition wins; data only
  - {name: product,  paths_from: "release/orchestration/phase-2/tools/product_identity.py#PRODUCT_CODE", extra: [probes/**, telemetry/**],
     owner: product, fallback: [evidence, history]}
  - {name: records,  paths: ["**"], owner: records, fallback: [product, evidence, history]}
```

The `records` ref is the bridge branch. Outside the bridge domain it is byte-identical to `6e7a2a3`, because
`tools/check_state.py verify` enforces the mutation boundary, and inside the domain it carries the bridge's own owner
and orchestration records. The partition reuses `product_identity.py`'s `PRODUCT_CODE` list (`runtime, cli, tests, framework, capabilities,
migrations, tools, fixtures, bin, scripts, Cargo.toml, Cargo.lock`). That is the same line the Phase-2 identity digest
draws, so "what is product" is not re-decided here. In ordinary V8.3 operation the view is a single ref
(`{primary: HEAD}`, one partition `**`). Nothing in the code assumes more than one ref.

**Occurrences, not copies.** The store keeps `occurrence(ref, commit, path, blob, mode)` rows and indexes each blob
once. Every result is reported as the occurrence(s) it came from. Each occurrence gets a deterministic
**version status**:

| Version status | Rule |
|---|---|
| `CANONICAL` | the occurrence is at the owning ref for its partition |
| `CANONICAL_FALLBACK` | the path is absent at the owner, and this is the first fallback ref that has it |
| `SAME_AS_CANONICAL` | a non-owner occurrence whose blob equals the canonical blob; it is folded into the canonical result |
| `HISTORICAL_VERSION` | a non-owner occurrence whose blob **differs** from the canonical blob for the same path |
| `HISTORY_ONLY` | the path exists only at `history` refs |

"Current" is decided **per path by partition ownership**, never by retrieval score and never by commit date. A pinned
ref whose branch has moved is reported as `REF_MOVED`, and the build refuses to follow it silently. (The frozen
product must not drift under the bridge.) Measured cost of the multi-ref model: the three named refs share almost
everything, and the union is 5,787 unique included blobs, 77.3 MB, about 1.03× one ref. All 98 refs, including the 95
history tips, come to 6,501 blobs and 99.4 MB, about 1.3× one ref (SO-04, SO-14).

---

## 2. Document/chunk/record identity and provenance

Every addressable unit carries **its own Git identity**. Provenance is therefore a lookup, not a claim.

| Unit | Identity | Provenance carried |
|---|---|---|
| **Blob** | Git blob id (sha1, as Git stores it) plus `sha256(bytes)` | size, kind, corpus rule outcome |
| **Occurrence** (file at a ref) | `(ref_name, commit, path)` → blob | version status (§1.2); `git log -1 -- path` introducing/last-changing commit on demand |
| **Chunk** | `chunk_id = sha256(blob_id ‖ chunker_version ‖ start_line ‖ end_line)[:24]` | blob, line range, parent section id, `text_sha256` |
| **Section** (markdown heading block, or YAML top-level key) | `section_id = sha256(blob_id ‖ anchor ‖ start_line)[:24]`, where `anchor` is the heading text or key path | blob, line range, heading/key |
| **Record** (anything with an explicit ID) | the ID itself (`OD-P2-10A`, `D-0002`, `P2-L-0046`, `P2-AR-0097`); a record-local ID is qualified by its record, e.g. `P2-AR-0097#F2` | definition site (`record_def(id, occurrence, section, rule)`), plus the **nine W1 attributes** below |
| **Symbol** | `symbol_id = sha256(blob_id ‖ kind ‖ qualified_name ‖ start_line)[:24]`; a symbol is also addressable by `(commit, path, qualified_name)` | adapter id and version, grammar version, exact span |
| **Edge** | `(src, type, dst, derivation, evidence_occurrence, evidence_line)` | derivation label: `EXACT_*` or `HEURISTIC_*` (§6) |
| **Packet item** | `item_id = sha256(unit id ‖ section letter ‖ delivery)[:24]` | everything above, plus the query and route that produced it |

**Record identity follows Contract v3 W1** (lines 1068-1080) field for field. This is the vocabulary the product's
`graph/identity.rs` already implements: stable id; type; canonical path; authoritative status (§5 class); lifecycle
state (§5); version/content hash (blob plus sha256); producer/provenance (declared fields such as `approved_by`,
`provenance`, `author`, plus the introducing and last-changing commit); supersedes/superseded-by (§5.2); and expected
and actual consumers (graph in-edges).

**ID grammar** (`config/id-grammar.yaml`, versioned). This is an ordered set of patterns and **definition rules**:
YAML top-level `id:`; YAML list-item `- id:` inside registers; markdown header-table `| Id |` rows; markdown headings
that *start with* or *name* an ID followed by a severity, such as `### 2.1 AR94-C1 (HIGH)`; ledger headings
`## P2-L-NNNN`; and file stems. It also says which IDs are **local** (short tokens such as `F2` or `C1` that are only
unique inside the record that defines them). The spike census found 1,052 distinct IDs and 80,287 mentions across the
three named refs (SO-17). Definitions resolve for most run, handoff, ledger and owner-record IDs. Findings resolved
only 30/186 under the draft heading rule, which is why the grammar needs the "heading names an ID with a severity"
rule. Several IDs are defined more than once because `fixtures/` carries copies of records. Fixtures are class
`FIXTURE`, never a definition of authority (§5.2). An ID that is mentioned but never defined is **dangling**: it is
reported, and never guessed.

---

## 3. Incremental freshness/invalidation

**Change detection uses Git object ids only.** A build reads the view: for each ref, `git rev-parse`, and for globs,
`git for-each-ref`. It hashes `config/*` and the bridge code tree (`git rev-parse HEAD:<domain>/govbridge`). It
compares all of this with the last build manifest.

| Outcome | Condition | Work done | LLM calls |
|---|---|---|---|
| `NOOP` | every ref commit, config hash, code tree and component pin is equal | none: the previous manifest stands. Target under 1 s; about 10 `git rev-parse` calls | **0** |
| `INCREMENTAL` | some ref moved | `git diff-tree -r --no-renames old new` per moved ref gives the changed paths; only **new blobs** are chunked, parsed and embedded; removed occurrences are dropped; cross-artefact facts are recomputed (below) | **0** |
| `FULL` | a component pin changed (chunker, tokenizer, grammar, adapter, model, id-grammar or corpus-rules version), or `--from-clean` | everything is rebuilt; the old store is moved aside, never deleted in place | **0** |

**What each layer depends on.** A change to any listed input invalidates exactly that layer's rows:

| Layer | Keyed by | Invalidated by |
|---|---|---|
| occurrences | `(ref commit)` | the ref moving |
| chunks + FTS rows | `(blob, chunker_version, corpus-rules sha)` | a new blob; a rule change (→ FULL for that layer) |
| vectors | `(chunk text_sha256, model pin id, embed-profile sha)` | a new chunk text; a pin change (→ the whole semantic layer; **no mixed-embedder index**, the same rule as `memory/indexer.rs:3-4`) |
| symbols, calls, literals | `(blob, adapter id+version, grammar version)` | a new blob; an adapter or grammar change |
| records, sections, IDs, metadata | `(blob, id-grammar sha)` | a new blob; a grammar change |
| cross-artefact edges, lifecycle, supersession | **recomputed globally after every non-NOOP build** from the tables above plus `authority-registry.yaml` | anything. This is cheap, and it avoids stale derived facts; the product indexer uses the same rule (`memory/indexer.rs:17-20`) |
| packets | their manifest's item set | an item's blob changing under the view; re-compilation is deterministic (§7.6) |

**Rename, move and delete** fall out of the occurrence model. A moved file keeps its blob, so nothing is re-indexed,
and a record ID survives a move because it comes from content, not path (W1). A deleted file loses its occurrence.
Blobs with no occurrence in the view are garbage-collected deterministically at the end of a build.

---

## 4. The structured, exact, lexical, semantic, graph and code routes

All routes read the same store (§2). All return `RetrievedItem`s carrying the unit id, occurrence(s), version status,
the authority class and lifecycle **already assigned by §5**, the route name, the raw score and the rank. **No route
can create a `MandatoryItem`** (§5.3).

### 4.1 Structured current-state lookup: `govbridge state get <state-alias> <key.path>`

This reads a YAML state file (`ORCHESTRATOR_STATE.yaml`, `GATE-REGISTER.yaml`, `CHECKPOINTS/*.yaml`) **at the
canonical occurrence**, with the duplicate-key-refusing loader. That loader is `UniqueKeyLoader`, reused from the
bridge's own `tools/check_state.py`. It returns the value together with its **provenance**:

* `(path, commit, blob, key_path, line_start–line_end)`, using PyYAML node marks;
* **seal status**: `state_hash` is recomputed with the same `canonical_hash` rule as `check_state.py`, giving
  `SEAL_OK`, `SEAL_MISMATCH` or `UNSEALED`;
* the **last commit that changed those lines** (`git blame -L`) and its date.

The last point is deliberate. SO-01 shows `phase-2/check_state.py show` printing `running P2-AR-0092 … RUNNING` beside
`lifecycle PHASE_2_PRODUCT_FROZEN_AWAITING_BRIDGE`. State keys age independently. The lookup cannot know semantically
that a key is stale, so it shows *when each key last changed*. The agent, and the demonstration grader, can then see
which parts are live.

### 4.2 Exact route: `govbridge exact {show|grep|id|path}`

This is a thin, deterministic wrapper over Git, and is authoritative about Git content:

* `show <ref>:<path>[:L1-L2]` returns bytes, the blob and the sha256;
* `grep -F <literal> [--ref R] [--paths GLOB]` runs `git grep -n -F` at the resolved commit;
* `id <ID>` returns the definition site(s) and all mention sites;
* `path <suffix>` resolves a path suffix such as `init.rs` against the view, and reports ambiguity instead of picking
  one.

It honours the corpus rules. For an excluded path it returns the metadata and the rule id, never the content.

### 4.3 Lexical route: SQLite FTS5

This is one FTS5 table over chunks: `tokenize = "porter unicode61 tokenchars '_'"`, so snake_case identifiers stay
whole. `MEMORY_POLICY.lexical.tokenizer` is `porter unicode61` (`MEMORY_POLICY.yaml:15`); `tokenchars '_'` is the one deliberate addition, and
it is recorded in the manifest. BM25 does the ranking. Queries support phrases, `NEAR()` and column filters.
**Measured:** the three named refs give 5,787 unique blobs, 78,058 line-aligned chunks, **9.5 s build + 0.3 s
optimise**, a 147.5 MB database, and 5–6 ms per query (SO-15, SO-16). The history layer adds about 714 blobs.

### 4.4 Graph route

Traversal is over the edge table (§6): `impact`/`depends-on` BFS to a bounded depth, filtered by edge type, with the
derivation label carried on every hop. The default depth is `MEMORY_POLICY.retrieval.graph_neighbour_depth` (1); task
profiles may raise it to 3. Output is paths, and every hop cites its evidence line.

### 4.5 Semantic route (decision and pins: `SEMANTIC_ROUTE.md`)

No operational semantic route exists today (SO-02). The bridge provisions **one provisional** local model,
`BAAI/bge-small-en-v1.5` at revision `5c38ec7c…` (MIT, 384-d, CLS pooling, ONNX, CPU). It sits behind a
`gov-capability/1` `embed` adapter, so it can be replaced. It is **bitwise deterministic** across processes, thread
counts (4 vs 16) and batch compositions (batch 1, batch 32 unsorted, batch 32 length-sorted) (SO-09, SO-10).
Throughput is about 25 chunks/s on this machine under load (SO-10, SO-11). Vectors live in the store
(`float32` little-endian); search is brute-force cosine in numpy (about 40k × 384 floats ≈ 61 MB). No vector server
is used.

**Only kinds admitted by `config/embed-profile.yaml` are embedded**: prose, structured records and code (§1.1
`L-MACHINE-OUTPUT`). Query text gets the model card's query prefix. The route is **supplementary by construction**:
its items can only land in sections B–H with delivery `RETRIEVED`.

### 4.6 Code/symbol/reference route: tree-sitter Rust adapter plus the existing Python AST plugin

**Choice and measurement.** rust-analyzer/SCIP would be the most precise option, but it needs a rustup component
installed outside the cache and a full `cargo check` of a working tree. ctags is not present. A regex index misses
nested items and macros. **tree-sitter-rust**, as pinned wheels, parses **Git blobs directly**, with no working tree
and no build. On `3c880d8` it parsed 217 `.rs` files (6.9 MB) in **1.56 s**, found 5,363 definitions (4,125 `fn`, 919
test fns), 82,114 call sites and 72,874 string literals, and resolved in 0.1 s (SO-12). It is error-tolerant: 10 files
contain localised `ERROR` nodes, for example `cli/src/main.rs:2285` and `exec_resolve.rs:370,681` (SO-13). The adapter
records those spans and falls back to a line-regex definition scan inside them, labelled `HEURISTIC_REGEX_FALLBACK`.

**Tables:** `symbol(symbol_id, blob, kind, name, qualified_name, module_path, start, end, is_test)`,
`call_site(blob, line, caller_symbol, callee_text, callee_name, call_kind)`,
`literal(blob, line, enclosing_symbol, value)`, and `resolution(call_site, target_symbol, label, n_candidates)`.

**Resolution labels, never blurred:**

| Label | Meaning |
|---|---|
| `EXACT_PATH` | a `crate::…::f` path resolves to exactly one definition in the module the path names |
| `HEURISTIC_TYPE_PATH` | a `Type::f` path matches one method in an `impl Type` |
| `HEURISTIC_SAME_FILE` | a bare call matches one fn defined in the same file |
| `HEURISTIC_UNIQUE_NAME` | the name is unique across the crate |
| `HEURISTIC_AMBIGUOUS` | there are several candidates; **all** are listed and none is chosen |
| `UNRESOLVED_EXTERNAL` | std or another crate |
| `MACRO` / `HEURISTIC_MACRO_TOKEN` | a call inside a macro token tree, found by token scan |

The spike's label mix: `EXACT_PATH` 1,266; `HEURISTIC_*` 31,772; `MACRO` 14,426; `UNRESOLVED_EXTERNAL` 34,650. Method
calls are mostly ambiguous: `.decide(` has 3 candidates. That is the honest state of syntactic resolution, and it is
labelled rather than hidden.

**Literal-key consumers.** A string literal that is an accessor argument on the same line (`d.str("mutation")`,
`r.get("mutation")`) is recorded as a `READS_KEY` fact. This is generic: it answers "who consumes attribute X", which
call graphs cannot, because the attribute is data. The spike found 28 non-test occurrences of the literal
`"mutation"`, including `tools.rs:1817` (SO-12).

**Symbol history (C6 temporal).** For every commit that a record **references** by hash (§6), the symbol table is
built lazily and cached by blob, so unchanged files are parsed once. `DELETED_IN` and `INTRODUCED_IN` edges come from
the set difference between two such commits along the commit graph. They are exact about the parse tables, and say
nothing about *why* a symbol went.

**Python** files go to the **existing** `capabilities/python/govos_capabilities/code_intel_python_ast.py`, unmodified.
It is run as a `gov-capability/1` `code_intel` plugin from its blob at the records commit. Other languages get
file-level lexical coverage only, and coverage reports them as `code_intel: NONE`.

**The generic chain probe the code route must pass** (acceptance for node B3). This is a generic operation: given
symbol names, return each definition, its callers and callees with labels, and the literal-key readers of a named
attribute. The builder is given only the operation and a list of names drawn from *any* part of the product. For this
architect's verification, I ran it on names I verified independently at `3c880d8` (SO-12, and direct reads
recorded in SO-20):

| Verified at `3c880d8` | Location | Code-route result |
|---|---|---|
| `init::native_layout_rules`; its pattern built by `format!("{d}/**")` | def `runtime/src/init.rs:90-149`; the construction is `init.rs:146` | callers `policy.rs:488` (`PolicySet::load`, `EXACT_PATH`), `init.rs:162` |
| `PolicySet::load` | `runtime/src/policy.rs:121-623` (reconstruction `:486-488`; kernel template + floor `:540-546`; overlay evaluation call `:549`) | caller `project.rs:145` (`Project::policies`, `HEURISTIC_TYPE_PATH`) plus 2 ambiguous |
| `paths::union_last_known_rules_across_store` | `runtime/src/paths.rs:1453-1485` (`paths.sort()` `:1467`) | callers `init.rs:329`, `adopt.rs:1806` (`EXACT_PATH`) |
| `policy_precedence::partition_floor_rules_against_kernel` | `runtime/src/policy_precedence.rs:940-978` | **one** caller: `cit/mod.rs:1623` (`apply_op`, `EXACT_PATH`) |
| `policy_precedence::evaluate_path_rules_overlay` | `policy_precedence.rs:786-916`; `:911` `effective.push(krule.clone()); // restored last, so it wins …` | production caller `policy.rs:549`; test callers in `policy_precedence.rs` and `tests/certification/{remediation_ac,repair4}.rs` |
| `RepositoryContract::decide` | `runtime/src/paths.rs:1789-1896` (doc `:1786` "Ordered rules; later rules override earlier ones") | 36 call sites, all `HEURISTIC_AMBIGUOUS` among 3 `decide`s, including `tools.rs:1808` |
| the consumer of `mutation` | `runtime/src/tools.rs:1817`, inside `installation_authority` (`tools.rs:1599`), which feeds `change_decision` (`tools.rs:1972`, envelope at `:1975`) → `gate_required` | `READS_KEY("mutation")` at `tools.rs:1817`; the `decide` call at `tools.rs:1808` |

---

## 5. Current-vs-superseded and authority filtering

### 5.1 Two orthogonal labels, assigned before any ranking

Every unit that retrieval can return carries an **authority class** and a **lifecycle status**. Both are assigned by
`govbridge.authority` from **record metadata and explicit, cited rules**, never from a score, and they are stored
before any route runs. A third, independent label is the **version status** of §1.2, which says which Git version is
current.

**Authority ladder** (rank 1 is highest; BR-HO-0001 §2.2 item 2):

| Rank | Class | Admissible in A | Admissible in D.1 | Typical sources (rules in `config/authority-registry.yaml`) |
|---|---|---|---|---|
| 1 | `OWNER_DECISION` | yes | yes | `GATES/OWNER-*.md`, `OC-BR-*`, launcher; **section-scoped** where a file holds several items (§5.2) |
| 2 | `CONTRACT` | yes | — | Contract v3 owner source and its canonical import; compiled contract as `CONTRACT` (derived copy) |
| 3 | `FROZEN_GATE_CONTRACT` | yes | — | `PHASE-2-FROZEN-GATE-CONTRACT.md` |
| 4 | `ARCHITECTURE_DECISION` | yes | yes | `spec/decisions/*.yaml`, `spec/architecture/*.yaml`, the three governing documents |
| 5 | `ORCHESTRATION_RECORD` | yes | only adjudications, labelled rank 5 | `ORCHESTRATOR_STATE.yaml`, `GATE-REGISTER.yaml`, ledgers, handoffs, runs, checkpoints, `P2-ADJ-*`, orchestrator research/design records |
| 6 | `EVIDENCE` | yes | no | probes, review outputs, test results, `release/**/evidence/**`, telemetry; product code and tests as **implementation facts**; research reports; lessons |
| 7 | `DERIVED` | **never** | no | anything the bridge computes: packets, index rows, graph paths, summaries |

**Non-ladder classes. These never rank as authority and are never admissible in A or D.1.** Their names are copied
**verbatim** from `ORCHESTRATOR_STATE.yaml → mandatory_bridge_inputs.authority_classes`:

| Class | Where it may appear | Mandatory rendering banner |
|---|---|---|
| `OWNER_DIRECTION_TO_TEST` | D.2 only | `OWNER DIRECTION TO TEST: NOT YET AUTHORITY. The synthesis tests it and may reject it.` Evidence **for and against** is shown adjacent (§7.3) |
| `HYPOTHESIS_TO_TEST` | D.3 only | `HYPOTHESIS TO TEST: NO CLASSIFICATORY FORCE. The bridge makes it testable and does not answer it.` |
| `HYPOTHESIS_RELEVANT_OBSERVATION` | F only | `OBSERVATION ABOUT ORCHESTRATOR REASONING. It concerns reasoning, not implementation, and is not evidence for any hypothesis.` |
| `EVIDENCE_WITHDRAWN` | E or F only | `WITHDRAWN: retained as evidence of a withdrawn claim; never cited as a finding.` |
| `FIXTURE` | H only | `TEST FIXTURE COPY, not a record` |
| `UNCLASSIFIED` | H only | `AUTHORITY UNKNOWN` |

**Lifecycle vocabulary:** `ACTIVE` · `SUPERSEDED` · `WITHDRAWN` · `PROPOSED` · `HISTORICAL` · `UNKNOWN`. The source
vocabulary maps onto it by a fixed table. `IN FORCE`, `ACTIVE` and `in_effect: true` map to `ACTIVE`. `PROVISIONAL`,
`PROPOSED`, `PENDING…` and `in_effect: false` map to `PROPOSED`. `SUPERSEDED` and a `superseded_by` field map to
`SUPERSEDED`. `WITHDRAWN` and `RETRACTED` map to `WITHDRAWN`. `HISTORICAL`, `retired` and `retained as historical` map
to `HISTORICAL`. **Anything else maps to `UNKNOWN`, which is never treated as `ACTIVE`.**

### 5.2 How classes and lifecycles are assigned, in precedence order, failing closed

1. **`mandatory_bridge_inputs` items** (the bridge's `ORCHESTRATOR_STATE.yaml`). The class is the item's `class`,
   exactly. Where several items share one file (OD-P2-10A, OD-P2-10B, F1-DIRECTION, F2-F3-COMMON-CLASS, PROPERTY-A and
   STANDING-STATE all live in `OWNER-DECISION-P2-0010A-B-REVIEW-8-DISPOSITION.md`), the registry anchors each item to
   its **heading-delimited section**. Every line of that file not covered by an anchored item is `UNCLASSIFIED`,
   scoped to that section. **The file-level class never flows into a section.** This is the rule that stops the F1
   direction inheriting `OWNER_DECISION` from the file that records it.
2. **Registry entries** (`config/authority-registry.yaml`) handle authority or lifecycle that records do not carry in
   machine-readable form. **Each entry must cite** `{path, commit, line, quote}`, and the build verifies that the
   quoted text occurs at that line of that blob. A mismatch fails the build. This is how the **known supersessions**
   are represented:

   | Supersession | Representation | Citation (verified at `6e7a2a3`) |
   |---|---|---|
   | OA-P2-06's stop condition superseded | `SUPERSEDES(OD-P2-07 → OA-P2-06, scope: "stop condition")`. **Scoped**: OA-P2-06 stays `ACTIVE`, carrying the note `partially superseded: stop condition`. OD-P2-08 §8's stop conditions are the current ones | `OWNER-DECISION-P2-0007-…md:9` "Authorises continuation **beyond** OA-P2-06's previous stop condition"; `OWNER-DECISION-P2-0008-…md:7` |
   | V8.2 over V8.1 | `V8.1 → HISTORICAL`; `SUPERSEDES(V8.2 → V8.1, scope: WHOLE)` | `phase-1/ORCHESTRATOR_STATE.yaml:70` "HISTORICAL_PHASE_1_OPERATOR_EVIDENCE … NOT a current operator interface"; `:275` |
   | CP-1 retired | `CP-1 → HISTORICAL` (retired as the Phase-1 target) | `phase-1/GATES/OWNER-DIRECTIVE-0004-…md:43`; `phase-1/GATES/GATE-REGISTER.yaml:11` |
   | "only serialised runs are authoritative" retracted | **section-scoped**: `V8_3_EVIDENCE_PACKAGE.md §5.3` sentence → `WITHDRAWN`, superseded by §5.0 ("Anything in §5 that disagrees with this block is historical and retracted") and `PERFORMANCE_DIAGNOSTIC.md` §3 ("the serialised band itself does not survive scrutiny") | `V8_3_EVIDENCE_PACKAGE.md:253-254,369-371`; `PERFORMANCE_DIAGNOSTIC.md:177,207` |
   | the withdrawn AR96 positive-control finding | `EVIDENCE_WITHDRAWN`, lifecycle `WITHDRAWN` | `RESEARCH/P2-AR0096-POSITIVE-CONTROL-GAP.md:1,6`; `mandatory_bridge_inputs` |
   | D-0001 superseded by D-0002 | from metadata (rule 3), not the registry | `spec/decisions/D-0001.yaml` `status: SUPERSEDED`, `superseded_by: D-0002` |

3. **Structured metadata.** For YAML records: `status`, `supersedes`, `superseded_by`, `amends`, `in_effect` and
   `approval_state`. For markdown owner records: the header-table rows `| Status |`, `| Supersedes |` and
   `| Authorises |`, mapped through the fixed vocabulary table.
4. **Path/type rules** in the registry (`class_rules`, glob → class). These give a **class** only, never an `ACTIVE`
   lifecycle.
5. **Otherwise** the unit is `UNCLASSIFIED` / `UNKNOWN`.

**Conflicts fail closed.** When two sources disagree, the **less authoritative** class wins: non-ladder beats ladder,
and a lower rank beats a higher one. The less active lifecycle wins as well. The unit is flagged `CLASS_CONFLICT` or
`LIFECYCLE_CONFLICT`, is excluded from A and D.1, and is listed in the packet's J section for the orchestrator.

The build fails in two cases:

* a class named in `mandatory_bridge_inputs.authority_classes` is missing from the class table;
* such a class has admissibility different from §5.1.

The table's other classes (`CONTRACT`, `FROZEN_GATE_CONTRACT`, `ARCHITECTURE_DECISION`, `DERIVED`, `FIXTURE`,
`UNCLASSIFIED`) come from the ladder in BR-HO-0001 §2.2 item 2, which covers the whole corpus.

### 5.3 The hard authority invariant, enforced in code

Section A is filled **only** by `govbridge.authority.resolver`, and violations are **impossible by type** and
**detectable by re-derivation**:

1. **Types.** `MandatoryItem` is a frozen dataclass constructed only in `resolver.py`. `Packet.section_a` accepts only
   `MandatoryItem`, checked with `isinstance` at insertion. Every route returns `RetrievedItem` and the graph returns
   `DerivedItem`. **No conversion function exists** between them.
2. **Import boundary.** `authority/resolver.py` and `authority/lifecycle.py` must not import `govbridge.lexical`,
   `.semantic`, `.code`, `.graph` or `.route`. A test parses the imports with `ast` and fails on any such import.
3. **Admissibility is a code constant.** The class table in §5.1 is a constant in `authority/classes.py`. A test
   asserts that it equals the state file's class vocabulary and the admissibility flags above.
4. **Independent re-derivation.** `govbridge.compile.validate` (a separate module, shared by the compiler, `packet
   verify`, the receipt checker and the grader) recomputes `resolver(task_spec, view)` **from scratch**. It asserts that
   section A equals the result, in order, by `(id, class, lifecycle, commit, path, blob, line range, sha256)`. It also
   asserts, for every item in every section, that the placement is admissible for its class and lifecycle and that
   the class banner is present in the rendered text. **The compiler refuses to emit an invalid packet**, and a stored
   packet can be re-verified at any time.
5. **Order cannot be inverted by score.** Within every section the sort key is `(pinned first, authority rank
   ascending, lifecycle order ACTIVE < PROPOSED < HISTORICAL/SUPERSEDED < WITHDRAWN < UNKNOWN, then fused score)`. The
   validator asserts that no item with a worse `(rank, lifecycle)` precedes a better one. **A semantically strong
   superseded record can never outrank a current one**, and it can never enter D.1.
6. **Outage and pressure.** With every index deleted, compilation must produce a byte-identical section A (W10,
   "retrieval/index outage does not erase deterministic required dependencies"). Under budget pressure, B–H are
   truncated first, and **A is never truncated**. If A alone exceeds the total budget, A items above the per-item cap
   are delivered **by exact reference** (path@commit, line range, sha256), with a read-token obligation (§7.4). If even
   that cannot fit, the compiler emits `BLOCKED_BUDGET` (W4, "explicit governed failure").

**The tests that prove it** (node B6 acceptance). These run on a small synthetic fixture corpus *and* on the real
view:

* `test_semantic_trap`: a superseded record that is the **top** lexical and semantic hit is never placed in D.1,
  appears only in E with its banner, and sorts below the active record wherever both appear;
* `test_retrieved_cannot_enter_a`: a route that tries to insert a `RetrievedItem` into A raises; a hand-edited packet
  with an extra A item fails `packet verify`;
* `test_outage_a_identical`: with the index moved aside, A is byte-identical;
* `test_budget_pressure`: with tiny budgets, A is intact, every drop is listed in the manifest, and `BLOCKED_BUDGET`
  is emitted when required;
* `test_mandatory_bridge_inputs_classes`: for the real `mandatory_bridge_inputs`, every item appears in its expected
  section with its exact class and banner. OD-P2-10A and OD-P2-10B are in A and D.1. `F1-DIRECTION` is only in D.2,
  and `F2-F3-COMMON-CLASS` only in D.3. `ORCHESTRATOR-REASONING-ERRORS` is only in F, and nowhere adjacent to D.3 as
  support. `DESIGN-P2-AR0096-POSITIVE-CONTROL-GAP` is only in E/F with `WITHDRAWN`;
* `test_section_scoping`: no line of the OD-P2-10A/B file outside an anchored item's section is delivered as
  `OWNER_DECISION`.

---

## 6. Whole-repository dependency/WHY lineage

### 6.1 Nodes and edges

**Nodes** are the units of §2: occurrence (file@ref), section, record (by ID), symbol, test (a symbol with
`is_test`), commit (only commits that records reference, plus the view commits), and finding (a record-local ID
defined inside a review record).

**Edges.** Every edge carries `derivation ∈ {EXACT_*, HEURISTIC_*}` and the occurrence and line that justify it. **A
heuristic edge is never rendered without its label.**

| Edge | Derivation | How it is derived |
|---|---|---|
| `DEFINES(occurrence|section → record)` | EXACT_DEFINITION | an id-grammar definition rule |
| `MENTIONS(section → record)` | EXACT_ID (the ID resolves to one definition); HEURISTIC_LOCAL_ID (a bare local ID resolved within the same record, or by an adjacent record qualifier) | id-grammar mention rules |
| `CITES_PATH(section → occurrence)`, `CITES_LINE(section → occurrence:L)` | EXACT_PATH when the path, or a unique path suffix, exists in the view at the **citing record's subject commit**; HEURISTIC_SUFFIX when it is ambiguous | regex for `path`, `path:NNN` and `path:NNN-MMM` |
| `CITES_COMMIT(section → commit)` | EXACT_COMMIT (the hex resolves) | 7–40 hex that resolves with `git cat-file -e` |
| `SUPERSEDES`, `AMENDS`, `EXTENDS` | EXACT_METADATA or REGISTRY_CITED, each with a scope | §5.2 |
| `CONTAINS(occurrence → section|chunk|symbol)` | EXACT_SPAN | spans |
| `CALLS(symbol → symbol)` | the labels of §4.6 | code route |
| `READS_KEY(symbol → literal)` | EXACT_SPAN (the literal is at that line) | code route |
| `TESTS(test → symbol)` | EXACT_PATH (the test calls it by a resolved path); HEURISTIC_NAME otherwise | code route |
| `EVIDENCE_MAP(test → requirement)` | EXACT_ID | `tests/governance/capability-evidence-map.yaml` rows |
| `CODE_CITES(symbol → record|requirement)` | EXACT_ID (an ID token inside the symbol's doc comment or body comment, such as `BC-P2-29`, `OC-P2-04 §4` or `Contract v3:308-313`); the edge asserts **the mention**, never that the claim is true | comment scan |
| `SYMBOL_MENTION(section → symbol)` | EXACT_QUALIFIED when the prose writes `file.rs::name` or `Type::name` and it resolves uniquely at the record's subject commit; HEURISTIC_NAME for a bare backticked `name` | prose scan |
| `CHANGED_IN(occurrence → commit)` | EXACT_GIT | `git diff-tree` over referenced commits |
| `INTRODUCED_IN / DELETED_IN(symbol → commit)` | EXACT_PARSE | symbol-table set difference between referenced commits (§4.6) |
| `RELATION_CUE(record → record)`, a typed reading of a MENTIONS edge (`reopens`, `closes`, `supersedes`, `withdraws`, `moot`) | **HEURISTIC_CUE**, always | a fixed cue-word list within the sentence of the mention. It is never used for authority; §5 alone decides authority |

**Subject commit.** A review or finding record makes claims about the code at the commit it reviewed. The review
header states that commit, and state `review_history[*].commit_reviewed` records it. Its `CITES_LINE` edges are
anchored **there**. They are then mapped to the canonical product ref: `EXACT_SAME_BLOB` if the file's blob is
unchanged, and otherwise `HEURISTIC_LINE_REMAP` through the `git diff` hunks. An anchor whose blob has since changed
is shown as **`STALE_ANCHOR`**, which is how query class 8 ("which evidence becomes stale?") is answered
mechanically.

### 6.2 The system-purpose chain

`govbridge why <seed>` is a deterministic traversal in the owner's order (OD-P2-10 §5; launcher):

```
product purpose → requirement → owner decision → architecture → dependency → implementation → tests → findings → lessons → current status
```

* **purpose**: the governing documents' purpose sections and the Contract v3 gate preamble that owns the
  requirement;
* **requirement**: Contract v3 items reached through `CODE_CITES`, `EVIDENCE_MAP` or record `MENTIONS`;
* **owner decision / architecture**: ACTIVE rank-1 and rank-4 records that mention the requirement or the seed;
* **dependency / implementation**: `CALLS` and `READS_KEY` in both directions at the canonical product ref;
* **tests**: `TESTS` and `EVIDENCE_MAP`;
* **findings / lessons**: review sections, ledger entries and lesson records that `MENTION` or `SYMBOL_MENTION` the
  seed, with `RELATION_CUE`s labelled heuristic;
* **current status**: structured state lookup (§4.1) for the findings' IDs.

Every hop is printed with its edge label and citation. A missing link is printed as `MISSING: <stage>` and is never
filled by retrieval (W8, "missing lineage link detection").

### 6.3 Historical lesson/failure retrieval: a profile, not a store

"Failed approaches" are units that already exist:

* sections of review records that define findings;
* ledger entries;
* `WITHDRAWN`/`SUPERSEDED` records;
* `DELETED_IN` symbols, for mechanisms a round removed;
* `lessons/`;
* rank-5 research records with `RETRACTED`/`WITHDRAWN` sections.

`govbridge history <seed>` returns them for a seed (a symbol or record) through `MENTIONS`, `SYMBOL_MENTION`,
`CITES_LINE` and `DELETED_IN`, ordered by commit time, and labelled. **No separate lesson store and no LLM
extraction** are needed.

---

## 7. Bounded context compilation

### 7.1 The task spec (input) — `schemas/task-spec.yaml`

Field names follow the product's W3 manifest (`runtime/src/context/manifest.rs:7-24`):

* `task_id`, `role`, `objective`;
* `required_inputs: [{id | state_ref | path@ref, reason, required_status?, content_hash?}]`. A `state_ref` such as
  `state:bridge#mandatory_bridge_inputs.items[*]` pulls a declared list from a state file, verbatim;
* `seeds: [symbol | record id | path]`;
* `queries: [{text, routes?, target_section?}]`;
* `supplementary_context`;
* `retrieval_exclusions: [glob]`. These are applied to every route, the resolver excepted, and are recorded in the manifest;
* `mutation_scope`, `prohibitions`, `required_checks`, `completion_vocabulary`;
* `budget_profile`.

### 7.2 Sections A–J, exactly as the launcher names them

| § | Name | Filled by (deterministic) | Admits |
|---|---|---|---|
| **A** | MANDATORY AUTHORITATIVE INPUTS | **resolver only**: `required_inputs`, resolved to exact occurrences/sections, with a sha256 check against `content_hash` or the state's recorded sha256. A mismatch or a missing input → `BLOCKED` (W3/W4) | `MandatoryItem`, ladder rank 1–6, lifecycle `ACTIVE` |
| **B** | SYSTEM PURPOSE / WHY | `why` traversal from seeds (§6.2) | `DerivedItem` referencing records; if a record is already in A, B references it by item id rather than duplicating it |
| **C** | DIRECT DEPENDENCY / IMPACT CONTEXT | graph neighbours of seeds, depth from the profile, both directions; labelled edges | `DerivedItem`/`RetrievedItem` |
| **D** | RELEVANT ACTIVE DECISIONS | **D.1**: ACTIVE `OWNER_DECISION`/`ARCHITECTURE_DECISION` (plus adjudications labelled rank 5) that are mandatory, or reached from seeds by graph or retrieval. **D.2**: `OWNER_DIRECTION_TO_TEST`. **D.3**: `HYPOTHESIS_TO_TEST`. Three separate, titled sub-blocks | per §5.1 |
| **E** | RELEVANT HISTORICAL / SUPERSEDED DECISIONS | lifecycle ∈ {SUPERSEDED, HISTORICAL, WITHDRAWN}; partial-supersession notes; `HISTORICAL_VERSION` occurrences | labelled lifecycle |
| **F** | FAILED APPROACHES / LESSONS | the history profile (§6.3); `HYPOTHESIS_RELEVANT_OBSERVATION`; `EVIDENCE_WITHDRAWN` | labelled |
| **G** | CODE / TEST / ENFORCEMENT SURFACES | code route at the canonical product ref: seed symbols, their callers/callees, `READS_KEY` consumers, `TESTS`; evidence probes | `RetrievedItem`/`DerivedItem` with resolution labels |
| **H** | SUPPLEMENTARY RETRIEVED CONTEXT | fused lexical and semantic hits not placed above; `UNCLASSIFIED`; `FIXTURE` | `RetrievedItem` |
| **I** | TASK CONTRACT / MUTATION SCOPE | the task spec's `mutation_scope`, `prohibitions` and objective, verbatim | — |
| **J** | COMPLETION / EVIDENCE OBLIGATIONS | `required_checks`, the completion vocabulary, the receipt schema (§7.4), the read tokens to return, and any `CLASS_CONFLICT`/`LIFECYCLE_CONFLICT`/dangling-ID notices | — |

**Mandatory but non-authoritative items are delivered too.** Items such as `OWNER_DIRECTION_TO_TEST`,
`HYPOTHESIS_TO_TEST`, `EVIDENCE_WITHDRAWN` and `HYPOTHESIS_RELEVANT_OBSERVATION` are **pinned**: delivered
deterministically, never displaced by budget, and never ranked. They go to their class's section, not to A. *Mandatory*
and *authoritative* are different properties, and the packet keeps them apart.

**Routing and fusion** (`govbridge.route`) is deterministic:

* the exact route runs when a query contains an ID, path or symbol token;
* the code route runs for symbol-like tokens;
* the lexical route always runs;
* the semantic route runs for natural-language queries of at least four words;
* graph expansion runs from resolved seeds.

Fusion is reciprocal-rank with `rrf_k = 60` (`MEMORY_POLICY.yaml:22-23`) **inside each (section, authority stratum)**,
never across strata. Duplicates are suppressed by `(blob, overlapping line range)` and by record id. The canonical
version wins over `SAME_AS_CANONICAL` copies. Parent expansion uses `parent_expansion_top_n: 3` and
`max_slice_chars: 1600` (`MEMORY_POLICY.yaml:24-26`).

### 7.3 Bounding policy (`config/budgets.yaml`)

Budgets are in UTF-8 bytes (tokens ≈ bytes/4), and a profile is chosen per task class. `bounded-builder` totals
100 KB, about 25k tokens. `synthesis` totals 360 KB, about 90k tokens. Both sit inside the 50k–150k-token band that V8.3
§3.1 measured as sufficient. The `synthesis` profile allocates, in KB: A no cap (see §5.3, point 6), B 16, C 40, D 40
(D.2/D.3 pinned), E 24, F 40, G 120, H 40, I 12, J 12. The per-item cap is 24 KB. Anything larger is delivered as an
excerpt of the matching sections plus an exact reference.

**At the ceiling** the compiler drops whole items, lowest in the section's sort order first, and never cuts one
mid-item. Each drop is recorded in the manifest as `{item_id, unit id, reason: BUDGET, score, bytes}`, and the rendered
section ends with `[N items / K bytes omitted: see manifest]`. **Truncation is never silent.**

**Evidence both ways, for a direction** (D.2). For every `OWNER_DIRECTION_TO_TEST` item, the compiler runs two
symmetric, fixed query templates over its subject:

* *consumers, dependents and uses* of the subject;
* *purpose, origin and the requirements it was created for*.

It places the results side by side under "evidence bearing on the direction, both ways". It never labels either side
as supporting.

### 7.4 Manifest, packet hash and consumption receipt (`schemas/packet-manifest.yaml`, `schemas/receipt.yaml`)

**The manifest** is canonical JSON with sorted keys and no timestamps. It records:

* `packet_schema` and the task-spec sha256;
* the view (`ref → commit`) and the build `manifest_sha256`;
* the bridge code tree id and the config shas;
* per section: the queries and parameters that produced it (route, k, filters, profile), and its items. Each item has
  its unit id, delivery, class, lifecycle, version status, `(ref, commit, path, blob, lines)`, `content_sha256`,
  bytes, route, raw score, rank and edge path with labels;
* the drops;
* `section_sha256`, computed over the section body.

`manifest_sha256` is the sha256 of the manifest with `manifest_sha256` and `packet_sha256` set to null. Each section's
**read token** is `sha256(manifest_sha256 ‖ section letter)[:12]`. It is printed as the **last line** of that section
in the rendered packet. `packet_sha256` is the sha256 of the final rendered bytes, and `packet_id =
packet_sha256[:16]`. **The manifest is not given to the worker**, only the rendered packet, so the tokens cannot be
copied from it. The compile timestamp goes to telemetry, **never into anything hashed**.

**Receipt** (worker → orchestrator). Its field names follow the product's W5 receipt (`runtime/src/context/receipt.rs:7-17`):

* `context_packet_hash`;
* `manifest_sha256`;
* `read_tokens` (one per section read);
* `inputs_consumed: [ID@content_sha256]` for **every** A item;
* `items_relied_on: [item_id]`;
* `external_reads: [{path@commit, lines, blob, why}]`, for anything read outside the packet;
* `outputs_produced`, `decisions_applied`, `acceptance_evidence`, `deviations`, `unresolved`.

**`govbridge receipt check`** runs the validator (§5.3) on the packet and then checks the following:

* the packet hash matches;
* every read token matches the value recomputed from the manifest. A worker can only produce it by holding this
  exact packet version and reaching the end of that section;
* every A item is acknowledged with its exact `content_sha256`;
* every cited `item_id` exists;
* every external read resolves to a real blob.

It reports `external_read_files` and `external_read_bytes`, the dumping measure (§8.3 and DEMONSTRATION_DESIGN §4). The
check is diligence evidence, not security: the tokens prove possession of the exact bytes, not comprehension.

### 7.5 The canonical worker bootstrap: `govbridge bootstrap <task-spec>`

The text is **one canon**. It is an **ADAPT** of `phase-2/tools/worker_bootstrap.py`, copied into the domain with its
provenance recorded:

* its verbatim-quote discipline (`contract_excerpt`, `decision_excerpt` with path and line range);
* its conventions blocks;
* its checkpoint protocol and completion semantics.

Two things change:

* `phase_state()`'s hard-coded text (SO-01: `cap2-candidate-1`, `GATE-P2-REPAIR-2`) becomes **structured state
  lookups** with provenance (§4.1);
* the fixed `DECISIONS` dictionary becomes the resolver's section A.

Output is the bootstrap prelude, followed by the packet A–J and then the receipt instructions. It is model-neutral. A
provider-specific wrapper, if one is ever needed, stays a thin adapter around the same text. This is the owner rule
recorded in V8.3 §2.3.

### 7.6 Checkpoint and renewal: `govbridge renew --checkpoint <file>`

A **packet checkpoint** (`schemas/packet-checkpoint.yaml`) records:

* `{run_id, packet_id, manifest_sha256, view commits, build manifest_sha256, read_tokens, items_relied_on}`;
* the worker's own `{done, open_questions, next_action}`.

This satisfies W9: the checkpoint records input IDs, versions and hashes. Renewal proceeds as follows:

1. Freshness check (§3). If the view and the index are unchanged, the result is `RENEW_NOOP` with the same packet id.
   The worker needs only its checkpoint plus section J. **There is no model call and no re-read.**
2. Otherwise the same task spec is recompiled, and the new manifest is diffed against the old one by
   `(item_id, content_sha256)`. The result is a **delta packet** containing: added and changed items; removed items,
   listed by id; A items whose content changed (re-delivered in full); and unchanged A items delivered **by reference**
   (id plus sha256), because the prior receipt proved that they were consumed.
3. The delta packet carries its own manifest and read tokens, so a new receipt covers it.

A long-running worker therefore renews context at a cost proportional to *what changed*, not to the corpus.

---

## 8. Deterministic rebuildability

### 8.1 Full rebuild from clean

The existing store directory is **moved aside**, never deleted in place. The build runs all layers against the view,
writes `manifest.json`, and then compares it with the committed `INDEX/manifests/<view_id>.json`.

The **build manifest** holds:

* the view commits;
* the corpus-rules, id-grammar, registry, embed-profile and budget shas;
* the bridge code tree id;
* the component pins: chunker version, FTS tokenizer, tree-sitter and grammar versions, and the embed model pin
  (§4.5);
* per-layer digests: sha256 over the sorted `occurrence`, `chunk`, `symbol`, `call_site`, `literal`, `record_def`,
  `edge` and `class/lifecycle` rows, and over the sorted `(chunk_id, vector_sha256)` pairs.

**Reproducibility is a hard check**: two full rebuilds from clean must produce the same `manifest_sha256`. This is
`MEMORY_POLICY.rebuild.must_reproduce_manifest_hash: true`, at `MEMORY_POLICY.yaml:39-40`. The vectors are reproducible
because the embedder is bitwise deterministic (SO-09, SO-10).

### 8.2 Incremental rebuild

This is §3. The acceptance property is **incremental ≡ full**: build at view V1, move to V2 incrementally, and the
`manifest_sha256` must equal a from-clean build at V2. This is the product's own BC-P2-29 principle, re-applied.

### 8.3 Telemetry: what is written, and where

Local rows go to `$GOV_BRIDGE_HOME/telemetry/*.jsonl`. The **committed** rows, from integration, coverage and
demonstration runs, go to `release/orchestration/phase-2-context-bridge/telemetry/index/*.jsonl`.

* **Build rows** (`builds.jsonl`):
  * `build_id`, `trigger` (`full|incremental|noop`), view `ref→commit`, `prev_manifest_sha256`, `manifest_sha256`,
    `reproduced_from_clean`;
  * changes: refs, blobs added and removed, occurrences added and removed;
  * per layer: `{rows, added, removed, seconds}`; code `parse_error_files`; semantic `{chunks_embedded,
    vectors_reused, model_pin}`; edges by label;
  * coverage `{files_total, included, excluded_by_rule, unclassified}`;
  * `store_bytes`, `cpu_seconds`, `peak_rss_kb`, host `{nproc, loadavg_start, loadavg_end}`;
  * **`llm_invocations: 0`, asserted.**
* **Packet rows** (`packets.jsonl`): `packet_id`, task-spec sha256, bytes per section, drops per section,
  `compile_seconds`, build `manifest_sha256`, freshness.
* **Receipt rows** (`receipts.jsonl`): verdict, missing acknowledgements, `external_read_files` and
  `external_read_bytes`.
* **Query rows** (local only): route, latency and result count. These feed Phase 3's latency metric.

---

## 9. Replaceable embedding/index/runtime interfaces

Each interface is an explicit contract with a version, and each implementation is identified in the build manifest.
This is Contract v3 D4, component separation.

| Component | Interface (stable contract) | Provisional implementation | Replacement procedure |
|---|---|---|---|
| Embedding model + runtime | **`gov-capability/1` `embed`**, exactly as `capabilities/PROTOCOL.md` and `plugin.py` define it. Request `{protocol, capability:"embed", inputs:{texts, dimensions, mode: query\|passage}}`; response `{ok, provider:{id,version}, outputs:{vectors, dim}}`. The adapter declares `model:{id, revision, artefacts}` and `runtime:{id, artefacts}` as PROTOCOL.md specifies for embed plugins, and fails closed (`MODEL_UNAVAILABLE`, `DIMENSION_MISMATCH`) the way `embed_sentence_transformers.py` does | ONNX Runtime CPU + `bge-small-en-v1.5` (SEMANTIC_ROUTE.md) | new pin → parallel semantic layer under the new pin id → held-out benchmark → switch the pin in config (a governed commit) → GC the old vectors. No redesign |
| Code intelligence | **`gov-capability/1` `code_intel`**: request `{source, path, language}` → `{symbols, imports, calls, chunks}`, the shape `code_intel_python_ast.py` returns, extended with `literals` and `parse_errors` | tree-sitter-rust adapter (new); python-ast plugin (reused) | register another adapter for a language; the resolver labels come from the adapter |
| Vector store | `VectorStore.put(chunk_id, vec) / search(qvec, k, filter) / digest()` | SQLite BLOB + numpy brute force | e.g. HNSW, once the corpus outgrows brute force; the digest must stay order-independent |
| Lexical engine | `Lexical.index(chunk) / search(query, k, filter)` | SQLite FTS5 | any BM25 engine; the tokenizer is part of the pin |
| Graph engine | the edge table schema plus `traverse(seeds, types, depth, labels)` | SQLite + BFS | any graph store that preserves the derivation labels |
| Reranker | `gov-capability/1` `rerank` (PROTOCOL.md) | **none**; `MEMORY_POLICY.reranker.provider: none` | a plugin + benchmark (Phase 3) |
| Router, compiler, receipt | packet-manifest, receipt and task-spec schemas (`schemas/`) | `govbridge.route`, `govbridge.compile` | the product's `gov context compile/receipt` once qualified. The schemas are already W3/W5 field-compatible |
| Runtime environment | `bootstrap/bootstrap.sh` + `config/requirements.lock` (hash-pinned) + `config/model-pin.yaml` | venv under `$HOME/.cache/gov-bridge/` | re-pin and re-bootstrap; the build manifest records the versions |

The bridge **invokes** plugins directly, as subprocesses speaking `gov-capability/1`. It does **not** use
`gov plugins register`, which needs an adopted project and Human Decision Gates, and would write governed state. On
promotion, the same plugin files are registered through that governed path, and nothing about them changes.

---

## 10. Promotion and reconciliation into full V8.3

The bridge becomes implementation and evidence input to V8.3 (OD-P2-10 §9). It is not throwaway, because its
**contracts** are the product's:

* **Stable contracts, to be kept verbatim or versioned forward:**
  * `gov-capability/1` embed and code_intel adapters;
  * the corpus-rules, canonical-view and id-grammar schemas;
  * W1-conformant record identity;
  * task-spec, packet-manifest, receipt and packet-checkpoint schemas (W3, W4, W5, W9 field-compatible);
  * the authority class table and admissibility rules (W2, W10);
  * the build-manifest and telemetry schemas (D1, D6).
* **Provisional, and expected to be replaced after Phase-3 evidence:**
  * the embedding model and runtime pin;
  * the budget numbers;
  * brute-force vector search;
  * tree-sitter's heuristic call resolution (rust-analyzer/SCIP is the precise successor);
  * the specific `canonical-view.yaml` for this lifecycle, which collapses to `{primary: HEAD}`;
  * the registry entries specific to this repository's history.
* **What Phase 3 measures it against** (OD-P2-10 §10 → Contract v3 D5, D6, V3, W10, W11):
  * authoritative-input delivery accuracy (`test_mandatory_*`);
  * exact, lexical, semantic, graph and code retrieval **Recall@K and MRR** on a held-out query set, with thresholds
    from `MEMORY_POLICY.regression` (`min_recall_at_k 0.8`, `min_mrr 0.5`, `max_stale_hit_rate 0.0`,
    `max_superseded_hit_rate 0.0`, at `MEMORY_POLICY.yaml:32-38`);
  * authority and stale/superseded filtering (the semantic-trap family);
  * the hidden memory oracle (DEMONSTRATION_DESIGN's schema generalises to any case);
  * dependency/impact accuracy against oracle chains;
  * rebuild equivalence and delete-rebuild;
  * wrong-indexing and missing-index cases (coverage: `unclassified = 0`);
  * the stale-index count (freshness);
  * latency (query rows) and context size and token efficiency (packet rows);
  * flooding (drops and ordering);
  * model/session handoff (renewal, `RENEW_NOOP`);
  * Gate-W consumption continuity (receipts).
* **How it moves out of `release/orchestration/phase-2-context-bridge/` without redesign.** The code is one Python
  package, `govbridge`, whose **only** coupling to its location is `GOV_BRIDGE_DOMAIN`, the default path to `config/`.
  Promotion means:
  1. moving `govbridge/`, `config/` and `schemas/` into the V8.3 location that the V8.3 architecture chooses;
  2. setting the view to `{primary: HEAD}`;
  3. registering the two plugins through `gov plugins register`;
  4. mapping `authority-registry.yaml` class rules onto the product's `AUTHORITY_POLICY` state classes, as a governed
     change.
  
  Because the packet, receipt and task-spec fields already match W3/W5, V8.3 can either keep `govbridge` as the
  orchestration-layer compiler, or replace it with the product's `gov context compile` once that engine is qualified.
  **Either way the evidence, meaning manifests, telemetry, receipts and the demonstration, carries over.**
  Reconciliation is a V8.3 decision. The bridge does **not** claim V8.3 is CURRENT and does not earn Phase 3.

---

## 11. Capability coverage: every required capability, its component and its requirement line

| Capability (launcher / OD-P2-10 §5) | Component (§) | Contract v3 anchor |
|---|---|---|
| canonical worker bootstrap | `compile.bootstrap` (§7.5), ADAPT | N (handoffs), W9 |
| deterministic mandatory-authoritative-input resolver | `authority.resolver` (§5.3, §7.2 A) | W3, W4, W10 |
| structured current-state lookup | `authority.state` (§4.1) | C1 |
| exact retrieval | `core.exact` (§4.2) | D2 "structured lookup for known IDs/paths", C4 |
| lexical retrieval | `lexical` (§4.3) | C4, D2 |
| dependency/impact graph traversal | `graph` (§4.4, §6) | C2, W8 |
| semantic/vector retrieval, on the replaceable architecture | `semantic` + `gov-capability/1` adapter (§4.5, §9) | C3, D4, D5 |
| code/symbol/reference retrieval | `code` (§4.6) | C5 |
| authority filtering | `authority.lifecycle` + `compile.validate` (§5) | W2, W10 |
| lifecycle current-vs-superseded filtering | `authority.lifecycle` + version status (§1.2, §5) | C6, W3 |
| provenance | identity model (§2), every item | W1 |
| bounded context compiler (A–J) | `compile` (§7) | C9, W4 |
| exact context manifest with IDs/versions/hashes | `compile.manifest` (§7.4) | W4 |
| context-packet provenance/hash | `compile.manifest` (§7.4) | W4 |
| worker consumption receipt | `compile.receipt` (§7.4) | W5 |
| checkpoint/renewal support | `compile.renewal` (§7.6) | W9, N |
| historical lesson/failure retrieval | `graph` history profile (§6.3) | C8, Q |
| system-purpose chain | `graph.why` (§6.2) | W8 |
| rebuild/freshness telemetry | `core.freshness` + telemetry (§3, §8) | D1, D6 |
| *(OC-BR-02)* whole-repository corpus + coverage | `core.corpus` (§1), node D1 | D1, D6 |

---

## 12. Cost

**Measured build costs on this machine** (20 threads, 15 GB RAM; load 2–14 from other sessions during the spikes):

| Operation | Cost | Evidence |
|---|---|---|
| Corpus scan, rules and secret regex, 3 refs (5,787 unique blobs) | 8.5 s | SO-04 |
| Same, all 98 refs | 17.1 s | SO-14 |
| Lexical FTS5 build, 3 refs (78k chunks) | 9.8 s, 148 MB | SO-16 |
| Code parse, all Rust at one commit | 1.6 s | SO-12 |
| Semantic, per chunk | ~0.04 s (about 25/s) | SO-10, SO-11 |
| Semantic full build, embed profile, union of the 3 named refs (3,021 blobs, 40.8 MB → **40,035 chunks, measured**) | **≈ 27 min CPU**, at the measured rate | SO-21 × SO-10 |
| Semantic, everything included (77.3 MB, 78,058 chunks) | ≈ 52 min, and **deliberately not done** (§1.1 `L-MACHINE-OUTPUT`) | SO-16 × SO-10 |
| Whole-repository full rebuild, every layer, 3 named refs | ≈ 28 min CPU: semantic ≈ 27 min; everything else ≈ 1 min (corpus 8.5 s + lexical 9.8 s + code ≈ 5 s for 3 commits + records/graph ≈ 30 s, the last estimated from the 11.6 s ID census, SO-17) | sum |

**Routine overhead against the ~10–20% objective** (OD-P2-09 §16; V8.3 §10). Every figure below is an estimate, and
§8.3's telemetry measures the real value per run.

* **Freshness check: 0 tokens, under 1 s.** This is the only operation that runs "just to see whether anything
  changed". It is Git ids and no model, as OD-P2-10 §11 requires.
* **Incremental index after an ordinary commit: 0 tokens, seconds of CPU.** The global edge recompute dominates. It
  has not been measured yet, and node I1 measures it; the estimate is under 30 s.
* **Per-worker context: the bootstrap (~5.6k tokens, SO-01) plus a packet** (bounded-builder about 25k tokens;
  synthesis about 90k). For bounded builders that is about 15–20% of a 150k-token worker context. It **replaces**
  exploratory reading. The measured V8.3 §3.4 case is P2-AR-0060: 102 tool calls before the first write against 35
  with a corrected packet. Net overhead is therefore expected to be at or below the objective for ordinary tasks. The
  measurement is `packet_bytes/4 ÷ total_run_tokens` together with `tool_calls_before_first_write`, reported per run.
* **Full rebuilds** (the ~27 min semantic layer) belong at G4/G5 boundaries only (V8.3 §10 cost tiering), never per
  task.

**What was deliberately not built:**

* no reranker (`MEMORY_POLICY` has `provider: none`);
* no LLM query planning, and no LLM summarisation of records;
* no GPU inference (for CPU determinism);
* no vector database server;
* no rust-analyzer/SCIP precise index;
* no invocation of the product `gov` engine (§0.2);
* no daemons or watchers (freshness is checked on demand);
* no cross-project memory (V8.3 §11);
* no MCP server (D-0004 defers it);
* no UI;
* no model bake-off, and no second model;
* no redaction pipeline for secret-matching files;
* no automatic lesson extraction.

---

## 13. Language, dependencies and footprint

**Language:** Python 3.12. All code and every committed artefact lives under
`release/orchestration/phase-2-context-bridge/`. `product_identity.py` counts top-level `tools/`, `capabilities/` and
similar paths as product code (`product_identity.py:23-26`), so nothing is added there.

```
release/orchestration/phase-2-context-bridge/
  govbridge/            core/ lexical/ code/ semantic/ authority/ graph/ route/ compile/  cli.py __main__.py
  config/               corpus-rules.yaml canonical-view.yaml id-grammar.yaml authority-registry.yaml
                        embed-profile.yaml budgets.yaml model-pin.yaml requirements.lock
  bootstrap/            bootstrap.sh    (pinned venv + model into $HOME/.cache/gov-bridge/; writes nothing in Git)
  tests/                core/ lexical/ code/ semantic/ authority/ graph/ compile/ integration/  fixtures/
  INDEX/manifests/      committed deterministic build manifests (small JSON)
  COVERAGE/             committed coverage reports (JSON, < 5 MB)
  telemetry/index/      committed build/packet/receipt rows
  DEMONSTRATION/        oracle commitment, demonstration packets, receipts, answers, grading
```

**Dependencies, each justified.** stdlib covers `sqlite3` + FTS5, `hashlib`, `subprocess` (git), `ast` and `json`.

| Dependency | Why |
|---|---|
| numpy (already present) | vectors |
| PyYAML (already present) | records and config |
| **onnxruntime 1.30.0** (MIT) | CPU inference for the one provisional embedder |
| **tokenizers 0.23.2** (Apache-2.0) | the model's own `tokenizer.json`; it pulls in `huggingface_hub` and friends, which are **installed but never called for downloads**: the bootstrap fetches pinned URLs itself |
| **tree-sitter 0.25.2** + **tree-sitter-rust 0.24.0** (MIT) | Rust code intelligence without a build |
| **pytest** | tests. The system has 9.0.3, and the venv pins it |

Every installed wheel is **hash-pinned** in `config/requirements.lock` (SO-07 lists the sha256 of each wheel resolved
in the spike) and installed with `pip --require-hashes`. The venv (≈201 MB), the wheel cache (≈50 MB), the model
(133 MB) and all indexes (≈150 MB lexical plus ≈61 MB vectors for the 3-ref union) live in `$HOME/.cache/gov-bridge/`,
outside Git. **No committed file exceeds 5 MB.** Built indexes are rebuildable artefacts, and only their manifests
are committed.

---

## 14. Limits, residual risks and open issues

1. **Call resolution is syntactic.** Method calls are mostly `HEURISTIC_AMBIGUOUS` (SO-12). Chains through trait
   objects or generic dispatch show every candidate, never a chosen one. The **literal-key** facts and the
   **path-qualified** mentions in records are what make an enforcement point reachable without type inference. A
   precise index is the named V8.3 successor.
2. **Secret-content exclusions hide 8 product files** (§1.1). This is disclosed in every packet that would have used
   them.
3. **Semantic throughput is CPU-bound**: a full semantic rebuild takes about 27 minutes (SO-21). Incremental builds are cheap.
   The route is supplementary, so an embedder outage degrades H and never touches A (W10).
4. **Registry entries are hand-authored.** They are **cited and verified**, and they only restrict: they add
   supersession, withdrawal or narrowing, and can never raise a class. A wrong entry fails the build when its quote
   does not match, or at worst hides a record from D.1. It cannot promote anything to authority.
5. **Receipts prove possession of bytes, not comprehension.** Comprehension is graded by the held-out oracle
   (DEMONSTRATION_DESIGN.md).
6. **Owner-level questions: none.** The corpus (OC-BR-02), the authority classes (`mandatory_bridge_inputs`), the
   exclusions (SECURITY/ARCHIVE policy), the model latitude (the launcher's semantic bootstrap rule) and the write
   boundary are all settled by the records. No trade-off is left open that the records cannot resolve.

---

## Appendix A: how BR-HO-0001 §2.2's ten required decisions map to this document

| BR-HO-0001 §2.2 item | Where decided |
|---|---|
| 1 Corpus and ref model (read with OC-BR-02) | §1.1, §1.2, §2 |
| 2 Authority and lifecycle model | §5.1, §5.2 |
| 3 Hard authority invariant, in code, plus its test | §5.3 |
| 4 The graph: nodes, edges, exact vs heuristic | §6.1 |
| 5 Rust code route, measured on `3c880d8` | §4.6 (SO-12, SO-13) |
| 6 Semantic route and pins | §4.5, `SEMANTIC_ROUTE.md` |
| 7 Context compiler: A–J, budgets, manifest, hash, receipt, checkpoint/renewal | §7 |
| 8 Freshness and rebuild, telemetry | §3, §8 |
| 9 Cost, and what was not built | §12 |
| 10 Language and footprint | §13 |
