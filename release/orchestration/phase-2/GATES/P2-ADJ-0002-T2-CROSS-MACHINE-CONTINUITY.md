# P2-ADJ-0002 — Orchestrator adjudication: T2 bindings must survive the owner's other provisioned machines

| Field | Value |
|---|---|
| Record | P2-ADJ-0002 (orchestrator adjudication of a cross-capability conflict surfaced during repair; **not** an owner decision; the owner may override) |
| Date | 2026-09-19 |
| Surfaced by | P2-AR-0023 (WS-2 round 2) "sealed evidence is honoured only on the machine that wrote it"; confirmed in `runtime/src/t2.rs` (round-1 WS-3 design): a record sealed on machine A is `Foreign` on machine B and is **not honoured** there |
| Classes touched | BC-P2-09 (T2 binding, WS-3) × Contract v3 S6 (cross-machine mechanics) × E4 (claims survive rebuild) × N/W9 (fresh-agent reconstruction) |

## The conflict

Round 1 made OS-written (T2) facts — gate records, decisions, CIT state, the plugin registry, governed evidence — honoured
only when their HMAC seal verifies under a **machine-local** key. That closes forgery (D-0007 rule 2), but it also means a
project cloned to the owner's second machine sees every OS-written fact as `Foreign`: decisions, CIT state, registrations
and green evidence written on the first machine are refused on the second. Owner-signed human answers stay portable.

## Why this is determined, not an owner decision

- **Contract v3 S6** (lines 947–950): *"tracked truth syncs through Git/private remote"*, *"derived runtime rebuilds
  locally"*. Governed records are tracked truth. Framework §1 ("the organisation, not the conversation, owns continuity")
  and the Release/Distribution protocol §16 (cross-machine mechanics) require the same.
- **D-0007 rule 2**: T2 facts come only from OS operations — hand-written or forged records stay refused.
- **ARCH-0003 §8** (owner-adopted): *"Headless CI and additional machines are provisioned outside the project repository
  with the verifier, public root metadata and protected machine/workload policy."* The owner has already fixed where the
  authority for an additional machine comes from: administrator provisioning, outside the repository.
- **OWNER-DECISION-P2-0002**: governed work happens on provisioned machines.

Both requirements bind at once and a conforming design exists inside the accepted boundary (e.g. a per-owner/per-project
binding authority delegated through the provisioned root, or per-machine keys authorised by such a delegation), so the
choice among conforming mechanisms is an implementation matter graded by the verifier — the same treatment the synthesis
gave BC-P2-10 and the owner gave the break-glass mechanism (ARCH-0003 §7.1).

## Requirement (routed to repair round 3, WS-3 with WS-8 provisioning)

A T2 fact written by an OS operation on any machine **provisioned for the owner/project** is honoured on every other such
machine after a Git clone/pull; a record written by anything else (hand edit, unprovisioned machine, a machine not
authorised by the provisioning, a forged or modified seal) is still refused, typed and observable. No private key or
shared secret is stored in any repository. No new external dependency class. The verifier will attack it with a
two-machine scenario (distinct `XDG_STATE_HOME`/`HOME`, both provisioned from the same test root; plus one unprovisioned
or foreign machine) covering gates, decisions, CIT state, plugin registrations and governed evidence.

If the round-3 builder finds that every conforming design forces a trade-off the sources leave open, it stops the item and
states the question; the orchestrator then presents it to the owner.
