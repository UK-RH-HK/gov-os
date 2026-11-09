Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-141-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-141 — the independent test designer's brief, round 2: the hook side (DAEO-xwro)

You are a fresh independent test designer for **W2-141** (`.tickets/DAEO-xwro.md`). Round 1 (`c3e0e16bc`, 88 cases in
`tests/acceptance/W2-141/`) tests the guard's `decide` function only, and found that the gap W2-138 hit is in the live
hook `.claude/hooks/role_reads.py`, which lets an engineer's search from a folder above its own acceptance folder
through. The CTO has put the hook in the ticket's paths: read the ticket's new section "The hook side" first.

**Your job:** add the hook-side cases for S1, S2 and S3 (and the failure lines), so the engineer builds the hook change
to them. Keep round 1's cases unless one is wrong; a change to one is its own commit with
`--trailer "Rewrite-Reason: DEC-1102"` and named in your return.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-141-tests`, branch `w2/W2-141-tests` (integrate merged in today).
- You write only `tests/acceptance/W2-141/`: new test files for the hook, support code and the README's map (new rows
  with full node ids, and the interface the hook cases assume).
- **Which hook the cases load:** a launched engineer cannot edit `.claude/` (DEC-315), so the engineer builds the
  changed hook as a whole-file copy at `docs/changes/W2-141-hook/role_reads.py`, and the operator copies it to
  `.claude/hooks/role_reads.py` at the lift's re-pin. Your cases load `docs/changes/W2-141-hook/role_reads.py` when it
  exists in the tree under test, else `.claude/hooks/role_reads.py`, by file path (importlib), and say in the README
  which one they ran on. Drive it the way `.claude/hooks/pretooluse.py` calls it (read how it imports and calls
  `role_reads`, and the hook's event JSON form as `guard4_check.py` builds it), with a planted project and a planted
  path map holding a `role_paths:` section (never the main tree's), so the cases are deterministic.
- What the cases show, through the hook: an engineer's Grep, Glob and recursive Bash searches from a folder above its
  acceptance folder (the repository root, `tests/`, `tests/acceptance/`) refused unless excluded, the refusal naming
  the folder and the exclusion (`!tests/acceptance/<T>/**` for Grep; `--exclude-dir=<T>`, the base name, for grep);
  the excluded forms allowed; S3's unchanged behaviour (other tickets' tests readable, other roles unaffected, a
  names-only listing and a grep for the tests' names by pattern still let through as the hook's note says, G-14's
  existing cases unchanged). Red on integrate where today's hook lets the search through.

## Rules
- **Never read this ticket's implementation (G-14; DEC-820 (c)):** never open `/home/usain/gov-os-worktrees/W2-141` or
  the branch `w2/W2-141`, and never read `docs/changes/W2-141-hook/` in any tree but your own (it does not exist in
  yours). You work from the ticket, round 1's cases and today's integrate code.
- **The exclusion line (DEC-1093 (2)), for you:** keep every search inside your own worktree, never from
  `/home/usain/gov-os-worktrees/` or `/home/usain/`; if a search shows you a line of the implementation anyway, stop
  and say so.
- **Search again once (DEC-1092 (1)):** if a search (Grep and Read; no `gov retrieve` in the sandbox) does not answer,
  search once more in your own, different words; then answer from both, with path and lines, or say "not found".
- No GPU, no model, no network, no real session.
- **The hidden-half rule:** never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder.
- Run your cases with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-141-tests/src` (through the heavy slot where the
  sandbox allows it), and `python3 -m gov.cli.main accept W2-141 --root /home/usain/gov-os-worktrees/W2-141-tests`.
- **DEC-1080:** Read and Grep tools; one simple command per Bash call; no `cd … &&` chains.
- **Commit** on `w2/W2-141-tests`, only `tests/acceptance/W2-141/`, with
  `--trailer "Task: DAEO-xwro" --trailer "Implements: DEC-1093, DEC-1102" --trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- **Before you end your session,** make sure every test run you started has finished.

## Return
Your whole return is your session's **final message**, in full (the launcher keeps it in this worktree's log; it is
the record): the twelve labelled fields of `EMG-common.md` (sandbox and `ps` checks first), the new cases (node id, KPI
line, red or green on integrate, why), any round-1 case changed, the commit, `gov accept`'s counts, `TESTS-READY` text.
