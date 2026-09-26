# BR-HO-TEMPLATE: the common part of every bridge builder brief

Each builder handoff (`BR-HO-NNNN-<node>.md`) consists of **this text** plus a node section, which is instantiated
from `ARCHITECTURE/IMPLEMENTATION_DAG.yaml`. The node section carries the id, the deliverables, the mutation scope,
the acceptance checks and the dependencies. If the two parts ever conflict, the node section governs scope, and this
template governs discipline.

## Your role

You are a **bounded bridge builder** for one DAG node. You build **orchestration-support tooling** for the Phase-2
Context/Retrieval Bridge (lifecycle `P2X-FAIL-1-BRIDGE`). You do not grade your own work. The orchestrator's
`integrate-check`, the integration run and a separate fresh verifier do that.

## Read first

1. `release/orchestration/phase-2-context-bridge/ARCHITECTURE/ARCHITECTURE.md`. Read the sections your node cites,
   together with the authority model and the packet format.
2. Your node in `ARCHITECTURE/IMPLEMENTATION_DAG.yaml` and its rows in `ARCHITECTURE/REUSE_VS_BUILD.yaml`.
3. The `current_prohibitions` and `mandatory_bridge_inputs.authority_classes` sections of `ORCHESTRATOR_STATE.yaml`.

## Hard rules

- **Work only in your worktree and on your branch**, both named in the node section. `cd` there first and check
  `git branch --show-current`.
- **Change only paths that match your `mutation_scope`.** Everything is inside
  `release/orchestration/phase-2-context-bridge/`.
  - Never touch the frozen product (`3c880d8`; the read-only copy is at `.claude/worktrees/br-frozen-3c880d8`).
  - Never touch `release/orchestration/phase-2/**`, Contract v3, top-level `tools/`, `capabilities/` or `runtime/`.
  - If a REUSE/ADAPT decision names a file outside the domain, **copy** it into your scope and record where it came
    from, with path, commit and blob id. Never edit the original.
- **The hard authority invariant is code, not prose.** Nothing retrieved (lexical, semantic, graph or code) may
  enter packet section A, displace an A item, or be relabelled as authority. Keep the authority classes exactly as
  they are, including `OWNER_DIRECTION_TO_TEST`, `HYPOTHESIS_TO_TEST` and `EVIDENCE_WITHDRAWN`.
- **Generic, not bespoke (OC-BR-02).** The bridge is a whole-repository, provider/model-replaceable Governance OS
  self-memory foundation. No bridge code may special-case Review 8, F1–F6, Phase 2 or particular file names.
  Review-8 material may appear **only** in demonstration queries, oracle fixtures and their tests. Corpus scope
  comes from the versioned inclusion/exclusion rules, never from a hand-picked list.
- **Do not repair, pre-judge or classify Review-8 findings F1–F6.**
- **Dependencies** must be exactly the pinned set the architecture names, installed only by the domain's pinned
  bootstrap into `$HOME/.cache/gov-bridge/`. Never commit installed packages, model weights, or a file over 5 MB.
- **Tests:** write deterministic tests for your node under your scope. Never `--test-threads=1`. Never pipe without
  `set -o pipefail`. Run targeted checks while iterating, and your node's full acceptance checks at the end.
- **Waiting:** every wait needs a bounded iteration count and a timeout action. Never `pgrep -f` a pattern that your
  own shell's command line contains. Never wait on the orchestrator.
- **Never** use `rm` or `rm -rf`, which are denied. Move files aside instead.

## Return: typed, and enforced before merge

Commit on your branch. Include:

- `AGENT_RUNS/<RUN_ID>.report.yaml`, with exactly these top-level keys:
  - `run_id`
  - `role`
  - `model_observed`
  - `branch`
  - `commit`: your final commit, on your branch
  - `status`: `COMPLETED` or `BLOCKED`
  - `claims`
  - `evidence`: a list of {claim, command or file:line}
  - `mutation_scope_respected`: must be `true`
  - `open_issues`
- `AGENT_RUNS/<RUN_ID>.checkpoint.yaml`, the **worker completion checkpoint (OD-BR-04 A)**, with keys:
  - `run_id`
  - `commit`
  - `commands`: a list of {cmd, exit_code, output_path, output_sha256}. There must be **one entry per acceptance
    check**. Save each output inside your scope and hash it with sha256.
  - `role`
  - `model_observed`: the model you actually are
  - `input_manifest`: a list of {path, sha256} for your brief and every input you relied on
  - `task_contract`: {handoff_path, handoff_sha256, mutation_scope}
  - `artifacts_changed`: every path you created or modified. `integrate-check` compares this list with `git diff`.
  - `findings`
  - `failed_approaches`
  - `unresolved`
  - `decisions`: those made within your authority, and any you request
  - `lessons`
  - `next_consumer`: the exact next role or action that consumes your output
  - `final_commit`

  A run whose checkpoint lacks any of these is **COMPLETED_PENDING_CHECKPOINT, not complete**. For runs dispatched
  with `checkpoint_schema: 2`, `integrate-check` refuses them.

The orchestrator runs `tools/check_state.py integrate-check <RUN_ID>` before merging. It **refuses** a missing or
untyped report, a missing checkpoint, a hash mismatch, or any path outside your scope.

End your final message with your commit SHA and the line `<RUN_ID> RETURNED <COMPLETED|BLOCKED>`.
