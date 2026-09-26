# OWNER-DIRECTION-BR-0005: retrieval completeness across multiple batches and hops

| Field | Value |
|---|---|
| Record | Owner direction (product owner, 2026-09-26), received during the third demonstration freeze, while GRADE was running. The text is transcribed **verbatim** below. |
| Id | **OD-BR-05** |
| Status | IN FORCE. It is a bridge behaviour and verification requirement **before bridge acceptance**. The orchestrator will build it before `P2_CONTEXT_RETRIEVAL_BRIDGE_BUILT` (see the assessment below), and also carries it into the verifier handoff. |

## Orchestrator assessment at receipt, from the code at the bridge tip `94d0211`

* **No hard-coded 8k limit.** The only 8000 in the code is `BINARY_SNIFF_BYTES`, the size of the binary-detection
  sniff. Packet budgets are configurable profiles in `config/budgets.yaml` (bounded-builder 100 KB, synthesis 360 KB).
* **NOT conforming, and the gap is real:**
  * Every route (lexical, semantic, code, exact) and the compiler take a **fixed top-k**, default 8, for a **single
    round per query** (`packet.py` ~609–617; `real_routes.py`).
  * No route supports paging, offset or continuation.
  * No retrieval stopping reason is recorded.
  * The bridge has no facet decomposition, no parallel facet retrieval and no adaptive follow-up.
  * Multi-hop exists only as graph traversal: `why`/`impact` depth, and G's T1→T2 expansion.
* In demonstration run-1, the multi-round adaptive retrieval (103 query invocations) was done **by the worker**, not
  by the bridge.

## Direction text (verbatim)

```text
BRIDGE RETRIEVAL COMPLETENESS CLARIFICATION — MULTI-BATCH / MULTI-HOP

Do not interrupt or restart valid running work. Incorporate this as a bridge behaviour/verification requirement before P2_CONTEXT_RETRIEVAL_BRIDGE_BUILT, or carry it explicitly into the independent verifier handoff if the current demonstration is already frozen.

Confirm that no retrieval route treats an 8k-token/chunk/result budget, fixed top-k, or single semantic query as the maximum evidence available to answer one task.

A single task/question must support multi-batch and multi-hop retrieval when its evidence exceeds one retrieval window.

Required behaviour:

1. Query decomposition
Decompose a complex task into independent evidence facets where appropriate, e.g.:

purpose/WHY;
requirements/Contract;
active decisions;
history/failed approaches;
dependencies/impact;
implementation/code;
final enforcement point;
tests/findings/evidence.

2. Parallel retrieval
Independent facets MAY be retrieved concurrently where this is deterministic/safe.

Example:

task
 ├─ WHY/history retrieval
 ├─ decision retrieval
 ├─ code/symbol retrieval
 ├─ graph/impact retrieval
 └─ tests/findings retrieval

3. Sequential/adaptive retrieval
Retrieval MUST also support follow-up rounds when earlier evidence discovers:

a new identifier;
dependency;
decision;
caller/callee;
test;
historical repair;
superseding record;
enforcement point;
unexplained gap.

The next query may therefore be generated from the evidence returned by the previous query.

4. Retrieval continuation
A per-query budget such as 8k tokens is a batch/context-control value, NOT an evidence-completeness boundary.

If relevant evidence exceeds one batch, continue retrieval through additional batches/pages/facets until a deterministic stopping criterion is met.

5. Completeness criterion
Do not stop merely because top-k results were returned.

Record why retrieval stopped, for example:

required authoritative inputs resolved;
required dependency edges traversed;
requested evidence facets covered;
no unresolved cited identifiers/dependencies remain;
additional retrieval adds only duplicates/low-value material;
explicit task/context budget reached, with unresolved coverage disclosed.

6. Merge before compilation
Across all retrieval rounds:

deduplicate;
reconcile versions;
filter superseded/current state;
apply authority rules;
preserve provenance;
preserve evidence-to-claim links.

Do not summarise away critical evidence merely to fit a retrieval batch.

7. Context larger than one model packet
If the complete supporting evidence exceeds the final worker context budget, support hierarchical synthesis:

evidence batches
  → evidence-grounded intermediate notes/claims
  → each retains source IDs/hashes/citations
  → final synthesis consumes those records + mandatory sources

Intermediate synthesis must not become an authority source and must remain traceable to original evidence.

8. Mandatory inputs remain separate
Multi-batch semantic retrieval must never substitute for deterministic mandatory-authoritative-input resolution.

9. Demonstrate it
Before bridge acceptance, include at least one test/query whose correct answer deliberately requires relevant evidence from multiple distant repository locations and exceeds a single retrieval batch.

Demonstrate:

multiple retrieval calls occurred;
parallel retrieval where independent;
sequential follow-up where evidence introduced new dependencies;
merged evidence remained provenance-bound;
the resulting answer/context covered all required facets.

Record telemetry for retrieval rounds, candidate tokens/chunks, deduplicated tokens/chunks, final compiled size, and stopping reason.

Do not hard-code 8k as the architecture limit. It may be a configurable per-retrieval batch size only.
```
