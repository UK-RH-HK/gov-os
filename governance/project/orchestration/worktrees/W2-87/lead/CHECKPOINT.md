# W2-87 lead checkpoint

- **State:** run 1. Base `df0782fa4c4e`, clean. DEC-952 present in the register. Schema allows the top-level block (no top-level additionalProperties; loader refuses no unknown key).
- **Measure gate:** `w2/integrate` holds W2-61's measure (`289b9314`): the re-measure runs in the lead's session.
- **Design:** `.gov-runtime/scratch/lead/design.md` (part 1 register, part 2 authority). Reranker scale probed: logits about −10..+5 (rerank lift 1.0).
- **Decided:** one test designer writes both parts in two commits; engineer batch 1 (register), then engineer batch 2 (authority), then a record batch. One head clone at the final commit, one store; launchers gov-base (df0782fa4c4e), gov-reg (batch-1 commit), gov-head (final): figures per step on the same store.
- **Reading of the drops:** a register chunk is never dropped for another entry's status (case R2); nothing newly dropped; per-entry leaving-out is W2-55's.
- **Next:** rebuild-0 (this worktree's code, log/rebuild-0.json) → launch TD (briefs/td-1.md) with tripwire 1.
- **Loop count:** 0.
- **Brief gaps (running):** the brief's "leave the drops as they stand" vs case 5's second half (last entry superseded keeps the others) — needed a reading (est. 10 min).
