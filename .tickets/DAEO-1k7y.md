---
id: DAEO-1k7y
status: in_progress
deps: []
links: [DAEO-ouet, DAEO-cb2b, DAEO-wnnz]
created: 2026-11-12T05:03:31Z
type: task
priority: 1
assignee: engineer
external-ref: W2-177
tags: [wave-2, accept, signals, full, shared-red]
wbs_id: W2-177
title: 'The six W2-96 signal reds: gov accept''s clean-up under a signal, red in every tree''s verify and in the nightly of 11-12'
class: implementation
state_class: AUTHORITATIVE
role: engineer
profile: FULL
depends_on: []
waits_on: []
allowed_paths:
- src/gov/accept/**
- tests/unit/accept/test_w2_96_run2.py
- tests/unit/accept/test_w2_96_review3.py
- tests/unit/accept/test_w2_96_review4.py
- tests/unit/accept/w2_96_reap.py
- tests/unit/accept/test_w2_177*
- docs/changes/W2-177-evidence.md
- tests/acceptance/W2-96/w2_96_support.py  # P-W2-177-1 (a): _popen's signal start state, a test designer's revision (the CTO, 2026-11-12 07:05)
- tests/acceptance/W2-56/w2_56_support.py  # P-W2-177-1 (a): start_launch's signal start state, the same revision
est_loc: 80
kpis:
  success:
  - 'S1 The cause is named with evidence before any change: why the six cases (`tests/unit/accept/test_w2_96_run2.py` four, `test_w2_96_review3.py` one, `test_w2_96_review4.py` one) and the W2-96 acceptance cases of the same family fail in the empty-HOME verify form, under the nightly''s cron start, and alone at load 18, yet passed in one W2-110 verify and alone with the real HOME; in particular whether the process under test starts with SIGINT ignored (the nightly''s red premise case R11 says the start form differs from the one the tests assume). Verify: docs/changes/W2-177-evidence.md names the cause, the start forms tried (empty HOME, real HOME, cron-like `setsid` with SIGINT ignored, a background job) and each one''s counts [DEC-1050]'
  - 'S2 With the fix, the six cases pass in every start form S1 tried, ten runs each, with no timeout raised and no case skipped. Verify: the ten-run counts per form in the evidence; `skip_known.json` unchanged [DEC-966, DEC-1050]'
  - 'S3 If the cause is the test''s own start form, not `gov accept`, the unit cases change and the W2-96 acceptance cases of the same family go to an independent test designer''s revision with a Rewrite-Reason (the CTO adds their paths then); if it is `gov accept`''s clean-up, the code changes and no test''s assertion is weakened. Verify: the diff: no unit assertion removed or loosened; a test change carries its reason in the commit [DEC-866, DEC-966]'
  failure:
  - 'A red hidden instead of fixed: a case added to skip_known.json, a timeout raised, a signal case skipped or deselected. Verify: the diff of skip_known.json, the cases'' timeouts and their markers is empty'
  - 'Any change outside the paths above. Verify: `git diff --name-only` of the ticket''s branch against its base lists only paths matched by the ticket''s allowed_paths'
non_goals:
- W2-56's two SIGINT ending cases (DAEO-wnnz, its own ticket), unless S1 finds the same cause, which the evidence then says
- the latency reds of W1-19 and W2-13 (W2-155)
done_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]
sources: [DEC-966, DEC-1050, DEC-866, DEC-1010, DEC-953]
acceptance_tests:
  path: tests/unit/accept/
  author: 'the existing W2-96 cases are the acceptance (S2); a new case in test_w2_177* for the cause S1 names, written red first'
track: A
reads:
- tests/acceptance/W2-96/test_w2_96_at_run_2.py
- tests/acceptance/W2-96/test_w2_96_at_no_leak.py
needs:
- src/gov/accept/runner.py
- src/gov/accept/command.py
---
# W2-177 The six W2-96 signal reds

The CTO's ruling P-W2-121-5 (2026-11-12 03:20, delegated P2): six cases in `tests/unit/accept/test_w2_96_{run2,review3,review4}.py`
(signals and timeouts in `gov accept`'s clean-up) are red in 13 of the 14 most recent lead verifies across eight trees
(W2-23, W2-11, W2-52, W2-176, W2-110, W2-115, W2-173, W2-121) and in the nightly of 11-12 (run 20261112-0404, `red-alone`,
with five W2-96 acceptance cases of the same family, among them the premise case R11). They are shared base reds: named
in every return, not blocking. This ticket fixes them. Class C2. Diagnosis first (S1), then the smallest fix; a test
revision of the acceptance folder is a test designer's, not the engineer's.

## P-W2-177-1 and P-W2-177-2 (the CTO, delegated P2, 2026-11-12 07:05)

- **P-W2-177-1 (a):** an independent test designer's revision, with a Rewrite-Reason naming this ticket and DEC-866, of
  `tests/acceptance/W2-96/w2_96_support.py`'s `_popen` and `tests/acceptance/W2-56/w2_56_support.py`'s `start_launch`: each of
  SIGINT, SIGTERM and SIGHUP set to ignored when the case names it, otherwise to default, as `w2_96_reap.launch_gov` now does
  (cause (B): a background start ignores SIGINT). Both paths are in allowed_paths for that revision only (dropped after the land).
  No assertion is weakened. Not (b): the verify's and the nightly's start form stay as they are, so the tests own their start state.
- **P-W2-177-2 (a):** done on w2/integrate (da6ba9c53): `type: task`.

## Approved after the fact (the owner, DEC-1142 (8), 2026-11-12 ~09:50)

Filed by the CTO without the owner's P1 (DEC-974; the prompt's §3); the owner approved it after the fact.
