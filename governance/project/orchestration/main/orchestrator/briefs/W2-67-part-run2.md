You are the ticket lead for ticket `DAEO-9nys` (`W2-67`, "Test hygiene: per-test copies, nested runs, temp folders, and the weak tests' revisions"), profile FULL, working only in the worktree `/home/usain/gov-os-worktrees/W2-67` on branch `w2/W2-67`.

**This is run 2: round 1 resumed** after your run 1's PACKAGES (P-W2-67-1). `git log --oneline -1` must show `60f71c42`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it. Read your own `.gov-runtime/scratch/lead/CHECKPOINT.md` first.

## The decisions (DEC-907, delegated; on `w2/integrate`, which you merge first)

- **P-W2-67-1 (a):** the ticket's role is now `engineer`.
  - Its `allowed_paths` hold only builder files: `tests/unit/guard/**`, `tests/conftest.py`, and `tests/unit/close/**` (round 2, not now).
  - Its acceptance files are named in the ticket file's body for its test designers (MR-3).
- **The copying fixtures** (`tests/acceptance/W1-07/w1_07_support.py`, W1-25's, W1-27's) are changed by **a second, fresh test designer**, with `Rewrite-Reason: the copy races git's background gc (I3 F9, I4 F5)`. It runs batch 1's `test_w2_67_*` files, `w2_67_tmp_probe.py` and `README-W2-67.md`, but never reads them: give it only their names and how to run them.
- **TD1-A:** the root `tests/conftest.py` refuses, at the start, a run given a per-run `--basetemp`, naming DEC-898. One opt-out stays, the environment flag `GOV_ALLOW_BASETEMP=1`. That is your engineer's builder work, with the guard unit test's fixed `/tmp` folder becoming `tmp_path`.
- **TD1B-A:** accepted (a rebuild admits git and gitleaks).
- **TD1C-A:** the fixtures' clean-up of the code-graph folders is round 2's.
- **TD1B-B and TD2-A** go to the owner's digest; nothing for you to change.
- **DEC-905:** every full run passes `-o tmp_path_retention_policy=failed`, under `flock /tmp/gov-os-verify.lock`. The common brief below gives the commands.
- **DEC-906:** W1-01's history case is a known red until W2-70 merges. Report it by name; do not let it stop your DONE.
- **DEC-904 item 2:** your run 1's temp folder is removed. Name this run's folder and its size in your return.

## This run's order

1. **Merge `w2/integrate` into this branch, in one Bash call, with its trailers** (`Task: DAEO-9nys`, `Implements: DEC-907`, `Role: orchestrator`, `Co-Authored-By`). The tree must equal git's own merge.
2. **The second test designer** (fresh, launched sandboxed, `--effort high`) on the copying fixtures, as above.
3. **A fresh engineer** (launched sandboxed, `--effort high`) on `tests/conftest.py`'s rule and the guard unit test's `tmp_path`, inside the allowed paths.
4. **Check:** batch 1's KPI tests are now green, and the four copying suites are green.
5. **Verify** in the close's form, under the lock, with the retention option. Measure the four copying suites' inodes and time "after", against your "before".
6. **FULL review,** limited to round 1's changes: a fresh read-only reviewer, brief A3 with `JUDGEMENT.md` word for word, `--effort max`. Commit the probe record under `docs/probes/DAEO-9nys/`.
7. **Return** DONE for round 1 (it merges early; the ticket closes later), or PACKAGES.

**Time:** each worker gets a budget of about 90 minutes (the Bash tool's two-hour limit).

---
