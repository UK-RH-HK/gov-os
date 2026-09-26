# OWNER-DIRECTION-BR-0006: durable record of the bridge's architecture and continuity requirements

| Field | Value |
|---|---|
| Record | Owner direction (product owner, 2026-09-26). The text is transcribed **verbatim** below. |
| Id | **OD-BR-06**. The owner's example filename was `…BR-0005-CONTEXT-RETRIEVAL-AND-CONTINUITY.md`. **BR-0005 is already taken** by OD-BR-05 (`OWNER-DIRECTION-BR-0005-MULTI-BATCH-MULTI-HOP-RETRIEVAL.md`), so this record is numbered BR-0006 to keep ids unique. It consolidates OC-BR-02, OD-BR-04 and OD-BR-05 and makes them durable. |
| Status | **IN FORCE** as an owner instruction for this bridge lifecycle, and as a **required carry-forward input to full V8.3**. It is **NOT** an amendment to Contract v3, and it is not normative there unless a later CIT or owner-approved contract evolution explicitly makes it so. |
| Survives | context compaction; outer-session replacement; bridge verification; Phase-2 resumption; full V8.3 reconciliation; Phase-3 retrieval qualification; later project adoption |
| Related records | OC-BR-02 (corpus and purpose), OD-BR-03 (verifier challenge items), OD-BR-04 (checkpoint discipline), OD-BR-05 (multi-batch / multi-hop retrieval) |
| Recorded on | side branch `bridge/orch-pending-0001`, because of the demonstration freeze (GRADE was running). It merges into the bridge branch, and is added to `ORCHESTRATOR_STATE.yaml` with its sha256, when the freeze lifts. |

## Direction text (verbatim)

```text
OWNER DIRECTION — DURABLE RECORD OF BRIDGE ARCHITECTURE AND CONTINUITY REQUIREMENTS

Record the decisions and corrections below durably so they survive:

context compaction;
outer-session replacement;
bridge verification;
Phase-2 resumption;
full V8.3 reconciliation;
Phase 3 retrieval qualification;
later project adoption.

Do not modify the frozen Phase-2 product or Contract v3.

Create an explicit owner record in the bridge governance domain, e.g.

GATES/OWNER-DIRECTION-BR-0005-CONTEXT-RETRIEVAL-AND-CONTINUITY.md

Treat it as owner instruction for this bridge lifecycle and required carry-forward input to full V8.3, but not as an amendment to Contract v3 unless a later CIT/owner-approved contract evolution explicitly makes it normative there.

1. Whole-repository memory foundation

The Context/Retrieval Bridge is a reusable Governance OS self-memory/context foundation over the whole canonical Governance OS repository.

Review-8 F1/F2/F3 are benchmark/oracle cases, not the corpus boundary.

Preserve whole-repository coverage across:

requirements/Contract;
constitution/policies;
owner decisions/CIT;
architecture/specifications;
code;
tests/evidence;
reports/research;
lessons/failed approaches;
migrations;
capabilities/tools/plugins;
orchestration/checkpoint/handoff history;
current/superseded lineage;
dependency/impact relationships.
2. Retrieval completeness

A fixed top-k or per-query token budget is not an evidence-completeness limit.

In particular, an 8k retrieval allowance is a configurable retrieval batch size only.

A single task may require:

8k + 8k + 8k + ...

across multiple repository locations before enough evidence has been collected.

Retrieval must support:

multiple batches;
pagination/continuation;
multiple facets;
adaptive follow-up;
multi-hop retrieval;
provenance-preserving merge;
deduplication;
authority/current/superseded filtering;
an explicit stopping reason.
3. Parallel + sequential retrieval

Support both.

Independent evidence facets should be retrievable in parallel where safe:

WHY | decisions | code | graph | tests | history

Evidence discovered by those searches may then trigger sequential/adaptive retrieval for newly discovered identifiers, dependencies, callers, decisions, tests, historical failures or enforcement points.

Therefore the intended pattern is:

task
  ↓
parallel facet retrieval
  ↓
merge / authority / lifecycle filtering
  ↓
identify unresolved dependencies
  ↓
sequential follow-up retrieval
  ↓
repeat until stopping criterion
  ↓
bounded context compilation
4. Evidence larger than the final context budget

If complete relevant evidence is larger than one final model context packet, use hierarchical evidence synthesis.

Intermediate summaries/notes must:

remain derived, not authoritative;
retain source IDs/hashes/citations;
preserve claim-to-source lineage;
disclose unresolved evidence;
be rebuildable from original evidence.

Do not silently discard critical evidence merely because one packet is full.

5. BGE position

BAAI/bge-small-en-v1.5 is a provisional bridge embedder, not the final Governance OS retrieval model.

Keep:

provider/model replaceability;
pinned model/revision/licence/dimensions;
deterministic reindexing;
model-independent index/provider interfaces.

Phase 3A/3B/3C may replace or augment it after broader evaluation.

6. Mandatory authority remains separate

Semantic/vector, lexical, graph and code retrieval are supplementary.

They may never substitute for deterministic mandatory-authoritative-input resolution.

Mandatory inputs must remain explicitly identifiable in the compiled context.

7. Checkpoint discipline

The checkpoint correction applied during this bridge is now a required orchestration behaviour:

material worker completion → typed worker checkpoint;
material lifecycle transition → outer-orchestrator checkpoint;
gate/decision/CIT → checkpoint;
handoff/model/session switch → checkpoint;
before anticipated compaction → checkpoint;
before session close → checkpoint.

A normal Git commit or narrative ledger entry alone is not a substitute for the required checkpoint semantics.

Worker checkpoints must preserve:

input/context manifest hash;
role/model;
task/mutation scope;
outputs;
tests/commands;
evidence hashes;
findings;
failed approaches;
lessons;
unresolved issues;
next consumer/action;
final commit.

Historical reconstruction must remain labelled RETROSPECTIVE_CHECKPOINT_RECONSTRUCTION.

8. Compaction / fresh-session continuity

Ensure a fresh outer session does not need conversation history.

Update the resume path so that after compaction/session replacement a fresh orchestrator reads, in deterministic order:

bridge ORCHESTRATOR_STATE.yaml;
latest validated outer checkpoint;
this owner direction;
active owner decisions;
latest ledger transition;
current handoff / running-work record;
exact next deterministic action.

The latest checkpoint must carry enough state to resume immediately.

If hook-based pre-compaction checkpointing is not confirmed active in the current session, continue manually checkpointing before compaction/session closure.

9. Carry forward into later phases

Also add these lessons/requirements to the appropriate non-normative V8.3 evidence/handoff artefact so the future full V8.3 architecture session explicitly receives:

whole-repository retrieval, not Review-8-specific retrieval;
multi-batch/multi-hop retrieval;
parallel + sequential retrieval;
explicit retrieval stopping criteria;
hierarchical evidence synthesis;
checkpoint enforcement;
provisional/replaceable BGE;
mandatory-authoritative inputs separate from supplementary retrieval.

Do not silently transform this evidence package into normative Contract authority.

10. Verification

Add the owner record to the bridge state as an active applicable instruction and hash-bind it.

Make the final bridge verifier handoff explicitly challenge whether these requirements are actually implemented rather than merely documented.

After recording this, continue the current bridge plan autonomously.

Report back with:

OWNER_DIRECTION_RECORDED

plus the commit SHA, record path, latest checkpoint ID, and the future-V8.3 carry-forward artefact updated.
```
