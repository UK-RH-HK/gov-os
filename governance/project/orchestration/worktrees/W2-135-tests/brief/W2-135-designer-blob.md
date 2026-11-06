Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-135-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-135 — the test designer's second pass: S3's reference moved to integrate's new retrieve.py (DAEO-c4pb)

You are the independent test designer for **W2-135**. Your first pass (`851715d78`) pinned S3's reference ("today's
code") to integrate's `retrieve.py` blob (`TODAY_BLOB`; your README's N-5). W2-32's S11 has since merged into
`w2/integrate` and changed `retrieve.py`. The CTO merged integrate into your branch.

## What to do
1. In `/home/usain/gov-os-worktrees/W2-135-tests` (branch `w2/W2-135-tests`), move `TODAY_BLOB`, or however S3 names
   the reference, to the `retrieve.py` now on `w2/integrate` (`git rev-parse w2/integrate:src/gov/retrieval/retrieve.py`).
   Update README N-5 to say so.
2. Check S3's premise still holds on the new reference (every scenario still holds what S3 names). S11's pool settings
   are off by default, so today's path is unchanged. Say if it does not hold.
3. Run the folder and `gov accept W2-135` through the heavy slot, with a scratch HOME whose `.local/lib` links to the
   real user site, as in your first pass. S1 stays red on integrate, and S2 and S3 green.
4. Change no other case.

## Rules
As in your first brief (`W2-135-designer.md`): only `tests/acceptance/W2-135/`; the hidden-half rule; DEC-1080 (Read
and Grep tools for reading; one simple command per Bash call; no `cd … &&`; no `git -C`; one line before a command
that will ask). Commit with `--trailer "Task: DAEO-c4pb" --trailer "Implements: DEC-1086" --trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.

## Return
The twelve labelled fields, with the commit and `gov accept`'s counts.
