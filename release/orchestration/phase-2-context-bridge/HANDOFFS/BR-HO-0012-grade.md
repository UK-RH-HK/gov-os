# BR-HO-0012: grading the Review-8 demonstration (GRADE, run BR-AR-0012)

| Field | Value |
|---|---|
| Your role | **Fresh rubric grader.** You did not build, did not author the oracle and did not answer the demonstration. |
| Model | spawned `model: opus` |
| Worktree / branch | `/home/usain/Dynamic-Agentic-Engineering-OS/.claude/worktrees/br-ar-0012`, branch `bridge/grade-0012` |
| Mutation scope | `release/orchestration/phase-2-context-bridge/DEMONSTRATION/oracle/**`, `…/DEMONSTRATION/grading/**` and `…/AGENT_RUNS/BR-AR-0012.*` |

## 0. Read first

1. `ARCHITECTURE/DEMONSTRATION_DESIGN.md`, all of it. §4 is the grading law.
2. `GATES/BR-ARCH-RULING-1-MANDATORY-INPUTS-ALWAYS-IN-A.md`, **including Addendum A1**. It governs how G3 treats
   lifecycle-UNKNOWN mandatory items in A, and how oracle `authority_expectations` rows that expect such an item
   outside A are read. **Report every oracle row that A1 affected.**
3. `ARCHITECTURE/schemas/grading-report.yaml`.
4. The demonstration run directory, `DEMONSTRATION/run-<n>/`: bootstrap, packet, supplementary packets, answers,
   receipt and `reads.json`.

## 1. Steps

1. **Unseal.** Copy **only** `oracle.yaml` from the sealed directory named in your dispatch message into
   `DEMONSTRATION/oracle/oracle.yaml`. **Never** copy `.authoring/`. `sha256sum` the copy. It must equal
   `DEMONSTRATION/oracle-commitment.yaml`'s `oracle_sha256`. **If it does not, stop and return BLOCKED.**
2. **Deterministic grading.** Run `python -m govbridge demo validate-oracle DEMONSTRATION/oracle/oracle.yaml`, then
   `python -m govbridge demo grade --oracle DEMONSTRATION/oracle/oracle.yaml --run DEMONSTRATION/run-<n>`. This
   produces every **[D]** result.
3. **Rubric grading.** Apply every **[R]** item yourself: `must_state` facts; no decision stated for F1; no F2/F3
   classification; no withdrawn finding cited as a finding; no reasoning-error passage offered as evidence. **Each
   rubric item is binary, and you must quote the answer text you judged.**
4. **G7 packet-size check, computed by you (OBS-BR-05).** `govbridge demo grade` never applies the "packet bytes ≤ 1% of
   corpus" condition: `grade_g7` requires `budget_bytes`, which `grade()` always passes as `None`. Compute it yourself:
   take `main packet.md` plus every file under `run-<n>/supplementary/queries/`, and compare the total with 1% of
   corpus bytes. Corpus bytes come from the committed build manifest's coverage for the three named refs; report the
   figure you used and where it came from. Report this condition's result separately from the deterministic G7
   result. Name OBS-BR-05 in the grading report.
5. **The orchestrator's secrecy-check result** is in your dispatch message. If it reports a hit, the verdict is
   `DEMONSTRATION_FAIL (INVALIDATED: sealed-path access)`, whatever the answers say.
6. Write `DEMONSTRATION/grading/run-<n>.yaml`, per `schemas/grading-report.yaml`. It must contain G1–G8 with reasons,
   the **headline context-efficiency figure** (G7), the A1-affected oracle rows, and the verdict: `DEMONSTRATION_PASS`
   or `DEMONSTRATION_FAIL`.

## 2. Discipline

* Grade the evidence, not the bridge's intentions. **A fail is a result, not a problem to be solved in grading.**
* Do not repair anything, re-run the demonstration, or edit answers.
* Your verdict is **builder-level evidence** for `P2_CONTEXT_RETRIEVAL_BRIDGE_BUILT`. **It is not the acceptance
  token.**

Return the typed report (`AGENT_RUNS/BR-AR-0012.report.yaml`) and the checkpoint (`AGENT_RUNS/BR-AR-0012.checkpoint.yaml`,
covering the sha256 check and both `govbridge demo` commands). End with your commit SHA and
`BR-AR-0012 RETURNED <COMPLETED|BLOCKED>`.
