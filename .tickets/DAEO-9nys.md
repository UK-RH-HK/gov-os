---
id: DAEO-9nys
status: in_progress
deps: []
links: []
created: 2026-10-23T13:03:15Z
type: task
priority: 1
assignee: engineer
external-ref: W2-67
tags: [wave-2, tests, hygiene, revision, full]
wbs_id: W2-67
title: 'Test hygiene: per-test copies, nested runs, temp folders, and the weak tests'' revisions'
class: test-revision
state_class: AUTHORITATIVE
role: engineer
depends_on: []
allowed_paths:
- tests/unit/close/**
- tests/unit/guard/**
- tests/conftest.py
kpis:
  success:
  - 'Every per-test copy commits with gc.auto=0 or copies the working files without .git; W1-27''s old-path case gets a project of its own instead of a whole-tree copy; a planted 7,000-object tree runs every copying case green in parallel [I3 F9, I4 F5, I4 §2.1]'
  - 'The 15 unit close functions that start a nested pytest get a bound a loaded machine meets (one worker, or a measured limit); worksteal is then re-measured in the nightly in file order [I2 F5, DEC-892 a, P-IS-3]'
  - 'W2-50''s large-store and hang cases run against a declared short limit; the guard unit test''s fixed /tmp folder becomes tmp_path [I1 F-11, I1 §2.3]'
  - 'The suites keep pytest''s own retention of three base folders and nothing passes a per-run --basetemp; a full run leaves at most three base folders behind [DEC-898]'
  - 'Each weak case revised is first shown red against a planted fault, then green on the head, each with a Rewrite-Reason; in this order: gov doctor''s 40 W1-27 cases (before W2-22, W2-18 or W2-09 changes doctor); W1-26''s 45 planted-defect cases, their fixture shown green before any defect; W1-30''s 13 first-round cases; W2-02''s unmeasured case; I3''s T-A3 rows (their folders named in this file when it is written) [P-IS-7 (a), I2 F2, F3, I4 F1]'
  - 'The root tests/conftest.py refuses, at the start, a run given a per-run --basetemp, naming DEC-898; one opt-out stays, the environment flag GOV_ALLOW_BASETEMP=1, for a measured trial [DEC-907 item 2]'
  failure:
  - A revised case that cannot fail for its fault; an expectation lowered; a copy that still races gc; an unbounded nested run; a per-run base folder; a test changed in a folder this file does not name.
profile: FULL
sources:
- DEC-889
- DEC-892
- DEC-898
- DEC-899
- DEC-904
- DEC-907
est_loc: 750
acceptance_tests:
  path: tests/acceptance/W1-27/
  author: independent-test-designer (MR-3); the revisions of other tickets' acceptance tests, each with a Rewrite-Reason
track: A
list_rows: []
---
# W2-67 Test hygiene: per-test copies, nested runs, temp folders, and the weak tests' revisions

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-67), from DEC-889 item 7 (P-H-5), DEC-892 item 1, DEC-898 and lens I's P-IS-3 and P-IS-7.

- **Place (owner, DEC-904 item 5):** the next free slot, ahead of W2-66's merge, because its fixes remove the tree-copying tests behind the inode explosions of 2026-10-22 and 2026-10-23 and much of the close time. As a test-revision ticket, it closes on its declared `acceptance_tests.path` once W2-07's class is pinned (DEC-896 item 3); that is why `acceptance_tests.path` names another ticket's folder.
- **Its rounds, under the overlap rule (the prompt §3):**
  - **Round 1, now:** the folders no ticket in flight holds:
    - the copying fixtures (`tests/acceptance/W1-07/w1_07_support.py`, `tests/acceptance/W1-25/**`, W1-27's old-path case);
    - `tests/acceptance/W1-26/**`, `W1-27/**`, `W2-02/**`;
    - the guard unit test's fixed `/tmp` folder;
    - the root `tests/conftest.py`'s temp-folder rule.
  - **Round 2, after W2-07 and W2-66 merge:** W1-30's 13 cases and the 15 nested-run unit close functions (`tests/unit/close/**`).
  - **Round 3, after W2-69 merges:** W2-50's large-store and hang cases.
- **Its verification run** goes under `flock /tmp/gov-os-verify.lock`, within 6,000,000 files and folders and 60 GB (DEC-904 item 3).
- **Roles:**
  - its independent test designer revises the acceptance tests;
  - its engineer changes the builder tests (`tests/unit/**`) and the shared fixtures (DEC-042).
- **Riding elsewhere (P-IS-7 (a)):** revisions of files an open ticket already holds:
  - W2-11: the skills' 41 cases;
  - W2-34: W1-09's and W1-14's;
  - W2-65: the unit hooks;
  - W2-44: containment's PF-7 case;
  - W2-04: W1-24's.
- **W2-L373's rename** is W2-69's (P-IS-5 (a), DEC-899).
- **Roles (DEC-907):** the ticket is an engineer's, for its builder files (`tests/unit/guard/**`, `tests/conftest.py`, and `tests/unit/close/**` in round 2). Its test designers write the acceptance files, named here, not in `allowed_paths` (MR-3): `tests/acceptance/W1-07/w1_07_support.py`, `tests/acceptance/W1-25/**`, `tests/acceptance/W1-26/**`, `tests/acceptance/W1-27/**`, `tests/acceptance/W1-30/**`, `tests/acceptance/W2-02/**`, `tests/acceptance/W2-50/test_w2_50_secrets_scan_scale.py`. The copying fixtures are changed by a second, fresh test designer with `Rewrite-Reason: the copy races git's background gc (I3 F9, I4 F5)`. It runs batch 1's `test_w2_67_*` files, `w2_67_tmp_probe.py` and `README-W2-67.md`, but never reads them.
