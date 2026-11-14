# W2-188 (DAEO-zlog): move the five matcher self-checks out of the README's map table (brief td-4, from the ticket lead)

You are a fresh independent test designer for ticket **DAEO-zlog (W2-188)**, profile STANDARD, class C3. Use your skill
`test-design`. You make **one README edit** and nothing else (DEC-1184, the CTO's routing under DEC-1156 (7)).

## Why
`gov accept W2-188` refuses before running anything: `ACCEPT_MAP_UNREADABLE: the README of tests/acceptance/W2-188/ has a
map row naming no KPI line it can read`. The cause is the map table's last row in `tests/acceptance/W2-188/README.md`
(line 30): its KPI cell reads "matcher self-checks (no KPI line; ...)". `gov accept`'s map reader
(`src/gov/accept/runner.py`, `parse_map`, lines 138-190) refuses any row of a table with a `KPI` column whose KPI cell
names no `success-N` / `failure-N` line. Text outside a table (a heading and a list) is not read as map rows. The suite
itself is green (54 passed, 0 failed).

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-188-tests |
| branch | w2/W2-188-tests (from w2/W2-188 at fbcfef374) |
| the only path you write | tests/acceptance/W2-188/README.md |
| the ticket (read-only) | /home/usain/gov-os-worktrees/W2-188-tests/.tickets/DAEO-zlog.md |

Never read /home/usain/gov-os-worktrees/W2-188 (the counterpart's tree), nor in your own tree the counterpart's work on
this ticket: `docs/changes/W2-188-CIT-P.md`, `docs/probes/DAEO-zlog/**` (DEC-820). Register by id only
(`docs/DECISION_REGISTER.md`; `### DEC-1184`, `### DEC-1156`).

## The edit (described behaviour)
1. Remove the map table's last row (line 30, `| matcher self-checks (no KPI line; ...) | ... | None: green now by design
   ... |`) from the table. No other row of the table changes, not by one byte.
2. Directly below the table (after line 30's removal, before the "Totals on the base" paragraph), add a heading at the
   same level as the map's heading plus one, or at the same level (`### Self-checks (no KPI line)` is suggested), and a
   short list: one line saying what the row's KPI cell and its last cell said ("they guard the readers' tolerance and
   strictness on made-up texts"; "green now by design (they read no repository file)"), then one list item per case,
   the five case ids word for word as the row names them
   (`test_w2_188_selfchecks.py::test_selfcheck_...`, each in backticks). Keep the wording of the row apart from the move.
3. Add one line to the "Revised 2026-11-14" notes, in their form: `Revised 2026-11-14 (brief td-4, Rewrite-Reason:
   DEC-1184, DEC-1156 (7)): the five matcher self-checks moved from the map table to their own list below it, so that
   gov accept reads every map row; the count stays 54 cases, no case changed.`
4. **No test file changes. No other README change** (the totals paragraph, the readings and the files table stay).
   If you find you must change anything else, stop, do not commit, and say what and why in `unresolved`.

## Check (record what you ran in your return)
- Parse the README with the product's own reader from your tree, through a script under the sandbox's own `$TMPDIR`
  (never a new folder under `.gov-runtime/scratch/`):
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-188-tests/src python3 -c "from gov.accept.runner import parse_map; import pathlib; m=parse_map(pathlib.Path('/home/usain/gov-os-worktrees/W2-188-tests/tests/acceptance/W2-188/README.md').read_text()); print(sorted(m), sum(len(v) for v in m.values()))"`
  It must print the eight lines (`failure-1..3`, `success-1..5`) and raise nothing.
- `git diff --stat` names only the README; `git diff` shows the one row removed and only the new heading, list and
  note added.
- Run the folder once on your branch through the heavy slot, with the sandbox's own `$TMPDIR`:
  `env HOME=/home/usain/gov-os-worktrees/W2-188-tests/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-188-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-188 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
  (a resource gate's refusal is a wait: wait and retry; if the sandbox refuses the heavy slot itself, run the same pytest
  line without it and say so). Expected: 54 passed, 0 failed. Report each red's one-line reason as the assertion gives
  it; do not open the counterpart's record to explain a red.

## Commit (your path only; trailers in ONE final paragraph)
```
git commit -m "W2-188 (DAEO-zlog): the README's five matcher self-checks move from the map table to their own list, so gov accept reads every map row (DEC-1184)" --trailer "Task: DAEO-zlog" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1156, CAP-33" --trailer "Rewrite-Reason: DEC-1184, DEC-1156 (7)" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- tests/acceptance/W2-188/README.md
```

## Rules
- Write files with the Write and Edit tools and absolute paths. Anything longer than one line goes in a script under the
  sandbox's own `$TMPDIR`.
- Refused twice for the same action by the guard, the sandbox or a hook: stop and say so; never work around it.
- Never open the evaluation sets' root or any hidden or memory-verdict folder; never secrets.
- No new ticket; a gap comes back in `unresolved` as a question with options.

## Return (your last message; only it is read)
The sandbox check and the `ps` check first, then the twelve fields as labelled lines (task, status, work_completed,
files_changed, evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action),
then: your commit's hash; the `parse_map` output; the pytest counts (passed / failed) with each red's reason in one line;
and a `TESTS-READY` text (the lead writes the marker).
