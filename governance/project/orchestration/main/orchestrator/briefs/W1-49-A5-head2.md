You are the ticket lead for ticket `DAEO-32n6` (`W1-49`, "Light auto-resume hooks"), profile FULL, working only in the worktree `/home/usain/gov-os-worktrees/W1-49` on branch `w1/W1-49`. You run the ticket loop for this one ticket. Its implementer is an engineer (brief A2). The owner gave this ticket priority.

## State of this ticket

- An earlier lead ran the test design: head `829f8a37`, 62 tests (9 `local_only`), red for the stated reasons. Its checkpoint is `.gov-runtime/scratch/lead/CHECKPOINT.md` in this worktree; read it. It returned three packages. Two are decided by the main orchestrator as recommended, and the suite already encodes them. They are recorded on `w1/integrate`, which this branch does not contain; **do not merge `w1/integrate` into this branch.** In full:
  - **DEC-258 (DP-1):** a hook can check and block, not write the checkpoint's content. The checkpoint is current when its file is at most 30 minutes old. On a manual compaction over a checkpoint that is not current, the hook blocks (exit 2) and says why. On an automatic compaction it lets it through and tells the user, and the SessionStart injection after it says `CHECKPOINT NOT CURRENT` with the path.
  - **DEC-259 (DP-2):** the two hooks act only when `GOV_ROLE` is `orchestrator`. A worker session gets no injection and is not blocked. An unset `GOV_ROLE` is not the orchestrator.
  - **DP-3 (the prompt path for a lead) is with the owner.** The suite stands as written (in a worktree: the lead checkpoint's path and its RESUME HERE section only). Build to the suite. If the owner chooses otherwise, one assertion and a few lines follow later.
- Settled facts for Claude Code 2.1.288, from the earlier designer: `"CLAUDE_CODE_AUTO_COMPACT_WINDOW": "300000"` in the settings `env` key sets the auto-compact window, so KPI line 3 has no residual; a SessionStart output field is capped at 10,000 characters; `claude -p "/compact" --resume <id>` forces a compaction headless.
- `.claude/settings.json` carries the held-out deny line: nobody reads the file aloud, prints it or diffs it (`git diff --stat` only). The engineer changes it with a short script that loads the JSON, adds the hook registrations and the env key, and writes it back; nothing else in the file changes, and the existing PreToolUse, PostToolUse and PostToolUseFailure registrations stay exactly as they are.

## What you do, in order

1. **Engineer** (brief A2, fresh), to the suite as it stands. Keep it small (estimate 120 LOC, proportion rule DEC-135). A hook failure must not stop a session from starting and must not touch the guard hooks.
2. **Verify** every suite and the validator. The 9 `local_only` cases start one real short session: run them in the background. The W1-08 and W1-46 suites on this branch are red from their own tickets; confirm that and report them apart.
3. **Reviewer** (brief A3): besides its own probes, a checkpoint with no RESUME HERE section, a missing checkpoint, a checkpoint whose section is larger than the cap, a main tree that is not a git repository, a hook that raises (the session must still start; the guard hooks must not fail open), and that the guard hook files and registrations are unchanged by this ticket. Findings that could lose work or make the guard fail open are fixed (a test batch first, as described behaviours, then a fresh engineer); the rest are residuals.
4. Return DONE with the whole ticket's summary. Learning metrics so far: KPI disputes 3 (DP-1 to DP-3).

