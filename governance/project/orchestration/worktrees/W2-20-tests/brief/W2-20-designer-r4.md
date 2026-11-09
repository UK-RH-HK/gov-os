Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-20-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-20 — the independent test designer's brief, round 4: three cases against your own interface (DAEO-r30l)

You are a fresh independent test designer for **W2-20** (`.tickets/DAEO-r30l.md`). Your cases in
`tests/acceptance/W2-20/` (rounds 1 to 3, README "The interface these tests assume") now pass **160 of 164** against the
engineer's round 2, which built to that interface; S16 is skipped (the CTO's measured run). Three cases still fail, and
in each the failure is where a case and the README's own interface (or P-6, settled in the ticket) disagree. The CTO
(moderator) asks you to settle each one, as the tests' author:

1. **S2, `[busy cores high, load low]`:** the case plants busy cores 3.9, both servers' CPU p95 at 0.0, 4 processors,
   load 0.1, and expects the gate **shut on cpu**. Your interface's cpu rule (`busy + p95(shared) + p95(query) < nproc`,
   equal shuts) **opens** it, since 3.9 < 4. S2's KPI line names no threshold.
2. **S10, `[a GPU planted]`:** the case takes a plain `gov resources` reading before the start check with no declared
   need, and counts that reading's `nvidia-smi` call as if the start check had made it. P-6 (settled in the ticket):
   a start check without a declared need never runs `nvidia-smi`; the reading and a start with a need read the GPU once.
3. **S13, the measure:** the case takes two plain readings and counts both readings' `nvidia-smi` calls as one check
   (S13: the GPU "read once per check").

For each: either **revise the case** to what the KPI line, your interface and P-6 say together (S2: plant figures that
the stated cpu rule shuts, or state a different rule if S2's words demand one; S10 and S13: count only the call under
test), each change its own commit with `--trailer "Rewrite-Reason: DEC-1097 (8)"`; or, if you judge the case right and
the interface wrong, **say so** with the KPI words that decide it, and change nothing (the CTO then takes it to the
engineer). Update the README's interface and map where you change them.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-20-tests`, branch `w2/W2-20-tests` (integrate merged in today). You
  write only `tests/acceptance/W2-20/`.
- Your cases run red on this tree's code (no gate here): show only that each revised case still collects and fails
  for the missing product, and that no other case changed.

## Rules
- **Never read W2-20's implementation (G-14):** never open `/home/usain/gov-os-worktrees/W2-20` or
  `/home/usain/gov-os-worktrees/W2-20-1017`, nor anything on `w2/W2-20` or `w2/W2-20-1017` (its code, unit tests or
  evidence file). This brief is all you need about the engineer's work. Keep every search inside your own worktree.
- **Search again once (DEC-1092 (1)):** if a search does not answer, search once more in your own words.
- **The hidden-half rule:** never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder.
- Run with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-20-tests/src` (through the heavy slot where the sandbox allows
  it). DEC-1080: Read and Grep tools; one simple command per Bash call.
- **Commit** on `w2/W2-20-tests` with
  `--trailer "Task: DAEO-r30l" --trailer "Implements: DEC-1088, DEC-1097" --trailer "Role: independent-test-designer" --trailer "Rewrite-Reason: DEC-1097 (8)" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- A small round.

## Return
Your whole return is your session's **final message** (the launcher keeps it; it is the record): the twelve labelled
fields of `EMG-common.md` (sandbox and `ps` checks first), each of the three cases with your ruling (revised, with the
commit, or right as it stands, with the KPI words), `TESTS-READY` text.
