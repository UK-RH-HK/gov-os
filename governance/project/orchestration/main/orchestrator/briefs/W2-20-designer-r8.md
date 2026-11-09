# W2-20 — the independent test designer's brief, round 8: DEC-1105's exception round (DAEO-r30l)

You are a fresh independent test designer for **W2-20** (`.tickets/DAEO-r30l.md`). The owner granted one exception
round to DEC-1010 (DEC-1105, the register's last entry: read it). Before the engineer's pass, two things from you:

1. **S16, a per-CPU measure (Rewrite-Reason: DEC-1105).** The CTO's two runs on round 3's code: run 1 passed (net
   2.86), run 2 failed by 0.003 (net 3.003 against share 2 + 1 = 3) with the slot's programs held to exactly 2 CPUs.
   The review (round 2, R2-F2): *"The case subtracts the background's median from a run's p95 of whole-machine busy
   cores, so the background's tail stays in the net figure. A per-CPU measure would separate the slot from the rest
   of the machine: the `cpuN` lines of `/proc/stat` for the slot's CPUs against the others, or the confined processes'
   own CPU time."* Revise S16 so the "with the slot" figure is the busy cores **on the slot's own CPUs** (the `cpuN`
   lines for the CPU set the slot gave its programs, which the case already records), sampled as now, so the
   machine's background does not enter it; and so the planted suite's whole load is accounted for: show also that the
   CPUs outside the slot's set gained no more than the background (no program escaped the set). **The bar is
   unchanged:** within the slot's share plus one, and no more than 20 % slower. The "without the slot" figure keeps
   showing the suite exceeds the share (else no measure). Print every figure for the evidence. One commit.
2. **R2-F1, a case first.** The review: *"The first reading after ten quiet minutes shuts the gate on cpu. `known()`
   counts any kept window sample of the server's process, however old, so a server is not resampled; the window is
   then filtered to `KEEP_S` (600 s), leaving it empty; `now` is null, and the gate shuts on cpu. A launch reads the
   gate once, so that launch is refused. The next one passes, because the failed reading added a fresh sample."*
   DEC-1105: a server whose kept readings have all expired is resampled before the cpu rule reads it, so the gate never
   refuses a launch for stale readings. **Write the case** through your interface: a planted history of the servers'
   CPU readings (the cache your README's interface names for the servers' current use, under a planted HOME) whose
   samples are all older than the keep window, with the servers present and idle; the start check (and `gov resources
   --check`) must open on cpu at the first reading and show a fresh `embedding_cpu_now`, not null. If your interface
   does not yet name that cache's form, state it in the README from what the KPI lines and round 7's interface say,
   and plant the servers' current use the way your other cases do; never read W2-20's code. New case, no Rewrite-Reason.

## Where you work
- `/home/usain/gov-os-worktrees/W2-20-tests`, branch `w2/W2-20-tests`. You write only `tests/acceptance/W2-20/`.

## Rules
- **Never read W2-20's implementation (G-14):** never open `/home/usain/gov-os-worktrees/W2-20` or `W2-20-1017`, nor
  anything on `w2/W2-20` or `w2/W2-20-1017`. Work from the ticket, your README and this brief.
- **The configuration format stays frozen** (from `28fbcfebf`): no case may need a configuration change.
- The hidden-half rule: never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder. Never write the real `~/.gov-os/`. DEC-1080: Read and Grep tools; one
  simple command per Bash call.
- Run with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-20-tests/src` (no product here: the new case collects and fails
  for the missing product; S16 skips without `GOV_W2_20_MEASURE`).
- **Commit** on `w2/W2-20-tests` with
  `--trailer "Task: DAEO-r30l" --trailer "Implements: DEC-1105, DEC-1097" --trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`,
  and `--trailer "Rewrite-Reason: DEC-1105"` on S16's commit.

## Return
Your whole return is your session's **final message** (the launcher keeps it; it is the record): the twelve labelled
fields of `EMG-common.md` (sandbox and `ps` checks first), S16's new measure in words, the R2-F1 case (node id, what it
plants, what it asserts) and any interface you stated, the commits, `TESTS-READY` text.
