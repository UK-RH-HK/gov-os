# BR-HO-0009: integrator, DAG node I1 (run BR-AR-0009)

**This brief is `HANDOFFS/BR-HO-TEMPLATE-builder.md` (read it first; its rules bind you) plus the node section
below.**

| Field | Value |
|---|---|
| Run | `BR-AR-0009` |
| DAG node | **`I1`**: integration. The CLI; the real routes wired into the compiler; demo tooling (the grader, the oracle validator, and read extraction as an ADAPT); the reproducibility and equivalence proofs; the committed manifest and telemetry. |
| Worktree | `/home/usain/Dynamic-Agentic-Engineering-OS/.claude/worktrees/br-ar-0009`, branch **`bridge/i1-0009`**, based on the bridge tip after B1–B6 all merged |
| Model | spawned `model: sonnet`, as a cross-cutting integrator |
| Depends on | B1–B6, all merged into your base. Read their typed reports in `AGENT_RUNS/BR-AR-000{3..8}.report.yaml`. |

## 1. Node section

**Take verbatim from `ARCHITECTURE/IMPLEMENTATION_DAG.yaml`, node `I1`:** the deliverables and **all nine** acceptance
checks. The orchestrator runs the last one (`check_state.py verify`). The design sources are `ARCHITECTURE.md` §3,
§7.4–§7.6, §8 (all), §9 and §10; `DEMONSTRATION_DESIGN.md` §2 and §4; and `ARCHITECTURE/schemas/*`.

## 2. Mutation scope (the DAG's I1 scope, widened by BR-DAG-AMEND-2)

Everything under `release/orchestration/phase-2-context-bridge/`:

- `govbridge/**`
- `tests/**`
- `config/**`
- `bootstrap/**`
- `INDEX/**`
- `telemetry/index/**`
- `AGENT_RUNS/BR-AR-0009.*`

**Not** `ARCHITECTURE/**`, `DEMONSTRATION/**`, `GATES/**`, `HANDOFFS/**`, `CHECKPOINTS/**`, `EVIDENCE/**`, `tools/**`,
`ORCHESTRATOR_STATE.yaml` or `PHASE_LEDGER.md`.

You own integration, so you may edit other nodes' modules. That power is bounded. **The orchestrator checks these
rules by `git diff` at merge, and violating any one refuses the merge:**

1. **Existing tests are frozen.** Under `tests/**` you may *add* files, and you may *rename* an existing test file
   verbatim (a pure `R100` rename). You may **not** modify or delete any existing `test_*.py` file. Existing
   `conftest.py` files and fixture modules may change only if every change is listed and justified in your report.
   The named invariant tests (§5.3 of the architecture: `test_semantic_trap`, `test_retrieved_cannot_enter_a`,
   `test_outage_a_identical`, `test_budget_pressure`, `test_mandatory_bridge_inputs_classes`, `test_section_scoping`,
   the resolver/lifecycle import-boundary test and the class-table-versus-state test) must pass **as they are**.
2. **Invariant modules are near-frozen.** In `govbridge/authority/{resolver,lifecycle,classes}.py` and
   `govbridge/compile/validate.py`, the only change you may make is moving hard-coded path constants into config (see
   §3). Any other edit must be listed in your report, with the reason. None may weaken the section-A type boundary,
   the re-derivation or the ordering invariant.
3. **No special-casing (OC-BR-02).** No bridge code may special-case Review 8, F1–F6, Phase 2 or particular IDs or file
   names.

## 3. Open issues routed to you. Close each one, or report precisely why not.

| From | Issue | What to do |
|---|---|---|
| B1 OI-2 | `exact id` is a mention-only placeholder | Resolve definition sites through B5's id grammar. |
| B1 OI-4 | INCREMENTAL re-walks a changed ref's whole tree | Use `diff_tree` for changed paths, **if** it keeps incremental ≡ full. |
| B1 OI-5 | A removed history ref is not detected | Detect it, drop its stale occurrences, and test it. |
| B1 OI-6 | CANONICAL_FALLBACK has no fixture test | Add the test. |
| B2 OI-1 / B4 OI-1 | Layers register only on import; a bare `freshness rebuild --layer X` raises KeyError | The CLI, and core freshness, discover and import every layer package deterministically. |
| B2 OI-4 | `build_manifest` calls every digest unconditionally | Fix centrally in core (the per-layer self-ensure already exists). |
| B3 | The reused Python AST adapter is not in the commit-wide symbol index | Wire it, or record why a Python index is not needed for this corpus. |
| B4 OI-2 | The semantic pins sit at `layers.vector.extra.semantic_block`, not `pins.semantic` | Add a per-layer pins hook in core, and conform to the schema. |
| B4 OI-3 | Retrieved results carry placeholder `UNCLASSIFIED`/`UNKNOWN` | Wire B5's classifier into **every** route's results (lexical, semantic, code, graph). A retrieved item then carries its real class and lifecycle, and stays `RETRIEVED`: **a class label is never a promotion into A**. |
| B4 OI-4 | The model-pin `local_name` does not match the bootstrapped cache layout | Fix the pin and/or `bootstrap.sh`. Re-run bootstrap twice. |
| B4 OI-5 | `embed_and_store` commits once, at the end | Commit per batch, so a killed rebuild resumes. Prove the result equals an uninterrupted build. |
| B4 OI-6 | A stale local manifest from the builder's run | Your from-clean rebuilds supersede it. Nothing to do. |
| B5 | Hard-coded state aliases in `resolver.py` and `BRIDGE_STATE_PATH` in `classes.py` | Move them to a config file inside your scope, keeping the same behaviour and tests. |
| B5 | Code-derived edges (CALLS/READS_KEY/TESTS) are on-demand, tested only on a B3-schema fixture | Wire them against the real B3 tables, so `why`/`impact` reach code. |
| B5 | A multi-path mandatory item resolves only its first path | Resolve every listed path. |
| B5 | `pathrules.glob_match` lacks brace alternation | Fix it centrally; B5's workaround may stay. |
| Orchestrator | `pytest tests -q` fails at collection: `tests/code/test_history.py` and `tests/graph/test_history.py` share a basename | Fix it **by an R100 rename** of one of them, or by config that makes plain `pytest tests -q` collect everything. **The acceptance command is plain `pytest tests -q`.** |
| TA OI-3 | `demo validate-oracle` must agree with `DEMONSTRATION/oracle-tools/check_oracle.py` | Match its stricter rules: lines on every code/test anchor; a record_id or section on line-less record/contract/evidence anchors; 40-hex commits; `process`/`production` keys only on both-ways consumer anchors. **Reuse `check_oracle.py` by import or subprocess rather than re-implementing it.** You never see the oracle itself; test against the synthetic fixture oracle only. |
| TA OI-4 | Section placement of the `EVIDENCE` and `ORCHESTRATION_RECORD` mandatory items | Make the compiled packet's placement follow `ARCHITECTURE.md` §5.1/§7.2 admissibility exactly. Print each `mandatory_bridge_inputs` item's section in your checkpoint output. |
| B6 | *(the orchestrator will append B6's routed issues here before dispatch)* | |

## 4. The long runs

A from-clean full rebuild includes the semantic layer, at about 30–40 minutes of CPU. The proofs need **three**:

* two from-clean builds at the current view, compared by `manifest_sha256`;
* one from-clean build at an **earlier records commit**, then `index update` to the current view, compared with the
  first.

Run them **sequentially**. Run each in the background with an explicit timeout. **Check completion by output, never by
elapsed time.** Record each run's wall and CPU seconds.

Use your own store, `GOVBRIDGE_STORE=$HOME/.cache/gov-bridge/store-BR-AR-0009`. For the second from-clean build, use a
**different** store path, so that "from clean" really is clean. Iterate on fixtures first. Run the full-corpus
proofs **once**, at the end.

## 5. Return

The typed report and checkpoint are as specified in the template. **Every acceptance check has exactly one checkpoint
entry**, and every §3 row appears in the report under `claims` (if closed) or `open_issues` (if not). Commit
`INDEX/manifests/<view_id>.json` and the telemetry rows, as the DAG says.
