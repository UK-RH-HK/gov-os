You are the ticket lead for ticket `DAEO-kl5e` (`W2-50`, "The durable scratch root: ~/gov-os-runs/<own ticket>/ in the guard and the launcher's sandbox (CIT-P)"), profile FULL, working only in the worktree `/home/usain/gov-os-worktrees/W2-50` on branch `w2/W2-50`. You run the ticket loop for this one ticket and return one summary. You are a headless session: nobody answers questions while you work, and only your final message is read.

**This is run 8, the resume.** `git log --oneline -1` must show `0affa162` (the last round's probe record, committed as it was), and `git status --short` must show nothing but sandbox placeholder files, if any (anything else: stop and return PACKAGES naming it). Read `.gov-runtime/scratch/lead/CHECKPOINT.md` in this worktree (run 7b): its "What the resume lead does" section holds, and this brief adds to it.

## Why you resume now

1. **The close queue (keystone 2 of the accepted revised plan, DEC-831)** waits on you twice: W2-50 itself is queued to close, and **every close is blocked** until the secrets scan below is fixed (P-W2-49). The owner put that fix into this resume (DEC-853).
2. W2-58 (Policy 2 in the guard, first in keystone 3, DEC-849) shares your files (`guard/decide.py`, `guard/protected.py`, `launch/launcher.py`) and starts when you merge.

## The owner's decisions for this run (DEC-779 to DEC-852 arrive in your worktree's register with the merge of step 1; DEC-853 to DEC-855 are staged for the owner's next commit — apply them as written here)

- **DEC-853 (P-W2-49 (a)), the secrets scan, in this resume:**
  1. `gov check`'s `secrets-indexing` (hard-block) timed out on 2026-10-19 on the main tree's stores: `gitleaks stdin` hit its 60-second limit (`_TIMEOUT_S`) on `.gov-runtime/store.db` (250 MB) and `.gov-runtime/codeintel/home/code.db` (210 MB). Each file is scanned as its bytes and, for SQLite, its rows as text, once per rule set (two when the project's rules extend the defaults), about 24 files at a time (`ThreadPoolExecutor()` on 20 cores). One pass over `store.db`'s bytes alone takes 11.7 s on a quiet machine. It is deterministic at these sizes, so every close would be refused.
  2. **The fix:** the time limit grows with the content's size (or a large store is scanned in bounded chunks, each within the limit), and the pool is bounded so that large files are not starved. Every file is still scanned with every rule set; a scan that cannot finish still fails closed.
  3. **Added by the owner:** a store whose hash has not changed since its last clean scan is not re-scanned; the clean result is reused, keyed on the store's hash. A changed store is always scanned in full. **A finding is never reused.**
  4. **Your ticket file first** (as W2-54 did; a reviewed ticket's file is not edited on `w2/integrate`): after step 1's merge, add to `.tickets/DAEO-kl5e.md` in this worktree the three KPI lines above (success: the scan finishes on stores of today's size; an unchanged store's clean result is reused by its hash; failure: every file still scanned with every rule set, a scan that cannot finish still fails closed, a store changed by one byte is scanned again in full, a finding is never reused) with the source DEC-853, and `tests/unit/secrets/**` to `allowed_paths`; commit it alone with `Task: DAEO-kl5e`, `Implements: DEC-853`, `Role: orchestrator`. The card in the WBS carries the same lines (staged for the owner).
- **DEC-831 (in the register after the merge):** the plan by keystones; DEC-838, DEC-839 (the full window; `--effort high` for the test designer and engineer, `max` for your FULL reviewer); DEC-801 to DEC-809 and `JUDGEMENT.md` for the probe; DEC-790: your resume probe judges under DEC-779 and DEC-785.

## This run's order

1. **Merge `w2/integrate` into this branch** (the checkpoint's rules: `Task: DAEO-kl5e`, `Role: orchestrator`; never `-s ours`; never drop the ticket's side; a conflict you cannot resolve keeping both sides is returned as PACKAGES). Integration brings W2-53, W2-54, the owner's batches up to `a5789de1`, the W2-59 and W2-62 ticket files, and the orchestration record.
2. **Your ticket file,** as in DEC-853 item 4.
3. **Tests first:** a fresh independent test designer, launched sandboxed (`--effort high`), for DEC-853's lines only, in `tests/acceptance/W2-50/` (a new file), from behaviour: a large derived store (build one of a size that today's scan cannot finish within its limit) is decided; an unchanged store is not scanned again and its clean result is labelled as reused with the hash it was keyed on; a store changed by one byte is scanned in full; a store holding a canary secret is refused every time, never from a reused result; a scan that still cannot finish fails closed. No other W2-50 test changes.
4. Check red yourself.
5. **Implement:** a fresh engineer, launched sandboxed (`--effort high`), in `src/gov/secrets/__init__.py` (the scan only) and `tests/unit/secrets/**`, keeping your branch's `stores_with_secrets` changes (the `~/gov-os-runs` link rule) intact.
6. **Verify in full** (the loop's step 4): a full rebuild first (about 21 minutes; in the background with an exit-code file; wait for load as the common brief says), then W2-50, every earlier suite, `tests/unit` and `gov check`. **`secrets-indexing` must be GREEN here, on this worktree's real stores after the rebuild:** that is the fix's proof. Run `gov check` twice in a row and report that the second run reused the clean results (and how long each took).
7. **A fresh FULL probe** (brief A3 with `JUDGEMENT.md`, role `independent-auditor`, `--effort max`), on the final code: the merge-back under the probe gate as W2-01 and W2-53 leave it, and the scan fix. Judged under DEC-779, DEC-785 and the two questions. Commit its probe record under `docs/probes/DAEO-kl5e/` only if it passes; findings marked "no" on the first question are rows you return.
8. Return.

---

