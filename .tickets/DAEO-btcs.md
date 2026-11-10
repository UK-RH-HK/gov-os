---
id: DAEO-btcs
status: open
deps: []
links: [DAEO-c1uz, DAEO-zuiy]
created: 2026-11-09T01:45:43Z
type: task
priority: 2
assignee: independent-test-designer
external-ref: W2-66c
tags: [wave-2, test-revision, lite]
wbs_id: W2-66c
title: 'W2-66''s live-map suite pins ACT-SELECT-FIXES-1''s lines: the couplings for the settings, the declared checks, the history rule and the fixture scans, and W2-66''s record-only case in the always-run set (DEC-1100 (1))'
class: test-revision
state_class: AUTHORITATIVE
role: independent-test-designer
depends_on: []
allowed_paths:
- tests/acceptance/W2-66/test_w2_66_select_fixes.py
kpis:
  success:
  - 'S1 Settings and hook wiring are coupled: on the live test map, a change of `.claude/settings.json`, `.rulesync/hooks.jsonc` or `.rulesync/permissions.jsonc` reaches W1-33''s `test_w1_33_guard_and_launcher.py`, W1-46''s `test_w1_46_research_installs.py` and W2-54''s `test_w2_54_sandboxed_worker.py`, through a coupling the map declares. Verify: a case per path, reading `governance/project/test-map.yaml` with the product''s own loader (`gov.close.select.load_map`) and matching with `gov.close.select.match`, asserts the three suites are among the targets of the couplings that path matches [DEC-1100 (1), DEC-1098 (2)(b), DEC-896 item 2]'
  - 'S2 The declared checks are coupled to W2-54''s no-weakening case alone: a change of any file under `template/governance/kernel/checks/` reaches `tests/acceptance/W2-54/test_w2_54_time_limit.py::test_no_hard_block_check_is_weakened` through a coupling, and no coupling that path matches names the whole file `test_w2_54_time_limit.py` or another of its cases. Verify: a case per tracked file of that folder (`git ls-files`), on the live map with the product''s loader and matcher [DEC-1100 (1), DEC-1045]'
  - 'S3 The history rule and the fixture scans are coupled: a change of any path under `tests/acceptance/` reaches `tests/acceptance/W1-01/test_w1_01_integration_merges.py::test_the_integration_merges_of_this_repository_pass`, and a change of an acceptance `.py` also reaches `tests/acceptance/W1-50/test_w1_50_freeze_fixture_settings.py::test_the_two_whole_tree_fixtures_are_found` beside W1-28''s `test_w1_28_fixture_copies.py`. Verify: cases on planted paths (an acceptance `.py`, an acceptance `.md`, a conftest) on the live map with the product''s loader and matcher; the `.md` reaches W1-01''s case and not W1-50''s [DEC-1100 (1), DEC-253, DEC-912 item 3]'
  - 'S4 W2-66''s record-only case is always run: the live map''s `record_reading` holds `tests/acceptance/W2-66/test_w2_66_live_test_map.py::test_every_record_of_each_of_dec_891_s_places_is_record_only`, so a scoped selection of a change that holds only a record under `governance/project/orchestration/` selects it, and a run that names no node id collects every row of the case (no opt-in list leaves a row out: `tests/optin-lifted-breadth.txt` holds no `rep:` line for it), the `governance/project/orchestration/` row included. Verify: a case reading `record_reading`; a case reading the opt-in lists with tests/conftest.py''s own reader (`optin_entries`) asserting none names the function; a case running the product''s `gov.close.select.plan` on a temporary copy of the repository''s test map and tickets folder in a planted git repository with one records-only commit, asserting the case is among the selected targets [DEC-1100 (1), DEC-889 item 2, DEC-891, DEC-1061]'
  - 'S5 Every coupling''s target exists: each target of every coupling in the live map names a tracked file or folder, or a node id whose file is tracked and whose function (with its class, when named) is defined in that file, so a renamed case reds here, not as an `UNRESOLVED_TARGET` refusal at a later selection. Verify: a case over every coupling target, the node ids checked by reading the file''s `def` and `class` lines (no collection, no run); a planted map with a misspelt node id reds the same helper [DEC-1100 (1), DEC-968]'
  - 'S6 Tests first: the cases were written from these lines, not from the patch; each case of S1 to S4 is red on the test map and breadth list of ACT-SELECT-FIXES-1''s parent commit and green on those after it, and the file''s cases are green on `w2/integrate`. Verify: the test designer''s record (in the commit body) of a run of the file with the ACT''s parent''s `governance/project/test-map.yaml` and `tests/optin-lifted-breadth.txt` (`git show` of each copied over in a scratch clone): every S1-S4 case red; then green on the ACT''s commit and on `w2/integrate` [DEC-1100 (1), DEC-906]'
  failure:
  - 'A case that passes on the map before ACT-SELECT-FIXES-1 (it pins nothing).'
  - 'Any file changed outside `tests/acceptance/W2-66/test_w2_66_select_fixes.py`; any other case of the W2-66 suite changed, skipped, xfailed or loosened.'
  - 'A case that runs a pytest selection, starts a gov command, or reads anything outside this repository''s tracked files and its own temporary folders.'
profile: LITE
sources:
- DEC-1109
- DEC-1112
- DEC-1100
- DEC-1098
- DEC-889
- DEC-891
- DEC-253
- DEC-968
- DEC-1061
- DEC-896
- DEC-912
- DEC-1045
- DEC-906
est_loc: 160
acceptance_tests:
  path: tests/acceptance/W2-66/
  author: 'independent-test-designer (MR-3), from these KPI lines, before the cases are relied on: the live test map read with the product''s own loader and matcher; planted paths and a planted git repository in a temporary folder; never the main tree''s store, and no pytest run from inside a case'
track: A
list_rows: []
needs: []
waits_on: []
---
# W2-66c W2-66's live-map suite pins ACT-SELECT-FIXES-1's lines

The owner's DEC-1100 (1): P-SELECT-FIXES-1's proposals (i), the test-map couplings for the miss kinds the P-SELECT-GRAPH
trial saw, and (ii), W2-66's record-only case in the always-run set, applied as **ACT-SELECT-FIXES-1** (the owner's
operator, `governance/project/orchestration/packages/ACT-SELECT-FIXES-1.md`), with **W2-66c, tests first, to pin
them**. The ACT's lines caught all 34 traced reds of the trial's 18 culprit trees in the replay (22 without them).

- **What it pins:** the four couplings (settings and hook wiring → W1-33, W1-46, W2-54's sandboxed worker; the
  declared checks → W2-54's no-weakening case alone; `tests/acceptance/**` → W1-01's integration-merge case; acceptance
  `.py` → W1-50's whole-tree fixture case beside W1-28's) and the record-reading line. S5 adds for couplings the check
  W2-66's `test_every_record_reading_target_exists` makes for `record_reading` (P-SELECT-FIXES-1 §1, "Brittle node
  ids").
- **Starts after the ACT's commit.** An ACT is not a ticket, so `gov plan` cannot hold this ticket on it: the CTO
  launches it only once the operator has committed ACT-SELECT-FIXES-1 (the map's sha256 `80d47adb410d`). S6 is what
  makes it tests first: every pinning case is shown red on the map of the ACT's parent.
- **A new file, not W2-66b's:** `test_w2_66_live_test_map.py` (and its README) is held by W2-66b (`DAEO-zuiy`, in
  progress), whose KPI keeps every other case of that file unchanged. A file of its own in the same suite folder is
  selected with W2-66 and needs no change to W2-66b. Its `RECORD_READERS` and `COUPLINGS` fixtures are not touched.
- **No product code:** nothing in `src/` or the schema changes; a coupling's suites already take node ids.
- **F1 (a)** (the CTO's choice, 2026-11-09, ACT-SELECT-FIXES-1 §5): the ACT also places in `record_only` the four
  records the whole case found unplaced, and drops the breadth list's `rep:` line for it, so a selection runs all
  seven rows. S4 pins that no opt-in list leaves a row out.
- **Profile LITE:** test cases only, read-only on the live map; an independent test designer, then the CTO's scoped
  run of `tests/acceptance/W2-66/`.
- **Est.:** about 160 lines, two hours with the S6 record.

[DEC-1100 (1), DEC-1098 (2)(b)]

- **Delegated (the CTO, DEC-1112 (3), 2026-11-10), D-10's red-fix list:** W2-66's DEC-891 record case leaves out a file under a `tools/` folder that a `.py` in that folder names by a string literal (W2-149's result schemas, read by `indep_launch.py`), option (a) of three; built on `w2/W2-66c-d10-tests` (`dc5c0fd87`), review READY (`reviews/D10-W2-66-review.md`). Rows from the review: F1 other read routes are missed, F2 `tools/win_toast.ps1` is listed record-only while `deadman.py` runs it (fails open for the selection; for the test map's owner), F4 a bare-name literal counts as read.
