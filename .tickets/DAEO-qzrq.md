---
id: DAEO-qzrq
status: in_progress
deps: []
links: [DAEO-r30l]
created: 2026-11-01T21:35:00Z
type: task
priority: 0
assignee: engineer
external-ref: W2-123
tags: [wave-2, implementation, retrieval, speed, standard]
wbs_id: W2-123
title: 'The shared embedding server serves several requests at once within its CPU cap, with the vectors unchanged, and the cap is measured not to become the new limit (SIZING-1 option 0, DEC-1014)'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: []
allowed_paths:
- src/gov/retrieval/ollama.py
- src/gov/retrieval/semantic.py
- tests/unit/retrieval/test_w2_123*
- docs/changes/W2-123-evidence.md
kpis:
  success:
  - 'A rebuild''s embedding request that times out behind other clients on the shared server is retried, bounded (at most three tries with a growing wait, each try under the existing per-request timeout), and the semantic stage still ends not_recreated, named, after the last failed try: never a partial store reported as built; the tries and waits are stated in the rebuild''s result [DEC-1026, DEC-1015 item 4]'
  - 'When the Gov OS starts its shared embedding server (`ensure_available`), it sets the number of parallel requests and the CPU cap from one configuration value each (defaults from the measure below), and states them in its result; an unreadable value refuses to start the server (named), never an uncapped one [DEC-1014, DEC-1010 item 7]'
  - 'Determinism: with parallel requests the embedder returns the same vector for the same text as with one request at a time (checked on a fixed set of chunks, to the stored precision); a difference refuses the setting [DEC-1014]'
  - 'Measured, in docs/changes/W2-123-evidence.md: throughput (chunks per second) and a cold rebuild''s semantic stage at 1, 2, 4 and 8 parallel requests, under the 8-core cap and without it, alone and with three rebuilds at once; the setting chosen is the one where the 8-core cap is not the limit (or the cap is raised with the figures), and the figures are stated [DEC-1014, DEC-996 item 3 A]'
  - 'A product feature for every adopted repository: the parallel requests and the CPU cap are read from the gate''s configuration file (W2-20), with the measured defaults; nothing of this machine (its CPU numbers, its ports) is written in the code [DEC-1014 item 6, DEC-982]'
  - 'The shared embedding server comes with a health probe (a fixed text embedded within a configured time, stated healthy, slow or hung) and a safe restart (the hung server stopped, started again under its configured cap, the restart recorded), both callable by the dispatcher (W2-121); a restart never happens while the server is answering [DEC-1015 item 2]'
  - 'Both servers the Gov OS starts (`ensure_available` and `ensure_query_available`) start under their cap from the gate''s configuration file (W2-20), the query server CPU-only; every restart, whether the Gov OS''s own or the dispatcher''s safe restart (W2-121), keeps the cap; a planted start of each shows it [ACT-OLLAMA-CAP-2, DEC-1017]'
  failure:
  - 'Parallel requests that change a vector; a server started uncapped; a setting chosen without its measure [DEC-1014]'
profile: STANDARD
sources:
- DEC-1014
- DEC-1011
- DEC-1010
est_loc: 80
acceptance_tests:
  path: tests/acceptance/W2-123/
  author: independent-test-designer (MR-3)
track: A
list_rows: []
---
# W2-123 Parallel requests on the embedding server

The owner's DEC-1014 (SIZING-1 option 0): the shared embedding server answers one request at a time (`-np 1`), so every
rebuild and retrieval check queues behind it; ACT-OLLAMA-CAP-1 capped it at 8 cores. This ticket lets it serve several
requests at once, keeps every vector the same, and measures that the 8-core cap does not become the new limit (W2-20's
gate then counts the server's CPU, as SMART-WORK-3 proposed).
