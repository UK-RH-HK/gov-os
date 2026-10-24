You are the ticket lead for ticket `DAEO-uzme` (`W2-70`, "Retire the two nested reruns: W1-05's switch-over case and W1-47's builder rerun"), profile LITE, a test-revision ticket, working only in the worktree `/home/usain/gov-os-worktrees/W2-70` on branch `w2/W2-70`.

**This is run 2, a short round.** `git log --oneline -1` must show `e052b7b5`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it. Read your own `.gov-runtime/scratch/lead/CHECKPOINT.md` from run 1 first, then the ticket file (`.tickets/DAEO-uzme.md`) as it stands after the merge below: it gains one KPI line (DEC-912 item 1).

## Why you start now

- **W1-01's merge rule (DEC-253, `merge_offences` in `tests/acceptance/W1-01/w1_01_support.py`)** passes a merge without the test designer's role only if each acceptance file it changes equals one parent's copy.
- **Two ordered merge-backs break it:** W2-66's `03f470a5` and W2-65's `4ef3293a`. Each holds acceptance files that equal neither parent but are exactly git's own clean merge of two test designers' edits (one W1-30 file; two W1-26 files). Nobody hand-edited them. W1-01's history and integration-merges cases are red on both branches.
- **The owner's decision (DEC-912 items 1 and 2):**
  - a merge commit passes when every file it changes under `tests/acceptance/` equals git's own merge of its parents (`git merge-tree --write-tree`), and every brought commit that touches the folder is still a test designer's or listed in `acceptance_exemptions` (DEC-906 item 2, unchanged);
  - any file that differs from git's own merge (a hand edit, a conflict resolution) stays a refusal;
  - a test designer makes it, and it must land before W2-66's verification and before the W2-59 + W2-65 merge. **W2-66's run 3 is waiting on you.**

## The decisions for this run

- **First, merge `w2/integrate` into this branch,** in one Bash call, with its trailers (`Task: DAEO-uzme`, `Implements: DEC-912`, `Role: orchestrator`, `Co-Authored-By`). Your head is already inside `w2/integrate`, so the merge brings only its side. The merge's tree must equal `git merge-tree --write-tree HEAD^1 HEAD^2` and `w2/integrate`'s tree.
- **The revision, by a fresh independent test designer** (launched sandboxed, `--effort high`), in `tests/acceptance/W1-01/` only, `Rewrite-Reason: DEC-912`:
  - `merge_offences` and its docstring as DEC-912 item 1 says. "Git's own merge" is the tree `git merge-tree --write-tree <first parent> <other parent>` writes (for an octopus merge, judge it as today, with no new allowance). A merge-tree run that reports a conflict, or that cannot run, gives no allowance: the file is judged as today.
  - The four fixture cases of the KPI line, in a temporary repository built from scratch:
    - a clean merge of two test designers' edits of one file passes;
    - the same merge with one line hand-edited stays red;
    - a merge that resolves a conflict in the file stays red;
    - a clean merge that brings an unlisted commit without the role stays red.
  - **Never touch the path map** (`acceptance_exemptions` is the owner's), and change no other acceptance folder.
- **Your own check** (a script file under `.gov-runtime/scratch/lead/`, never `python3 -c` with braces, DEC-409): with the revised code, `merge_offences` is empty for `03f470a5` and for `4ef3293a`, both read in this repository's object store (`git rev-parse` gives their full ids). It is still non-empty for a hand-edited fixture. Give the result in your return, with 12-digit ids only (DEC-911).
- **The verification run:** in the close's form, under `flock /tmp/gov-os-verify.lock`, with `-o tmp_path_retention_policy=failed` and the disk gate first (the common brief below). W1-01's two cases must be green on this branch.

## This run's order

1. The merge above.
2. The test designer's revision, one commit (or a revision commit and a fixtures commit), with its trailers and `Rewrite-Reason: DEC-912`.
3. Your check above, and W1-01's suite on its own.
4. Verify in full.
5. **Return** DONE. The orchestrator merges this branch into `w2/integrate` at once, and W2-66's run 3 then merges it back. Otherwise PACKAGES.

**Estimate:** about 30 to 60 lines in `w1_01_support.py` and the fixtures, about 2 hours with the full run.

**Time:** each worker gets a budget of about 90 minutes (the Bash tool's two-hour limit).

---
