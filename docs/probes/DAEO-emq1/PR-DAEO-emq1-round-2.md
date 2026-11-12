---
type: probe
task: DAEO-emq1
round: 2
reviewer_session: 08be4bc3-ab13-4bf1-a947-25806d701d02
implementer_session: 83bbdb92-7c96-4756-99e6-cc563c0e782a (eng-5), 221d1199-a8e5-45a0-ab74-10a0925d3d6c (eng-6); round 1's f12efad7-fc16-481c-a9f1-c8b7f093f989, 4a29722c-bd73-421e-b2b8-60a994fb5030, 68e7b7a7-425e-44dd-bfdd-f794eb1effbc
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: independent-auditor
judgement: fail
probed_commit: f39289d3a3799344641055c3f19e553e3b509f88
decisions_applied: DEC-1010, DEC-988, DEC-989, DEC-1083, DEC-1001, DEC-1002, DEC-983, DEC-136
---

# Probe record: W2-115 (DAEO-emq1), the smart close, FULL review round 2 of 2 (the last): FAIL

A fresh Independent Auditor session (`08be4bc3-ab13-4bf1-a947-25806d701d02`, claude-opus-5-5, effort high, read-only,
class C3) probed head `f39289d3a379` and wrote nothing (`git status --porcelain` empty). This is round 2, the last
(DEC-1010 item 1): there is no round 3, and the blocking finding goes to the CTO as a package. The reviewer's two
blocks below are copied unchanged from its return; the lead commits this record because the reviewer is launched
read-only (round 1's F-4, the CTO's PK-4: a row for the launch tool).

## What was probed

- The fix round of PK-3 (a): the test designer's F-1 and F-3 cases (451a775fa), F-7 (bdbf7f069), F-1 (4810c0828),
  F-3 (b5ae48b88), red iteration 1 (99dbe5450, f39289d3a) and the lead's schema fix of round 1's record (d8db5bb6f);
  the ticket's whole change `010399309..f39289d3a` (scope: only `allowed_paths:`, W2-115 acceptance, the six td-3
  files and the probe record; acceptance tests changed only in the test designer's commits).
- Four planted probes (P1: no green base, an untrailered first commit breaking a test, then trailered work; P2: a
  green base, another ticket's landed red, then trailered work; B1: a batch whose only target is the culprit's own new
  test; B3: a batch whose culprit's run alone times out), four mutants of this round's fail-open paths on a mirror
  (M1, M2 killed; M3, M4 survive the unit suites, the real code right), and the S9 script re-run (the table reproduces).
- Found sound: F-1 with the green base an ancestor (the slip's red refused, no repair ticket); the selection unmoved
  (S2, S3); the nightly record replaces the base run only where it excuses the red; F-3's confirmation only on a real
  failure; F-7's method honest; S1, S3, S8, S10, S11, S13, F2-F4 untouched since round 1.

## The lead's check

The lead's verify of this head (lead_verify.sh): parallel 4594 tests, 8 failed, all shared base reds (the six W2-96
signal cases; the two W2-153 cases, red alone on w2/integrate `f29fa36521e3`); serial 1 entry green; `gov accept`
85 passed, 0 failed (S12 has no tests by P4). The lead read `src/gov/close/select.py` `head_without_change` at
`f39289d3a379` and confirms R2-1's mechanism: with no green base on HEAD's line, the base is the parent of the oldest
Task-trailered commit, which is the fallback PK-3 (a) states, so the case is the CTO's to decide.

During the round the reviewer's own wait loop (an `until grep ... ; do sleep 10; done` on a finished task's output
that never held the awaited text) ran 97 minutes; the lead stopped that one process by pid (proc.sh stop 591587), and
the reviewer then returned. Its results had already been read (the reviewer's note).

## The reviewer's verdict

```
verdict: FAIL
head: f39289d3a379
findings: 6
- R2-1 | blocking | S4, F1 | src/gov/close/select.py:546 (used at :759, command.py:1816) | With no green base on HEAD's line, a red is judged against the parent of the ticket's oldest trailered commit. Planted P1: an untrailered first commit breaks W2-bb's widget test, then trailered work: the close exits 0, the ticket closes, the red is recorded caused:false with repair ticket p1-6prz. It should refuse RED_CAUSED. Ordinary work: yes, because a newly adopted project (close: scoped is the default) has no green record until its first green nightly or full close, and a forgotten trailer is an honest slip. Consequence: fails open. It follows PK-3 (a)'s written fallback, so it is a decision.
- R2-2 | major | F1, S4 | src/gov/close/select.py:546 | F-2 is worse this round: work landed on the main line between the green base and the ticket's fork is now judged as the ticket's. Planted P2: another ticket's landed commit breaks the widget test, then this ticket's trailered work: refused RED_CAUSED ("the head without the change: green"). Before this round it closed with a repair ticket. Ordinary work: yes, because any red landed since the newest green record counts, and here the green base is stale (PK-5). Consequence: other (fails closed). It follows DEC-988 item 3.
- R2-3 | minor | S6, F3 | src/gov/close/batch.py:624 | The rest is run on the batch's selection, computed on the whole build, minus the targets the rest lacks. A test that exists only without the culprit (one the culprit renamed or deleted) is never added, so another candidate's change reaching it lands without it run. Reasoned from the code, not planted. Before this round the rest's run refused (RUN_INCOMPLETE) whenever the culprit also added a file. Ordinary work: no, because it needs the culprit to rewrite or remove the one test covering another candidate's change, in a way that masks that change. Consequence: fails open. Smallest fix: the rest's selection is the union of the landed candidates' scoped selections on the rest's build.
- R2-4 | minor | S6, F3 | src/gov/close/batch.py:607, :626 | Two new guards are load-bearing but untested. M3 (a timeout with the candidate alone counts as confirmation): A is blamed, B lands. M4 (an empty target list allowed): B lands after a run of 0 tests. Both mutants pass all 14 unit batch tests, and no acceptance case plants either. The real code is right (B1: RUN_INCOMPLETE, B3: BATCH_UNEXPLAINED). Ordinary work: no. Consequence: other.
- R2-5 | minor | S9 | docs/research/W2-115-smart-close.md:43 | The script's docstring says to run it as `PYTHONPATH=... python3 -I s9.py`, but -I ignores PYTHONPATH, so `gov` cannot be imported (ModuleNotFoundError). The re-run paragraph's command, without -I, reproduces the table exactly. Ordinary work: no. Consequence: other.
- R2-6 | minor | S7 | src/gov/close/command.py:1846 | A refused scoped close writes no close record; the reds and their reasons are only in the refusal envelope on standard output, which is not kept. Scope: out (S7's record holds "the commit closed", and a refusal closes none). Ordinary work: yes. Consequence: other. Reversed by: an owner ruling that "each close" includes a refused one.
```

```verdict
{"kpis": [
{"kpi": "S1", "verdict": "pass", "findings": []},
{"kpi": "S2", "verdict": "pass", "findings": []},
{"kpi": "S3", "verdict": "pass", "findings": []},
{"kpi": "S4", "verdict": "fail", "findings": [{"id": "R2-1", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}, {"id": "R2-2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
{"kpi": "S5", "verdict": "pass", "findings": []},
{"kpi": "S6", "verdict": "pass", "findings": [{"id": "R2-3", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}, {"id": "R2-4", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
{"kpi": "S7", "verdict": "pass", "findings": [{"id": "R2-6", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]},
{"kpi": "S8", "verdict": "pass", "findings": []},
{"kpi": "S9", "verdict": "pass", "findings": [{"id": "R2-5", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
{"kpi": "S10", "verdict": "pass", "findings": []},
{"kpi": "S11", "verdict": "pass", "findings": []},
{"kpi": "S12", "verdict": "pass", "findings": [{"id": "S12-deferred", "scope": "out", "ordinary_work": "no", "consequence": "other"}]},
{"kpi": "S13", "verdict": "pass", "findings": []},
{"kpi": "F1", "verdict": "fail", "findings": [{"id": "R2-1", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}, {"id": "R2-2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
{"kpi": "F2", "verdict": "pass", "findings": []},
{"kpi": "F3", "verdict": "pass", "findings": [{"id": "R2-3", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}, {"id": "R2-4", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
{"kpi": "F4", "verdict": "pass", "findings": []}
]}
```

## Judgement

**Fail** (the reviewer's): R2-1 is in scope, reachable in ordinary work and fails open (S4, F1). It follows PK-3 (a)'s written fallback, so it goes to the CTO as a package in the lead's return, with R2-2 (F-2 made worse, fails closed) and the minor R2-3 to R2-6. No round 3 (DEC-1010).

## Notes: run 5, the accepted fix riding a resume (DEC-802; no review round 3, DEC-1010)

The owner decided R2-1 as P1-K (a) (DEC-1150 (2), 2026-11-12): drop the fallback. This record's round-2 verdict
stands as written; the fix below was accepted without a new review round (DEC-802) and is recorded here, not judged.

- w2/integrate `486bc0fb6992` merged (`8e66a9bd7`; no overlapping files).
- Test design (independent test designer, session `52989e19-3afc-4b72-81e8-e57cb5c9ac8c`; `374cc59e9`, `4f8897e00`,
  merged `93d722a38`): the not-an-ancestor case revised to the new rule (Rewrite-Reason: DEC-1150 (2)), R2-1's planted
  case (no green record, an untrailered slip) added, both red before the fix; the `unowned` fixture and the clone's
  first close re-planted with a green base on HEAD's line (Rewrite-Reason: DEC-1150 (2)); R2-4's two guards added
  (a culprit timing out alone is not confirmed: `BATCH_UNEXPLAINED`; the rest never lands on zero tests:
  `RUN_INCOMPLETE`), green on the code as the reviewer found it right. R2-5 went to the engineer (the guard denies the
  test designer reads of `docs/research/`).
- Engineer (session `49da35c0-2dce-4290-9c26-dcd87d1649f5`; `1b400c263`, `34601a7ba`): `select.head_without_change`
  returns the green base when it is an ancestor of HEAD, and None otherwise; with None every red is the change's
  (`RED_CAUSED`); the reason says so. R2-5's `-I` dropped. The lead brought the research doc's two stale passages to
  the rule (`b08fae150`).
- The lead's check at `b08fae150258`: lead_verify parallel 4793 tests, 1 failed
  (`tests/unit/resources/test_w2_157_backstop.py::test_l5b_..._item[middle]`, another ticket's, outside this change,
  green alone on re-run: load-sensitive); serial 1 entry green; `gov accept` 88 passed, 0 failed (S12 has no tests,
  P4). Round 2's shared base reds (W2-96, W2-153) are gone after the merge.
- Rows, not fixed here: R2-2 (PK-7, deferred with PK-5, the CTO), R2-3, R2-6. Before the land, the CTO brings the
  owner how EXAMIN's copy gets its first green base (the ticket's "P1-K decided").
