# Brief: engineer, DAEO-61vm (W2-170), FULL — the fix pass of review round 2 (Interface reading 9)

Budget: projection 6 USD.

You are a fresh engineer for ticket DAEO-61vm (W2-170), profile FULL, class C2. You work only in the worktree
`/home/usain/gov-os-worktrees/W2-170` on branch `w2/W2-170` (DEC-963). The package `src/gov/memaudit/` is built and
was green on its first acceptance batch; review round 1 found one blocking finding. This is **the one fix pass** of
this round (DEC-1133 (4), DEC-1131): fix what is below, nothing else.

## Step 0, before any work: the sandbox check (report it first in your return)

Do step 0 of `/home/usain/gov-os-worktrees/W2-170/.gov-runtime/scratch/brief/EMG-d4b-launched.md` with ticket id
`DAEO-61vm`: (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-61vm','w').write('x')"` must FAIL;
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the file or
(b) failed, stop there and return (delete nothing). Then read that file whole (its Engineer paragraph applies) and
`EMG-common.md` beside it.

## Standing rules

- First run `printenv GOV_ROLE GOV_TICKET` (expect `engineer`, `DAEO-61vm`) and
  `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-170`, `w2/W2-170`).
  If anything differs, stop and say so.
- **Writes (F5):** only `src/gov/memaudit/**`, `tests/unit/memaudit/**`, `docs/changes/W2-170-evidence.md`, and your
  scratch `/home/usain/gov-os-worktrees/W2-170/.gov-runtime/scratch/eng/`. Nothing else; never `git add -A`.
- **You never read this ticket's acceptance tests** (`tests/acceptance/W2-170/**`, including its README; DEC-820,
  DEC-1063): build to the Interface and the behaviour below. You may run them and read their failure output.
- **Code under test (DEC-732):** `PYTHONPATH=/home/usain/gov-os-worktrees/W2-170/src` per command. Quote
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-170/src python3 -c "import gov; print(gov.__file__)"`.
- **Searching (DEC-1065):** no `gov retrieve` and no `gov context` in the sandbox; the Read and Grep tools, naming the
  folder a search starts at; search again once in different words, then answer from what you read or say "not found".
  Grep the decision register only by id.
- **Policy 2 (DEC-820):** never open the actual `~/gov-os-eval`, `~/gov-os-runs` or any run folder (F3).
- **Command forms:** no shell variable or `$(…)` as a write target, no here-document, no `bash -c '…'`, no long inline
  `python3 -c`; anything longer than one line goes in a script file under
  `/home/usain/gov-os-worktrees/W2-170/.gov-runtime/scratch/eng/` written with the Write tool, then run. Foreground
  only. No checkout of another commit, reset, clean, amend, rebase, push, merge or install.
- **Refused twice for the same call: stop and say so; never work around a refusal** (no second form of a refused
  call). List refusals in your return.
- Budget (DEC-898): `TMPDIR=/tmp/gov-os-lead-W2-170` (or the sandbox's own TMPDIR if that one is not writable, as
  `EMG-d4b-launched.md` says); `-o tmp_path_retention_policy=failed`, never `--basetemp`. `du -sh` of your scratch at the end.
- Under `.gov-runtime/`, commit hashes as 12 digits (DEC-911). On an authentication error return `AUTH_REQUIRED`.

## The finding (review round 1, RV1), as a described behaviour (DEC-136)

A set is pre-flighted clean (`PREFLIGHT.json` ok). Afterwards the files in `hidden/` are replaced, as the writer's
round 2 does after the checker's round 1 (some now with the wrong commit, a missing source, a source under an evaluation
namespace). The round-2 notes accept them; `void` exits 0; `declare` exits 0 and writes `USED` for a set whose current
files were never pre-flighted. That fails open: the set is measured once and cannot be re-run.

## The fix, as decided (ticket Interface section 10, reading 9; read it in the ticket)

> The pre-flighted set is the set declared: `PREFLIGHT.json` records each delivered file's sha256 by id; `DC-PREFLIGHT`
> also refuses when a kept file is not byte-equal to a pre-flighted one (a set whose writer round 2 replaced `hidden/`
> after the pre-flight is never marked `USED` until it is pre-flighted again). Sections 3 and 5 read with this line.

Behaviour, stated by the lead (not test code):
- `preflight` writes into `PREFLIGHT.json`, on every run (ok or refused), one JSON object mapping **each delivered
  file's id** (the stem `q<nn>` of every `q<nn>.yaml` directly in `hidden/`, including one PF-FORM refuses) to the
  **lowercase 64-hex sha256 of that file's bytes**, no prefix, under one key of your naming (for example
  `files_sha256`), and nothing else in that object. Digests and ids only (S5, F1).
- `declare`'s `DC-PREFLIGHT` refuses (exit 1, writing nothing, as section 5 states for every `DC-` code other than
  `DC-DECISION`: no map entry, no `DECLARATION.json`, no ledger line, no `USED`) when `PREFLIGHT.json` is absent, not
  ok, has no such record, or **any kept file** (`hidden/*.yaml`, flat, not `dropped/`) has an id absent from the record
  or a sha256 other than the recorded one. Dropped files are not compared. A byte change that would still pass every
  check (a re-worded question, an appended comment) is refused too: only bytes count.
- Re-running `preflight` on the replaced set (it records the new digests) lets `declare` go on, when nothing else refuses.
- The first batch's behaviour is unchanged: preflight, `void` with drops, `declare` exit 0 and `USED`, in the same order.

## What failed on today's code (the lead's run of the new cases; 10 failed, 4 passed)

```
FAILED test_w2_170_s1_s3_preflighted_set.py::test_s3_rv1_files_replaced_after_a_clean_preflight_are_refused_by_dc_preflight_writing_nothing
FAILED test_w2_170_s1_s3_preflighted_set.py::test_s3_a_kept_file_rewritten_but_still_valid_is_refused_by_dc_preflight[comment-appended|keyword-marked|reworded-question]
FAILED test_w2_170_s1_s3_preflighted_set.py::test_s3_a_kept_file_whose_id_was_never_preflighted_is_refused_by_dc_preflight
FAILED test_w2_170_s1_s3_preflighted_set.py::test_s3_f2_a_replaced_set_preflighted_again_is_declared_and_marked_used
FAILED test_w2_170_s1_s3_preflighted_set.py::test_s1_preflight_json_records_each_delivered_file_s_sha256_by_id[clean-39|clean-40|refused-pf-commit|refused-pf-count-35]
```
The `declare` cases: exit 0 with `DECLARED: …` and `USED written` where exit 1 and `DC-PREFLIGHT` are required. The
record cases: "PREFLIGHT.json does not record each delivered file's sha256 by id (reading 9)".

## What you read

1. The ticket `/home/usain/gov-os-worktrees/W2-170/.tickets/DAEO-61vm.md`: KPI lines S1, S3, S5, F2 and the Interface
   sections 3, 5 and 10 (reading 9). The Interface is fixed; a gap goes in your return as a package.
2. The code you change: `src/gov/memaudit/preflight.py`, `declare.py`, `layout.py`, `common.py`, and your unit tests
   `tests/unit/memaudit/test_preflight.py`, `test_declare.py`.
3. New sources by id in `docs/DECISION_REGISTER.md`: DEC-1129, DEC-1010, DEC-1131, DEC-1133.

## Check and commit

1. Add unit tests for the behaviour above in `tests/unit/memaudit/` (no name containing `real`, `green_here` or
   `time_limit`), then run:
   `env HOME=/home/usain/gov-os-worktrees/W2-170/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-170/src TMPDIR=/tmp/gov-os-lead-W2-170 python3 -m pytest tests/unit/memaudit -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
2. Then the acceptance suite the same way on `tests/acceptance/W2-170` and read only its failure output: all 179 must
   pass. Quote the last line. A failure that seems to ask for something the Interface does not say: do not guess, name
   it as a package.
3. Update `docs/changes/W2-170-evidence.md`: the S1 and S3 rows (and F2) name reading 9 and the new evidence.
4. Commit only your paths:

       git commit -m "<subject>" --trailer "Task: DAEO-61vm" --trailer "Role: engineer" --trailer "Implements: DEC-1101, DEC-1125, DEC-1098, DEC-1097, DEC-1069, DEC-820, DEC-896, DEC-1050, DEC-1073, DEC-1052, DEC-1129, DEC-1010, DEC-1131, DEC-1133" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- <your paths>

   (`git add` a new file first: `git commit -- <path>` does not take an untracked file.) Then quote
   `git log --oneline -3`, `git status --short` and `git diff --name-only c0202ce81 HEAD` (only your allowed paths).
5. Before you return: `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` shows nothing of yours.

## Return

One message, your last, complete in itself. **The twelve fields first, each a labelled line** ("none" where nothing):

```
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
```

`status` is DONE, PACKAGES, ESCALATION, ESCALATION_BLOCKED, LAUNCH_BLOCKED or AUTH_REQUIRED, with one line of why. In
`evidence`: the sandbox and `ps` checks, the `gov.__file__` line, the unit and acceptance last lines, each commit hash
with its trailers, `du -sh` of your scratch. Also the refusals met (time, form, reason) and every Interface gap found.
