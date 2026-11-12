---
type: probe
task: DAEO-emq1
round: 1
reviewer_session: b85898ea-e991-4c5c-ac8a-97e917b26548
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: independent-auditor
judgement: fail
probed_commit: 569c2933d33cfb14688fa79f09112018c9e43a18
decisions_applied: DEC-1010, DEC-988, DEC-989, DEC-1083, DEC-1001, DEC-1002, DEC-983
---

# Probe record: W2-115 (DAEO-emq1), the smart close, FULL review round 1 of 2: FAIL

A fresh Independent Auditor session (`b85898ea-e991-4c5c-ac8a-97e917b26548`, claude-opus-5-5, effort high, read-only,
class C3) probed head `569c2933d33c` (the built close of run 2, w2/integrate merged at `6831c6e3a`, td-3's revisions
of W1-39 and W2-77 merged at `569c2933d`) and wrote nothing (`git status --porcelain` empty). This is round 1 of at
most 2 (DEC-1010 item 1). The reviewer's two blocks below are copied unchanged from its return; the lead commits this
record because the reviewer is launched read-only (the reviewer's F-4 is about exactly this).

## What was probed

- The whole change `0aec6e10c..569c2933d33c` (only `allowed_paths:`, `tests/acceptance/W2-115/` and the six td-3
  files; acceptance tests changed only in the test designer's commits 01ececd0b, 0bae231ad, d54172ffb).
- W2-115 acceptance, `tests/unit/close/`, W1-39's revised case, W2-77, W1-30 and W2-07 (the strict close, F4):
  272 passed, through the heavy-slot gate.
- Three planted probes (A: an untrailered commit before the ticket's first trailered one; B: a batch whose culprit's
  red is its own new test; C: integration work merged into the ticket branch breaking a selected test) and six
  mutants of the fail-open paths (S4's timeout match and failure-type match, S11's writer check, S2's refusal, S6's
  two guards): every non-equivalent mutant killed.
- Found sound: S1 (no file is strict; another value refused; the strict path unchanged), S3 (one code path for
  `--select`, `--verify` and the close), F2 (no accepted-reds or load-sensitive list), S8, S10, S13, S11's parsing.

## The lead's check

The lead read `src/gov/close/select.py:529` (`ticket_change`: the base is the first parent of the oldest
Task-trailered non-merge commit) and `select.py:749` (the changed set counted from the newest green record,
`green_base`) at `569c2933d33c`, and confirms F-1's mechanism: a commit between the green base and the first trailered
commit is counted in the change for the selection but sits in the base the reds are judged against.

## The reviewer's verdict

```
verdict: FAIL
head: 569c2933d33c
findings: 9
- F-1 | blocking | S4, F1 | src/gov/close/select.py:538 (used at command.py:1815) | The base a red is judged against is the parent of the ticket's oldest Task-trailered commit, but the change is counted from the newest green record. Planted: a green test, then the engineer's untrailered commit that breaks it, then trailered work. gov close exits 0, the ticket closes, and the record says caused:false with a repair ticket. Should refuse with RED_CAUSED. Smallest fix: judge against chosen["green_base"] when it is an ancestor (DEC-988 item 3, DEC-989). Ordinary work: yes, because the scoped close no longer checks trailers (no TRAILER_MISSING gate) and a missed trailer is an honest slip. Consequence: fails open. Reversed by: a hook or gate that refuses untrailered commits on a ticket branch, or an owner ruling that "the head without the change" means without the trailered commits only.
- F-2 | major | F1 | src/gov/close/select.py:538 | Integration work merged into the ticket's branch after its first commit, which breaks a selected test, is judged the ticket's. Planted probe C: RED_CAUSED "the head without the change: green". Should close with a repair ticket. Ordinary work: yes, because ticket branches here merge w2/integrate (this ticket did twice). Consequence: other (fails closed). Reversed by: a rule that ticket branches never merge integration before their close.
- F-3 | major | S6, F3 | src/gov/close/batch.py:588 | When a culprit's red is its own new test, the test cannot run without that candidate (absent), so no candidate "explains" it. Planted probe B (c1 adds a red test; c2 and c3 are clean): BATCH_UNEXPLAINED and nothing lands. Should send c1 back and land c2 and c3. close_build.py blames an absent case once it is confirmed with that candidate alone. Ordinary work: yes. Consequence: other (fails closed). Reversed by: the owner accepting that a batch refuses in this case.
- F-4 | major | S11 | src/gov/close/command.py:1730 | The writer counts only if its commit's Role is exactly independent-auditor. In this repository reviewers are read-only and every probe-record commit carries Role: orchestrator, so every FULL scoped close here refuses VERDICT_NOT_REVIEWER even when the lead copied the reviewer's verdict unchanged. Ordinary work: yes. Consequence: other (fails closed). Reversed by: the process changing so reviewers commit their own records.
- F-5 | major | S2, S1 | src/gov/close/select.py:108 | Scoped close records carry no evidence.scope: full, so in a scoped project the green base moves only with a green nightly. While the nightly stays red (the six W2-96 base reds), the change keeps growing. On this head, scoped(DAEO-emq1) is refused for 110 unmapped paths. Ordinary work: yes. Consequence: other (fails closed). Reversed by: a green nightly on integrate plus a test map that covers docs/, .claude/ and fixtures/.
- F-6 | minor | S6 | src/gov/close/batch.py:631 | WORK_BRANCH = "w2/{wbs}" bakes this repository's Wave 2 branch naming into product code. Another project, or a Wave 3 "w3/" branch, gets CANDIDATE_NOT_ISOLATED. Ordinary work: yes. Consequence: other.
- F-7 | minor | S9 | docs/research/W2-115-smart-close.md:36 | "This close's verdict" was computed by feeding close_build's recorded alone-runs into judge(), not by running this close. Failure types were not compared, and s9.py is not committed, so the table cannot be reproduced. Ordinary work: no. Consequence: other.
- F-8 | minor | S11 | src/gov/close/command.py:1702 | READY is not tied to the head that was reviewed. Commits made after the review close on the old verdict. Out of scope (S11 does not ask for this; DEC-802 allows accepted fixes without a new round). Consequence: other.
- F-9 | minor | S5 | src/gov/close/batch.py:635 | The batch's flaky candidates (red in the batch run, green alone) are not named in the landed tickets' close records and get no repair ticket, unlike the single close. Ordinary work: yes. Consequence: other.
```

```verdict
{"kpis": [
{"kpi": "S1", "verdict": "pass", "findings": [{"id": "F-5", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
{"kpi": "S2", "verdict": "pass", "findings": [{"id": "F-5", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
{"kpi": "S3", "verdict": "pass", "findings": []},
{"kpi": "S4", "verdict": "fail", "findings": [{"id": "F-1", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}]},
{"kpi": "S5", "verdict": "pass", "findings": [{"id": "F-9", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
{"kpi": "S6", "verdict": "pass", "findings": [{"id": "F-3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F-6", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
{"kpi": "S7", "verdict": "pass", "findings": []},
{"kpi": "S8", "verdict": "pass", "findings": []},
{"kpi": "S9", "verdict": "pass", "findings": [{"id": "F-7", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
{"kpi": "S10", "verdict": "pass", "findings": []},
{"kpi": "S11", "verdict": "pass", "findings": [{"id": "F-4", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F-8", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]},
{"kpi": "S12", "verdict": "pass", "findings": [{"id": "S12-deferred", "scope": "out", "ordinary_work": "no", "consequence": "other"}]},
{"kpi": "S13", "verdict": "pass", "findings": []},
{"kpi": "F1", "verdict": "fail", "findings": [{"id": "F-1", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}, {"id": "F-2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
{"kpi": "F2", "verdict": "pass", "findings": []},
{"kpi": "F3", "verdict": "pass", "findings": [{"id": "F-3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
{"kpi": "F4", "verdict": "pass", "findings": []}
]}
```

## Judgement

**Fail** (the reviewer's): F-1 is in scope, reachable in ordinary work and fails open (S4, F1). The fix round and the open calls (F-2 to F-5) go to the CTO in the lead's return.
