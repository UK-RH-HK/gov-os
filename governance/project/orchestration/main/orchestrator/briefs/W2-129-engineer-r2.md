# W2-129 — the engineer's second pass: S9's commit role, and S16 (DAEO-q7lk)

You are the engineer for **W2-129**, resumed. Your first pass (`gov accept` 102 of 103) is on `w2/W2-129`. The CTO has
merged in the designer's S16 cases and integrate. Two things to do, then `gov accept` again.

## 1. S9's one red: a commit's finding names the commit's role first
The KPI reads: "a commit's finding names its Role: and, once landed, the ticket's lead (orchestrator)". Your tool put
`orchestrator` in the role field and moved the commit's role into the fix text.
- **The reading:** the **role field names the commit's `Role:` trailer** (for example `independent-test-designer`).
- Where the commit has landed, the field adds the lead after it, for example
  `independent-test-designer; once landed: orchestrator`.
- A commit with no `Role:` names `orchestrator`.

## 2. S16, ticket changes (DEC-1088 (6), standing)
Read the line marked `[added, DEC-1088]` in `.tickets/DAEO-q7lk.md`.
- A commit in the range that changes a closed ticket's file is `CLOSED_TICKET_EDITED`. Closed means the ticket's status
  in the commit's parent; a decision mark does not excuse it.
- A commit that changes an open or in-progress ticket's `title`, `kpis`, `allowed_paths`, `reads`, `needs`,
  `waits_on`, `depends_on` or `acceptance_tests`, with no `DEC-n` in the changed lines (added or removed) nor in its
  `Implements:` or `Decided-by:` trailers, is `TICKET_CHANGE_UNMARKED`. It names the ticket, the commit (a short sha)
  and the field.
- A change of `status`, `assignee` or `links` alone on an open ticket is not a finding. The closing commit itself is
  not a finding.
- The role is orchestrator. The finding line keeps the form of the others: `CODE ids … | path:line | role | fix`.
- It is listed only when its commit is in the range.

## Where you work
Your worktree `/home/usain/gov-os-worktrees/W2-129`, your paths as before. Never read `tests/acceptance/W2-129/`.
Update `docs/research/W2-129-links.md`: the S9 reading, S16's form, and the `--all` run's counts on the main tree again.

## Tests and rules
As in your first brief:
- unit tests in `tests/unit/links/`;
- every run through the heavy slot;
- `gov accept W2-129` with `HOME=/home/usain`;
- the hidden-half rule;
- DEC-1080: Read and Grep tools; one simple command per Bash call; no `cd … &&`; no `git -C`; one line before a command
  that will ask;
- do not merge integrate.

Commit with `--trailer "Task: DAEO-q7lk" --trailer "Implements: DEC-1088" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.

## Return
The twelve labelled fields, with `gov accept`'s counts (all 135 cases), the unit tests, and the `--all` counts and time.
