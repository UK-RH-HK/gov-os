---
id: (assigned by tk at creation, when W2-66 has merged; W2-68 has no ticket yet)
status: open
type: task
priority: 1
assignee: engineer
external-ref: W2-68
tags: [wave-2, close, batch, reuse, fingerprint, full, keystone-2]
wbs_id: W2-68
title: 'Batched closes, reuse on the same code, and two fingerprints'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: [DAEO-c1uz]
allowed_paths:
- src/gov/close/batch.py
- src/gov/close/fingerprint.py
- src/gov/close/command.py
- src/gov/close/repo.py
- src/gov/store/**
- tests/unit/close/test_batch*
- tests/unit/close/test_fingerprint*
- tests/unit/store/test_fingerprint*
- tests/acceptance/W1-30/test_w1_30_store*
- docs/research/W2-68-batched-close.md
kpis:
  success:
  - 'A batch: queued closes on one integrated head share one rebuild, one gov check and one full regression on that head, then each ticket''s own checks one after another (its acceptance suite, the record-reading set, its trailers, paths, probe record and checkpoint); no code merges into w2/integrate while a batch runs; each close record cites the batch''s run (fingerprint, commit, JUnit XML) and its scope [DEC-883 item 1]'
  - 'A red batch: failing tests are re-run alone first, and a red that passes alone is a flaky candidate, not bisected; a red that fails alone is attributed by git bisect over the batch''s merges or by the failing tests'' own ticket, recorded with the evidence; nothing closes on a red run; the causing ticket is repaired and the batch re-runs; an unrelated ticket waits for a green run; an outside cause is fixed by the orchestrator and recorded [DEC-883 item 2, DEC-889 item 2 b]'
  - 'Same code: a close whose code fingerprint (the test map''s record-only paths left out) equals the last fully passing run''s reuses that run, and runs its own checks and the record-reading set; a failing run is never reused; any code difference runs fresh; the reused evidence states the reused run''s skip count [DEC-883 item 3, DEC-889 item 2, I4 F2]'
  - 'Two fingerprints: the code fingerprint governs the code index; changed record files refresh their lexical and semantic chunks incrementally; a lexical index whose record files differ is never fresh [DEC-889 item 2 (item 4)]'
  - 'The path map counts as code for the fingerprint (it is in the shared core, DEC-880), so a change to it runs fresh [P-IS-2, I-SYNTHESIS §4]'
  - 'W1-30''s test_a_store_rebuilt_without_embeddings_is_stale_one_commit_later is re-read against two fingerprints by its test designer, with a Rewrite-Reason [I2 §2.6]'
  - 'The trial on a fixture repository or a dev-tier programme, measured and reported in docs/research/W2-68-batched-close.md: the time per batch; reuse correct; a planted code change forcing a fresh run; a planted record-only commit running the set and nothing else; a red batch attributed, nothing closing on it [DEC-884 item 4]'
  failure:
  - A close citing a red run or another fingerprint's run; a reused run on different code; a store accepted on another code fingerprint; a lexical index fresh with changed records; a code merge during a batch; a red that passes alone being bisected; reused evidence hiding a skip.
profile: FULL
sources:
- DEC-883
- DEC-884
- DEC-889
- DEC-890
- DEC-896
est_loc: 300
acceptance_tests:
  path: tests/acceptance/W2-68/
  author: independent-test-designer (MR-3); written before implementation
track: A
list_rows: []
---
# W2-68 Batched closes, reuse on the same code, and two fingerprints

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-68), from DEC-883, DEC-889 item 2, DEC-890 (the split) and lens I's P-IS-2.

- **Starts** when W2-66 has merged and passed its ladder. Its entry criterion is the record-reading set settled in W2-66's test map. The second re-pin follows it (DEC-889 item 15).
- **Reads, never writes,** the test map's record-only list (W2-66's file).
