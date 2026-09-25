# BR-ARCH-RULING-1: a mandatory input is never moved out of section A because of its lifecycle

| Field | Value |
|---|---|
| Record | Orchestrator ruling (2026-09-25). It resolves a conflict between an architecture-internal rule and owner text, in favour of the owner text. **It is not an owner decision.** A later verifier may challenge it. |
| Trigger | B6 (BR-AR-0008) compiled the real demonstration task. **Ten mandatory items were placed in section H (supplementary retrieved context)** with notice `MANDATORY_ITEM_NOT_IN_A`. They were Contract v3 (`CONTRACT`), the frozen gate contract (`FROZEN_GATE_CONTRACT`), the owner launcher (`OWNER_DECISION`), the Review-8 return and the AR96 checkpoint (`EVIDENCE`), and the context pack, two design records, the Phase-2 ledger and the Phase-2 state (`ORCHESTRATION_RECORD`). |
| Cause | `govbridge/compile/packet.py:178` admits a mandatory item into A only if `lifecycle == ACTIVE`. Three rules then compound. Files without a machine-readable status line map to lifecycle `UNKNOWN` (ARCHITECTURE.md §5.1). Registry entries may only restrict, never raise a lifecycle (§5.2). And `UNKNOWN` is "never treated as ACTIVE". So a contract whose file has no status row can **never** reach A. |

## Ruling

**Section A membership is decided by the deterministic resolver, together with the class's admissibility in A. Lifecycle
never decides it.**

1. Every item the resolver returns whose class is admissible in A (ladder ranks 1–6) is placed in **A**, with delivery
   `MANDATORY`. This holds **whatever its lifecycle**.
2. Lifecycle stays **visible and honest**. A mandatory A item whose lifecycle is not `ACTIVE` (that is `UNKNOWN`,
   `PROPOSED`, `HISTORICAL`, `SUPERSEDED` or `WITHDRAWN`) carries a lifecycle banner. It is also listed in **J** as
   `MANDATORY_LIFECYCLE_NOT_ACTIVE`, so the orchestrator sees the classification gap or the stale task spec. **Nothing
   is relabelled ACTIVE.**
3. Lifecycle **continues** to gate **D.1** (active decisions only) and the within-section **ordering** (§5.3 item 5).
   A retrieved item can still never outrank a current one, and never enters A or D.1.
4. Non-ladder mandatory items keep their class placement (§5.1), pinned and delivered `MANDATORY`:
   * `OWNER_DIRECTION_TO_TEST` goes to D.2;
   * `HYPOTHESIS_TO_TEST` goes to D.3;
   * `HYPOTHESIS_RELEVANT_OBSERVATION` goes to F;
   * `EVIDENCE_WITHDRAWN` goes to E or F;
   * `UNCLASSIFIED` goes to H.

   An `UNCLASSIFIED` mandatory item still raises a J notice.
5. `compile/validate.py` enforces the same rule by re-derivation. It **refuses** any packet in which a
   resolver-returned, A-admissible item appears anywhere other than A.

## Authority for the ruling

* Launcher BR-0001: *"A. MANDATORY AUTHORITATIVE INPUTS"*; *"Semantic/lexical/graph/code retrieval may enrich context but
  may NEVER substitute for deterministic mandatory authoritative inputs."*
* OD-P2-10 §6: *"Retrieval must never silently replace an authoritative mandatory input."* Delivering Contract v3 as
  "supplementary retrieved context" is exactly that substitution, even when a notice is attached.
* ARCHITECTURE.md §5.3 item 6 (W10): *"retrieval/index outage does not erase deterministic required dependencies"*.
  Lifecycle labelling must not erase them either.
* Nothing here raises any class or lifecycle. The architecture's fail-closed intent is preserved: `UNKNOWN` is never
  treated as `ACTIVE`. The only change is that it no longer **removes** a required input.

## Implementation

The implementation is BR-AR-0013 (B6R, a fresh builder). Its scope is `govbridge/compile/**`, `tests/compile/**` and
`tests/fixtures/compile/**`. Handoff: `HANDOFFS/BR-HO-0013-b6r-mandatory-in-a.md`.

## Addendum A1: the grading consequence (2026-09-25, recorded before any demonstration run and without reading the oracle)

`ARCHITECTURE/DEMONSTRATION_DESIGN.md` §4 G3 contains the **[D]** clause *"section A or D.1 contains a non-ladder class
or a non-`ACTIVE` lifecycle"*. That clause predates this ruling. Read literally, it would fail every packet that
obeys the ruling. **It is read as follows, and I1's `demo grade` must implement this reading:**

* **Section A** fails G3 in any of these cases:
  * it contains a **non-ladder class**;
  * it contains **any item not returned by the resolver** (delivery other than `MANDATORY`);
  * it contains a **non-`ACTIVE` item that lacks its lifecycle banner**;
  * a non-`ACTIVE` item has no matching `MANDATORY_LIFECYCLE_NOT_ACTIVE` J notice.
* **Section D.1** fails G3 if it contains a non-ladder class or any non-`ACTIVE` lifecycle. This part is unchanged.
* **Oracle rows.** Any held-out oracle `authority_expectations` row that expects an **A-admissible** mandatory item
  somewhere other than A is **read as expecting A**. This concerns the test-author's OI-4: the sections for
  `EVIDENCE` and `ORCHESTRATION_RECORD` items were derived from the admissibility rules before this ruling existed.
  Every other oracle expectation stands **unchanged**. That covers the class, the banner, and the D.2/D.3/F/E/H
  placements of non-ladder items. The oracle's bytes, and its committed sha256, are untouched.

The grader must record, in the grading report, every oracle row that this reading affected. The orchestrator has
**not read the oracle**. This addendum follows only from the ruling and the public design text, so it cannot have been
tuned to the oracle's content.
