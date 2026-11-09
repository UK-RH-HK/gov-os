# W2-56 follow-ups R3, R5 — lead checkpoint (DAEO-wnnz; DEC-1112 (3), DEC-1114)

- 2026-11-09 23:14 UTC: worktrees W2-56-f-tests (w2/W2-56-f-tests) and W2-56-f (w2/W2-56-f) from w2/integrate 336828354.
- R5 decided (lead, under the CTO's delegation): a lead gets the launcher's own GOV_STORE (W2-116's configured
  integration_store, from the main repository's rebuild.yaml), never the parent's; TERM and TMPDIR not passed
  (S5's list; -p sessions; DEC-743 item 7). Within S5 ("the launcher's own values"; CIT-E §6 names GOV_STORE):
  no DEC-105 package.
- R3: the next test run removes a killed run's per-session folders (gov-cbm-<uid>-*, gov-path-*) whose owner is gone;
  live owners kept; unrecorded folders kept unless older than 24 h; links, other users', /tmp/gov-cbm-<uid> never.
- Designer launched 23:14 UTC, pid 3504466, brief briefs/W2-56-designer-f.md (xhigh). Next: merge its tests into
  w2/W2-56-f, red check, engineer (high) with the README's interface section, gov accept, review (max), merge.
- Loop count: lead's own.
