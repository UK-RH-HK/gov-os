---
id: DAEO-jpr0
status: in_progress
deps: [DAEO-qzrq]
links: [DAEO-blwa, DAEO-qzrq]
created: 2026-11-02T12:41:50Z
type: task
priority: 0
assignee: engineer
external-ref: W2-126
tags: [wave-2, implementation, retrieval, speed, standard]
wbs_id: W2-126
title: 'A machine-wide vector cache keyed by the text: each text is embedded once on the machine, whatever tree, clone or code asks (P1-LOAD-BALANCE-1 lever b.1 and b.6, DEC-1032)'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-qzrq
allowed_paths:
- src/gov/retrieval/semantic.py
- src/gov/retrieval/vector_cache.py
- tests/unit/retrieval/test_w2_126*
- docs/changes/W2-126-evidence.md
kpis:
  success:
  - 'Before it embeds a chunk or a question, the semantic stage and `query_vector` look up a machine-wide cache keyed by the model, its revision and the sha256 of the exact text sent; a hit uses the stored vector and sends nothing to the embedder; a miss embeds and stores the vector; the cache sits in the user''s own folder (one file, mode 0600), shared by every tree and clone on the machine [DEC-1032, P1-LOAD-BALANCE-1 b.1]'
  - 'The same vector for the same text: a cached vector is byte-for-byte what the embedder returned when it was stored; a rebuild of a tree whose chunks are all cached embeds nothing and its store equals the one built without the cache (the vectors byte for byte) [DEC-1032]'
  - 'Safe under many writers: concurrent rebuilds and searches read and write it at once without a corrupt entry, a lost write that is later read as a vector, or a lock held across an embedding request; an unreadable or locked cache is skipped (the text is embedded), named in the result, never a failure [DEC-1032]'
  - 'Bounded: a configured size limit (default from the measured corpus: about 2 corpora) with least-recently-used eviction; a model or revision change starts a new key space and never serves another model''s vector [DEC-1032]'
  - 'The retrieval check''s dev tiers (a-dev, b-dev) and their 52 questions are embedded once on the machine and hit the cache in every later `gov check`, with no cold embedding per check [DEC-1032, P1-LOAD-BALANCE-1 b.6]'
  - 'Measured, in docs/changes/W2-126-evidence.md: the texts sent to the embedder per day before and after (target: under one corpus, about 54,000, against about 503,000 in 13 hours on 2026-11-01/02); a lead''s first rebuild of a code-changing ticket and a close''s clone, before and after; the cache''s size [DEC-1032]'
  failure:
  - 'A vector served for a different text, model or revision.'
  - 'A store built with the cache that differs from one built without it.'
  - 'A rebuild or search that fails because of the cache.'
profile: STANDARD
sources:
- DEC-1032
- DEC-1031
- DEC-1015
- DEC-374
est_loc: 150
acceptance_tests:
  path: tests/acceptance/W2-126/
  author: independent-test-designer (MR-3)
track: A
list_rows: []
---
# W2-126 A machine-wide vector cache keyed by the text

The owner's DEC-1032 (P1-LOAD-BALANCE-1, levers b.1 and b.6): about 503,000 texts went through the shared embedder in
13 hours on 2026-11-01/02, nine full copies of the corpus, because every new tree, clone and close embeds its chunks
again, and W2-122's seeding is refused for any tree whose `gov` code differs from the base. A chunk's vector depends
only on the model, its revision and the text sent, not on the `gov` code, so one cache keyed by them, shared on the
machine, makes every text embedded once. It also makes the retrieval check's dev tiers and questions free after their
first use, and makes vectors reproducible across rebuilds (P-W2-123-2). The test designer starts at once from these
KPIs; the engineer starts when W2-123 (which holds `semantic.py` for the bounded retry, DEC-1026) has landed.
