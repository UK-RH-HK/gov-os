# BR-HO-0021: fresh test-author for the run-2 oracle (run BR-AR-0021, DAG node R1-TA2)

| Field | Value |
|---|---|
| Your role | **Fresh independent test-author.** You are not the run-1 test-author, not a builder, not the failure analyst and not a grader. You write the **held-out oracle** that grades demonstration run-2. |
| Model | spawned `model: opus` |
| Worktree / branch | `/home/usain/Dynamic-Agentic-Engineering-OS/.claude/worktrees/br-ar-0021`, branch `bridge/ta2-0021` |
| Mutation scope, in Git | `…/DEMONSTRATION/oracle-commitment-run-2.yaml`, `…/DEMONSTRATION/oracle-tools/**` and `…/AGENT_RUNS/BR-AR-0021.*` |
| Sealed location, outside Git | This is **given only in your dispatch message.** Write `oracle.yaml` there and nowhere else. **Never** write that path into any committed file or saved output; redact it as `<SEALED>`. |
| Checkpoint | **schema 2** (OD-BR-04 A). See §4. |

## 0. Read first

1. `ARCHITECTURE/DEMONSTRATION_DESIGN.md`, all of it. §5 is the oracle structure; §4 is the grading law your oracle
   feeds.
2. `ARCHITECTURE/schemas/oracle.yaml` and `DEMONSTRATION/oracle-tools/check_oracle.py`. The latter is the existing
   structural checker; extend it if you need to, **inside your scope**.
3. `ARCHITECTURE/demonstration-queries.yaml`: the **same public queries** as run-1.
4. `GATES/BR-ARCH-RULING-2-GRADING-INTERPRETATIONS-AND-CONTROL-A.md`. Its rules bind you:
   * **D-1:** a record anchor matches by record id or by section.
   * **D-2:** every must_state fact is **bound to a stage**. Place each fact on the stage whose claim naturally states
     it.
   * **D-3:** AUTH-1..4 are gated under G3; give each an answer-side expectation.
   * **D-4** and **D-5:** G7 accounting.
5. `ORCHESTRATOR_STATE.yaml` → `mandatory_bridge_inputs`: one authority row per item, with the class verbatim.
6. `GATES/BR-ARCH-RULING-1-MANDATORY-INPUTS-ALWAYS-IN-A.md` and its Addendum A1. Every A-admissible mandatory item
   is expected in **A**.

## 1. What you write, and from what

Ground truth is established by **you**, from **primary sources**: records at the bridge tip and at `6e7a2a3`, code at
**`3c880d8`** (read-only at `.claude/worktrees/br-frozen-3c880d8`, or `git show 3c880d8:<path>`), and Review-8
evidence at `58219d5`. **Verify every anchor against its blob**, and log each verification with a script that prints
only `anchor_id OK|FAIL`.

Where more than one anchor is equally correct, list the alternatives. That is what `any_of` and
`acceptable_alternative_enforcement_points` are for, and run-1 lost items to single-anchor strictness. **Do not
loosen any gate rule.** The design text governs.

## 2. You must never

* **Read or look at** any of these:
  * `bridge/grade-*`, in any form;
  * `DEMONSTRATION/oracle/`, `DEMONSTRATION/grading/**`, `DEMONSTRATION/run-1/answers.yaml` or `receipt.yaml`;
  * any `govbridge-sealed-*` directory other than yours, or anything under `~/.config/gov-bridge/sealed/` except the
    path in your dispatch message;
  * `ARCHITECTURE/REPAIR-1/CAUSE_ANALYSIS.md`.

  **Your oracle must be independent of run-1.** Transcripts are audited.
* Classify F2/F3 or dispose of F1. Assert facts and anchors only (`NOT_DETERMINED_BY_BRIDGE`; `NONE_STATED`).
* Look at `bridge/b*`, `bridge/r1-*` or any `govbridge/` code in progress.
* Use `rm`, or pipe without `set -o pipefail`.

## 3. Deliverables

* **The sealed `oracle.yaml`**, written last, after `check_oracle.py` passes on it.
* **`DEMONSTRATION/oracle-commitment-run-2.yaml`**: `{oracle_sha256, author_run: BR-AR-0021, author_model, written_at,
  schema: govbridge-oracle/1, supersedes_for_run_2: the run-1 commitment}`.
* **`DEMONSTRATION/oracle-tools/outputs-run-2/`**: redacted outputs only. There must be **no** oracle content and
  **no** sealed path in anything you commit.

## 4. Return: schema-2 worker completion checkpoint

* **`AGENT_RUNS/BR-AR-0021.report.yaml`**, with these keys:
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
* **`AGENT_RUNS/BR-AR-0021.checkpoint.yaml`**, with these keys:
  * `run_id`
  * `commit`
  * `commands`: a list of {cmd, exit_code, output_path, output_sha256}
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
  * `next_consumer`: GRADE2 (R1-GRADE2), via the commitment
  * `final_commit`

End with your commit SHA and `BR-AR-0021 RETURNED <COMPLETED|BLOCKED>`.
