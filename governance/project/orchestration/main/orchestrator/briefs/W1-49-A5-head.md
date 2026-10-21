You are the ticket lead for ticket `DAEO-32n6` (`W1-49`, "Light auto-resume hooks"), profile FULL, working only in the worktree `/home/usain/gov-os-worktrees/W1-49` on branch `w1/W1-49`. You run the ticket loop for this one ticket. Its implementer is an engineer (brief A2). The owner gave this ticket priority.

## State of this ticket

- New today, by owner decision DEC-248; read it, with DEC-208, DEC-237, DEC-250, DEC-025 and the Contract's CAP-37 with its covers item CAP-37.g. No acceptance tests yet; nothing implemented.
- What the hooks serve: the main orchestrator's checkpoint is `.gov-runtime/scratch/orchestrator/CHECKPOINT.md` in the main tree, with a section headed "RESUME HERE", and its prompt is `governance/project/prompts/w1-orchestrator.md`. A ticket lead's checkpoint is `.gov-runtime/scratch/lead/CHECKPOINT.md` in its worktree. `.gov-runtime/` is not tracked, so tests build stand-in checkpoints in a temporary project.
- The existing hooks (`template/governance/kernel/hooks/pretooluse.py`, `posttooluse.py`) and their registration in `.claude/settings.json` show how a hook is wired here (`$CLAUDE_PROJECT_DIR`). This ticket does not change them.
- `.claude/settings.json` is in the allowed paths for the hook registration and any env key only. It carries the held-out deny line: nobody reads the file aloud, prints it or diffs it (`git diff --stat` only). The engineer changes it with a short script that loads the JSON, adds the keys and writes it back, as W1-47's engineer did; tests read it by loading the JSON and looking only at `hooks` and `env`.
- W1-29 later replaces these two hook files with the full session hooks; keep them small (estimate 120 LOC, proportion rule DEC-135).

## Points the test designer must settle from the Claude Code documentation or by trying, not by guessing

- KPI line 1, "ensures the checkpoint is current": a hook is a command, not the model. What a PreCompact hook can actually do here (check freshness, block or warn, write a stamp) and what "current" is measured against is likely to need a decision package. Return it with a recommendation.
- KPI line 2, "the hook's size cap": the cap Claude Code puts on a SessionStart hook's injected context, as documented for the pinned version (2.1.288); the test asserts the injection stays inside it and still carries the prompt path and the whole RESUME HERE section, or says what is cut and how.
- KPI line 3: an acceptance test proves whether the auto-compact threshold can be configured in the pinned Claude Code (a settings key or an env key in `.claude/settings.json`). If it can't, the residual is returned to the main orchestrator for `bootstrap.md`, and the test asserts the residual.
- KPI line 4 needs one short real headless session, `local_only`, on the cheapest model with a turn limit, as DEC-232 did for the launcher: a stand-in checkpoint with invented tickets, decisions and loop counts, a forced compaction, then a next action that names them. If a forced compaction can't be triggered in a headless session, that is a package.
- No test and no worker reads the real orchestrator checkpoint for its content; it holds loop counts.

## What you do, in order

1. **Test design** (brief A1, a fresh designer, profile FULL, DEC-221).
2. **Check red** yourself.
3. **Engineer** (brief A2, fresh).
4. **Verify** every suite and the validator. The W1-08, W1-46 and W1-18 suites on this branch are red from their own tickets, which are in flight elsewhere; confirm their failures name only their own missing deliverables, and report them apart.
5. **Reviewer** (brief A3): besides its own probes, a checkpoint with no RESUME HERE section, a missing checkpoint, a checkpoint larger than the cap, a worktree with both a lead checkpoint and none, and a hook failure (it must not block the session from starting, and must not make the guard hooks fail open).

