# Brief td-2: independent test designer for DAEO-p8tv (W2-172), one revision batch, profile FULL, class C2

You are the independent test designer (MR-3) for ticket DAEO-p8tv (W2-172). Your suite `tests/acceptance/W2-172/` is
merged and red at 80da3fbcca0d. The CTO has answered your package PKG-W2-172-TESTS-1 (DEC-1112 (3), 2026-11-12), word
for word:

- **GATE-1 (a):** the driver splits `--gate-cmd`'s value with `shlex.split` and runs the words as given, so the default
  `gov resources --check` works; the Interface's "called with no arguments" reads "run as its words".
- **TD-1 (b):** the 12-line digest does not record `--force`; item 1's "and the digest" is corrected to the counts only.
- **TD-2 (b):** RN-NAME is judged by `STARTS.log` (an audit started), not by a refusal's `COUNTS.json`, so a refused run
  can be retried the same day.

Your task: one batch that revises every case asserting the opposite of TD-1 (b) or TD-2 (b), and nothing else. Your
lead found these (check them and find any others):
1. `test_s4_a_second_start_on_the_same_date_is_refused_rn_name_and_writes_nothing_there`
   (test_w2_172_s2_s4_refusals.py): it plants only `<R>/<A>/` (no `STARTS.log` line) and expects `RN-NAME`. Under
   TD-2 (b) the start is judged by a `STARTS.log` line naming `<A>`: plant that line (the folder too, as a first audit
   leaves it) and keep the "first audit's folder is left as it was" check.
2. `test_s2_the_first_check_that_fails_refuses`, its `RN-NAME` pairs: `make_fail("RN-NAME")` only makes the folder.
   Plant a `STARTS.log` line naming `<A>` instead (mind that a recent `STARTS.log` line is itself `RN-RECENT`, which
   comes before `RN-NAME` in item 3: choose its `at` so the pair still shows the order it means to show, e.g. the
   `(RN-STALE, RN-NAME)` pair, and say how in the docstring).
3. Add one case for TD-2 (b)'s purpose: a refusal (e.g. `RN-NOBASE` or `RN-REBUILD`) that wrote `<R>/<A>/COUNTS.json`,
   then the cause removed, then a retry on the same date starts (reaches `writer-1`).
4. The `forget()` helper and the README's `unresolved` lines on TD-1/TD-2/GATE-1: rewrite them to state the decisions
   (the README's `--force in the digest` and RN-NAME notes, and the wrapper gate default note: `gov resources --check`
   run as its words). The `C.refused_without_a_start(..., had_folder=...)` helper: keep it meaning "the folder existed
   before".
5. Any case asserting `--force` appears in the digest (TD-1 (b)): none known; if one exists, drop that assertion.

Every changed test gets, in its docstring, the line `Rewrite-Reason: PKG-W2-172-TESTS-1 TD-2 (b)` (or `TD-1 (b)`), and
the commit message names it too. Do not weaken any other case. You never read the engineer's work on this ticket
(branch w2/W2-172 beyond 80da3fbcca0d; any `src/gov/memaudit/` driver file this ticket adds, `memaudit_cron.sh`,
`tests/unit/memaudit/` beyond your base): the engineer is working in parallel in that tree.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-172-tests |
| branch | w2/W2-172-tests (from 80da3fbcca0d) |
| your allowed paths | tests/acceptance/W2-172/** |
| the ticket (KPI lines and the Interface at its end; item 3 is the one this batch reads) | /home/usain/gov-os-worktrees/W2-172-tests/.tickets/DAEO-p8tv.md |

Search with the Read, Grep and Glob tools; search again once in different words if the first does not answer
(DEC-1065). No `gov retrieve`, no `gov context` in the sandbox. Never open the real `~/gov-os-eval`, `~/gov-os-runs`, a
hidden half or the crontab.

## Rules
- The suite stays red where it was red (no driver exists at your base); collect it and run the changed files to show
  they fail by failing, not by erroring:
  `mkdir -p /tmp/gov-w2-172-td2 /home/usain/gov-os-worktrees/W2-172-tests/.gov-runtime/scratch/empty-home` then
  `TMPDIR=/tmp/gov-w2-172-td2 bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env HOME=/home/usain/gov-os-worktrees/W2-172-tests/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-172-tests/src python3 -m pytest tests/acceptance/W2-172 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`.
  A heavy-slot or resource refusal is a wait: run again when it opens.
- Anything longer than one line goes in a script under /home/usain/gov-os-worktrees/W2-172-tests/.gov-runtime/scratch/.
  Literal paths only as write targets.
- Commit your paths only, one commit:
  `git commit -m "<subject> (Rewrite-Reason: PKG-W2-172-TESTS-1 TD-2 (b))" --trailer "Task: DAEO-p8tv" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1101, DEC-1125, DEC-1097, DEC-1038, DEC-1050, DEC-1073" -- tests/acceptance/W2-172`
- Refused twice for the same call by the guard, the sandbox or a hook: stop and say so (DEC-1142 (9)).

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed / files_changed (each changed case's node id) / evidence (the pytest summary line) / tests / discoveries
/ risks / lessons / proposed_decisions / unresolved / recommended_next_action. Then `commits:` (hash12, subject,
trailers) and `guard_refusals:` (none, or each: time | form | the hook's reason | true or false-positive).
