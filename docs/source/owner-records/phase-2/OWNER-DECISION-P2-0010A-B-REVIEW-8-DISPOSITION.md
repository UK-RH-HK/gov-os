# OWNER-DECISION-P2-0010A / 0010B — Review-8 disposition

| Field | Value |
|---|---|
| Record | Owner decision (product owner, 2026-09-25) |
| Ids | **OD-P2-10A** (F2 scope classification), **OD-P2-10B** (Review-8 failure bridge), plus two explicitly **non-final** directions |
| Status | IN FORCE. Extends OD-P2-09 and OD-P2-10. |
| Subject | P2-AR-0097 (Review 8) at frozen commit **`3c880d8`**; review committed at `58219d5` |
| Product state | **FROZEN at `3c880d8`. Not to be modified.** |

## OD-P2-10A — F2 is NOT scope expansion

The owner overrules the OD-P2-09 §5 table's "old/untouched core ⇒ STOP as scope expansion" reading for this finding,
and agrees with Review 8's own argument.

> F2 is a **newly discovered implementation defect within the already-existing Phase-2 authority / Property-C
> requirements**. Correcting it does not introduce a new Governance OS capability or expand the Phase-2 product
> scope.

**F2 therefore remains a legitimate Phase-2 blocker.**

**However, F2 is not to be repaired yet.** The Review-8 failure bridge is activated and the product remains frozen
until the bridge-assisted whole-system synthesis determines the minimum correct disposition.

## OD-P2-10B — the Review-8 failure bridge is authorised and starts now

Built in a **separate fresh outer session / worktree / domain**, under the agreed **`P2X-FAIL-1`** process. It is
**orchestration support only** and must not modify:

* the frozen Phase-2 product;
* Contract v3;
* the frozen Phase-2 acceptance contract;
* existing authority / trust semantics.

Its acceptance token is **`P2_CONTEXT_RETRIEVAL_BRIDGE_READY`**, independently earned. Only after that does the next
action occur: **fresh whole-system root-cause synthesis, before any Phase-2 product repair.**

## F1 — owner direction recorded, NOT yet authority to act

F1 (the creator-liveness exemption accepting a dead-but-unreaped creator, reopening AR94-C1) is recorded as a
**strong deletion / simplification candidate**, because:

* the sandbox exemption has now failed under **multiple successive mechanisms** — path shape (AR92-C2), OS marker
  plus `(device, inode)` (AR94-C1), creator liveness (F1); and
* Review 8 reports, having verified both call sites itself, that **no production consumer requires the
  cross-process signal**.

> **This is not yet authority to delete it.**

The bridge-assisted synthesis must reconstruct the exemption's **purpose, consumers, dependencies and consequences**
and determine which of these is correct:

```
DELETE  /  SIMPLIFY  /  REPAIR  /  NARROW  /  RETAIN
```

**Prefer deletion if no required production capability depends on it.**

## F2 / F3 — classification hypothesis, NOT yet a final owner decision

The synthesis must **explicitly investigate** whether F2 and F3 are manifestations of one deeper defect class:

> **syntactic rule/property reasoning that fails to trace through composition / precedence / matching to the actual
> enforced semantic effect.**

> **Do not pre-classify them as the same class merely because the owner has suggested the hypothesis.** The
> bridge-assisted independent synthesis must test it against the implementation and the historical evidence.

## Property A

The Review-8 evidence that **Property A has held for a fourth consecutive independent round** is preserved. It is not
to be reopened or modified without new evidence that **directly falsifies** it.

## Standing state after this record

**Remain stopped. The Phase-2 product is frozen. No repair agent is to be dispatched.** The next Phase-2 product
action occurs only after the separate bridge reaches `P2_CONTEXT_RETRIEVAL_BRIDGE_READY` **and** the whole-system
synthesis has completed.
