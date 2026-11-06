---
id: DAEO-f58b
status: in_progress
deps: [DAEO-ecac, DAEO-lrre]
links: []
created: 2026-10-31T23:52:57Z
type: task
priority: 1
assignee: engineer
external-ref: W2-116
tags: [wave-2, implementation, memory, standard, smart-work]
wbs_id: W2-116
title: 'The designers'' store in the product: a double-buffered store of the integration branch, refreshed after the nightly and once more a day, that a test designer''s retrieval reads (SMART-WORK-1)'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-ecac
- DAEO-lrre
allowed_paths:
- src/gov/rebuild/integration.py
- src/gov/rebuild/command.py
- src/gov/launch/store.py
- tests/unit/rebuild/test_w2_116*
- tests/unit/launch/test_w2_116*
kpis:
  success:
  - '`gov rebuild --integration <branch>` keeps a store of that branch''s head in two detached worktrees outside the project, building into the one not in use and switching a link to it only when the build succeeded; a search during a build is answered from the ready one [DEC-963, DEC-983, DEC-982]'
  - 'It is refreshed after the nightly''s verdict and at a set second time each day (both in the project''s configuration), and its status (head, age) is in `gov status` [DEC-966 item 3, DEC-983, DEC-982]'
  - '`gov launch independent-test-designer` points the session''s retrieval at it; a designer''s retrieval never reads a ticket worktree''s store [DEC-963, DEC-983, DEC-982]'
  - 'The store is also refreshed after every landing on the integration branch, and it is the warm base `gov rebuild --seed` (W2-122) reads; a seed taken from a store behind the integration head is named, and only what changed since is re-embedded [DEC-1014 items 4 and 6, SMART-WORK-5 D, DEC-1015 item 3] (folds W2-06 S1, S2)'
  - 'A re-index never empties the semantic index; a model-less re-index reports the semantic facet unavailable instead [DEC-719]. [moved from W2-06 S5, DEC-1083]'
  failure:
  - 'A designer''s retrieval answered from a ticket worktree''s store.'
  - 'The link switched to a store whose build failed, or a search answered from a half-built store.'
  - 'A re-index that fails leaves the previous index and reports the failure; it never leaves no index [W2-M088]. [moved from W2-06 F1, DEC-1083]'
profile: STANDARD
sources:
- DEC-983
- DEC-982
- DEC-963
- DEC-966
est_loc: 150
acceptance_tests:
  path: tests/acceptance/W2-116/
  author: independent-test-designer (MR-3); from the spec and KPIs, in parallel with the implementer (DEC-963); a planted branch, a build killed half-way, a search during a build
track: B
list_rows: []
---
# W2-116 The designers' store in the product

The owner's SMART-WORK-1 decision 2 (DEC-983): the designers' store (DEC-963, DEC-966 item 3) becomes the product's, not only the CTO's `refresh_integration_store.sh` and `store_refresh_daily.sh`.

- **Why:** a test designer retrieves only from the integration branch's store, so its retrieval never serves a ticket's implementation. W2-33's role files and W2-83b's playbooks will tell an adopted product's designers so; nothing in the product builds that store.
- **This repository's own configuration:** the place (`~/gov-os-worktrees/W2-00-store`) and the two times a day; the CTO's scripts are retired once this lands.
- **Order:** after W2-60b (the launcher's files) and W2-33 (the rule it serves); before EXAMIN's copy (W2-27).

**DEC-1087 (3) placed here (CTO, 2026-11-06, delegated P3 on the scope):** the owner orders the refresh after every
merge into integrate built, tested and reviewed before re-pin window 4, so the window puts it live. The worktrees get
the integration store's path, so workers can search.
- **This pass builds S1, S3 (widened, below), S4 and S5, and the three failure lines.** S2's two daily times and
  `gov status` stay for the next pass. Until then the CTO's `store_refresh_daily.sh` runs as the backstop (DEC-1087
  (3)).
- **S3 widened:** `gov launch` points every worker session's retrieval at the integration store, not only a
  designer's. A designer's retrieval still never reads a ticket worktree's store. A worktree has no store of its own
  today, so a worker's search answers `STORE_MISSING` (checked 2026-11-06).
- **S4's trigger:** "after every landing" covers every merge into the integration branch, by the merge queue or by
  hand. The product offers the refresh as a command run after the merge (`gov rebuild --integration <branch>`, idempotent
  at an unchanged head). The hook that calls it after a hand merge is installed by the owner's operator in re-pin window
  4's ACT (hooks are the operator's). The design is the engineer's, stated in its evidence record.
- **The deps W2-60b (the session record) and W2-33 (the roles) are not needed** for this pass: it touches neither the
  session record nor the role files. They stay in `deps:` for S2 and the role rule's text.
- **The rebuild uses the code it runs under.** The store at window 4's head is built by window 4's code, so the pinned
  code and the store always match. The engineer states how the double buffer keeps the ready half answering while the
  other builds (F2).
