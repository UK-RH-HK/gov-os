---
id: DAEO-j9z6
status: closed
deps: [DAEO-emq1]
links: [DAEO-emq1]
created: 2026-11-11T23:59:00Z
type: task
priority: 1
assignee: engineer
external-ref: W2-115b
tags: [close, queue, full, emergency-2]
wbs_id: W2-115b
title: 'gov queue, the product''s deterministic landing: a thin queue on the close''s pieces (EMERGENCY-2 4.3 step 3)'
class: implementation
state_class: AUTHORITATIVE
role: engineer
profile: FULL
depends_on: [DAEO-emq1]
waits_on: []
closes:
- CAP-23.c
- CAP-39.c
- CAP-63.a
- CAP-63.b
- CAP-63.d
allowed_paths:
- src/gov/queue/**
- src/gov/close/select.py
- src/gov/close/batch.py
- tests/unit/queue/**
- tests/acceptance/W2-115b/**
- .tickets/DAEO-j9z6.md
- governance/project/facts.yaml
- src/gov/adopt/facts.py
- template/governance/kernel/templates/**
- .claude/templates/**
- src/gov/_shipped/template/governance/kernel/templates/**
- template/.rulesync/subagents/**
- .rulesync/subagents/**
- .claude/agents/**
est_loc: 480
kpis:
  success:
  - '`gov queue <ticket>[=<branch>] ... [--onto <branch>]` merges each ticket''s branch (`--no-ff`) onto the integration branch''s head in the warm clone, runs one impact-selected run on the merged result (the union of the candidates'' `select.scoped` selections, the change counted as the branch''s own commits since the integration head as well as the ticket''s), and on green moves the integration branch from that head to the tested merge with one close commit per landed ticket on top of it Verify: a planted repository, one ticket whose change is green: afterwards the integration branch''s head reaches the recorded tested merge through close commits only (each changing only that ticket''s ticket file, `docs/close/<id>/` and `docs/checkpoints/<id>/`); the tested merge''s parents are the old head and the branch''s tip; the run''s JUnit holds the ticket''s own suite and a suite that imports the changed module, and no suite the change reaches by nothing; the root''s working tree follows the branch where it is checked out there. [EMERGENCY-2 4.3 step 3; audit 1 §4; DEC-959 item 1, DEC-983]'
  - 'The ticket closes at the land: each landed ticket''s close record `docs/close/<id>/CL-<id>.md` (`close: queue`, the tested merge as `commit`, the selection, the runs'' counts, every red with its verdict, the culprits, the base, the queue''s record) is written and its status is `closed` in the same landing, with no test run of its own Verify: a planted green landing: the ticket''s close record holds those keys, `commit` equals the tested merge and `runs` the queue run''s counts, its `queue` key names the queue''s record, the ticket''s status at the new head is `closed`, and the planted tests'' run log shows only the queue''s run. [EMERGENCY-2 4.3 step 5; DEC-989]'
  - 'On red the failing tests are named and nothing moves: a ticket whose change turns a test red is not landed; the answer names each failing test''s node id and the ticket as the culprit, and the integration branch, the ticket''s branch and the ticket''s status are as they were Verify: a planted ticket that breaks a reached test: exit 3; the answer names the failing node id and the ticket among the culprits; the integration branch, the work branch and the ticket file are unchanged. [EMERGENCY-2 4.3 steps 3 and 4; W2-115 attribution]'
  - 'A red batch''s culprit is sent back and the rest land: of two tickets, the one whose change is red is not landed and stays open, named with its failing test; the other is landed and closed on the merged result without the culprit, run again there Verify: a planted batch of two tickets, one red: the culprit''s branch is not an ancestor of the new head and its status is open; the other''s branch is, its status is `closed`, its close record names the culprit and its `commit` is the merge without the culprit; exit 3. [DEC-959 item 1, DEC-982, W2-115 S6]'
  - 'Who wrote the acceptance tests is checked by code (G-1): a ticket whose branch holds a commit that changes `tests/acceptance/` or the ticket''s `acceptance_tests.path` without every `Role:` trailer of it being `independent-test-designer` or `owner` is refused before the run (`TEST_AUTHOR_REFUSED`, the commit''s id named) and not landed; a merge commit counts only where its result there differs from git''s own merge of its parents Verify: planted branches: an engineer-role commit to `tests/acceptance/` refused with its id named and nothing of it landed, the rest of the batch landing; a test designer''s or owner''s commit landing; a clean merge of the test designer''s branch landing; a merge that edits an acceptance test in its resolution refused. [MR-3 as audit 7 rewrites it; DEC-1050 (12); land.py G-1]'
  - 'Paths outside the ticket''s allowed paths are a notice, never a refusal: each commit''s path outside the ticket''s `allowed_paths` (read at the branch''s tip) and outside its own record places is listed under `path_notices` with the commit''s id, and the ticket lands Verify: a planted ticket with a commit outside its allowed paths: it lands and closes; the answer and its close record list that path and commit under `path_notices`; a path inside them is not listed. [audit 7 C-6, CAP-58.h as rewritten]'
  - 'Nothing project-specific: the integration branch and the work branch''s form come from `--onto` and `<ticket>=<branch>`, else from `governance/project/queue.yaml` (`integration`, `work_branch` with `{wbs}` and `{ticket}`), else the integration branch is the one checked out at the root; with neither the queue refuses before anything (`INTEGRATION_UNKNOWN`, `BRANCH_UNKNOWN`, exit 1) Verify: grep of `src/gov/queue/` for `w2/`, `integrate`, `DAEO-`, `/home/` finds 0 lines; a planted repository on `main` with branches `feature/<wbs>` named in `queue.yaml` lands with the same code; a planted repository with neither setting nor branch is refused with each code and changes nothing. [DEC-983, DEC-982; audit 1 §4 row 2]'
  - 'Minutes, measured: the answer and the queue''s record (`.gov-runtime/queue/<stamp>/queue.json`) state the seconds of each step (merge, selection, run, close) and the total Verify: a planted landing: the record exists at that place, holds the same result as the answer, and each of the five figures is a number of seconds, none negative, the total not less than any step. [EMERGENCY-2 4.3 step 3 "in minutes"; audit 1 §4 Time]'
  - 'DONE is the green landing itself (audit 1 question 2 (b)): the Definition of Done is three lines, acceptance green (`gov accept`), the landing''s checks green (`gov queue`: the run on the merged result green, the acceptance tests'' authors checked) and the close written at the land; DOD-4 (the FULL review) and DOD-6 (the return''s fields and guard_refusals) are gone from the facts files (the project''s and the default `gov adopt` writes), the ticket template''s `done_when`, the lead template and every generated copy Verify: `governance/project/facts.yaml`''s `dod` and the facts `gov adopt` writes in a planted repository each hold exactly DOD-1, DOD-2 and DOD-3, whose lines name `gov accept` (or its command key), `gov queue` and the close; no kernel template, `.claude/templates/` copy, `src/gov/_shipped/` copy, `.rulesync/` source or `.claude/agents/` file quotes DOD-4, DOD-5, DOD-6 or "DOD-1 to DOD-6"; the ticket template''s `done_when` is `[DOD-1, DOD-2, DOD-3]`; each `.claude/templates/` copy equals its kernel template byte for byte. [EMERGENCY-2 4.3 step 5; audit 1 §2 and question 2 (b); the owner''s working assumption of 2026-11-17, approved kernel text by the CTO''s message (3.5)]'
  failure:
  - 'The integration branch advanced after a red, after a refusal, or to anything but the tested merge with its close commits; or advanced from a head other than the one the run merged onto. Verify: planted runs that are red, red on the base too (`BATCH_UNEXPLAINED`), refused by G-1, and one where the integration branch moves during the run (`HEAD_MOVED`, exit 3): the branch is not moved by the queue in any of them (the moved head stays as it was moved).'
  - 'A ticket merged and not closed, or closed and not merged. Verify: after every planted run, each planted ticket''s status at the integration head is `closed` exactly when its branch''s tip is an ancestor of that head.'
non_goals:
- the close itself (W2-115), its strict mode, W2-193 and W2-194
- Gov OS's own landing tools (land.py, merge_queue.py, landing_select.sh) and the switch-over to gov queue (the CTO's, later)
- merge_queue.py's speed-ups (records-only head moves, store seeding and promotion, the identical-code skip), until friction asks for them
- the run of a direct commit (a chore) through the queue
- languages other than Python (W2-19)
done_when: [DOD-1, DOD-2, DOD-3]
sources: [EMERGENCY-2, DEC-983, DEC-982, DEC-959, DEC-989, DEC-1050, DEC-1083, DEC-1201, CAP-33, DAEO-zkr9]
acceptance_tests:
  path: tests/acceptance/W2-115b/
  author: independent-test-designer (MR-3); written before implementation
track: A
---
# W2-115b gov queue, the product's merge queue

Split from W2-115 (DAEO-emq1) by the CTO's delegated decision on its run 1's P1 (b), 2026-11-11: the six queue success
lines and two failure lines moved here word for word, with W2-97's queue (`governance/project/orchestration/tools/merge_queue.py`)
as the reference. Runs after W2-115 (the close it lands through). Class C3 (the landing path).

## Parked (the owner, DEC-1142 (8), 2026-11-12 ~09:50)

Parked in docs/plan/WAVE_3_PARKING.md as W3-P32: filed or split by the CTO without the owner's P1 (DEC-974; the prompt's §3). Not started again in Wave 2 without the owner's decision.

**Moved to Wave 3's list 2026-11-16 by the owner (DEC-1201 (3)):** W2-115b leaves Wave 2's list (status `deferred`, tag `wave-2` removed); it is not closed and not done. It is listed in `docs/plan/WAVE_3_PARKING.md` under "Moved from Wave 2 (DEC-1201)". `gov plan` no longer offers it.


## Rewritten for Emergency 2 (the CTO's brief, 2026-11-17)

EMERGENCY-2 §6.2 A-4 moves W2-115b back to the release ("the landing must exist in adopted repositories"); §4.3 step 3
is the deterministic landing it builds. The CTO's decision on audit 1's question 1 is option (b), a thin queue on the
product's existing pieces (`batch.isolate`, `select.scoped`, the close's record and `tk close`), about 300 to 500
lines, not a port of Gov OS's scratch `merge_queue.py`. The six success and two failure lines of 2026-11-11 predate
Emergency 2 and are replaced by the lines above; the warm-clone measure, the records-only head moves, the store
refresh and the identical-code skip are left out (non-goals) until friction asks for them. The FULL review
(DOD-4) and `guard_refusals` (DOD-6) go by §3.6 and §2.2. `select.py` and `batch.py` are in the allowed paths only
for keyword arguments the queue passes (`scoped`'s change, `isolate`'s workers); their behaviour without them is
unchanged.

**DONE by code (the owner's working assumption, 2026-11-17, through the CTO):** audit 1's question 2, option (b), is
added to this ticket: DONE is the green landing itself (accept green, the land's checks green, the close written);
the Definition of Done shrinks to those three lines and DOD-4 and DOD-6 go (success line 9). The kernel text for it
is approved by the CTO's message (§3.5).

**Closed at the land 2026-11-18 by the CTO (EMERGENCY-2 4.3 step 5):** merged into w2/integrate with gov accept green on the merged tree; no review (3.6).
