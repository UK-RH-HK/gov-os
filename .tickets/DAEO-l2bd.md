---
id: DAEO-l2bd
status: in_progress
deps: [DAEO-j9z6]
links: [DAEO-j9z6]
created: 2026-11-18T23:30:00Z
type: task
priority: 1
assignee: engineer
external-ref: W2-202
tags: [close, queue, landing, emergency-2]
wbs_id: W2-202
title: 'gov queue becomes the landing-and-close, part 1: base reds recorded, acceptance at the landing, a branch already merged, the pause (L2 §3 A1, A3, A4, A5; DEC-1214 L2, Q-CLOSE)'
class: implementation
state_class: AUTHORITATIVE
role: engineer
profile: FULL
depends_on: [DAEO-j9z6]
waits_on: []
allowed_paths:
- src/gov/queue/**
- src/gov/close/batch.py
- src/gov/adopt/facts.py
- src/gov/adopt/command.py
- tests/unit/queue/**
- tests/unit/close/**
- tests/acceptance/W2-202/**
- tests/acceptance/W2-115b/**
- governance/project/queue.yaml
- .tickets/DAEO-l2bd.md
est_loc: 330
kpis:
  success:
  - 'A1 S1: a batch whose merged run has a red that is red at the base with the same failure type lands; each landed ticket''s close record lists that red in `reds` (`verdict: base`, its test id, failure type and the base commit) and in `base_reds` (the test id), and the answer and `queue.json` name it too Verify: a planted repository with one test red on the base and one clean candidate: `gov queue` exits 0, the ticket is closed, the record holds the entry. [L2 §3 A1; DEC-1214 L2, Q-CLOSE]'
  - 'A1 S2: the same where the commit that made the test red has no `Task:` trailer: nothing is excused or refused by a trailer Verify: the same planted repository with the red-making commit made without a trailer: exit 0, the entry in the record. [L2 §2 Base reds]'
  - 'A1 S3: a red that is green at the base and that no single candidate explains is refused (`BATCH_UNEXPLAINED`) and nothing lands Verify: a planted batch of two candidates whose changes fail only together: exit 3, `BATCH_UNEXPLAINED`, the integration branch and both tickets as they were. [L2 §3 A1 S3]'
  - 'A3 S1: a feature ticket whose acceptance folder holds no test is refused by the queue with `NO_ACCEPTANCE_TESTS` (the ticket is out of the batch, the others go on, exit 3) Verify: a planted ticket whose acceptance folder is empty: exit 3, `NO_ACCEPTANCE_TESTS` named for it, nothing of it landed, the integration branch unmoved; a second ticket of the batch landing. [L2 §3 A3 S1]'
  - 'A3 S2: a ticket of the class research, audit, specification or coordination is judged on its record and lands without a test folder Verify: a planted ticket of each class with no acceptance folder and an evidence record or a specification that the close''s own gates (`check_evidence`, `check_specification`) accept: each lands and closes. [L2 §3 A3 S2]'
  - 'A3 S3: each KPI line''s pass or fail, from the runner `gov accept` uses on the tested merge, is in each landed ticket''s close record under `acceptance` (the folder, each line with its result) Verify: a planted landing: the record''s lines equal `gov accept`''s own answer on the same tree. [L2 §3 A3 S3]'
  - 'A4 S1: `gov queue <T>` for an open ticket whose work branch tip is already on the integration branch merges nothing, runs the checks and the run on the head, writes the close commit and moves the branch Verify: a planted ticket merged by hand into the integration branch, then `gov queue <T>`: exit 0, the close record is written, the ticket is `closed` at the new head, no merge commit is made by the queue. [L2 §3 A4 S1]'
  - 'A5 S1: while `gov pause` froze the project, `gov queue` lands nothing and says why (`PROJECT_PAUSED`, exit 1, nothing written, the branch unmoved); after `gov pause --off` it lands Verify: a planted repository: pause, queue (exit 1, branch unmoved, ticket open), pause --off, queue (lands). [L2 §3 A5 S1; CAP-05, audit 7 C-1]'
  - 'A5 S2: `gov adopt --facts` writes `governance/project/queue.yaml` (`integration`, `work_branch`) with the facts file it writes, and no `close.yaml`; a repository that has its own facts file is left wholly as it is (W2-174 S5) Verify: an adopted planted repository: the file holds both keys, a present queue.yaml is left as it is, no `governance/project/close.yaml` exists. [L2 §3 A5 S2]'
  failure:
  - 'A1 F1: a red the candidate causes is never recorded as a base red; the candidate does not land Verify: a planted candidate that breaks a test green at the base: exit 3, the candidate in `culprits`, no `base` verdict for that test. [L2 §3 A1 F1]'
  - 'A1 F2: a base red creates no file under `.tickets/` and no line under `docs/` outside `docs/close/` and `docs/checkpoints/` Verify: `git status --porcelain` of the clone and the tree diff of the landed head after the landing of S1 show no such path. [L2 §3 A1 F2]'
  - 'A3 F1: no test of the acceptance folder runs twice in one landing Verify: the JUnit names of the acceptance run and of the selection''s run of a planted landing are disjoint. [L2 §3 A3 F1]'
  - 'A4 F1: a closed ticket is still `TICKET_CLOSED` Verify: the existing case of W2-115b, kept. [L2 §3 A4 F1]'
  - 'A5 F1: a project with neither `queue.yaml` nor `close.yaml` and the root on `main` lands onto `main`; with no setting and no branch it is refused with `INTEGRATION_UNKNOWN` as before Verify: the existing W2-115b cases. [L2 §3 A5 F1]'
non_goals:
- A2 (one close record, one writer; waits for the M1 lead's close record), A6 to A8, every B item (the owner's yes)
- "`src/gov/close/command.py`'s record writing and `src/gov/dispatch/**`"
- retiring the close, `accepted_reds` or the strict mode
done_when: [DOD-1, DOD-2, DOD-3]
sources: [EMERGENCY-2, DEC-1214, DEC-983, DEC-982, DEC-959, DEC-953, CAP-33, CAP-05, DAEO-j9z6]
acceptance_tests:
  path: tests/acceptance/W2-202/
  author: independent-test-designer (MR-3); written before implementation
track: A
---
# W2-202 the landing becomes the close, part 1 (L2 §3 A1, A3, A4, A5)

A new KPI line on W2-115b (DAEO-j9z6), which is closed, is a new ticket (EMERGENCY-2 4.6). The lines are those of
`docs/emergency-2/L2-COMMANDS.md` §3 items A1, A3, A4 and A5, decided by the owner in DEC-1214 L2 and Q-CLOSE: the
landing and the close are one deterministic action; a red that is red at the base is recorded as a known base red and
does not block. A2 (one close record, one writer) waits for `e2/m1-context`'s change to the close record; A6 to A8 and
the retirements (B) wait for the owner's yes.

W2-115b's own cases that assert `BATCH_UNEXPLAINED` for a red that is red at the base (its "red on the base too" case)
assert the behaviour A1 replaces: the independent test designer rewrites them in this ticket with the line naming
DEC-1214 Q-CLOSE and `Rewrite-Reason:`.
