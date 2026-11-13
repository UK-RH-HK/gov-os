# Brief: independent test designer, DAEO-ifgf (W2-121b), FULL, class C2 — fix two acceptance cases (build, td-2)

Budget: projection 2 USD. A small batch: two cases in your own suite `tests/acceptance/W2-121b/`, nothing else.
Keep your context short.

You are a fresh independent test designer (MR-3) for ticket DAEO-ifgf (W2-121b). You work only in
`/home/usain/gov-os-worktrees/W2-121b-tests` on branch `w2/W2-121b-tests` (DEC-963). You never read the
implementation (`src/gov/dispatch/landing.py` and the rest of part b's code) or the engineer's records; you write to
the ticket's KPI lines and `## Interface` only (`/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-ifgf.md`,
binding).

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-ifgf','w').write('x')"` must fail;
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the
file or (b) failed, stop and return (delete nothing).

## Standing rules

- First `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer`, `DAEO-ifgf`) and
  `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-121b-tests`,
  `w2/W2-121b-tests`).
- **Writes:** only `tests/acceptance/W2-121b/**`. Scripts, if any, as files under your TMPDIR.
- **Every pytest** through the heavy slot, with the sandbox's TMPDIR (outside the repository and outside
  `~/gov-os-runs`), in this form (create the empty-home folder first if absent):
  `env TMPDIR=<your TMPDIR> PYTHONUSERBASE=/home/usain/.local HOME=/home/usain/gov-os-worktrees/W2-121b-tests/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-121b-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-121b -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
  A busy heavy slot is a wait: retry. If the sandbox refuses the heavy slot itself, say so and run the same line
  without `bash .../heavy_slot.sh`.
- No `gov retrieve` or `gov context`; Read and Grep only. No `$(…)` or variable as a write target, no here-document,
  no `bash -c`. Foreground only. No reset, checkout, clean, amend, rebase, push, merge, stash or install.
- Refused twice for the same call: stop and say so; never reach the same effect by another command, form or file.
  On an authentication error return `AUTH_REQUIRED`.

## The two findings (described behaviour; fix your cases to the ticket)

1. `test_b_s1_landing_batch.py::test_approved_tickets_go_as_one_batch_claimed_before_the_launch` asserts the batch's
   log reads "landing stub ran with 2 approval". The planted command is `... --before {approvals} --after`; by the
   Interface the token is replaced in place, so the stub receives four arguments (two flags and the two approvals),
   and the stub (`w2_121b_support.py`'s `LAND_STUB`) prints the count of *all* its arguments after `rec state`. A
   correct implementation therefore logs 4, and the case is red against the ticket. Make the log assertion check
   what the ticket states (that the log is the batch's output), e.g. have the stub count only the `<W2>=<12-hex>`
   arguments, or assert the count of all arguments; keep the argv assertions as they are.
2. `test_b_s3_nightly_hold.py::test_a_window_crossing_midnight_does_not_hold_outside_it` plants
   `configure(p, 60, 30)`: `from` = now+60 min, `until` = now+30 min. With `from` > `until` the window crosses
   midnight, so the window that began yesterday at `from` runs until today's `until` (now+30): now is *inside* it and
   the hold is correct by the Interface; the case's own comment ("now is after `until` and before `from`") needs
   `until` before now. Plant `until` before now and `from` after it (e.g. `configure(p, 60, -30)`), keeping the
   30-minute margins and the near-midnight skip.

Change nothing else. If either finding is wrong against the ticket in your reading, leave that case, and say why
with the ticket's line.

## Check and commit

1. Run your suite with the pytest line above (the branch carries the engineer's code: expect all green but for any
   case you judge otherwise). Quote the last line, and any failure's one-line reason.
2. Commit only your paths:

       git commit -m "W2-121b acceptance: two cases fixed to the ticket (the batch log's count; the midnight-crossing window's outside case)" --trailer "Task: DAEO-ifgf" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1007, DEC-1018" --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" -- tests/acceptance/W2-121b

   Then quote `git log --oneline -2` and `git status --short`.

## Return

One message, your last. The twelve fields first, each a labelled line ("none" where nothing):
task / status (DONE, PACKAGES, ESCALATION, AUTH_REQUIRED, with one line of why) / work_completed / files_changed /
evidence (the sandbox check, the run's last line, the commit hash with its trailers) / tests / discoveries / risks /
lessons / proposed_decisions / unresolved / recommended_next_action. Then `guard_refusals:` (none, or time | form |
reason).
