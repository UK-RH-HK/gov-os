You are the ticket lead for ticket `DAEO-c1uz` (`W2-66`, "Path-scoped regression at close: selection and evidence (the lite W2-38)"), profile FULL, working only in the worktree `/home/usain/gov-os-worktrees/W2-66` on branch `w2/W2-66`.

**This is run 2,** after your run 1's PACKAGES (P-W2-66-S1 and P-W2-66-T1). `git log --oneline -1` must show `ba38ab8d`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it. Read your own `.gov-runtime/scratch/lead/CHECKPOINT.md` first.

## The decisions since your run 1 (all on `w2/integrate`, which you merge first)

- **P-W2-66-S1, the scratch budget (DEC-904, DEC-905):** the owner's retention trial held, so every full run now passes `-o tmp_path_retention_policy=failed`.
  - The trial's full run peaked at 165,707 files and folders and 0.91 GB, against your run 1's 5.3 million and 47 GB.
  - Run under `flock /tmp/gov-os-verify.lock`, one verification run at a time; the commands are in the common brief below.
  - **Your ticket gains a KPI (DEC-905):** the close's own pytest runs (its parallel run and its serial-only cases) pass the option, and the evidence block names it.
  - Your run 1's temp folder is removed.
- **P-W2-66-T1, DEC-903 (delegated, accepted by the owner):**
  - `tests/acceptance/W1-39/test_w1_39_copy.py::test_copy_creates_the_overlay` is named for your test designer, with `Rewrite-Reason: DEC-896 item 2`: the overlay holds the path map and the test map.
  - The CLI's error module is `src/gov/cli/errors.py` in the shared core (your ticket file is corrected).
  - The path map's `test_inputs` key is removed by the orchestrator at your merge, not by you.
- **The merge order (DEC-899 item 2): W2-07 is merged** into `w2/integrate` (`2a9d1a11`). Its commit gates and pre-close gate rewrote `run()` in `src/gov/close/command.py` (+121/−35), and its new module is `src/gov/close/gates.py`.
  - **Merge `w2/integrate` into your branch, keeping both sides:** your calls into `select.py`, `nightly.py` and `evidence.py`, the record's lines and `--full`; W2-07's gates.
  - A conflict you cannot resolve keeping both sides is PACKAGES.
- **Also merged since:**
  - W2-70: the two nested reruns retired; W1-01's cases read the owner's `acceptance_exemptions` list, now green on `w2/integrate`.
  - W2-67 round 1: copies with `gc.auto 0`; the root `tests/conftest.py` refuses a per-run `--basetemp`.
  Your selection and test map must place their files.
- **DEC-906:** every change under `tests/acceptance/` is a test designer's commit.

## This run's order

1. **Merge `w2/integrate` into this branch, in one Bash call, with its trailers** (`Task: DAEO-c1uz`, `Implements: DEC-899`, `Role: orchestrator`, `Co-Authored-By`).
   - Resolve `command.py` keeping both sides.
   - The merge's tree must equal `git merge-tree --write-tree HEAD^1 HEAD^2` when it is clean, or the recorded resolution otherwise.
2. **A fresh test designer** (launched sandboxed, `--effort xhigh`): W1-39's overlay case (DEC-903), and the retention option's KPI (DEC-905).
3. **A fresh engineer** (launched sandboxed, `--effort high`): the retention option in the close's pytest runs, and whatever the merge left for your modules.
   - Then run your `briefs/eng-2.md` round, the measured report and the fixture trial in `docs/research/W2-66-scoped-close.md`, as planned in run 1:
     - a shared-core change runs everything;
     - a one-module change runs its suites;
     - a record-only commit runs the record-reading set;
     - the time of each.
4. **Verify in full** in the close's form, under the lock, with the retention option: rebuild, collection, `gov check`, the parallel run, the serial-only run.
5. **A fresh FULL review on the merged head** (brief A3 with `JUDGEMENT.md` word for word, `--effort max`; your first review). Commit the probe record only when it passes.
6. **Return** DONE (merge and fresh probe done; ready for the re-pin), or PACKAGES.

**Time:** each worker gets a budget of about 90 minutes (the Bash tool's two-hour limit).

---
