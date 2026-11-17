---
name: dec-1157-no-holds
description: "DEC-1157 removed every rule that holds or delays a lead except machine/governance protections; the CTO's practices that follow from it"
metadata:
  node_type: memory
  type: project
  originSessionId: b2f0511f-891b-4874-8930-6d34ca5972ea
  modified: 2026-11-12T23:49:06.248Z
---

DEC-1157 (owner, 2026-11-12 ~23:40, standing) removed: the night push rule, the night hold (night_hold.py stopped; config.json empty hold window), the interface check as a lead stop, one land per batch, the CPU band (config cpu_band [0,1000]), the 5-lead cap (max_leads removed), commit freezes during lands; merged dependencies count as met for starting (closing still waits; tonight via `plan_override: DEC-1157`); a land holds at most 2 of 3 heavy slots (heavy_slot.sh PRIO_CAP=2).

Kept: memory floor, 5 GB hold (mem_hold.py), mem_guard, OOM trip; guard refusals; spend brake; brief checks; review rounds, kernel gate, owner approval of kernel bytes; new tickets and splits to the owner; idle-check record.

**How to apply (CTO practice):**
- State each ticket's interface in the ticket at claim, before its lead takes a slot.
- Keep two lead lines prepared (claim, worktree, brief) at all times.
- Commit whenever needed, even during a land (accept the re-test).
- Land in batches of 2-3 tickets with disjoint paths.
- "Merged" means the dependency's merge commit is on integrate (a fresh claimed branch is an ancestor of integrate and is NOT merged work).
- Widenings and KPI edits within a ticket's own purpose: decide, list for reading.
- Logs: log/refused-starts.jsonl (tools/refused_starts.py, run in background) and log/heavy-slot-waits.jsonl (heavy_slot.sh).
- Not yet changed: the operator's cron line still reads the night-hold state file after 03:10 (a crontab ACT, class b).

Related: [[night-bring-lead-stoppers]], [[gate-refusal-is-a-wait]], [[cto-fixes-path-cases]].
