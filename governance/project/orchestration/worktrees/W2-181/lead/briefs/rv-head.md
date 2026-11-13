# Review 1 of W2-181 (DAEO-ywb5), a test revision of W2-157's F4 path case: a fresh, read-only LITE review

Budget: projection 3 USD.

You are a fresh, read-only independent reviewer (role `independent-auditor`, class C1, Opus at effort high, RUBRIC-2). You read everything and change nothing. You probe the head of `/home/usain/gov-os-worktrees/W2-181` against the ticket's KPI lines S1, F1 and F2. LITE profile: one round.

## Step 0, before any work: the sandbox check, reported first in your return
(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-ywb5','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` (both in `/home/usain/gov-os-worktrees/W2-181`) must work.
If (a) wrote the file or (b) failed, stop there and return. Then: `printenv GOV_ROLE GOV_TICKET` (expect `independent-auditor`, `DAEO-ywb5`).

## The head you probe
`499543a836d3` on branch `w2/W2-181`. `git -C /home/usain/gov-os-worktrees/W2-181 rev-parse HEAD` must begin with it **at your start and at your end**; if it differs, stop and say so. Base: `1f626332fde0` (the merge-base with `w2/integrate`). The change: one independent test designer commit, `120474643433` (Sonnet high), merged by the lead with `--no-ff` (`499543a836d3`). `git -C /home/usain/gov-os-worktrees/W2-181 diff --name-only 1f626332fde0...HEAD` should list only `tests/acceptance/W2-157/test_w2_157_nothing_else.py` and `tests/acceptance/W2-157/README.md`.

## The defect the revision answers (facts)
W2-157's `test_f4_the_branch_changes_only_the_tickets_allowed_paths` diffed whatever branch the suite ran on against its
merge-base with `w2/integrate` and judged the names against **W2-157's own** ticket paths (`.tickets/DAEO-ozyt.md`). So it
was red on every later ticket's branch that changes other paths (the next in `src/gov/resources/` is W2-121c) and on the
merge queue's candidate merge of such a ticket (a detached HEAD); W2-157 itself was ejected from a batch at 07:46 on the
same form (DECIDED-NOT-DONE row 171). W2-180 (DAEO-weh2) fixed W2-170's F5 and W2-173's F3/F4 the same way; this is the
last such case found on integrate. The ruling: the case judges only `w2/W2-157` and is skipped, with its reason named
(the branch found, or "detached HEAD"), on any other branch, a candidate merge, `w2/integrate` or a clone's checkout.

## What you judge
- The ticket `/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-ywb5.md`: S1, F1, F2, non-goals. Sources DEC-866 (the Rewrite-Reason), DEC-253, DEC-966, DEC-989: read each by id in `/home/usain/gov-os-worktrees/W2-181/docs/DECISION_REGISTER.md`.
- `tests/acceptance/W2-157/test_w2_157_nothing_else.py` (`judge_f4_paths`, `allowed_paths`, the real case and the six planted cases) and the README's changed lines; `w2_157_support.py` (`ROOT`, `SAFE_PATH`) as context. The form it copies: `git -C /home/usain/gov-os-worktrees/W2-181 show w2/W2-180:tests/acceptance/W2-170/test_w2_170_f5_paths.py`.
- The questions: on `w2/W2-157`, is the judgement exactly the earlier one (same base, diff, allowed set from the ticket's `allowed_paths` with comments dropped, fnmatch matcher, the acceptance folder prefix, asserts), so a change outside the paths still fails (F1)? Is every other checkout skipped with its reason, never red and never passed silently (S1)? How is the branch read (from the repository the test file sits in, not the current directory or an environment variable)? Do the planted cases really prove each outcome (fail on w2/W2-157 with an outside path; pass with an inside one; skip on w2/W2-121c, on a detached candidate merge and on w2/integrate)? Are the S5 cases in the file unchanged? Does the commit carry `Task: DAEO-ywb5`, `Implements:` from the ticket's sources and a `Rewrite-Reason:` naming this ticket?
- **Out of this review:** W2-157's code under test, the other cases of the folder (unchanged), other tickets' path cases (the ticket's non-goal), and anything that needs a deliberate construction: a row, not a round.

## What the lead ran (do not re-run these)
- td-1's folder run of `tests/acceptance/W2-157`: 121 passed, 1 skipped (the real F4, on `w2/W2-181-tests`: "F4 judges only the branch w2/W2-157; this is the branch w2/W2-181-tests: not judged here"); its scratch mutation (branch check removed) turned the three skip cases red.
- The lead's `gov accept W2-181` on the head: 121 passed, 1 skipped, 0 failed (record `/home/usain/gov-os-worktrees/W2-181/.gov-runtime/scratch/lead/log/accept-1.txt`).
- The lead's `lead_verify` on the head (record `/home/usain/gov-os-worktrees/W2-181/.gov-runtime/scratch/lead/log/verify/summary.txt`) and its re-run of eight timing-sensitive unit cases alone (`.../lead/log/rerun-reds.txt`).
- A clone check under `/tmp`, the head checked out as `w2/W2-157` (clean, then with a change outside its paths), as `w2/W2-121c` and as a detached candidate merge: record `/home/usain/gov-os-worktrees/W2-181/.gov-runtime/scratch/lead/log/clone-check.txt` (read it).

## How you work
- Read with the Read and Grep tools; one simple command per Bash call; no `cd … &&` chains (use `git -C` or full paths); no here-documents, backticks or `$(…)`; anything longer goes in a script file under your sandbox's TMPDIR, run by its path. **`gov retrieve` is not available in your sandbox** (DEC-1064/1065): if a search does not answer, or your answer may be incomplete, search once more in your own, different words with Read and Grep; then answer from both, or say "not found".
- **Re-run nothing the lead ran.** Run code only to probe a finding: you may import `judge_f4_paths` and call it on planted `git init` repositories under your sandbox's TMPDIR; every Python process with `PYTHONDONTWRITEBYTECODE=1`, `PYTHONPATH=/home/usain/gov-os-worktrees/W2-181/src` per command, `HOME` an empty folder under your TMPDIR, no network, no real embedder or model. Any pytest goes through `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest … -p no:cacheprovider -o tmp_path_retention_policy=failed` with `TMPDIR` outside the repository and outside ~/gov-os-runs and `PYTHONUSERBASE=/home/usain/.local`.
- **You write nothing in any tree.** `git -C /home/usain/gov-os-worktrees/W2-181 status --porcelain` must be empty when you finish. Clean your TMPDIR as you go. Budget: 2 GB and 100,000 files and folders (DEC-898); report `du -sh` and `du -s --inodes` of your TMPDIR in `evidence`.
- **Read refusals (DEC-849):** take a refusal, never look for another form. Count the refusals you met in your return.
- **Protected material (DEC-820, DEC-1097):** never read secrets or keys; never open or list the real sets root `~/gov-os-eval` or the real run folders `~/gov-os-runs`; never read or name the qualification oracle; never write in `~/gov-os-workbench`.
- **Row W2-L423's rule (DEC-911):** write commit hashes as 12 digits, never the full 40, except the one `probed_commit` line, and never write the keywords of the secrets rule that takes a bare 40-hex string; call it "row W2-L423's rule".
- **Refused twice for the same call: stop and say so; no third try.** Never work around a refusal.
- Estimate: about 15 minutes.

