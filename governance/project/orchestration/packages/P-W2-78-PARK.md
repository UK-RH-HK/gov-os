# P-W2-78-PARK: park W2-78's branch instead of merging it (an addendum to PLAN-W2-DEC953's Q5)

From the W2 orchestrator, 2026-10-30, for the owner, with the plan's review. It replaces W2-78's three packages (P-W2-78-MIGRATION, P-W2-78-COMMAND, P-W2-78-EARLIER-SUITES), which were written under the rules before DEC-953.

1. **Context.** W2-78 (DAEO-v4is) was started on 10-29 so that governance edits stop widening closes: it moves the path map's four ratchet lists (`accepted_reds`, `load_sensitive`, `accepted_history`, `acceptance_exemptions`) into record files of their own under `governance/project/records/`, and makes prompts and briefs record-only in the test map. DEC-953 has since lifted the ratchet lists as gates (item 1). Item 4a gets the same effect without a test-map change: `select_tests.py` leaves the governance files out of the change. The plan's Q5 assumed W2-78 was nearly done ("finish and close as built").
2. **What happened.** The lead returned at 17:00 (4.27 h, $8.31). The code is done: 90 of 90 of its own tests pass and its builder tests pass. But the full run had 81 reds:
   - 79 in earlier suites (W2-01 25, W2-53 26, W2-07 8, unit `test_history` 13, `test_ratchet` 4, `test_w2_07_decision_records` 2, W2-66 1). Their fixtures plant the lists in the path map without record files, which W2-78's code now refuses;
   - W1-08, red until a namespace line is added for `governance/project/records/**`;
   - one load timeout that passed alone.
   Merging needs:
   - a test-designer batch to revise those suites (about half a day);
   - two owner ACTs on the path map (a namespace line; then the four lists removed);
   - a one-line fix in `src/gov/close/command.py`;
   - a re-pin;
   - updates to the outside readers (`nightly_alone.py` and the orchestrator's tools).
3. **Why it matters.** Under DEC-953 none of that serves this repository's development: the lists no longer gate anything here, and governance edits no longer widen runs. Merging now would spend about a day of the memory and K3 critical path on machinery, the cost DEC-953 set out to stop.
4. **Options.**
   - **(a) Park:** keep the branch `w2/W2-78` and its worktree's commits unmerged; mark the ticket parked for Wave 3 hardening, or for when the Gov OS is whole and the lifted gates come back. Cost now: none. Risk: none; nothing on `w2/integrate` changes.
   - **(b) Finish and merge** as the lead proposed: about half a day of test revisions, two owner ACTs, a re-pin and the reader updates.
   - **(c) Merge only the test-map part** (prompts and briefs record-only): `select_tests.py` already covers it, so it adds nothing now.
5. **Recommendation:** (a), high confidence. Classification: no finding; a sequencing and scope call under DEC-953. The lead's discoveries go to the Wave 2 list as rows: `gov.check.pathmap` checks nothing when `namespaces` is a mapping (fails open: a row for the memory and records work); `gates.RECORD_PREFIXES` lacks `governance/project/records/`; W2-62's prompt case uses stand-in prompts.
6. **What it blocks:** nothing. W2-78 drops from the closes; the plan's Wave 2 count falls by one, and Q5 becomes "W2-76 finish and close; W2-78 parked".
