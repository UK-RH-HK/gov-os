Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-20-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-20 — the independent test designer's brief, round 5: S16's planted suite (DAEO-r30l)

You are a fresh independent test designer for **W2-20** (`.tickets/DAEO-r30l.md`, S16 and P-4). The CTO ran S16's
measured case outside the sandbox on this machine (20 CPUs; share 6 with the configured slots), as your README says:

```
GOV_W2_20_MEASURE=1 PYTHONPATH=<tree>/src python3 -m pytest tests/acceptance/W2-20/test_w2_20_measured.py -m local_only -p no:cacheprovider -s
E   AssertionError: the planted suite does not exceed the share without the slot: no measure
E   assert 3.645320197044335 > (6 + 1)
1 failed in 25.93s
```

The cause is in the case: `spin.py` spins `os.cpu_count()` **Python threads**, which the GIL holds to about one core per
program, so the planted suite (8 tests, `-n 2` with xdist) never loads more than three or four cores, and S16 can never
show the slot holding a CPU-hungry suite. S16 says "each start a program that uses every CPU".

**Your job:** make the planted program use every CPU it believes the machine has, ignoring its CPU set, with
processes (e.g. `multiprocessing` or `os.fork` per CPU, each spinning until the deadline), not threads; keep the
time-bound design (P-4), the measurement and the assertions as they are. One commit with
`--trailer "Rewrite-Reason: DEC-1097 (8)"`; note it in the README's S16 section. You cannot run the measure yourself
(it is `local_only`, outside the sandbox): show the case still collects and skips without `GOV_W2_20_MEASURE`, and that
the new `spin.py` alone, run for one second, starts one process per CPU (count them, e.g. via `os.cpu_count()` and the
children it starts), if your sandbox allows.

## Where you work
- `/home/usain/gov-os-worktrees/W2-20-tests`, branch `w2/W2-20-tests`. You write only `tests/acceptance/W2-20/`.

## Rules
- **Never read W2-20's implementation (G-14):** never open `/home/usain/gov-os-worktrees/W2-20` or `W2-20-1017`, nor
  anything on `w2/W2-20` or `w2/W2-20-1017`. Keep every search inside your own worktree.
- **The hidden-half rule:** never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder. DEC-1080: Read and Grep tools; one simple command per Bash call.
- **Commit** on `w2/W2-20-tests` with
  `--trailer "Task: DAEO-r30l" --trailer "Implements: DEC-1038, DEC-1097" --trailer "Role: independent-test-designer" --trailer "Rewrite-Reason: DEC-1097 (8)" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- A small round: a few minutes.

## Return
Your whole return is your session's **final message** (the launcher keeps it; it is the record): the twelve labelled
fields of `EMG-common.md` (sandbox and `ps` checks first), the change, the commit, `TESTS-READY` text.
