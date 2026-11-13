---
id: DAEO-5y8d
wbs_id: W2-182
external-ref: W2-182
title: The nightly's drift reds of 2026-11-13 fixed by test revision (W1-32's command list, W1-18 and W2-123's rebuild answer, W2-121 S1's race, W2-136 S10, W2-23 S6)
type: task
class: implementation
role: independent-test-designer
profile: LITE
status: closed
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
- tests/acceptance/W2-128/test_w2_128_rows.py  # row 8: the 'until W2-56' line deleted (DEC-1163 (1)), widened by the CTO (DEC-1157 (12))
- tests/acceptance/W2-128/README.md
- docs/probes/DAEO-5y8d/**  # the probe record
- tests/acceptance/W2-182/**  # the revision's own folder: its README maps the revised case ids so gov accept W2-182 runs them (DEC-892; the W2-90 form); CTO, DEC-1157 (12)
reads:
- .gov-runtime/scratch/orchestrator/drafts/nightly-20261113-analysis.md
- src/gov/check/commands.py
- src/gov/rebuild/**
- src/gov/session_watch/items.py
- .rulesync/hooks.jsonc
- template/governance/kernel/hooks/**
needs: []
waits_on: []
kpis:
  success:
  - 'B: W1-32''s recorded command list holds the four approved commands gov --help shows (dispatch W2-121, adapters W2-23, session-watch W2-159, wait W2-160), and nothing else changes in it [DEC-1163 (6), DEC-1156 (7)] Verify: tests/acceptance/W1-32/test_w1_32_command_set.py passes on w2/integrate; a planted unrecorded command name added to gov --help in a stand-in makes it fail'
  - 'C: W1-18''s and W2-123''s cases expect REBUILD_FAILED where a rebuild''s asked-for semantic store is not recreated (W2-124, DEC-1150 (3)), each keeping its point (the keyword answer and no start for W1-18; the last failed try''s record for W2-123) [DEC-1163 (6), DEC-1150 (3)] Verify: both cases pass on w2/integrate; each still fails on a planted break of what it guards (W1-18: a retrieval that starts the server; W2-123: a retry record that is not written)'
  - 'R: W2-121 S1 takes its second snapshot only after the fake launched job''s .exit file exists, so `gov dispatch status` is judged on what it writes, not on the job''s late write [DEC-1163 (6)] Verify: the case passes 20 runs in a row under the nightly''s load (beside a busy loop of 20 workers); it still fails when a stand-in status writes a file'
  - 'D: W2-136 S10''s scan allows `src/gov/session_watch` to call gov plan (W2-159''s S5: session-watch reads the dispatcher''s ready list by `gov plan --ready`); every other module outside plan/ and launch/ is still refused [DEC-1163 (6) D (a), DEC-105] Verify: the case passes on w2/integrate; a planted module outside plan/, launch/ and session_watch/ calling gov plan fails it'
  - 'F: W2-128''s row 8 records that the line "Run `gov accept` for a ticket whose suites need the code index outside the sandbox, until W2-56" is gone from both kernel templates (W2-56 closed; the owner''s DEC-1163 (1), b88a76172), so W2-128 and W2-152 S10 (which runs gov accept W2-128) are green [DEC-1163 (1), DEC-1156 (7)] Verify: tests/acceptance/W2-128/test_w2_128_rows.py passes on w2/integrate; the row-8 case fails when the line is planted back into template/governance/kernel/templates/role-lead.md'
  failure:
  - 'A revised case that no longer catches what it guards, or any case lowered, skipped or marked. Verify: each revised case fails on a planted break of what it guards (the S lines above); `git diff` adds no skip, xfail or flaky mark'
non_goals:
- no product code changes (src/gov/**); the behaviours these cases record were decided and landed by W2-45, W2-121, W2-23, W2-159, W2-160, W2-124 and W2-176
- 'not the 2 timing cases that pass alone under the nightly beside the leads (W2-112, W2-145 S4): environment, DEC-1159 (1)'
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

- **Delegated (CTO, 2026-11-13 13:40, P3):** run 2 was LAUNCH_BLOCKED (the launcher refuses a product-spec worker on a test-designer ticket, `launcher.py:63`), so the CTO wrote E (a)'s one line on `w2/W2-182` (f0cb5284d) instead of changing the ticket's role (which would make core-mutation flag its acceptance paths); the narrow audit judges it.
- **The owner's P-W2-182-E-1 (1) (DEC-1167 (4)):** E's template line reverted (f299a5eb6); line E and its template path moved to W2-185 (`DAEO-qyt2`) with W1-38's fixture and portability's per-hook exemption. W2-23 S6 (revised here to seven hooks) stays red until W2-185 lands, as it was red before W2-182.
