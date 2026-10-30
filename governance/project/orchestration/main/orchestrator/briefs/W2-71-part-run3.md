You are the ticket lead for ticket `DAEO-e8f0` (`W2-71`, "The secrets check passes a real commit hash of this repository for row W2-L423's rule only"), profile FULL, working only in the worktree `/home/usain/gov-os-worktrees/W2-71` on branch `w2/W2-71`.

**This is run 3: the repair of its refused close, tests only (DEC-946 item 1, finish before you start).** `git rev-parse --short=12 HEAD` must show `3b69bbd23775`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

**Read first:**
- the repair ticket `.tickets/DAEO-sg6x.md` (in the main tree, `/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-sg6x.md`), and its section "The orchestrator's reading";
- your run-2 checkpoint, `.gov-runtime/scratch/lead/CHECKPOINT.md`;
- the close's refusal: `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/close-queue-20261030-0007/close-DAEO-e8f0.json` (`error.details.red_findings`).

## Why you start now

- **Run 2 is merged** (`cd256641`) and its review passed, but W2-71's close was refused at 02:12 on 2026-10-30.
- **The red is in this ticket's own acceptance test:**
  - `tests/acceptance/W2-71/test_w2_71_keywords_in_parts.py::test_premise_the_list_holds_this_suites_own_files` fails;
  - `written_by_the_branch()` takes `git diff` from `merge-base(HEAD, w2/integrate)`, which is empty in the main tree once the ticket is merged (HEAD is integrate);
  - so the premise can pass only on this branch, never at the close, and its sister test `test_no_file_the_branch_writes_holds_a_keyword_of_row_w2_l423s_rule_whole` checks nothing there.
- **The other red** (`tests/acceptance/W2-54/test_w2_54_time_limit.py::…ends_green_within_its_limit`) is a time limit missed under load. It is the owner's question, not your work. Do not touch W2-54.

## The decisions for this run

1. **Merge `w2/integrate` into `w2/W2-71`** (`git merge --no-ff w2/integrate`, trailers `Task: DAEO-e8f0`, `Implements: DEC-911`, `Role: orchestrator`). The merge must be clean. Any conflict: `git merge --abort` and return PACKAGES.
2. **A fresh independent test designer** (`gov launch`, sandboxed, `--effort high`; its brief must not set `TMPDIR`) repairs the two tests in `tests/acceptance/W2-71/test_w2_71_keywords_in_parts.py` only:
   - The ticket's files come from its own commits: every commit reachable from HEAD whose message carries `Task: DAEO-e8f0`, their changed paths under the suite's folders, and the untracked files as now.
   - This holds on the branch and in the main tree after the merge alike.
   - The premise still requires the suite's own file in the list.
   - The sister test then reads real files in both places.
   - Each changed case carries a `Rewrite-Reason:` naming the refused close (2026-10-30 02:12) and this cause. No expectation is lowered, and no case is removed.
3. **Check it yourself, in both places:**
   - on this branch: the W2-71 suite green;
   - in a temporary clone of `w2/integrate` merged with this branch (under `/tmp/gov-os-lead-W2-71/`, by exact path), with HEAD equal to that merge: the premise and the sister test green;
   - plant one file holding a keyword whole in a ticket commit of the clone, and the sister test goes red. This is the check that the test is not vacuous.
4. **Verification, scoped:** `tests/acceptance/W2-71/` and `tests/unit/secrets_check/` in the close's form, and `pytest --collect-only -q` over `tests`. No full run: no code changes. The nightly rule, the close lock and the 01:00 cut-off of the common brief hold.
5. **No review:** a test-only repair of a FULL ticket whose code is unchanged. Say so in the return; the orchestrator decides whether the close's probe gate needs a note.
6. **Return** DONE (the branch ready to merge, then the re-close), or PACKAGES.

**Running beside you:** W2-84 holds `src/gov/guard/reads.py`; W2-03 holds `src/gov/store/**`, `src/gov/records/**` and `src/gov/decisions/**`; W2-60a holds `src/gov/launch/launcher.py`, `role.py` and `record.py`; W2-61 holds `src/gov/retrieval/measure.py`. Touch none of them.

**Estimate:** about 1.5 hours, about 40 test lines.

**Time:** the test designer gets about 60 minutes.

---
