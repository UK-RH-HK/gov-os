# BR-HO-0002: held-out oracle test-author (run BR-AR-0002, DAG node TA)

| Field | Value |
|---|---|
| Your role | **Fresh independent test-author.** You are not a builder, not the architect, not the demonstration agent and not the grader. You write the **held-out oracle** that the Review-8 demonstration will be graded against. |
| Your worktree | `/home/usain/Dynamic-Agentic-Engineering-OS/.claude/worktrees/br-ar-0002`, branch **`bridge/ta-0002`** |
| Mutation scope, in Git | `release/orchestration/phase-2-context-bridge/DEMONSTRATION/oracle-commitment.yaml`, `…/DEMONSTRATION/oracle-tools/**` and `…/AGENT_RUNS/BR-AR-0002.*`, **only** |
| Sealed location, outside Git | the oracle file itself goes to the **sealed directory** named in the dispatch message, and nowhere else. **Never commit it. Never copy it into any worktree. Never write its path into any committed file.** |
| Model | spawned `model: opus`. Record what you actually are. |

## 0. Read first

1. `release/orchestration/phase-2-context-bridge/ARCHITECTURE/DEMONSTRATION_DESIGN.md`: all of it, especially §1 (who
   sees what), §3 (the public query set), §4 (the grading rules your oracle feeds) and **§5 (the oracle structure)**.
2. `ARCHITECTURE/schemas/oracle.yaml`: your file must validate against it.
3. `ARCHITECTURE/demonstration-queries.yaml` and `ARCHITECTURE/demonstration-task.yaml`: the public queries.
4. `ORCHESTRATOR_STATE.yaml` → `mandatory_bridge_inputs`. Your `authority_expectations` rows come from here: one per
   item, with the class **verbatim**.
5. `GATES/OWNER-CLARIFICATION-BR-0002-CORPUS-AND-PURPOSE.md`. Review 8 is a *benchmark*.

## 1. What you write, and from what

The oracle states **ground truth**, established by you from **primary sources**:

* records at `6e7a2a3` (and the bridge branch's own GATES);
* code at **`3c880d8`**: read-only at `/home/usain/Dynamic-Agentic-Engineering-OS/.claude/worktrees/br-frozen-3c880d8`,
  or through `git show 3c880d8:<path>`;
* Review-8 evidence at `58219d5`;
* the Review-8 return copy in `EVIDENCE/review-8/`.

For each chain (`R8-CHAIN-F2`, `R8-CHAIN-F3`) you must cover every stage, in order, and mark exactly one
`is_enforcement_point`. The stages are:

1. requirement
2. source/construction
3. composition/union
4. partition/filtering
5. precedence/ordering
6. matcher/evaluator
7. final enforcement decision
8. concrete effective permission/behaviour
9. tests
10. prior findings/failed repairs
11. current Review-8 status

Every anchor must carry `kind`, `commit`, `path` and line range, and must be **verified by you against the blob**.
Log each verification command in your checkpoint.

**Verify everything yourself.** The architect's and the reviewer's line numbers are *leads*, not facts. Where a
stage is genuinely absent or not determinable, the schema's way of saying so is the right answer. Never invent an
anchor to fill a stage.

Also cover the rest of the public query set as §5 of the design requires:

* the side-by-side;
* F1 evidence **both ways**: the purpose and consumers the exemption was created for, *and* Review 8's
  no-production-consumer evidence;
* the ten query classes × subjects;
* the authority rows;
* the controls. The controls are subjects **unrelated to Review 8**, and they exist because the bridge must be
  generic (OC-BR-02).

## 2. What you must never do

- **Never classify** F2/F3 as one class or as different classes. **Never dispose** of F1 (delete, keep and so on).
  Assert facts and anchors only. The expected answers are `NOT_DETERMINED_BY_BRIDGE` for the side-by-side
  classification, and `NONE_STATED` for the both-ways disposition. Your oracle rewards an agent that keeps the owner's
  distinctions, and penalises one that resolves them.
- **Never look at** any `bridge/b*`, `bridge/i*` or `bridge/demo*` branch, or at any `govbridge/` code. None exists
  yet, and whatever appears must not shape your oracle.
- **Never modify** the product, `release/orchestration/phase-2/**`, or anything outside your scope. The orchestrator's
  `verify` and `integrate-check` refuse it.
- Never use `rm`. Never pipe without `set -o pipefail`. Every wait needs a bounded iteration count and a timeout
  action.

## 3. Deliverables and typed return

1. **The sealed oracle file** `oracle.yaml` in the sealed directory, written last, after it passes your own structural
   check.
2. `DEMONSTRATION/oracle-tools/check_oracle.py`: a stdlib + PyYAML structural checker against
   `ARCHITECTURE/schemas/oracle.yaml`. It enforces the node TA acceptance checks in
   `ARCHITECTURE/IMPLEMENTATION_DAG.yaml`:
   * 11 stages per chain, in order;
   * exactly one enforcement point;
   * one authority row per `mandatory_bridge_inputs` item;
   * every anchor has kind, commit and path.
3. `DEMONSTRATION/oracle-commitment.yaml`: `{oracle_sha256, author_run: BR-AR-0002, author_model, written_at, schema:
   govbridge-oracle/1}`. The sha256 is of the sealed file's exact bytes.
4. `AGENT_RUNS/BR-AR-0002.report.yaml`, with exactly these keys:
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

   Do **not** put oracle content, or the sealed path, in the report.
5. `AGENT_RUNS/BR-AR-0002.checkpoint.yaml`, with keys `run_id`, `commit` and `commands`. `commands` is a list of
   {cmd, exit_code, output_path, output_sha256}. It must include `check_oracle.py`'s run and the sha256 command. Save
   those outputs under `DEMONSTRATION/oracle-tools/outputs/`. **Redact** the sealed path in the saved outputs, for
   example by printing `<SEALED>/oracle.yaml`, and **never echo oracle content** into them.
   * Anchor verification is the exception: log it with a script that **reads** the oracle and prints only
     `anchor_id OK|FAIL`.

End your final message with your commit SHA and `BR-AR-0002 RETURNED <COMPLETED|BLOCKED>`.
