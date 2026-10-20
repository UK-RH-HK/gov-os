
## W1-50 follow-up residuals (a public judgement of commits, DEC-453, 2026-10-07)

- **Built:** `gov.guard.containment.judge_commits(root, commit_ids)` returns one finding (commit, paths,
  reason) per commit that the post-command check would flag in an orchestrator's own call; it calls the same
  per-commit judgement and the same reading of commits and merges (the parsing loop was split out so both use
  it; the 642 earlier cases are unchanged and green). It only reads. An empty list, an unknown id, a path that
  is not a repository and a git failure raise `ContainmentError`.
- **For `gov close` (W1-30):** it is called with the ticket's commits; any finding refuses the close. W1-30's
  private rule set is removed in that ticket.
- **It judges as the orchestrator's own call does** (each commit by its own `Role` and `Task` trailers); it has
  no caller's role or ticket to judge against. A commit naming a closed ticket is judged against that
  ticket's close commit, as in the check.
- **Learning metrics:** one designer turn and one engineer turn started by the orchestrator; 24 cases added;
  107 lines added and 19 removed in the module, 237 lines of unit tests.
- **Regression at `3d715a35`:** every suite green except W1-46's 23 live-session cases, which errored while
  three other test runs were going (DEC-372); W1-46 alone: 493 passed.
