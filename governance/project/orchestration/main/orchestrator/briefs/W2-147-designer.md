# W2-147 — the independent test designer's brief (DAEO-zi7s)

You are the independent test designer for **W2-147** (`.tickets/DAEO-zi7s.md`): `gov plan` breaks a cycle only at a
ticket inside it, and a ticket outside every cycle keeps all its waits (the owner's DEC-1102). Read the ticket in full
first. Its KPI lines S1 to S4 and its three failure lines are what you test. Profile STANDARD: every KPI line's success
and failure, plus the key edge cases; no combinatorial expansion.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-147-tests`, branch `w2/W2-147-tests`, made from `w2/integrate` today.
- You write only `tests/acceptance/W2-147/`: the cases, a `conftest.py` and support module if needed, and a `README.md`
  whose map the runner reads (header `| KPI line | Test (node id) | On integrate | Why |`, one id such as `S1` in each
  KPI cell, the test in backticks with its full node id, as `tests/acceptance/W2-133/README.md`). State there the
  interface the tests assume (the command and its `--json` form, how a break is named: `CYCLE_TIEBREAK`, the ticket
  chosen and the waits broken), so the engineer builds to it.
- **Your record:** your whole return (the twelve fields below) is your session's **final message**, in full: the
  launcher keeps it in this worktree's `.gov-runtime/scratch/lead/log/W2-147-designer.json`, which is the record (your
  session cannot write that folder itself, and its own scratchpad is deleted when it ends).
- You may read any code on `w2/integrate`: `src/gov/plan/` (`derive.py`'s `_order` and the fixed key, `command.py`,
  `render.py`, `tickets.py`), `tests/acceptance/W2-136/` and `tests/unit/plan/w2_136_store.py` for how a planted
  ticket store is built and `gov plan` driven, and W2-136's ticket (`.tickets/DAEO-p3ln.md`, its S4) for the key.

## What the cases must show (from the ticket)
- **S1:** a planted cycle A↔B with an outside ticket C that waits on A and sorts first by the fixed key: the break
  falls on A or B (inside the strongly connected component), only waits from inside it are broken, C's wait kept. Red
  on integrate where `_order` picks C.
- **S2:** the 2026-11-09 case, planted with stand-in tickets of the same shape (W2-145 ↔ W2-137 in a cycle, W2-88
  waiting on W2-145, W2-27 waiting on W2-88): W2-27's wait on W2-88 kept, W2-27 batched after W2-88. Red on integrate.
- **S3:** each planted graph in two shuffled file orders gives byte-identical text and `--json` output; each break
  named with its ticket and its broken waits.
- **S4:** two separate cycles, each broken once inside itself; a self-loop broken at that ticket and named; no cycle:
  the output byte-identical to integrate's for the same tickets (a green guard: capture integrate's output in the test
  from today's code at a pinned commit, or compare against a stored expected output with its commit named).
- Say for each case whether it is red on integrate for the right reason, or a green guard.

## Rules
- **Never read this ticket's implementation (G-14; DEC-820 (c)):** there is none yet; never open
  `/home/usain/gov-os-worktrees/W2-147` or the branch `w2/W2-147` if either appears, and never read the engineer's
  files on this ticket. You work from the ticket's KPI lines and today's integrate code only.
- **The exclusion line (DEC-1093 (2)), for you:** keep every Grep, Glob and recursive Bash search inside your own
  worktree, never from `/home/usain/gov-os-worktrees/` or `/home/usain/`, so no search can reach this ticket's engineer
  worktree; if a search shows you a line of the implementation anyway, stop reading it and say so in your return.
- **Search again once (DEC-1092 (1)):** if what you searched (Grep and Read; no `gov retrieve` in the sandbox,
  `EMG-d4b-launched.md`) does not answer, or you can tell your answer may be incomplete, search once more in your own,
  different words; then answer from both searches and the files you read, with path and lines, or say "not found".
  Two searches in all.
- Planted ticket stores in a temporary folder only, never this repository's `.tickets/`. No GPU, no model, no network.
- **The hidden-half rule:** never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder.
- Run your cases with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-147-tests/src` (through the heavy slot that
  `EMG-common.md` names where the sandbox allows it), and run
  `python3 -m gov.cli.main accept W2-147 --root /home/usain/gov-os-worktrees/W2-147-tests` to show the runner reads
  your map.
- **DEC-1080:** read with the Read and Grep tools; one simple command per Bash call; no `cd … &&` chains; one line
  before any command that will ask for permission.
- **Commit** on `w2/W2-147-tests`, only `tests/acceptance/W2-147/`, with
  `--trailer "Task: DAEO-zi7s" --trailer "Implements: DEC-1102" --trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- **Before you end your session,** make sure every test run you started has finished.
- Keep to the estimate: a small round (about 8 to 12 cases).

## Return
The twelve labelled fields of `EMG-common.md` (sandbox check and `ps` check first), with the case list (node id, KPI
line, red or green on integrate, and why), the commit, `gov accept`'s counts, `TESTS-READY` text, and anything
untestable or ambiguous as `discoveries` or a decision package with your recommendation and confidence.
