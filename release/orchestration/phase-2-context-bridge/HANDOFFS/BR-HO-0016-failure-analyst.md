# BR-HO-0016: run-1 failure analyst (run BR-AR-0016)

| Field | Value |
|---|---|
| Your role | **Fresh failure analyst.** You did not architect, build, integrate, author the oracle, answer the demonstration or grade it. You diagnose; you do not repair. |
| Model | spawned `model: opus` |
| Worktree / branch | `/home/usain/Dynamic-Agentic-Engineering-OS/.claude/worktrees/br-ar-0016`, branch `bridge/analyst-0016` |
| Mutation scope | `release/orchestration/phase-2-context-bridge/ARCHITECTURE/REPAIR-1/**` and `…/AGENT_RUNS/BR-AR-0016.*`, **only** |
| Checkpoint | **schema 2** (OD-BR-04 A). See §4. |

## 0. Why you exist

Demonstration run-1 **FAILED**. G1–G3 passed, meaning authority was preserved. G4, G5, G6, G7 and G8 failed. The
failures are low recall of the required evidence, per chain, per query class, for the F1 consumers and for the
controls, plus a context-size breach. The bridge preserved authority but did not deliver **complete relevance**.
Before any repair, the causes must be classified. The alternative is to repeat this programme's own failure pattern:
local finding, then a new local mechanism, then a new finding.

## 1. Read first

1. `GATES/OWNER-DIRECTION-BR-0006-CONTEXT-RETRIEVAL-AND-CONTINUITY.md` and
   `GATES/OWNER-DIRECTION-BR-0005-MULTI-BATCH-MULTI-HOP-RETRIEVAL.md`. These are binding. The retrieval
   architecture they require is **not yet built**.
2. `GATES/OWNER-CLARIFICATION-BR-0002-CORPUS-AND-PURPOSE.md`: whole repository, generic, never shaped around
   Review 8.
3. The grading, **on the quarantined branch only**, via `git show bridge/grade-0012:<path>`:
   * `…/DEMONSTRATION/grading/run-1.yaml`
   * `…/DEMONSTRATION/grading/**`
   * `…/AGENT_RUNS/BR-AR-0012.report.yaml`
   * the unsealed `…/DEMONSTRATION/oracle/oracle.yaml`

   **You may read these. Nobody downstream of you may.**
4. The run: `DEMONSTRATION/run-1/`, meaning the packet, `answers.yaml`, `receipt.yaml`, `supplementary/queries/`,
   `reads.json`, `PROTOCOL-NOTES.md` and `CONSUMPTION-AND-SECRECY.orchestrator.md`.
5. The bridge code (`govbridge/**`) and `ARCHITECTURE/{ARCHITECTURE.md, DEMONSTRATION_DESIGN.md}`. The demonstration
   store is `$HOME/.cache/gov-bridge/store-BR-AR-0010`: **read-only**, never update or rebuild it.

## 2. Your task

For **every** failed gate item (each missed chain stage fact or anchor, each failed query class, the G6 consumer
miss, the G7 size breach and each control), determine the cause. Classify each as exactly one of:

* `BRIDGE_NOT_IN_PACKET_BUT_RETRIEVABLE`: the evidence was in the index, and a query the bridge *should* have issued
  would have found it.
* `BRIDGE_NOT_RETRIEVABLE`: not indexed, excluded, mis-chunked, mis-classified or unreachable by any route or edge.
* `AGENT_BEHAVIOUR`: the evidence was in the packet or in the agent's own query outputs, and the agent did not use
  it.
* `GRADER_DEFECT`: this covers GD-1..9 and anything else you find.
* `ORACLE_STRICTNESS`: the oracle demands something the public query did not ask for, or demands one anchor where
  another is equally correct.

**Measure; do not guess.** Search the packet, the saved query outputs and the store for each required item: exact
path, blob and line, and record id. Report what you ran.

Then produce a **GENERIC repair plan**: `ARCHITECTURE/REPAIR-1/REPAIR_PLAN.md` and `REPAIR_DAG.yaml`. The DAG uses
the same node format as `ARCHITECTURE/IMPLEMENTATION_DAG.yaml`: id, title, depends_on, mutation_scope inside the
domain, deliverables, acceptance_checks as commands with expected results, routing, size and parallel group. It must
at minimum cover:

* **OD-BR-05 / OD-BR-06 §2–4**, `govbridge gather` or its equivalent:
  * facet decomposition;
  * deterministic parallel facet retrieval;
  * adaptive follow-up from discovered identifiers, callers, decisions, tests, repairs and supersessions;
  * continuation and paging with a **configurable** batch size;
  * a recorded stopping reason;
  * a merge before compilation that preserves provenance, deduplicates, reconciles versions and filters by authority
    and lifecycle;
  * budgeted **supplementary packets** with manifests, replacing raw query dumps (OBS-BR-06);
  * a schema and validator for hierarchical evidence notes;
  * telemetry for rounds, candidates, deduplicated counts, final size and stop reason.
* The **grader repairs GD-1..9**, each with a regression test.
* **OBS-BR-07**: the packet carries the public query set and the answer and receipt schemas.
* **OBS-BR-08**: the query commands apply the task's `retrieval_exclusions` automatically.
* **Whatever else your measurements show**: for example facets G, F, D, E or tests being under-populated, or
  history/lesson profiles being too thin.
* A **run-2 protocol**: a fresh test-author and a fresh sealed oracle at a location **not** recorded in any committed
  file; the same public queries; a fresh demonstration agent; a fresh grader.
* The **OD-BR-05 §9 multi-batch demonstration** as an acceptance node: a query whose evidence spans distant
  locations and exceeds one batch, plus an unrelated control, with telemetry.

## 3. Hard rules: the plan must be generic and must not leak the oracle

* **No oracle content** may appear in `REPAIR_PLAN.md`, `REPAIR_DAG.yaml` or any file you commit:
  * no expected answers, must_state facts, required anchor lists, trap or wrong lists;
  * no per-query expected items.

  Describe causes and fixes at the level of **capabilities**. For example, "the tests facet is never retrieved for
  chain queries" is acceptable; naming which test the oracle wanted is not. The orchestrator runs a verbatim-overlap
  check of your files against the oracle before any builder sees them.
* **No Review-8 special-casing.** Every fix must be generic (OC-BR-02) and demonstrable on an unrelated control.
* **Do not repair anything.** Do not touch `govbridge/**`, the stores or the product.
* Never use `rm`. Never pipe without `set -o pipefail`. Bounded waits only.

## 4. Return: schema-2 worker checkpoint (OD-BR-04 A)

Commit on `bridge/analyst-0016`. Required files:

* `ARCHITECTURE/REPAIR-1/{CAUSE_ANALYSIS.md, REPAIR_PLAN.md, REPAIR_DAG.yaml}`. `CAUSE_ANALYSIS.md` classifies each
  failed item by **category and count**. It references items by grade-report key only (for example "G5.QC7.S2"), and
  never quotes an oracle value.
* `AGENT_RUNS/BR-AR-0016.report.yaml`, with these keys:
  * `run_id`
  * `role`
  * `model_observed`
  * `branch`
  * `commit`
  * `status`
  * `claims`
  * `evidence`
  * `mutation_scope_respected`
  * `open_issues`
* `AGENT_RUNS/BR-AR-0016.checkpoint.yaml`, with these keys:
  * `run_id`
  * `commit`
  * `commands`: a list of {cmd, exit_code, output_path, output_sha256}, with outputs saved under
    `ARCHITECTURE/REPAIR-1/evidence/`
  * `role`
  * `model_observed`
  * `input_manifest`: a list of {path, sha256}
  * `task_contract`: {handoff_path, handoff_sha256, mutation_scope}
  * `artifacts_changed`
  * `findings`
  * `failed_approaches`
  * `unresolved`
  * `decisions`
  * `lessons`
  * `next_consumer`
  * `final_commit`

End with your commit SHA and `BR-AR-0016 RETURNED <COMPLETED|BLOCKED>`.
