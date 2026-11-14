# Brief: independent test designer, W2-184 (DAEO-6f0s), batch td-2 (one amended point)

You are the independent test designer for DAEO-6f0s (W2-184). Your batch td-1 (commit 875039257, 327 cases under
`tests/acceptance/W2-184/`) is merged and green on the engineer's head. The lead has amended one settled point of
the interface, **3.2a** (below, in the whole interface; read 3.2, 3.2a and section 8's `effort_source` line). This
batch tests that point only. Do not read the engineer's work on this ticket (branch w2/W2-184 past b624fa3c1).

## Where you write
- Your tree: /home/usain/gov-os-worktrees/W2-184-tests, branch w2/W2-184-tests (at 875039257). Write only
  `tests/acceptance/W2-184/`. Reuse your support module.

## What to write
1. A role whose table effort is max (a fixture `Launch default` of max, or a `Launch by criticality` entry of max),
   launched with `--effort max` after `--` and no `--reason`: accepted; the record's `effort` max, `effort_source`
   `after --`, `effort_reason` null.
2. A FULL ticket's second `independent-auditor` launch (the probe) with `--model <opus> --effort max` after `--`, as
   `launch_worker.sh` passes it, and no `--reason`: accepted; `review_round` 2, `effort` max, `effort_source` `probe`.
   This one drives `gov launch` itself (no new option is needed), as W2-60a's cases do.
3. Still refused: a max after `--` where the resolved effort is high (round 1, or a non-FULL ticket, or an engineer
   on a high table) with no `--reason` (you may already have this: keep it, and name it).
4. If any td-1 case contradicts 3.2a, revise it and add the trailer `Rewrite-Reason: W2-184 interface 3.2a (lead,
   2026-11-14)` in the same final trailer paragraph.
Each new case is red on the engineer's current head for the stated reason only if the head does not yet build 3.2a;
you cannot see the head, so state per case what it would fail on in a launcher that applies 3.2 without 3.2a.

## How to run tests (every pytest)
```
env HOME=/home/usain/gov-os-worktrees/W2-184-tests/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-184-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-184 -q -p no:cacheprovider -o tmp_path_retention_policy=failed
```
(If heavy_slot.sh cannot take a slot inside the sandbox, run pytest directly as you did in td-1, and say so.) Use the
session's own `$TMPDIR`. No `gov retrieve`, no `gov context`: search with Read and Grep, and once more in other words.

## Commit (your paths only; trailers in ONE final paragraph)
```
git -C /home/usain/gov-os-worktrees/W2-184-tests commit -m "W2-184 (DAEO-6f0s): acceptance cases for interface 3.2a (a max after -- equal to the resolved effort needs no --reason)" --trailer "Task: DAEO-6f0s" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1120, DEC-1010" -- tests/acceptance/W2-184
```
No merge, no push. Refused twice for the same action: stop and say so; never work around it.

## Return (your last message): the twelve fields, each a labelled line
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: /
proposed_decisions: / unresolved: / recommended_next_action:

---
# THE INTERFACE (word for word, with 3.2a)

