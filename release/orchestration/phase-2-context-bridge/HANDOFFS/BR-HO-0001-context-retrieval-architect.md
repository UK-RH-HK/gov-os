# BR-HO-0001: Context/Retrieval Architect (run BR-AR-0001)

| Field | Value |
|---|---|
| Your role | **Fresh Context/Retrieval Architect.** You design, you do not build. You are not the orchestrator, not a builder and not a verifier. |
| Lifecycle | `P2X-FAIL-1-BRIDGE`: the Phase-2 Context/Retrieval Bridge, orchestration support only |
| Your worktree | `/home/usain/Dynamic-Agentic-Engineering-OS/.claude/worktrees/br-ar-0001`, branch **`bridge/arch-0001`**, based on the bridge branch. **Write only here.** |
| Frozen product, read-only | `/home/usain/Dynamic-Agentic-Engineering-OS/.claude/worktrees/br-frozen-3c880d8`, detached at **`3c880d8`**, chmod a-w. **Read and grep it; never build or write there.** You can also use `git show 3c880d8:<path>` and `git show 58219d5:<path>` from your worktree. |
| Mutation scope | `release/orchestration/phase-2-context-bridge/ARCHITECTURE/**` and `release/orchestration/phase-2-context-bridge/AGENT_RUNS/BR-AR-0001.*` **only** |
| Model | You were spawned with `model: opus`. Record the model you actually are in your report. |

## 0. Read these first, in this order. They are mandatory authoritative inputs, not suggestions.

1. `release/orchestration/phase-2-context-bridge/GATES/OWNER-LAUNCHER-BR-0001-P2X-FAIL-1.md`: the owner's instructions,
   verbatim, and how "P2X-FAIL-1" resolves. **The capability list, the ten-section compiler (A–J), the hard authority
   invariant, the semantic bootstrap rule and the Review-8 demonstration in it are your requirements.**
2. `release/orchestration/phase-2/GATES/OWNER-AMENDMENT-P2-0010-CONTEXT-RETRIEVAL-BRIDGE.md`: especially §5 (the
   eighteen capabilities, which include **provenance, context-packet provenance/hash, and checkpoint/renewal
   support**, beyond the launcher's list), §6 (the authority model), §7 (what the bridge is *for*), §10 (Phase 3
   becomes qualification, so design so that it can be qualified) and §11 (**cost**).
3. `release/orchestration/phase-2/GATES/OWNER-DECISION-P2-0010A-B-REVIEW-8-DISPOSITION.md`
4. `release/orchestration/phase-2-context-bridge/ORCHESTRATOR_STATE.yaml`: anchors, hashes, prohibitions and routing.
5. `release/orchestration/phase-2-context-bridge/EVIDENCE/review-8/P2-AR-0097-return.verbatim.md` and `PROVENANCE.md`
6. `release/orchestration/phase-2/REVIEW_8_CONTEXT_PACK.md`. **This is the hand-built precursor of what the bridge
   must produce mechanically.** One orchestrator assembled it by hand from memory and records. Study what it contains
   and how it was sourced. The bridge's job is to let a fresh agent get context this good, or better, without a
   human-in-the-loop orchestrator.
7. `release/orchestration/phase-2/V8_3_EVIDENCE_PACKAGE.md` §2 (governed worker bootstrap) and §3 (context
   governance). These are non-normative empirical lessons, and they are directly relevant.
8. **`ORCHESTRATOR_STATE.yaml` → `mandatory_bridge_inputs`.** This holds the owner's Review-8 disposition
   (OD-P2-10A/B) and every `evidence_for_the_synthesis` reference that the stopped Phase-2 orchestrator recorded at
   `6e7a2a3`. Each item is hash-bound and carries an **authority class that you must preserve exactly**:

   | Class | Items | Meaning for the bridge |
   |---|---|---|
   | `OWNER_DECISION` | OD-P2-10A (F2 is not scope expansion; it is a blocker; it is not repaired yet), OD-P2-10B (the bridge is authorised; the token), Property A preservation, the standing state | Binding. |
   | `OWNER_DIRECTION_TO_TEST` | F1 as a strong DELETE/SIMPLIFY candidate | **Not yet authority.** The synthesis tests it and may reject it. The bridge must surface the evidence for it *and* against it. |
   | `HYPOTHESIS_TO_TEST` | F2/F3 as one deeper class | **No classificatory force.** It must not be pre-classified because the owner suggested it. |
   | `HYPOTHESIS_RELEVANT_OBSERVATION` | the Phase-2 orchestrator's three parallel reasoning errors (`orchestrator_error_f3`) | These concern the orchestrator's *reasoning*, not the *implementation*. They are never evidence for the hypothesis. |
   | `EVIDENCE` / `EVIDENCE_WITHDRAWN` | the Review-8 probes and return; the AR96 builder checkpoint (at `3c880d8:telemetry/checkpoints/`); `P2-AR0096-POSITIVE-CONTROL-GAP.md` (withdrawn) | Facts. A withdrawn finding is never cited as a finding. |
   | `ORCHESTRATION_RECORD` | the context pack, `P2-PROBE-OPTION-C.md`, `P2-HISTORICAL-RULE-SOURCE.md`, ledger entries P2-L-0033..0047, the Phase-2 state keys | The current record. It has no authority over owner records. |

   Read every item listed there. Your authority/lifecycle model (§2.2 item 2) must be able to represent **these exact
   classes**. In particular:

   * a direction or a hypothesis must be structurally incapable of entering packet section A, or of being rendered
     as a decision;
   * section D (active decisions) must keep OD-P2-10A/B distinct from the F1 direction and from the F2/F3 hypothesis.

## 1. What the bridge is for, in one paragraph

After this build stage, a **fresh whole-system root-cause synthesis** will run on the Review-8 findings before any
Phase-2 product repair (OD-P2-10 §7, OD-P2-10A/B). That synthesis must classify each response as one of REPAIR /
REUSE / DELETE / NARROW / DEFER / OWNER DECISION. To do so it must understand **why** each mechanism exists, what it
depends on, what depends on it, which approaches already failed, and **where the actual enforcement decision is
made**. Across eight rounds, the recurring failure was reasoning about a *representation* while the effect was
decided *downstream* of it. The bridge exists so that the synthesis, and the repair and review agents after it, are
not deprived of that context. **Build the minimum that makes this true. Nothing else.**

## 2. Your tasks

### 2.1 Inventory what already exists, with evidence. Do not assume.

Find every existing retrieval, index, memory, context, bootstrap or code-intelligence primitive, and for each one say
whether it is **operational today**. Run it if that is cheap. Places you must look, as a minimum:

* `release/orchestration/phase-2/tools/`: `worker_bootstrap.py` (the canonical worker bootstrap compiler, built in
  Phase 2), `prep_packet.py`, `telemetry_context_extract.py`, `check_state.py`, `product_identity.py`
* `capabilities/`: `PROTOCOL.md`, `python/govos_capabilities/{plugin.py, embed_sentence_transformers.py,
  embedder_hashed_ngram.py, code_intel_python_ast.py}`, `tests/`. This is the D-0006 **replaceable capability-plugin
  architecture**. OD-P2-10 §5 says semantic retrieval should use "the existing replaceable architecture where
  available". Establish whether that holds, and at which commit.
* the runtime at `3c880d8`: any memory, retrieval, index, context, `code_index` or lesson machinery
  (`runtime/src/**`), and the `gov` subcommands that expose it. Say whether a *product* primitive can be **invoked**
  by the bridge without being **modified**. The bridge must not change product code. Calling a built binary or reading
  its outputs is a different matter; state which applies, with evidence.
* `framework/policies/{CONTEXT_POLICY,MEMORY_POLICY,ARCHIVE_POLICY}.yaml`, `framework/skills/{SKL-MEMORY-RECONSTRUCTION,SKL-IMPACT-ANALYSIS}.yaml`,
  `spec/decisions/*.yaml` (does their metadata carry status and supersession?), `lessons/`, `spec/research/`
* the record corpus itself: `release/orchestration/phase-{1,2}/**` (ledgers, state, GATES, HANDOFFS, AGENT_RUNS,
  RESEARCH, CHECKPOINTS), and the Review-8 evidence at `58219d5`

### 2.2 Design the minimum bridge architecture

Write `ARCHITECTURE/ARCHITECTURE.md`. It must cover, at minimum, each launcher capability and each OD-P2-10 §5
capability. Name the component for each, or say explicitly why the capability needs none. The launcher's
capabilities are:

- canonical worker bootstrap
- deterministic mandatory-authoritative-input resolver
- structured current-state lookup
- exact retrieval
- lexical retrieval
- dependency/impact graph traversal
- baseline semantic/vector retrieval
- code/symbol/reference retrieval
- authority and lifecycle filtering (current vs superseded)
- provenance
- bounded context compiler (sections A–J)
- exact context manifest/hash
- worker consumption receipt
- checkpoint/renewal support
- historical lesson/failure retrieval
- the system-purpose chain
- rebuild/freshness telemetry

It must also decide the following, explicitly:

1. **Corpus and ref model.** Which sources are indexed, **at which Git refs**. Records are at the bridge base
   `6e7a2a3`. The frozen product is at `3c880d8`. Review-8 evidence is at `58219d5`. Earlier failed approaches may
   live on `phase2/*` branches. How does the index stay hash-bound to exact objects? The bridge must be able to say
   *"this chunk is blob X of path P at commit C"*.
2. **Authority and lifecycle model.** How authority class (owner decision > contract > frozen gate contract >
   architecture/decision records > orchestration state > evidence > derived/retrieved) and lifecycle status
   (ACTIVE / SUPERSEDED / WITHDRAWN / PROPOSED / HISTORICAL) are assigned **deterministically, from record metadata
   and explicit rules, never from retrieval scores**. Say how the known supersessions are represented, and how an
   unclassifiable record is handled. Fail closed: unknown authority never ranks as authority. Known supersessions
   include OD-P2-08 superseding OA-P2-06's hard stops, V8.2 over V8.1, CP-1 retired, and "only serialised runs are
   authoritative" retracted.
3. **The hard authority invariant, enforced in code, not in prose.** Section A (mandatory authoritative inputs) is
   filled **only** by the deterministic resolver. No lexical, semantic, graph or code hit may enter A, displace an A
   item, or be relabelled as authority. A semantically strong superseded record must never outrank a current one.
   Specify the mechanism that makes a violation impossible or detectable, and the test that proves it.
4. **The graph.** Its nodes and edges, and how edges are *derived*: explicit IDs and cross-references in records;
   code call/reference relations at `3c880d8`; test→code; finding→code; finding→repair→later finding. Say which
   edges are exact and which are heuristic, and label them so. A heuristic edge is never presented as an exact one.
5. **Code/symbol/reference retrieval for Rust.** The product is Rust. Pick the minimal practical route, whether that
   is ctags, `rust-analyzer`, a regex symbol index, tree-sitter or something else, and **measure** that it works on
   `3c880d8`. It must be able to take the Review-8 rule-composition chain from the pattern construction in
   `init::native_layout_rules`, through `PolicySet::load`, `union_last_known_rules_across_store`,
   `partition_floor_rules_against_kernel` and `policy_precedence::evaluate_path_rules_overlay`, to `decide`
   (last-match-wins) and the enforcement point that consumes `mutation` (`tools.rs:1817` per Review 8). **Verify these
   names and locations yourself**; do not inherit them.
6. **Semantic/vector route.** Say whether an operational semantic route exists; the environment facts are in the
   state file. If none exists, you **may** provision **one** lightweight provisional local embedding model behind a
   replaceable adapter. Prefer the existing D-0006 plugin protocol as that adapter if it fits. **Do not hard-code the
   final model.** BGE-family models are permitted but not mandated. Pick the **smallest suitable current local
   option** the evidence supports. CPU-deterministic embeddings are strongly preferred, so that a rebuild is
   reproducible. Pin and record the model ID, the exact revision/hash, the licence, the dimensions, the
   runtime/provider, the index manifest/schema and the rebuild/reindex procedure. Everything installed or downloaded
   lives **outside Git**, for example in a venv and a model cache under `$HOME/.cache/gov-bridge/`, created by a
   deterministic, pinned bootstrap script inside the domain. You may run a **feasibility spike** (install, embed,
   time it) in scratch space. Record its commands and outputs in your checkpoint. A spike is not a build.
7. **The context compiler and its packet.** Sections A–J exactly as the launcher names them. Specify the bounding
   policy (token/byte budgets per section, and what happens at the ceiling: truncation must be recorded, never
   silent), the manifest (IDs, versions, Git object IDs, hashes, the query and parameters that produced each
   section), the packet hash, and the **worker consumption receipt**: what a worker returns to prove it read the exact
   packet, and how the receipt is checked. Also specify **checkpoint/renewal**: how a long-running worker resumes or
   renews context without re-reading everything.
8. **Freshness and rebuild.** Deterministic change detection from Git object IDs. OD-P2-10 §11 rules out any LLM
   invocation just to find that nothing changed. Specify full rebuild from clean, incremental rebuild, and telemetry:
   which fields, and where they are written.
9. **Cost.** Estimate the routine overhead against the ~10–20% objective (OD-P2-09 §16; V8_3_EVIDENCE_PACKAGE §10),
   and name what you deliberately did **not** build.
10. **Language and footprint.** Python 3.12 with stdlib, numpy and PyYAML is available, with SQLite 3.45 and FTS5.
    Justify every added dependency. All bridge code and every committed artefact live under
    `release/orchestration/phase-2-context-bridge/`. The reason: `product_identity.py` counts top-level `tools/`,
    `capabilities/` and similar paths as **product code**, so nothing may be added there. Built indexes are
    **rebuildable artefacts**. Commit their manifests, not large binaries; no committed file over 5 MB.

### 2.3 The Review-8 demonstration: design it so that it can be *graded* by someone other than the builders

The owner requires that, before the bridge is declared built, a **fresh** agent reconstructs the full chain for the
Review-8 rule-composition findings. It must do so without dumping the whole repository and without prior chat:

requirement/intended property → source/construction → composition/union → partition/filtering → precedence/ordering
→ matcher/evaluator → final enforcement decision → concrete effective permission/behaviour → tests → prior
findings/failed repairs → current Review-8 finding/status

It must reach the **actual decision/enforcement point**, not an upstream representation. It must also answer the ten
query classes in the launcher. Design:

* the **query set** the demonstration runs through the bridge, which is public and given to builders as acceptance;
* the **structure of a held-out oracle**: the expected chain elements, each with a file:line anchor at `3c880d8` and
  the record IDs that must be present. A **separate fresh test-author** will write the oracle from primary sources,
  and builders never see it. You specify its *schema and grading rules*, not its content;
* the grading rules. What counts as reaching the enforcement point? How is a chain graded that stops at an upstream
  representation? How is "whole-repository dumping" measured? Use packet size against corpus size, and the
  consumption receipt.

The grading must also check that the packet **preserves the authority classes in `mandatory_bridge_inputs`**. A packet
fails in any of these cases:

* it presents the F1 direction as a decision;
* it presents the F2/F3 hypothesis as a classification;
* it cites the withdrawn positive-control finding as a finding;
* it presents the orchestrator's reasoning errors as evidence for the hypothesis.

It must also surface the F1 evidence **both ways**: the consumers Review 8 found, *and* whatever purpose or consumers
the exemption was created for.

**The bridge must make the F2/F3 single-class hypothesis *testable*, not answer it.** The retrieval and graph
must put F2's path (pattern construction → reconstruction → restore-last → last-match-wins → enforcement) and F3's
path (foreign union → no partition gate → exact-string conflict → ordering → enforcement) side by side, down to their
real enforcement points. Neither the bridge nor you may classify them.

### 2.4 Produce the implementation DAG and the reuse-vs-build decisions

* `ARCHITECTURE/REUSE_VS_BUILD.yaml`. For every capability in §2.2, give a decision of `REUSE` (path@commit),
  `ADAPT` (path, and what changes, applied to a *copy* inside the domain, never to the original), `BUILD` or
  `NOT_NEEDED`. Give the rationale and the evidence: the command you ran, or file:line.
* `ARCHITECTURE/IMPLEMENTATION_DAG.yaml`. Nodes that bounded builders can execute. Each node has:
  - `id`
  - `title`
  - `capabilities` covered
  - `depends_on`
  - `mutation_scope`: globs, all inside the domain
  - `deliverables`
  - `acceptance_checks`: deterministic commands with expected results
  - `routing`: `sonnet` by default; `haiku` only if genuinely mechanical; `deterministic` if it is a script run
  - `size`: S / M / L
  - `parallel_group`

  Keep **disjoint mutation scopes** across nodes that run in parallel. Include an **integration node** and the
  **demonstration node(s)**. The test-author oracle node and the fresh-agent demonstration run are roles the
  orchestrator dispatches; list them as nodes with `routing: opus` and `mutation_scope` inside the domain.
  Aim for the smallest DAG that satisfies the requirements. Roughly 4–8 build nodes is the right order of magnitude;
  justify more.

## 3. Hard constraints

- **Never** modify the frozen product (`3c880d8`, any `phase2/*` branch), `release/orchestration/phase-2/**`,
  Contract v3, the frozen gate contract, or any kernel/runtime trust semantics. The orchestrator's `verify` refuses
  any change outside the bridge domain.
- **Do not** repair, pre-judge or classify F1, F2, F3 or F4. Do not perform the root-cause synthesis. That is a later,
  separate stage.
- **Do not** design V8.3 features beyond this scope, run Phase-3A ecosystem research, or run a model bake-off. One
  provisional model, justified, is the ceiling.
- **Do not** let any bridge output be an authority source. Every packet must label derived and retrieved material
  as such.
- **Tests:** never `--test-threads=1`; never pipe without `set -o pipefail`; never bare `cargo fmt`. You should not
  need to run the product suite at all.
- **Waiting:** never wait on the orchestrator. Every wait needs a bounded iteration count and a deterministic timeout
  action. Never `pgrep -f` a pattern that your own shell's command line contains.
- **Do not use** `rm`/`rm -rf`; permission rules deny them. Move scratch files aside instead.

## 4. Return: typed, and enforced before your branch is integrated

Commit on `bridge/arch-0001`. Required files:

- `ARCHITECTURE/ARCHITECTURE.md`
- `ARCHITECTURE/REUSE_VS_BUILD.yaml`
- `ARCHITECTURE/IMPLEMENTATION_DAG.yaml`
- `ARCHITECTURE/DEMONSTRATION_DESIGN.md`: the query set, the oracle schema and the grading rules
- `ARCHITECTURE/SEMANTIC_ROUTE.md`: the decision and pins, or the reason none is needed
- `AGENT_RUNS/BR-AR-0001.report.yaml`: typed return, with **exactly** these top-level keys:
  - `run_id`
  - `role`
  - `model_observed`
  - `branch`
  - `commit`: your final commit, which must be on your branch
  - `status`: `COMPLETED` or `BLOCKED`
  - `claims`: a list
  - `evidence`: a list of {claim, command or file:line}
  - `mutation_scope_respected`: `true` only if every changed path is inside your scope
  - `open_issues`: a list. Include any genuine owner-level question here, and say why the records cannot resolve it.
- `AGENT_RUNS/BR-AR-0001.checkpoint.yaml` with keys:
  - `run_id`
  - `commit`
  - `commands`: a list of {cmd, exit_code, output_path, output_sha256}. Save each output under
    `ARCHITECTURE/spike-outputs/`, and hash the saved file with sha256.

The orchestrator runs `tools/check_state.py integrate-check BR-AR-0001` before merging. It refuses a missing or
untyped report, a missing checkpoint, an output whose hash does not match, or any path outside your scope.

End your final message with your commit SHA and a single line: `BR-AR-0001 RETURNED <COMPLETED|BLOCKED>`.
