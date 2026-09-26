# Pending state updates: recorded on side branch `bridge/orch-pending-0001` during the third freeze

`ORCHESTRATOR_STATE.yaml` on the bridge branch is frozen at `94d0211`. A commit there would move the demonstration's
records ref. The facts below are applied to the state when the freeze lifts, after GRADE. **A resumed orchestrator
reads this file, `bridge/d1-0010` and `bridge/demo-0011`.**

## D1 addendum
* `bridge/d1-0010` at `aec095e`. `store-BR-AR-0010` was brought to `94d0211` by a FULL update: 2,530 s wall and
  9,329 CPU-s. The manifest is `11372e02…d5b0`. Freshness is a NOOP in 0.03 s. Coverage across 98 refs equals
  `git ls-tree`, with 0 unclassified. `integrate-check` BR-AR-0010: PERMITTED.

## run-1 compiled (orchestrator)
* `bridge/demo-0011` at `9f64c8c`. `packet_sha256` is `b5126140…2019`; `packet verify` PASS.
* `packet.md` is 274,798 bytes, `bootstrap.md` 282,782 bytes and `manifest.json` 419,496 bytes.
* Section item counts: A 20 · G 325 · H 43 · D.1/D.2/D.3 17/4/1.
* The public task inputs (the 41 queries, the answers schema and the receipt schema) were copied verbatim into
  `run-1/task-inputs/`, because the packet does not carry them and `ARCHITECTURE/` is excluded (**OBS-BR-07**).

## DEMO dispatched
* BR-AR-0011 run-1 was dispatched at about 00:25 BST on 2026-09-26: agent `br-demo-0011`, spawned `model: opus`,
  observed `claude-opus-5-5`, transcript `agent-a8a5be03e0483583d.jsonl`.

## Owner direction received
* **OD-BR-03** (verifier challenge items), in `GATES/OWNER-DIRECTION-BR-0003-VERIFIER-CHALLENGE-ITEMS.md` on this
  branch.

## DEMO returned; audited by the orchestrator
* BR-AR-0011 run-1 returned ANSWERED, at `bridge/demo-0011` `a9fc27b`. The agent answered all 41 queries: 39
  ANSWERED and 2 PARTIAL. The receipt check PASSES, re-run by the orchestrator. `integrate-check` BR-AR-0011:
  PERMITTED.
* Consumption: peak context 503,981 tokens over 210 turns. The packet plus the saved query outputs come to 1,338,001
  bytes. Detail in `run-1/CONSUMPTION-AND-SECRECY.orchestrator.md`.
* Secrecy: 0 accesses to the sealed directory or the oracle; 0 excluded-path reads; 0 overlaps of oracle substance.
* **OBS-BR-07:** the packet lacks the public query set and the answers/receipt schemas.
* **OBS-BR-08:** the query commands do not apply the task's `retrieval_exclusions` automatically. The agent's first
  search returned one snippet of public `ARCHITECTURE/demonstration-queries.yaml` text.

## GRADE dispatched
* BR-AR-0012 was dispatched at about 01:00 BST on 2026-09-26: agent `br-grade-0012`, spawned `model: opus`, on
  branch `bridge/grade-0012`, cut from `bridge/demo-0011` at `a9fc27b`.

## Owner directions OD-BR-04 and OD-BR-05 received during the freeze
* **OD-BR-04** (checkpoint discipline) is enforced on this branch:
  * `check_state.py checkpoint`, a mechanical outer checkpoint;
  * `verify` refuses any state without a matching checkpoint, once `checkpoint_discipline: OD-BR-04` is set at
    merge;
  * `integrate-check` requires the schema-2 worker checkpoint for runs marked `checkpoint_schema: 2`;
  * PreCompact and SessionEnd hooks are in the project's `.claude/settings.local.json`, locally git-excluded, calling
    `$HOME/.cache/gov-bridge/hooks/bridge-checkpoint-hook.sh`. The pipe-test wrote BR-CP-0004.
  * **Live in this session only after `/hooks` is opened or on restart.**
  * The first contemporaneous outer checkpoint since BR-CP-0002 is BR-CP-0003.
  * The `RETROSPECTIVE_CHECKPOINT_RECONSTRUCTION` for runs 0001–0015 is labelled as retrospective.
* **OD-BR-05** (multi-batch / multi-hop retrieval) was assessed **not conforming**. **Plan:**
  * after GRADE, merge and lift the freeze;
  * write an orchestrator design addendum derived from OD-BR-05;
  * dispatch a fresh bounded builder, **B7 `govbridge gather`**, covering:
    * facet decomposition;
    * deterministic parallel facet retrieval;
    * adaptive follow-up;
    * paging and continuation;
    * a recorded stopping reason;
    * merge with provenance and authority;
    * an evidence-note schema for hierarchical synthesis, with a traceability validator;
    * telemetry;
  * run its demonstration: a multi-location query that exceeds one batch, plus an unrelated control;
  * rebuild the store at the new tip, then emit BUILT.
  * OD-BR-05 is also carried into the verifier handoff.
