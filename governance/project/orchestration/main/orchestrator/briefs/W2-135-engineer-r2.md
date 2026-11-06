# W2-135 — the engineer's round 2: cut lines, not items (DAEO-c4pb)

You are the engineer for **W2-135**, resumed. The review (`.gov-runtime/scratch/orchestrator/reviews/w2-135.md`; read
F1 to F4) found that the first cut reached whole items of ordinary lines, so an agent could lose the line that answers.
DEC-1086 B says "a guard against one-line files only". The CTO re-worded **S1 and S2** (read the ticket again:
`.tickets/DAEO-c4pb.md`, its "Round 2" notes) and added `src/gov/decisions/register.py` to your paths. The designer's
round-2 cases and integrate are merged into your branch.

## The change
- In `item()`: **each line over 4,000 characters** is sent as its first 4,000 characters. Measure a line without its
  newline; a cut line keeps its newline. **Every other line is sent whole.** An item of ordinary lines is never cut,
  however long.
- An item with a cut line carries `cut: {"chars": <the item's full text length>, "sent": <the length sent>, "lines":
  [<the line numbers cut>]}`. Path, lines, id, chunk id and sha256 are those of the full span. The budget's `used` is
  still counted on the full text.
- **F2, in `register.leave_out`'s `narrowed()`:** a narrowed register item carries a `cut` key only if its own lines
  hold a cut line, with its own figures; otherwise no key. Its text goes through the same line cap.
- Nothing else changes (S3).

## Tests and rules
As in your first brief:
- your unit tests revised to the new S1 and S2;
- the evidence record updated;
- every run through the heavy slot;
- `gov accept W2-135` with a HOME whose `.local/lib` links to the real user site;
- then `tests/unit/retrieval`, `tests/unit/decisions`, `tests/acceptance/W2-32` and `tests/acceptance/W2-133`, with the
  standard exclusion. The 18 W2-112 socket cases fail inside the sandbox; the CTO runs them outside.

Never read `tests/acceptance/W2-135/`. The hidden-half rule. DEC-1080 (Read and Grep tools; one simple command per Bash
call; no `cd … &&`; no `git -C`; one line before a command that will ask). Do not merge integrate.

Commit with `--trailer "Task: DAEO-c4pb" --trailer "Implements: DEC-1086" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.

## Return
The twelve labelled fields, with the diff's size, the unit tests, `gov accept`'s counts and the regression counts.
