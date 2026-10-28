---
id: DAEO-2gc7
status: open
deps: []
links: []
created: 2026-10-28T22:19:23Z
type: task
priority: 1
assignee: engineer
external-ref: W2-68
tags: [wave-2, close, batch, full]
wbs_id: W2-68
title: 'Batched closes, reuse on the same code, and two fingerprints'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: []
allowed_paths:
- src/gov/close/batch.py
- src/gov/close/fingerprint.py
- src/gov/close/command.py
- src/gov/close/repo.py
- src/gov/store/**
- tests/unit/close/test_batch*
- tests/unit/close/test_fingerprint*
- tests/unit/store/test_fingerprint*
- docs/research/W2-68-batched-close.md
kpis:
  success:
  - 'A batch: queued closes on one integrated head share one rebuild, one gov check and one full regression on that head; then each ticket''s own checks run one after another (its acceptance suite, the record-reading set, its trailers, paths, probe record and checkpoint); no code merges while a batch runs; each close record cites the batch''s run (fingerprint, commit, JUnit XML) and its scope [DEC-883 item 1, DEC-890]'
  - 'A red batch: failing tests re-run alone first, and a red that passes alone is a flaky candidate, not bisected; a red that fails alone is attributed by git bisect over the batch''s merges, or by the failing tests'' own ticket, with the evidence; nothing closes on a red run; the causing ticket is repaired and the batch re-runs; an unrelated ticket waits for a green run; an outside cause is fixed by the orchestrator and recorded [DEC-883 item 2, DEC-889 item 2 b]'
  - 'Same code: a close whose code fingerprint (record-only paths left out, the test map''s record_only list read, not written) equals the last fully passing run''s reuses it, and runs its own checks and the record-reading set; a failing run is never reused; the reused evidence states the reused run''s skip count, so a silent skip is not inherited unseen [DEC-883 item 3, DEC-889 item 2, I4 F2]'
  - 'Two fingerprints: the code fingerprint governs the code index; changed record files refresh their lexical and semantic chunks incrementally; a lexical index whose record files differ is never fresh [DEC-889 items 2 and 4]'
  - 'The path map counts as code for the fingerprint: it is in the shared core (DEC-880), so a change to it runs fresh [DEC-880, DEC-899]'
  - 'Re-read against two fingerprints: W1-30''s test_a_store_rebuilt_without_embeddings_is_stale_one_commit_later, by this ticket''s test designer, with a Rewrite-Reason [DEC-889, I2 section 2.6, DEC-906]'
  - 'A measured trial on a fixture or dev-tier programme: the time per batch; reuse correct; a planted code change forcing a fresh run; a planted record-only commit running the set and nothing else; a red batch attributed, with nothing closing on it [DEC-884 item 4]'
  failure:
  - A close that cites a red run or another fingerprint's run; a reused run on different code; a store accepted on another code fingerprint; a lexical index fresh with changed records; a code merge during a batch; a red that passes alone being bisected; reused evidence that hides a skip.
profile: FULL
sources:
- DEC-883
- DEC-884
- DEC-889
- DEC-890
- DEC-880
- DEC-899
- DEC-936
est_loc: 300
acceptance_tests:
  path: tests/acceptance/W2-68/
  author: independent-test-designer (MR-3); written before implementation; also W1-30's test_a_store_rebuilt_without_embeddings_is_stale_one_commit_later (Rewrite-Reason)
track: A
list_rows: []
---
# W2-68 Batched closes, reuse on the same code, and two fingerprints

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-68), confirmed at the review point (DEC-899, P-IS-1 to P-IS-7 (a)); keystone 2.

- **Why:** the queue of 2026-10-21 ran six closes on the same code, about 85 minutes each (DEC-883). Queued closes on one head share one regression; a close on code that already passed reuses that run; a store built on the same code fingerprint is fresh. The queue of 2026-10-27 measured the cost of not batching: each close's own gates took about 12 minutes, longer than the scoped close itself.
- **Starts** now (DEC-936 item 2: the third re-pin carries W2-68 and W2-71). Its condition is met: W2-66 has merged and passed its ladder (closed 2026-10-27, `f8d1f60a`), and its entry criterion holds, since the record-reading set is settled in W2-66's test map (P-IS-2).
- **Paths:** `command.py` for the calls and the record's lines only; `repo.py` for the store-freshness check only; `src/gov/store/**` for the fingerprints a rebuild records and the incremental record load only.
- **Not in this ticket:** package P-SCOPE-RECORDS-1 (DEC-929 item 1: the path map's lists into record files of their own, prompts and briefs on the record-only list) is the owner's to decide. If the owner places it here, the ticket is amended before the engineer starts.
- **Rides:** the third re-pin, with W2-71, as each merges and passes its checks (DEC-933 item 1).
