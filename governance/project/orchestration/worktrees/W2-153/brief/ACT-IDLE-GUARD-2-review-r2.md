Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-153/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# The review of ACT-IDLE-GUARD-2, round 2 of 2 (DEC-1010): the idle guard's F1-F3, with round 1's F1 fixed

You are a fresh, read-only independent reviewer of an ACT before it goes to the owner (DEC-1104 (2)). READY is computed
by `verdict.py` from your block. This is the last review round for this ACT: a finding that still blocks goes to the
owner once, with options.

## The ACT
- **Package:** `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/dispatch-1/ACT-IDLE-GUARD-2.md` (its round-2 note names F1).
- **Bundle:** `.../drafts/dispatch-1/acts/ACT-IDLE-GUARD-2/` (manifest sha256 `a3fe076cf3339f5da0fcd54462f8270467d731d08805215b394f66c725737422`);
  round 1's bundle kept as `acts/ACT-IDLE-GUARD-2.r1/` (manifest `531d98c0...`), its package `ACT-IDLE-GUARD-2.r1.md`.
- **Round 1's review:** `/home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/reviews/ACT-DISPATCH-1-review.md`
  (one record for ACT-DISPATCH-1 and this ACT; its F1 blocked this ACT: the plan arm's `git for-each-ref --merged
  w2/integrate` also listed a just-claimed ticket's fresh branch, so a prepared ticket stopped being named).
- **The file:** `stop_idle_check.py` (the Stop hook's idle check) and its tests; class (O), by the owner's operator by hand.
- **The fix (option (a) of round 1's F1):** a branch is left out as merged only when its tip is not on `w2/integrate`'s
  first-parent line; three new cases (F1's exact state; a fresh branch older than the head; a truly merged ticket).

## Check
1. Round 1's F1 is fixed: in your own `--no-hardlinks` clone, plant F1's state (a claimed ticket, its branch at integrate's
   head, no commits of its own) and a truly merged ticket (a commit and a `--no-ff` merge): the first stays named, the
   second is left out and logged. Also a fast-forward-merged ticket: what happens (named, once per turn, with the
   IDLE-REASON escape, as the package says)? Judge it by the two questions.
2. Nothing else regressed: round 1's F2 to F5 rows; the hook stays inside its `timeout: 10` (plan 5 s, the two git calls
   3 s together); it can only ever stop blocking for a false cause, never stop blocking for a true one; it never fails the
   session.
3. Hashes and scope: `before/` equals the live files on `w2/integrate` today; `after/` differs only by the change; every
   hash in the package, `list.txt` and `manifest.json` recomputed; the red-then-green counts hold (tests through
   `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`, one folder per run,
   `-p no:cacheprovider -o tmp_path_retention_policy=failed`).
Never run the live hook against the live session; never write a live file.

KPI id for the verdict block: `act-idle-guard-2`.

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word. Every finding carries `Ordinary work: yes|no, because …` and
`Consequence: fails open|loses work|other`, and `scope: in` only if it concerns this ACT.

## Write and return
- **You write nothing** in any tree. Single simple Bash commands (DEC-1080). Every wait by pid only
  (`bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/proc.sh wait --max <s> <pid>`).
  Row W2-L423's rule: under `.gov-runtime/`, commit hashes as 12 digits and none of that rule's keywords.
- Scratch budget 30 GB and 2,000,000 files and folders, your own TMPDIR; remove your clone (`chmod -R u+w` first);
  report `du -sh` and `du -s --inodes` in `evidence`.
- The hidden-half rule holds: never open anything under `~/gov-os-eval/`, or any `hidden`, `memory-verdict` or
  `memory-verdict-2` folder. Refused twice for the same call: stop and say so.
- **Your record is your session's final message**, in full: the twelve labelled fields first (task, status,
  work_completed, files_changed, evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved,
  recommended_next_action); your answers to the checks; every finding with its two lines and scope; then
  `REVIEW_MD_BEGIN`, the review record in markdown, `REVIEW_MD_END`; at the end the fenced `verdict` block
  `{"kpis": [{"kpi": "act-idle-guard-2", "verdict": "pass|fail", "findings": [...]}]}`, each finding
  `{"id", "scope", "ordinary_work", "consequence"}` (ids from F1).
- Estimate: 25 minutes.
