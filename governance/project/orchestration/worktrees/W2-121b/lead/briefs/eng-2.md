# Brief: engineer, DAEO-ifgf (W2-121b), FULL, class C2 — fix four red S2 cases (round 2, eng-2)

Budget: projection 3 USD. A small fix. Keep your context short.

You are a fresh engineer for ticket DAEO-ifgf (W2-121b). You work only in `/home/usain/gov-os-worktrees/W2-121b` on
branch `w2/W2-121b`. Part b's code is already built (commit `ab5799760`: `src/gov/dispatch/landing.py`, `heavy.py`
and changes in `config.py`, `procs.py`, `run.py`, `state.py` and `status.py`). 48 of 52 acceptance cases pass.
Four new cases are red; make them green without turning any other case red. You never read or edit
`tests/acceptance/` (your role's reads are denied there). You see the cases' names, pass/fail and failure messages
through pytest only.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-ifgf','w').write('x')"` must fail;
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the
file or (b) failed, stop and return (delete nothing).

## Standing rules

- First `printenv GOV_ROLE GOV_TICKET` (expect `engineer`, `DAEO-ifgf`) and
  `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-121b`, `w2/W2-121b`).
- The ticket's `## Interface` is binding: `/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-ifgf.md`, read
  item 2 (closes).
- **Writes (allowed paths only):** `src/gov/dispatch/**` and `tests/unit/dispatch/test_w2_121b*`. Do not change what
  part a's `procs.find` reports in its `jobs` list (part a's suites `tests/acceptance/W2-121/` and
  `tests/unit/dispatch/` must stay green); compute what part b needs in part b's code. Scratch files go under
  `/home/usain/gov-os-worktrees/W2-121b/.gov-runtime/scratch/eng/`.
- **Every pytest** goes through the heavy slot, with a TMPDIR outside the repository and outside `~/gov-os-runs`, in
  this form (create the empty-home folder first if absent):
  `env TMPDIR=<your TMPDIR> PYTHONUSERBASE=/home/usain/.local HOME=/home/usain/gov-os-worktrees/W2-121b/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-121b/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <FOLDER or file> -q --tb=line -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
  A busy heavy slot is a wait, not a refusal: retry.
- No `gov retrieve` or `gov context`; Read and Grep only (search again once, in other words). No `$(…)` or variable
  as a write target, no here-document, no `bash -c`. Foreground only. No reset, checkout, clean, amend, rebase, push,
  merge, stash or install.
- Refused twice for the same call (guard, sandbox or hook): stop and say so; never reach the same effect by another
  command, form or file. On an authentication error return `AUTH_REQUIRED`.

## The failing output (all you are given)

`tests/acceptance/W2-121b/test_b_s2_closes.py::test_a_close_under_a_shell_wrapper_blocks_the_landing_of_its_ticket`,
parametrised `[w2-id-bash-c]`, `[w2-id-sh-c]`, `[ticket-id-bash-c]`, `[ticket-id-sh-c]`: 4 failed, each
`AssertionError: the landing went ahead although it must wait`. The landing stub ran with argv
`['W2-7=a1b2c3d4e5f6']` and `land.txt` was claimed. The planted processes: a wrapper
`[<shell>, "-c", "cd /x && gov-close-stub <id> ; echo done"]` and, as its child (its parent pid is the wrapper's), the
close `[<python>, "/opt/gov/gov-close-stub", <id>]`, where `<id>` is `W2-7` or its ticket id. The configured close
marker is `gov-close-stub`. The same case then removes both processes and plants a wrapper with a child for W2-8 (not
in the landing's set), and expects the batch to go.

## Check and commit

1. Add a unit case in `tests/unit/dispatch/test_w2_121b_landing.py` for the wrapped close. Run `tests/acceptance/W2-121b`,
   then `tests/acceptance/W2-121` and `tests/unit/dispatch`, with the pytest line above. Quote each run's last line.
2. Commit only your paths:

       git commit -m "W2-121b: a close's tickets from every process matching the close marker (a close under a shell wrapper)" --trailer "Task: DAEO-ifgf" --trailer "Role: engineer" --trailer "Implements: DEC-1014" --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" -- src/gov/dispatch tests/unit/dispatch

   Then quote `git log --oneline -2` and `git status --short` (expect empty).

## Return (your last message; nothing else is read)

The twelve fields, each a labelled line ("none" where nothing):
- task
- status (DONE, PACKAGES, ESCALATION or AUTH_REQUIRED)
- work_completed
- files_changed
- evidence (the sandbox check result, and each pytest run's last line)
- tests (counts per suite)
- discoveries
- risks
- lessons
- proposed_decisions
- unresolved
- recommended_next_action

Then `commits:` (hash12, subject, and the trailers as committed) and `guard_refusals:` (none, or time | form | reason).
