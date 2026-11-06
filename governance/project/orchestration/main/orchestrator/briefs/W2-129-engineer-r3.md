# W2-129 — the engineer's round 2 of review: F2, F1, F3 (DAEO-q7lk)

You are the engineer for **W2-129**, resumed. The review (`.gov-runtime/scratch/orchestrator/reviews/w2-129.md`; read
F1 to F5) passes every line but S16, on F2.

## Fix
- **F2 (blocks):** `check.py:802` skips the other changes in a commit that closes a ticket. Check the eight watched
  fields (`title`, `kpis`, `allowed_paths`, `reads`, `needs`, `waits_on`, `depends_on`, `acceptance_tests`) in a closing
  commit exactly as in any other commit against an open ticket: an unmarked change is `TICKET_CHANGE_UNMARKED`. The
  status change itself (and `assignee`, `links`) is still not a finding. Add a unit test on a planted repository.
- **F1 (rides along):** UNMARKED_CHANGE and `--propose-marks` ignore the changing entry's status. A PROPOSED, REJECTED or
  WITHDRAWN entry that states `Supersedes:` or a change is not a changer: no UNMARKED_CHANGE, and no proposed mark. Add
  a unit test.
- **F3 (record):** write the CTO's measured timing into `docs/research/W2-129-links.md`. On the main tree at
  `416b59da1779`, the median of five runs: `--all` 3.14 s; `--since HEAD~1` 2.94 s. The first `--all` gave 3,037
  standing findings, by code and role:
  - UNMARKED_CHANGE orchestrator 188;
  - UNKNOWN_ID: independent-test-designer 381, orchestrator 56, owner 1, product-spec 3;
  - UNLINKED_ID orchestrator 1,897;
  - STATUS_CONFLICT: orchestrator 110, product-spec 6;
  - NOT_IN_FORCE_AS_RULE: orchestrator 35, product-spec 106;
  - ENFORCES_SUPERSEDED independent-test-designer 44;
  - CLOSED_TICKET_EDITED orchestrator 117;
  - TICKET_CHANGE_UNMARKED orchestrator 93.

  These are the clean-up's baseline.

F4 and F5 are rows; leave them.

## Rules
As before:
- your paths only;
- never read `tests/acceptance/W2-129/` (the designer is adding F2's cases in parallel; the CTO merges them after you);
- every run through the heavy slot; `gov accept W2-129` with `HOME=/home/usain`;
- the hidden-half rule;
- DEC-1080 (Read and Grep tools; one simple command per Bash call; no `cd … &&`; no `git -C`; one line before a command
  that will ask);
- do not merge integrate.

Commit with `--trailer "Task: DAEO-q7lk" --trailer "Implements: DEC-1088" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.

## Return
The twelve labelled fields, with the diff's size, the new unit tests and `gov accept`'s counts.
