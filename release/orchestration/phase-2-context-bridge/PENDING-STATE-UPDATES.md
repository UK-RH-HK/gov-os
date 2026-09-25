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
