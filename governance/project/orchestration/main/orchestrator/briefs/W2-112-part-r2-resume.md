You are the ticket lead for ticket `DAEO-clon` (`W2-112`, "One reranker serves every session: a shared, on-demand reranker service on the GPU"), profile FULL, working only in the worktree `/home/usain/gov-os-worktrees/W2-112` on branch `w2/W2-112`.

**This is the resume of run 1 after the owner's stop of 2026-11-02 ~17:00, under the emergency plan (DEC-1039 item 1: the shared reranker on the GPU, resumed from its checkpoint, round 2's review).** `git rev-parse --short=12 HEAD` must show `f59c9ba5560e`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

## Read first
Your own checkpoint, `/home/usain/gov-os-worktrees/W2-112/.gov-runtime/scratch/lead/CHECKPOINT.md`: its "Exact next step to resume" (steps 1 to 5) is this run's work, in order. The decisions it cites (DEC-1033 to DEC-1037) are in force; DEC-1038 and DEC-1039 are new since your stop (read them in `docs/DECISION_REGISTER.md`).

## What changed since your stop
- `w2/integrate` is now `3630679c` (the emergency re-pin to `pin-a7182f6c` is live; the query server runs on the GPU; the gate's thread budget is live in `tools/heavy_slot.sh`). Merge it first (your step 1), then `w2/W2-112-tests` at `ed0891667f46`.
- **DEC-1038 (4): every heavy job through the gate**, yours and your workers' included: test runs through `.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh` (or `verify_lock.sh`, which uses it), rebuilds through `tools/rebuild_slot.sh`. Nothing heavy past it.
- **The GPU budget (DEC-1039 (1b)):** the GPU is shared with the two embedders (about 5.6 of 15.9 GB used at 19:25). Your real-reranker service may run only while you measure or verify, holds one of the two GPU reranker slots (DEC-1036 (2)), and is stopped at the end with its memory confirmed released. If `nvidia-smi` (`/usr/lib/wsl/lib/nvidia-smi`) shows less than 4 GB free before you start it, wait (up to 20 minutes, checking each minute) rather than start it; say so in your return.
- Processes are judged with `.gov-runtime/scratch/orchestrator/tools/tree_busy.sh <W2>` (never `pgrep -f` on a path).

## Review round 2, the last (DEC-1010)
Your step 4: a fresh independent-auditor, old form unsandboxed, `--effort max`, with the tripwire; its brief carries `governance/project/briefs/JUDGEMENT.md` word for word and the structured `verdict` block. On a pass: the probe record at `docs/probes/DAEO-clon/PR-DAEO-clon.md`, checked with `tools/verdict.py`, committed alone. **On a fail: stop and return PACKAGES with the findings and your options** (this goes to the owner once, DEC-1010); no third round.

## Return
DONE (head, the review's verdict, the scoped results with every red explained, the GPU measure if re-taken, residuals) or PACKAGES. Then the CTO lands W2-112 through the queue as an emergency patch and writes the stopgap's retirement ACT for the owner (your research doc's last section). Leftovers you cannot remove (`rm` needs the owner): name them.

**Estimate:** about 2 hours (merges, verification, one review). Scratch (DEC-898): 20 GB and 1,000,000 files and folders, outside the tracked tree; `TMPDIR=/tmp/gov-os-lead-W2-112`.
