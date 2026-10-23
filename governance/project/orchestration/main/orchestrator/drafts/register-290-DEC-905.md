
## 290. The retention trial's result of 2026-10-23, applied (register v0.290, recorded by the W2 orchestrator on branch `w2/integrate`)

### DEC-905 — The retention trial held: `-o tmp_path_retention_policy=failed` is the default for the close, the nightly run and the leads; the bridge cap ends; the lock stays
- **Status:** ACCEPTED. Items 1 to 3 are the owner's conditional decision (DEC-904 item 1: "if it holds, it becomes the default"), applied by the orchestrator on the trial's evidence. Item 4 is delegated: stricter only, under the prompt §7. `Task: decision-record`, `Role: orchestrator`. The owner may overturn either. · **Under:** DEC-904, DEC-898, DEC-902, DEC-880 item 2 (b) · **Basis:** the trial (`.gov-runtime/scratch/orchestrator/tools/retention_trial.sh`; results kept in the orchestrator's `log/retention-trial-2026-10-23.txt` and its samples).
  - One full parallel run in the close's form, on a clone of `de2b5bf1`, with the option, under the verification lock, at a load of about 25 (W2-69's lead running).
  - **Peak:** 165,707 files and folders and 0.91 GB, sampled every 30 seconds; 129,629 after the run. W2-66's lead's run without the option made 5,306,782 and 47 GB.
  - **The planted failing test's folder was kept.**
  - **The results:** 15,464 passed and 30 skipped (the same 30 tests as the rehearsal of 2026-10-21's full run). The three reds and one error are not the option's:
    - the planted failure;
    - W1-01's MR-3 history case (`test_only_the_test_designer_commits_to_acceptance_tests`), red on `w2/integrate` since the owner's commit `c9a08678` (package P-W1-01-H);
    - W2-58's two launched-session cases, whose sandbox could not create its bridge sockets under the trial's long `TMPDIR` (`/tmp/gov-os-trial-retention/tmp`). They passed with the option under `/tmp` and under a lead-length path (`/tmp/gov-os-lead-W2-99`), 3 of 3 each.
  - **Time:** 2,459 s at a load of about 25, against W2-50's close's parallel run of 2,046 s at 2.7. No evidence of a cost; not a clean comparison.
- **Decision:**
  1. **The option is the default** for the leads' full verification (the common lead brief's commands), the nightly run (`nightly.sh`) and the close (W2-66's KPI, in its close command in `src/gov/close/command.py`).
  2. **The bridge cap of DEC-904 item 3 ends.** A lead's full run fits DEC-898's 20 GB and 1,000,000 again.
  3. **The disk floor and DEC-898's budgets stand.**
  4. **The lock stays (delegated, stricter only):** one verification run at a time across the machine, under `flock /tmp/gov-os-verify.lock`. It keeps two full runs from loading the machine at once, which also keeps the timing cases' runs quiet. The owner may lift it.
  5. **A session's own `TMPDIR`** (DEC-898) stays short, at most a lead-length path such as `/tmp/gov-os-lead-<W2 id>`, so the launcher's sandbox can create its sockets.
- **Where it goes (DEC-851):**
  - this register, with DEC-904's status line marked;
  - the prompt §15 (the default; the cap ended; the lock), v3.22;
  - `LEAD-w2-common.md` (the commands);
  - RESUME HERE;
  - W2-66's ticket file (its own commit);
  - `nightly.sh`.
- Next free id: DEC-906.

| Version | Date | Change |
|---|---|---|
| 0.290 | 2026-10-23 | DEC-905 (the retention trial held: peak 165,707 inodes and 0.91 GB against 5.3 million and 47 GB, a failing test's folder kept, results unchanged; the option the default for the close, the nightly run and the leads; the bridge cap ended; the lock kept, delegated and stricter only; a session's TMPDIR kept short). Next free id: DEC-906. |
