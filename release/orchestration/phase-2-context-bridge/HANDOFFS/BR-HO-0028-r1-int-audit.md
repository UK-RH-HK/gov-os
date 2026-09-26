# BR-HO-0028: independent REPAIR-1 integration audit (run BR-AR-0028, DAG node R1-INT)

| Field | Value |
|---|---|
| Your role | **A fresh, independent integration AUDITOR.** You did not build any REPAIR-1 node. You do **not** fix code: every defect you find is reported with its owner node, and the orchestrator routes it (BR-DAG-AMEND-R1-16). |
| Model | spawned `model: opus` |
| Worktree / branch | `/home/usain/Dynamic-Agentic-Engineering-OS/.claude/worktrees/br-ar-0028`, branch `bridge/r1-int-0028` |
| Mutation scope | `…/tests/integration/test_repair1_integration.py`, `…/EVIDENCE/repair-1/**` and `…/AGENT_RUNS/BR-AR-0028.*`, **only** |
| Checkpoint | schema 2 (OD-BR-04 A), with a `conformance` row for **every** numbered check below |

## 0. Read first

1. `ARCHITECTURE/REPAIR-1/REPAIR_DAG.yaml`: the node `R1-INT`, and every node it depends on.
2. `ORCHESTRATOR_STATE.yaml`, in particular `dag.amendments` BR-DAG-AMEND-R1-1 … R1-23, and the `agent_runs` entries
   BR-AR-0017 … BR-AR-0034. The entries record what each builder claimed, what the orchestrator verified, the
   disclosed limits and the routed residuals. You audit the **integrated tree**, not those claims.
3. `ARCHITECTURE/ARCHITECTURE.md` (§1.2 the canonical view, §5 the authority invariant, §7 compilation and budgets)
   and `ARCHITECTURE/DEMONSTRATION_DESIGN.md` §4, for G7's own definition of corpus bytes.
4. `HANDOFFS/BR-HO-R1-TEMPLATE-repair-builder.md`, rules 1–8 and amendments R1-T1 … R1-T3. Its secrecy rules bind
   you, apart from the one exception in §2.

## 1. How you run

* **The interpreter.** Use `PY=$HOME/.cache/gov-bridge/venv/bin/python` for everything. Never use a bare
  `python3`, `pip` or `pytest`. Never create a venv or install anything; a missing dependency is BLOCKED.
* **Pin the view first.** The `records` ref follows the live orchestration branch, and the orchestrator may commit
  while you work. Write `EVIDENCE/repair-1/pinned-view.yaml`: a copy of `config/canonical-view.yaml` with every
  `follow: tip` ref pinned to the commit it resolves to when you start, recorded in a header comment. Use it
  (`--view`) for **every** real-view check, so that nothing you measure can drift.
* **Stores.** Build your own stores from clean with the pinned view: `$HOME/.cache/gov-bridge/store-BR-AR-0028-a`
  and `-b`. Never touch `store-BR-AR-0010` or any other run's store. Name every store you create.
* **Discipline.** Never `rm`. Never pipe without `set -o pipefail`. Every wait is bounded, and a from-clean build
  may take 40–70 minutes, so poll with a bound. Never wait on the orchestrator.

## 2. Secrecy

You must **never** read any of these:
* `bridge/grade-*`, in any form;
* any `govbridge-sealed-*` or `gbx-*` directory;
* `~/.config/gov-bridge/**`;
* `DEMONSTRATION/oracle/`, `DEMONSTRATION/grading/**`, `DEMONSTRATION/run-1/answers.yaml` or `receipt.yaml`;
* `ARCHITECTURE/demonstration-queries.yaml`, as input to any check.

**The ONE exception**, for check 6 only: you may read the public tool `DEMONSTRATION/oracle-tools/check_oracle.py`
and the schema `ARCHITECTURE/schemas/oracle.yaml`, to build a **synthetic** oracle. They contain no oracle content.
Transcripts are audited.

## 3. The checks

Save each check's output as `EVIDENCE/repair-1/int-NN-<name>.out`, recording `$PY` and the pinned commits. Where a
check asserts a zero or a negative, measure it a second, independent way.

1. **The full suite.** `$PY -m pytest -q -p no:cacheprovider tests`, twice, with 0 failures. Then once more with
   `-p no:randomly` if that plugin exists; skip that run otherwise.
2. **Rebuild from clean.** Build into two fresh stores, one via `$PY -m govbridge.core.freshness rebuild
   --from-clean` and one via `$PY -m govbridge index rebuild --from-clean`, both with the pinned view. Check:
   * identical build-manifest digests for **every** layer, including the lineage layer and
     `occurrence_distinct_path`;
   * then freshness NOOP on both;
   * coverage unclassified 0.
3. **Genericity (OC-BR-02).** Run the DAG's grep, and a broader audit: no Review-8 item, F-finding, Phase-2 file or
   Review-8 chain symbol named in `govbridge/`, `config/` or test code, excluding fixture DATA. List every hit and
   classify it: rule text or a violation.
4. **CONTROL-A, real view.** Using `tests/fixtures/controls/control-a/` with the pinned view:
   * **Compile twice** in two separate processes, with `PYTHONHASHSEED=0` and `=1`. Require byte-identical main
     packets AND identical supplementary and notes directories (R1-RA writes these). Then run `packet verify` (PASS)
     and `receipt check` with a synthetic receipt.
   * **Gather** every CONTROL-A query and report:
     * stop reasons and follow-up rounds;
     * every requested facet present, or disclosed as MISSING or BUDGET with a handle;
     * wall time;
     * main and supplementary bytes against corpus bytes, where corpus bytes follow **G7's own definition** in
       DEMONSTRATION_DESIGN.md §4 (state the definition and the number).
   * **Compare before and after** against `tests/fixtures/controls/control-a/baseline/`: no facet lost.
5. **Budgets, section by section.** Every non-exempt section of the CONTROL-A packet is within its cap. Report the
   sizes of A (never truncated) and the pinned J. Also report whether the main packet exceeds the profile total, and
   why.
6. **The grader cross-check (BR-DAG-AMEND-R1-3)** and GD-7.
   * Build a SYNTHETIC bound-mode oracle that passes `check_oracle.py --require-binding`. Grade a synthetic
     answers-plus-packet with `govbridge demo grade`: stage-bound facts are scoped per D-2, query-bound facts come
     out PENDING_RUBRIC, and nothing crashes.
   * Re-check GD-7 (packet de-duplication) on the integrated tree.
7. **Zero-count audit (R1-7).** Take every layer, edge kind, derivation label, facet and stop reason that has **0**
   rows or occurrences on the real view. Re-measure each independently: a raw git grep of the shape, never the code
   under test. Record it as confirmed-absent (with the command) or as a defect.
8. **Read-only query commands (R1-15).** Run every query command against a store whose FILE and DIRECTORY are both
   read-only: search, why, impact, history, exact, state, gather, compile, packet verify, receipt check, notes,
   cite and answers lint. The store's sha256 must be unchanged, and nothing may error for want of write access.
9. **Budget coherence (R1-21, R1-22).** Check every budget in `config/*.yaml` for any dependence on wall-clock time
   that can change CONTENT, and check the gather budget against the follow-up budget against the measured costs.
   Report inconsistencies; never change config.
10. **One view per operation (R1-23).** On the real view, run a dynamic resolution-count probe (count calls to the
    view resolver) for compile, gather, why, history, cite and answers lint. Each must resolve once per operation,
    and the recorded view in each output must equal the commits used. List the residuals the orchestrator recorded
    for R1-XC pass 5 and assess them.
11. **Test hermeticity.** Every `tests/**/conftest.py` isolates `GOVBRIDGE_STORE` (setenv to a tmp store, never
    only delenv). No test reads the machine-wide default store.
12. **History refs in verify.** Does `packet verify` re-derive correctly when a `phase2/*` history ref moves after
    compile? This is R1-RM's open issue; answer it with a fixture test.
13. **The cross-cutting fixes, on the real view:**
    * the `-m freshness` entry point (R1-5);
    * the gitobj repo_root cache (R1-6);
    * lazy authority config (R1-12);
    * a thread-safe excluded_hits count (R1-14, exact under `--threads 16`);
    * the transient-git retry disclosure (R1-22).
14. **Observation closure.** For every observation OBS-BR-01 … OBS-BR-20 in the state that REPAIR-1 addresses,
    state CLOSED with evidence, or OPEN with the reason.
15. **State consistency.** `python3 tools/check_state.py verify` reports STATE_CONSISTENT (this tool is exempt from
    `$PY`).

Encode the checks that can run hermetically as tests in `tests/integration/test_repair1_integration.py`, with an
isolated store and fixtures only. Real-view checks stay as evidence runs.

## 4. Your verdict

Write `EVIDENCE/repair-1/INT-VERDICT.yaml` with these fields:
* `verdict`: `INTEGRATION_ACCEPTED` or `DEFECTS_FOUND`;
* `pinned_view`: the commits;
* `defects`: a list of {id, severity HIGH|MEDIUM|LOW, owner_node, file:line, evidence path, why it matters for the
  run-2 demonstration or for an independent verifier};
* `residuals`: accepted limits;
* `checks`: one row per check.

**A HIGH defect means the verdict is `DEFECTS_FOUND`.** Do not fix anything. Then write the schema-2 report and
checkpoint, run `integrate-check BR-AR-0028`, commit, and end with the SHA and
`BR-AR-0028 RETURNED <COMPLETED|BLOCKED>`.
