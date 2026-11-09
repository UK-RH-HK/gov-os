# W2-142 — the product-spec worker's brief (DAEO-qskx)

You are a fresh product-spec worker for **W2-142** (`.tickets/DAEO-qskx.md`): search again once in the kernel skills.
Read the ticket in full first (S2 now includes the discovery skill's version bump, marked DEC-1097 (8)), then
`governance/project/orchestration/packages/LIFT-1/SEARCH-AGAIN-PRACTICE.md` §2, §3.1 and §3.2.

## Where you work
- **Your worktree:** `/home/usain/gov-os-worktrees/W2-142`, branch `w2/W2-142`: `w2/integrate` with the designer's
  cases merged in.
- **Your paths:** `template/governance/kernel/skills/retrieval/SKILL.md`, `template/governance/kernel/skills/discovery/SKILL.md`,
  `docs/changes/W2-142-evidence.md`.
- **You never read `tests/acceptance/W2-142/`** (DEC-820 (c)): run those cases only through `gov accept W2-142` and read
  only its results. Every Grep or Glob call that could reach it carries `!tests/acceptance/W2-142/**`, and every
  recursive Bash search the matching exclusion (`grep -r --exclude-dir=W2-142`).

## The change
- **The retrieval skill:** step 7 after step 6, the package's §3.1 text exactly (one paragraph); W2-138's step-5 line
  kept; `version` 1.0.0 to 1.1.0. Nothing else changes.
- **The discovery skill:** line 55 gains the package's §3.2 sentence exactly; `version` 1.0.0 to 1.1.0. Nothing else.
- Both under the skills validator's size budget:
  `python3 -m gov.check.skill_validator --both-layouts template/governance/kernel/skills/retrieval template/governance/kernel/skills/discovery`
  with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-142/src`.
- **The evidence record** `docs/changes/W2-142-evidence.md`: one row per KPI line; S3 reads "the CTO's, at the lift's
  re-pin ACT: the generated `.claude/` copies regenerated there, and the adoption count's first reading".
- The generated `.claude/skills/` copies are not yours (DEC-315; regenerated at the ACT).
- When done: `python3 -m gov.cli.main accept W2-142 --root /home/usain/gov-os-worktrees/W2-142`, and report its counts.

## Rules
- **The hidden-half rule:** never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder.
- **DEC-1080:** Read and Grep tools; one simple command per Bash call; no `cd … &&` chains.
- **Do not merge `w2/integrate` yourself.** Never touch `tests/acceptance/**`, `.tickets/` or `.claude/`.
- **Commit** on `w2/W2-142`, only your paths, with
  `--trailer "Task: DAEO-qskx" --trailer "Implements: DEC-1094, DEC-1097" --trailer "Role: product-spec" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- A small change: keep it short.

## Return
Your whole return is your session's **final message**, in full (the launcher keeps it; it is the record): the twelve
labelled fields of `EMG-common.md` (sandbox and `ps` checks first), the diff, the validator's output and
`gov accept`'s counts.
