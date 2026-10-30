You are the ticket lead for ticket `DAEO-9nys` (`W2-67`, "Test hygiene: per-test copies, nested runs, temp folders, and the weak tests' revisions"), profile FULL, working only in the worktree `/home/usain/gov-os-worktrees/W2-67` on branch `w2/W2-67`.

**This is run 5: the merge-back, the re-verification and the fresh probe (DEC-941 item 2, DEC-895), not a new round.** All three declared rounds are built: round 1 is merged into `w2/integrate` (`4da40b60`); rounds 2 and 3 were verified at `db8d50bb4893` and passed their review at `a74e9c67e913` (run 4). `git rev-parse --short=12 HEAD` must show `d0140d4d222e`. `git status --short` must show exactly one line, `?? tests/acceptance/W1-27/w2_67_td4_plant.py` (the inert plant DEC-920 item 5 keeps here; never commit it, never delete it). Anything else: stop and return PACKAGES naming it.

**Read first:**
- your run-4 checkpoint, `.gov-runtime/scratch/lead/CHECKPOINT.md` (its last line: a merge of `w2/integrate` redoes the probe);
- the ticket file (`.tickets/DAEO-9nys.md`) and its card in `docs/plan/WAVE_2_WBS.md` §2 ("#### W2-67");
- DEC-907, DEC-914, DEC-916, DEC-920, DEC-895 and DEC-941 (items 2 and 6), and DEC-946 (item 1);
- the run-3 probe record on your branch, `docs/probes/DAEO-9nys/PR-DAEO-9nys-run3.md` (what was judged, and the lead's own run of TD1C-A's case outside the sandbox).

## Why you start now

- **Finish before you start (owner, DEC-946 item 1):** closing built work comes before any new ticket, and W2-67 is named there. The verification-lock trial waits on W2-67's close (DEC-941 item 6, DEC-942 item 5).
- **Your probe is stale.** `tests/acceptance/W1-30/README.md` changed on both sides since your merge base: W2-57's `4fe257d5` (its r11 and r13 notes) on `w2/integrate`, your `+4` lines on the branch. W2-57, W2-68 and W2-07 also changed the close's code your W1-30 cases and your nested-run unit functions exercise (`src/gov/close/command.py`, `gates.py`, `serial.py`, `batch.py`, `fingerprint.py`, `repo.py`). Under DEC-895, the probe is redone on the merged head.
- **Where the branch stands:** 20 commits ahead of `w2/integrate` and 233 behind; merge base `6f94b16fec21`. A dry merge (`git merge-tree --write-tree w2/W2-67 w2/integrate`) reports **no conflict**.
- **What changed in your folders meanwhile, on `w2/integrate`:**
  - `tests/acceptance/W1-30/`: `README.md`, `test_w1_30_r11_declared_here.py`, `test_w1_30_r13_probe_findings.py` (W2-57) and `test_w1_30_r15_policy_pairs.py`. None of them is a case you revised.
  - `tests/acceptance/W1-27/test_w1_27_doctor.py`: W2-65's canary declarations (`03d9aa08`, DEC-913 item 3), the fix for the red P-W2-65-3 named on round 1's doctor case.
  - `tests/unit/close/`: `test_batch_refresh.py`, `test_batch_reuse.py`, `test_fingerprint.py` (W2-68), `test_serial.py` (W2-57) and `test_w2_07_decision_records.py`. None is one of your three files.
  - No change to `tests/acceptance/W2-50/`, `tests/conftest.py` or `tests/unit/guard/`.

## The decisions for this run

1. **Merge `w2/integrate` into `w2/W2-67`** (`git merge --no-ff w2/integrate`, with `Task: DAEO-9nys`, `Implements: DEC-941` and `Role: orchestrator` in the final trailer block). Never `-s ours`, and never drop this ticket's side (DEC-750 item 3).
   - If git reports a conflict that a mechanical fix resolves (both sides kept as written, and neither side's behaviour changed), resolve it and say how in the return. Any other conflict: `git merge --abort`, and return PACKAGES naming each file.
   - After the merge:
     - `git show HEAD:tests/acceptance/W1-30/README.md` must hold both W2-57's r11 and r13 notes and your four lines;
     - `grep -c '^### DEC-941' docs/DECISION_REGISTER.md` must show 1. If it does not, stop and return PACKAGES: the trailer gate would refuse every `Implements: DEC-941`.
2. **Rebuild** from this worktree's code (check `gov.__file__` first), as `flock /tmp/gov-os-rebuild.lock` around the rebuild command, never `--no-embeddings`. Name every entry or record the load lists as `invalid`; `invalid: []` is expected.
3. **Verification: in full,** in the close's form (LEAD-w2-common), plus `pytest --collect-only -q` over `tests` (DEC-868). Your rounds 2 and 3 and the close's code of W2-57, W2-68 and W2-07 have never run as one. Look hardest at:
   - **W1-30's 13 revised cases and the nested-run unit close functions** (the 13 that start a real nested pytest, in `tests/unit/close/test_measured.py`, `test_parallel_runs.py` and `test_run_and_record.py`, and the seven serial collect-only ones run 4's reviewer counted), against the merged close;
   - **W2-50's large-store and hang cases**, and W1-27 and W1-26 whole;
   - **KPI 4's count:** after the parallel run, count pytest's base folders left under your `TMPDIR` (`/tmp/gov-os-lead-W2-67`), and quote the figure. At most three.
   - **TD1C-A's code-graph case** (`tests/acceptance/W1-27/test_w2_67_codegraph_folders.py`): you run it yourself, outside the sandbox, as run 4 did, with the daemon folders under `/tmp/gov-cbm-1000` counted before and after.
   - **Known reds:**
     - DEC-919's case (row W2-L440), which lists `tests/acceptance/W1-27/conftest.py`: name it, and it does not stop your DONE (DEC-920 item 1);
     - W1-42's accepted reds;
     - the load-sensitive cases, re-run alone;
     - W2-54's green-here cases may time out under load (row W2-L429), so re-run them alone.
   - Any other red is named with its cause.
4. **Repair: at most one batch in this run,** whether it comes from a verification red or from the probe (item 5). Only these files may change, each split by file from the tickets running beside you:
   - **A red in your revised acceptance cases:** a fresh independent test designer (DEC-906; launched sandboxed, `--effort xhigh`; its brief must not set `TMPDIR`), each change with a `Rewrite-Reason:` and no expectation lowered. Its files are only the ones your branch changed:
     - in `tests/acceptance/W1-27/`, `tests/acceptance/W1-30/` and `tests/acceptance/W2-50/`, the files `git diff --name-only 6f94b16fec21 d0140d4d222e` names;
     - never W1-30's `README.md`: a note goes in `README-W2-67.md` instead.
   - **A red in your unit close functions:** a fresh engineer (`gov launch`, sandboxed, `--effort high`), in `tests/unit/close/test_measured.py`, `test_parallel_runs.py` and `test_run_and_record.py` only.
   - **Not in this run:** `tests/conftest.py` (every running lead's verification reads it, so a change there waits until no lead verifies), any other file in `tests/unit/close/` and `tests/unit/guard/`, and any file of `src/`. A red whose fix needs one of them is returned as PACKAGES.
   - **A nested pytest in another ticket's file** (`test_serial*`, `test_batch*`, `test_fingerprint*`, `test_w2_07_*`, `test_nightly_cleanup*`) is not yours: it is a residual row, never a repair here.
   - After the batch: the red cases and their suites again; a second full run only if a file changed.
5. **The fresh probe (DEC-895, DEC-916, DEC-920 item 6).**
   - **Before it:** `gov checkpoint` (DEC-511), committed with your trailers. That commit is the probed head. Nothing is committed after it except the probe record.
   - **Who:** one fresh FULL reviewer, launched sandboxed with `--effort max`, using brief A3 with `JUDGEMENT.md` word for word, on that head.
   - **What it is given:** run 3's probe record, and the list of files the merge brought into your folders (above). Its brief says that TD1C-A's case is judged from your own run outside the sandbox, recorded in the probe record (run 4's lesson).
   - **What it probes:**
     - the whole ticket's work as merged: rounds 1 to 3, each KPI line against the merged code;
     - whether each revised case still fails for its planted fault on the merged close (W1-30's plants PF1 to PF16; PF2 is caught by the unit suite since DEC-868 item 3);
     - whether every nested run of those functions stays bounded under the merged `serial.py` and `batch.py`;
     - whether the conftest's `--basetemp` refusal and its sweep of killed runs still hold beside W2-68's batch and the nightly's clone;
     - whether `README.md` in W1-30 keeps both sides.
   - **Judgement:** a finding that fails open or loses work, which an honest agent can hit in ordinary work, fails the probe; everything else is a residual.
   - **When it passes:** commit the record as `docs/probes/DAEO-9nys/PR-DAEO-9nys-run5.md`. Then dry-run the close's probe gate (`gov.close.command._check_probe`) on it, as run 4 did.
   - **When it fails:** if no repair batch has been spent, one test-design batch, one engineer, the red cases and a full run, then a second and last review. If a batch is already spent, return PACKAGES under the park rule.
6. **Out of this run, named in the return as open KPI parts, with no work on them:**
   - **KPI 2's second half:** worksteal re-measured in the nightly (row W2-L446). The nightly is frozen (DEC-946 item 9).
   - **KPI 5's T-A3 rows:** the ticket file names none of their folders, and its declared rounds do not include them.
   - **Rows W2-L447 (F-A) and W2-L448 (F-B):** already filed; nothing to do.
7. **Your trailers** (LEAD-w2-common, DEC-927 item 2): run `trailer_gate.py` on your worktree before you return.
8. **Before you return,** list each commit on `w2/integrate` after the one you merged that touches a file this ticket's commits changed:
   - `git log --format=%h --name-only` over the range from the `w2/integrate` commit you merged to `w2/integrate`, against `git log --grep='Task: DAEO-9nys' --name-only`;
   - W2-03's, W2-20's and W2-37's merge-backs change `tests/acceptance/W1-26/README.md`, and W2-20's and W2-37's also change `W1-07/w1_07_support.py` and `W2-02/`.
   
   Do not merge again. The orchestrator orders the merges.
9. **Return** DONE (green, the fresh probe passed and committed; ready to merge into `w2/integrate`, then the close queue), or PACKAGES. Carry the residuals as they stand (F-A, F-B, row W2-L446, the plant file), and add any new one.

**The park rule (DEC-941 item 2):** if the repair grows beyond this one run, stop and return PACKAGES naming the cost. That covers:
- a second repair batch;
- a fix outside the files item 4 allows (`tests/conftest.py` included);
- a red whose cause is another ticket's code.

Name what is left, its size in lines and hours, and what waits on it: the verification-lock trial (DEC-941 item 6), and the tickets whose closes the copies and nested runs slow.

**Running beside you:**
- **W2-77** (`DAEO-b6hm`) writes new `tests/unit/close/test_nightly_cleanup*` files and `src/gov/close/nightly.py`.
- **W2-57** (`DAEO-cy5o`, review only, run 4b) judged `tests/unit/close/test_serial*` and W1-30's `README.md`, r11 and r13. Your merge into `w2/integrate` will change that README, so the orchestrator closes W2-57 first, or re-probes it.
- **W2-03** holds `src/gov/store/**`, `src/gov/records/**`, `src/gov/decisions/**` and `src/gov/check/citations.py`.
- **W2-05** holds the git-environment lines across `src/gov/**/*.py`.
- **W2-71** holds `src/gov/secrets/**` and `tests/unit/secrets_check/**`. Your W2-50 cases test that check: run them, change nothing there.
- **W2-61** holds `src/gov/retrieval/measure.py` and `tests/acceptance/W2-61/`.
- **W2-60a** holds `src/gov/launch/launcher.py`, `role.py`, `record.py`, `tests/unit/launch/test_role*` and `test_launch_record*`.

Do not touch any of them. If a fix needs a change there, return PACKAGES.

**Verification's machine rules:**
- **The nightly (owner, DEC-933, DEC-936):** while `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/NIGHTLY-RUNNING` exists, you and your workers run no suite and no full run. Wait, and go on the moment it is gone.
- **Closes:** while `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING` exists, start no worker and no suite.
- **The 01:00 cut-off (owner, DEC-939 item 6):** from about 01:00, start no full verification run that `nightly_estimate.py estimate` says cannot finish before 02:00.
- **Every full run** goes under `flock /tmp/gov-os-verify.lock`, and **every rebuild** under `flock /tmp/gov-os-rebuild.lock`.

**Estimate:** about 3.5 hours:
- the merge and the rebuild, about 30 minutes;
- one full run, about 95 minutes (the last two nightly runs took 5,623 s and 5,707 s), split over background jobs within the two-hour limit;
- the checkpoint, the review and the probe record, about an hour;
- the return.

With one repair batch and a second review, up to 7 hours.

---
