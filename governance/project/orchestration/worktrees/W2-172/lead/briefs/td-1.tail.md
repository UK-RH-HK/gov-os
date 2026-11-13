

## Rules
- One test (or more) per KPI line S1-S9 and F1-F5, each doing what its Verify says, read with the Interface items the
  line names. Name each after its id (`test_s1_...`, `test_f3_...`). Cover each printed code a KPI line reaches: the
  `RN-` refusals of item 3 (`RN-LOCK`, `RN-NOBASE`, `RN-RECENT`, `RN-REBUILD`, `RN-SIDE`, `RN-STALE`, `RN-NAME`), the
  `BL-` refusals of item 10, `STEP <name> ...`, `STOPPED <step> <exit>`, `STOPPED <step> gate busy`, `REFUSED <code>`,
  the `due` lines and reason codes of item 9, `audited` / `not audited, next due <date>` of item 11, and the exit codes
  of item 12.
- Reach the code as its callers do: `python3 -m gov.memaudit run|due|baseline|status --sets-root <root> ...` and
  `bash memaudit_cron.sh` in a child process, judged by exit code, printed lines, and the files under
  `<runs>/indep/memaudit/` (item 4) and `<runs>/indep/AUDITS.log`. Every child gets this tree's `src/` first on
  `PYTHONPATH` (fail the run if it would import `gov` from elsewhere, as W2-170's and W2-171's suites do). Never import
  the ticket's new modules at collection, so the suite runs red by failing, not by erroring at import.
- **The seams the Interface names, and only those:** `--launch <file>` (a planted stub launch script: it logs its argv,
  answers per step and per attempt with a planted exit code and a planted counts line as stdout's last line, e.g.
  `out.revise`/`out.rejected` for `checker-1`; a writer delivers a planted set into the planted sets root as the real
  script would; an auditor delivers a planted `classes.json` and appends the `AUDITS.log` line in the real script's form);
  `--store-link`, `--repo`, `--gov`, `--claude`, `--gate-cmd`; the environment `GOV_INDEP_RUNS_DIR`, `GOV_MEMAUDIT_NOW`,
  `GOV_MEMAUDIT_GATE_POLL_S`, `GOV_MEMAUDIT_GATE_MAX_S`, `GOV_MEMAUDIT_PYTHON`, `GOV_MEMAUDIT_SETS_ROOT`,
  `GOV_MEMAUDIT_GATE`. W2-170's and W2-171's subcommands run for real (`<py> -m gov.memaudit preflight|void|measure|
  judge|classes|pool`), fed by the fake `gov` and fake `claude` as W2-171's world feeds them; plan faults the way
  W2-171's world does (e.g. two degraded attempts give `measure` exit 2 after USED). Running the real launch script with
  W2-149's stub `claude` is optional (one case at most, only if a planted walls template and approved list are cheap to
  plant from W2-149's/W2-173's support); if you do not, say so in `unresolved`.
- **Path hygiene for S1/F1 (the substring grep must mean something):** every path that can appear on a printed command
  line (the sets root, the repository, the store link, the launch stub, the fake `gov` and `claude`, the interpreter)
  must itself contain none of `fixtures/`, `runs/` or `indep-walls/`. pytest's `tmp_path` takes the test's name, so
  keep those words out of test names and folder names, and name the planted runs folder something without `runs/` too
  (it is passed in the environment only). Assert that precondition in the test before the grep.
- S1: a set with revisions (checker-1's counts `out.revise + out.rejected > 0`): the `STEP` lines are exactly writer-1,
  preflight, checker-1, writer-2, checker-2, void, measure, judge, auditor, classes, pool, figures; a clean set: the same
  without writer-2 and checker-2; the auditor runs with an empty misses file. Each launch line: only `--sets-root
  <root>`, the brief path under `governance/project/indep-briefs/memory-audit/`, `--brief-sha256` equal to the sha256 of
  `git show <C>:<brief>` in the planted repository (plant briefs whose bytes differ from the working tree's at a later
  commit to show `git show <C>` is what is hashed), `--commit <C>`, `--set <A>`, `--round`/`--audit` as item 2.
- S2: store link HEAD fresh and an ancestor of `w2/integrate` (starts); committer time 30 h before `GOV_MEMAUDIT_NOW`
  (`RN-STALE`); on a side branch (`RN-SIDE`); `<store-link>.lock` held by the test with a `flock` (`RN-REBUILD`); each
  refusal: exit 1, no child started (the stub's log empty), the counts say why. The audit name `memory-audit-<yyyymmdd>`
  from `GOV_MEMAUDIT_NOW`'s UTC date names the audit folder and `--set`.
- S3: launch exits 10, 20, 21, 22 at a launch step (stop, one call each, `STOPPED <step> <code>`, exit 2, COUNTS'
  `stop`); 16 then 0 (goes on, `retried` true); 16 twice (stop after exactly two calls); a stop before USED leaves the set
  unmeasured (no `measure` STEP, nothing in `HISTORY.jsonl`), and the next audit, a day later by the clock seam with
  `--force` as needed, starts a new set name; a fault after USED (`measure` exit 2): the digest's `OWNER` line,
  `HISTORY.jsonl` gains `measured: false, used: true`, and a later `run` never runs `measure` for that set.
- S4: a second `run` while the test holds `<R>/LOCK` (`RN-LOCK`); `STARTS.log` last line 3 days before now
  (`RN-RECENT`); the same with `--force` starts, and `COUNTS.json`'s `force` is true and the digest says so.
- S5: planted histories (`HISTORY.jsonl`, `STARTS.log`, git histories with committer dates) with `GOV_MEMAUDIT_NOW`:
  churn 40 % (weekly); three measured lines under 5 % with the rest met (monthly, `stable`); then each of the four
  triggers alone at H (`churn` >= 10 %, a retrieval-glob change since the last audit commit, last `passes` false, last
  `pool_regression` true: weekly with that reason); `due` at 5 and 6 days in weekly (exit 1 then 0), 27 and 28 in
  monthly; the churn's denominator less the planted `tree-exclude.txt` matches (show an excluded path changing does not
  count). Check the three printed lines exactly.
- S6: `baseline` on an empty log (appends one line in the launch script's form, `BASELINE <12 hex>`); a second baseline
  (`BL-EXISTS`, log unchanged); a commit not in the repository (`BL-COMMIT`, nothing written); `run` with no log line
  (`RN-NOBASE`).
- S7/F2: one planted end-to-end audit: `DIGEST.txt` has exactly the 12 lines of item 7 in that order, each matching your
  own regular expression written from the item, and standard output holds the same 12 lines; plant a unique word in a
  question, a gold path and an answer, then grep `DIGEST.txt`, the driver's standard output and standard error, and every
  file under `<runs>/indep/memaudit/` (item 4 says everything there is counts, codes, ids, hashes and repository paths):
  0 hits each. A stop's digest too (the `not reached` words, `STOP` line).
- S8: planted audits and retrieval-glob commits: a retrieval change before a measured audit's commit (`audited`, exit
  0), after it (`not audited, next due <date>`, exit 1), none since `<since>` (`audited`).
- S9: the wrapper with `GOV_MEMAUDIT_PYTHON` pointing at a planted interpreter shim that answers `-m gov.memaudit due`
  with planted output and exit and logs any `run` call: not due (no `run` call, exit 0, one `cron.log` line); due (one
  `run` call with `--sets-root` and `--gate-cmd`, the wrapper exits with run's code, one `cron.log` line). Gate busy: the
  real `run` with an always-busy `--gate-cmd` stub, a small `GOV_MEMAUDIT_GATE_MAX_S` and `GOV_MEMAUDIT_GATE_POLL_S`:
  `STOPPED measure gate busy`, exit 2, no `measure` child started; leave `GOV_MEMAUDIT_NOW` unset in that case (plant the
  store commit at the real now) so the wait can run out whether the engineer measures it by the seam or the real clock;
  the wrapper does not override the 3600 default. `grep -c crontab` of the wrapper is 0.
- F1: S1's run under a file-access spy over the driver's own process (e.g. a `sitecustomize.py` on a planted
  `PYTHONPATH` entry that adds a `sys.addaudithook` logging `open`, `os.listdir`, `os.scandir` with the pid; keep only the
  driver's pid): no path under the sets root opened by the driver itself.
- F3: covered by S4's refusals and S3's stop-before-USED case; name them in the README.
- F4: the planted repository holds a path map, a guard file, `.claude/settings.json` and a walls template; `git status
  --porcelain` there after a full run is empty for them; the wrapper's `grep -c crontab` is 0.
- F5: `git diff --name-only <merge-base with w2/integrate>...HEAD` lists only the ticket's allowed_paths plus
  `tests/acceptance/W2-172/`; it judges only branch `w2/W2-172` and skips elsewhere (DECIDED-NOT-DONE row 171); say so in
  its docstring.
- Tests are red now (no `run`/`due`/`baseline`/`status` subcommands, no wrapper). Run them and say which are red and
  why; anything green now is a fault in the test unless it guards "nothing else happens".
- Keep the suite fast (seconds per case, the whole folder in a few minutes): fake commands only; the end-to-end world
  built once per module where cases do not write to it. No test named with `real`, `green_here` or `time_limit` unless
  it must be skipped by that filter. Bounded polls, never a bare sleep.
- **Every pytest through the heavy-slot gate**, one folder per run, TMPDIR outside the repository and outside
  ~/gov-os-runs:
  `TMPDIR=/tmp/gov-w2-172-td bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env HOME=/home/usain/gov-os-worktrees/W2-172-tests/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-172-tests/src python3 -m pytest tests/acceptance/W2-172 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
  (make the TMPDIR and the empty HOME folders first with `mkdir -p`). A heavy-slot or resource refusal is a wait: run
  again when it opens.
- Add `tests/acceptance/W2-172/README.md` as W2-171's: how the tests reach the code, what is planted, each KPI's cases.
- Anything longer than one line goes in a script under /home/usain/gov-os-worktrees/W2-172-tests/.gov-runtime/scratch/.
  Literal paths only as write targets.
- Commit your paths only:
  `git commit -m "<subject>" --trailer "Task: DAEO-p8tv" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1101, DEC-1125, DEC-1097, DEC-1038, DEC-1050, DEC-1073" -- tests/acceptance/W2-172`
- Refused twice for the same call by the guard, the sandbox or a hook: stop and say so; never reach the same effect by
  another command, form or file (DEC-1142 (9)).

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed / files_changed / evidence (the pytest summary line, red and green counts per KPI) / tests /
discoveries / risks / lessons / proposed_decisions / unresolved / recommended_next_action. Then `commits:` (hash12,
subject, trailers) and `guard_refusals:` (none, or each: time | form | the hook's reason | true or false-positive).
