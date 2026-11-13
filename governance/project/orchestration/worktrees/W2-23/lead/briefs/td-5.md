# Brief: independent test designer, DAEO-kmcr (W2-23), FULL — one S3 case for R2-1 (resume run 5, td-5)

Budget: projection 2 USD. Class C2. Keep your context short: read only what this case needs.

You are a fresh independent test designer (MR-3) for ticket DAEO-kmcr (W2-23). You work only in
`/home/usain/gov-os-worktrees/W2-23-tests` on branch `w2/W2-23-tests` (DEC-963), which holds the acceptance tests
(`tests/acceptance/W2-23/`). You never read or write `/home/usain/gov-os-worktrees/W2-23` (the implementation), and
you never read `src/gov/adopt/` or `src/gov/adapters/`: write to the Interface's words and the behaviour below.

## Step 0, before any work: the sandbox check (report it first in your return)

Do step 0 of `/home/usain/gov-os-worktrees/W2-23-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md` with ticket id
`DAEO-kmcr`: (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-kmcr','w').write('x')"` must FAIL;
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the file
or (b) failed, stop there and return (delete nothing). Then read `EMG-common.md` beside it.

## Standing rules

- First `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer`, `DAEO-kmcr`) and
  `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-23-tests`,
  `w2/W2-23-tests`).
- The ticket: `/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-kmcr.md`: Interface item 6, and the last
  section, "P-W2-23-8 (the owner, DEC-1142 (2), 2026-11-12 ~09:50)" (about line 142). There is no context packet this
  run (`gov context` refused it: CONTEXT_OVER_CEILING, 8274 tokens over 6000); read those two parts of the ticket.
- **Writes:** only `tests/acceptance/W2-23/**`. Scripts, if any, as files under your sandbox `TMPDIR`.
- **Every pytest goes through the heavy slot**, with a `TMPDIR` outside the repository and outside `~/gov-os-runs`
  (your sandbox `TMPDIR` is fine; never one under `/home/usain/gov-os-worktrees/` or `/home/usain/gov-os-runs/`),
  `PYTHONUSERBASE=/home/usain/.local`, `-p no:cacheprovider -o tmp_path_retention_policy=failed` (the command below).
- `PYTHONPATH=/home/usain/gov-os-worktrees/W2-23-tests/src`. No `gov retrieve` or `gov context`; search with Read and
  Grep, and search again once in other words if the first search does not answer (DEC-1065). No `$(…)` or variable as
  a write target, no here-document, no `bash -c`. Foreground only. No reset, checkout, clean, amend, rebase, push,
  merge or install.
- Refused twice for the same call: stop and say so; never reach the same effect by another command, form or file
  (DEC-1142 (9)). On an authentication error return `AUTH_REQUIRED`.

## What to add (S3 only; every existing case stays exactly as it is)

S3: "The A8 dependency proof finds every listed citation form." Interface item 6 lists "a citation of only the store's
folder or a glob". Review round 2 (finding R2-1, reproduced by the lead) found that a folder citation that **ends a
question** is not found: `Did you search legacy/memory?`, `Is it still in legacy/memory/?`, and, for the nested store,
`Should we keep notes/memory?` each give no citer, while the same with `.` or `!` is found. The owner decided
P-W2-23-8 (a): one test case for it.

Add **one** test function in `tests/acceptance/W2-23/test_w2_23_citations.py`, e.g.
`test_s3_a_folder_citation_ending_a_question_is_found`, parametrized over the three forms (pytest ids such as
`flat-no-slash`, `flat-slash`, `nested-no-slash`):
1. the flat store (the one `retire_store_proposal` / `store_files` retire): a rule file holding only
   `... legacy/memory?` (the folder, no slash, then `?` and end of line);
2. the flat store: a rule file holding only `... legacy/memory/?`;
3. the nested store (`retire_nested_store_proposal` / `nested_store_files`, `NESTED_STORE`): a rule file holding only
   `... notes/memory?`.
Drive A8 as the existing round-2 cases do (see `_nested` and the sentence-final cases about lines 70-112:
`Adoption(...).through("A6", ...)` then `run("A8")`): A8 must refuse `ADOPT_STORE_STILL_CITED` and `proof_said` must
print the planted rule file as found. Reuse the existing helpers; add new helpers rather than change an old one.

A `?` is also a glob character, and a glob is a listed form. If no existing S3 case plants a glob whose `?` sits
inside the token (e.g. `legacy/memory/leg-00?.md`, matching a store file), add that as a fourth parameter (id
`glob-question-inside`) so the fix cannot drop the glob reading; if one exists, name it in your return and add nothing.

Docstring citing P-W2-23-8 (a) and R2-1. No `real`, `green_here` or `time_limit` in any name or id. Update the
README's S3 row to name the new case.

## Check and commit

1. Run the folder through the heavy slot (one line; `<your TMPDIR>` is your sandbox `TMPDIR`, outside the repository):

       env TMPDIR=<your TMPDIR> HOME=/home/usain/gov-os-worktrees/W2-23-tests/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-23-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-23 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"

   This branch holds the implementation before the fix, so the three `?`-ending parameters are expected **red**
   (no citer found); the glob control, if added, green; every old case green. Say plainly which parameter is red and
   why (one line each), and quote the last line. A `?`-ending parameter that is green here shows nothing for R2-1;
   say so if one is.
2. Commit only your paths:

       git commit -m "W2-23 acceptance: S3 a folder citation ending a question is found (R2-1; P-W2-23-8 (a))" --trailer "Task: DAEO-kmcr" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-729, DEC-1052, DEC-954, DEC-315, DEC-1112" --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" -- tests/acceptance/W2-23

   Then quote `git log --oneline -2` and `git status --short`.

## Return

One message, your last. **The twelve fields first, each a labelled line** ("none" where nothing):

```
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
```

`status` is DONE, PACKAGES, ESCALATION, ESCALATION_BLOCKED, LAUNCH_BLOCKED or AUTH_REQUIRED, with one line of why. In
`evidence`: the sandbox check, the run's last line, the commit hash with its trailers. Also the refusals met.
