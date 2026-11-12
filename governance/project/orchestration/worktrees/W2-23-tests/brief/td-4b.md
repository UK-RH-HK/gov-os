# Brief: independent test designer, DAEO-kmcr (W2-23), FULL — S3 round 2 cases (resume run 4, td-4b: relaunch of td-4, refused at the resource gate)

Budget: projection 2 USD. Class C2. Keep your context short: read only what these cases need.

You are a fresh independent test designer (MR-3) for ticket DAEO-kmcr (W2-23). You work only in
`/home/usain/gov-os-worktrees/W2-23-tests` on branch `w2/W2-23-tests` (DEC-963), which holds the acceptance tests
(`tests/acceptance/W2-23/`). You never read or write `/home/usain/gov-os-worktrees/W2-23` (the implementation), and
you never read `src/gov/adopt/` or `src/gov/adapters/`: write to the Interface's words and the behaviours below.

## Step 0, before any work: the sandbox check (report it first in your return)

Do step 0 of `/home/usain/gov-os-worktrees/W2-23-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md` with ticket id
`DAEO-kmcr`: (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-kmcr','w').write('x')"` must FAIL;
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the file
or (b) failed, stop there and return (delete nothing). Then read `EMG-common.md` beside it.

## Standing rules

- First `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer`, `DAEO-kmcr`) and
  `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-23-tests`,
  `w2/W2-23-tests`).
- The ticket: `/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-kmcr.md` (Interface item 6, and the last
  "Delegated ... run 3's P-W2-23-7 (a)" paragraph). The context packet (`gov context`, built by the lead):
  `/home/usain/gov-os-worktrees/W2-23-tests/.gov-runtime/scratch/brief/context-td.json`.
- **Writes:** only `tests/acceptance/W2-23/**`. Scripts, if any, as files under your sandbox `TMPDIR`.
- Every run: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-23-tests/src`. No `gov retrieve` or `gov context`; search with
  Read and Grep, and search again once in other words if the first search does not answer (DEC-1065). No `$(…)` or
  variable as a write target, no here-document, no `bash -c`. Foreground only. No reset, checkout, clean, amend,
  rebase, push, merge or install.
- Refused twice for the same call: stop and say so; never work around a refusal. On an authentication error return
  `AUTH_REQUIRED`.

## What to add (S3 only; the existing S3 cases stay exactly as they are)

S3: "The A8 dependency proof finds every listed citation form." Interface item 6 lists, among others, "a citation of
only the store's folder or a glob" and "`../` followed by only the tail of the path". The independent review found two
behaviours the current cases do not plant (the CTO's P-W2-23-7 (a)); add acceptance cases, in
`tests/acceptance/W2-23/test_w2_23_citations.py` (and helpers in `w2_23_support.py` as needed), that drive A8 the way
the existing cases do (`Adoption(...).through("A6", ...)` then `run("A8")`, and `proof_said` on the refusal):

1. **Sentence-final citations.** A citation that ends a sentence with a full stop is still a citation. Plant, each
   alone in a rule file of its own: (i) the store's folder followed by `.` (`... is legacy/memory.`); (ii) the store's
   folder with its slash followed by `.` (`... see legacy/memory/.`); (iii) a `../` tail followed by `.` — use the tail
   of a store file whose name is **not** a record id (e.g. `../memory/index.md.`), so no id match can stand in for the
   tail form. A8 must refuse `ADOPT_STORE_STILL_CITED` and print each of these files as found.
2. **A store whose files all sit in subfolders, cited by its folder.** "The store's folder" (the CTO's reading, ticket
   P-W2-23-7 (a)): the deepest folder holding all the store's files, and each folder between it and a file. Plant a
   store with no file directly in its folder and at least two levels of subfolders, e.g. `notes/memory/2025/q1/a.md`
   and `notes/memory/2026/b.md` (its folder is `notes/memory`), retired the same way the existing store is (find how
   `retire_store_proposal` and `store_files` name the store, and make a variant for this one). Each alone in a rule
   file of its own, and each must be printed as found: (i) the store's own folder (`notes/memory/`), (ii) the same
   without the slash, mid-sentence (`notes/memory and ...`), (iii) a folder between it and a file
   (`notes/memory/2025/`). Keep a control that a rule citing nothing of the store is not printed.
   If the existing support cannot retire a second store without changes to what the old cases plant, add new helpers
   rather than change the old ones.

Name each case `test_s3_...` (no `real`, `green_here` or `time_limit` in a name), with a docstring citing P-W2-23-7 (a)
and the behaviour. Update the README's S3 row to name the new cases.

## Check and commit

1. `env HOME=/home/usain/gov-os-worktrees/W2-23-tests/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-23-tests/src python3 -m pytest tests/acceptance/W2-23 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
   on this branch. It holds the implementation before the fix, so the new cases are expected **red** on the
   sentence-final folder and tail and on the nested-store folder citations (the review reproduced
   `citations('The old store is legacy/memory.', [...], []) -> []`); every old case stays green. Say plainly which
   new case is red and why (one line each), and quote the last line. A new case that is green here shows nothing for
   R1/R2; say so if one is.
2. Commit only your paths:

       git commit -m "W2-23 acceptance: S3 sentence-final folder and tail citations; a nested store cited by its folder (P-W2-23-7 (a))" --trailer "Task: DAEO-kmcr" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-729, DEC-1052, DEC-954, DEC-315, DEC-1112" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- tests/acceptance/W2-23

   Then quote `git log --oneline -2` and `git status --short`.

## Return

One message, your last. **The twelve fields first, each a labelled line** ("none" where nothing):

```
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
```

`status` is DONE, PACKAGES, ESCALATION, ESCALATION_BLOCKED, LAUNCH_BLOCKED or AUTH_REQUIRED, with one line of why. In
`evidence`: the sandbox check, the run's last line, the commit hash with its trailers. Also the refusals met.
