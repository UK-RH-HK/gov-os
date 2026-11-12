---
id: DAEO-ifgf
status: in_progress
deps: [DAEO-cb2b]
links: [DAEO-cb2b]
created: 2026-11-12T01:50:00Z
type: task
priority: 1
assignee: engineer
external-ref: W2-121b
tags: [wave-2, dispatch, full]
wbs_id: W2-121b
title: "gov dispatch, part b: landing: the landing hand-off, no wait on a non-conflicting close, the nightly never kept from starting"
class: implementation
state_class: AUTHORITATIVE
role: engineer
profile: FULL
depends_on: [DAEO-cb2b]
waits_on: []
reads:
- src/gov/dispatch/**
- src/gov/resources/**
- governance/project/orchestration/tools/dispatch/**  # the CTO's dispatcher, a reference only
- .tickets/DAEO-cb2b.md  # part a's Interface
needs: []
allowed_paths:
- src/gov/dispatch/**
- tests/unit/dispatch/test_w2_121b*
- src/gov/resources/slots.py  # with the slot line from W2-121c (DEC-1144 (5)), only as that line needs
- docs/probes/DAEO-ifgf/**  # the probe record (P-W2-121b-1, the CTO, 2026-11-12)
est_loc: 500
kpis:
  success:
  - 'Every ticket the orchestrator approved to land goes to the project''s landing command (W2-115 (which took W2-117), where it exists; a configured command otherwise) as one batch whenever it is free, the tree clean and on the integration branch, and no close running; never one not approved, never twice (the approvals claimed before the launch); each outcome becomes an inbox item Verify: planted approvals: an approved ticket goes to the landing command as one batch when the tree is clean, on the integration branch and no close runs; an unapproved ticket never goes; an approved one never goes twice (the approval is claimed before the launch); each outcome is an inbox item. [DEC-1007, DEC-989] [re-worded, DEC-1084]'
  - 'A landing never waits for a close it does not conflict with: a running close blocks a landing only when a ticket it closes is among the landing''s, or while it is committing its records; otherwise the landing goes ahead, and two record commits never collide (retried) Verify: planted closes: a running close with a ticket in the landing''s set blocks the landing, as does one committing its records; a running close with no shared ticket does not block it; two record commits at the same time both land (one retried). [DEC-1014 item 5]'
  - 'The project''s nightly is never kept from starting by a landing: from a configured time before its start until it has started (its running marker), or a configured latest time, the dispatcher claims no landing; one already running is finalised; the status names the hold Verify: a planted configured hold time before the nightly: from then until its running marker (or the latest time) no landing is claimed, a landing already running is finalised, and the status names the hold. [DEC-1018 item 1]'
  - 'Every heavy step takes a heavy-job slot (W2-20: test runs, rebuilds, full checks, retrieval measures), so peaks stay capped whenever they come; a heavy step found running outside a slot is named in the status as a finding Verify: a planted heavy step (test run, rebuild, full check, retrieval measure) is shown holding a slot; a planted one running with no slot is named in the status as a finding. [DEC-1008, DEC-979 D1]'
  failure: []
non_goals:
- the dispatcher core (W2-121, part a) and the other parts
done_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]
sources: [DEC-1007, DEC-1008, DEC-1003, DEC-979, DEC-998, DEC-1009, DEC-1010, DEC-1014, DEC-1015, DEC-1018, DEC-1030, DEC-1031, DEC-1083, DEC-1084, DEC-1088, DEC-715, DEC-944, DEC-952, DEC-982, DEC-983, DEC-989, DEC-995, DAEO-ts4y, DAEO-1ahb]
acceptance_tests:
  path: tests/acceptance/W2-121b/
  author: independent-test-designer (MR-3); written before implementation
track: A
---
# W2-121b gov dispatch, part b

Split from W2-121 (DAEO-cb2b) by the CTO's delegated decision on its run 1's P-W2-121-1 (a) and P-W2-121-3 (a), 2026-11-12: these KPI lines moved word for word; it builds on part a's Interface (in W2-121's ticket) and runs after it. The reference is the CTO's dispatcher (`governance/project/orchestration/tools/dispatch/`), never a target.

## Waits on the owner's K9 decision (DEC-1142 (8), 2026-11-12)

Kept for now; whether parts a (closed) and b meet K9's "a dispatcher" for EXAMIN's copy is the owner's decision. Not started before it.

## K9 decided (the owner, DEC-1144 (5), P1-E option 1, 2026-11-12)

K9's "a dispatcher" (DEC-1008 (2)) is parts a and b. This part gains, word for word, W2-121c's first KPI line ("Every heavy step takes a heavy-job slot ...", DEC-1008 (3)), now its last success line, and `src/gov/resources/slots.py` in its paths as that line needs: a widening by the owner's decision (DEC-974). Startable now, on EXAMIN's path; W2-121c (less that line) and W2-121d stay parked.

## Interface (DEC-1052; P-W2-121b-1 (a), the CTO's delegated decision, DEC-1112 (3), 2026-11-12)

All generic: nothing names this repository; every new key in `governance/project/dispatch.yaml`'s `dispatch:`. Builds on part a's Interface (DAEO-cb2b).

1. **The claim and the batch (S1).** A pass may claim only when: no landing of its own is unfinished, the root (the
   tree `gov dispatch` runs in) has no tracked change and is on `integration_branch`, no conflicting close (2), no
   nightly hold (3). It claims by an atomic rename `land.txt` -> `land-claimed-<land id>.txt` (`<land id>` =
   `land-<UTC stamp>`) *before* the launch; lines whose `<W2>=<head>` is already in `land-done.txt` are dropped from
   the batch (never twice). The batch: `landing_command` with the token `{approvals}` replaced by one argument per line
   `<W2>=<head>` (appended at the end when the token is absent), run detached in the root, output
   `logs/<land id>`, exit code `logs/<land id>.exit`. A later pass finalises it: one line per approval
   `<W2>=<head> <time> <exit code> <land id>` into `land-done.txt`, one inbox item `<land id>.land.txt`
   (`log: <land id>`, `W2: <ids space-separated>`, `status: landed` | `failed (exit N)`, `kind: land`), and the
   claimed file removed. A line not of the form `<W2>=<12-hex>` is never sent and is named in the status.
2. **Closes (S2).** A running close is a process matching `job_markers["close"]`; the tickets it closes are those of
   its arguments equal to a W2 id or ticket id in the landing's set. It blocks a landing only when one of them is in
   the set, or while it commits its records: the root's `.git/index.lock` exists, or the root's tracked changes all
   lie under `close_record_paths` (a list of path prefixes, default `[]`). Any other close does not block.
   "Two record commits never collide": part b provides `gov.dispatch.landing.commit_records(root, paths, message,
   trailers, attempts=3, wait_s=2)`, a commit that retries while another holds `index.lock`; two at once both land
   (one retried). Wiring `gov close` and W2-115 to it is theirs, not in these paths.
3. **The nightly hold (S3).** `nightly_hold` gains an optional `marker` (a path, relative to the root or absolute): from
   `from` (local time) no landing is claimed until `marker`'s mtime is later than today's `from`, or until `until`
   (the latest time; a window with `from` > `until` crosses midnight). Without `marker` the hold lasts until `until`.
   A landing already claimed is finalised as usual, never stopped; starts and the inbox are not held. Status
   (`status.json` key `land_hold` and a `status.txt` line): `land: held for the nightly until it starts (from HH:MM,
   at the latest HH:MM)`. Exit 0.
4. **Heavy steps (S4).** The heavy steps are the `job_markers` kinds `test`, `rebuild`, `check` and `measure`. Full
   checks and retrieval measures take the existing `test` slot (`gov resources --slot test -- ...`): no new slot kind,
   so `src/gov/resources/command.py` (outside the paths) is untouched; `slots.py` gains at most a read helper (the
   runner pids of the slots held, from `holders()`). A heavy step is in a slot when it or an ancestor is a slot's
   runner; the status lists each heavy step with its slot (`heavy_steps: [{kind, pid, slot}]`), and one with no slot
   is a `findings:` entry `heavy step outside a slot: <kind> pid <pid>` (a finding shown, never a failed pass).

Exit codes: a landing held (busy, unclean tree, wrong branch, conflicting close, nightly) is exit 0, its reason in
the status as `land: <reason>`.
