Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-176/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# The review of ACT-CONTEXT-WATCH-1, round 2 of 2 (DEC-1010): rebuilt on W2-176's no-cap hook bytes

You are a fresh, read-only independent reviewer of an ACT before it goes to the owner (DEC-1104 (2): rehearsal, a READY
review and matching hashes). READY is computed by `verdict.py` from your block. This is the last review round: a finding
that still blocks goes to the owner once, with options.

## The ACT
- **Package:** `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/context-watch-1/ACT-CONTEXT-WATCH-1.md`
  (section 7 says what changed in round 2).
- **Bundle:** `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/acts/ACT-CONTEXT-WATCH-1/` (manifest sha256
  `5bdfa0981808513db3d9fceeb30f13ba11ea72ea28528ef40664bfe9a931da5a`). Round 1's bundle is kept beside it as
  `acts/ACT-CONTEXT-WATCH-1.r1-c6dabb5e/` and its drafts as `drafts/context-watch-1.r1-c6dabb5e/`.
- **Round 1's review:** `/home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/reviews/ACT-CONTEXT-WATCH-1-review.md`
  (READY on the hook bytes `c6dabb5eed39`, which the owner withdrew on 2026-11-12 because they carried a token cap; DEC-1141 in
  `/home/usain/Dynamic-Agentic-Engineering-OS/docs/DECISION_REGISTER.md`).
- **What round 2 changes, and nothing else should:** the approved hook sha256 that `check` and `apply` require is now
  `213882efd7b83e9988a50d3a348dc92479d4b402d2f54985db9e6ffd84d2a242` (W2-176 at `3b6c5cb79d39`: the cap removed, R8 fixed;
  its delta review READY, filed beside this brief as `drafts/W2-176-delta-review.md` under the orchestrator folder); the
  behaviour check (`tools/check_hook.py`, manifest check 3) plants a claude-opus-5-5 worker against its own 1,000,000 window
  (token counts x5) and adds one case, 180,000 tokens silent (no cap), so its count is 8; the rehearsal merges W2-176's new
  head in its clone; the manifest's `dec` names DEC-1141 for the replaced DEC-1118.

## Check
1. **The diff between the rounds:** `diff -r` round 1's bundle against round 2's: only `apply.sh`'s hash line, the manifest
   (the hash, check 3's body and count, `dec`, the hashes of `apply.sh` and `rehearsal.log`) and `rehearsal.log` differ; the
   `before/` and `after/` copies and `list.txt` are byte-identical, and `before/` still equals the live `.claude/settings.json`
   and `.rulesync/hooks.jsonc` on `w2/integrate` today.
2. **Every hash recomputed:** the package's section 3 table, `list.txt`, `manifest.json`.
3. **Check 3 is right for the new bytes:** run it as the manifest writes it (`bash -c` from a `--no-hardlinks` clone of
   `w2/integrate` with `w2/W2-176` merged in the clone only): exit 0, prints 8; on round 1's hook bytes (`3a580a4b4d42`
   merged instead) it fails at the 180,000 case. Is anything the new hook does left unchecked that round 1 checked?
4. **Fail safe and class unchanged:** the round 1 answers on a missing hook file, the matcher `Bash` and class (b) still hold.
Never touch the live `.claude/`; never run a real Claude session.

KPI id for the verdict block: `act-context-watch-1`.

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word. Every finding carries `Ordinary work: yes|no, because …` and
`Consequence: fails open|loses work|other`, and `scope: in` only if it concerns this ACT.

## Write and return
- **You write nothing** in any tree. Single simple Bash commands (DEC-1080). Every wait by pid only
  (`bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/proc.sh wait --max <s> <pid>`).
  Row W2-L423's rule: under `.gov-runtime/`, commit hashes as 12 digits and none of that rule's keywords.
- Scratch budget 30 GB, your own TMPDIR; remove your clone (`chmod -R u+w` first); report `du -sh` in `evidence`.
- The hidden-half rule holds: never open anything under `~/gov-os-eval/`, or any `hidden`, `memory-verdict` or
  `memory-verdict-2` folder. Refused twice for the same call: stop and say so.
- There is no token cap: use your model's full window.
- **Your record is your session's final message**, in full: the twelve labelled fields first (task, status,
  work_completed, files_changed, evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved,
  recommended_next_action); your answers to the checks; every finding with its two lines and scope; then
  `REVIEW_MD_BEGIN`, the review record in markdown, `REVIEW_MD_END`; at the end the fenced `verdict` block
  `{"kpis": [{"kpi": "act-context-watch-1", "verdict": "pass|fail", "findings": [...]}]}`, each finding
  `{"id", "scope", "ordinary_work", "consequence"}` (ids from F1).
- Estimate: 15 minutes.
