# W2-81 (DAEO-l78m), A1: rewrite four map rows of the acceptance README so the pinned `gov accept` reads them (P-W2-81-LAND-2, decided yes by the CTO, 2026-11-11 18:55 UTC, a delegated P2 under DEC-906)

You are a fresh **independent-test-designer**, launched under ticket `DAEO-l78m` (W2-81, "the adoption proving ground").
First run `printenv GOV_ROLE GOV_TICKET`; if it does not print `independent-test-designer` and `DAEO-l78m`, stop at once
and say so. The session is headless: nobody can answer while you work.

`gov brief independent-test-designer DAEO-l78m` refuses (checked 18:55 UTC): `BRIEF_NOT_READY` with `KPI_NO_VERIFY` for S1
to S12 and F1 to F5, plus `NON_GOALS_MISSING` and `EST_LOC_OVER 1200`. This brief is hand-built, as DEC-1130 (1) requires
for a reviewed ticket in progress. `EMG-common.md`, `NIGHT-common.md` and `LIFT-common.md` (beside this file) hold, except
where this brief says otherwise (the hidden-half rule, no installs, never the full suite, no gitleaks).

## The behaviour to fix (DEC-136: a described behaviour)
Since 11-10, W2-96's stricter map reader (`dac10e5df`, `1df7ccd60`; `parse_map` and `line_names` in
`src/gov/accept/runner.py`, which you may read) refuses `tests/acceptance/W2-81/README.md`: `gov accept DAEO-l78m` exits 4
with `ACCEPT_MAP_UNREADABLE` ("a map row naming no KPI line it can read") and runs no case. Nothing is wrong with the 276
cases; they pass under pytest. The map is the table under "The KPI lines of the ticket, mapped to their tests".

**The rule the reader applies.** In a table whose header starts "KPI" and "Tests", a row with backticked items must have a
KPI cell that **starts** (after bold marks) with a KPI line name: `S4`, `F3`, `S1, S2`, `S3-7`, `S3 to 7`, joined by
`,` `;` `/` `&` `+` `and`. What follows the list is prose, but every further line name in the prose is read or refused: one
led by `(`, `,` or `and` and already read is fine (`(S4, F3)`); one such as "item F2" or "F1's fixture" refuses the cell.
Backticked names in the cell are never read for lines.

**The four rows** (README lines 774-777; check the numbers in the file) start their KPI cell with prose, so the reader finds
no line name: `**Review (batch 4)** Items 1 to 10 above ...`, `**Round 3 (DEC-1005)** Items 1 and 2 ...`,
`**Round 2b (DEC-997)** Items 1 to 7 ...`, `**Round 2 (DEC-993)** Items 1 to 7 ...`. The CTO's helper tried, read-only, these
four openings with the rest of each cell left as it is, and the reader then read the whole map:

| Row | New start of the KPI cell (the bold part replaces "**Name (id)** Items ..."; keep the rest of the cell) |
|---|---|
| Review (batch 4) | `**S3, S4, S5, S6, S7, S9, F1, F2, F3, F4** Review batch 4, items 1 to 10 above, each against ...` |
| Round 3 | `**S7, S10, F4, F5** Round 3 (DEC-1005), items 1 and 2 of "The final review's findings": ...` |
| Round 2b | `**S4, S5, S6, S7, S10, F2, F3, F4, F5** Round 2b (DEC-997), items 1 to 7 of "The third review's findings": ...` |
| Round 2 | `**S3, S5, S6, S7, S9, S10, F1, F4, F5** Round 2 (DEC-993), items 1 to 7 above: ...` |

Each list is the union of the per-item lines already written in the cell ("1 and 5 (S4, F3), 2 (S7, F4) ..."); verify
that against the cell as you edit, and fix a list that does not equal it. This is a proposal, not a script: if the reader
refuses a cell in this form, find the nearest wording it reads, which still starts with the lines the row serves, and say
what you changed.

## Task
1. Rewrite only those four rows' KPI cells (their start, as above). **Nothing else changes:** not their Tests cell, not any
   other row, not any text outside the map, no test code, no other file. The mapping of tests to lines is otherwise as it was.
2. Check, in this order (all in the worktree, with this tree's `src`):
   a. `gov accept DAEO-l78m` (the pinned `~/.local/bin/gov`; one run; it runs the 276 cases and takes a few minutes). It
      must no longer refuse with `ACCEPT_MAP_UNREADABLE`; say its exit code and the per-line counts it prints. A red line
      with a real failing case is not yours to fix: name it. Do not run it with an empty `HOME` (pytest is in the user
      site; the child run would crash).
   b. The W2-81 suite once, through the gate:
      `PYTHONPATH=/home/usain/gov-os-worktrees/W2-81/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-81 -q -p no:cacheprovider -o tmp_path_retention_policy=failed`
      expecting 276 passed, none skipped.
3. One commit, only `tests/acceptance/W2-81/README.md`:
   `git commit -m "<subject>" --trailer "Task: DAEO-l78m" --trailer "Role: independent-test-designer" --trailer "Rewrite-Reason: W2-96 S-D10b map reader" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- tests/acceptance/W2-81/README.md`.
   Never merge, push, amend or rebase.

## Where you work
- Worktree `/home/usain/gov-os-worktrees/W2-81`, branch `w2/W2-81`, head `76c9b5cd1071`; no other worker runs there. Check
  `git rev-parse HEAD` and `git status --short` (clean, apart from two untracked empty harness folders under
  `tests/acceptance/W2-81/**/.claude/`, which you leave) before you start; if the head differs, stop and say so.
- Write only `tests/acceptance/W2-81/README.md`. **No commit on `w2/integrate`**; never touch the main tree.
- `TMPDIR`: a folder of your own under `/home/usain/gov-os-worktrees/W2-81/.gov-runtime/scratch/lead/tmp-designer` (for
  sockets, at most `/tmp/gov-os-lead-W2-81`). Scratch budget: 30 GB and 2,000,000 files and folders; report `du -sh` and
  `du -s --inodes` of it in `evidence`, and clean it as you go.

## Rules
- Every wait or stop by pid only, through `tools/proc.sh` (never a name match, never `pgrep -f`, never the Monitor tool).
- Row W2-L423's rule: write none of the keywords `tools/keyword_warn.py` looks for; commit hashes as 12 digits.
- Single simple commands; edit with the Edit tool. A refusal is taken, not routed round; **refused twice for the same call:
  stop and say so**. Hidden-half rule as in `EMG-common.md`: never `~/gov-os-eval/`, `~/gov-os-runs/`, folders named
  `hidden` or `memory-verdict`.
- Estimate: 20 minutes, mostly the two runs. Context: hand over past about 200k tokens.

## Return
The twelve fields first, as labelled lines at the start of their own lines, short: task, status, work_completed,
files_changed, evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action.
Status DONE, PARTIAL or PACKAGES. `work_completed`: the old and new start of each of the four cells. `tests`: the exit code
and counts of 2a and 2b. `files_changed`: the one path and the commit sha (12 digits).
