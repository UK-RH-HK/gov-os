# OWNER-AMENDMENT-P2-0010 — Conditional early V8.3 Context/Retrieval Bridge

| Field | Value |
|---|---|
| Record | Owner amendment (product owner, 2026-09-24) |
| Id | **OD-P2-10** |
| Status | IN FORCE. Amends OD-P2-09 **only** in the conditional case below. All other instructions remain binding. |
| Scope | Conditional on Review 8's outcome. Changes nothing before Review 8 except §1's added step. |

## 1. The pre-Review-8 sequence gains one required step

```
AR95 completion
    ↓
pre-final owner-question sweep            (OD-P2-09 §4, mandatory)
    ↓
whole-system / impact CONTEXT PACK        (NEW — mandatory, this record)
    ↓
fresh independent Review 8
```

**None of these may be skipped**, and Review 8's independence requirement is unchanged. V8.3 is **not** to be built
before Review 8 in anticipation of failure.

## 2. If Review 8 passes — route unchanged

Mint the exact immutable candidate → fresh formal Phase-2 verification → `GOVERNANCE_CAPABILITY_BASELINE_ACCEPTED` →
fresh V8.3 architecture/build/review session → V8.3 accepted and activated → Phase 3 → `PROVISIONAL_RETRIEVAL_PROFILE_READY`
→ Phase 4.

## 3. If Review 8 fails with another blocking HIGH

**Do NOT immediately enter another narrow local repair/review cycle.** Freeze the Phase-2 product implementation.

Before further Phase-2 product repair, create a **separate fresh session** whose only purpose is the

> **V8.3 CONTEXT / RETRIEVAL BRIDGE**

— the minimum context/retrieval capability needed to give future agents strong whole-system memory and reasoning
context. This is an explicit, **narrow** exception to "V8.3 work begins only after Phase-2 acceptance."

It is **orchestration/development infrastructure only**. It does **not** become the accepted Governance OS product,
the Phase-2 candidate, a normative authority source, proof that Phase 3 is accepted, a replacement for Contract v3,
or a replacement for deterministic mandatory-input resolution. **V8.2 remains the normative Phase-2 control-plane
definition while Phase 2 is unfinished.**

## 4. Why the exception exists — the owner's reasoning, recorded verbatim in substance

> The purpose is to stop developing Governance OS while its own agents are effectively deprived of the memory/context
> system Governance OS is intended to provide.

A repair/review agent should be able to understand **why** a mechanism exists, **what** requirement it satisfies,
**which** decisions created or constrain it, **what** depends on it and what it depends on, **which** previous
approaches failed, **which** lessons apply, **what** can safely be deleted, and **what** the whole-system consequence
of a change is — *without reading the full repository or relying on chat history.*

```
independence  =  independent reasoning + COMPLETE RELEVANT CONTEXT
independence ≠  independent reasoning + architectural ignorance
```

## 5. Minimum bridge scope — build only these eighteen

canonical worker bootstrap; deterministic mandatory-authoritative-input resolver; structured current-state lookup;
exact retrieval; lexical retrieval; dependency/impact graph traversal; semantic/vector retrieval on the existing
replaceable architecture where available; code/symbol/reference relationship retrieval where available; authority
filtering; lifecycle current-vs-superseded filtering; provenance; bounded context compiler; exact context manifest
with IDs/versions/hashes; context-packet provenance/hash; worker consumption receipt; checkpoint/renewal support;
historical lesson/failure retrieval; and the system-purpose chain

```
product purpose → requirement → owner decision → architecture → dependency
  → implementation → tests → findings → lessons → current status
```

**Do not build unrelated V8.3 features simply because this session exists.**

## 6. Authority model — preserved

```
AUTHORITATIVE INPUTS            → resolved deterministically
GRAPH / DEPENDENCY STATE        → what is connected
LEXICAL / SEMANTIC / CODE       → suggests potentially relevant supplementary material
```

**Retrieval must never silently replace an authoritative mandatory input.** A semantically strong historical result
must never outrank a current authoritative decision or specification merely because it scores higher.

## 7. Resuming Phase 2 with the bridge — the anti-snowball rule

Once the bridge can construct reliable bounded context, return to the frozen Phase-2 problem. **Before any
implementation:**

```
finding → whole-system retrieval/context pack → fresh architecture/root-cause synthesis
```

That synthesis must classify the response as exactly one of:

`REPAIR EXISTING MECHANISM` · `REUSE EXISTING PRIMITIVE` · `DELETE MECHANISM` · `NARROW REQUIREMENT` ·
`DEFER TO LATER LIFECYCLE` · `OWNER DECISION`

**Only then may Phase-2 product code change.** The objective is to prevent the exact loop this phase has been in:

> local finding → new local mechanism → reviewer attacks new mechanism → another mechanism

when the whole-system architecture might have supported a simpler answer.

## 8. Phase 2 is not waived

After any bridge-assisted repair: freeze → fresh independent adversarial review → exact candidate → fresh formal
Phase-2 verifier. Phase 2 completes only on `GOVERNANCE_CAPABILITY_BASELINE_ACCEPTED`.

## 9. After acceptance

Reconcile the successful bridge into the full V8.3 design; complete the remaining V8.3 requirements; run a fresh
independent V8.3 review before making V8.3 CURRENT. **Do not throw the bridge away and rebuild retrieval from
scratch unless evidence requires it** — it becomes implementation/evidence input to final V8.3.

## 10. Phase 3 becomes qualification, not re-engineering

If retrieval mechanics were substantially built in the failure branch, **do not redo the engineering** because Phase 3
has formally started. Phase 3 qualifies the already-built profile, testing at minimum: authoritative-input delivery;
exact, lexical, semantic, graph and code retrieval; authority filtering; stale/superseded filtering; a hidden memory
oracle; dependency/impact accuracy; rebuildability; delete/rebuild behaviour; Recall@K or accepted equivalent;
MRR/ranking or equivalent; false positives; wrong-indexing; stale-index count; latency; context size; token
efficiency; context flooding; missing-index cases; model/session handoff; Gate-W consumption continuity.

**The Phase-3 acceptance gate is not skipped** — it may simply be short.

## 11. Cost and simplicity

> Use **complete relevance, not complete repository loading.**

Bounded packets. Deterministic filtering before model reasoning. **No LLM invocation solely to determine that nothing
relevant changed.** Do not build a retrieval system whose operation costs more than the engineering it supports. The
~10–20% routine-overhead objective (OD-P2-09 §16, recorded in `V8_3_EVIDENCE_PACKAGE.md` §10) remains.

## 12. Owner return conditions

Return to the owner if: Review 8 passes and formal acceptance later finds an owner-level issue; **or** Review 8 fails
and the bridge requires a genuinely new product/security/authority trade-off; **or** evidence shows the
memory/retrieval architecture itself must materially change from the accepted design. Otherwise execute the
conditional route autonomously.
