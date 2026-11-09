Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-128/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-128 round 2a — the independent review (DAEO-t8mp)

You are a fresh, read-only independent reviewer. Review **W2-128**'s round 2a (`.tickets/DAEO-t8mp.md`: read the
body's "Round 2a" in full, and its TPL-6 line S11). Round 1 was reviewed READY (`governance/project/orchestration/reviews/w2-128-r1.md`;
round 2a answers its F6 and F7).

## What to review
- **The branch:** `w2/W2-128` in `/home/usain/gov-os-worktrees/W2-128` at `5c494e255960`, against `w2/integrate`
  (`git diff w2/integrate...w2/W2-128`): `skills/test-design/SKILL.md`, `skills/orchestration/SKILL.md`,
  `roles/orchestrator.md`, `templates/checkpoint.md`, `template/.rulesync/skills/*/SKILL.md`, `docs/changes/W2-128-CIT-P.md`,
  and round 2a's cases `tests/acceptance/W2-128/test_w2_128_round2a.py` (TESTS-READY `f3e2a55accd4`).
- **The runs (the CTO's, outside the sandbox):** `gov accept W2-128` 113/113; W1-35's orchestration cases 27/27; the
  skills validator no findings. Structural pass against integrate: portability NOTICE (the `.rulesync/` and `.claude/`
  copies, which `ACT-CLAUDE-COPIES-1` regenerates, expected); links NOTICE: `UNKNOWN_ID {ID} in CP-0000's task`
  (`templates/checkpoint.md:7`), the same count as the `DAEO-0000` it replaced. Judge whether that example should
  carry a value `gov links` does not flag.

## Check
- The test-design read rule against DEC-963 and DEC-820 (c): it permits the integrated code, forbids this ticket's
  implementation and the counterpart's work, and contradicts nothing in T-4 (`role-test-designer.md`).
- The orchestration skill: "Briefs" points to the templates; nothing still tells a lead to copy the standing sentences
  or state each step in full; K-4's two lines match DEC-820 and keep the held-out contents refusal (DEC-525); nothing
  else changed beyond the version.
- `roles/orchestrator.md`: only the line on the retired briefs changed.
- Every bracketed id ACCEPTED and not lifted or expired; the CIT-P record's new rows true.
- Do the cases prove the lines, or could a text pass them and miss the line?

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
  with one entry: `S11` (round 2a's part), plus `F7` if a citation fails.
