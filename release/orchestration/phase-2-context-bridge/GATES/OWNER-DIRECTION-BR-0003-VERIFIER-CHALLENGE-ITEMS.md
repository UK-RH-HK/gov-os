# OWNER-DIRECTION-BR-0003: challenge items the independent verifier must carry

| Field | Value |
|---|---|
| Record | Owner direction (product owner, 2026-09-26), received mid-session during the third demonstration freeze. The text is transcribed **verbatim** below. |
| Id | **OD-BR-03** |
| Status | IN FORCE for this lifecycle. It adds verifier challenge items and amends nothing else. |
| Binding on | the build-stage orchestrator, which must carry these items in `HANDOFFS/BR-HO-VERIFY-*.md` **before** it issues `P2_CONTEXT_RETRIEVAL_BRIDGE_BUILT`; and the independent verifier, which must test each one rather than accept it silently |
| Durability note | Recorded on side branch `bridge/orch-pending-0001`, cut from the frozen tip `94d0211`, so the demonstration view does not move. It merges into the bridge branch after GRADE. |

## Direction text (verbatim)

```text
Continue run-1 as planned. No owner decision is required.

Before issuing P2_CONTEXT_RETRIEVAL_BRIDGE_BUILT, ensure the durable verifier handoff explicitly carries the following as challenge items rather than silently accepting them:

test whether the seed-derived code route's failure to honour retrieval_exclusions can expose content excluded by the security policy or create an alternate retrieval bypass;
test whether the limited number of formal checkpoint artefacts satisfies the bridge's enforced-checkpoint requirement, given that most intermediate durability currently comes from sealed state + ledger commits;
retain OBS-BR-04/05/06 and the unwired Python-AST route as explicit residuals;
measure the run-1 context packet size/tokens and record which supplied artefacts the fresh agent actually consumed;
do not treat successful retrieval of the Review-8 answer as sufficient if the agent merely receives the answer or oracle indirectly — demonstrate reconstruction from legitimate repository evidence and preserve the secrecy audit.

Do not stop or restart valid work. Continue through the existing build-stage plan and stop only at P2_CONTEXT_RETRIEVAL_BRIDGE_BUILT or a genuine owner-level trade-off.
```

## How the orchestrator discharges each item

| # | Item | Orchestrator action before BUILT | Verifier challenge |
|---|---|---|---|
| 1 | The seed-derived code route ignores `retrieval_exclusions` | Carry it as a named challenge. The code layer itself honours the corpus-rule exclusions: B3R, with 0 leaked rows for the 11 `X-SEC-CONTENT` blobs. `retrieval_exclusions` is a separate, task-level list, covering for example `ARCHITECTURE/**` and `DEMONSTRATION/**`. | Test whether a seed citation into an excluded path, whether security-excluded or task-excluded, surfaces its content in G or H, or opens another bypass. |
| 2 | Few formal checkpoint artefacts | State the facts: `CHECKPOINTS/` holds BR-CP-0001/0002. Durability otherwise comes from the sealed state (hash-checked by `verify`), the ledger, per-run typed reports and checkpoints (enforced by `integrate-check`), and role-branch commits. | Judge whether this meets "enforced checkpoints rather than prompt-only checkpoint requests". |
| 3 | Residuals | Keep OBS-BR-04 (sealed path visible in state), OBS-BR-05 (G7 1% check disabled in the grader), OBS-BR-06 (no supplementary packets) and the unwired Python-AST route in the handoff, explicitly. | Confirm or reclassify each. |
| 4 | run-1 size and consumption | Measure `packet.md`/bootstrap bytes, the actual input tokens from the demonstration agent's transcript usage, and the artefacts it actually opened (transcript extraction). Record them in §5 of the handoff. | Re-derive them from the transcript. |
| 5 | Reconstruction, not receipt of the answer | Preserve the secrecy audit, which checks the demonstration agent's tool calls for the sealed path and the oracle. Record which inputs **legitimately** carry Review-8 conclusions: section A includes the Review-8 return and the context pack as mandatory inputs by owner design. The grade must therefore rest on **verification at `3c880d8`**, meaning code anchors the agent read and checked, not on restating the return. | Judge whether the chains were reconstructed from repository evidence (verified anchors, enforcement points read in code) rather than copied from the return or the context pack. Test whether any oracle content reached the agent. |
