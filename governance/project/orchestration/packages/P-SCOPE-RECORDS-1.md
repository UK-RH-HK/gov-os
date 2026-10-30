# P-SCOPE-RECORDS-1 — Governance edits stop widening closes: the path map's lists into record files of their own; prompts and briefs on the record-only list (DEC-929 item 1)

From: the W2 orchestrator, drafted 2026-10-29; delivered with the re-plan package. Six parts (DEC-818).

## 1. Context

- W2-66's path-scoped close (closed `f8d1f60a`) runs only the suites a change touches. It runs everything when a changed path is shared core, or is placed by nothing in the test map (`governance/project/test-map.yaml`, `shared_core` and `record_only`).
- **The path map is shared core.** It holds the configuration, and also four lists edited often: `load_sensitive`, `accepted_reds`, `accepted_history` and `acceptance_exemptions`.
- **Prompts and briefs are placed by nothing**, so they count as unplaced.
- Governance commits between closes therefore turn the next close into a full run. The owner asked for this package after the queue of 2026-10-27 (DEC-929 item 1). Meanwhile, non-urgent record commits wait for the gap between queues (DEC-929 item 2).

## 2. What happened (measured)

- **W2-66's close of 10-27 ran full on records alone.** Its evidence says `why_full: SHARED_CORE` (the path map) and `UNPLACED` (`LEAD-w2-common.md`, `w2-orchestrator.md`) (`docs/close/DAEO-c1uz/CL-DAEO-c1uz.md`, evidence block). That cost 4,186 s of tests against about 300 s for the scoped closes after it (annex B §2.1), about 65 extra minutes.
- **The six closes after it were scoped,** because only the queue's own record commits came between them.
- **W2-58's close of 10-28 ran full,** but for code (`src/gov/close/*`) as well as the path map. This package would not have scoped it.
- **Path-map list edits since 10-21:**
  - DEC-927's 39 accepted-history entries (`e95d3520`);
  - the W2-57 corrections and removals (`6367e965`);
  - DEC-891's and DEC-924's entries;
  - each owner commit of a ratchet or history entry.
  
  Each is a record by nature but shared core by its place.

## 3. Why it matters

Fast closes are the first item of the minimum for EXAMIN's copy (DEC-930 item 1). Today the owner's own commits of a ratchet entry, and my prompt and brief edits, each cost about an hour of machine time on the next close. They also push record work into the gaps between queues.

## 4. Options

| Option | What changes | Could let through | Cost |
|---|---|---|---|
| **(a) All three, as one small ticket (W2-78, STANDARD, engineer and test designer)** | (1) The four lists move from the path map into record files of their own, for example `governance/project/records/{load-sensitive,accepted-reds,accepted-history,acceptance-exemptions}.yaml`. The judge's readers read them: `gov.close.ratchet`, `history`, `gates`, `traceability`, the W1-01 history case. The record-reading set gains every test that reads them. (2) The path map's configuration stays shared core. (3) `governance/project/prompts/**` and `governance/project/briefs/**` join `record_only`, and every test that reads them joins the record-reading set (for example W2-62's session-start case). | **A shrinking list entry** (a removal) no longer forces a full run. A test it un-excuses would then run only in the next full close or the nightly, so a red could surface a night late, never be let through: the next full run judges it, and the nightly runs every night (DEC-933). **A growing entry** is an owner commit validated with the pinned readers (DEC-895), so it excuses nothing silently. **A prompt or brief edit** changes how agents work, not code: a test reading those files that the record-reading set misses would run only at night. The sweep for readers is part of the ticket's KPIs. | About 150 lines (readers, schema, migration, test map); one close slot; one re-pin. Owner commit: the list migration moves entries the owner committed, so the move itself is an owner commit, or is accepted by decision. |
| **(b) Prompts and briefs only** (a test-map change) | Item (3) alone. | As above, for prompt and brief edits only. | A few lines in `test-map.yaml` (W2-66's and W2-68's), through a ticket, since the test map is shared core. The lists still widen closes. |
| **(c) Not now** | Nothing. | Nothing new. | About an hour per widened close, and record work held between queues. |

## 5. Recommendation

**(a), as ticket W2-78**, started in the next free slot after W2-77. Its acceptance tests come from a fresh test designer and include:
- the record-reading set holds every reader of the moved lists, and of the prompts and briefs (a sweep test, as W2-66's live test map does for DEC-891's places);
- a removal from `load_sensitive` runs the ratchet's suites;
- a scoped close after a list edit stays scoped.

Confidence: medium-high. Measured gain: about an hour per close that only governance edits would have widened (one of the eight closes of 10-27).

## 6. What it blocks, and what waiting costs

- **It blocks** nothing outright.
- **Waiting costs** about an hour of machine time each time a governance edit lands between closes, and record commits held back while a queue runs (DEC-929 item 2).
- **What it does not fix:** code changes to shared core (as W2-58's on 10-28) still run full, by design.
