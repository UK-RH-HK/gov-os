# Brief: independent test designer, DAEO-61vm (W2-170), FULL — the second test batch: Interface reading 9 (run 2)

Budget: projection 8 USD.

You are a fresh independent test designer (MR-3). Ticket: DAEO-61vm (W2-170), profile FULL, class C2. You work only in
the worktree `/home/usain/gov-os-worktrees/W2-170-tests` on branch `w2/W2-170-tests` (DEC-963). You never read or write
the ticket's own worktree, `/home/usain/gov-os-worktrees/W2-170`.

This is a **fix round** after review round 1. The first batch of acceptance tests (`tests/acceptance/W2-170/`, run 1,
yours to extend) and the implementation are both merged. The review found RV1, stated here as a described behaviour
(DEC-136): *a set is pre-flighted clean; afterwards the files in `hidden/` are replaced (as the writer's round 2 does
after the checker's round 1); the checker's round-2 notes accept them; `void` exits 0; `declare` then exits 0 and writes
`USED` for a set whose current files were never pre-flighted.* The CTO decided the fix (a delegated stricter-only
decision) and wrote it into the ticket as Interface section 10, **reading 9**:

> The pre-flighted set is the set declared: `PREFLIGHT.json` records each delivered file's sha256 by id; `DC-PREFLIGHT`
> also refuses when a kept file is not byte-equal to a pre-flighted one (a set whose writer round 2 replaced `hidden/`
> after the pre-flight is never marked `USED` until it is pre-flighted again). Sections 3 and 5 read with this line.

Your job: the acceptance cases for reading 9, red on today's code for the right reason, with every first-batch case
still as it was.

## Step 0, before any work: the sandbox check (report it first in your return)

Do step 0 of `/home/usain/gov-os-worktrees/W2-170-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md` with ticket id
`DAEO-61vm`: (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-61vm','w').write('x')"` must FAIL;
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the file or
(b) failed, stop there and return (delete nothing). Then read `EMG-common.md` beside it.

## Standing rules

- First run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer`, `DAEO-61vm`) and
  `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-170-tests`,
  `w2/W2-170-tests`). If anything differs, stop and say so.
- **Writes:** only `tests/acceptance/W2-170/**` (and your scratch `.gov-runtime/scratch/td/`). Nothing else.
- **Do not read the implementation** (Policy 2, DEC-820: the counterpart's work on the same ticket): never open
  `src/gov/memaudit/**` or `tests/unit/memaudit/**`, and do not search inside them. You test through the child process
  `python3 -m gov.memaudit ...` and the printed lines, exit codes and files that the Interface names.
- **Code under test (DEC-732):** every test run uses this worktree's own `src/`:
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-170-tests/src`, set per command (the first batch's support module already
  does this for child processes; keep it). Quote in your return
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-170-tests/src python3 -c "import gov; print(gov.__file__)"`.
- **Searching (DEC-1065):** no `gov retrieve` and no `gov context` in the sandbox. Use the Read and Grep tools, naming
  the folder a search starts at; if a search does not answer, search again once in different words, then answer from
  what you read or say "not found". Grep the decision register only by id.
- **Never open the actual `~/gov-os-eval`, `~/gov-os-runs` or any run folder**, by hand or from a test (F3). Everything is
  planted under pytest's `tmp_path` with the first batch's `w2_170_world.py`.
- **Command forms:** no shell variable or `$(…)` as a write target, no here-document, no `bash -c '…'`, no long inline
  `python3 -c`; anything longer than one line goes in a script file under
  `/home/usain/gov-os-worktrees/W2-170-tests/.gov-runtime/scratch/td/` written with the Write tool, then run.
  Foreground only. No checkout of another commit, reset, clean, amend, rebase, push, merge or install.
- **Refused twice for the same call: stop and say so; never work around a refusal.** Count refusals in your return.
- Budget (DEC-898): `TMPDIR=/tmp/gov-os-lead-W2-170` on every run; `-o tmp_path_retention_policy=failed`, never
  `--basetemp`. Give `du -sh` of your scratch at the end.
- Under `.gov-runtime/`, commit hashes as 12 digits, never 40 (DEC-911). On an authentication error return `AUTH_REQUIRED`.

## What you read (in this order)

1. **The ticket, authoritative:** `/home/usain/gov-os-worktrees/W2-170-tests/.tickets/DAEO-61vm.md`: the KPI lines
   S1 and S3 and F2, and the `## Interface`, above all section 3 (what `PREFLIGHT.json` holds), section 5 (`declare`'s
   refusals, `DC-PREFLIGHT`, "writing nothing", the order of the five writes) and section 10 reading 9. The Interface is
   fixed: a gap or clash goes in your return as a package; write the test to the words where they are clear.
2. The context packet `/home/usain/gov-os-worktrees/W2-170-tests/.gov-runtime/scratch/brief/context-td.json`, and the
   new sources by id in `docs/DECISION_REGISTER.md`: DEC-1129, DEC-1010, DEC-1131, DEC-1133 (with DEC-136 for "a finding
   becomes a described behaviour").
3. Your first batch: `tests/acceptance/W2-170/README.md`, `w2_170_world.py`, `conftest.py`,
   `test_w2_170_s1_preflight.py`, `test_w2_170_s3_declare.py` (the S3 flow: preflight, void with drops, declare).
4. The writer brief's round 2 (`governance/project/indep-briefs/memory-audit/writer.md`) and the package's section 3.3
   (`governance/project/orchestration/packages/MEMORY-AUDIT-1.md`): what a round-2 delivery changes in `hidden/`.

## What you write

New cases in `tests/acceptance/W2-170/` (a new file `test_w2_170_s1_s3_preflighted_set.py` or added to the S1/S3
files, your choice), the README's KPI map and expected-red table updated. At least:

1. **RV1 as described:** a clean set is pre-flighted (exit 0); then, as round 2 would, some files in `hidden/` are
   rewritten so that pre-flighting them would refuse (for example one gets the earlier commit, one a source missing at
   the commit); notes `XCHECK-r2.md` accept every question; `void` exits 0; `declare` exits 1 and prints `DC-PREFLIGHT`;
   then, per section 5's "writing nothing": no `USED`, no `DECLARATION.json`, no `declaration` or `used` ledger line, and
   the sets root's path map unchanged (no entry for the audit).
2. **Byte-equal, not "still valid":** a kept file rewritten after the pre-flight so that it would still pass every check
   (for example a re-worded `question`) is also refused by `DC-PREFLIGHT`, writing nothing.
3. **A kept file whose id was never pre-flighted** (pre-flight on fewer files, then a new `q<nn>.yaml` delivered) is
   refused by `DC-PREFLIGHT`.
4. **Pre-flighted again, it goes on:** after case 1's refusal, `preflight` re-run on the replaced set (now valid, or
   fixed back to valid) exits 0, and `declare` then exits 0 and writes `USED` ("never marked USED until it is
   pre-flighted again").
5. **`PREFLIGHT.json` records each delivered file's sha256 by id:** for every `q<nn>` delivered, the sha256 hex of that
   file's bytes appears in `PREFLIGHT.json` tied to that id. The Interface names no key, so find the mapping
   key-agnostically (a JSON object somewhere in the file whose keys are exactly the delivered ids and whose values are
   those digests, or a list of objects pairing them); state the reading in the README. Also on a refused pre-flight.
6. **The S3 flow stays green:** pre-flight, `void` with 3 drops (the dropped files are no longer kept, so they need not
   match), `declare` exit 0 with `USED`: confirm the first batch's S3/F2 cases still cover this and still pass; add one
   case only if none does.
7. **S5 / F1 still hold** for the new record: `PREFLIGHT.json` and the printed lines of these cases carry no question,
   gold answer, source path or heading (digests and ids only), by the first batch's unique-word method if it fits.

Name each new case in the README's KPI map under S1 or S3 (and F2 where it is about `USED`). **Naming (DEC-1065):** no
test, class, parametrize id or file name may contain `real`, `green_here` or `time_limit`.

## Check and commit

1. `env HOME=/home/usain/gov-os-worktrees/W2-170-tests/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-170-tests/src TMPDIR=/tmp/gov-os-lead-W2-170 python3 -m pytest tests/acceptance/W2-170 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
   (make the empty-home folder first). Expected on today's code: **the new cases 1, 2, 3 and 5 fail** (declare exits
   0 and writes `USED`; no digests by id), for that reason and no other; cases 4 and 6 may pass; **every first-batch case
   passes as before**. Quote the last line, the failing case names with a one-line reason each, and the
   `--collect-only -q` count with the same filters.
2. Check the README map with a script under `.gov-runtime/scratch/td/` calling `gov.accept.runner.parse_map`: every one
   of S1–S6 and F1–F5 maps to at least one case, and each new case is in the map; quote its output.
3. Commit only `tests/acceptance/W2-170/**`:

       git commit -m "W2-170 acceptance, batch 2: Interface reading 9, the pre-flighted set is the set declared (review round 1's RV1)" --trailer "Task: DAEO-61vm" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1101, DEC-1125, DEC-1098, DEC-1097, DEC-1069, DEC-820, DEC-896, DEC-1050, DEC-1073, DEC-1052, DEC-1129, DEC-1010, DEC-1131, DEC-1133" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- tests/acceptance/W2-170

   Then quote `git log --oneline -2` and `git status --short`.

## Return

One message, your last, complete in itself. **The twelve fields first, each a labelled line** ("none" where nothing):

```
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
```

`status` is DONE, PACKAGES, ESCALATION, ESCALATION_BLOCKED, LAUNCH_BLOCKED or AUTH_REQUIRED, with one line of why.
In `evidence`: the sandbox check's result, the `gov.__file__` line, the collect and run last lines, the map check's
output, the commit hash with its trailers, `du -sh` of your scratch. In `tests`: the new cases per KPI line and the
expected-red table in short. Also say the read refusals met (time, form, reason) and every Interface gap you found.
