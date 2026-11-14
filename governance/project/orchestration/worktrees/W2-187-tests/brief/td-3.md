Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-187-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# Brief td-3: independent test designer for DAEO-0cd2 (W2-187), fix batch 2, profile FULL, class C2

You are a fresh independent test designer (MR-3) for ticket DAEO-0cd2 (W2-187: the memory audit's standing hidden set).
The suite `tests/acceptance/W2-187/` and the revisions of the W2-170, W2-171 and W2-172 files are merged with the
engineer's code, and `w2/integrate` is merged too, which brings three changes to the ticket since the suite was written.
You do exactly the three items below, as described behaviour (DEC-136), and change nothing else. The ticket's
`## Interface` (I1-I12) is binding; if you read an item differently from the reading below, say so as a package
(question, options with cost, recommendation, confidence, what it blocks), and do not change it.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-187-tests |
| branch | w2/W2-187-tests (now at f66fba56a) |
| your allowed paths | tests/acceptance/W2-187/**, tests/acceptance/W2-171/test_w2_171_cli_layout_ledger.py, tests/acceptance/W2-171/test_w2_171_s5_misses_f2.py |
| the ticket (amended: read S10, F5, the Interface's I10 item 6, and the three "Amended"/"Path case" paragraphs at its end) | /home/usain/gov-os-worktrees/W2-187-tests/.tickets/DAEO-0cd2.md |
| the suite's map and S10 helpers | tests/acceptance/W2-187/README.md, test_w2_187_s10_maintain.py, w2_187_maintain.py, w2_187_world.py |
| W2-61h's N2 (b) cases (how a rewritten heading-cited section was planted there; read for ideas, never edit) | tests/acceptance/W2-61h/w2_61h_support.py, test_w2_61h_visible_new.py |
| how `gov accept` reads the README's map | src/gov/accept/runner.py (`parse_map`, `line_names`) |

You may run the engineer's code; do not read the engineer's changes under `src/gov/memaudit/`,
`src/gov/adopt/memory_sets.py` or `governance/project/orchestration/tools/memaudit_cron.sh` (the base copies are at
`git show 5336a6fca:<path>`). Search with the Read, Grep and Glob tools; if the first search does not answer, search
once more in different words, then answer from both or say "not found" (DEC-1065). No `gov retrieve`, no `gov context`
in the sandbox. Everything planted under `tmp_path`; never the real sets root, the real runs folder or any hidden or
memory-verdict folder (DEC-820).

## The three items
1. **The README's map is unreadable to `gov accept`.** `gov accept W2-187` refuses with
   `ACCEPT_MAP_UNREADABLE: ... the README of tests/acceptance/W2-187/ has a map row naming no KPI line it can read`.
   The row is `| scope | ... test_scope_the_branch_changes_only_the_tickets_allowed_paths_and_its_acceptance_folder |`.
   That case guards no KPI line. Take the row out of the map table and name the case in prose below the table (an
   unmapped case still runs and still counts as a failure if red). Check the result with the parser:
   `PYTHONPATH=/home/usain/gov-os-worktrees/W2-187-tests/src python3 -c "from pathlib import Path; from gov.accept.runner import parse_map; m = parse_map(Path('tests/acceptance/W2-187/README.md').read_text()); print(sorted(m), sum(map(len, m.values())))"`
   It must print every `success-1` to `success-11` and `failure-1` to `failure-6` and raise nothing. Do not add a map
   row for S12 or F7: their interface is not stated yet (the lead's package W2-187-S12), and they come in a later batch.
   Commit with no Rewrite-Reason (the README is this ticket's own).
2. **The CTO's path case W2-187-P1 (a)** (the ticket's "Path case 2026-11-14" paragraph; DEC-1156 (7)): two W2-171 files
   pin the 85 % bar.
   - `tests/acceptance/W2-171/test_w2_171_cli_layout_ledger.py:120-121`
     (`test_the_ledger_events_have_item_3s_fields`) plants 35 right of 40 and expects `"passes": True`.
   - `tests/acceptance/W2-171/test_w2_171_s5_misses_f2.py:82`
     (`test_s5_a_verdict_below_the_bar_stands_as_recorded_and_is_a_result`) expects `BAR at least 34 right (NOT met)`.

   Revise the bar values only (at 95 % the bar on 40 is 38), keeping what each case guards: the first plants a passing
   verdict, the second one below the bar. Make the smallest change; nothing else in either file. Commit with
   `Rewrite-Reason: DEC-1179 (2)`.
3. **N2 (b) in S10 (6) and I10 item 6** (DEC-1180 (1), the ticket's first "Amended 2026-11-14" paragraph). Add a case to
   `test_w2_187_s10_maintain.py`: a planted heading-cited source whose section text (from its heading line to the next
   heading of the same or a higher level, or the end of the file) differs between the source's own commit and the head,
   while its heading is still found, is listed in `REANCHOR-<week>.json` by question id and entry number. A heading-cited
   section unchanged is not listed. An entry that both moved-and-changed and was rewritten is listed once. The existing
   S10 (6) case (one changed cited block listed, one moved unchanged block not) keeps passing, and no question, answer or
   path text is in the request or the digest. Map the new case under `success-10` in the README. Commit with
   `Rewrite-Reason: DEC-1180 (1)`. This case is red until the engineer builds N2 (b) in parallel; say so.

## Rules
- **Every pytest through the heavy-slot gate**, the sandbox's own `$TMPDIR`:
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env HOME=/home/usain/gov-os-worktrees/W2-187-tests/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-187-tests/src python3 -m pytest tests/acceptance/W2-171 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
  For item 2, run the whole `tests/acceptance/W2-171` folder (it must be green). For item 3, run
  `tests/acceptance/W2-187/test_w2_187_s10_maintain.py`. Report each summary line. A heavy-slot refusal is a wait;
  run again when it opens. Run a long one with a Bash timeout of 3600000 ms.
- Literal paths only as write targets. If a Write into `.gov-runtime/scratch/` is refused, write no script; use
  one-line commands.
- **Commit** your paths only, one commit per item, the trailers in ONE final paragraph:
  `git commit -m "<subject>" --trailer "Task: DAEO-0cd2" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1179, DEC-1156" [--trailer "Rewrite-Reason: ..."] --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" -- <your paths>`
  Never `Role: owner` or `Decided-by:`. No merge, no push, no edit of `.tickets/` or the register.
- Refused twice for the same call by the guard, the sandbox or a hook: stop and say so; never reach the same effect by
  another command, form or file (DEC-1142 (9)). A permission denial of a Write is a refusal too: do not redo it by
  another form.

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed / files_changed / evidence (the pytest summary lines, the parser's output) / tests / discoveries / risks
/ lessons / proposed_decisions / unresolved / recommended_next_action. Then `commits:` (hash12, subject, trailers) and
`guard_refusals:` (none, or each: time | form | the hook's reason | true or false-positive).
