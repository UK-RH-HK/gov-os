---
id: DAEO-03dg
status: open
deps: []
links: []
created: 2026-10-29T15:55:51Z
type: task
priority: 2
assignee: independent-test-designer
external-ref: W2-80
tags: [wave-2, tests, orchestration, close, tools, standard]
wbs_id: W2-80
title: 'Acceptance tests for the close queue''s gates (a) to (h) and its refusal path'
class: test-design
state_class: AUTHORITATIVE
role: independent-test-designer
depends_on: []
allowed_paths:
- tests/acceptance/W2-80/**
kpis:
  success:
  - 'Hermetic: the cases run the committed queue (governance/project/orchestration/tools/close_queue.sh) in a temporary git repository, with stand-ins for gov, the gate tools, the collection run, the record-reading suites, the secrets scanner, the load reading and the waits, through the interface the README states (repository root, log and lock folders, tools folder, pinned gov, load source and wait lengths, each settable and defaulting to today''s values). They never touch this repository, its stores, its lock, the nightly marker or the real pinned gov; they need no network, sleep seconds at most, run under 120 s alone, and are never skipped: a missing interface fails, naming it [DEC-941, DEC-906, DEC-899 item 7]'
  - 'A planted fault per gate stops the queue before the close with exit 2: its reason in the queue log names the gate and the ticket; the lock is removed; gov close is never called; nothing is committed after the gate. One fault per gate: the disk floor (DEC-898); (c) the checkpoint failing, and its commit failing; the rebuild failing; row W2-L423''s early warning naming a file; (a) a collection error and a non-zero collection exit; (f) a red record-reading suite; (b) gov check not green; (e) a commit of the ticket without Implements:; (h) work without a task, and a pinned gov naming no interpreter that runs; (d) a modified, a staged and an untracked file, and a file ignored only by an uncommitted .gitignore [DEC-868, DEC-898, DEC-892, DEC-911, DEC-922, DEC-941]'
  - 'Network gate (g): unreachable hosts hold the queue and retry, naming the hosts in the log at each try; after the sixth try the queue stops with exit 2; hosts reachable again before then let it go on (with the waits shortened through the interface) [DEC-892]'
  - 'Each gate fails closed: a gate tool that is missing, crashes or gives unreadable output stops the queue with that gate''s reason. Gate (d) as written today passes when its tool cannot run, since its output is piped through head and a crash gives an empty result; its case is red first for that reason [DEC-868, DEC-941]'
  - 'A refused close: when gov close exits non-zero, the queue logs CLOSE REFUSED (exit n), removes the lock and exits 4, commits nothing, and attempts no later ticket of the queue (no checkpoint commit, no rebuild for it). A passing close goes on to the next ticket. Every assertion of the scratch test_close_queue_refusal.sh is covered [DEC-929 item 3, DEC-941]'
  - 'Outputs are committed only after a clean close and the skip guard: a skip count other than the expected one, or a close result the guard cannot read, stops with exit 3 and STOPPED AFTER THE CLOSE, with nothing committed. A clean close commits exactly the ticket file, the close record and the closing checkpoint, with the trailers Task, Implements: DEC-868 and Role: orchestrator. The secrets scanner flagging the staged outputs stops with nothing committed. A stop after the close never says "before the close", as today''s stop line does for a staging, scan or commit fault; that case is red first [DEC-899 item 7, DEC-868, DEC-941]'
  - 'What the close is given: gov close receives gate (b)''s own check result (the file gate (b) wrote), and an item <ticket>:<DEC-n> passes the owner''s decision to that ticket''s close only [DEC-889 item 2, DEC-862, DEC-868]'
  - 'The quiet window: no close starts while the nightly''s marker exists or the load stands at or above the threshold; the queue starts only after the stated run of quiet readings, and the lock is set from the start [DEC-780, DEC-868]'
  - 'The queue refuses to run when it or one of its gate tools differs from its commit or is untracked, as nightly_cron.sh does: it stops before the lock wait, naming the file, with nothing committed [P-TOOLS-REVIEW-1 section 4 (a) item 1, DEC-941]'
  - 'Mutation checks on each gate''s condition, as for the nightly: for each gate, a copy of the queue with that gate''s condition removed or inverted makes that gate''s case fail; so do the refusal line''s exit code changed to 0 and the skip guard removed. The README lists each mutant and the cases it fails; a mutant that no case kills is a named gap, never left silent [DEC-936 item 3.1, DEC-941]'
  failure:
  - A planted fault that reaches gov close, or a gate whose tool cannot run passing.
  - A refused close that exits 0 or goes on to the next ticket.
  - Outputs committed after a refused close, a failed skip guard or a scanner finding.
  - A case that runs the queue against this repository, its lock or the real pinned gov, or that is skipped.
profile: STANDARD
sources:
- DEC-941
- DEC-936
- DEC-927
- DEC-929
- DEC-868
- DEC-899
- DEC-892
- DEC-898
- DEC-911
est_loc: 450
acceptance_tests:
  path: tests/acceptance/W2-80/
  author: independent-test-designer (MR-3); written before the orchestrator's change to the queue; the tests are the deliverable
track: C
list_rows: []
---
# W2-80 Acceptance tests for the close queue's gates (a) to (h) and its refusal path

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-80), from package P-TOOLS-REVIEW-1 §4 (a) item 2, accepted by the owner (DEC-941; DEC-936 item 2.4).

- **Why:** the queue decides whether a close starts and what reaches the commit. Its own faults are among this fortnight's refusals: T8 (exit 0 after a refusal), S1 (no rebuild first), S2 (a close started under load) and T9 (a collect log too big). The orchestrator's tooling is present in 14 of 18 refused closes. Only the refusal path has a test, `test_close_queue_refusal.sh`, and it runs a line range cut out of the script.
- **Entry:** the orchestrator first commits the queue and its gate tools under `governance/project/orchestration/tools/`, with a README (P-TOOLS-REVIEW-1 §4 (a) item 1). That move is not this ticket's. Today the queue hard-codes the repository, the log, the lock, the tools, the pinned gov, `/proc/loadavg` and its waits. The README states the interface the cases need, and the orchestrator's change provides it.
- **Paths:** `tests/acceptance/W2-80/**` only, with a README that maps each KPI line to its cases and its red reason, and lists the mutants.
- **Closes** after the orchestrator's change to the queue turns the red cases green. Those cases are the interface, gate (d)'s fail-closed read, the after-the-close stop wording and the self-check. The change is a record commit under `governance/project/orchestration/tools/`, read by the tools' independent audit (P-TOOLS-REVIEW-1 §4 (a) item 3).
