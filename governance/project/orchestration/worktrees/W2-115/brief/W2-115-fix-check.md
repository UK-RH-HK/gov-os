Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-115/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-115 (DAEO-emq1): the narrow check of P1-K (a)'s fix (the owner's P1-M (a), 2026-11-12: a third look, limited to the fix)

You are a fresh, read-only independent reviewer. Not a design review: review round 2 failed on R2-1 (fails open), the owner
decided P1-K (a) (drop the fallback: `select.head_without_change` returns the green base when it is an ancestor of HEAD, and
nothing otherwise; with no green base every red counts as the change's), the fix rode a resume (DEC-802), and the owner allowed
this one narrow check (P1-M (a)) so the queue has a passing record. READY is computed by `verdict.py` from your block.

The worktree: /home/usain/gov-os-worktrees/W2-115 (branch w2/W2-115, head ea6dc2c14727). Round 2's record and the fix's notes:
docs/probes/DAEO-emq1/PR-DAEO-emq1.md (lines ~85-100).

## Check exactly this
1. The code change since round 2's reviewed head (f39289d3a379) is the fallback's removal in `src/gov/close/select.py`
   (`head_without_change`) and nothing else in `src/` (`git diff f39289d3a379 ea6dc2c14727 -- src/`); the merge of w2/integrate
   (8e66a9bd7) brings only integrate's files.
2. R2-1 is closed: with no green record on HEAD's line, an untrailered commit that breaks a test, then trailered work, makes the
   close refuse (the red counts as the change's), not exit 0. Run the planted case td-5 added, and probe it yourself in your TMPDIR
   (a throwaway repository; read-only on the worktree).
3. The test revisions (the not-an-ancestor case, R2-1's planted case, R2-4's two guards, R2-5's `-I` fix) each carry their
   Rewrite-Reason and change only what the owner's decision changes; `gov accept W2-115` passes on the head (run it through
   heavy_slot.sh) and the unit tests of `src/gov/close/` pass.
4. Nothing else regressed in what round 2 passed: S1-S3 and S5-S7 unchanged (spot-check their cases).
KPI id for the verdict block: `w2-115-fix-check`.

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word: each finding with `Ordinary work: yes|no, because …`,
`Consequence: fails open|loses work|other`, and `scope: in` only if it concerns this fix.

## Write and return
- You write nothing in any tree except your own TMPDIR. Single simple Bash commands. Every wait by pid only
  (`bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/proc.sh wait --max <s> <pid>`).
- Every pytest through `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`,
  TMPDIR outside the repository and outside ~/gov-os-runs, `-p no:cacheprovider`.
- Read-only probes by Bash into your own TMPDIR are allowed at any hour (DEC-1144 (7)). A resource gate's refusal is a wait
  (DEC-1146). Never open the evaluation sets' root or any hidden or memory-verdict folder. A session refused twice for an action
  by the guard, the sandbox or a hook stops and says so.
- **Your record is your final message**: your answers to checks 1-4; every finding with its lines and scope;
  `REVIEW_MD_BEGIN` ... `REVIEW_MD_END`; then the fenced `verdict` block
  `{"kpis": [{"kpi": "w2-115-fix-check", "verdict": "pass|fail", "findings": [...]}]}`.
- Estimate: 15 minutes.
