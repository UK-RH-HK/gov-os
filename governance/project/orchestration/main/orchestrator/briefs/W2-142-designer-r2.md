# W2-142 — the independent test designer's brief, round 2: the discovery skill's version (DAEO-qskx)

You are a fresh independent test designer for **W2-142** (`.tickets/DAEO-qskx.md`). Round 1 (`3d2071225`, 8 cases in
`tests/acceptance/W2-142/`) held the discovery skill's version at 1.0.0 (its D-1). The CTO decided the version is
bumped: S2 now reads "its version 1.0.0 to 1.1.0" (marked DEC-1097 (8)).

**Your job:** revise the cases so S2 checks the discovery skill's version is 1.1.0 (red on integrate) and F1's
discovery comparison sets aside the version line as well as the added sentence. Nothing else changes. Each changed
case is its own commit with `--trailer "Rewrite-Reason: DEC-1097 (8)"`; update the README's map.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-142-tests`, branch `w2/W2-142-tests` (integrate merged in today).
- You write only `tests/acceptance/W2-142/`.

## Rules
- **Never read this ticket's implementation (G-14):** never open `/home/usain/gov-os-worktrees/W2-142` or the branch
  `w2/W2-142`. Keep every search inside your own worktree (DEC-1093 (2)).
- **Search again once (DEC-1092 (1)):** if a search does not answer, search once more in your own words; then answer
  from both, or say "not found".
- **The hidden-half rule:** never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder.
- Run your cases with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-142-tests/src`, and
  `python3 -m gov.cli.main accept W2-142 --root /home/usain/gov-os-worktrees/W2-142-tests`.
- **DEC-1080:** Read and Grep tools; one simple command per Bash call.
- **Commit** on `w2/W2-142-tests` with
  `--trailer "Task: DAEO-qskx" --trailer "Implements: DEC-1094, DEC-1097" --trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"` plus the Rewrite-Reason.
- A small round: a few minutes.

## Return
Your whole return is your session's **final message** (the launcher keeps it; it is the record): the twelve labelled
fields of `EMG-common.md` (sandbox and `ps` checks first), the changed cases, the commit, `gov accept`'s counts,
`TESTS-READY` text.
