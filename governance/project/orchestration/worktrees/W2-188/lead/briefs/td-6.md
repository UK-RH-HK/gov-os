# W2-188 (DAEO-zlog): finish the README map fix so gov accept reads every map row (brief td-6, from the ticket lead)

You are a fresh independent test designer for ticket **DAEO-zlog (W2-188)**, profile STANDARD, class C3. Use your skill
`test-design`. You finish **one README edit** and nothing else (the CTO's routing under DEC-1156 (7); DEC-1184 names the
close on `gov accept`).

## Why
`gov accept W2-188` refuses: `ACCEPT_MAP_UNREADABLE: ... a map row naming no KPI line it can read`. The previous test
designer (brief td-5) moved the five matcher self-checks out of the map table into their own list (that edit is in your
tree, **uncommitted**: `git diff` shows it) and then found, with `parse_map` (`src/gov/accept/runner.py:138-190`), two
more causes, both in the map table's KPI cells:
1. Every KPI cell starts with a backticked name (`` `success-1` (...) ``). `line_names` reads a line name only at the
   cell's start, so the backtick makes all eight cells name no line.
2. The `failure-3` cell's words "§9 keeps S10's second reranker forbidden" hold `S10`, which the reader takes as an
   unlisted line `success-10` (`Unlisted`).
The lead checked both with the product's reader and ran `gov accept` on a throwaway clone with the fix below: `pass`,
54 passed, 0 failed (5 unmapped: the self-checks). The lead approves P-W2-188-MAP-1 (a).

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-188-tests |
| branch | w2/W2-188-tests (from w2/W2-188 at fbcfef374), README edited and uncommitted |
| the only path you write | tests/acceptance/W2-188/README.md |
| the ticket (read-only) | /home/usain/gov-os-worktrees/W2-188-tests/.tickets/DAEO-zlog.md |

Never read /home/usain/gov-os-worktrees/W2-188 (the counterpart's tree), nor in your own tree the counterpart's work on
this ticket: `docs/changes/W2-188-CIT-P.md`, `docs/probes/DAEO-zlog/**` (DEC-820). Register by id only.

## The edit (on top of the uncommitted one; keep it)
1. In each of the eight map rows (`success-1` to `success-5`, `failure-1` to `failure-3`), drop the two backticks round
   the line name at the start of the KPI cell: `` | `success-1` (A9's ...`` becomes `| success-1 (A9's ...`. Nothing
   else in those cells changes, except:
2. In the `failure-3` row's KPI cell, put `S10` in a code span: "§9 keeps S10's second reranker forbidden" becomes
   "§9 keeps `S10`'s second reranker forbidden".
3. No other byte of the table changes (the tests cells and the expected-red cells stay).
4. Replace the td-4 note added by the previous designer with this one (keep the backticks round the Rewrite-Reason, as
   the earlier notes do): `Revised 2026-11-14 (briefs td-5 and td-6, `Rewrite-Reason: DEC-1184, DEC-1156 (7)`): the five
   matcher self-checks moved from the map table to their own list below it, the eight KPI cells name their line without
   backticks, and the failure-3 cell's S10 stands in a code span, so that gov accept reads every map row; the count stays
   54 cases, no case changed.` (wrap it as the earlier notes are wrapped).
5. **No test file changes. No other README change.** If you find you must change anything else, stop, do not commit,
   and say what and why in `unresolved`.

## Check (record what you ran in your return)
- Parse the README with the product's own reader (a script under the sandbox's own `$TMPDIR`, never a new folder under
  `.gov-runtime/scratch/`):
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-188-tests/src python3 -c "from gov.accept.runner import parse_map; import pathlib; m=parse_map(pathlib.Path('/home/usain/gov-os-worktrees/W2-188-tests/tests/acceptance/W2-188/README.md').read_text()); print(sorted(m), sum(len(v) for v in m.values()))"`
  Expected: the eight lines and 53, nothing raised.
- `git diff --stat` names only the README; `git diff` shows only the row removal, the eight cells' backticks, the S10
  code span, and the new heading, list and note.
- Run the folder once through the heavy slot, with the sandbox's own `$TMPDIR` (the empty home folder already exists;
  do not create it):
  `env HOME=/home/usain/gov-os-worktrees/W2-188-tests/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-188-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-188 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
  (a resource gate's refusal is a wait). Expected: 54 passed, 0 failed.

## Commit (your path only; trailers in ONE final paragraph)
```
git commit -m "W2-188 (DAEO-zlog): the README's map reads in gov accept: the five self-checks in their own list, the KPI cells' line names without backticks, S10 in a code span (DEC-1184)" --trailer "Task: DAEO-zlog" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1156, CAP-33" --trailer "Rewrite-Reason: DEC-1184, DEC-1156 (7)" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- tests/acceptance/W2-188/README.md
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
