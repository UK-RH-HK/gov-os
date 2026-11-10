Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-128/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-128 round 2b — the independent review (DAEO-t8mp)

You are a fresh, read-only independent reviewer. Review **W2-128**'s round 2b (`.tickets/DAEO-t8mp.md`: read the
body's "Round 2b" in full). It answers round 2a's review, `governance/project/orchestration/reviews/w2-128-r2a.md`
(F1 to F4, and F5's link notice).

## What to review
- **The branch:** `w2/W2-128` in `/home/usain/gov-os-worktrees/W2-128` at `5cfa4b28f`, against `w2/integrate`
  (`git diff w2/integrate...w2/W2-128`). Round 2b's change is commit `9d95279c9`:
  - `skills/orchestration/SKILL.md` and `skills/test-design/SKILL.md`, both 1.2.0;
  - `template/.rulesync/subagents/orchestrator.md` and `template/.rulesync/skills/`;
  - `templates/checkpoint.md`;
  - `docs/changes/W2-128-CIT-P.md`.
  Also review the designer's revised and added cases (TESTS-READY `aeee55f658f6`, `Rewrite-Reason:`).
- **The runs (the CTO's, outside the sandbox):** `gov accept W2-128` 121/121; the skills validator found nothing.

## Check
- **F2:** is each lifted or expired rule restated correctly against DEC-1057 (R-6), DEC-963 item 1 and DEC-820, with
  nothing else in the skill changed?
- **F4:** does the read rule cite CAP-38.c? The worker reports that the "Writing acceptance tests" lines still cite
  CAP-38.b, because the guard case does not allow that section. Is that a finding?
- **F1:** does the template's rulesync orchestrator copy carry the kernel line?
- **The checkpoint example:** is `task: ''` with its comment enough, and does `gov links` stay quiet on the
  template?
- **F3:** do the strengthened cases now prove their lines?
- Is every bracketed id ACCEPTED, and not lifted or expired? Are the CIT-P rows true?

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word: read it and apply it. Every finding carries
`Ordinary work: yes|no, because …`, `Consequence: fails open|loses work|other`, and the evidence that would reverse it
(DEC-1014).

## Write and return
- **You write nothing** in any tree; run nothing that writes (tests read-only with `-p no:cacheprovider`, only
  `tests/acceptance/W2-128`). Single simple Bash commands (DEC-1080). The hidden-half rule holds: never open anything
  under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`, `memory-verdict` or `memory-verdict-2` folder.
- **Search again once (DEC-1092 (1)):** if a search does not answer, search once more in your own words; then answer
  from both, with path and lines, or say "not found".
- **Your record is your session's final message**, in full: the twelve labelled fields of `EMG-common.md` (sandbox and
  `ps` checks first), your verdict per round-1 line, every finding with its lines and `scope: in|out`, and at the end
  the fenced `verdict` block in DEC-1010's form:
  `{"kpis": [{"kpi": "S1", "verdict": "pass|fail", "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}, ...]}`
  with one entry: `S11` (round 2b's part), `S14` (the checkpoint example), plus `F7` if a citation fails.
