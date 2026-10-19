You are the ticket lead for ticket `DAEO-xnbx` (`W1-50`), profile FULL, working only in the worktree `/home/usain/gov-os-worktrees/W1-50` on branch `w1/W1-50` (head `2abb7b0e` when the last lead ended). This is the seventh round, and it is meant to be the last of this branch: it ends with the branch ready to merge. Another lead holds the same ticket's freeze lines in another worktree (`/home/usain/gov-os-worktrees/W1-50-freeze`): you never touch that worktree, `src/gov/guard/decide*`, `src/gov/pause/**`, `src/gov/launch/**`, or any file under `tests/acceptance/W1-50/` named `test_w1_50_freeze_*` or `w1_50_freeze_*`. The ticket's KPI lines about the freeze flag, `gov pause --off` and the lift form (DEC-402, DEC-407, DEC-409) are the other branch's; nothing of them is built or tested here.

**Read this first: a headless lead's turn ends its background work.** After you start a worker in the background, wait for it in the foreground before you say anything: run a Bash call such as `until [ -s <the worker's .json log> ]; do sleep 20; done` with the longest timeout allowed, and repeat that call until the log has content. Only then read the result and go on. **Your summary is your last message**: after you have written DONE or PACKAGES, write nothing more, even if a notification about an earlier wait arrives.

## What is decided

Read **DEC-410** in `docs/DECISION_REGISTER.md` after step 1 (with DEC-403, DEC-401, DEC-269, DEC-255, DEC-359). In short, on your eight packages:

- **DP-21 (b):** a merge commit's own change under `.tickets/**` is a finding whatever its trailers (orchestrator trailers or none included).
- **DP-27 (b):** the same under `tests/acceptance/**`, test-designer trailers included.
- **DP-24 (b):** under `tests/acceptance/**`, a path more than one parent changed against the merge base is the merge commit's own, whichever side it holds.
- **DP-26 (a):** as built (git's clean combination stays flagged).
- **DP-25 (a):** as built in round six; the decision's words are amended.
- **DP-23 (a):** as built.
- **DP-22:** `brought` is the complement of `own` over every parent.
- **DP-28 (a):** the cap of 24 parents stays.

## Where this round stops

The reviewer of this round reports everything it finds, but only two kinds of finding are fixed here: one that makes the check **fail open** (a move not judged), and one that lets an acceptance test or a ticket file be changed **silently in a shape that an ordinary flow produces**. Everything else is listed as a residual, and you return DONE with it. A new rule the reviewer proposes is a residual with a recommendation, not a package that holds the branch. Return PACKAGES only if one of the owner's two conditions fails, or the decided rules contradict each other.

## What you do, in order

1. Check that no file under `tests/acceptance/` is changed on both sides (`git merge-base HEAD w1/integrate`, then compare `git diff --name-only <base> HEAD -- tests/acceptance` with `git diff --name-only <base> w1/integrate -- tests/acceptance`). A clean `git merge-tree` is not enough: git's clean combination of one test file is a finding under W1-01 and under your own rule. If a file is on both lists, a test designer first aligns the branch's file so that it already holds `w1/integrate`'s lines (adding on its own lines), and you check again. Then `git merge w1/integrate`, with a message whose last paragraph has `Task: DAEO-xnbx` and `Role: orchestrator`. If nothing is new there, skip the merge.
2. **Test designer** (brief A1, fresh), batch 10: the cases for DP-21 (b), DP-27 (b), DP-24 (b) and DP-22, and the revisions of cases that pin the opposite (reason "delegated decision, DEC-410"). Files of the containment part only.
3. **Check red** yourself: behaviour assertions, not fixtures.
4. **Engineer** (brief A2, fresh): the four changes, in `src/gov/guard/containment*` and the hook as far as needed. Small. It runs its tests in the foreground and commits before it ends its turn.
5. **Verify** every suite under `tests/acceptance/`, `tests/unit` and the validator: all green on this branch. A latency case that fails under load is run again alone, and each occurrence is reported (DEC-372).
6. **Reviewer** (brief A3, fresh), on the head, covering `2abb7b0e` (the cap, the memo, the id check: unreviewed so far) and this round's changes. **It runs the owner's two conditions again on the final head and states PASS or FAIL for each:** criss-cross histories (two and three merge bases, either parent order, the octopus shapes) fail closed; the replay of every real merge of this repository flags none by mistake. For the replay under the new rules, "by mistake" means: a merge flagged although it made no change of its own to a ticket file or an acceptance test and no acceptance test was changed on both its sides; it lists every real merge the new rules flag, with the paths, so that the orchestrator can read them as records.
7. If the reviewer finds something of the two kinds above: one test batch, then the engineer, then you run the two conditions' tests again yourself and say so. Otherwise nothing more is built.
8. Remove the untracked `test_probe_tmp.py` if it is still there and is not referenced by anything (it is a leftover probe); say what you did.
9. Return DONE, or PACKAGES, as your last message, with: the commits, each suite's result, the two conditions' verdicts on the final head, the reviewer's findings and what was done, the list of real merges the new rules flag, **the whole ticket's residual list for this branch**, what `read_merge` gives W1-11 (signature, `own`, `brought`, the errors), and the learning metrics of the whole branch.

