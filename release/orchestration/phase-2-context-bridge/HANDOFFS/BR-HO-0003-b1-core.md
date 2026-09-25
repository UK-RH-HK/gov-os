# BR-HO-0003: builder, DAG node B1, core (run BR-AR-0003)

**This brief is `HANDOFFS/BR-HO-TEMPLATE-builder.md` (read it first; its rules bind you) plus the node section
below.**

| Field | Value |
|---|---|
| Run | `BR-AR-0003` |
| DAG node | **`B1`**: core. Git object access, canonical view, corpus rules and coverage, content-addressed store, chunking, exact route, freshness, build manifest, telemetry writer, pinned bootstrap |
| Worktree | `/home/usain/Dynamic-Agentic-Engineering-OS/.claude/worktrees/br-ar-0003`, branch **`bridge/b1-0003`** |
| Model | spawned `model: sonnet` |
| Depends on | nothing |
| Runs in parallel with | the test-author (TA). You never see its work, and it never sees yours. |

## Node section

**Take verbatim from `ARCHITECTURE/IMPLEMENTATION_DAG.yaml`, node `B1`:** the deliverables, the acceptance checks and
the mutation scope. Your mutation scope is that node's `mutation_scope` **plus**
`release/orchestration/phase-2-context-bridge/AGENT_RUNS/BR-AR-0003.*`. It is recorded in the orchestrator's state,
and `integrate-check` enforces it.

Design sources: `ARCHITECTURE/ARCHITECTURE.md` §1, §2, §3, §4.2 and §8, the parts of §9 your interfaces expose,
`ARCHITECTURE/SEMANTIC_ROUTE.md` §2 and §5.1, `ARCHITECTURE/REUSE_VS_BUILD.yaml` rows for your capabilities, and
`ARCHITECTURE/schemas/*`. The spike scripts in `ARCHITECTURE/spike-scripts/` are **evidence of feasibility, not code
to import**. You may copy their logic into your scope.

## Orchestrator amendment BR-DAG-AMEND-1: store isolation for parallel builders (binding)

B2, B3, B4 and B5 will run **in parallel** after you. Each will build layers into the store. So:

1. The **index store root must be configurable** through the environment variable `GOVBRIDGE_STORE`. If it is unset,
   default to `$HOME/.cache/gov-bridge/store/<view_id>`. The store module, the freshness module, the manifest and every
   CLI in `govbridge.core` must resolve the store only through one function, `govbridge.core.store.store_root()`.
2. The **venv** (`$HOME/.cache/gov-bridge/venv`) and the **model cache** (`$HOME/.cache/gov-bridge/models/`) stay
   shared. After bootstrap they are **read-only in use**: no later node installs into the venv. So `requirements.lock`
   must already contain every wheel that B2–B6 and I1 need, as SEMANTIC_ROUTE.md §2 / SO-07 lists them, plus pytest.
3. Add a test: two different `GOVBRIDGE_STORE` values build independent stores, and a `freshness update` in one never
   touches the other.
4. Run your own acceptance checks with `GOVBRIDGE_STORE=$HOME/.cache/gov-bridge/store-BR-AR-0003`.
5. Do **not** modify or delete `$HOME/.cache/gov-bridge/spike-br-ar-0001/`. It is the architect's spike evidence.

## Notes on the acceptance checks

* The coverage check's expected counts at `3c880d8` are the architect's measurement (SO-05). If yours differ,
  document each difference with the rule that causes it. **Never tune a rule to hit a number.**
* The checks that cite `3c880d8:runtime/src/init.rs:146` and `3c880d8:release/orchestration/phase-2/ORCHESTRATOR_STATE.yaml`
  are **acceptance data**. No code may special-case those paths (OC-BR-02).
* Your canonical-view file must follow ARCHITECTURE.md §1.2. The `records` ref is `refs/heads/bridge/p2-context-retrieval`
  and follows its tip. The product and evidence refs are **pinned**, and they report `REF_MOVED` rather than following a
  moved branch.
