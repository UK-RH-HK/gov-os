---
id: DAEO-c9n8
status: in_progress
deps: []
links: [DAEO-61vm]
created: 2026-11-12T05:40:00Z
type: task
priority: 2
assignee: independent-test-designer
external-ref: W2-179
tags: [wave-2, test-revision, memory, audit, nightly, lite]
wbs_id: W2-179
title: 'W2-170''s F3 file-access case counts the repository''s own files as runs-folder opens when the repository lives under ~/gov-os-runs (the nightly''s clone); red in the nightly of 11-12'
class: test-revision
state_class: AUTHORITATIVE
role: independent-test-designer
profile: LITE
depends_on: []
waits_on: []
allowed_paths:
- tests/acceptance/W2-170/test_w2_170_s4_map.py
- tests/acceptance/W2-170/README.md
est_loc: 15
kpis:
  success:
  - 'S1 `test_f3_a_run_s_file_access_log_shows_no_open_of_the_true_sets_root_or_runs_folders` judges only opens of the true sets root and of the runs folders outside the repository under test: an open of a file of the repository itself (its own source, tests and stores) is not a runs-folder open, wherever the repository lives. Verify: the case passes in a clone under ~/gov-os-runs/<x>/ (as the nightly runs it) and in a clone elsewhere; a planted open of a file under the true runs folder outside the repository still fails it [DEC-820 (b), (d), DEC-866]'
  failure:
  - 'A real runs-folder or sets-root open let through. Verify: the planted open of a runs-folder file outside the repository fails the revised case, in both clone places'
  - 'Any change outside the paths above, or a case removed, skipped or loosened beyond the repository''s own files. Verify: `git diff` of the case shows only the exclusion of the repository''s own root; `git diff --name-only` lists only the allowed paths'
non_goals:
- the memory audit's code (W2-170, closed)
done_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]
sources: [DEC-820, DEC-866, DEC-966, DEC-1101]
acceptance_tests:
  path: tests/acceptance/W2-170/
  author: 'independent-test-designer (MR-3), Sonnet high (RUBRIC-2, class C1): the revision with a Rewrite-Reason (DEC-866)'
track: B
reads:
- src/gov/memaudit/preflight.py
- tests/acceptance/W2-170/conftest.py
needs:
- tests/acceptance/W2-170/test_w2_170_s4_map.py
---
# W2-179 W2-170's F3 case and the nightly's clone

The nightly of 11-12 (run 20261112-0404, head 9bbef27f1d05) is red on
`tests/acceptance/W2-170/test_w2_170_s4_map.py::test_f3_a_run_s_file_access_log_shows_no_open_of_the_true_sets_root_or_runs_folders`
(red alone too): its `reached` list holds 100-odd paths, every one a file of the repository under test, because the nightly's
clone lives at `~/gov-os-runs/W2-00/nightly/<run>/`, inside the runs folder the case watches. The code is not at fault (W2-170
closed with the case green in its worktree). A test revision: exclude the repository's own root from "the runs folders".
Class C1. The hidden-half rule holds: the revised case plants its own sets root and runs folder.

## Approved after the fact (the owner, DEC-1142 (8), 2026-11-12 ~09:50)

Filed by the CTO without the owner's P1 (DEC-974; the prompt's §3); the owner approved it after the fact. It should have been a fix inside an existing ticket (its paths and KPI lines widened by the owner's decision), not a new ticket.
