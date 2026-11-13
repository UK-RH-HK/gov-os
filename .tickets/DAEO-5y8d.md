---
id: DAEO-5y8d
wbs_id: W2-182
external-ref: W2-182
title: The nightly's drift reds of 2026-11-13 fixed by test revision (W1-32's command list, W1-18 and W2-123's rebuild answer, W2-121 S1's race, W2-136 S10, W2-23 S6)
type: task
class: implementation
role: independent-test-designer
profile: LITE
status: in_progress
state_class: AUTHORITATIVE
priority: 1
created: 2026-11-13
deps: []
allowed_paths:
- tests/acceptance/W1-32/test_w1_32_command_set.py
- tests/acceptance/W1-32/README.md
- tests/acceptance/W1-18/test_w1_18_on_demand_start.py
- tests/acceptance/W1-18/README.md
- tests/acceptance/W2-123/test_w2_123_retry.py
- tests/acceptance/W2-123/README.md
- tests/acceptance/W2-121/test_s1_lock_off_status.py
- tests/acceptance/W2-121/README.md
- tests/acceptance/W2-136/test_w2_136_never_a_gate.py
- tests/acceptance/W2-136/README.md
- tests/acceptance/W2-23/test_w2_23_space.py
- tests/acceptance/W2-23/README.md
- docs/probes/DAEO-5y8d/**  # the probe record
- template/.rulesync/hooks.jsonc  # E (a): the template's hooks source gains context_watch.py (a product-spec worker's line, not a test designer's)
kpis:
  success:
  - 'B: W1-32''s recorded command list holds the four approved commands gov --help shows (dispatch W2-121, adapters W2-23, session-watch W2-159, wait W2-160), and nothing else changes in it [DEC-1163 (6), DEC-1156 (7)] Verify: tests/acceptance/W1-32/test_w1_32_command_set.py passes on w2/integrate; a planted unrecorded command name added to gov --help in a stand-in makes it fail'
  - 'C: W1-18''s and W2-123''s cases expect REBUILD_FAILED where a rebuild''s asked-for semantic store is not recreated (W2-124, DEC-1150 (3)), each keeping its point (the keyword answer and no start for W1-18; the last failed try''s record for W2-123) [DEC-1163 (6), DEC-1150 (3)] Verify: both cases pass on w2/integrate; each still fails on a planted break of what it guards (W1-18: a retrieval that starts the server; W2-123: a retry record that is not written)'
  - 'R: W2-121 S1 takes its second snapshot only after the fake launched job''s .exit file exists, so `gov dispatch status` is judged on what it writes, not on the job''s late write [DEC-1163 (6)] Verify: the case passes 20 runs in a row under the nightly''s load (beside a busy loop of 20 workers); it still fails when a stand-in status writes a file'
  - 'D: W2-136 S10''s scan allows `src/gov/session_watch` to call gov plan (W2-159''s S5: session-watch reads the dispatcher''s ready list by `gov plan --ready`); every other module outside plan/ and launch/ is still refused [DEC-1163 (6) D (a), DEC-105] Verify: the case passes on w2/integrate; a planted module outside plan/, launch/ and session_watch/ calling gov plan fails it'
  - 'E: the template''s hooks source `template/.rulesync/hooks.jsonc` wires `context_watch.py` as the root `.rulesync/hooks.jsonc` does (ACT-CONTEXT-WATCH-1), and W2-23 S6 expects the seven kernel hooks [DEC-1163 (6) E (a)] Verify: W2-23 S6 passes on w2/integrate; a planted eighth hook script with no wiring fails it; `python3 -m gov.adapters.portability` exits 0 on the template'
  failure:
  - 'A revised case that no longer catches what it guards, or any case lowered, skipped or marked. Verify: each revised case fails on a planted break of what it guards (the S lines above); `git diff` adds no skip, xfail or flaky mark'
non_goals:
- no product code changes (src/gov/**); the behaviours these cases record were decided and landed by W2-45, W2-121, W2-23, W2-159, W2-160, W2-124 and W2-176
- not the 2 timing cases that pass alone under the nightly beside the leads (W2-112, W2-145 S4): environment, DEC-1159 (1)
done_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]
sources: [DEC-1163, DEC-1156, DEC-1150, DEC-1159, DEC-105, DEC-781]
acceptance_tests: {path: tests/acceptance/W2-182/}
---

# W2-182 The nightly's drift reds of 2026-11-13

The owner's DEC-1163 (6), route (a): one small gap ticket for the five red-alone cases of the nightly of 2026-11-13 that
are not the Node 18 PATH (fixed by 8f68e0c7c). Each records a behaviour the owner already decided and that has landed;
every ticket that broke them is closed. Analysis: `.gov-runtime/scratch/orchestrator/drafts/nightly-20261113-analysis.md`.

- **B** (W1-32): `dispatch` (W2-121, merge 787b097ac), `adapters` (W2-23), `session-watch` (W2-159), `wait` (W2-160).
- **C** (W1-18, W2-123): W2-124's "a rebuild without its asked-for semantic store fails named" (799b2b65f, merge a2f28ccf3).
- **R** (W2-121 S1): a race in the test under load (passes alone).
- **D** (W2-136 S10 against W2-159 S5): the owner's (a).
- **E** (W2-23 S6): W2-176's 7th kernel hook (context_watch.py, hand merge 3430341c4) never reached `template/.rulesync/hooks.jsonc`; the owner's (a).

A test designer revises the cases (`Rewrite-Reason: DEC-1163 (6)`); a product-spec worker adds the template's hook line; a narrow independent check; the land.
