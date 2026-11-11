---
type: probe
task: DAEO-ouet
reviewer_session: cb3033a9-3f2e-4d3a-8604-ed8258e68b4d
implementer_session: the D-10 red-fix list's test designer of `6bcbbcdd5` and `65fa76dc3` (the reaping of planted gov accept runs; its session log went with its removed worktree)
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 9ca161a6fe38b4dbac953841f4f76e5b91654cfa
---

# Fresh probe of W2-96 (DAEO-ouet) at 9ca161a6fe38, after D-10's merge (DEC-895)

- **Why fresh:** `probe_impact.py` named it stale: the merge `f7e63ae4e` (D-10's red-fix list, the incident of 2026-11-10 00:43) changed four judged files under tests/unit/accept/.
- **Brief:** `.gov-runtime/scratch/orchestrator/briefs/D10-W2-96-probe.md`; a fresh, read-only independent reviewer, effort max, launched by the CTO's D-10 helper; verdict.py READY (no blocking finding); the orchestrator's judgement: pass.
- **The reviewer's record follows, as returned.**

# Probe record: W2-96 (DAEO-ouet), the full probe after D-10's merge into its judged files (DEC-895)

**Sandbox check (Step 0, `EMG-d4b-launched.md`): passed.**
- (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-W2-96','w').write('x')"` failed as required, with `OSError: [Errno 30] Read-only file system`. No file was created.
- (b) `echo sandbox-trial | git hash-object -w --stdin` returned `1ae28402a109c3397a44b19239a00adfa9472eb0`, and `git update-index --refresh` exited 0.

**ps check:** `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` printed nothing. I ran the brief's pipe as given. Each command here gets its own process namespace (my planted processes had pids from 48 to 2491), so the check only sees that command's processes.

- **task:** DAEO-ouet (W2-96). A fresh, read-only full probe of `gov accept` at integrate `9ca161a6fe38`, after D-10's merge `f7e63ae4e` changed four of its judged builder test files and added `w2_96_reap.py` (commits `6bcbbcdd5` and `65fa76dc3`). KPI id: `w2-96-full-probe`.
- **decisions:** DEC-959, DEC-1061, DEC-987, DEC-732, DEC-317, DEC-866, DEC-1109, DEC-801, DEC-808, DEC-1010, DEC-1014.
- **status:** DONE. The verdict is **pass**. There are three findings: none is in this revision's scope, and none fails open or loses work.
- **work_completed:**
  - Read the ticket, the last probe, D-10's review, the incident and the merge.
  - Read the revision's diff (`1b7394be9..65fa76dc3`), `w2_96_reap.py`, the four test files, `runner.py` and the CLI entry point.
  - Read W2-96's acceptance README, its support module's environment, and the opt-in lists and filter.
  - Ran the builder cases serially and with 4 workers.
  - Ran `gov accept W2-96` the declared way, then again with both opt-ins.
  - Ran two mutation checks on scratch copies of `src/` in my TMPDIR.
- **files_changed:** No tracked file changed: `git status --porcelain` is empty and HEAD is unchanged. Step 0 wrote its blob and refreshed the index's stat data, as the brief requires.
  - **Not quite nothing:** the acceptance runs left ignored bytecode folders in this worktree, `src/gov/{accept,records,store,tasks}/__pycache__/`, written at 10:33:22Z. They were not in my baseline `git status --porcelain --ignored` (see F3). I did not remove them, since the rules allow `rm` only inside my own TMPDIR.
  - **A false refusal worked round:** the Edit tool asked for a permission grant for my TMPDIR copies, which sit outside the working directories. I made the mutations instead with one in-sandbox `sed -i` per scratch copy (the equivalent form, DEC-1040 item 3).
- **evidence:**
  - Probed commit `9ca161a6fe38`; session `cb3033a9-3f2e-4d3a-8604-ed8258e68b4d`.
  - `git log 90122df096e7..9ca161a6fe38 -- src/gov/accept` is empty: gov's code is unchanged since the last probe.
  - `f7e63ae4e` merges `65fa76dc3` (5 files, 374 insertions, 65 deletions) with the trailers `Task: DAEO-ouet` and `Implements: DEC-1109, DEC-866`.
  - Scratch use peaked at 6.6 MB and 581 inodes, mostly the two copies of `src/`. I then removed it.
- **tests:** Every run went through `heavy_slot.sh`, with a scratch HOME (its `.local/lib` linked to the user site), my own TMPDIR, `PYTHONDONTWRITEBYTECODE=1` and `-p no:cacheprovider`.
  - **Builder cases** (`tests/unit/accept`, `--optin lifted,breadth`, with the real-model exclusion flags): 98 collected; the flags left nothing out.
    - Serial: **98 passed in 79.76 s**.
    - With `-n 4`: **98 passed in 23.21 s**.
  - **`gov accept W2-96`, the declared way** (the pin interpreter, `PYTHONPATH=<tree>/src`): **exit 3, `outcome: fail`**, `error_kind` null.
    - Totals: 74 passed, 0 failed, 0 skipped; 15 of them unmapped.
    - Passed per line: success 1–5 were 11/15/16/9/18 and failure 1–4 were 12/16/9/16. No line had a failed case.
    - Even so, success-2, success-5, failure-1 and failure-4 answer `fail` (F1).
  - **The same command with `GOV_TESTS_OPTIN=lifted,breadth`:** **exit 0, `outcome: pass`**, 109 passed, 0 failed, 0 skipped.
    - Passed per line: success 1–5 were 14/22/23/11/36, failure 1–4 were 18/23/11/31, and 23 were unmapped.
    - These figures are identical to the last probe's.
  - The exclusion flags can't be passed through `gov accept`. W2-96's acceptance folder has no `local_only` marker and no test named with those words, so they would leave nothing out.
  - **Mutation checks** (scratch copies only):
    - With gov changed to neither kill its pytest group nor reap the run: 16 cases selected; **11 failed in the call phase, 5 passed, 0 teardown errors**.
    - With gov changed to stop holding signals during its clean-up: **10 of 10 failed, 0 teardown errors**.
- **discoveries:**
  1. The declared `gov accept W2-96` fails at integrate even though every case it collects passes (F1).
  2. W2-96's README holds two maps. gov reads only a table with a `Test` or `File` column, so D-4's regenerated table (`README.md:441-452`) is ignored and the original map (lines 51–74) governs.
  3. This confirms D-10's review, discovery 1: gov strips `PYTHON*` variables from its child, so `PYTHONUSERBASE` never reaches it. A scratch HOME with `.local/lib` linked works both for gov's child and for the planted runs.
  4. I saw D-10's F4 happen, but only under a gov that already fails R16. Under the no-kill mutant, the reaper exited 0 while two forking chains were still running. Those chains had sessions of their own and had moved under init once gov ended; they were bounded by their own 20 s.
- **risks:** F1 to F3, below. Until F1 is fixed, a close or a lead's check that runs `gov accept W2-96` the declared way will get exit 3. W2-96 is due to close at the lift (P1-13).
- **lessons:**
  - After a suite is cut, compare `gov accept`'s default run with the opted-in run. Under R5, a map item that names a function the cut removed whole becomes a false failure.
  - Take a baseline of `git status --porcelain --ignored`, not only `--porcelain`, before running a suite that starts gov from the tree's `src/`.
- **proposed_decisions:** none.
- **unresolved:** who fixes F1, and how. That is the CTO's call.
- **recommended_next_action:** Take the probe as pass and file F1–F3 as rows. For F1, three options:
  - (a) Remove the two `# cap` lines from `tests/optin-lifted-breadth.txt` (lines 1164 and 1167). R15's and R16-SIGTERM's cases would run in the full run again, which is D-4's own round-2 rule. It costs about half a minute per run.
  - (b) Have the test designer point those two map rows at cases that run by default (with a Rewrite-Reason).
  - (c) Have the close run W2-96's acceptance with both opt-ins.

  I recommend (a), with medium confidence.

## Answers to the checks

**1. Do the revised builder tests still test what W2-96's KPIs need? Yes.**
- **Signal handling (128 plus N, and signals held during the clean-up):**
  - Every signal still goes to gov's pid alone.
  - The r9/r12 cases (11), r11 (3), r2 (2), r14's stopped run (6) and r16's stopped and forking runs (7) still assert, in the case's body:
    - the exit code is 128 plus the first signal;
    - no marker or traceback appears in gov's output;
    - the given TMPDIR is empty;
    - the child, grandchild or orphan is gone.
  - Those lines are unchanged. The diff touches only the launch line, the `launch` argument, imports and docstrings.
  - Against the no-hold mutant, all 10 clean-up-signal cases went red. gov exited with 128 plus a later signal, or died by a signal (−2, −15), or left its `gov-accept-…` folder in the given TMPDIR.
- **The clean-up:** the case still checks that the given TMPDIR is empty the moment gov ends. The harness keeps its wrapper, record and reaper in `tmp_path/w296_reap`, never in the given TMPDIR.
- **No test content reaching the caller:** gov's stdout and stderr are still read through one pipe and searched for the marker. The wrapper's recording writes only pids, to a file outside the given TMPDIR, and prints nothing.
- **gov's own behaviour is untouched by the new launch:**
  - Its own session changes nothing gov does. gov signals only its pytest's group and its own children, by pid (`runner.py:155-160` and `194-211`). It reads no session, group or terminal state.
  - The recording subclass wraps the only Popen on the accept path (`runner.py:339`). There is no other subprocess in the runner, the command module or the config loader.
  - A signal landing during the recording's write would leave gov without its child's handle. Even then, gov's subreaper pass stops the child (`runner.py:364-368`), and no case signals before the planted test has started.

**2. Is any case weaker, or passing for the reaper's reason instead of gov's? No.**
- **The reaper is idle during the case's body.**
  - It blocks reading a pipe whose only write end the case holds (`w2_96_reap.py:46`).
  - That end is closed in the fixture's finaliser after the body (`:189`), or when the case's process dies. So every check in the body runs before the reaper acts.
  - The fixture adds one assertion, that the reaper exits 0 (`:203`), and removes none.
- **The mutation run shows it.** With gov not killing or reaping its run, 11 cases failed in the call phase, and the reaper still exited 0 with no teardown errors. The failures were:
  - the three r16 stopped runs ("the orphan outlived gov");
  - two forking runs (forked pids still alive);
  - four r9/r12 cases (the child not gone);
  - two r2 cases (the grandchild not gone).

  The two `hop` variants passed, as they would have before the revision (F2).
- **r2 and review 3's case:**
  - r2 now runs gov's `main(argv)` through the wrapper instead of `-m gov.cli.main`. That is the same call (`main.py:263-264`).
  - Review 3's patch now applies before gov is imported. The runner looks up `os.unlink`, `os.rmdir` and `runner._remove` at call time, so the same calls are patched.
- **The three proof cases test the harness, not gov.** They also passed against the no-kill mutant, which is their purpose: the reaper alone cleaned up.

**3. Counts:** the builder cases were 98/98 serially and 98/98 with 4 workers. The declared `gov accept W2-96` gave exit 3 (74 passed, 0 failed, four lines failing on named tests that weren't collected). With both opt-ins it gave exit 0 (109 passed). The `tests` field has the per-line figures.

**4. Judgement: pass** for W2-96 at `9ca161a6fe38`.
- gov's code is unchanged since the passing probe.
- With every case run, its acceptance result is identical to that probe's.
- The revised builder tests still test gov's own behaviour.
- F1 is a mismatch between the README map and the opt-in list, outside W2-96's code and outside this revision, and it fails closed.

**Probed and found sound:**
- Signals go to gov's pid alone.
- The reaper is idle until the case ends.
- The reaper targets only recorded pids and the groups of their descendants. It never matches by name.
- The reaper exited 0 in every case of all four test runs.
- The launch form is equivalent for r2 and review 3.
- gov's acceptance result is unchanged once all its cases run.

## Findings

**F1. The declared `gov accept W2-96` reports a failing run at integrate, although every case it runs passes.**
- **What was done:** I ran `PYTHONPATH=<tree>/src <pin>/bin/python -m gov.cli.main accept W2-96` at `9ca161a6fe38`.
- **What happened:**
  - It gave exit 3, `outcome: fail`, with 74 passed and 0 failed.
  - success-2, success-5, failure-1 and failure-4 answer `fail` with no failed case.
  - Those are exactly the lines of the README map's two rows that name `test_r15_eight_thousand_empty_sibling_folders_are_removed_within_the_bound` and `test_r16_a_sigterm_to_gov_alone_while_a_nested_run_sleeps_leaves_no_process_and_nothing_later` (`README.md:71-72`).
  - D-4's cut moved both functions whole into `breadth` (`tests/optin-lifted-breadth.txt:1164` and `:1167`, marked `# cap`). A run without the opt-in never collects them.
  - gov then fails each line whose named test matched no case, which is R5's rule, by design.
  - D-4's regenerated map has no `Test` or `File` column, so gov ignores it.
  - With both opt-ins the same command passes (109 passed, 0 failed), with the last probe's counts.
- **What should have happened:** the declared run should pass, as it did at the last probe. Either the named cases run by default, or the map names only cases that do.
- **Cause:** D-4's cut (`c429c0d26`, `cb96180d1`; DEC-1061), not the D-10 revision and not `src/gov/accept`. I found no record of this in `governance/` or the register.
- **What would reverse it:** a declared run at `9ca161a6fe38` that exits 0 with every line passing, or the two functions being collected without the opt-in.
- Ordinary work: yes, because any engineer, lead or close that runs `gov accept W2-96` the declared way at integrate meets it, with no construction needed.
- Consequence: other (it fails closed: a false failure, with no failing case hidden)
- Scope: out

**F2 (row). The builder cases for a fork-and-exit chain (`hop`) can pass while gov leaves the chain running.**
- **What was done:** I changed gov, in a scratch copy, so that it neither kills its pytest group nor reaps the run, then ran the reaper-using process cases.
- **What happened:**
  - Both `hop` variants passed while every other process check failed.
  - The likely reason, from the planted program (`test_w2_96_review4.py:48-50`): each process in the chain records its pid only after a 5 ms pause, and the process recorded before it has already exited.
  - The case judges only recorded pids (`:180-183`), so at most moments none of them is alive.
  - The revision didn't touch these lines, so this was already true before it.
- **What should have happened:** the cases should fail whenever the chain outlives gov, as the `breed` variants did.
- **What would reverse it:** repeated runs of the two `hop` variants against the same mutant failing every time.
- Ordinary work: no, because a gov that stops reaping is caught by the `breed` cases, the orphan cases and the acceptance R16 cases. Only a regression specific to fork-and-exit chains would depend on these two, and they would still catch it in some runs.
- Consequence: other
- Scope: out

**F3 (row). Each run of W2-96's acceptance suite writes or refreshes ignored bytecode in the tree's `src/`.**
- **What was done:** I compared `git status --porcelain --ignored` before and after my runs.
- **What happened:**
  - `src/gov/{accept,records,store,tasks}/__pycache__/` appeared, written at 10:33:22Z during the `gov accept W2-96` runs.
  - The suite starts its planted `python3 -m gov.cli.main` processes with an environment built from scratch, deliberately without `PYTHONDONTWRITEBYTECODE` (`w2_96_support.py:31-34` and `1328-1338`). Those processes import gov from the tree's `src/` (DEC-732).
  - gov's own child pytest runs with `-B`, and the planted project stays clean.
  - `git status --porcelain` stays empty.
- **What should have happened:** a read-only run should leave the tree as it found it, ignored files included. A possible fix is to start the planted gov with `python3 -B`, which never reaches its child's environment.
- **What would reverse it:** the folders not appearing after a run on a tree that doesn't have them.
- Ordinary work: yes, because every run of the suite in a worktree does it.
- Consequence: other (ignored caches only; nothing lost, nothing hidden)
- Scope: out

Classification: 0 yes / fails open or loses work; 2 yes / other (F1, F3); 1 row for Wave 3 (F2). D-10's review findings F1–F5 stand as its rows.

**Verdict: pass.**

```verdict
{"kpis": [{"kpi": "w2-96-full-probe", "verdict": "pass", "findings": [{"id": "F1", "scope": "out", "ordinary_work": "yes", "consequence": "other"}, {"id": "F2", "scope": "out", "ordinary_work": "no", "consequence": "other"}, {"id": "F3", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}]}
```
