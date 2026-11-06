# W2-129 — the test designer's third pass: S16 in a closing commit (DAEO-q7lk)

You are the independent test designer for **W2-129**. The review (`.gov-runtime/scratch/orchestrator/reviews/w2-129.md`,
finding F2) found that S16 is not checked in a commit that **closes** a ticket. If the closing commit also rewrites
`kpis`, `allowed_paths` or `acceptance_tests` with no decision id, nothing is reported. The KPI exempts only "status,
assignee or links alone", and DEC-1088 (6) says `gov links` flags any change without a decision.

## What to do
In `/home/usain/gov-os-worktrees/W2-129-tests` (merge `w2/integrate` first if it moved: `git merge w2/integrate`),
add to `tests/acceptance/W2-129/` (S16):
- a commit that closes an open ticket **and** changes its `kpis` with no decision id: `TICKET_CHANGE_UNMARKED`, naming
  the ticket, the commit and `kpis`;
- the same with `allowed_paths` and with `acceptance_tests`;
- a closing commit that changes only `status` (and `assignee`): no finding (a guard);
- a closing commit whose `kpis` change carries `[re-worded, DEC-n]`: no finding (a guard).

Add the README rows (`| S16 | ... |`). Leave every other case. The new reds are red on the branch for the right
reason. Run the folder and `gov accept W2-129` through the heavy slot (`HOME=/home/usain`).

## Rules
As before: only `tests/acceptance/W2-129/`; the hidden-half rule; DEC-1080 (Read and Grep tools; one simple command per
Bash call; no `cd … &&`; no `git -C`; one line before a command that will ask). Commit with
`--trailer "Task: DAEO-q7lk" --trailer "Implements: DEC-1088" --trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.

## Return
The twelve labelled fields, with the commit, the new cases (red or green) and `gov accept`'s counts.
