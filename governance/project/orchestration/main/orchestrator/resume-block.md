# CHECKPOINT — W1 orchestrator (Wave 1 under the live guard)

- **Updated:** 2026-10-04, evening, after the owner's answers (DEC-306…DEC-326) and the closes of W1-49, W1-09 and
  W1-12. **Read "RESUME HERE" first; everything below it is history.** Prompt is **v4.1** (`3ccbf75c`).
- **Branch:** `w1/integrate`; head `beb8f9c4` (W1-16 claimed); tree clean; nothing pushed.

## RESUME HERE (2026-10-04, evening — after W1-49, W1-09, W1-12 closed)

- **Prompt v4.1**: section 6 also delegates stricter-only decisions (refuses more, denies more, fails closed, doesn't
  block the owner) even on the guard, containment or the launcher. **Next free register id: DEC-327.** Register v0.67.
- **W1-49 is CLOSED and the owner has been told** (final message of this turn). DEC-250: after W1-49's close I stop
  only for owner-level packages, escalations and `WAVE_1_EXIT_READY`; the owner updates prompt section 7. Until the
  prompt says so, the CONTEXT_CHECKPOINT stop in section 7 still stands as written. The PreCompact hook now appends a
  state block to THIS file at each compaction: leave the block, rewrite the written part. Auto-compact applies to
  sessions started after `840f1e37`. Never print or diff `.claude/settings.json`.
- **Last full run:** at `168397f6` (after the W1-12 merge), ALL GREEN: W1-01 46 + 28 skipped, W1-02 529, W1-03 364,
  W1-04 336, W1-05 99, W1-06 96, W1-07 228, W1-08 209, W1-09 77, W1-10 76, W1-12 21, W1-15 92, W1-18 15, W1-37 4,
  W1-45 105, W1-47 970, W1-48 172, W1-49 105, unit 455, validator ALL PASS; W1-46 32 failed / 105 passed / 120
  errors (its branch is not merged) and W1-50 26 failed / 17 passed (by design). Since then only `bootstrap.md` and
  two tickets changed.
- **Regression command:** `bash .gov-runtime/scratch/orchestrator/reg.sh <abs log/reg dir> > <abs
  log/reg/at-<head>.txt>` in the background (four groups in parallel, about 6 minutes; ends with the validator's
  RESULT line; a red suite's full output is kept as `log/reg/<suite>.full.txt`). Don't commit in the main tree while
  it runs.
- **Standing rules** (register + WBS): DEC-235/236/237 (6 tickets, gate `free -g` ≥ 4 GiB and load < 20, heavy
  counts double, `git merge --no-ff` with trailers in the last paragraph, full run, close, remove worktree, delete
  branch); DEC-253/254 (merge findings and worker-commit misattributions are records; copy the worktree's
  `.gov-runtime/findings.jsonl` to `log/<W1-id>-findings.jsonl` before removing it); DEC-256 (W1-50's
  implementation after W1-46 merges); DEC-249 (mid-wave audit when W1-21 is merged).
- **How a lead is started** (always background, one Bash call each):
  `cd ~/gov-os-worktrees/<W1-id> && /home/usain/.local/bin/claude -p --output-format json --permission-mode
  acceptEdits --allowedTools "Bash" "Read" "Edit" "Write" "Grep" "Glob" "Agent" "Monitor" "TaskStop" --settings
  '{"env":{"GOV_ROLE":"orchestrator","GOV_TICKET":"<ticket id>"}}' < <abs>/briefs/<W1-id>-A5-runN.md >
  <abs>/log/<W1-id>-lead-runN.json 2> <abs>/log/<W1-id>-lead-runN.err`. A brief = `briefs/<W1-id>-A5-headN.md` +
  `briefs/LEAD-common.md`. Read only the JSON's `result`. Every head carries the "wait in the foreground" paragraph.
- **If I was restarted:** background leads may be gone. `pgrep -af "local/bin/claude -p"`; a lead with an empty log
  and no process is restarted fresh with the same brief (it resumes from its worktree's lead checkpoint and
  `git log`).

### In flight (6 of 6: W1-16 counts double)

| W1 | ticket | state | next |
|---|---|---|---|
| W1-46 | `DAEO-jdqr` FULL | **lead run 2 RUNNING** (`briefs/W1-46-A5-run2.md`, `log/W1-46-lead-run2.json`): merge integrate, test batch 4 (DEC-311, 313, 314, 315, 316, 271–273, 317), engineer incl. the generic `main.py` change (DEC-317), re-merge integrate, verify with live sessions, narrow review, the worktree-commit question | On DONE: merge, full run, residuals (earlier list in `log/W1-46-lead-run1.json` + this round + the here-document guard observation from W1-15/W1-49), close; **pass the DEC-317 module convention to W1-25's brief**; then start W1-25's lead, W1-50's implementation lead, and W1-33 |
| W1-50 | `DAEO-xnbx` FULL | **lead run 2 RUNNING** (`briefs/W1-50-A5-run2.md`, `log/W1-50-lead-run2.json`): test design batch 2 only (DEC-266…270, DEC-318, DEC-319) | Leave the batch on the branch. Implementation lead (engineer, review) only after W1-46 merges |
| W1-25 | `DAEO-rrxp` STANDARD | idle, head `58869523`, 52 tests red. Answers: DEC-317 (wiring done in W1-46's round), DEC-320 (`docs/checkpoints/<ticket>/`; only orchestrator-role sessions run `gov checkpoint`; no guard exception), DEC-321 (stale after 4 h or 20 commits), DEC-279…282 | After W1-46 merges: fresh lead (merge integrate; small test batch for DEC-320/321 if the suite needs it; engineer builds to the DEC-317 convention; verify) |
| W1-34 | `DAEO-egm9` LITE | **lead run 1 RUNNING** (`briefs/W1-34-A5.md`, `log/W1-34-lead-run1.json`); brief names DEC-308 | On DONE: merge, full run, close; unblocks W1-11 |
| W1-16 | `DAEO-lkeb` FULL, heavy | **lead run 1 RUNNING** (`briefs/W1-16-A5.md`, `log/W1-16-lead-run1.json`); carries the token rule fix (DEC-324/325; ticket commit `ab50e7e5`) | Expect packages (interface, hit@5 question set). On DONE: merge, full run, close; unblocks W1-20 |

### Ready, waiting for a slot (critical path first)

- **W1-17** (`DAEO-rxln`, STANDARD, critical path, heavy = 2 slots): ready since DEC-322 answered W1-10 DP-3. Start
  it as soon as two slots are free. Its brief: DEC-322 (tests build their own store), W1-15's filter, DEC-289.
- **W1-13** (`DAEO-w616`, FULL) and **W1-14** (`DAEO-w9l3`, STANDARD): ready since W1-09 and W1-12 closed. Check
  their `allowed_paths` don't overlap each other or a ticket in flight. Briefs: DEC-307 (the `specification` key;
  W1-12 to W1-14 write it), DEC-302/305, **DEC-326: DEC-305 supersedes G-08's `feature-readiness.md`**, the W1-12 and
  W1-09 residuals in `bootstrap.md`.
- **W1-33** (role definitions): after W1-46 closes. **W1-11**: after W1-34. **W1-28** (gov pause): deps W1-02,
  W1-07, W1-09 closed — check its paths against W1-46/W1-50 (guard files) before starting.

### Owner queue

- **Nothing is open with the owner.** Told in this turn's final message: W1-49 closed (DEC-250); digest of delegated
  DEC-325 and DEC-326; W1-17 ready and next.
- One slip told to the owner: I listed `~/gov-os-workbench/s0b2/out/` once (file names only; DEC-198 and DEC-310 say
  exact paths only).

### Notes to carry

- W1-30's brief: `gov close` reads a vendored skill's version from `vendored.yaml` (DEC-262).
- W1-27's test design: the disabled `code_intelligence` form (DEC-265); the doctor check of the vendored `tk`
  (DEC-296); `gov rebuild` wired to `gov.store.load` (DEC-275), and DEC-322 is revisited then.
- W1-26: new KPI line, the CIT-E link check [CAP-30.e] (`b7938555`, DEC-309); `.gov-runtime/scratch/` counting as a
  store for the secrets check (W1-15 residual).
- DEC-277: before any real record uses `evidence_for`, `tests`, `generates`, `validates`, a product-spec gap worker
  checks them against the archived Framework §11.2.
- W1-46's worktree-commit question (can a launched session in a linked worktree commit) is in its run 2 brief;
  leads switch to `gov launch` only after it is answered.
- At W1-46's close: update W1-08's `systems` snapshot note if the roster changed.

(Earlier resume blocks are in `resume-block-history-2026-10-04.md` in this folder.)

