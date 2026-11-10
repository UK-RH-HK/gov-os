Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-96-maps-lift-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# The lift's map fixes: the review of W2-92's and W2-05's README maps made readable by gov accept (W2-96, DAEO-ouet)

You are a fresh, read-only independent reviewer. **Narrow scope: two README maps, wording only.** READY is computed
by `verdict.py` from your block.

## What happened
- `gov accept`'s reader (merged `8f6e66a17`: after a cell's first line name, a further name is read only after a join;
  a repeat is ignored; any other further name, e.g. a possessive, refuses the cell) refused two maps of tickets that
  close at the lift:
  - **W2-92** README line 128: `**Success 6 with success 4.** Nothing else in the bundle changes; S1's record route
    answers as before` (the possessive "S1's").
  - **W2-05** README lines 132-134: three `Edge: ...` rows naming no KPI line.
- A test designer revised both READMEs (DEC-866, Rewrite-Reason; wording only, the mapping kept).

## What to review
- `git -C /home/usain/gov-os-worktrees/W2-96-maps-lift-tests diff 1905b2969 d269ed550` (head `d269ed550`, two
  commits: `ba5cf0f87` rewords W2-92 row 128 and names the line of each W2-05 edge row (F1, S2, S1); `d269ed550`
  writes in full four test names that rows 133-134 had elided (`test_..._...`), since `gov accept` fails a line whose
  named test matches no case).
- The ticket files: `.tickets/DAEO-0z8c.md` (W2-05) and `.tickets/DAEO-n0wb.md` (W2-92).

## Check
1. **Same meaning:** W2-92: does the row still list exactly success-6 and success-4, and is the prose's meaning kept?
   W2-05: does each edge row keep its cases and words, and where it now names a KPI line, is that the line the ticket's
   own words place the edge under (nothing a line requires lowered, no case dropped or moved off a line)?
2. **Reads:** read both maps with the reader itself (names only, no suite run):
   `PYTHONPATH=<the worktree>/src python3 -c "from pathlib import Path; from gov.accept.runner import parse_map;
   print(sorted(parse_map(Path('<the worktree>/tests/acceptance/W2-92/README.md').read_text())))"`, and W2-05's.
   Neither raises; W2-92's line set equals the one at integrate (lines named by the other rows plus success-4 and
   success-6). Every backticked item of W2-05 rows 132-134 that `names_a_test` accepts names an existing test (and
   row id), each the one its elided form meant, so no line fails for a name matching no case.
3. **Trailers and scope:** Task, Role, Implements, Rewrite-Reason and Co-Authored-By; only the two READMEs changed;
   no Tests cell changed.

KPI id for the verdict block: `lift-maps-readable`.

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word. Every finding carries `Ordinary work: yes|no, because …` and
`Consequence: fails open|loses work|other`, and `scope: in` only if it concerns this revision.

## Write and return
- **You write nothing** in any tree. No test runs (the reader check only). No GPU, no installs. Single simple Bash
  commands (DEC-1080). `EMG-common.md`'s hidden-half rule holds.
- **Your record is your session's final message**, in full:
  - the twelve labelled fields of `EMG-common.md` (sandbox and `ps` checks first);
  - your answers to the checks;
  - every finding, with its two lines and its scope;
  - at the end, the fenced `verdict` block:
    `{"kpis": [{"kpi": "<id>", "verdict": "pass|fail", "findings": [...]}]}`, one entry per KPI id named above,
    each finding `{"id", "scope", "ordinary_work", "consequence"}` (ids from F1).
- Estimate: 10 minutes.
