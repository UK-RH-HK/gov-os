
## W1-29 and W1-25 follow-up residuals (automatic checkpoints in the ignored scratch folder, DEC-444, 2026-10-07)

- **Built:** PreCompact and Stop write their checkpoint record under
  `.gov-runtime/scratch/checkpoints/(ticket)/`; a deliberate `gov checkpoint` still writes under
  `docs/checkpoints/(ticket)/`. `gov.checkpoint.record.write` takes `dest="automatic"` or `"deliberate"` (the
  default). Record numbers are unique per ticket across both places. `brief`, `briefs` and `watch` read the
  newer of the two by creation time (on a tie the deliberate one) and return its path. W1-25 was reopened for
  its module's part.
- **An automatic record carries `head_commit`,** the HEAD when it was written, and the watchdog counts commits
  from it (an ignored file is never committed, so the earlier count from "the commit that added the record"
  would always be zero). A record in the scratch folder **without** that field counts zero commits: the
  product's writer always sets it, so only a hand-placed record can lack it.
- **Automatic records written before this change stay under `docs/checkpoints/`** in the trees where hooks ran
  (untracked); nothing moves them. In this repository and its worktrees they are the orchestrator's to remove.
- **An installed project must ignore `.gov-runtime/`** for the tree to stay clean after a hook: for the
  adoption tickets (W1-39, W1-41).
- **Records:** the designer's commit `3f09f660` names "Claude Opus 4.6" as co-author.
- **Learning metrics:** one designer turn and two engineer turns started by the orchestrator; 12 cases added
  and 6 revised (owner decision); about 95 lines of source.
- **Regression at `MERGEID`:** REGLINE
