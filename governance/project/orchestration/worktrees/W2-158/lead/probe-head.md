---
type: probe
task: DAEO-8a3f
reviewer_session: aa5e31e2-c8a5-4aab-b986-0cd13daab9af
implementer_session: not recorded
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 4916311219bda0a224e6874caf33f093c529f008
decisions_applied: DEC-1052, DEC-1073, DEC-1010, DEC-801
---

# Probe record: W2-158 (DAEO-8a3f) gov check --structural, STANDARD review, round 1

## The lead's judgement

- **Who probed.** A fresh read-only independent auditor (Opus, high, class C2) launched by W2-158's lead through
  `launch_worker.sh` (log `~/gov-os-worktrees/W2-158/.gov-runtime/scratch/lead/log/rev-1.json`, brief
  `.../lead/briefs/rev-1.md`), on head `4916311219bd` of `w2/W2-158` (the ticket's work plus w2/integrate merged at
  0aec6e10c). Round 1 of at most 2 (DEC-1010). The sandbox trial file stayed absent. The tripwire showed changes only
  in other trees (the queue's landing to 010399309d69, W2-115, W2-146 and W2-159 leads), none in W2-158.
- **Verdict PASS.** Every line S1-S5 and F1-F4 passes. 0 blocking, 1 major (F-1), 4 minor (F-2 to F-5); no finding
  fails open or loses work (DEC-801): the pass gates nothing.
- **F-1 (major, S4).** `git diff --name-only <base>..HEAD` with rename detection hides a kernel role, skill or hook
  file moved out of its folder, so portability reads `skipped (no such change)`; the fix is `--no-renames`. A missed
  notice, never a refusal. Not fixed in this ticket: it is a row for the CTO (a one-flag fix with a planted `git mv`
  case; the reference tool `structural_pass.py:184` has the same gap).
- **F-2 (minor, S3/F1).** Under `| head -1` a closed stdout ends the pass with exit 120 and a BrokenPipeError
  traceback, not 0. No gate reads it. A row (catch BrokenPipeError around the prints).
- **F-3 (minor, S5).** Links gets its own full bound after the families, so the worst case is about twice the bound;
  the reading L7 states it. Measured well inside the limit on this repository. A row.
- **F-4 (minor, S1).** A declaration with no `family` and an id starting `skill-regression` counts as skills (the
  engineer's recorded reading 3). Today's declarations all carry the field. A row.
- **F-5 (minor, S5).** Settled: the lead's main-tree measurement is in `docs/changes/W2-158-evidence.md` (9.37 s on
  010399309d69 without a base; the reviewer's 19.66 s with a base on a clone of the head).
- **The lead's verify of this head.** `lead_verify.sh`: 4220 tests, 6 failed, all six W2-96 signal cases in
  `tests/unit/accept/test_w2_96_{run2,review3,review4}.py`; re-run alone on this head and on w2/integrate's head
  010399309d69: the same 17 of 20 parametrised cases fail on both (a shared base red, not this ticket's; logs
  `.../lead/log/basered-{head,integrate}.txt`). Every W2-158 case green. `gov accept W2-158`: pass, 61 passed, 0
  failed, all nine KPI lines.
- **Judgement: pass.** No new round. F-1 to F-4 go as rows to the CTO.

## The reviewer's record (as returned)

