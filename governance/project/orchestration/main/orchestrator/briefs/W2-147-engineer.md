# W2-147 — the engineer's brief (DAEO-zi7s)

You are the engineer for **W2-147** (`.tickets/DAEO-zi7s.md`): `gov plan` breaks a cycle only at a ticket inside it,
and a ticket outside every cycle keeps all its waits (the owner's DEC-1102). Read the ticket in full first, with its
note on the self-loop.

## Where you work
- **Your worktree:** `/home/usain/gov-os-worktrees/W2-147`, branch `w2/W2-147`: `w2/integrate` with the designer's
  cases merged in.
- **Your paths:** `src/gov/plan/**`, `tests/unit/plan/test_w2_147*`, and `docs/changes/W2-147-evidence.md` (your
  evidence record: one row per KPI line S1 to S4).
- **You never read `tests/acceptance/W2-147/`** (DEC-820 (c), DEC-1056): not by Read, Grep, Glob, cat, git show or any
  other tool. Run those cases only through `gov accept W2-147` and read only its results (names, pass or fail, the
  failure messages). Every Grep or Glob call that could reach that folder carries `!tests/acceptance/W2-147/**`, and
  every recursive Bash search the matching exclusion (`grep -r --exclude-dir=W2-147`; see EMG-common).

## The change
- `src/gov/plan/derive.py`'s `_order` today breaks the incoming waits of the first remaining ticket by the fixed key
  even when that ticket is not in a cycle (seen 2026-11-09: it broke W2-27's wait on W2-88 while W2-145 and W2-137
  formed the cycle). Break a cycle only inside its strongly connected component: choose the break ticket from the
  component by the fixed key (priority, then WBS order, then id), break only its waits from inside the component, and
  name each break in the output (`CYCLE_TIEBREAK`, the ticket chosen and the waits broken), deterministically in any
  file order.
- A ticket outside every cycle keeps all its waits and is batched after what it waits on.
- A ticket waiting on itself (a `waits_on` self-loop), which `hard_waits` drops silently today, is kept as a wait, so
  the self-loop is broken at that ticket and named (the ticket's note).
- With no cycle, the output stays byte-identical to today's.

## Tests and evidence
- **Unit tests** in `tests/unit/plan/test_w2_147*`, with planted ticket stores in a temporary folder (see
  `tests/unit/plan/w2_136_store.py`), never this repository's `.tickets/`.
- **Every test run** through
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh <command>`
  (where the sandbox allows it), with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-147/src`.
- **When your unit tests pass:** run `python3 -m gov.cli.main accept W2-147 --root /home/usain/gov-os-worktrees/W2-147`
  and report its counts; then `tests/unit/plan` and `tests/acceptance/W2-136` (W2-136's cases must stay green), and
  list every red with its cause. Fix only what is inside your paths; a red elsewhere you name.

## Rules
- **The hidden-half rule:** never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder.
- **Search again once (DEC-1092 (1)):** if a search (Grep and Read; no `gov retrieve` in the sandbox,
  `EMG-d4b-launched.md`) does not answer, search once more in your own, different words; then answer from both, with
  path and lines, or say "not found". Two searches in all.
- **DEC-1080:** read with the Read and Grep tools; one simple command per Bash call; no `cd … &&` chains; one line
  before any command that will ask for permission.
- **Do not merge `w2/integrate` yourself.** Never touch `tests/acceptance/**`, `.tickets/` or `.claude/`.
- **Commit** on `w2/W2-147`, only your paths, with
  `--trailer "Task: DAEO-zi7s" --trailer "Implements: DEC-1102" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- **Before you end your session,** make sure every test run you started has finished.

## Return
Your whole return is your session's **final message**, in full (the launcher keeps it in this worktree's log; it is
the record): the twelve labelled fields of `EMG-common.md`, with the sandbox check and the `ps` check first, the diff's
size, the unit tests' names and outcome, `gov accept`'s counts, and the regression run's counts with every red named.
