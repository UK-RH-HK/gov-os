You are the ticket lead for ticket `DAEO-c1uz` (`W2-66`, "Path-scoped regression at close: selection and evidence (the lite W2-38)"), profile FULL, working only in the worktree `/home/usain/gov-os-worktrees/W2-66` on branch `w2/W2-66`.

**This is run 3, the last round,** after your run 2's PACKAGES (P-W2-66-M1 and P-W2-66-R2). `git log --oneline -1` must show `5634d430`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it. Read your own `.gov-runtime/scratch/lead/CHECKPOINT.md` and `.gov-runtime/scratch/lead/P-W2-66-R2.md` first. Your run 2's temp folder is removed.

## The owner's decisions (DEC-912, on `w2/integrate`)

- **M1 (a):** W1-01's merge rule is revised. A merge passes when every file it changes under `tests/acceptance/` equals git's own merge of its parents, and any other file stays a refusal.
  - **W2-70's round 2 makes the revision,** in its own worktree, now. You do not touch W1-01.
  - Your merge-back `03f470a5` goes green once it is in.
- **R2 (a), the owner's exception to DEC-413:** one more round and a third, last review, here.
  - **P1:** a selected test-map target that cannot be resolved at the head (a record-reading, every-close or coupling target whose file or test function was renamed or is gone) widens the run to the full regression, and the record names the target and the reason, with tests.
  - **P2 rides:** W1-28's held-out copy check is coupled to every file under `tests/acceptance/` that its scan reads.
  - Your ticket file gains these two KPI lines (`b2632d76`).
- **The last round:** if the third review finds another fail-open case an honest agent can hit, no fourth round starts. Return PACKAGES with the options.

## This run's order

1. **Merge `w2/integrate` into this branch,** in one Bash call, with its trailers (`Task: DAEO-c1uz`, `Implements: DEC-912`, `Role: orchestrator`, `Co-Authored-By`).
   - Keep both sides.
   - The tree must equal `git merge-tree --write-tree HEAD^1 HEAD^2` when the merge is clean, or the recorded resolution otherwise.
   - Then rebuild, and read the ticket file as it stands.
2. **A fresh test designer** (launched sandboxed, `--effort xhigh`) writes the cases for P1 and P2, one per KPI line, plus fixtures where a record-reading, an every-close and a coupling target are each renamed: each run widens and is named.
3. **Check red yourself.**
4. **A fresh engineer** (launched sandboxed, `--effort high`), inside your allowed paths: the widening in `src/gov/close/select.py` and the test map's coupling.
5. **Wait for W2-70's round 2 to merge.** The orchestrator writes the file `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/flags/W2-70-R2-MERGED`, which holds the merge's 12-digit id, once it has merged W2-70 into `w2/integrate`.
   - Wait with bounded until-loops (`until [ -s <file> ]; do sleep 60; done` under a timeout), repeated, for up to 3 hours.
   - **Then merge `w2/integrate` into this branch again,** as in step 1.
   - If the file is still absent after 3 hours, return PACKAGES saying so, with everything else done.
6. **Verify in full** in the close's form, under the lock, with the retention option: rebuild, collection, `gov check`, the parallel run, the serial-only run. W1-01's two cases must now be green. Any red is named with its cause.
7. **The third and last FULL review** on that head: brief A3 with `JUDGEMENT.md` word for word, `--effort max`, a fresh session. It judges F1 to F6, P1 and P2 answered, and the head as a whole. Commit the probe record only when it passes.
8. **Return** DONE (ready to merge, the probe passed), or PACKAGES.
   - Give R1 to R4, the feature-gated row and P-W2-66-a as residual rows, with their classifications.
   - Note for W2-07's readers the record key `class_evidence`.

**Estimate:** about 30 lines for P1 and P2, about 4 to 5 hours with the wait, the full run and the review.

**Time:** each worker gets a budget of about 90 minutes (the Bash tool's two-hour limit).

---
