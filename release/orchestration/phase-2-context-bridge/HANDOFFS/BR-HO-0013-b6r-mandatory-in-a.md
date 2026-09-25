# BR-HO-0013: bounded repair B6R, keeping mandatory inputs in section A whatever their lifecycle (run BR-AR-0013)

**This brief is `HANDOFFS/BR-HO-TEMPLATE-builder.md` (read it first; its rules bind you) plus the section below.**

| Field | Value |
|---|---|
| Run | `BR-AR-0013`. You are a **fresh** builder, not the B6 builder. |
| Worktree | `/home/usain/Dynamic-Agentic-Engineering-OS/.claude/worktrees/br-ar-0013`, branch **`bridge/b6r-0013`**, based on the bridge tip after B6 merged |
| Model | spawned `model: sonnet` |
| Mutation scope | `release/orchestration/phase-2-context-bridge/govbridge/compile/**`, `…/tests/compile/**`, `…/tests/fixtures/compile/**` and `…/AGENT_RUNS/BR-AR-0013.*`. **Nothing else.** In particular, not `govbridge/authority/**`. |
| Governing record | **`GATES/BR-ARCH-RULING-1-MANDATORY-INPUTS-ALWAYS-IN-A.md`**. Read it first. It is the whole specification of this repair. |

## The defect

`govbridge/compile/packet.py:178` (`place_item`) admits a MANDATORY item into A only when `lifecycle == ACTIVE`. On the
real `ARCHITECTURE/demonstration-task.yaml`, that sends Contract v3, the frozen gate contract, the owner launcher and
seven other mandatory items into **H**, under a `MANDATORY_ITEM_NOT_IN_A` notice (see the compile loop near line 400).

## What to change

1. **Placement.** A resolver-returned item whose class is admissible in A goes to **A**, whatever its lifecycle.
   * Non-`ACTIVE` lifecycles keep their honest label and get the lifecycle banner already defined in `packet.py`
     (around line 74).
   * Emit a J notice `MANDATORY_LIFECYCLE_NOT_ACTIVE` with `{id, class, lifecycle}`. Replace
     `MANDATORY_ITEM_NOT_IN_A`, which should no longer be reachable for A-admissible classes.
   * D.1 eligibility stays **ACTIVE-only**. Ordering stays as it is.
2. **Non-ladder classes are unchanged**:
   * `OWNER_DIRECTION_TO_TEST` goes to D.2;
   * `HYPOTHESIS_TO_TEST` goes to D.3;
   * `HYPOTHESIS_RELEVANT_OBSERVATION` goes to F;
   * `EVIDENCE_WITHDRAWN` goes to E or F;
   * `UNCLASSIFIED` goes to H, with a J notice.
3. **Validator.** `compile/validate.py` must **refuse** a packet in which any resolver-returned, A-admissible item sits
   outside A. It must also refuse one in which a non-`ACTIVE` A item lacks its lifecycle banner. It keeps every
   existing check: re-derivation of A, admissibility per class, banners, and ordering.
4. **Nothing may raise a lifecycle.** `UNKNOWN` stays `UNKNOWN`. Do not touch the classifier.

## Tests you must add

Give each a unique basename across `tests/**`.

* **Fixture test.** A mandatory `CONTRACT` item with lifecycle `UNKNOWN` lands in A, with its banner and a J notice.
  A mandatory `ORCHESTRATION_RECORD` item with lifecycle `UNKNOWN` also lands in A. A mandatory
  `OWNER_DIRECTION_TO_TEST` item lands in D.2 and **not** A. A retrieved item of any class **never** lands in A.
* **Validator negative control.** Take a packet with a resolver A-admissible item moved from A to H by hand. It must
  fail `packet verify`.
* **Real-view acceptance.** Compile `ARCHITECTURE/demonstration-task.yaml` with `--fake-routes`, twice, and require:
  * every A-admissible `mandatory_bridge_inputs` item, and every owner record in the task spec, is in A: in
    particular `state:bridge#contract_v3`, `PHASE-2-FROZEN-GATE-CONTRACT` and `OWNER-LAUNCHER-BR-0001`;
  * `F1-DIRECTION` is only in D.2, `F2-F3-COMMON-CLASS` only in D.3, and `ORCHESTRATOR-REASONING-ERRORS` only in F;
  * the two runs produce byte-identical packets.

  Save the per-item section map to your checkpoint outputs.

**The existing six named invariant tests must still pass.** If an existing test asserts the old "UNKNOWN is kept out of
A" behaviour for a *mandatory* item, you may change that assertion, but **only** that assertion. Quote the before and
after lines in your report.

## Isolation

* Run with `GOVBRIDGE_STORE=$HOME/.cache/gov-bridge/store-BR-AR-0013`. The venv is read-only.
* Run `pytest tests -q --import-mode=importlib` to check coexistence. The plain-collection basename clash belongs to
  I1.
