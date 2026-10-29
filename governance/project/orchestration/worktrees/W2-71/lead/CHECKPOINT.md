# W2-71 lead checkpoint (DAEO-e8f0, run 2: F1, partial clones) — IN PROGRESS

- Run 1: DONE at 1598a1c0996c (probe PR-DAEO-e8f0 passed at 700102de5f4d). Run 1's record follows below the line.
- Run 2 (the last round, DEC-413) started 2026-10-29 12:24, from P1-MORNING-2026-10-29 item 4 (orchestrator's delegated decision, stricter only).
- The rule: in a partial clone (extensions.partialClone, any remote with promisor true, any partialclonefilter; an unreadable configuration counts as one), the exemption asks git nothing about objects and the finding stays. GIT_NO_LAZY_FETCH=1 on the object lookup as a second guard (git here is 2.43.0, which ignores it; 2.44 honours it).
- Trailers: Implements: DEC-911 only. This worktree's register stops at DEC-937, so DEC-938 would not resolve in the trailer gate (it reads the worktree's register).
- Order: td-2 (test designer, xhigh) -> red check -> eng-2 (engineer, high) -> rebuild + full run -> rev-2 (reviewer, max) -> probe record -> return.
- Loop count: 0 (engineer iterations this run).
- State: writing td-2 brief.

---

# Run 1's final record

- State: done. The probe passed; nothing more committed after 1598a1c0 (the probe record of head 700102de5f4d).
- Commits since 51a443a47ae8: 8d5a99274dc5 test designer (213 cases); a63e012f6745 engineer (src/gov/secrets/__init__.py); baf2a759a241 engineer (unit tests); 2a58872b, 700102de5f4d checkpoints; 1598a1c0 probe record.
- Verification: rebuild 0; gov check GREEN except YELLOW core-decision-citations and openspec-validate; parallel 1 failed (DEC-919 known) / 16696 passed / 31 skipped; serial 180 passed; collect-only no error; keyword_warn 0.
