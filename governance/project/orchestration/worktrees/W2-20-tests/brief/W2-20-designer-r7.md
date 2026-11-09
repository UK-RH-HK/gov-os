Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-20-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-20 — the independent test designer's brief, round 7: the CTO's rulings (DAEO-r30l)

You are a fresh independent test designer for **W2-20** (`.tickets/DAEO-r30l.md`). Your cases (rounds 1 to 6,
`tests/acceptance/W2-20/`, README "The interface these tests assume") pass 163/163 against the engineer's round 2
(S16 run by hand). The independent review and the CTO have ruled three things that change your cases **before** the
engineer's round 3:

1. **F2, the CPU rule (the CTO's ruling under DEC-1097 (8): a false refusal).** The review found: *"The CPU rule
   counts the embedding servers twice. `busy` already includes the servers' current use, and the rule adds each
   server's p95 on top. That p95 is kept for a week, and during store rebuilds the shared server's p95 can sit near
   8 cores, so the gate shuts at about 12 busy cores of 20 whenever a rebuild runs."* The CTO: a rule that shuts the
   gate during store rebuilds refuses honest work; fix it. **Revise your interface's cpu rule and its cases** (S2,
   S12, and `test_exactly_at_a_threshold[cpu]` or any case that pins the rule) so the servers are not counted twice:
   for example `busy + max(0, p95(shared) − now(shared)) + max(0, p95(query) − now(query)) < nproc` (only the part of
   each server's p95 above its current use is added), with the reading showing the servers' current use beside their
   p95. State the rule you choose in the README and plant cases that show: a rebuild-like reading (the shared server
   busy now near its p95) no longer shuts the gate where real CPU room exists; a reading with the servers idle now but
   a high p95 still counts the p95's headroom; equal still shuts. Each changed case its own commit with
   `--trailer "Rewrite-Reason: the CTO's ruling under DEC-1097 (8), a false refusal (review F2)"`.
2. **The configuration format is frozen from `28fbcfebf`** (W2-20's head when ACT-GATE-CONFIG-2 writes the machine's
   file): round 3 must not change key names or meanings. **Add one case** that pins it: `gov resources --init-config`
   under a planted HOME writes exactly the key set, value form (`{value, date, source}` where the interface says so)
   and nesting your README's "The configuration file" section states today, and nothing else. (Use the README's own
   statement as the expected set; never W2-20's code.) New case, no Rewrite-Reason.
3. **S16's background (the CTO did not accept round 6's reading).** A background sampled just after the plain run
   includes the plain run's tail and flatters the net figure. Sample the background **once, before the plain run**, on
   a quiet machine, and take its **median**; use that one background for both runs' net figures; print gross, net and
   the background's median and p95. Keep the real share, the CPU-set check, the time-bound design and the 20 % check.
   One commit with `--trailer "Rewrite-Reason: DEC-1097 (8)"`.

## Where you work
- `/home/usain/gov-os-worktrees/W2-20-tests`, branch `w2/W2-20-tests`. You write only `tests/acceptance/W2-20/`.

## Rules
- **Never read W2-20's implementation (G-14):** never open `/home/usain/gov-os-worktrees/W2-20` or `W2-20-1017`, nor
  anything on `w2/W2-20` or `w2/W2-20-1017`. Work from the ticket, your README and this brief.
- The hidden-half rule: never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder. Never write the real `~/.gov-os/`. DEC-1080: Read and Grep tools; one
  simple command per Bash call. Search again once (DEC-1092 (1)) if needed.
- Run with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-20-tests/src` (no product here: show each new or revised case
  collects and fails for the missing product, and no other case changed).
- **Commit** on `w2/W2-20-tests` with
  `--trailer "Task: DAEO-r30l" --trailer "Implements: DEC-1088, DEC-1097" --trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"` plus the Rewrite-Reason named above.

## Return
Your whole return is your session's **final message** (the launcher keeps it; it is the record): the twelve labelled
fields of `EMG-common.md` (sandbox and `ps` checks first), the cpu rule you chose with its words, each case changed or
added with its commit, `TESTS-READY` text.
