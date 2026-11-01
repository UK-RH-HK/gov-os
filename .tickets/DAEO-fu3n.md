---
id: DAEO-fu3n
status: open
deps: [DAEO-nqa2, DAEO-zpdj, DAEO-3r1j]
links: [DAEO-nqa2, DAEO-8lmb]
created: 2026-11-01T15:30:00Z
type: task
priority: 1
assignee: independent-test-designer
external-ref: W2-90c
tags: [wave-2, test-revision, guard, lite]
wbs_id: W2-90c
title: 'The cases of W2-90b that need W2-105 (the template''s install block removed) or W2-110 (a product''s CTO-only install rule): W2-90''s seven named reds and any case W2-90b names (the owner''s split, DEC-999)'
class: test-revision
state_class: AUTHORITATIVE
role: independent-test-designer
depends_on:
- DAEO-nqa2
- DAEO-zpdj
- DAEO-3r1j
allowed_paths:
- tests/acceptance/W1-05/test_w1_05_live_hooks.py
- tests/acceptance/W1-05/conftest.py
- tests/acceptance/W1-46/test_w1_46_research_installs.py
- tests/acceptance/W1-46/conftest.py
- tests/acceptance/W2-59/test_w2_59_hook_lines.py
- tests/acceptance/W2-59/test_w2_59_hook_lines_worker_env.py
- tests/acceptance/W2-90c/**
kpis:
  success:
  - 'W2-90''s seven named reds (W1-05''s two orchestrator-asks cases, W1-46''s research npm-install case, four W2-59 cases) judge the kernel''s wiring and pass on the head with W2-105 and W2-106 merged [DEC-965 item 1, DEC-966]'
  - 'Every case W2-90b named in its return as needing W2-105 or W2-110 judges the kernel''s wiring and passes on the head with them merged [DEC-999]'
  - 'Nothing is lowered: no case deleted, skipped, xfailed or weakened; every revised file''s commit carries Rewrite-Reason: DEC-953 item 2; a README under the ticket''s folder maps every case [DEC-906, MR-3]'
  failure:
  - 'A revised case still reads this repository''s live settings, or is red with W2-105, W2-106 and W2-110 merged.'
  - 'A case deleted, skipped, xfailed or its verdict weakened.'
profile: LITE
sources:
- DEC-999
- DEC-965
- DEC-966
- DEC-953
est_loc: 60
acceptance_tests:
  path: tests/acceptance/W2-90c/
  author: independent-test-designer (MR-3); a test-revision ticket judged on its revised suite (DEC-892)
track: B
list_rows: []
---
# W2-90c The cases of W2-90b that wait for W2-105 or W2-110

The owner split W2-90b on 2026-11-01 (DEC-999) so it does not wait for W2-105 or ACT 2: W2-90b fixes now every case
whose fixtures need only the kernel's hook file; this ticket holds the cases that truly need W2-105 (the template's
install block removed) or W2-110 (a product's CTO-only install rule), after both land and after W2-90b.
