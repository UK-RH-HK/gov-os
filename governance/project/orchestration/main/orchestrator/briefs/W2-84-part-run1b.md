You are the ticket lead for ticket `DAEO-m1u3` (`W2-84`, "the hidden-set refusal in every tree"), profile FULL, working only in the worktree `/home/usain/gov-os-worktrees/W2-84` on branch `w2/W2-84`.

**This is run 1b: the resume of run 1, which stopped under the 90-minute rule (P-W2-84-HOLD (a), the orchestrator's delegated choice).** `git rev-parse --short=12 HEAD` must show `@@HEAD@@`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

**Read first:**
- your run-1 checkpoint, `.gov-runtime/scratch/lead/CHECKPOINT.md`;
- the design note, `.gov-runtime/scratch/lead/design.md`;
- the reviewer's brief, `briefs/rev-1.md` (filled, not launched).

## Why you start now
- **W2-84 is on memory's critical path:** W2-61h, the hidden half of the standing measure, waits on it (DEC-950).
- **The state:** the fix is in at code head `c0f35c87fd8a`, its own suites are green, and the parallel phase is green. The serial phase and the review are left. The close queue that held you has ended.

## The decisions for this run
1. **Do not merge `w2/integrate` again** unless `git diff --stat <your merge base> w2/integrate -- src/gov/guard tests/unit/guard tests/acceptance/W2-84` is non-empty. If it is non-empty, merge, re-run the parallel phase, and the probe covers the merged head.
2. **The serial phase:** `verify-serial.sh full1`, as your checkpoint names it (about 30 to 40 minutes).
   - W2-84 changes the guard, the judge's own core, so this is a full run under the verification lock (DEC-952).
   - W1-05's latency cases fail under load: if red, re-run them alone and report both.
3. **The FULL review** with `briefs/rev-1.md` (JUDGEMENT.md word for word, `--effort max`, read-only, sandboxed).
   - Its probe asks above all whether any route lets a measured session read a hidden part in any tree: an absolute path, another worktree, a run clone, a symlink, git's object store.
   - Commit the probe record only when it passes.
   - If it fails on a fail-open finding: one test batch, one engineer, the runs, review 2 (DEC-413).
4. **Return** DONE (probe passed; ready to merge) or PACKAGES.

**Estimate:** about 2 to 3 hours.

---
