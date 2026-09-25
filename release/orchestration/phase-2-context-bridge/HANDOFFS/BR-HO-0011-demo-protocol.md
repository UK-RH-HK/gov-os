# BR-HO-0011: demonstration run (DEMO, run BR-AR-0011), orchestrator protocol

**This file is for the orchestrator, not for the demonstration agent.** The agent receives **only** the bootstrap
output, the compiled packet and the rules in §3. That is the architecture's own requirement
(DEMONSTRATION_DESIGN.md §1–§2). It must not see this file, `ARCHITECTURE/**`, `AGENT_RUNS/**`, `DEMONSTRATION/**`
beyond its own run directory, or any `HANDOFFS/BR-HO-0*` file.

## 1. Preconditions: each is a deterministic check, recorded in the ledger before dispatch

1. I1 (BR-AR-0009) is merged, and `check_state.py verify` returns STATE_CONSISTENT.
2. D1 (BR-AR-0010): coverage reports `unclassified == 0` for every ref, and `included + excluded == files_total`.
3. `python -m govbridge freshness` returns `NOOP` against the committed build manifest.
4. `DEMONSTRATION/oracle-commitment.yaml` is merged. Its sha256 equals the sealed file's; the orchestrator checks
   the hash only and never reads the content.

## 2. Orchestrator steps

1. Create the run directory `DEMONSTRATION/run-1/` on a fresh branch `bridge/demo-0011`, in worktree `br-ar-0011`.
2. `python -m govbridge bootstrap ARCHITECTURE/demonstration-task.yaml > DEMONSTRATION/run-1/bootstrap.md`
3. `python -m govbridge compile ARCHITECTURE/demonstration-task.yaml --out DEMONSTRATION/run-1/packet` (real routes).
   Then run `python -m govbridge packet verify` on it. It must PASS.
4. Commit the bootstrap, the packet and the manifest **before** dispatch. Record `packet_sha256` in the state.
5. Dispatch a **fresh** opus agent that is not a builder, not the test-author and has no prior chat. Its prompt is the
   bootstrap text, plus the rules in §3, plus the packet's path.
6. When it returns:
   * run `govbridge receipt check`;
   * extract its reads from its transcript into `DEMONSTRATION/run-1/reads.json`, using I1's `demo extract-reads`;
   * **grep every non-TA, non-GRADE subagent transcript for the sealed directory name.** A hit invalidates the run.

## 3. The rules the agent receives, verbatim, after the bootstrap text

```text
You are a FRESH demonstration agent for the Governance OS self-memory/context bridge. You are not a builder, not a
test-author, not a grader, and you have no prior conversation.

Your inputs are ONLY: the bootstrap text above; the compiled context packet at <PACKET_DIR> (read its manifest first);
and these `python -m govbridge` query commands, run from <WORKTREE>/release/orchestration/phase-2-context-bridge with
PYTHONPATH=. and GOVBRIDGE_STORE=<STORE>: search, why, impact, history, exact, state. Every query command writes a
supplementary output: save EACH command's full stdout to
<RUN_DIR>/supplementary/queries/NN-<command>.json and append the exact command line to
<RUN_DIR>/supplementary/queries/INDEX.md (these outputs count toward your context size, OBS-BR-06).

You MAY read files directly, but you MUST declare every such read in receipt.yaml `external_reads` (path, commit,
blob). Undeclared reads fail the run. Keep direct reads few and targeted.

You MUST NOT: read anything under ARCHITECTURE/, AGENT_RUNS/, DEMONSTRATION/ (except your own run directory),
HANDOFFS/BR-HO-0*, any directory named govbridge-sealed-*, or any Claude session transcript; enumerate or content-sweep
the whole repository (no grep -r / rg at the root, no find . / ls -R at the root, no git ls-tree -r over a whole
commit, no git grep without a pathspec); repair, classify or pre-judge any Review-8 finding; state a disposition for
F1; say F2 and F3 are, or are not, one class (the only permitted classification line is
`classification: NOT_DETERMINED_BY_BRIDGE`); cite the withdrawn AR96 positive-control finding as a finding; present
the orchestrator's reasoning errors as evidence for any hypothesis.

For every claim, cite a packet item_id, or an exact (path, commit, lines). For chain queries, verify each stage at
commit 3c880d8 and identify the ACTUAL decision/enforcement point, meaning the code whose evaluated result decides
the concrete behaviour, not an upstream representation of it.

Write <RUN_DIR>/answers.yaml (schema: the packet's section J names it; one entry per query id in section I) and
<RUN_DIR>/receipt.yaml (acknowledge every section-A item with its exact content_sha256, and every supplementary
packet). Run `python -m govbridge receipt check --packet <PACKET_DIR> --receipt <RUN_DIR>/receipt.yaml` and fix your
receipt until it passes. Commit both files on your branch. End with your commit SHA and
`BR-AR-0011 RETURNED <ANSWERED|PARTIAL|BLOCKED>`.
```

## 4. Grading (GRADE, run BR-AR-0012) follows this file's §2.6 and HANDOFFS/BR-HO-0012-grade.md

## 5. Adaptations recorded before any run (OBS-BR-06, run-0)
* The query commands write no supplementary *packets*. Their outputs are saved under `supplementary/queries/`, the
  receipt names only the main packet, and G7 counts the saved outputs' bytes as packet bytes. That count is done by
  the rubric grader, because of OBS-BR-05.
* `run-0-predispatch-g-empty` was compiled and **never dispatched**. The demonstration run is `run-1`, compiled after
  BR-AR-0015.
