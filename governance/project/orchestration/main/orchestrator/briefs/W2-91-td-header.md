# W2-91 (DAEO-a3u2) — resume: TD-1 and TD-2 decided, verification by the merge queue (DEC-1013, delegated)

**Read this first; it overrides the steps below where they differ.** Your run 1 is accepted at `f652eeae3911`
(`gov accept` 8 of 8). The CTO decided: **TD-1 (a)**: KPI 3 is narrowed to what exists (the overlay stays restricted;
the indexer reads embedding_policy only); the export command is Wave 3 row W3-P18; adjust your own cases only if one
asserts the dropped export clause, nothing lowered. **TD-2 (a)**: W2-86's guard case
(`test_guard_outside_template_every_verdict_as_at_the_base`) joins your paths: one fresh independent test designer
revises it to leave DEC-957's three newly embedded sets (the root files, `governance/**`, `schemas/**`) out of its
comparison, `Rewrite-Reason: DEC-957, DEC-1013`, no other expectation lowered. Merge the tests branch while no worker
runs; `gov accept DAEO-a3u2` once. **VERIFY-1**: do NOT rebuild or run the scoped set: the merge queue's run on the
merged result is your verification (DEC-959 item 1). Return DONE with the exact head.

---

