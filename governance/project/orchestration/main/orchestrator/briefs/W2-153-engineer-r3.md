# W2-153 R1 — the engineer's brief: one more unit file's fixtures (DAEO-8s85)

You are a fresh engineer for **W2-153** (`.tickets/DAEO-8s85.md`: read "The review's R1"). W2-153's launcher refuses
a launch without `<root>/.claude/templates/<stem>.md`. After integrate merged W2-56's follow-ups R3/R5, one more unit
file launches leads in fixture repositories without that copy:
`tests/unit/launch/test_w2_56_r5_lead_store.py` (12 red). Its "a place that cannot be used refuses the lead before
anything starts" cases now meet the template refusal first. The file is in your paths.

## The change
- In each file's fixtures, plant `.claude/templates/<stem>.md` for the role launched. Planting all eight is simplest;
  any content will do. Where a case asserts a refusal for another reason (the gate, a plan, a held-out file), the copy
  must be there so that the other refusal is what is tested.
- Change no assertion and no expected value. The one exception: an assert that the caller's arguments end the argv
  may allow the single appended `--append-system-prompt-file <path>` pair, as you did for W2-136's unit case.
- Then run `tests/unit/launch`, `tests/unit/resources` and `tests/unit/adapters` in full, with
  `-m "not local_only" -k "not real and not green_here and not time_limit"` and an empty `HOME`: 0 failures. Then
  `gov accept W2-153` and `gov accept W2-56` on your tree. The acceptance fixtures are a test designer's, being fixed
  in parallel on `w2/W2-153-tests`; report W2-56's red cases as expected until the CTO merges them.

## Where you work, rules, return
- Your worktree `/home/usain/gov-os-worktrees/W2-153`, branch `w2/W2-153` (integrate merged in).
  `.claude/templates/` is now tracked from integrate (ACT-CLAUDE-COPIES-1), so your launcher starts you.
- **You never read `tests/acceptance/W2-153/`** (DEC-820 (c)). Run it only through `gov accept`, or with
  `python3 -m pytest … -rf` (`PYTHONUSERBASE=/home/usain/.local`) if `gov accept` crashes in the sandbox. Read only
  the result lines.
- Use `PYTHONPATH=/home/usain/gov-os-worktrees/W2-153/src`. No whole-suite run. Never start a real session. No GPU,
  model, network, installs or `gov retrieve`. Never open `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder. DEC-1080: one simple command per Bash call. Search again once
  (DEC-1092 (1)) if a search does not answer.
- Do not merge. Never touch `tests/acceptance/**`, `.tickets/` or `.claude/`.
- **Commit** on `w2/W2-153`, only that file, with
  `--trailer "Task: DAEO-8s85" --trailer "Implements: DEC-1050, DEC-1112" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- A small round.
- **Return** (your final message, in full): the twelve labelled fields of `EMG-common.md` (sandbox and `ps` checks
  first), the files changed, the three unit folders' counts, `gov accept W2-153`'s and W2-56's counts.
