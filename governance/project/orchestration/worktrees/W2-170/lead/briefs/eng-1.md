# Brief: engineer, DAEO-61vm (W2-170), FULL — the memory audit's set record (build run 1)

Budget: projection 25 USD.

You are the engineer for ticket DAEO-61vm (W2-170), profile FULL, class C2. You work only in the worktree
`/home/usain/gov-os-worktrees/W2-170` on branch `w2/W2-170` (DEC-963). The lead (an orchestrator session) merged
`w2/integrate` into it (`49c776675`), so the ticket file carries its Interface section 10 readings 1 to 8, and the
independent test designer's acceptance tests are already merged (`79a8fb87f`) and red.

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
- **Writes (F5):** only `src/gov/memaudit/**`, `tests/unit/memaudit/**`, `governance/project/test-map.yaml`,
  `docs/changes/W2-170-evidence.md`, and your scratch `/home/usain/gov-os-worktrees/W2-170/.gov-runtime/scratch/eng/`.
  Nothing else; never `git add -A`.
- **You never read this ticket's acceptance tests** (`tests/acceptance/W2-170/**`, DEC-820, DEC-1063): build to the
  KPI lines and the ticket's `## Interface`, never to the tests. You may run them (below) and read their failure output.
- **Code under test (DEC-732):** every run uses this worktree's `src/`: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-170/src`,
  per command. Quote `PYTHONPATH=/home/usain/gov-os-worktrees/W2-170/src python3 -c "import gov; print(gov.__file__)"`.
- **Searching (DEC-1065):** no `gov retrieve` and no `gov context` in the sandbox. Use the Read and Grep tools, naming
  the folder a search starts at; if a search does not answer, search again once in different words, then answer from
  what you read or say "not found". Grep the decision register (`docs/DECISION_REGISTER.md`, 1.6 MB) only by id.
- **Policy 2 (DEC-820):** never open the real `~/gov-os-eval`, `~/gov-os-runs` or any run folder, by hand or from a
  test (F3). Your unit tests plant everything under pytest's `tmp_path` and set `HOME` for child processes to a planted
  empty folder.
- **Command forms:** no shell variable or `$(…)` as a write target, no here-document, no `bash -c '…'`, no long inline
  `python3 -c`; anything longer than one line goes in a script file under
  `/home/usain/gov-os-worktrees/W2-170/.gov-runtime/scratch/eng/` written with the Write tool, then run. Foreground
  only. No checkout of another commit, reset, clean, amend, rebase, push, merge or install.
- **Refused twice for the same call: stop and say so; never work around a refusal.** List refusals in your return.
- Budget (DEC-898): `TMPDIR=/tmp/gov-os-lead-W2-170` on every run (make it first); pytest's
  `-o tmp_path_retention_policy=failed`, never `--basetemp`. Give `du -sh` of your scratch at the end.
- Under `.gov-runtime/`, commit hashes as 12 digits, never 40 (DEC-911). On an authentication error return `AUTH_REQUIRED`.

## What you read (in this order)

1. **The ticket, authoritative:** `/home/usain/gov-os-worktrees/W2-170/.tickets/DAEO-61vm.md`: its KPI lines (S1-S6,
   F1-F5, each with its `Verify:` clause) and its `## Interface`, sections 1 to 10. **The Interface is fixed:** you
   conform to it exactly (module and function names of section 8, flags, layout, codes, exit codes, printed lines,
   JSON keys, ledger events, the order of writes). Section 10's eight readings are decided, in particular:
   `say(line, sets_root)` returns the exit word and counts like section 8's others; a file `PF-FORM` refuses counts in
   `n` (PF-COUNT) only, not in the quotas or the spread; a path map unreadable at the commit gives `ERROR: <class>`
   and exit 4, never a PF- code; `DC-DECISION` writes no map entry (the map entry follows only an `ok: true`
   declaration). A gap or clash you find in the Interface goes into your return as a package (question, options with
   cost, recommendation, confidence, what it blocks); build to its clear words and name the unclear point.
2. **The context packet:** `/home/usain/gov-os-worktrees/W2-170/.gov-runtime/scratch/lead/briefs/context-eng.txt`
   (the ticket, its ten source decisions, supplementary chunks). Read each source decision by id in the register:
   DEC-1101, DEC-1125, DEC-1098, DEC-1097, DEC-1069, DEC-820, DEC-896, DEC-1050, DEC-1073, DEC-1052.
3. **What this generalises:** the fresh 80's tools, copied for you to
   `/home/usain/gov-os-worktrees/W2-170/.gov-runtime/scratch/ref/fresh80/` (`preflight.py`, `f80lib.py`): they pin one
   set name and one run folder; the package derives everything from `--sets-root` and `--audit`.
4. **The briefs the set comes from:** `governance/project/indep-briefs/memory-audit/writer.md` (question form, the
   twelve categories, `drawn`, `sources`), `checker.md` (the notes' `## Questions` line form; section 5a),
   `governance/project/orchestration/packages/MEMORY-AUDIT-1.md`.
5. **The interfaces the tool uses:** `governance/project/path-map.yaml` (`memory-verdict-2` under `evaluation_sets`,
   the `evaluation-sources` / `evaluation-fixtures` namespaces, the glob rule); `src/gov/util/parts.py`
   (`evaluation_sets`); `src/gov/retrieval/measure.py` (how it accepts a set from a sets root's map: S4);
   `src/gov/retrieval/lexical.py` (`ids_in`, `whole_id`); `src/gov/store/loader.py` (`fingerprints`);
   `governance/project/orchestration/tools/indep_launch.py` (stage B4 selection rule, `SEEDS.log` / `AUDITS.log`
   forms, how it delivers `XCHECK-r<n>.md`); `governance/project/indep-walls/tree-exclude.txt`;
   `governance/project/test-map.yaml` and `gov close`'s scoped selection (under `src/gov/close/` or
   `src/gov/closure/`) for S6.

## What you build

`src/gov/memaudit/` (`__init__.py`, `__main__.py`, and the modules section 8 names: `layout`, `say`, `ledger`,
`preflight`, `drops`, `declare`, plus the domain/subsystem tables as data), est. 450 lines of code; your unit tests in
`tests/unit/memaudit/` (stand-ins and planted roots under `tmp_path` only; fast; no network, no model); the
`test-map.yaml` placement of `src/gov/memaudit/**` → `tests/unit/memaudit/` (S6: a change there selects these tests,
not the full suite); `docs/changes/W2-170-evidence.md` (one row per KPI line, S1-S6 and F1-F5, with the evidence).

Behaviour notes from the lead (behaviour, not test code):
- **File times are coarser than the clock.** On this file system a file's mtime can be coarser than
  `time.time_ns()`, so "wait until the clock is past `DECLARATION.json`'s mtime" is not enough for `USED` to be
  strictly later. Write `USED` only once a probe file you create (and then remove) in the run folder has its **own**
  mtime strictly past `DECLARATION.json`'s mtime (nanoseconds); bound the wait (a few seconds), and fail closed
  (`ERROR: <class>`, exit 4, no `USED`) if it never passes.
- `say` is the only printer, on stdout and stderr alike; no traceback or exception text anywhere (F1). Any
  unexpected exception in a subcommand ends as the one line `ERROR: <class>` and exit 4; argparse errors exit 4,
  `--help` exits 0.
- Read sources, `retrieval.yaml`, the path map and `tree-exclude.txt` from the commit (`git show` / `git cat-file`),
  never the working tree; never write the repository (its `git status --porcelain` stays empty).
- Whole-folder pytest with an empty `HOME` needs `PYTHONUSERBASE=/home/usain/.local` (pytest is a user install).

## Check and commit

1. Your unit tests:
   `env HOME=/home/usain/gov-os-worktrees/W2-170/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-170/src TMPDIR=/tmp/gov-os-lead-W2-170 python3 -m pytest tests/unit/memaudit -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
   (no test, class, parametrize id or file name of yours may contain `real`, `green_here` or `time_limit`).
2. When they pass, run the acceptance suite the same way on `tests/acceptance/W2-170` (or
   `PYTHONPATH=/home/usain/gov-os-worktrees/W2-170/src python3 -m gov.cli.main accept W2-170 --root /home/usain/gov-os-worktrees/W2-170`)
   and read only its failure output. Fix what fails against the Interface; if a failure seems to ask for something the
   Interface does not say, do not guess: name it in your return as a package. Quote the last line.
3. `python3 -m gov.memaudit preflight --help` (and `void`, `declare`) each exit 0.
4. Commit only your paths, in batches as you go:

       git commit -m "<subject>" --trailer "Task: DAEO-61vm" --trailer "Role: engineer" --trailer "Implements: DEC-1101, DEC-1125, DEC-1098, DEC-1097, DEC-1069, DEC-820, DEC-896, DEC-1050, DEC-1073, DEC-1052" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- <your paths>

   `Implements:` lists only ids from the ticket's `sources:`; an id you need that is not there goes in `discoveries`.
   Then quote `git log --oneline -5`, `git status --short` and
   `git diff --name-only 79a8fb87f HEAD` (must list only your allowed paths and the merge's `.tickets/DAEO-61vm.md`,
   `governance/project/orchestration/packages/DECIDED-NOT-DONE.md`).
5. Before you return: `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` shows nothing of yours.

## Return

One message, your last, complete in itself. **The twelve fields first, each a labelled line** ("none" where nothing):

```
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
```

`status` is DONE, PACKAGES, ESCALATION, ESCALATION_BLOCKED, LAUNCH_BLOCKED or AUTH_REQUIRED, with one line of why. In
`evidence`: the sandbox check and the `ps` check, the `gov.__file__` line, the unit and acceptance last lines, the
`--help` exits, each commit hash with its trailers, `du -sh` of your scratch. In `tests`: unit cases per KPI line and
the acceptance counts. Also the refusals met (time, form, reason) and every Interface gap you found.
