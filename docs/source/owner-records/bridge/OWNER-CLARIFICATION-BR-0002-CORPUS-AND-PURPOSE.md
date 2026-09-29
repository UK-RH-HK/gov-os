# OWNER-CLARIFICATION-BR-0002: bridge corpus and purpose

| Field | Value |
|---|---|
| Record | Owner clarification (product owner, 2026-09-25), received mid-session while BR-AR-0001 was running. It is transcribed **verbatim** below. |
| Id | **OC-BR-02** |
| Status | IN FORCE for this lifecycle. It clarifies OWNER-LAUNCHER-BR-0001 and OD-P2-10 §5 and amends neither. |
| Applies to | BR-AR-0001, before its architecture is frozen, and every later bridge role |
| Supersedes | Nothing. BR-HO-0001 §1 ("Build the minimum that makes this true") and §2.2 item 1 ("which sources are indexed") are read in light of this record. **The minimum is now the minimum *generic whole-repository* foundation, not the minimum Review-8 mechanism.** |

## What changes for BR-HO-0001, as read by the orchestrator (the verbatim text governs)

1. **Corpus boundary.** The corpus is the **whole canonical Governance OS repository**. The exclusions are secrets,
   generated, binary and build artefacts, and anything that policy marks non-indexable. It is **not** the Review-8
   records.
2. **Purpose.** The purpose is a **generic, reusable Governance OS self-memory/context foundation**. It must be
   **provider/model-replaceable**. It must **not** be a bespoke Phase-2 or Review-8 retrieval mechanism.
3. **Review 8.** Review 8 (F1/F2/F3) is the **first mandatory benchmark/oracle case**. It is not the corpus boundary,
   and it must not bias the design.
4. **Code location and read scope.** Code may still physically live under
   `release/orchestration/phase-2-context-bridge/`, which keeps the frozen-product boundary. Its **read/index scope
   spans the canonical repository**. The mutation boundary is unchanged: the bridge still **writes** nothing outside
   its domain.
5. **Ten items the architecture must now define explicitly:**
   1. corpus inclusion/exclusion rules
   2. document/chunk/record identity and provenance
   3. incremental freshness/invalidation
   4. the structured, exact, lexical, semantic, graph and code routes
   5. current-vs-superseded and authority filtering
   6. whole-repository dependency/WHY lineage
   7. bounded context compilation
   8. deterministic rebuildability
   9. replaceable embedding/index/runtime interfaces
   10. **the promotion/reconciliation path into full V8.3**, so that the bridge does not become throwaway Phase-2 tooling (consistent with OD-P2-10 §9)

Unchanged:

* OD-P2-10A/B and the authority classes in `mandatory_bridge_inputs`;
* the hard authority invariant;
* the prohibitions: no product mutation, no F1/F2/F3 repair, no Phase-3A research, no final model bake-off, V8.3
  not CURRENT, and the bridge is not an authority source;
* the two tokens (`…_BUILT` is ours; `…_READY` is the independent verifier's).

## Clarification text (verbatim)

```text
OWNER CLARIFICATION — BRIDGE CORPUS AND PURPOSE

Continue the current P2X-FAIL-1 bridge session; do not restart completed bootstrap work.

Clarification before BR-AR-0001 architecture is frozen:

The Context/Retrieval Bridge is not a retrieval system for Review 8 or F1/F2/F3 specifically.

Its retrieval/memory corpus is the whole canonical Governance OS repository, subject to proper exclusions for secrets, generated/binary/build artefacts and anything policy marks non-indexable.

The bridge should establish a generic, reusable Governance OS self-memory/context foundation covering, as applicable:

Contract/constitution/policies;
owner decisions and active/superseded architecture;
specifications and requirements;
source code;
tests and evidence;
research/reports;
lessons and failed approaches;
migrations;
capabilities/plugins/tools;
orchestration/checkpoint/handoff history;
dependency and impact relationships;
temporal/current-vs-superseded lineage.

Review-8 F1/F2/F3 are benchmark/oracle cases, not the retrieval corpus boundary.

BR-AR-0001 must therefore design a provider/model-replaceable whole-repository indexing and retrieval architecture. It may optimise implementation effort for this temporary bridge, but it must not create a bespoke Phase-2 or Review-8 retrieval mechanism.

The bridge implementation may physically live under release/orchestration/phase-2-context-bridge/ to preserve the frozen Phase-2 product boundary, but its read/index corpus must span the canonical Governance OS repository.

The architect must explicitly define:

corpus inclusion/exclusion rules;
document/chunk/record identity and provenance;
incremental freshness/invalidation;
structured/exact/lexical/semantic/graph/code routes;
current-vs-superseded and authority filtering;
whole-repository dependency/WHY lineage;
bounded context compilation;
deterministic rebuildability;
replaceable embedding/index/runtime interfaces;
how this bridge can later be promoted/reconciled into full V8.3 instead of becoming throwaway Phase-2 tooling.

Review 8 remains the first mandatory demonstration because it is a difficult known case. It must not bias the architecture into a Review-8-specific solution.

Proceed with BR-AR-0001 after recording this clarification durably.
```
