# W2-129 — the test designer's second pass: S16, ticket changes (DAEO-q7lk)

You are the independent test designer for **W2-129**. Your first pass wrote S1 to S15 (`5d5fe8ab`). The owner's
DEC-1088 (6), standing, adds **S16** to the ticket (read it: `.tickets/DAEO-q7lk.md`, the line marked `[added,
DEC-1088]`):
- a closed ticket is never edited;
- each change to an open ticket is marked with the decision that made it;
- `gov links` flags `CLOSED_TICKET_EDITED` and `TICKET_CHANGE_UNMARKED`.

The CTO merged integrate into your branch.

## What to do
In `/home/usain/gov-os-worktrees/W2-129-tests`, add cases to `tests/acceptance/W2-129/` for S16, on your planted
repository with planted commits:
- a commit that edits a ticket already closed before it: `CLOSED_TICKET_EDITED`;
- a commit that changes an open ticket's `kpis` (and one each for `allowed_paths`, `depends_on`, `title`) with no
  decision id in the changed lines nor in `Implements:` or `Decided-by:`: `TICKET_CHANGE_UNMARKED`, naming the ticket,
  the commit and the field;
- the same change with a `[re-worded, DEC-n]` mark in the line, or with `Implements: DEC-n`: no finding;
- a change of `status`, `assignee` or `links` alone: no finding;
- the role is orchestrator;
- the finding is listed only when the commit is in the range (`--since`).

Add the README rows (`| S16 | ... |`) in the runner's form. Leave S1 to S15 as they are. Run the folder and
`gov accept W2-129` through the heavy slot (`HOME=/home/usain`). S16's cases are red on today's branch for the right
reason (no such code yet).

## Rules
As in your first brief: only `tests/acceptance/W2-129/`; the hidden-half rule; DEC-1080 (Read and Grep tools for
reading; one simple command per Bash call; no `cd … &&`; no `git -C`; one line before a command that will ask).
Commit with `--trailer "Task: DAEO-q7lk" --trailer "Implements: DEC-1088" --trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.

## Return
The twelve labelled fields, with the commit, S16's case list (red or green, why), `gov accept`'s counts, and the
output format S16's lines assume.
