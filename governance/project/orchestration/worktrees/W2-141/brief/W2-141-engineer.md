Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-141/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-141 — the engineer's brief (DAEO-xwro)

You are the engineer for **W2-141** (`.tickets/DAEO-xwro.md`): the guard refuses an engineer's Grep, Glob or recursive
Bash search that can reach its own ticket's acceptance folder unless the call excludes it, and the refusal says how
(DEC-1093 (2), DEC-1102). Read the ticket in full first, with "The hook side" and "The designer's round-2 points
settled".

## Where you work
- **Your worktree:** `/home/usain/gov-os-worktrees/W2-141`, branch `w2/W2-141`: `w2/integrate` with the designer's
  cases (both rounds) merged in.
- **Your paths:** `src/gov/guard/reads.py`, `src/gov/guard/role_paths.py`, `tests/unit/guard/test_w2_141*`,
  `docs/changes/W2-141-evidence.md`, `docs/changes/W2-141-hook/**`, `tests/unit/hooks/test_live_hook.py` (its one
  `G14_PASSED` case `grep -r foo tests/`, which S1 now refuses: revise only that case, commented `DEC-1093 (2)`).
  `.claude/hooks/role_reads.py` is in the ticket's paths, but **you cannot edit `.claude/`** (the launcher's DEC-315 deny
  rules): never try. Instead:
  - `docs/changes/W2-141-hook/role_reads.py`: a whole-file copy of `.claude/hooks/role_reads.py` with your change (the
    acceptance cases load it when it exists);
  - `docs/changes/W2-141-hook/pretooluse.py`: a whole-file copy of `.claude/hooks/pretooluse.py` with only `"Glob"`
    added to the tool list that routes to `role_reads` (the G-14 block); nothing else changed in it;
  - a short `docs/changes/W2-141-hook/README.md`: what each copy changes against the live file (the diff), for the
    operator's ACT at the lift's re-pin. The CTO prepares the ACT; nothing live changes now.
- **You never read `tests/acceptance/W2-141/`** (DEC-820 (c), DEC-1056): run those cases only through `gov accept W2-141`
  and read only the results. Every Grep or Glob call that could reach that folder carries `!tests/acceptance/W2-141/**`,
  and every recursive Bash search the matching exclusion (`grep -r --exclude-dir=W2-141`: the base name; see
  EMG-common). This is exactly what the ticket builds: keep to it.

## The change (S1 to S3)
- **The decide side** (`src/gov/guard/reads.py`): integrate's `decide` already refuses broad searches; it lacks
  accepting an exclusion, Glob with `**`, `ag` and `ack`, and a reason that names the folder and says how to exclude
  it (for Grep `!tests/acceptance/<T>/**`, for grep `--exclude-dir=<T>`, for rg `-g '!tests/acceptance/<T>/**'`, for find
  `-not -path` / `-prune`; for Glob, a path or pattern that cannot reach it).
- **The hook side** (`role_reads.py`'s staged copy): an engineer's search from a folder above its own acceptance folder
  (the repository root, `tests/`, `tests/acceptance/`) is no longer let through unless it excludes the folder; the
  refusal says how. S3: other tickets' tests readable, other roles unaffected, a names-only listing and a grep for the
  tests' names by pattern still let through, G-14's existing cases unchanged.
- Never make a guard decision fail open; a target the guard cannot resolve keeps today's behaviour.

## Tests and evidence
- **Unit tests** in `tests/unit/guard/test_w2_141*` (the hook copy may be loaded by path with importlib).
- **Every test run** through
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh <command>`
  (where the sandbox allows it), with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-141/src`.
- **When your unit tests pass:** `python3 -m gov.cli.main accept W2-141 --root /home/usain/gov-os-worktrees/W2-141`,
  report its counts; then `tests/unit/guard tests/unit/hooks` and `tests/acceptance/W2-84`, and list every red with its
  cause.
- **The evidence record** `docs/changes/W2-141-evidence.md`: one row per KPI line; "applied by the operator's ACT at
  the lift's re-pin" for the hook copies.

## Rules
- **The hidden-half rule:** never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder.
- **Search again once (DEC-1092 (1)):** if a search (Grep and Read; no `gov retrieve` in the sandbox) does not answer,
  search once more in your own, different words; then answer from both, with path and lines, or say "not found".
- **DEC-1080:** Read and Grep tools; one simple command per Bash call; no `cd … &&` chains.
- **Do not merge `w2/integrate` yourself.** Never touch `tests/acceptance/**`, `.tickets/` or `.claude/`.
- **Commit** on `w2/W2-141`, only your paths, with
  `--trailer "Task: DAEO-xwro" --trailer "Implements: DEC-1093, DEC-1102" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- **Before you end your session,** make sure every test run you started has finished.

## Return
Your whole return is your session's **final message**, in full (the launcher keeps it in this worktree's log; it is
the record): the twelve labelled fields of `EMG-common.md` (sandbox and `ps` checks first), the diff's size, the unit
tests' names and outcome, `gov accept`'s counts, and the regression run's counts with every red named.
