# W2-20 — the independent test designer's brief, round 6: S16's share (DAEO-r30l)

You are a fresh independent test designer for **W2-20** (`.tickets/DAEO-r30l.md`, S16, S17, P-4). Round 5's planted
suite now loads the machine, and the CTO's run outside the sandbox **passed** S16:
`share 6 of 20 CPUs (3 slots); busy cores p95 with the slot 3.13, without 20.00; time with 12.8 s, without 12.6 s (+1 %)`.
The independent review's **F3** says the case judged that against the wrong share:

> F3. S16's evidence used the wrong share. The case sets `share = affinity // slots`, which is 6. The slot's real CPU
> set is the 8 CPUs outside the servers' sets divided by 3, so 2 CPUs. Against the real share plus one (3), the recorded
> 3.13 is over. That figure counts the whole machine, including whatever else ran at the time. The confinement itself
> holds by construction (`sched_setaffinity`). So the KPI's aim is probably met, but the evidence does not show it.

**Your job:** make S16 judge against the slot's **real** share: S17's rule and your interface (the slot's CPU set: the
logical CPUs outside the servers' configured CPU sets, divided by the slots; read the share from what your interface
says the slot reports, e.g. its record or `slots.held`, or compute it from the planted or real configuration as the
interface states), and measure the planted suite's busy cores **net of the machine's background**: sample the busy
cores for a few seconds just before each run and subtract that p95 (or its median), printing both, so other sessions'
load does not count against the slot. Keep the time-bound design and the 20 % check. One commit with
`--trailer "Rewrite-Reason: DEC-1097 (8)"`; note it in the README's S16 section. The CTO re-runs the measure outside
the sandbox.

## Where you work
- `/home/usain/gov-os-worktrees/W2-20-tests`, branch `w2/W2-20-tests`. You write only `tests/acceptance/W2-20/`.

## Rules
- **Never read W2-20's implementation (G-14):** never open `/home/usain/gov-os-worktrees/W2-20` or `W2-20-1017`, nor
  anything on `w2/W2-20` or `w2/W2-20-1017`. Work from the ticket, your README's interface and this brief.
- The hidden-half rule: never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder. Never read or write the real `~/.gov-os/` except as the case already
  reads `gate.json`. DEC-1080: Read and Grep tools; one simple command per Bash call.
- **Commit** on `w2/W2-20-tests` with
  `--trailer "Task: DAEO-r30l" --trailer "Implements: DEC-1038, DEC-1097" --trailer "Role: independent-test-designer" --trailer "Rewrite-Reason: DEC-1097 (8)" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- A small round.

## Return
Your whole return is your session's **final message** (the launcher keeps it; it is the record): the twelve labelled
fields of `EMG-common.md` (sandbox and `ps` checks first), the change, the commit, `TESTS-READY` text.
