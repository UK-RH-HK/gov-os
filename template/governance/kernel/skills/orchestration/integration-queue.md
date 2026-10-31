# Orchestration: the integration queue

A reference file of the orchestration skill, one level below `SKILL.md`. It states the method; the guard decides
(CAP-24.b). A project's own values stand as `<placeholders>` (DEC-539).

The merge queue tests each candidate merge before the integration branch moves, so the branch is never red from a
merge nobody tested (DEC-959 item 1).

## Enqueue

- The stream's Senior Engineer (the orchestrator, where there are no streams) enqueues a ticket once its lead's
  DONE is verified (every KPI clause read against the tests and the code, DEC-449) and its QA findings are settled.
- The entry names the ticket, its branch head and the lead's scoped run on it.

## Test the candidate merge

- `<the project's queue tool>` merges the batch's heads onto the head of `<integration branch>` in a scratch clone,
  under the merge rule: `Task:` on every merge, never `-s ours`, never dropping a ticket's side, never removing what
  git's own merge keeps (DEC-750, DEC-754).
- If the merged code is identical to what a lead tested, that run stands and nothing re-runs. Otherwise the scoped
  set (the union of the batch's selections) runs once on the merged result; never the full suite, which runs only
  in the nightly (DEC-959 item 1, DEC-968 item 1).

## Advance or eject

- **Green:** `<integration branch>` advances to the tested merge, and nothing else.
- **Red:** each failing case is re-run alone with the batch's merges reverted. Still failing there, it is not the
  batch's: the batch goes on, the record names it, and it is dealt with at once (DEC-968 items 2 and 3). Passing
  there, the culprit is found by taking each ticket's merges out in turn: the culprit goes back to its lead and the
  rest advance on the same run. A failure no single ticket explains refuses the whole batch (DEC-979 item 3).
- A merge that cannot be reverted, or a run that errors, refuses: the queue fails closed.

## Record

For each batch, in `<the project's close record path>`: the heads, the tested merge commit, the selection's scope,
the results, the cases not caused by the batch, and each ejected ticket with its reason. The close cites this run
(DEC-959 item 1).

## Never

- Push: the push is the owner's (DEC-959 item 2).
- Advance on an untested merge, or weaken a check to let a batch through (DEC-768 item 4).
