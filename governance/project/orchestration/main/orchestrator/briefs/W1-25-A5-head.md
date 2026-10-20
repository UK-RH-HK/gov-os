You are the ticket lead for ticket `DAEO-rrxp` (`W1-25`, "gov checkpoint"), profile STANDARD, working only in the worktree `/home/usain/gov-os-worktrees/W1-25` on branch `w1/W1-25`. You run the ticket loop for this one ticket. Its implementer is an engineer (brief A2). STANDARD has no reviewer step.

## State of this ticket

- No acceptance tests yet; nothing implemented. `allowed_paths`: `src/gov/checkpoint/**`, `tests/unit/checkpoint/**`, `template/governance/kernel/checks/fresh-agent-reconstruction*`.
- Its dependencies are closed: W1-07 (the `gov` CLI skeleton and its command registry) and W1-08 (the checkpoint schema and template under `template/governance/kernel/`; note the W1-08 residual in `governance/project/bootstrap.md` that the checkpoint record has no type-specific fields yet, and that older schemas exist under `schemas/records/`, the checkpoint one among them). Read the Contract's CAP-37 (a, b, c, f), CAP-13.b, CAP-20.a, CAP-38.b, and DEC-025, DEC-150, DEC-156, DEC-208.
- A neighbouring ticket in flight, W1-49 (light auto-resume hooks, DEC-248), builds the PreCompact and SessionStart hooks and owns those hook files; W1-29 builds the full session hooks later. This ticket builds `gov checkpoint` and its watchdog, not hooks. Do not touch `template/governance/kernel/hooks/` or `.claude/settings.json`.
- Things the test designer must look at and not guess; each is a decision package if the sources leave it open:
  - `gov checkpoint` is one of the commands W1-07 reserved: its `NOT_IMPLEMENTED` case in `tests/acceptance/W1-07/test_w1_07_registry.py` is revised with the reason "planned: command implemented" (DEC-190), counted apart from rewrites. `src/gov/cli/**` is not in this ticket's paths: see how the registry dispatches to a command's module, and return a package if the command cannot be wired from inside `src/gov/checkpoint/**`;
  - "the carried schema": which schema a checkpoint conforms to (W1-08's under `template/governance/kernel/schemas/`, or the older one under `schemas/records/`), and what "an input by id with its hash" requires;
  - where a checkpoint is written, given that `.gov-runtime/` outside `scratch/` is closed to worker roles and that the orchestrator's checkpoint lives in `.gov-runtime/scratch/orchestrator/` "until W1-25" (WBS rule on the orchestrator write scope);
  - "at every ticket transition, compaction and stop": which of these this ticket can show without the hooks (W1-29) and without `gov close` (W1-30);
  - `--watch`: the policy values (age, commits since, context utilisation) and where they come from; how context utilisation is known without a harness hook;
  - "a fresh session resumes … from the checkpoint alone" and the fresh-agent-reconstruction family check: whether a real short headless session is needed (`local_only`, cheapest model, turn limit, as DEC-232 did) and how the check is registered before `gov check` exists (W1-26, DEC-187).
- No test and no worker reads the real orchestrator checkpoint for its content; it holds loop counts.

## What you do, in order

1. **Test design** (brief A1, a fresh designer, profile STANDARD, DEC-221: every KPI line's success and failure plus the key edge cases; every covers id gets at least one test).
2. **Check red** yourself.
3. **Engineer** (brief A2, fresh). Estimate 180 LOC; proportion rule DEC-135.
4. **Verify** every suite and the validator. Suites of tickets still in flight elsewhere (W1-46, W1-49, W1-50, W1-10, W1-15) may be red on this branch from their own missing deliverables; W1-50 is red by design (26 failed, 17 passed). Confirm that and report them apart.

