# Brief td-2: independent test designer, fix round, for DAEO-cb2b (W2-121, part a), profile FULL, class C2

You are the independent test designer (MR-3) for ticket DAEO-cb2b (W2-121, part a: `gov dispatch tick` and
`gov dispatch status`). Your first batch (td-1, commit 0384e71db) is the acceptance suite in `tests/acceptance/W2-121/`
(read its README.md and `w2_121_support.py` first: the planted project, the stubs and the helpers are yours). The
independent review's round 1 failed with findings you now turn into tests, as **described behaviours**: you get the
behaviour, never the engineer's code. You never read the engineer's work on this ticket (`src/gov/dispatch/**`,
`tests/unit/dispatch/**`; the guard refuses them).

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-121-tests |
| branch | w2/W2-121-tests |
| your allowed paths | tests/acceptance/W2-121/** |
| ticket (KPI S2, S4, S5, S6, S9; the Interface section; the sections P-W2-121-5 to P-W2-121-7 at its end) | /home/usain/gov-os-worktrees/W2-121-tests/.tickets/DAEO-cb2b.md |
| the round-1 interface readings (still hold) | /home/usain/gov-os-worktrees/W2-121/.gov-runtime/scratch/lead/briefs/interface-1.md |
| **the fix round's readings (build to these)** | /home/usain/gov-os-worktrees/W2-121/.gov-runtime/scratch/lead/briefs/interface-2.md |
| the gate you plant | src/gov/resources/machine.py, src/gov/resources/config.py, src/gov/resources/gate.py (docstrings) |
| the context bundle (the ticket and its sources, as `gov context` built it) | /home/usain/gov-os-worktrees/W2-121/.gov-runtime/scratch/lead/briefs/ctx-td-2.md |
| the sources (read each by id in docs/DECISION_REGISTER.md; grep the register only by id) | DEC-1007, DEC-1010, DEC-1014, DEC-998 |

Search with the Read, Grep and Glob tools; if the first search does not answer, search once more in different words,
then answer from both or say "not found" (DEC-1065). No `gov retrieve`, no `gov context` in the sandbox.

## The behaviours to test (one test or more each; name each after its KPI: `test_s4_...`, `test_s2_...`)
- **F-1 (S4):** an inbox item, once written, is never written again as unread. Planted: a finished session's return item
  is written; it is read (moved to `inbox/read/`) and then deleted; the next passes write no item for that log in
  `inbox/` (nor in `inbox/read/`). The same when the item is deleted straight from `inbox/` unread. The same for a start
  that never ran (its never-ran item deleted: not written again). If cheap, the same for an S7 owner item.
- **F-2 (S4):** an escalation is recorded only after the notifier exits 0, retried at a bounded cadence, its failure shown
  every pass. Planted (your stub notifier given a planted exit code, as your stub launcher has one):
  (a) the notifier exits 1 with `notify_retry_s: 0`; the next pass, with the notifier fixed (exit 0), runs it again for
  that item; after that success no more runs for it on later passes;
  (b) the notifier keeps exiting 1 with `notify_retry_s: 3600`: the pass after the failure does not run it again, and
  that pass's status (`status.txt` and `status.json`'s `problems`) still names the item's failed escalation;
  (c) a notifier that times out (your `set_notify_sleep` past a small `command_timeout_s`): the escalation is not
  recorded as raised: with `notify_retry_s: 0` and the notifier then working, a later pass runs it for that item;
  (d) a failed notifier does not fail the pass: exit 0 (no start refused), `ok` true in `status.json`.
  (e) an item read (moved to `inbox/read/`) while its escalation is failing is never retried and its problem line goes.
- **F-3 (S4, S5):** a `dispatch.yaml` without `notifier_command` (and one with `[]`): `tick` exits 2 naming
  `notifier_command`, starts nothing (a ready entry planted; the stub launcher never runs), and the status's first line
  is `PASS FAILED ...` naming it. Add `notifier_command` to the missing-key cases you already have if that is how your
  suite is built.
- **F-4 (S9):** a return whose `files_changed:` names a file that exists in the ticket's worktree only untracked (not
  committed, not ignored): the item's `unresolved:` line names it. Guards in the same case or beside it: a committed
  path is not named; a path that exists and is ignored by the worktree's `.gitignore` is not named.
- **F-5 (S2, S6):** the shut-gate refusal that only the gate gives: a gate shut for load (or CPU busy cores) with memory
  ample for every peak (so the room check alone would admit): no start, exit 3, every entry skipped with a reason that
  names the gate and does not rest on memory. Tighten your existing shut-gate tests if they accept a "memory" reason
  where the gate is what must refuse.

Not yours: F-6 (the engineer's, a unit test).

## Rules
- Keep every existing test green on its own behaviour; change an existing test only where the readings above change the
  behaviour (F-2: an escalation is no longer recorded on a failed notifier; F-3: a missing notifier is exit 2 at load)
  and say which in `work_completed`.
- The new cases are red now against the current code where the behaviour is missing (F-1, F-2, F-3, F-4 expected red;
  F-5 may be green: it guards a check that exists). Run them and say which are red and why.
- Everything planted under pytest's tmp_path as in your first batch: never the real HOME, ~/.claude, the real /proc for
  counting, or a real session; bounded polls, never a bare sleep. Seconds per case.
- Every pytest run goes through the heavy-slot gate, one folder per run, TMPDIR outside the repository:
  `env HOME=/home/usain/gov-os-worktrees/W2-121-tests/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local TMPDIR=/tmp PYTHONPATH=/home/usain/gov-os-worktrees/W2-121-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-121 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
  (a single file or `-k` selection in the same form while you work).
- Update README.md's KPI-to-test table for the new cases.
- One-line commands only; anything longer in a script under /home/usain/gov-os-worktrees/W2-121-tests/.gov-runtime/scratch/.
  Literal paths only as write targets.
- Commit your paths only:
  `git commit -m "<subject>" --trailer "Task: DAEO-cb2b" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1007, DEC-1010, DEC-1014, DEC-998" -- tests/acceptance/W2-121`

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed / files_changed / evidence (the pytest summary line; the new cases with red or green and why) / tests /
discoveries / risks / lessons / proposed_decisions / unresolved / recommended_next_action. Then `commits:` (hash12,
subject, trailers) and `guard_refusals:` (none, or each: time | form | the hook's reason | true or false-positive).
A question the ticket and these readings do not settle: write your reading into the test's docstring and name it in
`unresolved`.
