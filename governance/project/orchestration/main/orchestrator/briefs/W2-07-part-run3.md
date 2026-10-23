You are the ticket lead for ticket `DAEO-r9ss` (`W2-07`, "gov close by ticket class; the commit gates before any test; complete, tracked repair tickets; a share for every close"), profile STANDARD, working only in the worktree `/home/usain/gov-os-worktrees/W2-07` on branch `w2/W2-07`.

**This is run 3,** after your run 2's PACKAGES (P-W2-07-T2, P-W2-07-T3). `git log --oneline -1` must show `d2eee219`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it. Read your own `.gov-runtime/scratch/lead/CHECKPOINT.md` first.

## The decisions (on `w2/integrate`, which you merge first)

- **P-W2-07-T2 (a), DEC-908 (delegated):** your test designer's batch gains the 14 W1-30 cases, each with a `Rewrite-Reason:` naming its decision, and no other expectation lowered:
  - **8 in `test_w1_30_context_failures.py`,** to DEC-868 item 3: refused at once by the pre-close `gov check`, naming context-reproducibility, uncounted;
  - **5 to DEC-868 item 1 (b) and KPI 5** (the check runs on every close, and the record states it): `test_w1_30_governance_checks.py` ×2, `test_w1_30_r8_commits.py` ×2, `test_w1_30_r13_installed_skills.py` (refused naming core-authority);
  - **1 to KPI 10 (W2-M252):** `test_w1_30_iteration.py::test_each_refusal_opens_repair_ticket`.
  - DEC-455, DEC-480 and DEC-454 are marked changed for these parts.
- **P-W2-07-T3: decided by DEC-906, not an `accepted_reds` entry.** W1-01's history case and its integration-merge case are a known red until W2-70 merges; W2-70 revises them to read an exact-commit exemption list. **Report them by name as known, change nothing for them, and do not let them stop your DONE.**
- **DEC-905:** every full run passes `-o tmp_path_retention_policy=failed`, under `flock /tmp/gov-os-verify.lock`; the commands are in the common brief below. Your run 2 peaked at about 5.25 million inodes without it; this run should stay far below 1,000,000.
- **Row W2-L416 (DEC-908):** in W1-30's fixture, repeated closes pass without a fresh checkpoint after the close's own repair-ticket commit. If your checkpoint gate can take it with a small change inside your paths, do. Otherwise name it in your return; it then goes to W2-24.
- Your run 2's temp folder is removed. Name this run's folder and its size in your return.

## This run's order

1. **Merge `w2/integrate` into this branch, in one Bash call, with its trailers** (`Task: DAEO-r9ss`, `Implements: DEC-908`, `Role: orchestrator`, `Co-Authored-By`). The tree must equal git's own merge.
2. **Test designer round 3:** a fresh independent test designer, launched sandboxed, `--effort high`, on exactly the 14.
3. **Check:** run W1-30, W2-53, W2-01, W2-07 and `tests/unit/close`, each in its own process. All green apart from W1-01's known cases.
4. **Re-verify** in the close's form under the lock, with the retention option: rebuild, collection, `gov check`, the full parallel run and the serial-only run.
5. **Return DONE.** The orchestrator merges this ticket first, before W2-66.

**Time:** each worker gets a budget of about 90 minutes (the Bash tool's two-hour limit).

---
