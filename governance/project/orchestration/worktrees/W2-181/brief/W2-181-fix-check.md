Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-181/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-181 (DAEO-ywb5): the narrow check of W2-157's F4 revision (DEC-1156 (6), (7); DEC-1154)

You are a fresh, read-only independent reviewer. Not a design review: W2-181 is a LITE test revision built to its checkpoint
earlier today and parked; the owner returned it to land now (DEC-1156 (6)). READY is computed by `verdict.py` from your block.
Worktree: /home/usain/gov-os-worktrees/W2-181 (branch w2/W2-181, head 499543a836d3).

## Check exactly this
1. `git diff --name-only $(git merge-base HEAD w2/integrate) HEAD` lists only `tests/acceptance/W2-157/test_w2_157_nothing_else.py`
   and `tests/acceptance/W2-157/README.md`, and the commit `120474643` carries `Role: independent-test-designer` and a
   Rewrite-Reason; nothing in `src/`.
2. `test_f4_the_branch_changes_only_the_tickets_allowed_paths` judges only when HEAD is `refs/heads/w2/W2-157` and skips elsewhere
   with its reason (the branch found, or "detached HEAD"); it still fails on a planted `w2/W2-157` branch with a change outside
   W2-157's paths (probe in a planted repository in your TMPDIR); the same form as W2-180's revision of W2-170's F5
   (`tests/acceptance/W2-170/test_w2_170_f5_paths.py`). No other case in the file changed what it guards.
3. W2-157's acceptance folder passes on the head (through heavy_slot.sh); with the branch merged onto current w2/integrate in a
   clone in your TMPDIR, the F4 case skips with its reason (as the merge queue's clone sees it).
KPI id: `w2-181-fix-check`.

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
{"kpis": [{"kpi": "w2-181-fix-check", "verdict": "pass|fail", "findings": [...]}]}
```
Estimate: 15 minutes.
