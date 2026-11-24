---
id: DAEO-5x4l
status: closed
deps: [DAEO-t6hf, DAEO-jozo]
links: []
created: 2026-09-30T22:49:58Z
type: task
priority: 1
assignee: engineer
external-ref: W1-21
tags: [wave-1, implementation, full]
wbs_id: W1-21
title: gov retrieve with completeness
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-t6hf
- DAEO-jozo
allowed_paths:
- src/gov/retrieval/retrieve*
- src/gov/retrieval/bundle*
- src/gov/retrieve/**
- tests/unit/retrieve/**
- template/governance/kernel/checks/retrieval-regression*
kpis:
  success:
  - Paging with continuation; facets; dedup by chunk hash; authority/current filter drops superseded and must-not-cite records; one rerank over the merged set [CAP-16.a, CAP-18.a, CAP-51.b]
  - Every bundle cites by id and sha256 and carries one stopping reason from the fixed list [CAP-55.a]
  - RETR-A-04 and RETR-X-02 dev runs produce multi-batch bundles [CAP-16.b]
  - A child hit is expanded to its parent span only within the bundle budget, and the bundle names each expansion (DEC-091) [CAP-18.b]
  - 'Registers the retrieval-regression family check: the dev query set meets its recorded hit@5 and forbidden-citation baselines [CAP-38.b]'
  - Retrieval spend has its own radius-scaled budget (follow-up rounds by profile), separate from the packet ceiling; reaching it ends with BUDGET_EXHAUSTED_WITH_GAPS and the gap list, never silent truncation
    [CAP-04.c, CAP-16.c]
  - For a ticket whose scope matches a committed failure or lesson record, the bundle returns that record ahead of implementation evidence [CAP-14.a]
  failure:
  - A batch-size limit is reported as completeness
  - A superseded record is cited as current
profile: FULL
sources:
- DEC-080
- DEC-091
- G-19
- S0a-G-06
- CAP-14
- CAP-16
- CAP-18
- CAP-41
- CAP-55
- CAP-04
- CAP-38
- CAP-51
est_loc: 300
acceptance_tests:
  path: tests/acceptance/W1-21/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-21 gov retrieve with completeness

The retrieval-completeness engine behind the retrieval skill (DEC-080).

## Fix: `retrieve_check` and the kit check never fail on hit@k (F9; audit N-14; DEC-1210, DEC-1233, EMERGENCY-2 5.2)

Found 2026-11-22 (audit N-14): `src/gov/retrieval/retrieve_check.py` exited 1 when hit@5 fell under the baseline's `hit_at_5`,
and the kit check `template/governance/kernel/checks/retrieval-regression.yaml` was `severity: hard-block`, so a low hit@5
could block a close. hit@k is a reported diagnostic only (EMERGENCY-2 5.2). Kind: a fix; the ticket stays closed. Failing
tests first: `tests/acceptance/W1-21/test_w1_21_no_hit_floor.py` (README ids nofloor-N; 6 red, 3 guards on the base),
`38df7bf90`, with `test_w1_21_family_check.py` revised (Rewrite-Reason DEC-1210, DEC-1233); code `23573ca4c`:
`retrieve_check.py` prints `hit@5: <value>` as a diagnostic and never exits 1 on it (forbidden citations over their
baseline and `unmeasured` still exit 1), `hit_at_5` is out of `retrieve_baseline.yaml`, the kit check is kept at `severity:
warning` (the CTO's ruling: kept, not deleted) with its header reworded; `677a2ebb4`: `tests/optin-lifted-breadth.txt` names
the renamed W1-21 case. Nothing in `src` or `template` expects `hard-block` for it; release manifests under `docs/releases/*`
hold the old template text as history. W1-21's folder run with breadth: `test_w1_21_merge.py::
test_several_batches_are_reranked_in_one_pass_over_the_merged_set` and `::test_a_rerank_over_more_than_thirty_candidates` fail
("a rerank request carried more than 16 texts (DEC-1067 (f))") and fail the same on `w2/integrate` (2 failed, 6 passed,
checked in a scratch worktree at `30d406be2`): not this fix's, so `gov accept W1-21` stays red on them. Lead `fixes-015b`
(Sonnet), branch `e2/fixes-015b`.

## Fix: two rerank cases take the bounds DEC-1090 (2) gives (F16)

Found 2026-11-22 (fixes-015a): W1-21's two rerank cases pinned a request size the module no longer has; the bounds in force
are `MAX_REQUEST_TEXTS` and `MAX_REQUEST_CHARS` (DEC-1090 (2)). Kind: a fix, no new ticket; the ticket stays closed. The
two cases were revised to read the bounds from the module (`13167f939`); no code change.
