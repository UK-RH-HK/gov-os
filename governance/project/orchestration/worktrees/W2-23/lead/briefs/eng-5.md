# Brief: engineer, DAEO-kmcr (W2-23), FULL — S3 fix R2-1, a folder citation ending a question (resume run 5, eng-5)

Budget: projection 2 USD. Class C2. Keep your context short: read only what this change needs; cut long outputs to
head and tail.

You are a fresh engineer for ticket DAEO-kmcr (W2-23). You work only in `/home/usain/gov-os-worktrees/W2-23` on branch
`w2/W2-23` (DEC-963). The ticket's code is built and verified; review round 2 failed S3 on one finding, R2-1, and the
owner decided the fix (ticket, last section "P-W2-23-8 (the owner, DEC-1142 (2), 2026-11-12 ~09:50)", about line
142). You fix R2-1 in one function and nothing else.

## Step 0, before any work: the sandbox check (report it first in your return)

Do step 0 of `/home/usain/gov-os-worktrees/W2-23/.gov-runtime/scratch/brief/EMG-d4b-launched.md` with ticket id
`DAEO-kmcr`: (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-kmcr','w').write('x')"` must FAIL;
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the file
or (b) failed, stop there and return (delete nothing). Then read that file (its Engineer paragraph applies) and
`EMG-common.md` beside it.

## Standing rules

- First `printenv GOV_ROLE GOV_TICKET` (expect `engineer`, `DAEO-kmcr`) and
  `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-23`, `w2/W2-23`).
- The ticket: `/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-kmcr.md` (Interface item 6; the last section,
  P-W2-23-8). There is no context packet this run (`gov context` refused it: CONTEXT_OVER_CEILING); read those parts.
- **Writes:** only `src/gov/adopt/safety.py` and `tests/unit/adopt/test_safety.py`, and scratch under your `TMPDIR`.
  Never `git add -A`. **Never read `tests/acceptance/W2-23/**`** (DEC-820, DEC-1063); the test designer's new S3
  case is merged into this branch and you run it, but you do not open it.
- **Every pytest goes through the heavy slot**, with a `TMPDIR` outside the repository and outside `~/gov-os-runs`
  (your sandbox `TMPDIR` is fine; never one under `/home/usain/gov-os-worktrees/` or `/home/usain/gov-os-runs/`),
  `PYTHONUSERBASE=/home/usain/.local`, `-p no:cacheprovider -o tmp_path_retention_policy=failed` (the command below).
- Every run: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-23/src`. Quote
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-23/src python3 -c "import gov; print(gov.__file__)"`.
- No `gov retrieve` or `gov context`; search with Read and Grep, and search again once in other words if the first
  search does not answer (DEC-1065). Command forms: no `$(…)` or variable as a write target, no here-document, no
  `bash -c`; scripts as files under your sandbox `TMPDIR`. Foreground only. No reset, checkout, clean, amend, rebase,
  push, merge or install.
- Refused twice for the same call: stop and say so; never reach the same effect by another command, form or file
  (DEC-1142 (9)). On an authentication error return `AUTH_REQUIRED`.

## The change: `safety.citations` (`src/gov/adopt/safety.py`, about lines 239-345)

**R2-1 — a folder citation that ends a question is missed.** Reproduced at the head:
`citations('Did you search legacy/memory?', ['legacy/memory/index.md', 'legacy/memory/decisions/leg-001.md'], [])`
-> `[]`; `'Is it still in legacy/memory/?'` -> `[]`; `'Should we keep notes/memory?'` with the nested store
`['notes/memory/2025/q1/a.md', 'notes/memory/2026/b.md']` -> `[]`; the same texts ending in `.` or `!` are found.
Cause: `?` is in the folder form's blocking set as a glob character (`_NOT_MORE_PATH_DIR`, ~line 281), and the glob
reading of the token (`_GLOB_TOKEN`, ~line 240, and the loop ~lines 324-333) matches no store file.

The behaviour wanted (about 3 lines):
- A `?` (or a run of `?` and `.`) that **ends** a folder citation — followed by whitespace, end of text, a closing
  quote or bracket, or other sentence punctuation — is a sentence's stop: no part of the path and no bar to the folder
  match, as the full stop already is. `found` holds the citation without the stop.
- A `?` followed by more path characters still blocks the folder form and stays a glob character
  (`legacy/memory?x`, `legacy/memory/?.md`); every glob form found today stays found, including a glob whose `?`
  sits inside the token (`legacy/memory/decisions/leg-00?.md` -> the store file `legacy/memory/decisions/leg-001.md`).
- In the glob token handling, a trailing `?` that may be either a glob character or a question's stop: read it both
  ways, and the token cites the store if either reading does (a citation found in doubt holds a retirement back; one
  missed lets A8 retire a store still cited, the failure R2-1 names).
- Do not touch the other forms or any other function. Update the docstring's sentence on the stop ("A full stop that
  ends a folder or a tail is not part of it") to name the `?`.

## Unit tests (`tests/unit/adopt/test_safety.py`, beside the existing `test_s3_*` cases)

Add cases for: the three R2-1 texts found as `folder` with `found` without the `?` (`legacy/memory`, `legacy/memory/`,
`notes/memory`); `legacy/memory??` and `legacy/memory?)` found; `legacy/memory?x` and `legacy/memory/?.md` not found as
`folder`; the glob `legacy/memory/decisions/leg-00?.md` still found as `glob` (with the store above); a glob ending in a question's stop
(`Is it legacy/memory/*.md?`) found. Every existing case stays as it is and passes. No test name containing `real`,
`green_here` or `time_limit`.

## Check and commit

1. Run through the heavy slot (one line; `<your TMPDIR>` is your sandbox `TMPDIR`):

       env TMPDIR=<your TMPDIR> HOME=/home/usain/gov-os-worktrees/W2-23/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-23/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/unit/adopt tests/unit/adapters tests/acceptance/W2-23 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"

   All pass; quote the last line.
2. Commit only your paths:

       git commit -m "W2-23 (DAEO-kmcr): A8 citations: a folder citation ending a question is found; a trailing ? in a glob read both ways (R2-1; P-W2-23-8 (a))" --trailer "Task: DAEO-kmcr" --trailer "Role: engineer" --trailer "Implements: DEC-729, DEC-1052, DEC-954, DEC-315, DEC-1112" --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" -- src/gov/adopt/safety.py tests/unit/adopt/test_safety.py

   Then quote `git log --oneline -2` and `git status --short`.

## Return

One message, your last. **The twelve fields first, each a labelled line** ("none" where nothing):

```
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
```

`status` is DONE, PACKAGES, ESCALATION, ESCALATION_BLOCKED, LAUNCH_BLOCKED or AUTH_REQUIRED, with one line of why. In
`evidence`: the sandbox check, the `gov.__file__` line, the run's last line, the commit hash with its trailers. Also
the refusals met.
