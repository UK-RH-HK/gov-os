# W2-135 — the test designer's round 2: cut lines, not items (DAEO-c4pb)

You are the independent test designer for **W2-135**. The review (`.gov-runtime/scratch/orchestrator/reviews/w2-135.md`;
read its findings F1 to F4) showed that S1 as first worded cut whole items over 4,000 characters, ordinary expanded
sections included, so an agent could lose the very line that answers. DEC-1086 B says "a guard against one-line files
only". The CTO re-worded **S1 and S2** (read the ticket again: `.tickets/DAEO-c4pb.md`, and its "Round 2" note). The
CTO merged integrate into your branch.

## What to do
1. In `/home/usain/gov-os-worktrees/W2-135-tests`, revise `tests/acceptance/W2-135/` to the new S1 and S2:
   - each line over 4,000 characters is sent as its first 4,000, and every other line whole;
   - `cut: {"chars", "sent", "lines"}` on an item with a cut line;
   - an expanded section of ordinary lines (about 11,000 characters) sent whole, with no cut key;
   - the long Markdown line cut with its neighbours whole, both alone and in an expanded section;
   - a narrowed register item carries a cut key only if its own lines hold a cut line (F2).
   - S3 stays: nothing else changes. Update its reference handling, so the comparison takes off only the cut lines'
     text and the cut key.
2. **F3:** run `tests/acceptance/W2-133/` against the expected behaviour. If its pinned comparison would still be
   touched by long-line cuts, say which cases and why, in your return; W2-133's folder is not yours to change.
3. Run your folder and `gov accept W2-135` through the heavy slot (a HOME whose `.local/lib` links to the real user
   site). Say which cases are red on integrate for the right reason, and which are green guards.

## Rules
As in your first brief: only `tests/acceptance/W2-135/`; the hidden-half rule; DEC-1080 (Read and Grep tools for
reading; one simple command per Bash call; no `cd … &&`; no `git -C`; one line before a command that will ask).
Commit with `--trailer "Task: DAEO-c4pb" --trailer "Implements: DEC-1086" --trailer "Role: independent-test-designer" --trailer "Rewrite-Reason: DEC-1086 B (review F1, F2)" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.

## Return
The twelve labelled fields, with the commit, the case list (red or green), `gov accept`'s counts and F3's answer.
