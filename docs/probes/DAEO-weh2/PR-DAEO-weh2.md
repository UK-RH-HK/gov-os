---
type: probe
task: DAEO-weh2
reviewer_session: ecc7954f-bc80-4434-80f4-42135b62d88e
implementer_session: 64909468-8787-4179-a0b0-7ea52ce69641, 622b2f28-a79e-470e-967c-58151c382c96
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 0d98914dc37f3705beed02d72d98500ea9e48fd4
decisions_applied: [DEC-866, DEC-253, DEC-966, DEC-989]
---

# Probe record: W2-180 (DAEO-weh2), the LITE review of the branch-scope revision of W2-170's F5 and W2-173's F3/F4 path cases

- **What was probed.** Head `0d98914dc37f` of `w2/W2-180`, against base `6c9a5bb525ee`, the merge-base with `w2/integrate`, which holds the ticket's "Widened" section. It holds two independent test designer commits, each merged by the ticket lead:
  - `e3ff31fc5f87` (td-1, session `64909468-8787-4179-a0b0-7ea52ce69641`): W2-170's `test_f5_the_branch_changes_only_paths_the_ticket_allows` now goes through `judge_f5_paths(root)`. It judges only when HEAD is `refs/heads/w2/W2-170` and is skipped, with its reason, on any other checkout. Six planted cases go with it.
  - `56f401a86c90` (td-2, session `622b2f28-a79e-470e-967c-58151c382c96`): W2-173's F3 and F4 now go through `judge_f3_paths` and `judge_f4_paths`, which judge only on `w2/W2-173`. Planted cases go with them.
  - Both READMEs are updated. Both commits carry the Rewrite-Reason (DEC-866).
  - Both designers were Sonnet at effort high, class C1.
- **Who probed.** A fresh read-only reviewer, role `independent-auditor`, session `ecc7954f-bc80-4434-80f4-42135b62d88e`, Opus at effort high, class C1, 2026-11-12. It was started through `gov launch` under its OS sandbox, and the ticket lead commissioned and judged it.
  - The lead's tripwire shows no change in this ticket's trees during its session, and `git status --porcelain` stayed empty.
- **Step 0.**
  - The write outside the worktree was refused: read-only file system.
  - `git hash-object -w` and `git update-index --refresh` worked.
  - `gov.__file__` = `/home/usain/gov-os-worktrees/W2-180/src/gov/__init__.py`.
  - One Write-tool refusal for a probe script under TMPDIR, taken and not retried. The verdict does not rest on it.
- **The lead's runs beside it, all on `0d98914dc37f`.**
  - Clone check (`.gov-runtime/scratch/lead/log/clone-check.txt`): a clone under `/tmp`, with the head checked out three ways.
    - As the branch `w2/W2-170`: F5 fails on `tests/acceptance/W2-173/*` (outside W2-170's paths), and F3 and F4 skip with their reason.
    - As `w2/W2-173`: F4 fails on `tests/acceptance/W2-170/*`, F3 passes, and F5 skips with its reason.
    - Detached: all three skip with "this is a detached HEAD".
    - The clone is removed.
  - `gov accept W2-180`: pass, 184 passed, 0 failed, 1 skipped (the real F5 on `w2/W2-180`).
  - `lead_verify`: RED, 4,062 tests, 6 failed. All six are W2-96's shared base reds:
    - four fail on `w2/integrate`'s head `d02e957ba35a` (`.gov-runtime/scratch/lead/log/base-red.txt`);
    - the other two pass when run alone on this head (`rerun-alone.txt`, load-sensitive).
  - The designers' folder runs: W2-170 184 passed, 1 skipped; W2-173 91 passed, 2 skipped. The skips are the real path cases on the tests branch.
- **Threat model (DEC-801, DEC-808).** The review judges against ADR-0001's threat model: honest agent mistakes and plausible accidents in ordinary work, not deliberate adversaries.
- **Verdict: pass.** Classification (DEC-809): yes and fails open or loses work 0; yes and other 0; rows 2 (RV1, RV2). The lead's judgement agrees:
  - RV1 is a row. If the judge itself were later revised to skip on the own branch, the planted "must fail" and "must pass" cases would only skip, not go red. This needs a further wrong revision, which would itself be reviewed.
  - RV2 is a row. On a reopened W2-170 or W2-173, the queue's candidate-merge run no longer judges the paths. This is the CTO's ruling, and both tickets are closed.
  - Both are returned to the orchestrator as residuals.

## The reviewer's record (verbatim)

task: DAEO-weh2
decisions: DEC-866, DEC-253, DEC-966, DEC-989, DEC-801, DEC-808, DEC-1010, DEC-1014
probed_commit: 0d98914dc37f (the full id is in the front matter; the lead shortened it here under row W2-L423's rule)

**Scope:** S1, F1, F2 and the ticket's "Widened" section. Files: `tests/acceptance/W2-170/test_w2_170_f5_paths.py`, `tests/acceptance/W2-173/test_w2_173_unchanged.py` and the changed lines of both READMEs. Out of scope: the code under test, the other cases in both folders, and other tickets' path cases.

**Method:**
- **Reading:** the full diff and the lead's clone-check record.
- **Probe run 1:** I set the F5 module's own-branch name to a wrong value and ran its planted "fails" case.
- **Probe run 2:** in planted repositories:
  - each own branch (`w2/W2-170`, `w2/W2-173`) checked out in a linked worktree, with a change outside the ticket's paths: F5, F4, and F3 with a forbidden path;
  - W2-173's planted F3 and F4 "fails" cases with a wrong own-branch name;
  - W2-173's planted skip cases with the branch check removed.
- Seven repositories in all, each built once. Everything is removed.

**Probed and found sound:**
- **Same judgement on the own branch (F1):**
  - **W2-170:** after the new branch check, `judge_f5_paths` keeps the old steps line for line: the `w2/integrate` and ticket-file skips, the merge-base with integrate, the three-dot `--no-renames` diff, `allowed_paths` plus the acceptance folder, `gov.close.select.match` and the same assert. The real case calls it with `W.TREE`.
  - **W2-173:** `branch_names`, `ticket_allowed_paths`, the forbidden list, `OWN_RECORDS` and the fallback to dac438772 only gained a `root` parameter. The real cases pass `support.TREE`, which is the same repository root.
  - **Live check:** the lead's clone check shows the judgement working. Checked out as `w2/W2-170`, F5 goes red on W2-173's files; checked out as `w2/W2-173`, F4 goes red on W2-170's files. In my probes, a linked worktree on each own branch was red for F5, F4 and F3, so a ticket's ordinary worktree does not trigger the skip.
- **Every other checkout skips with its reason (S1):** a detached HEAD skips with "this is a detached HEAD". Any other branch skips naming the branch it found. Both ticket-file and integrate-missing skips are kept. The clone check confirms the detached case gives three named skips. Nothing passes silently on another checkout: the skip comes before any diff.
- **How the branch is read:** with `git -C <root> symbolic-ref -q HEAD`, where root is the test file's own repository (`HERE.parents[2]`). It never uses the current directory or an environment variable. W2-173's git calls run in a clean environment (`GIT_ENV`). W2-170's inherit the environment, as they did before.
  - Another spelling of the own name, such as a lowercase `w2/w2-170`, would skip. The tooling makes `w2/W2-NNN` branches, so this is not ordinary work.
- **Planted cases:** they call the same `judge_*` functions as the real cases. A revision that judged everywhere is caught: the other-branch, detached and integrate cases go red with "DID NOT RAISE Skipped" (probed for F3). A revision that skipped everywhere is not caught as red (RV1).
- **Nothing else loosened (F2):** both files change only the path cases and add planted cases. The S5 case in W2-173's file is unchanged. The branch diff lists exactly the four allowed paths. Both test-designer commits carry the Rewrite-Reason trailer (DEC-866).
- **"Widened" is answered:** W2-173's F3 and F4 now judge only `w2/W2-173`.

**Findings**

- **RV1 (rows S1/F1, `scope: in`):**
  - *What was done:* I set the own-branch name to a wrong value, as a later revision might by mistake. Then I ran the planted "branch with a change outside its paths fails" cases for F5, F4 and F3.
  - *What happened:* each case was **skipped** with the judgement's own reason. None went red. The real case skipped too, so the folder would be green with three more skips.
  - *What should have happened:* a planted "must fail" or "must pass" case should fail when the judgement skips on the planted own branch.
  - Ordinary work: no, because at this head the planted cases fail and pass as required. It needs a further, wrong revision of the judge, and that revision would itself be reviewed.
  - Consequence: other (a weaker guard against a future regression, not a breach let through today).
  - *Would reverse it:* a run showing that a skip inside those planted cases ends red, for example from a conftest hook or a skip-count gate on the folder.
- **RV2 (row S1, `scope: out`):**
  - *What was done:* I read the revision against DEC-989 item 2, under which a ticket merges and closes on the queue's run on the candidate merge, which is a detached HEAD.
  - *What happened:* if W2-170 or W2-173 were reopened, their own path cases would skip on that run. Only a run on the ticket's own branch, such as the lead's verify, judges them. A run during a rebase on the own branch also skips, because HEAD is detached.
  - *What should have happened:* this is what the CTO's ruling asks for ("a candidate merge" is to be skipped). It is recorded as a row, not a defect.
  - Ordinary work: no, because both tickets are closed (DAEO-61vm, DAEO-qz4p), and on a reopen the lead's verify runs on the branch, where the judgement works.
  - Consequence: other.
  - *Would reverse it:* a record showing a ticket's own verify run only on a detached or cloned checkout.

**Classification:** 0 yes/fails open or loses work; 0 yes/other; 2 rows (RV1, RV2).

```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass", "findings": [{"id": "RV2", "scope": "out", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "F1", "verdict": "pass", "findings": [{"id": "RV1", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "F2", "verdict": "pass", "findings": []}]}
```
