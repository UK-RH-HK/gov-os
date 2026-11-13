## Review 1 of W2-180 (DAEO-weh2): READY, no blocking finding

The revision does what the CTO's ruling asks. On W2-170's own branch the F5 case still judges exactly as before. So do W2-173's F3 and F4 cases on theirs. On every other checkout they skip and name the reason. I found two non-blocking rows for Wave 3 and nothing that justifies a second round.

```
task: Fresh read-only LITE review of W2-180 (DAEO-weh2) head 0d98914dc37f against S1, F1, F2 and "Widened"
status: DONE: one round; S1, F1, F2 pass; two rows, nothing blocking
work_completed: Step 0 sandbox check; read the diff from 6c9a5bb525ee to 0d98914dc37f, the ticket, the four source decisions by id, both support modules, the lead's clone-check record and the commit trailers; planted git repositories in TMPDIR and called the real judgement and planted-case functions (two probe runs)
files_changed: none
evidence: Step 0: (a) writing /home/usain/gov-os-worktrees/.sandbox-trial-DAEO-weh2 failed with "OSError: [Errno 30] Read-only file system"; (b) `echo sandbox-trial | git hash-object -w --stdin` returned 1ae28402a109 and `git update-index --refresh` succeeded; GOV_ROLE=independent-auditor, GOV_TICKET=DAEO-weh2. Head at start and at end 0d98914dc37f. gov.__file__ = /home/usain/gov-os-worktrees/W2-180/src/gov/__init__.py. Session id ecc7954f-bc80 (from the tool-results path). TMPDIR at peak about 2.3 MB and 530 inodes; after cleanup 20K and 8 inodes. Read refusals met: 1 (the Write tool for a probe script under TMPDIR; I took it and wrote no file). Trailers: e3ff31fc5f87 and 56f401a86c90 each carry `Role: independent-test-designer`, `Task: DAEO-weh2` and `Rewrite-Reason: DEC-866, W2-180 (DAEO-weh2): …`; the lead's merges e63381d7c4.. and 0d98914dc37f carry `Role: orchestrator`, `Task: DAEO-weh2`. Branch diff stat: exactly the four allowed paths (354 lines added, 34 removed).
tests: none run as pytest; two python probe runs on planted repositories (see Method)
discoveries: The planted "fails" and "passes" cases use pytest.raises(AssertionError) or a plain call. pytest's skip exception is not an AssertionError, not even an Exception. So if a later revision skipped everywhere, those planted cases would show as skipped, not red (RV1).
risks: The guard against a skip-everywhere revision is only the folder's skip count (RV1). For a reopened W2-170 or W2-173, the queue's candidate-merge run no longer judges the paths; only a run on the ticket's own branch does (RV2).
lessons: If a planted "must fail" case wraps a function that can skip, it should turn a skip into a failure. Otherwise a regression to "skip always" shows only as more skips.
proposed_decisions: none
unresolved: none
recommended_next_action: Take W2-180 to the queue as READY; file RV1 and RV2 as Wave 3 rows
```

### Probe record

task: DAEO-weh2
decisions: DEC-866, DEC-253, DEC-966, DEC-989, DEC-801, DEC-808, DEC-1010, DEC-1014
probed_commit: 0d98914dc37f3705beed02d72d98500ea9e48fd4

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