# W2-128 round 2a — the product-spec worker's brief (DAEO-t8mp)

You are a fresh product-spec worker for **W2-128** (`.tickets/DAEO-t8mp.md`). Round 1 (the templates) is merged.
Read the ticket's body, **"Round 2a"**, in full: it lists this round's work exactly. Then read the review
`governance/project/orchestration/reviews/w2-128-r1.md` (findings F6 and F7), and the decisions DEC-963, DEC-820,
DEC-508, DEC-525, DEC-1050 and DEC-1052 in `docs/DECISION_REGISTER.md`, by id.

## The work (round 2a only)
1. **`template/governance/kernel/skills/test-design/SKILL.md`, "Read restriction":** the designer reads the
   integrated code on `w2/integrate` and never this ticket's implementation (DEC-963). Drop the outright ban on
   `src/` (review F7).
2. **`template/governance/kernel/skills/orchestration/SKILL.md`:**
   - "Briefs" points to the kernel templates (`template/governance/kernel/templates/`: `brief.md` and the `role-*.md`).
     Retire "states each step in full" and "carries the standing sentences word for word" (review F6, its lines 14,
     29, 61).
   - K-4's two lines (today 84 and 85) restated per DEC-820: reads are open, apart from secrets, the held-out
     material's contents, the counterpart's work on the same ticket and the hidden half of an evaluation set. Keep
     the held-out contents refusal [DEC-525, DEC-820].
3. **`template/governance/kernel/roles/orchestrator.md`, line 39:** point to the role templates in place of the retired
   `brief-*.md` texts (F6). Nothing else in the role files.
4. **JUDGEMENT's rules only in T-6:** check that no kernel template other than `role-reviewer.md` carries them.
5. **`template/governance/kernel/templates/checkpoint.md`'s example:** a placeholder id, not `DAEO-0000` (for
   example `{ID}`, a key in `keys.yaml`).
6. **`template/.rulesync/skills/<s>/SKILL.md`** for discovery, retrieval, orchestration and test-design: byte copies
   of the kernel skills.
7. **Versions:** the orchestration and test-design skills one minor up. The skills validator must pass:
   `python3 -m gov.check.skill_validator --both-layouts template/governance/kernel/skills/orchestration template/governance/kernel/skills/test-design`.
   It refuses an unknown `gov` subcommand in a code span, so do not write `` `gov brief` `` in backticks until W2-152
   lands. Name it in plain words.
8. **`docs/changes/W2-128-CIT-P.md`:** round 2a's rows (the two skills and the role line are kernel changes).

Every line that states a rule ends with its ACCEPTED decision id (check `Changed by:` and `Lifted by:` too). Change
nothing in the two skills beyond the parts named.

## Where you work
- **Your worktree:** `/home/usain/gov-os-worktrees/W2-128`, branch `w2/W2-128`, holding integrate and round 2a's cases
  (TESTS-READY `f3e2a55accd4`). Your paths: the ticket's `allowed_paths`.
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
