# W2-121b (DAEO-ifgf): the narrow check of the template default (the owner, 2026-11-12: a change decided after a ticket's review gets a narrow independent check of that change; the ticket lands on it)

You are a fresh, read-only independent reviewer. Not a design review: W2-121b's FULL review passed at round 2 (`dae1c10e0392`); then
the owner widened it by one line (DEC-1149 (2)): the template's default `working_size_bytes` in `src/gov/resources/config.py`
becomes 805,306,368 B (0.75 GiB), dated 2026-11-12 with its source naming DEC-1149, with one unit case. It rode run 3b (DEC-802).
READY is computed by `verdict.py` from your block. Worktree: /home/usain/gov-os-worktrees/W2-121b (branch w2/W2-121b, head b24361b51).

## Check exactly this
1. `git diff dae1c10e0392 b24361b51 -- src/ tests/` holds only: the merge of w2/integrate (its files byte-identical to integrate's at
   that merge), the one change in `src/gov/resources/config.py` (the default's value, date and source; nothing else in the file),
   and the one new unit case in `tests/unit/dispatch/test_w2_121b_config_default.py`.
2. `config.template()` returns `working_size_bytes` 805306368 with the date and a source naming DEC-1149; the unit case asserts that
   and fails on the old value (probe by reverting the value in your TMPDIR copy, never in the worktree).
3. Nothing W2-121b's review passed moved: `gov accept W2-121b` and the dispatch unit tests pass on the head (through heavy_slot.sh).
KPI id: `w2-121b-default-check`.

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word; each finding with `Ordinary work: yes|no, because …`, `Consequence: fails
open|loses work|other`, `scope: in|out`.

## Write and return
You write nothing in any tree except your own TMPDIR. Single simple Bash commands; every wait by pid only; every pytest through
`bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`, TMPDIR outside the repository
and ~/gov-os-runs, `-p no:cacheprovider`. Read-only probes by Bash into your own TMPDIR are allowed (DEC-1144 (7)). A resource gate's
refusal is a wait (DEC-1146). Never open the evaluation sets' root or any hidden or memory-verdict folder. Refused twice by the guard,
the sandbox or a hook: stop and say so. Your final message: answers 1-3, findings, `REVIEW_MD_BEGIN` ... `REVIEW_MD_END`, then
```verdict
{"kpis": [{"kpi": "w2-121b-default-check", "verdict": "pass|fail", "findings": [...]}]}
```
Estimate: 10 minutes.
