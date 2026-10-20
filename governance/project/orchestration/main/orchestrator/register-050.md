
## 50. Owner decisions: integration merges, the W1-01 history test, and containment by commit trailers (W1-50) (register v0.50, appended by the W1 orchestrator on branch `w1/integrate`)

Owner decisions of 2026-10-04, on the orchestrator's P1 package (the W1-37 merge commit `00e3d539` made
`test_only_the_test_designer_commits_to_acceptance_tests` of W1-01 fail) and its package on containment findings.

### DEC-253 — The W1-01 history test accepts an integration merge of test-designer commits
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on the P1 package, option (a) · **Under:** MR-3, DEC-235, DEC-106
- **Decision:**
  - A test designer revises `test_only_the_test_designer_commits_to_acceptance_tests` so that an integration merge
    commit passes when every change it brings under `tests/acceptance/` comes from commits on the merged side
    carrying `Role: independent-test-designer`.
  - Every non-merge commit is still checked exactly as now.
  - The revision is recorded as a rewrite after implementation, reason "owner decision: integration merges".

### DEC-254 — Merge findings and worker-commit misattributions are records, for now
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER, on the containment package, option (a) · **Under:** DEC-171, DEC-235, DEC-206
- **Decision:** Until W1-50 is built, a containment finding raised by an integration merge of the main
  orchestrator, and a finding that attributes a worker's commit to the call of the lead that was waiting for it, are
  records of permitted actions. They are noted in `governance/project/bootstrap.md` and in each ticket's close row;
  they are not defects.

### DEC-255 — New ticket W1-50: containment attribution by commit trailers
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER · **Under:** CAP-58, DEC-076, DEC-182, DEC-235 · **Amends:** the Wave 1 ticket set (49 → 50 tickets)
- **Decision:**
  - A new ticket, W1-50: role engineer, profile FULL, priority high, depends on W1-03.
  - KPIs:
    - a forward HEAD move, including an integration merge by the orchestrator, is judged commit by commit: each
      commit's paths against the allowed paths of its own `Role` and `Task` trailers, not against the caller;
    - a merge commit itself is not a finding when every commit it brings passes that check;
    - a worker's commit made during another actor's call is judged by its own trailers;
    - a commit with no `Role` or `Task` trailer is judged against the caller, as today.
  - Allowed paths: `src/gov/guard/containment*`, `template/governance/kernel/hooks/posttooluse*`,
    `template/governance/kernel/hooks/pretooluse*`, `tests/unit/containment/**`.
  - Its test design batch also carries the W1-01 revision of DEC-253.
  - The Contract gets a covers item under CAP-58, in its own commit.
  - Written by the orchestrator to make the ticket valid, and open to the owner's change: the estimate of 100 LOC
    and the failure KPI lines, which mirror the success lines.

### DEC-256 — Order of work around W1-50
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER · **Under:** DEC-235
- **Decision:**
  - W1-50 is claimed now, and only its test design batch runs, in its own worktree.
  - That batch is merged, with the revised W1-01 test included.
  - The orchestrator confirms W1-01 is green on `w1/integrate` (the W1-37 merge then passes).
  - Merges and closes resume, W1-37 included.
  - W1-50's implementation starts after W1-46 is merged, because both touch `src/gov/guard/**`.

| Version | Date | Change |
|---|---|---|
| 0.50 | 2026-10-04 | Owner decisions: DEC-253 (the W1-01 history test accepts an integration merge whose acceptance-test changes all come from test-designer commits; a rewrite after implementation, "owner decision: integration merges"), DEC-254 (merge findings and worker-commit misattributions are records for now), DEC-255 (new ticket W1-50, containment attribution by commit trailers; engineer, FULL, priority high, depends on W1-03), DEC-256 (W1-50's test batch first and merged; then merges and closes resume; its implementation after W1-46). |
