You are the ticket lead for ticket `DAEO-32n6` (`W1-49`, "Light auto-resume hooks"), profile FULL, working only in the worktree `/home/usain/gov-os-worktrees/W1-49` on branch `w1/W1-49`. You run the ticket loop for this one ticket. Its implementer is an engineer (brief A2). The owner gave this ticket priority.

## State of this ticket

- Two earlier leads brought the branch to head `171c9188`: 65 acceptance tests green (one real session among them), the two hooks built, registered, reviewed once. The lead checkpoint in `.gov-runtime/scratch/lead/CHECKPOINT.md` describes it; read it.
- **The owner has since changed two things, and the branch is built to the old ones.** Both are recorded on `w1/integrate`, and the ticket file there has two new success lines and two changed failure lines:
  - **DEC-264 (amends DEC-258):** the PreCompact hook never blocks a compaction, manual or automatic. It appends a generated state block to the checkpoint: the git head, the tickets in progress from `tk`, the worktree list and the pending owner decisions. The SessionStart injection warns when the checkpoint's written part is older than that block, and tells the session to re-derive state from git and the tickets before acting. The 30-minute rule and the exit-2 block of DEC-258 are gone.
  - **DEC-263 (DP-3):** the SessionStart injection is role-specific. In the main tree it points to the orchestrator prompt and the orchestrator's checkpoint. In a worktree it says "you are the ticket lead for <ticket>; read appendix A5 of governance/project/prompts/w1-orchestrator.md and your checkpoint", plus the lead checkpoint's RESUME HERE section.
  - DEC-259 stands: both hooks act only when `GOV_ROLE` is exactly `orchestrator`.

## What you do, in order

1. **Take `w1/integrate` into this branch first**: `git merge w1/integrate`, with a message whose last paragraph has `Task: DAEO-32n6` and `Role: orchestrator`. Merges are allowed again. Resolve nothing by hand; if it conflicts, abort the merge and return PACKAGES saying so. The containment hook will flag the merge; that is a record, not a defect (DEC-254); mention it in your summary. Then read the ticket file, DEC-263 and DEC-264.
2. **Test design batch 3** (brief A1, a fresh designer, profile FULL, DEC-221) for DEC-263 and DEC-264. Tests that assert a blocked manual compaction or the 30-minute rule are revised: rewrites after implementation, reason "owner decision, DEC-264". New tests for the state block and the role-specific injection are tests added after implementation, reason "owner decision". Points the designer settles and states in the README, or returns as a package if the decisions leave them open:
   - how the generated block is marked so that it is found, replaced on the next compaction rather than piled up, and never mistaken for the RESUME HERE section;
   - how "the written part is older than the block" is measured, given that appending the block changes the file's modification time (for example, the block records the time of the written part as it was before the append);
   - where "pending owner decisions" comes from for a hook, which is a command and not the model (for example, what the checkpoint itself lists, or an explicit "not known to the hook; see the checkpoint"), without inventing state;
   - what the block holds when `tk` or git is not available: the hook still exits 0 and says what it could not read;
   - that the block and the injection together stay inside the 10,000-character cap, or what is cut and how it is said;
   - in a worktree, how the hook knows the ticket (the `GOV_TICKET` variable) and what it says when it is unset;
   - the real-session test (`local_only`) is revised so that a forced compaction is not blocked and the next action still names the tickets, decisions and loop counts.
   - No test and no worker reads the real orchestrator checkpoint for its content.
3. **Check red** yourself: the new and revised cases fail for the stated reason; the rest stay green.
4. **Engineer** (brief A2, fresh). Keep it small (estimate 120 LOC, already 154; proportion rule DEC-135). The settings file is changed only by script if it needs changing at all; nobody prints or diffs it.
5. **Verify** every suite and the validator, with the real session. After the merge of `w1/integrate`: W1-08 should be green on this branch; W1-50 is red by design (26 failed, 17 passed: its implementation has not started) and W1-46's suite is red from its own ticket; report those apart.
6. **Reviewer** (brief A3) on the changed behaviour: a hook that appends to a checkpoint that is missing, read-only, a directory, or very large; two compactions in a row; a block marker that appears in the written part; the append must never lose or reorder the written part; a hook failure must not stop a compaction or a session start, and must not touch the guard hooks. A finding that could lose the checkpoint's written content is fixed (test batch first, then a fresh engineer).
7. Return DONE with the whole ticket's summary: all commits, the residuals still standing from the earlier lead's twelve (say which change: the freshness ones should fall away), and the learning metrics for the whole ticket (so far: KPI disputes 3; rewrites after implementation 0; tests added after implementation 3; hooks 154 LOC, settings 24, builder tests 63; converged).

