# Brief: engineer, DAEO-kmcr (W2-23), FULL — one acceptance red to fix (build run, eng-2)

Budget: projection 3 USD. Class C3. Keep your context short (the week's usage is near its brake, DEC-1126): read only
what this fix needs; cut long outputs to head and tail.

You are a fresh engineer for ticket DAEO-kmcr (W2-23). You work only in `/home/usain/gov-os-worktrees/W2-23` on branch
`w2/W2-23` (DEC-963). The ticket's code is built (commits 775a9df62, 1dc34d608, 11eb9dac4) and the independent
acceptance tests are merged (02a5401be). One acceptance case is red for a code reason; you fix that and nothing else.

## Step 0, before any work: the sandbox check (report it first in your return)

Do step 0 of `/home/usain/gov-os-worktrees/W2-23/.gov-runtime/scratch/brief/EMG-d4b-launched.md` with ticket id
`DAEO-kmcr`: (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-kmcr','w').write('x')"` must FAIL;
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the file
or (b) failed, stop there and return (delete nothing). Then read that file (its Engineer paragraph applies) and
`EMG-common.md` beside it.

## Standing rules

- First `printenv GOV_ROLE GOV_TICKET` (expect `engineer`, `DAEO-kmcr`) and
  `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-23`, `w2/W2-23`).
- **Writes:** only `src/gov/adopt/safety.py`, `tests/unit/adopt/**`, and scratch under your `TMPDIR`. Never
  `git add -A`. **Never read `tests/acceptance/W2-23/**`** (DEC-820, DEC-1063): build to the behaviour below.
- Every run: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-23/src`. Quote
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-23/src python3 -c "import gov; print(gov.__file__)"`.
- No `gov retrieve` or `gov context`; search with Read and Grep (DEC-1065). Command forms: no `$(…)` or variable as a
  write target, no here-document, no `bash -c`; scripts as files under your sandbox `TMPDIR` (the scratch folder may be
  refused for Write). Foreground only. No reset, checkout, clean, amend, rebase, push, merge or install.
- Refused twice for the same call: stop and say so; never work around a refusal. On an authentication error return
  `AUTH_REQUIRED`.

## The red (the failing output, and the behaviour it asks for)

The failing output is in `/home/usain/gov-os-worktrees/W2-23/.gov-runtime/scratch/brief/reds-1.txt` (read only the
`test_s3_…` part; the two `test_s1_…` failures there are a test defect the test designer is fixing, not yours). In
short: A8's dependency proof (`gov.adopt.safety.citations`) does not find the planted citation `glob
(.rulesync/rules/cite-glob.md)`. The behaviour, from the ticket's Interface item 6 ("a citation of only the store's folder
or a glob"): a rule's prose sentence reading **`The vote rules are in legacy/memory/**/*.md.`** cites the store
`legacy/memory/` (records such as `legacy/memory/decisions/leg-001.md`) by a glob, followed by the sentence's full
stop. It must be printed as found (form `glob`). The likely cause, for you to confirm: `_GLOB_TOKEN` takes the trailing
`.` into the token, so `_glob` wants `.md.`. A glob followed by `,`, `:`, `;`, `)` or a closing quote, or at a line end,
must be found too; a glob with no literal first folder (`**/*`, `*.md`) stays not a citation; no form outside item 6's
list becomes found.

## Check and commit

1. A unit case for the sentence above (and one with a trailing comma) in `tests/unit/adopt/test_safety.py`; then
   `env HOME=/home/usain/gov-os-worktrees/W2-23/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-23/src python3 -m pytest tests/unit/adopt tests/unit/adapters -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
   (no test name of yours may contain `real`, `green_here` or `time_limit`): all pass; quote the last line.
2. `env HOME=/home/usain/gov-os-worktrees/W2-23/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-23/src python3 -m pytest tests/acceptance/W2-23/test_w2_23_citations.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed`
   (you run it; you read only its failure output, never the file): quote the last line.
3. Commit only your paths:

       git commit -m "W2-23 (DAEO-kmcr): A8 proof finds a glob citation followed by sentence punctuation (S3)" --trailer "Task: DAEO-kmcr" --trailer "Role: engineer" --trailer "Implements: DEC-729, DEC-1052, DEC-954, DEC-315, DEC-1112" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- src/gov/adopt/safety.py tests/unit/adopt/test_safety.py

   Then quote `git log --oneline -2` and `git status --short`.

## Return

One message, your last. **The twelve fields first, each a labelled line** ("none" where nothing):

```
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
```

`status` is DONE, PACKAGES, ESCALATION, ESCALATION_BLOCKED, LAUNCH_BLOCKED or AUTH_REQUIRED, with one line of why. In
`evidence`: the sandbox check, the `gov.__file__` line, the two last lines, the commit hash with its trailers. Also the
refusals met (time, form, reason).
