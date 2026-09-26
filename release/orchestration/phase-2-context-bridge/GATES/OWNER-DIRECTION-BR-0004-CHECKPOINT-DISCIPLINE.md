# OWNER-DIRECTION-BR-0004: checkpoint discipline

| Field | Value |
|---|---|
| Record | Owner direction (product owner, 2026-09-26), received during the third demonstration freeze, while GRADE was running. The text is transcribed **verbatim** below. |
| Id | **OD-BR-04** |
| Status | IN FORCE from receipt, for this lifecycle. It governs every role dispatched afterwards, and every orchestrator transition. |
| Recorded on | side branch `bridge/orch-pending-0001`, because of the freeze. It merges into the bridge branch after GRADE. |

## Direction text (verbatim)

```text
BRIDGE CHECKPOINT STATUS CHECK + BEHAVIOUR CORRECTION

Do not interrupt, cancel or duplicate valid running work.

First inspect the actual bridge orchestration state and report whether the checkpoint requirements below are already satisfied. Do not infer from Git commits alone.

1. STATUS CHECK

For every completed or materially progressed bridge run (BR-AR-*, architect, oracle author, B1–B6, repair roles, integrator, demonstration roles), report:

run ID;
completion state;
typed report present? YES/NO;
worker checkpoint present? YES/NO;
handoff present where another role consumes its output? YES/NO;
exact commit/output hashes recorded? YES/NO;
unresolved findings/lessons recorded? YES/NO;
next consumer explicitly identified? YES/NO.

Also report:

current outer-orchestrator checkpoint ID;
time/commit of most recent outer checkpoint;
whether a checkpoint occurred after each major lifecycle transition;
whether checkpointing is enforced before context compaction/session handoff rather than merely requested in prompts.

If the current durable state already satisfies these properties through an equivalent typed artefact, identify the exact artefact and explain why it is equivalent. Do not count an ordinary Git commit or narrative ledger entry alone as a worker checkpoint.

2. REQUIRED BEHAVIOUR FROM NOW ON

From this point forward, enforce:

A. Worker completion checkpoint

Every material spawned role must persist, before being considered complete:

run ID / role / model actually used;
input/context manifest hash;
task contract and mutation scope;
files/artifacts changed or produced;
commands/tests run with exit status;
evidence/output hashes;
findings/discoveries;
failed approaches;
unresolved issues;
decisions requested or made within authority;
lessons;
exact next consumer/action;
final commit SHA.

A role without this durable checkpoint must be treated as COMPLETED_PENDING_CHECKPOINT, not fully complete.

B. Outer-orchestrator lifecycle checkpoint

Create/update an outer checkpoint after every material transition, including:

architecture accepted for build;
completion/integration of a DAG node or repair;
freeze/unfreeze;
demonstration completion;
grading completion;
gate transition;
owner decision/CIT;
before handoff to another session;
before anticipated context compaction;
before session close;
whenever the current context is becoming large enough that continuity could depend on conversation memory.

The checkpoint must record:

current lifecycle/gate state;
completed work;
running work with live evidence;
exact bridge commit;
index/store version/hash;
active decisions;
open findings/residuals;
current evidence status;
exact next deterministic action;
enough information for a fresh outer session to resume with no chat history.

C. Pre-compaction rule

Do not rely on the model remembering to checkpoint after compaction has already begun.

When context pressure/compaction risk is detected, first persist and validate a checkpoint, then allow continuation/renewal.

The checkpoint mechanism should be substrate/orchestration-enforced where practical, not prompt-only.

D. Do not manufacture historical evidence

Do not retroactively invent checkpoints claiming to have existed when they did not.

For already-completed bridge roles lacking a formal checkpoint:

reconstruct only from durable evidence;
label these explicitly RETROSPECTIVE_CHECKPOINT_RECONSTRUCTION;
cite the underlying run report/commit/test outputs;
never present reconstructed checkpoints as contemporaneous worker checkpoints.

Only reconstruct historical checkpoints where necessary for safe continuity or independent verification; do not waste hours recreating redundant paperwork.

3. CURRENT WORK

Continue the current demonstration/build path after this check unless a genuine continuity defect requires immediate correction.

Do not restart completed builders merely because their historical checkpoint artefact is missing.

If checkpoint enforcement itself requires a material architecture change or owner trade-off, stop and report:

OWNER_DECISION_REQUIRED: YES

Otherwise record the correction durably and continue.

End the status portion with exactly:

CHECKPOINT_DISCIPLINE: CONFORMING

or

CHECKPOINT_DISCIPLINE: CORRECTION_APPLIED

or

CHECKPOINT_DISCIPLINE: OWNER_DECISION_REQUIRED
```
