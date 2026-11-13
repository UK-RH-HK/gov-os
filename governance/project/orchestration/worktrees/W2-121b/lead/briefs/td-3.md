# Brief: independent test designer, DAEO-ifgf (W2-121b), FULL, class C2 — one S2 case from the review's finding (round 2, td-3)

Budget: projection 2 USD. A small batch: one or two cases in your own suite `tests/acceptance/W2-121b/`, nothing else.
Keep your context short.

You are a fresh independent test designer (MR-3) for ticket DAEO-ifgf (W2-121b). You work only in
`/home/usain/gov-os-worktrees/W2-121b-tests` on branch `w2/W2-121b-tests` (DEC-963). You never read the
implementation (part b's code under `src/gov/dispatch/`) or the engineer's records; you write to the ticket's KPI
lines and `## Interface` only (`/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-ifgf.md`, binding).

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

## The finding (from the independent review, as described behaviour)

S2 says "a running close with a ticket in the landing's set blocks the landing"; the Interface (item 2): "A running
close is a process matching `job_markers["close"]`; the tickets it closes are those of its arguments equal to a W2 id
or ticket id in the landing's set." In ordinary work a close is started through a shell: an agent's Bash tool runs
`/bin/bash -c "… gov close W2-7 …"` (the whole command in **one** argument of the shell), and cron runs `sh -c "…"`.
Then two processes match the close marker: the wrapper shell (whose arguments hold the command as one string, so no
argument equals `W2-7`) and its child, the close itself (`… gov-close-stub W2-7`, whose argument does equal `W2-7`).
The landing of W2-7 must be held: the child is a process matching the marker with an argument equal to a W2 id in the
landing's set. Today's suite plants every close as one flat process, so it does not reach this.

## What to write

Add to `test_b_s2_closes.py` (and map it in `README.md` under S2 with its full node id):
- A close under a shell wrapper blocks the landing of its ticket: plant (with `plant_proc` and its `ppid` argument) a
  wrapper process, e.g. argv `["/bin/bash", "-c", "cd /x && gov-close-stub W2-<n> ; echo done"]`, and as its child the
  close itself, argv `[<python>, "<stub path>/gov-close-stub", "W2-<n>"]` with `ppid` = the wrapper's pid; approve
  W2-<n> in `land.txt` with a clean tree; tick: held (exit 0, no landing command run, `land.txt` not claimed, a `land: `
  line in the status), as in the existing flat-close cases. Cover the ticket-id form too (the child's argument the
  `DAEO-…` id), as one parametrised case or a second case.
- Keep a positive pairing so the case is red now and green only when the hold works: e.g. after the hold, remove the
  two planted processes (or plant the same wrapper with a different ticket) and tick again: the batch goes.

Change nothing else in the suite.

## Check and commit

1. Run your suite with the pytest line above. The branch carries the engineer's current code: the new case(s) should
   be red there (the landing goes), and the other 48 green. Quote the last line and the new cases' one-line failure
   reasons. If the new case is green, say so and why: it then checks nothing new.
2. Commit only your paths:

       git commit -m "W2-121b acceptance: a close under a shell wrapper blocks the landing of its ticket (S2, review round 1 RV1)" --trailer "Task: DAEO-ifgf" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1014" --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" -- tests/acceptance/W2-121b

   Then quote `git log --oneline -2` and `git status --short`.

## Return

One message, your last. The twelve fields first, each a labelled line ("none" where nothing):
task / status (DONE, PACKAGES, ESCALATION, AUTH_REQUIRED, with one line of why) / work_completed / files_changed /
evidence (the sandbox check, the run's last line, the commit hash with its trailers) / tests / discoveries / risks /
lessons / proposed_decisions / unresolved / recommended_next_action. Then `guard_refusals:` (none, or time | form |
reason).
