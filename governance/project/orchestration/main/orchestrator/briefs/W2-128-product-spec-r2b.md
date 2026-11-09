# W2-128 round 2b — the product-spec worker's brief (DAEO-t8mp)

You are a fresh product-spec worker for **W2-128** (`.tickets/DAEO-t8mp.md`). Rounds 1 and 2a are merged.
Read the ticket's body, **"Round 2b"**, in full: it lists this round's work exactly. Then read the review
`governance/project/orchestration/reviews/w2-128-r2a.md` (findings F1 to F5), and the decisions DEC-963, DEC-820,
DEC-508, DEC-525, DEC-1050 and DEC-1052 in `docs/DECISION_REGISTER.md`, by id.

## The work (round 2b only; the ticket's "Round 2b")
1. **F1:** `template/.rulesync/subagents/orchestrator.md` takes the kernel role's retired-briefs line (the kernel
   `roles/orchestrator.md`'s current line).
2. **F2, `template/governance/kernel/skills/orchestration/SKILL.md`:**
   - the per-round `gov checkpoint` record (DEC-511) is lifted by DEC-1057 (R-6): drop the requirement, or restate it
     as what DEC-1057 keeps;
   - "never two writing sessions in one tree" cites DEC-963 item 1, not DEC-254 (an expired interim rule);
   - the "nothing … read from another session's folders" line is brought in line with DEC-820, where reads are open
     apart from its four refusals.
3. **F4, `template/governance/kernel/skills/test-design/SKILL.md`:** the read rule cites CAP-38.c (independent
   authorship), not CAP-38.b or DEC-136. The Inputs and Writing lines may be re-cited the same way if they are wrong.
   The guard allows it; it is not required.
4. **`template/governance/kernel/templates/checkpoint.md`:** the front-matter `task:` is empty (`task: ''`), with a
   comment naming the ticket's DAEO id ({ID}) to fill. `gov links` then reads no unknown id in the template.
5. **Versions:** orchestration and test-design 1.1.0 to **1.2.0**. The skills validator passes on both; do not write
   `gov` subcommands the validator does not know in backticks.
6. **The template's rulesync skill copies** (`template/.rulesync/skills/{orchestration,test-design}/SKILL.md`): byte
   copies of the kernel skills again.
7. **`docs/changes/W2-128-CIT-P.md`:** round 2b's rows.

Every line that states a rule ends with its ACCEPTED decision id (check `Changed by:` and `Lifted by:`). Change
nothing beyond the parts named.

## Where you work
- **Your worktree:** `/home/usain/gov-os-worktrees/W2-128`, branch `w2/W2-128`, holding integrate and round 2b's cases
  (TESTS-READY `aeee55f658f6`). Your paths: the ticket's `allowed_paths`.
- **You never read `tests/acceptance/W2-128/`** (DEC-820 (c)). Run the cases with
  `python3 -m gov.cli.main accept W2-128 --root /home/usain/gov-os-worktrees/W2-128`. If that crashes in the sandbox,
  run `python3 -m pytest tests/acceptance/W2-128 -q -p no:cacheprovider -rf` with
  `PYTHONUSERBASE=/home/usain/.local`. Read only the result lines. Exclude the folder from every Grep, Glob and
  recursive search.
- Also run W1-35's brief cases:
  `python3 -m pytest tests/acceptance/W1-35/test_w1_35_orchestration.py -q -p no:cacheprovider -m "not local_only" -k "not real and not green_here and not time_limit" -rf`.
  This is not the whole W1-35 folder. Read only the result lines. Run `python3 -m gov.check.schema` too.
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-128/src` throughout.
- The generated `.claude/` and `.rulesync/` copies are the ACT's (`ACT-CLAUDE-COPIES-1`): never touch them, nor
  `tests/acceptance/**` or `.tickets/`. Do not merge.
- Never open `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`, `memory-verdict` or `memory-verdict-2` folder. No
  GPU, model, network, installs or `gov retrieve`.
- DEC-1080: one simple command per Bash call. Search again once (DEC-1092 (1)) if a search does not answer.
- **Commit** on `w2/W2-128`, only your paths, with
  `--trailer "Task: DAEO-t8mp" --trailer "Implements: DEC-963, DEC-1050, DEC-1052" --trailer "Role: product-spec" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- A small round: keep it short.

## Return
Your final message, in full:
- the twelve labelled fields of `EMG-common.md` (sandbox and `ps` checks first);
- per item, what changed (file and line);
- the validator's output;
- the counts of the three checks.
